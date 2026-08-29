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

#: SÀN của bước vặn, tính theo BỀ RỘNG khuôn của núm.
#:
#: Bước nhân theo giá trị hiện tại (`hien × 0,25`) có một chỗ chết: núm nào
#: đang ở gần 0 thì bước cũng gần 0, và nó KHÔNG BAO GIỜ đi được đâu.
#: `netToiThieuBps` xuất phát 0,5 nên bước đầu là 0,125 — đổi ngưỡng ngần
#: ấy thì kỳ vọng nhích vài phần trăm bps, dưới `BIEN_VUOT` 0,15, nên lượt
#: nào cũng bị TRẢ LẠI. Đo trên băng thật: 0,5 → 15 cải thiện 0,56 bps, thừa
#: sức vượt biên nhiễu; nhưng đi bằng bước nhân thì phải qua ~20 lượt mà
#: lượt nào cũng nhỏ hơn nhiễu. Cỗ máy ĐO ĐƯỢC đích nhưng không bước tới
#: được — và nó im lặng, vì mỗi lượt trả lại đều trông như một quyết định
#: thận trọng đúng đắn.
#:
#: 5% bề rộng khuôn: đủ để một lượt tạo ra khác biệt đo được, vẫn đủ nhỏ để
#: cần hai chục lượt mới đi hết khuôn.
SAN_BUOC_KHUON = 0.05


def buoc_van(nut: str, hien: float) -> float:
    """Bước vặn của một núm — LỚN HƠN trong hai cách tính.

    Nhân theo giá trị hiện tại giữ cho núm lớn không nhảy quá xa; sàn theo
    bề rộng khuôn giữ cho núm nhỏ không đứng yên mãi.
    """
    k = NUT_VAN[nut]
    return max(abs(hien) * BUOC_TOI_DA,
               (float(k["max"]) - float(k["min"])) * SAN_BUOC_KHUON)

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
    #: Lượt THỬ (không ghi tham số) hay lượt THẬT. Phải nằm trong sổ, không
    #: thì đọc lại một dòng «NHẬN giuGio 8→6» mà không biết nó đã được áp
    #: hay chỉ là một lượt diễn tập — và hai thứ ấy khác nhau hoàn toàn.
    thu: bool = True

    def tom_tat(self) -> dict:
        return {
            "luc": self.luc, "soKhungBang": self.soKhungBang,
            "soDoDuoc": self.soDoDuoc,
            "kyVongTruoc": self.kyVongTruoc, "kyVongSau": self.kyVongSau,
            "trieuChung": list(self.trieuChung), "deXuat": list(self.deXuat),
            "nhan": self.nhan, "traLai": list(self.traLai),
            "ghiChu": self.ghiChu, "thu": self.thu,
        }


# ══════════════════════════════════════════════════════════════════════════
#  ĐỀ XUẤT — tất định, không gọi model
# ══════════════════════════════════════════════════════════════════════════
def de_xuat_tat_dinh(trieuChung: list, ts: ThamSo,
                     daTraLai=()) -> list[DeXuat]:
    """Từ triệu chứng ra đề xuất. Cùng đầu vào luôn cho cùng đầu ra.

    Không gọi model, và đó là chủ ý: một cỗ máy tự vặn tham số của chính mình
    phải dựng lại được từng quyết định. Model có thể vào ở tầng GIẢI THÍCH
    (`vì sao chênh lệch đổi`), không vào ở tầng quyết định.

    ## `daTraLai` — vì sao vòng lặp từng kẹt ở đúng một đề xuất

    Đo trên máy sống 29/08: triệu chứng nặng nhất là `du-doan-lac-quan`, núm
    của nó là `giuGio`, đề xuất 8→6, chạy lại đo ra TỆ HƠN, trả lại. Lượt
    sau: cùng dữ liệu, cùng triệu chứng, cùng đề xuất, cùng kết quả. Mãi
    mãi. Núm `netToiThieuBps` — thứ mà một phép quét tay cho thấy có cải
    thiện thật — không bao giờ tới lượt, vì nó thuộc một triệu chứng nhẹ
    hơn và hàm này chỉ trả về đúng cái đầu tiên.

    Truyền vào những đề xuất ĐÃ ĐO VÀ ĐÃ TRẢ LẠI thì lượt sau đi tiếp
    xuống ứng viên kế. Vẫn ĐÚNG MỘT đề xuất mỗi lượt — luật «vặn hai núm
    rồi khá lên thì không biết núm nào có công» không đổi.

    Thứ tự ứng viên là TẤT ĐỊNH (theo độ nặng triệu chứng), không theo kết
    quả đo. Đó là khác biệt giữa "thử lần lượt theo một danh sách đã định
    trước" và "thử hết rồi chọn cái đẹp nhất" — cái sau là tự lừa bằng
    nhiều phép so sánh, và hàm này không làm thế.
    """
    bo = {(str(x.get("nut")), round(float(x.get("den", 0.0)), 9))
          for x in (daTraLai or []) if isinstance(x, dict)}
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
            moi = _kep(nut, hien + huong * buoc_van(nut, hien))
            if abs(moi - hien) < 1e-9:
                continue                       # đã chạm biên, không đề xuất
            if (nut, round(moi, 9)) in bo:
                continue                       # đã đo rồi và đã trả lại
            ra.append(DeXuat(nut, hien, moi, t.ma))
            break                              # luật 2: mỗi triệu chứng MỘT núm
    # Luật 2 lần nữa, ở tầng lượt: chỉ giữ đề xuất của triệu chứng NẶNG nhất
    # trong số những cái CHƯA bị trả lại.
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
    kq = KetQuaTienHoa(luc=bay_gio(), thu=bool(thu))
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
        _ghi_so(kq)
        return kq

    # 4. đề xuất — bỏ qua những cái đã đo và đã trả lại trên MẪU KHÔNG LỚN
    # HƠN mẫu hiện tại. Băng dài thêm thì một đề xuất từng bị trả lại đáng
    # được đo lại: nó bị trả vì chưa đủ bằng chứng, không phải vì đã có
    # bằng chứng ngược.
    daTra = []
    for x in doc_so(200):
        if int(x.get("soKhungBang") or 0) > kq.soKhungBang:
            continue
        daTra.extend(x.get("traLai") or [])
    dx = de_xuat_tat_dinh(tc, goc, daTra)
    kq.deXuat = [d.tom_tat() for d in dx]
    if not dx:
        kq.ghiChu = "có triệu chứng nhưng không núm nào hợp lệ để vặn."
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
    """Ghi CẢ lượt trả lại, không chỉ lượt nhận — và cả lượt THỬ.

    Sổ chỉ ghi lượt thành công là một lịch sử toàn thắng lợi, và nó giấu mất
    thứ đáng đọc nhất: bao nhiêu lần đề xuất bị nhiễu đánh lừa mà cổng đã
    chặn được.

    Bản đầu còn bỏ luôn mọi lượt THỬ, và hệ quả tệ hơn hẳn: vòng chạy tự
    động phải chạy ở chế độ thử (nó không được tự vặn tham số khi chưa ai
    cho phép), nên nó chạy mà **không để lại dấu vết nào**. Nhìn vào
    `duong_tien_hoa()` thấy `soLuot: 0` và kết luận vòng chưa bao giờ quay —
    trong khi nó quay đều. Một cơ chế chạy mà không ghi thì với người đọc
    nó bằng một cơ chế không chạy.

    `thu` nằm trong mỗi dòng, nên đọc lại phân biệt được ngay lượt diễn tập
    với lượt đã áp thật.
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
