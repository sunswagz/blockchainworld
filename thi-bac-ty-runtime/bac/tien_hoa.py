"""Vòng tiến hoá — bảy bước, và chỗ dễ tự lừa nhất trong cả runtime.

    1. thu hoạch   đọc băng
    2. đo          chạy lại với tham số HIỆN TẠI → kỳ vọng nền
    3. chẩn        triệu chứng đo được (chan_doan.py)
    4. đề xuất     mỗi triệu chứng gợi ý núm nào, vặn theo hướng nào
    5. thử         chạy lại A/B trên CÙNG băng
    6. quyết       nhận hay trả lại, theo luật ở dưới
    7. ghi sổ      kể cả khi trả lại — nhất là khi trả lại

## Bốn luật, và mỗi luật chặn một cách tự lừa

**1. Không núm nào chạm tới cửa AN TOÀN.** `doiHoiHaiMark`,
`doiHoiItNhatMotMoc`, `nhanUocLuongMoc`, `lechDongHoToiDaGiay` không nằm
trong `NUT_VAN`. Chúng không phải ngưỡng hiệu năng — chúng là câu "ta không
biết đủ để vào lệnh". Cho vòng tiến hoá nới chúng ra là dạy nó rằng đường
nhanh nhất tới điểm cao là **tắt đèn báo**, và nó sẽ tìm ra ngay.

Phí cũng không có ở đây. Phí là sự thật về thế giới, không phải núm.

**2. Một lượt vặn ĐÚNG MỘT núm.** Vặn hai núm rồi thấy khá lên thì không
biết núm nào có công — và lượt sau sẽ vặn tiếp cả hai theo cùng hướng, kể
cả cái đang làm hại.

**3. Bước nhỏ, có trần.** Mỗi lượt dịch tối đa `BUOC_TOI_DA` phần, và không
bao giờ ra ngoài `[min, max]` của núm. Không trần thì một lượt gặp nhiễu
thuận có thể đẩy ngưỡng ra chỗ mà mọi cơ hội đều qua cửa.

**4. Nhận chỉ khi ĐỦ MẪU và cải thiện VƯỢT NHIỄU.** Cần ≥30 cơ hội hậu
kiểm được ở cả hai bên, và cải thiện phải vượt `BIEN_VUOT`. Thiếu một trong
hai thì trả lại — và **đứng yên là một kết quả hợp lệ**, không phải thất bại.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .bang import doc_bang
from .chan_doan import chan_doan
from .chay_lai import ThamSo, doi_chieu, mot_luot
from .config import CONFIG, DATA_DIR
from .models import bay_gio

SO_TIEN_HOA = DATA_DIR / "tien-hoa.jsonl"

#: Cải thiện phải vượt ngần này (bps kỳ vọng) mới coi là thật, không phải
#: nhiễu. Đặt thấp hơn thì vòng tiến hoá sẽ "tiến bộ" mỗi ngày mà tổng lại
#: không đi đâu cả — đúng kiểu tự lừa khó thấy nhất.
BIEN_VUOT = 0.15

#: Mỗi lượt dịch tối đa bấy nhiêu phần giá trị hiện tại.
BUOC_TOI_DA = 0.25

#: Cần bấy nhiêu cơ hội hậu kiểm được ở CẢ HAI bên mới dám kết luận.
TOI_THIEU_MAU = 30

#: Núm vặn được. **Cửa an toàn cố ý KHÔNG có ở đây** — xem luật 1 đầu file.
NUT_VAN = {
    "giuGio":               {"min": 0.5,  "max": 24.0, "o": "goc"},
    "grossToiThieuBpsNgay": {"min": 0.5,  "max": 60.0, "o": "ruiRo"},
    "netToiThieuBps":       {"min": -5.0, "max": 40.0, "o": "ruiRo"},
    "lechMarkToiDaBps":     {"min": 5.0,  "max": 120.0, "o": "ruiRo"},
    "tuoiToiDaGiay":        {"min": 15.0, "max": 300.0, "o": "ruiRo"},
}

#: Cửa an toàn — liệt kê tường minh để phép kiểm bắt được nếu ai đó lỡ đưa
#: một trong số chúng vào `NUT_VAN`.
CUA_AN_TOAN = ("doiHoiHaiMark", "doiHoiItNhatMotMoc", "nhanUocLuongMoc",
               "lechDongHoToiDaGiay")


@dataclass
class DeXuat:
    nut: str
    tu: float
    den: float
    vi: str                      # mã triệu chứng đẻ ra đề xuất này

    def tom_tat(self) -> dict:
        return {"nut": self.nut, "tu": self.tu, "den": self.den, "vi": self.vi}


@dataclass
class KetQuaTienHoa:
    luc: str
    soKhungBang: int = 0
    soDoDuoc: int = 0
    kyVongTruoc: float | None = None
    kyVongSau: float | None = None
    trieuChung: list = field(default_factory=list)
    deXuat: list = field(default_factory=list)
    nhan: dict | None = None
    traLai: list = field(default_factory=list)
    ghiChu: str = ""

    def tom_tat(self) -> dict:
        return {
            "luc": self.luc, "soKhungBang": self.soKhungBang,
            "soDoDuoc": self.soDoDuoc,
            "kyVongTruoc": self.kyVongTruoc, "kyVongSau": self.kyVongSau,
            "trieuChung": list(self.trieuChung), "deXuat": list(self.deXuat),
            "nhan": self.nhan, "traLai": list(self.traLai),
            "ghiChu": self.ghiChu,
        }


# ══════════════════════════════════════════════════════════════════════════
#  ĐỀ XUẤT — tất định, không gọi model
# ══════════════════════════════════════════════════════════════════════════
def de_xuat_tat_dinh(trieuChung: list, ts: ThamSo) -> list[DeXuat]:
    """Từ triệu chứng ra đề xuất. Cùng đầu vào luôn cho cùng đầu ra.

    Không gọi model, và đó là chủ ý: một cỗ máy tự vặn tham số của chính mình
    phải dựng lại được từng quyết định. Model có thể vào ở tầng GIẢI THÍCH
    (`vì sao chênh lệch đổi`), không vào ở tầng quyết định.
    """
    ra: list[DeXuat] = []
    for t in trieuChung:
        for nut in (t.nutGoiY or []):
            if nut not in NUT_VAN:
                continue                       # cửa an toàn: bỏ qua, im lặng
            hien = _doc_nut(ts, nut)
            if hien is None:
                continue
            huong = _huong(t.ma, nut)
            if huong == 0:
                continue
            moi = _kep(nut, hien * (1.0 + huong * BUOC_TOI_DA))
            if abs(moi - hien) < 1e-9:
                continue                       # đã chạm biên, không đề xuất
            ra.append(DeXuat(nut, hien, moi, t.ma))
            break                              # luật 2: mỗi triệu chứng MỘT núm
    # Luật 2 lần nữa, ở tầng lượt: chỉ giữ đề xuất của triệu chứng NẶNG nhất.
    return ra[:1]


def _huong(maTrieuChung: str, nut: str) -> int:
    """Vặn lên (+1) hay xuống (−1). 0 = không biết, đừng vặn."""
    return {
        # cửa quá chặt → nới ngưỡng xuống để có mẫu mà học
        ("cua-qua-chat", "grossToiThieuBpsNgay"): -1,
        ("cua-qua-chat", "netToiThieuBps"): -1,
        ("cua-qua-chat", "lechMarkToiDaBps"): +1,
        ("cua-qua-chat", "tuoiToiDaGiay"): +1,
        ("cua-qua-chat", "giuGio"): +1,
        # dự đoán lạc quan → giữ ngắn lại, funding chưa kịp tụt
        ("du-doan-lac-quan", "giuGio"): -1,
        ("du-doan-lac-quan", "netToiThieuBps"): +1,
        # lỗ → siết
        ("ky-vong-am", "netToiThieuBps"): +1,
        ("ky-vong-am", "grossToiThieuBpsNgay"): +1,
        ("ky-vong-am", "giuGio"): -1,
        ("duoi-nang", "netToiThieuBps"): +1,
        # cửa sổ hụt mốc → kéo dài ra cho chạm được mốc
        ("cua-so-hut-moc", "giuGio"): +1,
    }.get((maTrieuChung, nut), 0)


def _doc_nut(ts: ThamSo, nut: str) -> float | None:
    o = NUT_VAN[nut]["o"]
    v = ts.giuGio if o == "goc" else (ts.ruiRo or {}).get(nut)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _kep(nut: str, v: float) -> float:
    n = NUT_VAN[nut]
    return max(float(n["min"]), min(float(n["max"]), v))


def dat_nut(ts: ThamSo, nut: str, gt: float, ten: str) -> ThamSo:
    """Bản sao của `ts` với đúng MỘT núm đổi."""
    rui = dict(ts.ruiRo or {})
    giu = ts.giuGio
    if NUT_VAN[nut]["o"] == "goc":
        giu = gt
    else:
        rui[nut] = gt
    return ThamSo(ten=ten, giuGio=giu, ruiRo=rui)


# ══════════════════════════════════════════════════════════════════════════
#  MỘT LƯỢT
# ══════════════════════════════════════════════════════════════════════════
def tham_so_hien_tai() -> ThamSo:
    return ThamSo(ten="hiện tại",
                  giuGio=float(CONFIG["quet"]["giuGio"]),
                  ruiRo=dict(CONFIG["ruiRo"]))


def mot_luot(thu: bool = True, tuNgay: str | None = None) -> KetQuaTienHoa:
    """Một lượt tiến hoá. `thu=True` (mặc định) thì KHÔNG ghi gì.

    Mặc định là chế độ thử, và đó là chủ ý: một nút bấm nhầm không được phép
    vặn tham số của cỗ máy. Muốn ghi thật phải truyền `thu=False`.
    """
    kq = KetQuaTienHoa(luc=bay_gio())
    khung = doc_bang(tuNgay)
    kq.soKhungBang = len(khung)
    phi = CONFIG["san"]
    goc = tham_so_hien_tai()

    # 2. đo nền
    nen = mot_luot_chay_lai(khung, goc, phi)
    kq.soDoDuoc = nen.soDoDuoc
    kq.kyVongTruoc = nen.ky_vong_bps

    # 3. chẩn
    tc = chan_doan(nen)
    kq.trieuChung = [t.tom_tat() for t in tc]

    if all(t.ma in ("khoe", "thieu-mau", "dong-ho-lech") for t in tc):
        kq.ghiChu = ("không bệnh nào vặn tham số chữa được — không vặn gì. "
                     "Vòng tiến hoá đứng yên là một kết quả hợp lệ.")
        if not thu:
            _ghi_so(kq)
        return kq

    # 4. đề xuất
    dx = de_xuat_tat_dinh(tc, goc)
    kq.deXuat = [d.tom_tat() for d in dx]
    if not dx:
        kq.ghiChu = "có triệu chứng nhưng không núm nào hợp lệ để vặn."
        if not thu:
            _ghi_so(kq)
        return kq

    # 5–6. thử rồi quyết
    d = dx[0]
    moi = dat_nut(goc, d.nut, d.den, f"{d.nut}={d.den:g}")
    so = doi_chieu(khung, goc, moi, phi)
    kq.kyVongSau = (so["B"] or {}).get("kyVongBps")

    if not so["duMau"]:
        kq.traLai.append({**d.tom_tat(), "vi": "chưa đủ mẫu",
                          "chiTiet": so["ghiChu"]})
        kq.ghiChu = so["ghiChu"]
    elif so["caiThienBps"] is None or so["caiThienBps"] < BIEN_VUOT:
        kq.traLai.append({
            **d.tom_tat(), "vi": "cải thiện không vượt nhiễu",
            "caiThienBps": so["caiThienBps"], "bienVuot": BIEN_VUOT})
        kq.ghiChu = (f"đề xuất {d.nut} {d.tu:g}→{d.den:g} chỉ cải thiện "
                     f"{so['caiThienBps']:.3f} bps < biên vượt {BIEN_VUOT} — trả lại.")
    else:
        kq.nhan = {**d.tom_tat(), "caiThienBps": so["caiThienBps"]}
        kq.ghiChu = (f"NHẬN {d.nut} {d.tu:g}→{d.den:g}, cải thiện "
                     f"{so['caiThienBps']:.3f} bps trên {so['B']['soDoDuoc']} mẫu.")
        if not thu:
            _ghi_cau_hinh(d.nut, d.den)

    if not thu:
        _ghi_so(kq)
    return kq


def mot_luot_chay_lai(khung, ts, phi):
    """Bọc `chay_lai.mot_luot` — tách ra để phép kiểm cắm bản giả vào được."""
    from .chay_lai import mot_luot as _cl
    return _cl(khung, ts, phi)


# ══════════════════════════════════════════════════════════════════════════
#  GHI
# ══════════════════════════════════════════════════════════════════════════
def _ghi_cau_hinh(nut: str, gt: float) -> None:
    """Ghi núm đã nhận vào `config.json`. Chỉ gọi khi `thu=False`."""
    p = Path(__file__).resolve().parent.parent / "config.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return
    if NUT_VAN[nut]["o"] == "goc":
        d.setdefault("quet", {})[nut] = gt
        CONFIG["quet"][nut] = gt
    else:
        d.setdefault("ruiRo", {})[nut] = gt
        CONFIG["ruiRo"][nut] = gt
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")


def _ghi_so(kq: KetQuaTienHoa) -> None:
    """Ghi CẢ lượt trả lại, không chỉ lượt nhận.

    Sổ chỉ ghi lượt thành công là một lịch sử toàn thắng lợi, và nó giấu mất
    thứ đáng đọc nhất: bao nhiêu lần đề xuất bị nhiễu đánh lừa mà cổng đã
    chặn được.
    """
    try:
        SO_TIEN_HOA.parent.mkdir(parents=True, exist_ok=True)
        with SO_TIEN_HOA.open("a", encoding="utf-8") as f:
            f.write(json.dumps(kq.tom_tat(), ensure_ascii=False) + "\n")
    except (OSError, TypeError, ValueError):
        pass


def doc_so(n: int = 60) -> list[dict]:
    if not SO_TIEN_HOA.exists():
        return []
    ra = []
    try:
        for d in SO_TIEN_HOA.read_text(encoding="utf-8").splitlines():
            d = d.strip()
            if not d:
                continue
            try:
                ra.append(json.loads(d))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return ra[-n:]


def duong_tien_hoa() -> dict:
    """Sổ tiến hoá gộp — có mạnh hơn thật không, bằng số."""
    ds = doc_so(500)
    nhan = [x for x in ds if x.get("nhan")]
    tra = [x for x in ds if x.get("traLai")]
    cai = [x["nhan"].get("caiThienBps") for x in nhan
           if isinstance(x.get("nhan"), dict)
           and x["nhan"].get("caiThienBps") is not None]
    return {
        "soLuot": len(ds),
        "soLanNhan": len(nhan),
        "soLanTraLai": len(tra),
        "soLanDungYen": len(ds) - len(nhan) - len(tra),
        "tongCaiThien": sum(cai) if cai else None,
        "chuoi": [{"luc": x.get("luc"), "nhan": x.get("nhan"),
                   "ghiChu": x.get("ghiChu")} for x in ds[-12:]],
        "ganNhat": ds[-1] if ds else None,
    }
