"""Vòng tiến hoá ngày — chỗ cỗ máy mạnh hơn hôm qua, và ĐO ĐƯỢC là mạnh hơn.

    python -m kham.tien_hoa            chạy một lượt
    python -m kham.tien_hoa --thu      xem sẽ làm gì, không ghi gì

Bảy bước, và model chỉ chạm vào đúng bước thứ tư:

    1  THU HOẠCH   đọc băng + sổ kết toán
    2  ĐO          thống kê: kỳ vọng, đuôi, hiệu chỉnh, theo chiến thuật
    3  CHẨN        tìm bệnh bằng SỐ                    ← chan_doan.py
    4  ĐỀ XUẤT     model đọc chẩn đoán, đề nghị vặn nút   ← chỗ DUY NHẤT
    5  THỬ         chạy lại băng với tham số mới       ← chay_lai.py
    6  CỔNG        chỉ nhận nếu tốt hơn VÀ đuôi không tệ hơn
    7  GHI SỔ      nhật ký tiến hoá: hôm nay so hôm qua

Đúng hình vòng tiến hoá của repo (`scripts/tien-hoa.mjs`): model bị kẹp
giữa hai lớp số học nó không viết. Bước 3 nói cho nó biết bệnh gì; bước
5–6 quyết định thuốc có tác dụng không. Bỏ một lớp là còn một cái máy tự
làm hỏng mình.

## Không có khoá model thì vòng vẫn quay

Đây là điều kiện thiết kế, không phải tính năng phụ. Thiếu
`ANTHROPIC_API_KEY` thì bước 4 rơi về **người đề xuất tất định**: quét lưới
một nút quanh giá trị hiện tại, chọn ứng viên tốt nhất theo băng.

Chậm hơn model? Đúng. Nhưng nó vẫn tiến hoá mỗi ngày, và nó KHÔNG BAO GIỜ
đề xuất một thứ không kiểm được. Model làm vòng này thông minh hơn; vắng
model làm nó chậm hơn, không làm nó chết.

## "Mạnh hơn mỗi ngày" phải đo được, không phải khẩu hiệu

Mỗi lượt ghi một dòng vào `data/tien-hoa.jsonl`: tham số trước, tham số
sau, kỳ vọng trước, kỳ vọng sau, trên bao nhiêu mẫu, và LÝ DO nhận hay
trả lại. Không có sổ đó thì "mạnh hơn" là chuyện kể.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .bang import doc_bang
from .chay_lai import ThamSo as ChayLaiThamSo
from .chay_lai import mot_luot as chay_lai_mot_luot
from .chan_doan import (NUT_THEO_DUONG, NUT_VAN, TrieuChung, chan_doan,
                        de_bai, doc_tham_so, kep)
from .chay_lai import ThamSo, doi_chieu
from .config import CONFIG, DATA_DIR, ROOT, nao_cham_bat
from .dinh_gia import HieuChinh
from .so import So, bay_gio, thong_ke

SO_TIEN_HOA = DATA_DIR / "tien-hoa.jsonl"

# Cổng chặn. Đặt TRƯỚC khi nhìn dữ liệu, và không nới theo kết quả.
TOI_THIEU_MAU = 40          # mỗi bên phải khớp ngần này trong băng
BIEN_VUOT = 1.10            # ứng viên phải hơn đương nhiệm 10%
DUOI_TOI_DA = 1.15          # thua lớn nhất không được quá 1,15 lần


@dataclass
class DeXuat:
    nut: str
    tuGiaTri: float
    denGiaTri: float
    chuaTrieuChung: str
    lyLe: str
    nguon: str = "tat-dinh"     # tat-dinh | model

    def tom_tat(self) -> dict:
        return {"nut": self.nut, "tu": self.tuGiaTri, "den": self.denGiaTri,
                "chua": self.chuaTrieuChung, "lyLe": self.lyLe,
                "nguon": self.nguon}


@dataclass
class KetQuaTienHoa:
    luc: str
    soKhungBang: int
    soLenhKetToan: int
    nguonMau: str = "that"
    trieuChung: list[dict] = field(default_factory=list)
    deXuat: list[dict] = field(default_factory=list)
    nhan: dict | None = None
    traLai: list[dict] = field(default_factory=list)
    kyVongTruoc: float | None = None
    kyVongSau: float | None = None
    ghiChu: str = ""

    def tom_tat(self) -> dict:
        return {
            "luc": self.luc, "soKhungBang": self.soKhungBang,
            "soLenhKetToan": self.soLenhKetToan,
            "nguonMau": self.nguonMau,
            "trieuChung": self.trieuChung, "deXuat": self.deXuat,
            "nhan": self.nhan, "traLai": self.traLai,
            "kyVongTruoc": self.kyVongTruoc, "kyVongSau": self.kyVongSau,
            "ghiChu": self.ghiChu,
        }


# ══════════════════════════════════════════════════════════════════════════
#  BƯỚC 4 — ĐỀ XUẤT
# ══════════════════════════════════════════════════════════════════════════

def de_xuat_tat_dinh(tc: list[TrieuChung]) -> list[DeXuat]:
    """Người đề xuất KHÔNG cần model: quét lưới một nút quanh giá trị hiện tại.

    Chọn triệu chứng nặng nhất còn nút vặn được, rồi thử nhích nút gợi ý
    đầu tiên một bước theo chiều LÀM CHẶT LẠI. Chiều đó là mặc định vì
    phần lớn bệnh của một bot non là nó vào lệnh quá dễ; nới lỏng thì để
    triệu chứng `dung-ngoai` yêu cầu riêng.
    """
    for t in sorted(tc, key=lambda x: -x.nang):
        if not t.nutGoiY:
            continue
        for duong in t.nutGoiY:
            n = NUT_THEO_DUONG.get(duong)
            if n is None:
                continue
            hien = doc_tham_so(duong)
            if hien is None:
                continue
            # `dung-ngoai` là bệnh ngược: nới ra. Còn lại thì siết vào.
            chieu = -1.0 if t.ma == "dung-ngoai" else 1.0
            # Nhưng `mo-hinh-lech` thì TRIỆU CHỨNG ĐÃ BIẾT HƯỚNG, và bản
            # đầu vứt nó đi.
            #
            # Đã thấy tận mắt trên băng thật: chẩn ra "thiên RỤT RÈ QUÁ"
            # rồi đề xuất SIẾT `batDinhToiThieu` chặt thêm — đúng ngược
            # hướng bệnh. Cổng trả lại, nên không hại gì; nhưng một người
            # đề xuất chỉ biết đi một chiều thì mãi mãi không tìm ra chiều
            # kia, và vòng tiến hoá đứng yên vì lý do sai.
            if t.ma == "mo-hinh-lech":
                nhan = str(t.bangChung.get("chieu") or "")
                if "RỤT RÈ" in nhan:
                    chieu = -1.0          # rụt rè thì phải NỚI bất định ra
                elif "TỰ TIN" in nhan:
                    chieu = 1.0
                # "hai chiều lẫn lộn" thì giữ mặc định — không đoán bừa.
            # Nút "càng thấp càng kỹ" thì đảo chiều lại cho đúng nghĩa siết.
            if duong in ("khoDoi.giaCapToiDa", "ruiRo.kellyPhan",
                         "khoDoi.capChuaKhopToiDaUsd", "khoDoi.giayChoChanHai"):
                chieu = -chieu
            moi = kep(duong, hien + chieu * n.buoc)
            if moi is None or abs(moi - hien) < 1e-12:
                continue
            return [DeXuat(duong, hien, moi, t.ma,
                           f"quét lưới một bước {'siết' if chieu > 0 else 'nới'} "
                           f"để chữa `{t.ma}`")]
    return []


def de_xuat_bang_model(deBai: dict) -> list[DeXuat]:
    """Hỏi Claude. Trả rỗng nếu thiếu khoá, thiếu gói, hoặc trả lời không hợp lệ.

    KHÔNG bao giờ để lỗi ở đây làm chết vòng tiến hoá — vắng model thì
    người gọi rơi về `de_xuat_tat_dinh`.
    """
    if not nao_cham_bat():
        return []
    try:
        import anthropic
    except ImportError:
        return []

    loi_nhac = (
        "Bạn là nhà khoa học của một cỗ máy giao dịch thị trường tiên đoán.\n"
        "Bạn KHÔNG giao dịch và KHÔNG viết code. Việc duy nhất của bạn: đọc\n"
        "chẩn đoán ĐÃ ĐO và đề nghị vặn tối đa 2 nút trong danh sách cho phép.\n\n"
        "Mọi đề nghị của bạn sẽ được chạy lại trên băng ghi thật rồi mới quyết\n"
        "nhận hay trả lại. Đề nghị một thứ không kiểm được thì nó bị bỏ, nên\n"
        "đừng đề nghị sửa kiến trúc, thêm chiến thuật, hay đổi công thức.\n\n"
        "Trả về ĐÚNG một khối JSON, không kèm lời nào khác:\n"
        '{"deXuat":[{"nut":"<đường>","den":<số>,"chua":"<mã triệu chứng>",'
        '"lyLe":"<một câu tiếng Việt>"}]}\n'
    )
    try:
        kh = anthropic.Anthropic()
        r = kh.messages.create(
            model=CONFIG.get("naoCham", {}).get("model", "claude-opus-5"),
            max_tokens=1200,
            system=loi_nhac,
            messages=[{"role": "user",
                       "content": json.dumps(deBai, ensure_ascii=False, indent=2)}],
        )
        tho = "".join(getattr(b, "text", "") for b in r.content)
    except Exception:                                   # noqa: BLE001
        return []

    try:
        i, j = tho.index("{"), tho.rindex("}") + 1
        d = json.loads(tho[i:j])
    except (ValueError, json.JSONDecodeError):
        return []

    ra: list[DeXuat] = []
    for x in (d.get("deXuat") or [])[:2]:
        duong = str(x.get("nut") or "")
        if duong not in NUT_THEO_DUONG:
            continue                       # đề nghị ngoài bảng thì BỎ, không kẹp
        hien = doc_tham_so(duong)
        moi = kep(duong, x.get("den"))
        if hien is None or moi is None or abs(moi - hien) < 1e-12:
            continue
        ra.append(DeXuat(duong, hien, moi, str(x.get("chua") or "?"),
                         str(x.get("lyLe") or "")[:200], nguon="model"))
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  BƯỚC 5–6 — THỬ rồi CỔNG
# ══════════════════════════════════════════════════════════════════════════

def thu_mot_de_xuat(khung: list[dict], dx: DeXuat) -> dict:
    """Chạy lại băng với tham số cũ và mới, rồi cho qua cổng."""
    cl = CONFIG["canLoi"]
    at = float(cl["bienAnToan"])
    net = float(cl["netEdgeToiThieu"])

    # Hai nút này vào thẳng ThamSo; các nút khác đổi CONFIG rồi chạy lại.
    if dx.nut == "canLoi.netEdgeToiThieu":
        a = ThamSo("đương nhiệm", net, at)
        b = ThamSo("ứng viên", dx.denGiaTri, at)
        kq = doi_chieu(khung, a, b)
    elif dx.nut == "canLoi.bienAnToan":
        a = ThamSo("đương nhiệm", net, at)
        b = ThamSo("ứng viên", net, dx.denGiaTri)
        kq = doi_chieu(khung, a, b)
    else:
        # Nút không nằm trong đường chạy lại: đặt tạm vào CONFIG, chạy, trả lại.
        cu = _dat_tham_so(dx.nut, dx.denGiaTri)
        try:
            a = ThamSo("đương nhiệm", net, at)
            b = ThamSo("ứng viên", net, at)
            kq = doi_chieu(khung, a, b)
        finally:
            _dat_tham_so(dx.nut, cu)

    A, B = kq["A"], kq["B"]
    ly: list[str] = []

    if not kq["duMau"] or min(A["soKhop"], B["soKhop"]) < TOI_THIEU_MAU:
        ly.append(f"chưa đủ mẫu (A {A['soKhop']}, B {B['soKhop']}, "
                  f"cần {TOI_THIEU_MAU} mỗi bên)")
    else:
        if B["kyVong"] < A["kyVong"] * BIEN_VUOT:
            ly.append(f"kỳ vọng {B['kyVong']:+.5f} chưa vượt "
                      f"{A['kyVong']:+.5f} đủ biên {BIEN_VUOT:g}×")
        if abs(B["thuaLonNhat"]) > abs(A["thuaLonNhat"]) * DUOI_TOI_DA:
            ly.append(f"thua lớn nhất ${abs(B['thuaLonNhat']):.2f} vượt "
                      f"{DUOI_TOI_DA:g}× đương nhiệm ${abs(A['thuaLonNhat']):.2f}")

    return {"deXuat": dx.tom_tat(), "A": A, "B": B,
            "cho": not ly, "lyDo": ly, "ketLuan": kq["ketLuan"]}


def _dat_tham_so(duong: str, gt) -> float | None:
    d = CONFIG
    k = duong.split(".")
    for x in k[:-1]:
        d = d.setdefault(x, {})
    cu = d.get(k[-1])
    d[k[-1]] = gt
    return cu


def ghi_config(duong: str, gt: float) -> bool:
    """Ghi tham số mới xuống `config.json`. Đây là bước duy nhất ĐỔI THẬT.

    Giữ nguyên mọi khoá chú thích `//...` — chúng là tài liệu nằm trong
    chính file cấu hình, và mất chúng là mất lý do vì sao mỗi con số ở đó.
    """
    p = ROOT / "config.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    n = d
    k = duong.split(".")
    for x in k[:-1]:
        if x not in n or not isinstance(n[x], dict):
            return False
        n = n[x]
    n[k[-1]] = gt
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    _dat_tham_so(duong, gt)
    return True


# ══════════════════════════════════════════════════════════════════════════
#  VÒNG
# ══════════════════════════════════════════════════════════════════════════

def mot_luot(thu: bool = False, tuNgay: str | None = None) -> KetQuaTienHoa:
    kq = KetQuaTienHoa(luc=bay_gio(), soKhungBang=0, soLenhKetToan=0)

    # 1–2. thu hoạch + đo
    khung = doc_bang(tuNgay)
    so = So()
    ket = so.doc(5000)
    hc = HieuChinh()
    kq.soKhungBang = len(khung)
    kq.soLenhKetToan = len(ket)

    tk = thong_ke(ket)
    kq.kyVongTruoc = None if tk.get("chuaCo") else tk["kyVong"]

    bo_qua = _dem_bo_qua(khung)

    # ── mẫu để chẩn: THẬT trước, mô phỏng sau ─────────────────────────
    #
    # Cỗ máy này có thể chạy hàng tuần mà chưa đặt lệnh nào — đường tới
    # sàn đứt, hoặc chưa cơ hội nào qua sàng. Lúc đó `chan_doan` chỉ trả
    # đúng một câu: "chưa đủ để chẩn gì". Câu ấy đúng, nhưng nó khoá luôn
    # vòng tiến hoá: 12/12 lượt đứng yên, không tham số nào từng đổi.
    #
    # Nay khi sổ thật còn mỏng thì dựng mẫu từ CHẠY LẠI trên băng đã ghi —
    # việc này làm được kể từ khi có sổ kết quả. Nhưng mẫu mô phỏng lạc
    # quan có hệ thống (không trượt thêm, không khớp một phần, không chọn
    # lọc bất lợi), nên nó đi kèm nhãn `nguonMau` và nhãn ấy theo xuống
    # tận từng triệu chứng.
    nguonMau = "that"
    if len(ket) < TOI_THIEU_MAU and khung:
        cl = CONFIG["canLoi"]
        mp = chay_lai_mot_luot(khung, ChayLaiThamSo(
            ten="mô phỏng", netEdgeToiThieu=float(cl["netEdgeToiThieu"]),
            bienAnToan=float(cl["bienAnToan"])))
        if mp.laiLoTungLenh:
            ket = [{"laiLo": x} for x in mp.laiLoTungLenh]
            tk = thong_ke(ket)
            nguonMau = "chay-lai"
            kq.nguonMau = nguonMau
            kq.soLenhKetToan = len(ket)
            kq.kyVongTruoc = None if tk.get("chuaCo") else tk["kyVong"]

    # 3. chẩn
    tc = chan_doan(ket, {
        "saiSoTB": hc.sai_so_tuyet_doi_tb(),
        "tongMau": hc.tong_mau,
        "bang": hc.bang(),
    }, bo_qua, nguonMau=nguonMau)
    kq.trieuChung = [t.tom_tat() for t in tc]

    if all(t.ma in ("khoe", "thieu-mau") for t in tc):
        kq.ghiChu = ("không có bệnh nào vượt ngưỡng — không vặn gì. "
                     "Vòng tiến hoá đứng yên là một kết quả hợp lệ.")
        if not thu:
            _ghi_so(kq)
        return kq

    # 4. đề xuất — model trước, tất định là lưới đỡ
    db = de_bai(tc, {n.duong: doc_tham_so(n.duong) for n in NUT_VAN})
    dx = de_xuat_bang_model(db) or de_xuat_tat_dinh(tc)
    kq.deXuat = [d.tom_tat() for d in dx]
    if not dx:
        kq.ghiChu = "không nghĩ ra đề xuất nào hợp lệ"
        if not thu:
            _ghi_so(kq)
        return kq

    # 5–6. thử rồi cổng
    for d in dx:
        r = thu_mot_de_xuat(khung, d)
        if r["cho"]:
            kq.nhan = r
            kq.kyVongSau = r["B"]["kyVong"]
            if not thu and ghi_config(d.nut, d.denGiaTri):
                kq.ghiChu = (f"NHẬN: {d.nut} {d.tuGiaTri} → {d.denGiaTri}. "
                             f"{r['ketLuan']}")
            else:
                kq.ghiChu = f"(thử) sẽ nhận: {d.nut} → {d.denGiaTri}"
            break
        kq.traLai.append(r)
    else:
        kq.ghiChu = ("mọi đề xuất đều bị cổng trả lại — giữ nguyên tham số. "
                     "Trả lại KHÔNG phải thất bại: nó là cổng làm đúng việc.")

    if not thu:
        _ghi_so(kq)
    return kq


def _dem_bo_qua(khung: list[dict]) -> dict[str, int]:
    """Đếm lý do bỏ qua trong băng — nguyên liệu cho triệu chứng `dung-ngoai`."""
    ra: dict[str, int] = {}
    for k in khung:
        for tt in (k.get("thiTruong") or []):
            so = tt.get("so") or {}
            up = so.get("UP") or {}
            ly = "thang-cho" if up.get("thangCho") else (
                "khong-dung-duoc" if up.get("dungDuoc") is False else None)
            if ly:
                ra[ly] = ra.get(ly, 0) + 1
    return ra


def _ghi_so(kq: KetQuaTienHoa) -> None:
    SO_TIEN_HOA.parent.mkdir(parents=True, exist_ok=True)
    with SO_TIEN_HOA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kq.tom_tat(), ensure_ascii=False) + "\n")


def doc_so(n: int = 60) -> list[dict]:
    if not SO_TIEN_HOA.exists():
        return []
    ra = []
    for d in SO_TIEN_HOA.read_text(encoding="utf-8").splitlines():
        d = d.strip()
        if d:
            try:
                ra.append(json.loads(d))
            except json.JSONDecodeError:
                continue
    return ra[-n:]


def duong_tien_hoa() -> dict:
    """Sổ tiến hoá gộp lại — thứ trả lời câu "có mạnh hơn thật không".

    Không có hàm này thì "mạnh hơn mỗi ngày" là chuyện kể. Có nó thì đó là
    một dãy số ai cũng đọc được, kể cả khi dãy số ấy nói là KHÔNG mạnh hơn.
    """
    ds = doc_so(400)
    nhan = [x for x in ds if x.get("nhan")]
    ky = [(x["luc"], x["kyVongTruoc"], x["kyVongSau"]) for x in nhan
          if x.get("kyVongTruoc") is not None and x.get("kyVongSau") is not None]
    return {
        "soLuot": len(ds),
        "soLanNhan": len(nhan),
        "soLanTraLai": sum(1 for x in ds if x.get("traLai") and not x.get("nhan")),
        "soLanDungYen": sum(1 for x in ds if not x.get("deXuat")),
        "chuoi": [{"luc": l, "truoc": a, "sau": b} for l, a, b in ky][-40:],
        "tongCaiThien": sum(b - a for _, a, b in ky) if ky else None,
        "ganNhat": ds[-1] if ds else None,
    }


def _main() -> int:
    thu = "--thu" in sys.argv
    kq = mot_luot(thu=thu)
    print("=" * 74)
    print("  VÒNG TIẾN HOÁ — Khâm Thiên Giám" + ("  (THỬ, không ghi gì)" if thu else ""))
    print("=" * 74)
    print(f"  băng {kq.soKhungBang} khung · sổ {kq.soLenhKetToan} lệnh đã kết toán")
    print()
    print("  TRIỆU CHỨNG:")
    for t in kq.trieuChung:
        print(f"    [{'!' * max(1, t['nang'])}] {t['ma']}: {t['moTa']}")
    if kq.deXuat:
        print()
        print("  ĐỀ XUẤT:")
        for d in kq.deXuat:
            print(f"    {d['nut']}: {d['tu']} → {d['den']}  ({d['nguon']})")
            print(f"       {d['lyLe']}")
    if kq.traLai:
        print()
        print("  CỔNG TRẢ LẠI:")
        for r in kq.traLai:
            for l in r["lyDo"]:
                print(f"    · {l}")
    print()
    print(f"  {kq.ghiChu}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
