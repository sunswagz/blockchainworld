"""Băng ghi và chạy lại — P0 của lộ trình, và nó phải làm TRƯỚC mô hình.

Lý do P0 đứng trước mọi thứ khác: nếu không lưu sổ lệnh, tick và fill ngay từ
đầu thì ba tháng nữa dù có muốn nghiên cứu cũng không có "ký ức thế giới" nào
để chạy lại. Mô hình viết sau lúc nào cũng được; dữ liệu không quay lại được.

Và không có chạy lại thì không có cách nào biết một thay đổi là TỐT HƠN hay
chỉ là KHÁC ĐI — đúng bài học đã ghi lại ở tu-cam-thanh-runtime.

Định dạng: JSONL một dòng một khung hình, gzip. Cố ý thô sơ: thứ cần là đọc
lại được sau sáu tháng bằng bất cứ công cụ nào, không phải nhanh.

## Vì sao MỖI PHIÊN một file, chứ không nối thêm vào file của ngày

Bản đầu mở `gzip.open(..., "at")` — nối thêm vào file của ngày hôm nay. Hợp lệ
về mặt định dạng: một file gzip được phép là nhiều "thành viên" nối đuôi nhau,
và `gzip.open` đọc được cả chuỗi đó.

Chỉ hỏng khi tiến trình chết mà chưa đóng file — và tiến trình này bị tắt bật
mấy lần một ngày. Lúc đó thành viên cuối CỤT: thiếu block kết thúc, thiếu CRC.
Lần chạy sau nối một thành viên MỚI ngay sau đám byte cụt ấy, và giờ rác nằm
GIỮA file. Trình đọc chạy tới đó, gặp header gzip của thành viên mới nằm ở chỗ
đáng lẽ là dữ liệu nén, và ném `zlib.error: invalid block type`.

Hậu quả đo được ngày 21/08/2026, trên băng thật:

    bang-2026-08-20.jsonl.gz    1.419 / 10.450 dòng đọc được   (mất 86%)
    bang-2026-08-21.jsonl.gz    6.819 / 20.048 dòng đọc được   (mất 66%)

Không lỗi nào báo. `doc_bang()` chỉ đơn giản trả về ít hơn sự thật, và mọi
phép hậu kiểm dựng trên đó vẫn đúng công thức — trên một mẩu dữ liệu bị cắt.

Nên nay: **không bao giờ nối thêm**. Mỗi phiên ghi mở một file riêng, tên có
giờ và pid. Phiên bị giết chỉ làm cụt ĐUÔI file của chính nó, và phần trước
đuôi vẫn đọc được — vì trình đọc dưới đây chịu được đuôi cụt.

## Và vì sao trình đọc phải CHỊU ĐƯỢC file hỏng

Băng hỏng không phải chuyện hiếm cần báo lỗi — nó là chuyện thường phải sống
chung: máy sập, ổ đầy, Ctrl+C giữa lúc đang xả. Trình đọc bản đầu bắt mỗi
`OSError`, mà `zlib.error` KHÔNG phải `OSError`. Nên một file hỏng làm cả lời
gọi ném ra ngoài, kéo theo mất luôn những file NGUYÊN VẸN của các ngày khác.

Đường đi của lỗi đó, đã xảy ra thật:

    doc_bang() ném zlib.error
      → /api/bang, /api/chay-lai, /api/doi-chieu trả 500
      → `tien_hoa.mot_luot()` chết ngay dòng đầu
      → vòng tự tiến hoá đứng hẳn, mà buồng lái vẫn hiện "đã chạy hôm nay"

Nay `doc_bang()` **không bao giờ ném**. Gặp thành viên hỏng thì giữ phần đã
giải nén được, nhảy tới header gzip kế tiếp, đọc tiếp — rồi KHAI ra đã bỏ mất
bao nhiêu. Im lặng nuốt lỗi và im lặng trả về thiếu là cùng một cái bẫy.
"""
from __future__ import annotations

import gzip
import json
import os
import time
import zlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .config import CONFIG, DATA_DIR

_B = CONFIG["bang"]

#: Đầu một thành viên gzip: magic + phương pháp nén deflate.
_DAU = b"\x1f\x8b\x08"


def _thu_muc() -> Path:
    """Thư mục băng. Đường TƯƠNG ĐỐI tính từ `DATA_DIR`, không từ `ROOT`.

    Phải thế thì `KTG_DATA_DIR` mới tách được sổ sách của phép kiểm khỏi sổ
    sách thật. Bản đầu tính từ `ROOT`, nên mọi phép kiểm chạm tới băng đều ghi
    thẳng vào băng THẬT — đúng cái bẫy mà đầu `scripts/selftest.py` chép lại từ
    Tử Cấm Thành, chỉ là ở một cửa khác.
    """
    p = Path(_B["thuMuc"])
    if not p.is_absolute():
        # `"data/bang"` là cách viết cũ, hồi đường còn tính từ ROOT. Bỏ khúc
        # `data/` ở đầu để cấu hình cũ vẫn trỏ đúng chỗ cũ.
        cac = p.parts
        if cac and cac[0] == "data":
            cac = cac[1:]
        p = DATA_DIR.joinpath(*cac) if cac else DATA_DIR / "bang"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ══════════════════════════════════════════════════════════════════════════
#  GHI
# ══════════════════════════════════════════════════════════════════════════
class MayGhi:
    """Ghi mỗi khung hình trạng thái xuống đĩa. Mỗi phiên một file riêng."""

    def __init__(self) -> None:
        self.bat = bool(_B.get("ghi", True))
        self._ngay = ""
        self._f = None
        self.soKhung = 0
        self.soLoiGhi = 0
        self.loiCuoi: str | None = None
        self.duong: Path | None = None

    def _duong_moi(self, ngay: str) -> Path:
        """Tên file của MỘT phiên ghi: ngày + giờ + pid.

        Giờ và pid không phải để trang trí — hai tiến trình cùng chạy (đã xảy
        ra: quên tắt bản cũ rồi mở bản mới) mà ghi chung một file thì hai dòng
        nén xen kẽ nhau, và cả file thành rác không cứu lại được.
        """
        tm = _thu_muc()
        goc = f"bang-{ngay}-{time.strftime('%H%M%S', time.gmtime())}-{os.getpid()}"
        p = tm / f"{goc}.jsonl.gz"
        n = 2
        while p.exists():
            p = tm / f"{goc}-{n}.jsonl.gz"
            n += 1
        return p

    def _mo(self):
        ngay = time.strftime("%Y-%m-%d", time.gmtime())
        if self._f is None or ngay != self._ngay:
            self.dong()
            self._ngay = ngay
            self.duong = self._duong_moi(ngay)
            # "wt" chứ KHÔNG "at" — xem đầu file để biết vì sao.
            self._f = gzip.open(self.duong, "wt", encoding="utf-8")
        return self._f

    def ghi(self, khung: dict) -> None:
        if not self.bat:
            return
        try:
            f = self._mo()
            f.write(json.dumps(khung, ensure_ascii=False, separators=(",", ":")) + "\n")
            self.soKhung += 1
            # Xả mỗi 50 khung. `flush()` của gzip phát một block đồng bộ, nên
            # phần trước lần xả cuối vẫn giải nén được kể cả khi tiến trình bị
            # giết ngay sau đó — mất tối đa 50 khung, không mất cả file.
            if self.soKhung % 50 == 0:
                f.flush()
        except (OSError, TypeError, ValueError) as e:
            # `TypeError`/`ValueError` = khung có thứ không đổi ra JSON được.
            # Bản đầu chỉ bắt `OSError`, nên một khung bẩn ném ngược lên vòng
            # lặp rồi vào nhật ký thành "vòng N lỗi" — đúng chỗ không ai nghĩ
            # tới băng ghi. Nay là một con số buồng lái đọc được.
            self.soLoiGhi += 1
            self.loiCuoi = f"{type(e).__name__}: {e}"

    def dong(self) -> None:
        if self._f is not None:
            try:
                self._f.flush()
                self._f.close()
            except OSError:
                pass
            self._f = None

    def don_cu(self) -> int:
        """Xoá băng quá hạn giữ. Trả về số file đã xoá."""
        gio_han = time.time() - float(_B.get("ngayGiuLai", 30)) * 86400
        xoa = 0
        for p in _thu_muc().glob("bang-*.jsonl.gz"):
            if self.duong is not None and p == self.duong:
                continue                    # đừng xoá file đang mở
            try:
                if p.stat().st_mtime < gio_han:
                    p.unlink()
                    xoa += 1
            except OSError:
                pass
        return xoa

    def tom_tat(self) -> dict:
        return {"soKhung": self.soKhung, "bat": self.bat,
                "soLoiGhi": self.soLoiGhi, "loiCuoi": self.loiCuoi,
                "duong": self.duong.name if self.duong else None}


# ══════════════════════════════════════════════════════════════════════════
#  ĐỌC
# ══════════════════════════════════════════════════════════════════════════
@dataclass
class BaoCaoDoc:
    """Đọc được bao nhiêu, và mất bao nhiêu. Không trường nào là trang trí.

    `soDongHong` đếm cả mẩu dòng ở hai mép mỗi chỗ đứt: nối lại được thì đã
    nối, không nối được thì phải ĐẾM chứ không được lặng lẽ bỏ.
    """
    soFile: int = 0
    soFileHong: int = 0
    soKhung: int = 0
    soDongHong: int = 0
    soByteBoQua: int = 0
    fileHong: list[str] = field(default_factory=list)

    @property
    def lanh_lan(self) -> bool:
        return self.soFileHong == 0 and self.soDongHong == 0

    def tom_tat(self) -> dict:
        return {
            "soFile": self.soFile, "soFileHong": self.soFileHong,
            "soKhung": self.soKhung, "soDongHong": self.soDongHong,
            "soByteBoQua": self.soByteBoQua, "fileHong": self.fileHong[:12],
            "lanhLan": self.lanh_lan,
        }


def _dau_thanh_vien_ke(raw: bytes, tu: int) -> int:
    """Tìm chỗ có thể là đầu một thành viên gzip, kể từ `tu`.

    Ba byte đó cũng xuất hiện ngẫu nhiên trong dữ liệu đã nén, nên đây chỉ là
    ỨNG VIÊN: lọc thêm bằng byte FLG (chỉ 5 bit thấp được dùng). Ứng viên sai
    thì `zlib` ném ngay ở lần giải nén kế và ta lại nhảy tiếp — đoán sai ở đây
    tốn một vòng lặp, không tốn dữ liệu.
    """
    k = raw.find(_DAU, tu)
    while k >= 0 and (k + 4 > len(raw) or raw[k + 3] >= 0x20):
        k = raw.find(_DAU, k + 1)
    return k


def _giai_nen(raw: bytes, bao: BaoCaoDoc, ten: str) -> list[bytes]:
    """Giải nén nhiều thành viên gzip, chịu được thành viên cụt hoặc hỏng.

    Trả về danh sách ĐOẠN, không phải một khối liền: mỗi chỗ đứt là một ranh
    giới, và hai mẩu dòng ở hai bên ranh giới ấy KHÔNG được dán vào nhau. Dán
    vào nhau thì thỉnh thoảng ra một dòng JSON hợp lệ mà nội dung là hai nửa
    của hai khung hình khác nhau — một con số sai trông y hệt số đúng.
    """
    doan: list[bytes] = []
    i, n, hong = 0, len(raw), False
    while i < n:
        d = zlib.decompressobj(31)
        ra, j, vap = bytearray(), i, False
        while j < n:
            try:
                ra += d.decompress(raw[j:j + 65536])
            except zlib.error:
                vap = True
                break
            j += 65536
            if d.eof:
                break
        if ra:
            doan.append(bytes(ra))
        if vap or not d.eof:
            hong = True
            k = _dau_thanh_vien_ke(raw, i + 1)
            if k < 0:
                bao.soByteBoQua += max(0, n - (j if vap else i))
                break
            bao.soByteBoQua += max(0, k - (j if vap else i))
            i = k
        else:
            i = n - len(d.unused_data) if d.unused_data else n
    if hong:
        bao.soFileHong += 1
        bao.fileHong.append(ten)
    return doan


def lan_luot(tuNgay: str | None = None,
             bao: BaoCaoDoc | None = None) -> Iterator[dict]:
    """Sinh từng khung hình một. KHÔNG BAO GIỜ ném.

    `tuNgay` dạng YYYY-MM-DD; None = mọi ngày. Truyền `bao` vào thì báo cáo hư
    hỏng được cộng dồn vào đó — đọc sau khi vòng lặp chạy hết.

    Có bản sinh dần vì cả băng KHÔNG vừa bộ nhớ mãi được: 30.753 khung của hai
    ngày đầu đã là ~150 MB JSON và mất 7–20 giây chỉ để dựng danh sách, mà hạn
    giữ là 30 ngày. Chỗ nào chỉ đi qua băng một lượt thì dùng hàm này; chỗ nào
    thật sự phải quét lại nhiều lượt (`doi_chieu` chạy hai bộ tham số trên cùng
    một băng) thì mới gọi `doc_bang()`.
    """
    bao = bao if bao is not None else BaoCaoDoc()
    for p in sorted(_thu_muc().glob("bang-*.jsonl.gz")):
        # tên: bang-<ngày>[-<giờ>-<pid>].jsonl.gz — mười ký tự sau "bang-"
        # luôn là ngày, ở cả tên cũ lẫn tên mới.
        ngay = p.name[len("bang-"):][:10]
        if tuNgay and ngay < tuNgay:
            continue
        bao.soFile += 1
        try:
            raw = p.read_bytes()
        except OSError:
            bao.soFileHong += 1
            bao.fileHong.append(p.name)
            continue
        for doan in _giai_nen(raw, bao, p.name):
            for d in doan.split(b"\n"):
                d = d.strip()
                if not d:
                    continue
                try:
                    k = json.loads(d)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    bao.soDongHong += 1
                    continue
                bao.soKhung += 1
                yield k


def doc_bang_day_du(tuNgay: str | None = None) -> tuple[list[dict], BaoCaoDoc]:
    """Đọc cả băng vào bộ nhớ, kèm báo cáo hư hỏng. KHÔNG BAO GIỜ ném."""
    bao = BaoCaoDoc()
    return list(lan_luot(tuNgay, bao)), bao


def doc_bang(tuNgay: str | None = None) -> list[dict]:
    """Đọc lại băng. Giữ nguyên chữ ký cũ cho chỗ cần quét lại nhiều lượt."""
    return doc_bang_day_du(tuNgay)[0]


def dem_bang(tuNgay: str | None = None) -> BaoCaoDoc:
    """Đếm khung hình mà KHÔNG giữ khung nào lại.

    `/api/bang` chỉ cần con số, và bản trước gọi `doc_bang()` rồi `len()` —
    tức là dựng cả gigabyte đối tượng Python để đọc ra một số nguyên, trên một
    luồng của buồng lái, mỗi lần ai đó mở bảng.
    """
    bao = BaoCaoDoc()
    for _ in lan_luot(tuNgay, bao):
        pass
    return bao


# `chay_lai` cũ chỉ ĐẾM cơ hội đã ghi trong băng — nó trả về một con số
# trông như backtest nhưng không dựng lại được gì, nên không so được hai bộ
# tham số. Đã thay bằng `kham/chay_lai.py`, chạy lại theo sự kiện thật.
# Module này giờ chỉ còn lo việc GHI và ĐỌC băng.

may_ghi = MayGhi()
