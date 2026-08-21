"""Băng ghi — ký ức thô của bốn cảng, để còn CHẠY LẠI được.

Sổ ở `so.py` ghi **kết luận** (cơ hội nào, NET bao nhiêu, qua cửa hay không).
Băng ở đây ghi **nguyên liệu**: từng báo giá thô của từng cảng, từng lượt quét.

Hai thứ khác nhau về mục đích, và thiếu cái thứ hai thì không đào tạo được gì:

    sổ    trả lời "hôm qua ta đã quyết thế nào"
    băng  trả lời "nếu ngưỡng khác đi thì ta ĐÃ quyết thế nào"

Không có băng thì mọi lần vặn ngưỡng đều là đổi số cho vui — không cách nào
biết một thay đổi là TỐT HƠN hay chỉ là KHÁC ĐI. Đó là lý do `chay_lai.py`
đứng trước `tien_hoa.py` trong lộ trình, không phải ngược lại.

Định dạng: JSONL một dòng một khung hình, gzip. Cố ý thô sơ: thứ cần là đọc
lại được sau sáu tháng bằng bất cứ công cụ nào, không phải nhanh.

## Hai bài học chép nguyên từ `kham-thien-giam-runtime/kham/bang.py`

Cả hai đã trả giá bằng dữ liệu thật ở cung kia, nên ở đây làm đúng ngay từ
đầu chứ không đợi cắn lại lần nữa.

**1. Mỗi phiên một file, KHÔNG nối thêm.** `gzip.open(..., "at")` hợp lệ về
định dạng, và hỏng ngay lần đầu tiến trình bị giết: thành viên gzip cuối cụt,
lần chạy sau nối thành viên mới ngay sau đám byte cụt, rác nằm GIỮA file.
Trình đọc chạy tới đó là ném `invalid block type` và mất tất cả phần sau. Đo
được ở cung kia: **mất 73% băng**, không lỗi nào báo.

**2. Trình đọc phải chịu được file hỏng và KHÔNG BAO GIỜ ném.** `zlib.error`
không phải `OSError`, nên `except OSError` bắt hụt và một file hỏng kéo theo
mất luôn những ngày NGUYÊN VẸN. Gặp thành viên hỏng thì giữ phần đã giải nén
được, nhảy tới header gzip kế, đọc tiếp — rồi KHAI ra đã bỏ mất bao nhiêu.

**3. Cụt đuôi KHÔNG phải hỏng.** File của mọi phiên bị Ctrl+C đều thiếu block
kết thúc. Gộp hai loại lại là đèn báo đỏ vĩnh viễn, và cảnh báo lúc nào cũng
đỏ thì thôi ai nhìn — kể cả lần nó đúng.
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

#: Bao lâu xả băng xuống đĩa một lần. Mất tối đa ngần này giây băng nếu
#: tiến trình bị giết — và con số này KHÔNG phụ thuộc nhịp quét.
XA_MOI_GIAY = 60.0

#: Đầu một thành viên gzip: magic + phương pháp nén deflate.
_DAU = b"\x1f\x8b\x08"


def _thu_muc() -> Path:
    """Thư mục băng. Đường TƯƠNG ĐỐI tính từ `DATA_DIR`, không từ `ROOT`.

    Phải thế thì `TBT_DATA_DIR` mới tách được sổ sách của phép kiểm khỏi sổ
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
        self._lanXa = 0.0

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
            # Xả theo THỜI GIAN, không theo số khung. `flush()` của gzip
            # phát một block đồng bộ, nên phần trước lần xả cuối vẫn giải nén
            # được kể cả khi tiến trình bị giết ngay sau đó.
            #
            # Đếm khung là sai ở đây, và nó sai theo nhịp: Khâm Thiên Giám
            # chạy nhịp 2 giây nên "mỗi 50 khung" là 100 giây, còn cung này
            # nhịp 30 giây nên cùng con số ấy thành **25 phút** mất trắng mỗi
            # lần tắt máy. Với một cung cần HÀNG GIỜ băng mới có một mẫu hậu
            # kiểm, 25 phút là nhiều.
            #
            # Đã thấy thật lúc dựng: bảng trạng thái hiện "băng phiên này 3
            # khung · trên đĩa 0 khung" — không sai, nhưng đọc như hỏng.
            gio = time.time()
            if gio - self._lanXa >= XA_MOI_GIAY:
                f.flush()
                self._lanXa = gio
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

    **`cụt đuôi` và `đứt giữa` là HAI chuyện, đừng gộp.** Gộp thì đèn báo đỏ
    vĩnh viễn, vì file của mọi phiên bị Ctrl+C đều thiếu block kết thúc — và
    một cảnh báo lúc nào cũng đỏ thì người ta thôi nhìn nó, rồi thôi nhìn cả
    lần nó đúng. Đúng cái bẫy `cong-bo/assets/js/` đã cắn ở repo cha.

        cụt đuôi   thành viên cuối thiếu block kết thúc, KHÔNG mất gì phía
                   sau vì phía sau không có gì. Bình thường sau mỗi lần tắt
                   máy; mất tối đa 50 khung chưa xả.
        đứt giữa   phải NHẢY QUA byte mới đọc tiếp được. Đây mới là mất dữ
                   liệu, và là dấu hiệu file bị nối thêm sau một đuôi cụt.

    `soDongHong` đếm cả mẩu dòng ở hai mép mỗi chỗ đứt: nối lại được thì đã
    nối, không nối được thì phải ĐẾM chứ không được lặng lẽ bỏ.
    """
    soFile: int = 0
    soFileHong: int = 0          # đứt GIỮA — có mất dữ liệu
    soFileCutDuoi: int = 0       # chỉ cụt đuôi — bình thường sau khi tắt máy
    soKhung: int = 0
    soDongHong: int = 0
    soByteBoQua: int = 0
    fileHong: list[str] = field(default_factory=list)

    @property
    def lanh_lan(self) -> bool:
        """Cụt đuôi KHÔNG làm băng mất lành — xem giải thích ở trên."""
        return self.soFileHong == 0 and self.soByteBoQua == 0

    def tom_tat(self) -> dict:
        return {
            "soFile": self.soFile, "soFileHong": self.soFileHong,
            "soFileCutDuoi": self.soFileCutDuoi,
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
    i, n = 0, len(raw)
    hong = cut_duoi = False
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
        if not vap and d.eof:
            i = n - len(d.unused_data) if d.unused_data else n
            continue
        k = _dau_thanh_vien_ke(raw, i + 1)
        if k < 0:
            # Hết file mà không còn thành viên nào phía sau. Không nhảy qua
            # byte nào cả, nên đây là CỤT ĐUÔI chứ không phải mất dữ liệu —
            # trừ khi zlib vấp thật, lúc đó phần đuôi mới đúng là rác.
            if vap:
                hong = True
                bao.soByteBoQua += max(0, n - j)
            else:
                cut_duoi = True
            break
        # Còn thành viên phía sau mà thành viên này không kết thúc đàng hoàng
        # → có byte phải nhảy qua. Đây mới là đứt GIỮA.
        hong = True
        bao.soByteBoQua += max(0, k - (j if vap else i))
        i = k
    if hong:
        bao.soFileHong += 1
        bao.fileHong.append(ten)
    elif cut_duoi:
        bao.soFileCutDuoi += 1
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
