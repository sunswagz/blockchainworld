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
import time
from dataclasses import dataclass, field
from pathlib import Path

from .bang import NguonKhung, giai_doan_cua
from .chay_lai import ThamSo as ChayLaiThamSo
from .chay_lai import gop_doi_chieu
from .chay_lai import mot_luot as chay_lai_mot_luot
from .chan_doan import (NUT_THEO_DUONG, NUT_VAN, TrieuChung, chan_doan,
                        de_bai, doc_tham_so, kep)
from .chay_lai import ThamSo, doi_chieu
from .config import CONFIG, DATA_DIR, ROOT, nao_cham_bat
from . import nan_lai
from .dinh_gia import HieuChinh
from .so import So, bay_gio, thong_ke

SO_TIEN_HOA = DATA_DIR / "tien-hoa.jsonl"

# Mốc để đo mỗi bước mất bao lâu. Một lượt trên băng 8 ngày mất
# quãng hai mươi phút, và trước bản này nó chạy CÂM suốt chừng ấy —
# không phân biệt được "đang quét băng" với "treo".
_MOC = 0.0

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
    daThu: int = 0              # bao nhiêu ứng viên đã đo và bị trả lại
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
            "nguonMau": self.nguonMau, "daThu": self.daThu,
            "trieuChung": self.trieuChung, "deXuat": self.deXuat,
            "nhan": self.nhan, "traLai": self.traLai,
            "kyVongTruoc": self.kyVongTruoc, "kyVongSau": self.kyVongSau,
            "ghiChu": self.ghiChu,
        }


# ══════════════════════════════════════════════════════════════════════════
#  BƯỚC 4 — ĐỀ XUẤT
# ══════════════════════════════════════════════════════════════════════════

TIM_MAY_BUOC = 4        # dò xa nhất mấy bước dọc theo chiều bệnh
NHO_MAY_LUOT = 20       # trả lại trong ngần này lượt thì coi như đã thử


def da_tra_lai(soLuot: int = NHO_MAY_LUOT) -> set:
    """Những (nút, giá trị) mà cổng đã đo và trả lại gần đây.

    Không có trí nhớ này thì người đề xuất tất định là một vòng lặp chết:
    nó luôn chọn triệu chứng nặng nhất, nút gợi ý đầu tiên, một bước theo
    chiều bệnh — tức là ĐÚNG MỘT ứng viên, mỗi ngày, mãi mãi. Cổng đo, cổng
    trả lại, hôm sau đề xuất lại y hệt. Đã thấy tận mắt hai lượt liên tiếp:

        dinhGia.batDinhToiThieu 0,015 → 0,010
        → TRẢ LẠI: kỳ vọng +24,11 chưa vượt +24,54 đủ biên 1,1×

    Sổ tiến hoá sẽ dài ra mỗi ngày một dòng giống hệt dòng trước, và
    "mạnh hơn mỗi ngày" thành một câu không có gì đỡ.

    Nhớ có HẠN, không nhớ vĩnh viễn: băng đổi, chợ đổi, một ứng viên thua
    hôm nay có thể thắng tháng sau. Hết `soLuot` lượt thì nó được thử lại.
    """
    ra = set()
    for d in doc_so(soLuot):
        for r in (d.get("traLai") or []):
            dx = r.get("deXuat") or {}
            nut, den = dx.get("nut"), dx.get("den")
            if nut is not None and isinstance(den, (int, float)):
                ra.add((nut, round(float(den), 10)))
    return ra


def ung_vien(tc: list[TrieuChung]):
    """Sinh lần lượt mọi ứng viên đáng thử, ưu tiên bệnh nặng, bước ngắn.

    Dò dọc theo chiều mà chẩn đoán chỉ ra: một bước, hai bước, ba bước.
    Đây mới là "quét lưới" đúng nghĩa — bản trước dừng ngay ở bước một.
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
            chieu = _chieu_van(t, duong)
            for k in range(1, TIM_MAY_BUOC + 1):
                moi = kep(duong, hien + chieu * n.buoc * k)
                if moi is None or abs(moi - hien) < 1e-12:
                    continue
                yield t, duong, hien, moi, chieu, k


def _chieu_van(t: TrieuChung, duong: str) -> float:
    """Vặn về phía nào. Tách riêng để đọc được, và để kiểm được."""
    # `dung-ngoai` là bệnh ngược: nới ra. Còn lại thì siết vào.
    chieu = -1.0 if t.ma == "dung-ngoai" else 1.0

    if t.ma == "mo-hinh-lech":
        # Nút giảm chấn là ngoại lệ, và ngoại lệ có lý do: bảng hiệu chỉnh
        # ĐÃ đo được mô hình lệch đi đâu, ở cả hai đuôi. Giảm chấn chỉ
        # quyết đi bao nhiêu phần đường ấy — nên chữa `mo-hinh-lech` bằng
        # nút này luôn là đi XA HƠN, bất kể bệnh là rụt rè hay tự tin.
        # Nhét nó vào cái thang "siết/nới" chung là hiểu sai nó làm gì.
        if duong == "nanLai.heSoGiamChan":
            return 1.0
        # Còn hai nút kia thì TRIỆU CHỨNG ĐÃ BIẾT HƯỚNG, và bản đầu vứt
        # nó đi: chẩn ra "thiên RỤT RÈ QUÁ" rồi đề xuất SIẾT bất định chặt
        # thêm — đúng ngược hướng bệnh. Cổng trả lại nên không hại gì,
        # nhưng một người đề xuất chỉ biết đi một chiều thì mãi mãi không
        # tìm ra chiều kia.
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
    return chieu


def de_xuat_tat_dinh(tc: list[TrieuChung],
                     daThu: set | None = None) -> list[DeXuat]:
    """Người đề xuất KHÔNG cần model: dò lưới dọc theo chiều chẩn đoán chỉ.

    Chọn ứng viên đầu tiên chưa bị cổng trả lại gần đây — ưu tiên bệnh
    nặng nhất, nút nhắm thẳng nhất, bước ngắn nhất. Hết ứng viên mới thì
    trả rỗng và NÓI RA, chứ không lặng lẽ đề nghị lại thứ vừa bị bác.
    """
    daThu = daThu if daThu is not None else da_tra_lai()
    daBo: list[str] = []
    for t, duong, hien, moi_gt, chieu, k in ung_vien(tc):
        if (duong, round(moi_gt, 10)) in daThu:
            daBo.append(f"{duong}={moi_gt:g}")
            continue
        buoc = "một bước" if k == 1 else f"{k} bước"
        return [DeXuat(duong, hien, moi_gt, t.ma,
                       f"dò {buoc} {'siết' if chieu > 0 else 'nới'} "
                       f"để chữa `{t.ma}`")]
    if daBo:
        # Không im lặng. "Hết ứng viên mới" là một trạng thái có thật và
        # đáng đọc — nó nói rằng vùng quanh cấu hình hiện tại đã được đo
        # hết và không chỗ nào khá hơn, chứ không phải vòng tiến hoá hỏng.
        print(f"[tiến hoá 4/7] {len(daBo)} ứng viên đều đã bị trả lại gần "
              f"đây, bỏ qua: {', '.join(daBo[:6])}",
              file=sys.stderr, flush=True)
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

def thu_mot_de_xuat(khung, dx: DeXuat) -> dict:
    """Chạy lại băng với tham số cũ và mới, rồi cho qua cổng.

    ## Cả hai lượt đều chạy KÈM PHÉP NẮN, vì máy thật chạy kèm phép nắn

    Vòng chạy thật đọc `self.phepNan` rồi nắn `gc.pUp` trước khi cân lợi
    (`vong.py`). Cổng thì dựng `ThamSo` không có `phepNan`, nên nó chạy
    lại một cỗ máy KHÔNG nắn — tức là không phải cỗ máy đang chạy.

    Hậu quả có hai tầng, và tầng dưới nặng hơn:

    1. `nanLai.heSoGiamChan` vặn kiểu gì cũng không đổi kết quả chạy lại,
       vì lượt chạy ấy có nắn đâu mà giảm chấn. Một nút nữa nằm trong
       bảng mà không ai vặn được.
    2. Nặng hơn: "đương nhiệm" mà cổng đo KHÔNG PHẢI đương nhiệm. Mọi
       phán quyết cổng từng đưa ra đều là phán quyết về một cỗ máy khác.
       Nó vẫn bác bỏ được (thô so với thô là một phép so hợp lệ), nhưng
       nó trả lời sai câu hỏi đang hỏi.

    Nên nắn được khớp lại ở CẢ HAI phía. Phía B khớp lại SAU khi đổi
    config: `dung_duoc` của phép nắn phụ thuộc chính hệ số giảm chấn, nên
    dùng lại đường khớp của phía A là lặng lẽ đo nhầm lần nữa.
    """
    cl = CONFIG["canLoi"]
    at = float(cl["bienAnToan"])
    net = float(cl["netEdgeToiThieu"])
    pn = nan_lai.khop(HieuChinh())

    # Hai nút này vào thẳng ThamSo; các nút khác đổi CONFIG rồi chạy lại.
    if dx.nut == "canLoi.netEdgeToiThieu":
        a = ThamSo("đương nhiệm", net, at, phepNan=pn)
        b = ThamSo("ứng viên", dx.denGiaTri, at, phepNan=pn)
        kq = doi_chieu(khung, a, b)
    elif dx.nut == "canLoi.bienAnToan":
        a = ThamSo("đương nhiệm", net, at, phepNan=pn)
        b = ThamSo("ứng viên", net, dx.denGiaTri, phepNan=pn)
        kq = doi_chieu(khung, a, b)
    else:
        # Nút không đi qua `ThamSo` mà nằm trong CONFIG. Phải chạy HAI
        # lượt ở HAI trạng thái config khác nhau.
        #
        # Bản đầu đặt config sang giá trị MỚI rồi chạy cả A lẫn B với hai
        # `ThamSo` giống hệt nhau — tức là so một thứ với chính nó. Kết
        # quả luôn "bằng", nên tám trong mười nút vặn được KHÔNG BAO GIỜ
        # qua nổi cổng, bất kể đề xuất đúng hay sai hướng.
        #
        # Đây mới là lý do thật khiến vòng tiến hoá chưa từng nhận gì —
        # nặng hơn cả chuyện thiếu mẫu, vì nó không lộ ra ở đâu cả: cổng
        # vẫn chạy, vẫn in ra một phán quyết, chỉ là phán quyết đó vô nghĩa.
        ka = chay_lai_mot_luot(khung, ThamSo("đương nhiệm", net, at,
                                             phepNan=pn))
        cu = _dat_tham_so(dx.nut, dx.denGiaTri)
        try:
            # Khớp LẠI sau khi đổi config: `dung_duoc` phụ thuộc hệ số
            # giảm chấn, nên đường khớp của phía A không đại diện cho B.
            kb = chay_lai_mot_luot(khung, ThamSo("ứng viên", net, at,
                                                 phepNan=nan_lai.khop(HieuChinh())))
        finally:
            _dat_tham_so(dx.nut, cu)
        kq = gop_doi_chieu(ka, kb)

    A, B = kq["A"], kq["B"]
    ly: list[str] = []

    if not kq["duMau"] or min(A["soKhop"], B["soKhop"]) < TOI_THIEU_MAU:
        ly.append(f"chưa đủ mẫu (A {A['soKhop']}, B {B['soKhop']}, "
                  f"cần {TOI_THIEU_MAU} mỗi bên)")
    else:
        if B["kyVong"] < A["kyVong"] * BIEN_VUOT:
            # Nói rõ ứng viên hơn hay kém, rồi mới nói thiếu bao nhiêu.
            # Bản trước viết "kỳ vọng +26,085 chưa vượt +25,920 đủ biên
            # 1,1×" — đúng chữ nhưng đọc như một lỗi số học, vì hai con
            # số ấy nhìn thoáng là B ĐÃ vượt A. Người đọc mất một lúc mới
            # hiểu ngưỡng là A×1,1 chứ không phải A.
            can = A["kyVong"] * BIEN_VUOT
            ty = (B["kyVong"] / A["kyVong"]) if A["kyVong"] else float("nan")
            ly.append(
                f"kỳ vọng {B['kyVong']:+.5f} "
                f"({'hơn' if B['kyVong'] > A['kyVong'] else 'kém'} đương "
                f"nhiệm {A['kyVong']:+.5f}, tỉ lệ {ty:.3f}×) nhưng cổng "
                f"đòi ≥ {can:+.5f} (biên {BIEN_VUOT:g}×)")
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

    ## Sửa TẠI CHỖ, không viết lại cả file

    Bản đầu nạp JSON, đổi một khoá, rồi `json.dumps(..., indent=2)` đè
    lại. Nó giữ được mọi khoá chú thích `//...` — nhưng mất sạch bố cục
    người ta xếp tay: dòng trống ngăn nhóm, và bốn market viết gọn mỗi
    cái hai dòng. Một lượt vặn đổi đúng một con số mà `git diff` ra 55
    thêm / 32 xoá.

    Và đây là việc chạy MỖI NGÀY. File cấu hình bị xáo lại hằng ngày thì
    không ai còn đọc được `git log` của nó, mà `git log` của config chính
    là biên niên sử của vòng tiến hoá.

    Nên: tìm đúng dòng, thay đúng con số, đụng vào không gì khác.

    ## Và ĐỌC LẠI để chắc là đã đổi thật

    Sửa văn bản thì có đường thất bại mà JSON không có: khớp nhầm một
    khoá cùng tên ở nhánh khác, hoặc không khớp gì cả. Nên sau khi ghi
    thì nạp lại và đối chiếu; không khớp thì trả file về như cũ và báo
    hỏng, chứ không để lại một file nửa vời.
    """
    p = ROOT / "config.json"
    try:
        tho = p.read_text(encoding="utf-8")
        d = json.loads(tho)
    except (OSError, json.JSONDecodeError):
        return False

    k = duong.split(".")
    n = d
    for x in k[:-1]:
        if x not in n or not isinstance(n[x], dict):
            return False
        n = n[x]
    if k[-1] not in n:
        return False

    moi_tho = _thay_tai_cho(tho, k, gt)
    if moi_tho is None:
        return False
    try:
        kiem = json.loads(moi_tho)
    except json.JSONDecodeError:
        return False
    doc = kiem
    for x in k[:-1]:
        doc = doc.get(x) or {}
    if abs(float(doc.get(k[-1], 0)) - float(gt)) > 1e-12:
        return False

    p.write_text(moi_tho, encoding="utf-8")
    _dat_tham_so(duong, gt)
    return True


def _thay_tai_cho(tho: str, k: list[str], gt) -> str | None:
    """Thay giá trị của khoá `k` trong văn bản JSON, giữ nguyên phần còn lại.

    Đi theo ĐƯỜNG chứ không tìm tên khoá khắp file: `netEdgeToiThieu` có
    thể xuất hiện ở nhiều nhánh, và thay nhầm nhánh là đổi một tham số
    không ai yêu cầu.
    """
    import re

    vi = 0
    for cha in k[:-1]:
        m = re.compile(r'"' + re.escape(cha) + r'"\s*:\s*\{').search(tho, vi)
        if m is None:
            return None
        vi = m.end()

    m = re.compile(r'("' + re.escape(k[-1]) + r'"\s*:\s*)(-?[0-9.eE+]+)'
                   ).search(tho, vi)
    if m is None:
        return None
    so = repr(gt)
    if isinstance(gt, float) and gt.is_integer():
        so = str(int(gt))
    return tho[:m.start()] + m.group(1) + so + tho[m.end():]


# ══════════════════════════════════════════════════════════════════════════
#  VÒNG
# ══════════════════════════════════════════════════════════════════════════

def _buoc(so: int, ten: str) -> None:
    """Kêu lên mình đang ở bước nào. Bảy bước, mỗi bước quét lại cả băng."""
    global _MOC
    gio = time.time()
    troi = gio - _MOC
    _MOC = gio
    dong = f"[tiến hoá {so}/7] {ten}" + (f"  (+{troi:.0f}s)" if so > 1 else "")
    print(dong, file=sys.stderr, flush=True)
    try:
        from .bus import bus
        bus.ghi(dong, loai="tin")
    except Exception:      # noqa: BLE001
        pass


def mot_luot(thu: bool = False, tuNgay: str | None = None) -> KetQuaTienHoa:
    global _MOC
    _MOC = time.time()
    kq = KetQuaTienHoa(luc=bay_gio(), soKhungBang=0, soLenhKetToan=0)

    _buoc(1, "thu hoạch: quét băng đếm lý do đứng ngoài")
    # 1–2. thu hoạch + đo
    #
    # `NguonKhung` chứ KHÔNG `doc_bang`. Đo trên băng 8 ngày: nạp cả băng
    # mất 77 giây và 3,4 GB thường trú, rồi vòng này quét lại nó ba tới
    # bốn lượt trong khi vẫn giữ nguyên khối ấy. Máy lún xuống swap và
    # một lượt tiến hoá chạy quá hai mươi phút mà chưa in nổi dòng đầu —
    # trong khi đây là thứ phải chạy được MỖI NGÀY, không ai ngồi canh.
    # Hạn giữ băng là 30 ngày, nên đường đi của cách cũ là hết bộ nhớ.
    khung = NguonKhung(tuNgay)
    so = So()
    ket = so.doc(5000)
    hc = HieuChinh()
    kq.soLenhKetToan = len(ket)

    tk = thong_ke(ket)
    kq.kyVongTruoc = None if tk.get("chuaCo") else tk["kyVong"]

    # Lượt quét đầu; sau nó `khung.soKhung` mới có số.
    bo_qua = _dem_bo_qua(khung)
    soQuanSat = bo_qua.pop("_soQuanSat", 0)
    kq.soKhungBang = khung.soKhung
    _buoc(2, f"đo: {kq.soKhungBang} khung, sổ thật {len(ket)} lệnh")

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
    if len(ket) < TOI_THIEU_MAU and kq.soKhungBang and not soQuanSat:
        # Băng không có DÒNG NÀO thuộc khung ăn thua, mà đó là loại duy
        # nhất `chay_lai` chấm được. Ba lượt quét băng phía sau chắc chắn
        # trả về 0 khớp — bỏ chúng đi và NÓI RA, thay vì đốt vài phút mỗi
        # ngày để tới cùng một chỗ.
        _buoc(3, "băng không có dòng khung ăn thua — bỏ qua phần chạy lại")
        kq.ghiChu = (
            f"băng {kq.soKhungBang:,} khung nhưng KHÔNG dòng nào thuộc khung "
            "ăn thua, nên cổng tiền không có gì để chấm. Đường tới chợ đứt "
            "thì đây là trạng thái đúng — nửa vòng học từ Binance vẫn chạy.")
        kq.trieuChung = [{"ma": "thieu-mau", "nang": 1,
                          "moTa": kq.ghiChu,
                          "bangChung": {"soKhungBang": kq.soKhungBang,
                                        "soDongQuanSat": 0},
                          "nutGoiY": []}]
        if not thu:
            _ghi_so(kq)
        return kq

    if len(ket) < TOI_THIEU_MAU and kq.soKhungBang:
        cl = CONFIG["canLoi"]
        _buoc(2, "sổ thật còn mỏng — dựng mẫu bằng CHẠY LẠI trên băng")
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

    _buoc(3, f"chẩn trên {len(ket)} mẫu ({nguonMau})")
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

    _buoc(4, "đề xuất")
    # 4. đề xuất — model trước, tất định là lưới đỡ
    db = de_bai(tc, {n.duong: doc_tham_so(n.duong) for n in NUT_VAN})
    daThu = da_tra_lai()
    dx = de_xuat_bang_model(db) or de_xuat_tat_dinh(tc, daThu)
    kq.deXuat = [d.tom_tat() for d in dx]
    kq.daThu = len(daThu)
    if not dx:
        kq.ghiChu = (
            f"vùng quanh cấu hình hiện tại đã dò hết: {len(daThu)} ứng viên "
            f"đều đã đo và bị trả lại trong {NHO_MAY_LUOT} lượt gần đây. "
            "Đứng yên vì ĐÃ THỬ, không phải vì chưa nghĩ ra."
            if daThu else "không nghĩ ra đề xuất nào hợp lệ")
        if not thu:
            _ghi_so(kq)
        return kq

    _buoc(5, f"thử {len(dx)} đề xuất qua cổng — mỗi đề xuất quét băng HAI lượt")
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
    """Đếm lý do bỏ qua trong băng — nguyên liệu cho triệu chứng `dung-ngoai`.

    Đếm luôn số dòng KHUNG ĂN THUA vào khoá `_soQuanSat`. Cổng tiền chỉ
    chấm được dòng ấy; bằng 0 thì mọi lượt chạy lại phía sau chắc chắn
    trả về 0 khớp, và ba lượt quét băng ấy là công cốc — mỗi ngày.
    """
    ra: dict[str, int] = {"_soQuanSat": 0}
    for k in khung:
        for tt in (k.get("thiTruong") or []):
            if giai_doan_cua(tt) != "dat-cuoc":
                if giai_doan_cua(tt) == "quan-sat":
                    ra["_soQuanSat"] += 1
                continue
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
