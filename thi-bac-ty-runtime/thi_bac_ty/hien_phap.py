"""HIẾN PHÁP — luật vận hành, viết dưới dạng CHẠY ĐƯỢC.

## Vì sao không phải một tệp nguyên tắc

Kho này đã tự chứng minh rằng nguyên tắc nằm trong văn xuôi thì không giữ
được gì. `bac/rui_ro.py` từng khai ba cửa mà `xet()` không hề đọc tới; buồng
lái bày chúng dưới nhãn *"cửa đang có hiệu lực"* suốt nhiều tuần. Không ai
cố tình nói dối — chỉ là luật ở một chỗ và mã ở chỗ khác, và hai chỗ ấy trôi
xa nhau mà không gì báo.

Đúng dạng ấy lặp lại bốn lần nữa chỉ trong một phiên:

    docstring cầu dao khai "ba trong mười" trong khi mã nối bốn
    `trung_uong` khai "không nhảy cóc" trong khi `_hop_le` cho nhảy cóc
    lớp bọc che `kiem_khai` của ty thật
    lớp bọc che `vonToiThieuKinhTeUsd` của ty thật

Nguyên tắc chỉ nằm trong văn xuôi CHÍNH LÀ kiểu hỏng mà cả runtime này sinh
ra để bắt: **hệ thống nói về chính mình một điều không đúng.**

## Nên mỗi điều mang theo phép canh của nó

    ma      tên ngắn, để gọi trong nhật ký và trong lời từ chối
    cau     luật, viết cho người đọc
    vi      CHUYỆN ĐÃ XẢY RA dạy ra luật ấy — phần đáng giá nhất
    kiem    hàm canh, hoặc `None`
    nguon   luật này đến từ đâu

## Điều KHÔNG canh được phải khai ra là không canh được

Đây là phần quan trọng nhất, và là thứ một tệp nguyên tắc không làm được.

Một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì tệ hơn không
có: người đọc tưởng mình được che hai mươi điều trong khi thật ra được che
mười lăm. `soat()` tách rõ hai nhóm, và `tom_tat()` in cả số điều KHÔNG
canh được lên đầu.

Đó chính là bài học của ba cửa giả, nâng lên tầm cả hệ thống.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Dieu:
    ma: str
    cau: str
    vi: str
    nguon: str
    kiem: object = None          # () -> (bool, str) | None = chưa canh được

    def soat(self) -> dict:
        if self.kiem is None:
            return {"ma": self.ma, "canhDuoc": False, "dat": None,
                    "chiTiet": "", "cau": self.cau, "vi": self.vi,
                    "nguon": self.nguon}
        try:
            dat, ct = self.kiem()
        except Exception as e:                            # noqa: BLE001
            dat, ct = False, f"phép canh NỔ: {type(e).__name__}: {e}"
        return {"ma": self.ma, "canhDuoc": True, "dat": bool(dat),
                "chiTiet": str(ct), "cau": self.cau, "vi": self.vi,
                "nguon": self.nguon}


# ══════════════════════════════════════════════════════════════════════
#  Phép canh
# ══════════════════════════════════════════════════════════════════════

def _doc(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def _goi_ty() -> list[Path]:
    """Thư mục TY: gói nào có một lớp kế thừa `khuon_ty.Ty`.

    Nhận diện theo CẤU TRÚC, không theo một danh sách loại trừ. Danh sách
    loại trừ đòi người ta nhớ cập nhật nó, và lần quên đầu tiên đã xảy ra
    ngay: `phai_sinh_chung/` ra đời thì phép canh coi nó là một ty, rồi báo
    `bac` đang "gọi thẳng một ty khác" — trong khi `bac` chỉ đang dùng hạ
    tầng của chính họ mình.

    Một ty thì `import ... khuon_ty ... Ty` và kế thừa nó; hạ tầng thì
    không. Đó là khác biệt thật, và nó tự đúng khi thêm gói mới.
    """
    ra = []
    for d in sorted(GOC.iterdir()):
        if (not d.is_dir() or not (d / "__init__.py").exists()
                or d.name.startswith((".", "_"))
                or d.name in ("thi_bac_ty", "scripts", "web", "dichvu")):
            continue
        for p in d.glob("*.py"):
            s = _doc(p)
            if "khuon_ty import" in s and re.search(
                    r"\nclass \w+\(Ty\):", s):
                ra.append(d)
                break
    return ra


def _trung_uong_khong_biet_ty():
    xau = []
    for p in (GOC / "thi_bac_ty").glob("*.py"):
        ten_ty = {d.name for d in _goi_ty()}
        for dong in _doc(p).splitlines():
            d = dong.strip()
            for t in ten_ty:
                if d.startswith((f"import {t}", f"from {t}")):
                    xau.append(f"{p.name}: {d}")
    return (not xau), ("; ".join(xau) if xau else
                       f"trung ương không import ty nào ({len(_goi_ty())} ty)")


def _ty_khong_goi_ty():
    ten = {d.name for d in _goi_ty()}
    xau = []
    for d in _goi_ty():
        for p in d.glob("*.py"):
            for dong in _doc(p).splitlines():
                s = dong.strip()
                for k in ten - {d.name}:
                    if s.startswith((f"import {k}", f"from {k}")):
                        xau.append(f"{d.name}/{p.name}: {s}")
    return (not xau), ("; ".join(xau) if xau else
                       "không ty nào gọi thẳng ty khác")


def _ty_khong_tu_quan_von():
    """Ty không được có sổ cái, ví, danh mục hay lớp đặt lệnh của riêng nó."""
    CAM = {"so_cai": "sổ cái", "danh_muc": "danh mục", "vi.py": "ví",
           "dat_lenh": "lớp đặt lệnh", "ket_toan": "kế toán",
           "rui_ro_tong": "rủi ro tổng"}
    xau = []
    for d in _goi_ty():
        for p in d.glob("*.py"):
            for k, nhan in CAM.items():
                if k.rstrip(".py") in p.stem or p.name == k:
                    xau.append(f"{d.name}/{p.name} ({nhan})")
    return (not xau), ("; ".join(xau) if xau else
                       "không ty nào tự dựng sổ cái, ví, danh mục hay lớp đặt lệnh")


def _so_cai_chi_them():
    s = _doc(GOC / "thi_bac_ty" / "so_cai.py")
    xau = [x for x in ("UPDATE but_toan", "DELETE FROM but_toan") if x in s]
    return (not xau), ("; ".join(xau) if xau else
                       "sổ cái không có UPDATE lẫn DELETE — sửa chỉ bằng dao()")


def _mo_phong_cung():
    s = _doc(GOC / "thi_bac_ty" / "thuc_thi.py")
    return ("self.moPhong = True" in s), (
        "moPhong gán True CỨNG" if "self.moPhong = True" in s
        else "moPhong ĐỌC TỪ THAM SỐ — một cấu hình có thể bật lệnh thật")


def _doi_ten_nguoi():
    """Ba hành động phải có tên người: đóng cầu dao, áp tham số, quay lui."""
    import inspect
    from .cau_dao import CauDao
    from .trung_uong import TrungUong
    thieu = []
    for lop, ten_ham in ((CauDao, "dong_lai"), (TrungUong, "ap_dung"),
                         (TrungUong, "quay_lui")):
        sig = inspect.signature(getattr(lop, ten_ham))
        p = sig.parameters.get("nguoi")
        if p is None or p.default is not inspect.Parameter.empty:
            thieu.append(f"{lop.__name__}.{ten_ham}")
    return (not thieu), ("; ".join(thieu) if thieu else
                         "cả ba hành động đều đòi tên người, không có mặc định")


def _rui_ro_tra_tran():
    from .rui_ro_tong import PhanQuyet
    import dataclasses
    f = {x.name for x in dataclasses.fields(PhanQuyet)}
    return ("choToiDaUsd" in f), (
        "PhanQuyet mang choToiDaUsd" if "choToiDaUsd" in f
        else "PhanQuyet không có trần — đã thành nhị phân")


def _rui_ro_lay_max():
    s = _doc(GOC / "thi_bac_ty" / "rui_ro_tong.py")
    co_max = "cao = max(cao," in s
    khong_tb = "sum(" not in s.split("def diem")[1].split("def ")[0] if "def diem" in s else True
    return (co_max and khong_tb), (
        "điểm rủi ro lấy MAX" if co_max and khong_tb
        else "điểm rủi ro KHÔNG lấy max — rủi ro không bù trừ được")


def _cong_duyet_mot_ket_luan():
    from .cong_duyet import KET_LUAN_QUA
    ok = KET_LUAN_QUA == ("b-tot-hon",)
    return ok, (f"chỉ {KET_LUAN_QUA} được qua" if ok else
                f"cổng duyệt nhận {KET_LUAN_QUA} — có nhánh 'tốt hơn nhờ ôm "
                f"rủi ro đậm hơn' lọt vào")


def _cua_an_toan_khong_van_duoc():
    from .chan_doan_he import CUA_AN_TOAN_HE, NUT_TRUNG_UONG
    trung = set(NUT_TRUNG_UONG) & set(CUA_AN_TOAN_HE)
    return (not trung), ("; ".join(sorted(trung)) if trung else
                         f"{len(CUA_AN_TOAN_HE)} cửa an toàn, không cửa nào "
                         f"nằm trong bảng núm vặn được")


def _ty_khai_nguong_kinh_te():
    """Mọi ty phải khai `vonToiThieuKinhTeUsd` — chưa khai thì chết ở cửa.

    Thử HÀNH VI, không đọc mã nguồn. Bản đầu quét chuỗi trong `khuon_ty.py`
    và nó qua ngay cả khi câu `if` đã bị vô hiệu — một phép canh đọc văn bản
    canh đúng cái văn bản, không canh cái luật.
    """
    from .khuon_ty import Ty

    class _Quen(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "quên khai"

        def quet(self):
            return []

        def xet(self, co):
            return False, []

        def trinh(self, co):
            return None

    class _Am(_Quen):
        vonToiThieuKinhTeUsd = -1.0

    class _Du(_Quen):
        vonToiThieuKinhTeUsd = 100.0

    xau = []
    if not any("vonToiThieuKinhTeUsd" in l for l in _Quen.kiem_khai()):
        xau.append("ty QUÊN khai vẫn qua cửa đăng ký")
    if not _Am.kiem_khai():
        xau.append("ty khai số ÂM vẫn qua cửa đăng ký")
    if _Du.kiem_khai():
        xau.append("ty khai ĐÚNG mà bị chặn: " + "; ".join(_Du.kiem_khai()))
    # Và mọi ty đang chạy đều phải khai.
    import importlib
    chua = []
    for d in _goi_ty():
        for p in d.glob("ty_*.py"):
            try:
                m = importlib.import_module(d.name + "." + p.stem)
            except Exception:                             # noqa: BLE001
                continue
            for v in vars(m).values():
                if (isinstance(v, type) and issubclass(v, Ty) and v is not Ty
                        and getattr(v, "ma", "")):
                    if not getattr(v, "vonToiThieuKinhTeUsd", None):
                        chua.append(v.ma)
    if chua:
        xau.append("ty đang chạy chưa khai: " + ", ".join(chua))
    return (not xau), ("; ".join(xau) if xau else
                       "cửa đăng ký chặn ty quên khai và ty khai số âm; "
                       "mọi ty đang chạy đều đã khai")


def _khong_ep_live():
    from .che_van_hanh import QUAN_SAT, che_cua_ty

    class _T:
        ma, ho, vonToiThieuKinhTeUsd = "x.y.v1", "phai-sinh", 1000.0
    # NAV nhỏ → trần nhỏ → phải QUAN SÁT, dù có lớp ký lệnh
    c = che_cua_ty(_T(), 100.0, 0.15, lopKyLenhCoChua=True)
    return (c.che == QUAN_SAT), (
        "engine dưới ngưỡng vốn luôn QUAN SÁT" if c.che == QUAN_SAT
        else f"engine dưới ngưỡng vốn bị ép lên {c.che}")


def _khong_runtime_nao_len_site():
    """Runtime Python không được vào bản dựng site lẫn workflow."""
    kho = GOC.parent
    bd = _doc(kho / "scripts" / "build-dist.mjs")
    m = re.search(r"const HALLS = \[(.*?)\]", bd, re.S)
    trong_halls = [x for x in re.findall(r'"([^"]+)"', m.group(1) if m else "")
                   if x.endswith("-runtime")]
    wf = kho / ".github" / "workflows"
    trong_wf = []
    if wf.is_dir():
        for p in wf.glob("*.yml"):
            if "thi-bac-ty-runtime" in _doc(p):
                trong_wf.append(p.name)
    xau = trong_halls + trong_wf
    return (not xau), ("; ".join(xau) if xau else
                       "runtime không có trong HALLS lẫn workflow nào")


def _khoa_khong_ra_trinh_duyet():
    s = _doc(GOC / "bac" / "server.py")
    kh = s.split("def cau_hinh")[1].split("@app")[0] if "def cau_hinh" in s else ""
    xau = [x for x in ("os.environ[", "os.getenv(") if x in kh]
    return (not xau), ("; ".join(xau) if xau else
                       "/api/cau-hinh chỉ trả có/không, không trả giá trị khoá")



def _khai_gi_phai_noi_do():
    """Mọi ty khai `CUA` thì `tom_tat()` phải bày ĐÚNG bộ khoá ấy.

    Từng ty đã có phép kiểm riêng, nhưng chưa gì canh trên TOÀN HỆ — nên ty
    thứ năm quên hợp đồng ấy sẽ không ai biết cho tới khi nó bày ra một cửa
    giả. Đây đúng là chỗ hiến pháp làm được việc mà một phép kiểm lẻ không
    làm được.
    """
    import importlib
    xau, da_soi = [], []
    for d in _goi_ty():
        for p in d.glob("*.py"):
            s = _doc(p)
            if "CUA = (" not in s:
                continue
            try:
                m = importlib.import_module(d.name + "." + p.stem)
                cua = set(getattr(m, "CUA"))
                lop = getattr(m, "CongRuiRo")
            except Exception as e:                        # noqa: BLE001
                xau.append(d.name + "/" + p.name + ": không soi được (" + str(e) + ")")
                continue
            da_soi.append(d.name + "/" + p.stem)
            c = lop(dict({k: 1 for k in cua}, _khoa_la_de_thu=1))
            bay = set(c.tom_tat())
            if "_khoa_la_de_thu" in bay:
                xau.append(d.name + "/" + p.stem + ": tom_tat() bày khoá lạ như một cửa")
            elif bay != cua:
                xau.append(d.name + "/" + p.stem + ": tom_tat() lệch CUA")
    if not da_soi:
        return False, "không soi được ty nào có hợp đồng CUA"
    return (not xau), ("; ".join(xau) if xau else
                       str(len(da_soi)) + " cổng ty giữ đúng hợp đồng CUA: "
                       + ", ".join(da_soi))


def _von_cam_ket_phai_thay_duoc():
    """Vốn đã cam kết phải HIỆN ở danh mục, hoặc chỗ lệch phải được KHAI.

    Canh tĩnh, đọc mã: một phép canh động cần một `TrungUong` đang chạy, mà
    hiến pháp thì soát được cả lúc chưa có runtime nào.
    """
    tu = _doc(GOC / "thi_bac_ty" / "trung_uong.py")
    ds = _doc(GOC / "thi_bac_ty" / "doi_soat_vi_the.py")
    xau = []
    if "doi_soat_vi_the(" not in tu:
        xau.append("Trung Ương KHÔNG đối soát lúc khởi động")
    if "canh_vi_the(" not in tu:
        xau.append("Trung Ương KHÔNG đo lại lệch mỗi vòng")
    if "moPhong" not in ds:
        xau.append("đối soát không phân biệt mô phỏng với tiền thật")
    if "if not b.moCoi or b.canNguoi:" not in ds:
        xau.append("nhánh TIỀN THẬT không được chặn trước vòng đóng")
    n = ds.count('"DA_DONG"')
    if n != 1:
        xau.append(f"có {n} chỗ chuyển sang DA_DONG, phải đúng 1")
    return (not xau), ("; ".join(xau) if xau else
                       "đối soát chạy lúc khởi động VÀ mỗi vòng; mô phỏng "
                       "thì đóng ở sổ kèm bút toán, tiền thật thì ngắt cầu "
                       "dao và đòi người")


def _none_khac_khong():
    from .phan_bo import MAC_DINH as PB
    from .rui_ro_tong import PHAT_CHUA_DO
    xau = []
    if not (0.0 < PHAT_CHUA_DO < 1.0):
        xau.append("PHAT_CHUA_DO=" + str(PHAT_CHUA_DO))
    for k in ("phatChuaDoSucChua", "phatChuaDoKhoaVon"):
        v = PB.get(k)
        if v is None or not (0.0 < float(v) < 1.0):
            xau.append("phan_bo." + k + "=" + str(v))
    return (not xau), ("; ".join(xau) if xau else
                       "chưa đo thì bị PHẠT chứ không cho 0: rủi ro "
                       + str(PHAT_CHUA_DO) + " · sức chứa "
                       + str(PB["phatChuaDoSucChua"]) + " · khoá vốn "
                       + str(PB["phatChuaDoKhoaVon"]))


def _to_trinh_thu(ma, net, von=200.0, chua=9000.0, vmin=1.0):
    from .to_trinh import Chan, RuiRo, ToTrinh
    return ToTrinh(
        chienLuoc="perpetual.funding_spread.v1", ho="phai-sinh", taiSan=ma,
        chan=(Chan("LONG", "a", ma), Chan("SHORT", "b", ma)),
        vonCanUsd=von, sucChuaToiDaUsd=chua, grossBps=net + 2.0,
        phiUocBps=2.0, netUocBps=net, giuGio=8.0, khoaVonDenGiay=0.0,
        vonToiThieuKinhTeUsd=vmin,
        ruiRo=RuiRo(0.2, 0.2, 0.1, 0.2, 0.2, 0.0), tinCay=0.9,
        moHinhPhiDuChua=True, sucChuaConThieu=("x",))


def _tu_choi_phai_co_ly_do():
    """Chạy thật một lượt phân bổ có từ chối, và soi MỌI dòng từ chối."""
    from .danh_muc import DanhMuc
    from .phan_bo import PhanBo
    from .rui_ro_tong import RuiRoTong
    lo = [_to_trinh_thu("T" + str(i), 8.0) for i in range(8)]
    lo.append(_to_trinh_thu("XAU", -1.0))
    lat = PhanBo().chia(lo, RuiRoTong(), DanhMuc(1000.0), None, "hien-phap")
    if not lat.tuChoi:
        return False, "dựng được một lô mà KHÔNG có dòng từ chối nào để soi"
    thieu = [str(x.get("maToTrinh", "?")) for x in lat.tuChoi if not x.get("lyDo")]
    return (not thieu), ("; ".join(thieu) if thieu else
                         str(len(lat.tuChoi)) + " dòng từ chối, dòng nào cũng "
                         "có lý do")


def _cap_du_hoac_khong_cap():
    from .danh_muc import DanhMuc
    from .rui_ro_tong import RuiRoTong
    t = _to_trinh_thu("BTC", 8.0, von=1000.0, chua=90000.0, vmin=1000.0)
    pq = RuiRoTong().xet(t, DanhMuc(1000.0))       # trần một cơ hội = $150
    ok = (not pq.duyet) and pq.choToiDaUsd == 0.0
    return ok, ("trần $150 < ngưỡng $1.000 → TỪ CHỐI, không cấp nửa vời"
                if ok else
                "cấp " + str(pq.choToiDaUsd) + " cho engine cần 1000 — nửa vời")


def _cau_dao_bat_doi_xung():
    from .cau_dao import CauDao
    NG = {"lechDongHoToiDaGiay": 60.0, "soCangChetToiDa": 0,
          "tuoiToiDaGiay": 300.0, "sutVonToiDaPct": 10.0}
    cd = CauDao()
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=50.0, nguong=NG)
    if cd.cho_phep()[0]:
        return False, "sụt vốn 50% mà cầu dao KHÔNG ngắt"
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    if cd.cho_phep()[0]:
        return False, ("sụt vốn TỰ mở lại khi tín hiệu hết — nó là hậu quả, "
                       "không phải tín hiệu")
    if cd.het_ly_do("sut-von"):
        return False, "het_ly_do() gỡ được sụt vốn — lý do này phải cần người"
    if not cd.dong_lai("sut-von", "hien-phap"):
        return False, "người đóng lại KHÔNG được"
    return True, "sụt vốn không tự mở; chỉ người đóng lại được"


def _ngat_roi_van_quan_sat():
    """Cầu dao ngắt thì vẫn ghi nhận tờ trình, chỉ KHÔNG cấp vốn."""
    import tempfile
    from .khuon_ty import Ty
    from .trung_uong import TrungUong

    class _T(Ty):
        ma = "perpetual.funding_spread.v1"
        ho = "phai-sinh"
        moTa = "thử hiến pháp"
        vonToiThieuKinhTeUsd = 1.0

        def __init__(self):
            super().__init__()
            self.i = 0

        def quet(self):
            # Mỗi vòng một tài sản khác: cùng tài sản thì cửa chống trùng
            # bỏ qua, và phép canh sẽ qua vì một lý do khác.
            self.i += 1
            return ["T" + str(self.i)]

        def xet(self, co):
            return True, []

        def trinh(self, co):
            return _to_trinh_thu(co, 8.0, von=100.0)

    tu = TrungUong(tempfile.mkdtemp(prefix="hp-"), {"vonBanDauUsd": 1000.0})
    tu.dang_ky(_T())
    truoc = tu.danh_muc.tienMatUsd

    # HAI vòng, và vòng thứ hai mới là vòng đáng canh: lúc ấy cầu dao ĐÃ
    # ngắt từ trước, và cám dỗ "đang ngắt thì thôi quét cho đỡ tốn" mới có
    # chỗ xuất hiện. Một vòng thì cầu dao chưa ngắt lúc ghi nhận, nên phép
    # canh qua vì một lý do không liên quan.
    for vong in (1, 2):
        lat = tu.mot_vong(lechDongHoGiay=99999.0, cangChet=["x", "y"],
                          tuoiXauNhatGiay=99999.0)
        if not lat.cauDaoNgat:
            return False, "vòng " + str(vong) + ": dựng được tình huống mà cầu dao KHÔNG ngắt"
        if lat.soTyChay < 1:
            return False, "vòng " + str(vong) + ": ngắt rồi thì thôi QUÉT"
        if lat.soGhiNhan < 1:
            return False, ("vòng " + str(vong) + ": ngắt rồi thì thôi GHI "
                           "NHẬN — đã tự làm mình mù đúng lúc cần nhìn nhất")
        if abs(tu.danh_muc.tienMatUsd - truoc) > 1e-9:
            return False, "vòng " + str(vong) + ": ngắt rồi mà vẫn cam kết vốn"
    return True, "hai vòng liền, cầu dao ngắt: vẫn quét, vẫn ghi nhận, KHÔNG cam kết vốn"


def _bang_chay_lai_duoc():
    """Ghi một khung băng THẬT rồi dựng lại từ nó — không đọc mã.

    Vòng khép kín: `BaoGia` → `tom_tat()` (đúng thứ vào băng) →
    `dung_bao_gia()` (đúng thứ đọc ra) → phải có lại DẤU THỜI GIAN. Đọc mã
    chỉ chứng minh có một khoá tên `nguonTsMs`; chỉ đi hết vòng mới chứng
    minh nó về đúng chỗ cần.
    """
    from phai_sinh_chung.models import BaoGia

    bg = BaoGia(san="a", ma="BTC", rate=1e-4, intervalGio=8.0,
                markPx=100.0, mocKeMs=9_000,
                nguonTsMs=1_000, nhanTsMs=1_100)
    d = bg.tom_tat(2_000.0)
    thieu = [k for k in ("nguonTsMs", "nhanTsMs", "rate", "intervalGio",
                         "markPx", "mocKeMs") if d.get(k) is None]
    if thieu:
        return False, ("bản vào băng THIẾU nguyên liệu: " + ", ".join(thieu)
                       + " — chạy lại được hay không quyết ở đây")
    if d["nguonTsMs"] != 1_000:
        return False, f"dấu thời gian méo trên đường vào băng: {d['nguonTsMs']}"
    return True, ("bản vào băng mang đủ nguyên liệu, gồm cả dấu thời gian "
                  "gốc — nửa ĐỌC canh ở `kiem_chay_lai()`, vì canh nó ở đây "
                  "đòi Trung Ương import `bac/`, và điều "
                  "`trung-uong-khong-biet-ty` cấm đúng chuyện ấy (nó đã bắt "
                  "được bản đầu của chính phép canh này)")


def _ly_do_deu_mang_ma():
    """Chạy THẬT mọi cửa từ chối, rồi soát mã trên câu chúng ĐẺ RA.

    Không đọc mã nguồn: một phép canh đọc `MA_TU_CHOI` chỉ chứng minh cái
    bảng ấy tồn tại, không chứng minh cửa nào cũng đi qua nó. Cách duy nhất
    biết chắc là ép từng cửa nhả ra một câu rồi soát chính câu đó.
    """
    from .chan_doan_he import _ma_ly_do
    from .danh_muc import DanhMuc
    from .phan_bo import MA_TU_CHOI as MA_PB
    from .phan_bo import ly_do as ly_pb
    from .rui_ro_tong import MA_TU_CHOI as MA_RR
    from .rui_ro_tong import RuiRoTong

    thieu = []
    for ma in MA_PB:
        kw = {"n": 12, "cap": 1.0, "san": 2.0}
        cau = ly_pb(ma, **{k: v for k, v in kw.items()
                           if "{" + k in MA_PB[ma]})
        if _ma_ly_do(cau) != ma:
            thieu.append("phan_bo:" + ma)

    # Rủi Ro Tổng: ép TỪNG cửa nhả câu. Đòi thấy ĐỦ mọi mã trong bảng —
    # "vài cửa có mã" không chứng minh được gì về cửa thứ sáu, và cửa thứ
    # sáu mới là cửa người sau thêm vào mà quên mã.
    thay = set()
    def _sua(**kw):
        """Tờ trình thử với vài trường bị ép — `ToTrinh` đông cứng nên phải
        đi cửa `object.__setattr__`, và đó là chuyện chỉ phép canh được làm."""
        t = _to_trinh_thu("BTC", 8.0)
        for k, v in kw.items():
            object.__setattr__(t, k, v)
        return t

    hong = _sua(vonCanUsd=-1.0)                      # ép SAI KHUÔN
    canh = [
        # (cấu hình Rủi Ro Tổng, tờ trình)
        ({"ruiRoToiDa": -1.0, "tinCayToiThieu": 1.1,
          "netMoiGioToiThieuBps": 1e9, "batBuocDuMoHinhPhi": True,
          "batBuocDoDuocSucChua": True, "khoaVonToiDaGiay": -1.0,
          "batBuocDoDuocThanhKhoanThoat": True},
         _to_trinh_thu("BTC", 8.0)),
        ({}, hong),
        ({"batBuocKhaiVonToiThieu": True},
         _to_trinh_thu("BTC", 8.0, vmin=None)),
        # Xin 100 mà sức chứa 200 là HỢP KHUÔN; trần một cơ hội siết xuống
        # 50, dưới mức tối thiểu 90 → «dưới vốn tối thiểu». Dựng bằng cách
        # cho `sucChuaToiDaUsd` nhỏ hơn `vonCanUsd` thì `hop_le` bắt trước
        # và cửa cần ép không bao giờ tới lượt.
        ({"tranMotCoHoi": 0.05},
         _to_trinh_thu("BTC", 8.0, von=100.0, chua=200.0, vmin=90.0)),
        ({"batBuocDuMoHinhPhi": True},
         _sua(moHinhPhiDuChua=False, phiConThieu=("truot-gia",))),
        ({"batBuocDoDuocSucChua": True}, _sua(sucChuaToiDaUsd=None)),
        # `vonToiThieuKinhTeUsd = None` (không phải 0 — khai 0 là SAI KHUÔN)
        # để trần siết về 0 rơi vào nhánh «hết chỗ» chứ không bị nhánh
        # «dưới vốn tối thiểu» chặn trước.
        ({"tranMotCoHoi": 0.0, "batBuocKhaiVonToiThieu": False},
         _sua(vonToiThieuKinhTeUsd=None)),
    ]
    for c, t in canh:
        for x in RuiRoTong(c).xet(t, DanhMuc(1000.0)).lyDo:
            m = _ma_ly_do(x)
            if m is None:
                thieu.append("rui_ro_tong:KHÔNG-MÃ:" + x[:40])
            else:
                thay.add(m)
    sot = set(MA_RR) - thay
    if sot:
        thieu.append("rui_ro_tong:cửa-CHƯA-ÉP-NỔ:" + ",".join(sorted(sot)))
    la = thay - set(MA_RR)
    if la:
        thieu.append("rui_ro_tong:mã-ngoài-bảng:" + ",".join(sorted(la)))
    if thieu:
        return False, "; ".join(thieu)
    return True, (f"{len(MA_PB)} mã ở Phân Bổ và ĐỦ {len(thay)} cửa của Rủi "
                  f"Ro Tổng đều nhả câu MANG MÃ")


def _chua_du_mau_thi_noi_chua_du():
    from .chan_doan_he import TOI_THIEU_TO_TRINH, chan_doan_he
    from .chay_lai_he import TOI_THIEU_MAU, doi_chieu
    from .hieu_nang import TOI_THIEU_GIO, do_hieu_nang
    xau = []
    t = chan_doan_he({"soDangKy": {"pheu": {"phatHien": 1}}})
    if [x.ma for x in t] != ["thieu-to-trinh"]:
        xau.append("chan_doan_he không chặn ở ngưỡng mẫu")
    if doi_chieu([], {}, {}, 1000.0).get("duDeKetLuan") is not False:
        xau.append("chay_lai_he kết luận trên lô rỗng")
    d = do_hieu_nang([(0.0, 100.0), (3_600_000.0, 100.3)], 100.0)
    if d.get("cagrPhanTram") is not None:
        xau.append("hieu_nang quy một giờ ra CAGR năm")
    return (not xau), ("; ".join(xau) if xau else
                       "ba tầng đều có ngưỡng mẫu: "
                       + str(TOI_THIEU_TO_TRINH) + " tờ trình · "
                       + str(TOI_THIEU_MAU) + " mẫu · "
                       + str(int(TOI_THIEU_GIO)) + " giờ")


def _dung_yen_la_hop_le():
    from .chan_doan_he import chan_doan_he, de_xuat
    anh = {"soDangKy": {"pheu": {"phatHien": 300, "DUYET_TY": 200,
                                 "DUYET_RUI_RO": 150, "DA_CAP_VON": 100,
                                 "DA_MO": 95}},
           "danhMuc": {"tiLeDungVon": 0.55}}
    t = chan_doan_he(anh)
    if [x.ma for x in t] != ["khoe"]:
        return False, "hệ lành mà vẫn chẩn ra " + str([x.ma for x in t])
    dx = de_xuat(t, {"ruiRoTong": {"tranMotCang": 0.35}})
    return (not dx), ("hệ lành thì KHÔNG đề xuất vặn gì" if not dx
                      else "hệ lành mà vẫn đề xuất vặn " + dx[0].nut)



def _do_bang_duong_nav():
    """Sụt vốn phải tính từ ĐỈNH TRƯỚC ĐÓ, không từ vốn ban đầu.

    Dựng một đường 100 → 140 → 120: sụt thật là 14% (từ đỉnh 140), còn tính
    từ vốn gốc thì ra 0% và cả đợt rơi ấy biến mất khỏi báo cáo.
    """
    from .hieu_nang import do_hieu_nang
    GIO = 3_600_000.0
    nam = 365 * 24 * GIO
    d = do_hieu_nang([(0.0, 100.0), (nam * 0.5, 140.0), (nam, 120.0)], 100.0)
    tu_dinh = (140.0 - 120.0) / 140.0 * 100.0
    ok = abs(d["sutVonToiDaPhanTram"] - tu_dinh) < 1e-6
    return ok, ("sụt vốn tính từ đỉnh: " + format(tu_dinh, ".2f") + "%"
                if ok else
                "sụt vốn ra " + format(d["sutVonToiDaPhanTram"], ".2f")
                + "% thay vì " + format(tu_dinh, ".2f")
                + "% — đang tính từ vốn gốc, và cả đợt rơi biến mất")


# ══════════════════════════════════════════════════════════════════════
#  Các điều
# ══════════════════════════════════════════════════════════════════════

def _ha_tang_khong_phai_ty() -> tuple[bool, str]:
    """Gói hạ tầng dùng chung KHÔNG được nhận nhầm là ty.

    Nhận diện theo cấu trúc thì điều này tự đúng; phép canh ở đây để nếu
    ai đó quay về danh sách loại trừ thì nó đỏ ngay, chứ không đợi tới lúc
    `ty-khong-goi-ty` buộc tội oan một ty vô can.
    """
    ten = {d.name for d in _goi_ty()}
    ha_tang = {d.name for d in GOC.iterdir()
               if d.is_dir() and d.name.endswith("_chung")}
    lan = ten & ha_tang
    return (not lan,
            f"gói hạ tầng bị nhận nhầm là ty: {sorted(lan)}" if lan
            else f"{len(ten)} ty · {len(ha_tang)} gói hạ tầng · không lẫn")


DIEU: tuple[Dieu, ...] = (
    # ── I · phân quyền ───────────────────────────────────────────────────
    Dieu("trung-uong-khong-biet-ty",
         "Trung Ương KHÔNG biết ty nào tồn tại.",
         "Ngày trung ương phải import một ty để xử một trường hợp riêng là "
         "ngày hợp đồng đã hỏng: từ đó mọi ty mới đều cần một nhánh `if` "
         "trong lõi, và lõi thôi là lõi.",
         "bản đồ §26", _trung_uong_khong_biet_ty),

    Dieu("ty-khong-goi-ty",
         "Không ty nào gọi thẳng một ty khác.",
         "Bản đồ §6: mọi thứ đi qua Thông Chính Ty. Cho hai ty gọi nhau là "
         "dựng một đồ thị phụ thuộc mà không ai vẽ được, và một ty hỏng kéo "
         "theo ty khác.",
         "bản đồ §6", _ty_khong_goi_ty),

    Dieu("ty-khong-tu-quan-von",
         "Ty không giữ tiền, không có sổ cái, không có ví, không đặt lệnh.",
         "Mỗi việc trong số đó cần nhìn thấy TOÀN BỘ danh mục — thứ mà theo "
         "định nghĩa không ty nào nhìn thấy. Khâm Thiên Giám là ví dụ sống: "
         "nó có đủ cả bốn, và vì thế nằm ngoài tầm nhìn của Rủi Ro Tổng.",
         "bản đồ §26 · nợ kiến trúc trong README", _ty_khong_tu_quan_von),

    # ── II · trung thực ──────────────────────────────────────────────────
    Dieu("khai-gi-phai-noi-do",
         "Cửa nào KHAI ra thì `xet()` phải ĐỌC thật; khoá lạ bị lọc khỏi "
         "bảng tóm tắt.",
         "`bac/rui_ro.py` từng khai ba cửa mà `xet()` không đọc tới, và "
         "buồng lái bày chúng dưới nhãn 'đang có hiệu lực' suốt nhiều tuần. "
         "Không ai nói dối — luật ở một chỗ, mã ở chỗ khác.",
         "sự cố ba cửa giả", _khai_gi_phai_noi_do),

    Dieu("von-cam-ket-phai-thay-duoc",
         "Vốn đã cam kết phải HIỆN ở Danh Mục — hoặc chỗ lệch phải được "
         "KHAI ra và chặn việc cam kết thêm.",
         "Đo 28/08/2026: sổ đăng ký có 4 tờ đứng DA_MO với 500 USD đã cấp, "
         "danh mục báo 0 vị thế và 0 đã cam kết. Sổ nằm trên đĩa, danh mục "
         "dựng trong RAM — nên mỗi lần khởi động lại là một lần vốn đã tiêu "
         "bốc hơi khỏi mẫu số, và tiền rảnh rộng hơn sự thật. Không lỗi nào "
         "nổ; chỉ có một con số 0 trông rất khoẻ.",
         "doi_soat_vi_the.py", _von_cam_ket_phai_thay_duoc),

    Dieu("none-khac-khong",
         "`None` là CHƯA ĐO, không phải 0.",
         "Coi 'chưa đo được rủi ro cầu nối' thành 'không có rủi ro cầu nối' "
         "là thưởng cho sự mù, và cả hệ thống sẽ trôi về phía những ty đo "
         "được ít nhất.",
         "rui_ro_tong.PHAT_CHUA_DO", _none_khac_khong),

    Dieu("so-cai-chi-them",
         "Sổ Cái chỉ THÊM. Sửa sai chỉ có một đường: bút toán ĐẢO.",
         "Một lịch sử sửa được thì không còn là lịch sử. Và đảo phải chặn "
         "được đảo hai lần — đảo một khoản thu 12,5 ba lần cho ra LỖ 25, sổ "
         "vẫn cân, mọi dòng vẫn có lý do.",
         "so_cai.dao()", _so_cai_chi_them),

    Dieu("tu-choi-phai-co-ly-do",
         "Mọi lần từ chối đều kèm lý do, và lý do có MÃ để gộp được.",
         "Một hệ thống chỉ ghi lại lúc nó đồng ý thì lịch sử của nó toàn "
         "thắng lợi. Và lý do chứa số thì mỗi lần một chuỗi khác, nên bảng "
         "'vì sao từ chối' vỡ thành tám dòng nói cùng một điều.",
         "sự cố viSaoTuChoi vỡ tám dòng", _tu_choi_phai_co_ly_do),

    # ── III · quyền lực ──────────────────────────────────────────────────
    Dieu("rui-ro-tra-tran",
         "Rủi Ro Tổng trả về một TRẦN, không phải một chữ có/không.",
         "Trả nhị phân thì một cơ hội tốt xin $500 trong lúc chỉ còn chỗ cho "
         "$120 bị vứt cả. Trả trần thì nó được cấp $120, và `lyDoCat` nói rõ "
         "trần nào đã chặn.",
         "bản đồ §8", _rui_ro_tra_tran),

    Dieu("rui-ro-lay-max",
         "Điểm rủi ro lấy MAX, không lấy trung bình.",
         "Rủi ro không bù trừ. Một cơ hội an toàn năm mặt và chết ở mặt thứ "
         "sáu vẫn là một cơ hội chết — trung bình sẽ làm nó trông êm.",
         "to_trinh.RuiRo.cao_nhat()", _rui_ro_lay_max),

    Dieu("cap-du-hoac-khong-cap",
         "Cắt trần xuống dưới ngưỡng kinh tế của engine thì TỪ CHỐI, không "
         "cấp nửa vời.",
         "Cấp $150 cho engine cần $1.000: vốn bị giữ chỗ, một slot vị thế bị "
         "tiêu, lãi không bù nổi phí cố định. Ta trả tiền để học một điều đã "
         "biết trước.",
         "tệp vốn §minimum_economic_capital", _cap_du_hoac_khong_cap),

    Dieu("khong-ep-live",
         "Engine không đủ vốn tối thiểu chỉ được QUAN SÁT. Máy không tự ép "
         "một engine lên chế độ cao hơn.",
         "Chia $100 cho bốn engine là mỗi cái $25, và ở $25 thì phí, gas, cỡ "
         "lệnh tối thiểu ăn sạch — bốn engine cùng lỗ thay vì một engine có "
         "lãi.",
         "tệp vốn, câu chốt", _khong_ep_live),

    Dieu("ty-khai-nguong-kinh-te",
         "Mỗi ty PHẢI khai ngưỡng kinh tế của chính nó; chưa khai thì chết ở "
         "cửa đăng ký.",
         "Một ty không biết ngưỡng của mình sẽ đều đặn trình lên những cơ hội "
         "mà phí ăn sạch, để trung ương loại hộ — và chuyển việc ấy sang "
         "trung ương là bắt nó biết chi phí của từng ngành.",
         "tệp vốn", _ty_khai_nguong_kinh_te),

    # ── IV · máy không tự ký ─────────────────────────────────────────────
    Dieu("may-khong-tu-ky",
         "Máy đo, máy đề xuất, máy chặn — máy KHÔNG tự ký. Đóng cầu dao, áp "
         "tham số, quay lui: cả ba đòi TÊN NGƯỜI.",
         "Vòng 'kết quả → AI phân tích → AI sửa tham số → chạy tiền thật' "
         "hỏng không phải vì AI dở, mà vì nó không có chỗ nào để sai một "
         "cách NHÌN THẤY ĐƯỢC. Sau ba mươi lượt tham số đã trôi rất xa mà "
         "không lượt nào là lượt sai rõ ràng.",
         "bản đồ §17", _doi_ten_nguoi),

    Dieu("mot-ket-luan-duoc-qua",
         "Cổng Duyệt chỉ nhận `b-tot-hon`. 'Tốt hơn nhờ ôm rủi ro đậm hơn' "
         "KHÔNG được qua.",
         "Nới hết mọi trần thì luôn rót được nhiều vốn hơn và lợi suất bình "
         "quân gần như luôn đẹp hơn. Nhận nhánh ấy là dạy vòng tiến hoá rằng "
         "đường lên điểm là TỰ THÁO PHANH.",
         "cong_duyet, luật 7", _cong_duyet_mot_ket_luan),

    Dieu("cua-an-toan-khong-van-duoc",
         "Không núm nào chạm tới cửa AN TOÀN.",
         "Chúng không phải ngưỡng hiệu năng — chúng là câu 'ta không biết đủ "
         "để vào lệnh'. Cho vòng tiến hoá nới chúng là dạy nó rằng đường "
         "nhanh nhất tới điểm cao là TẮT ĐÈN BÁO, và nó sẽ tìm ra ngay.",
         "tien_hoa luật 1 · chan_doan_he.CUA_AN_TOAN_HE",
         _cua_an_toan_khong_van_duoc),

    Dieu("dung-yen-la-hop-le",
         "Không triệu chứng nào vượt ngưỡng thì ĐỨNG YÊN, và đó là kết quả "
         "hợp lệ — thường gặp nhất.",
         "Duyệt một thay đổi không đo được cải thiện là thêm nhiễu vào hệ "
         "thống rồi gọi nó là tiến hoá.",
         "chan_doan · cong_duyet luật 6", _dung_yen_la_hop_le),

    # ── V · an toàn ──────────────────────────────────────────────────────
    Dieu("mo-phong-la-cung",
         "Không cấu hình nào biến mô phỏng thành lệnh thật.",
         "Lớp ký lệnh CHƯA TỒN TẠI. Một cờ tắt được là một lời hứa suông, và "
         "lời hứa suông về tiền thật là loại lời hứa tệ nhất.",
         "thuc_thi.DieuPhoiThucThi", _mo_phong_cung),

    Dieu("cau-dao-bat-doi-xung",
         "Cầu dao NGẮT tự động, ĐÓNG LẠI phải có người.",
         "Máy phát hiện sự cố nhanh hơn người, nhưng máy không phân biệt "
         "được 'sự cố đã qua' với 'sự cố vẫn còn nhưng tín hiệu tạm im' — và "
         "cái thứ hai chính là lúc đóng lại thì mất tiền.",
         "cau_dao", _cau_dao_bat_doi_xung),

    Dieu("ngat-roi-van-quan-sat",
         "Cầu dao ngắt thì vẫn quét, vẫn ghi nhận, vẫn chẩn đoán — chỉ KHÔNG "
         "cam kết vốn.",
         "Dừng cả việc quan sát là tự làm mình mù đúng lúc cần nhìn nhất.",
         "trung_uong.mot_vong luật 2", _ngat_roi_van_quan_sat),

    Dieu("runtime-khong-len-site",
         "Không runtime nào vào `HALLS` của build-dist, và không runtime nào "
         "vào bất kỳ workflow nào.",
         "Thêm vào HALLS là đẩy mã nguồn và cấu hình lên Pages lẫn IPFS — mà "
         "IPFS đã pin là không rút lại được. Đưa vào Actions là đòi một "
         "secret tính tiền theo token quay lại repo.",
         "CLAUDE.md", _khong_runtime_nao_len_site),

    Dieu("khoa-khong-ra-trinh-duyet",
         "`/api/cau-hinh` chỉ trả CÓ/KHÔNG, không bao giờ trả giá trị khoá.",
         "Buồng lái chạy ở localhost, nhưng localhost vẫn là một trình "
         "duyệt, và một tiện ích mở rộng đọc được tab là đọc được khoá.",
         "CLAUDE.md · bac/server.cau_hinh", _khoa_khong_ra_trinh_duyet),

    # ── VI · đo lường ────────────────────────────────────────────────────
    Dieu("chua-du-mau-thi-noi-chua-du",
         "Dưới ngưỡng mẫu thì trả `None` và nói rõ, không ngoại suy.",
         "Quy 0,3% của nửa ngày ra một con số cả năm cho ra một tỉ suất vô "
         "nghĩa mà trông rất thuyết phục. Vặn tham số theo nó là học thuộc "
         "nhiễu — và nó sẽ *trông như* đang tiến bộ.",
         "chan_doan.TOI_THIEU_MAU · hieu_nang.TOI_THIEU_GIO", _chua_du_mau_thi_noi_chua_du),

    Dieu("do-bang-duong-nav",
         "Đo bằng CAGR và SỤT VỐN TỐI ĐA tính từ ĐỈNH, không bằng một APR "
         "nhân thẳng.",
         "Vốn thật đi qua 100 × 1,12 × 1,31 × 0,92 × 1,22. Một năm âm ở giữa "
         "không chỉ làm chậm — nó ăn vào cái nền mà mọi năm sau nhân lên từ "
         "đó.",
         "tệp vốn", _do_bang_duong_nav),

    Dieu("khong-do-bang-so-do",
         "Ở giai đoạn vốn nhỏ, KHÔNG đánh giá bộ máy bằng số đô kiếm được.",
         "$100 kiếm 20%/năm là $20, trong khi hạ tầng $10/tháng là $120 — "
         "vẫn âm. Cái đáng đo là chất lượng quyết định; `+$10` có thể là kết "
         "quả rất đáng giá nếu nó chứng minh một engine có kỳ vọng dương.",
         "tệp vốn", None),

    Dieu("von-ngoai-bat-san",
         "Khoá đọc vốn ngoài BẬT SẴN, không đợi ngày mở cửa đặt lệnh.",
         "Cơ chế `von_ngoai.py` dựng xong từ lâu mà `vonNgoai` để rỗng — "
         "một lớp an toàn không ai cấu hình. Cỗ máy kia tắt thì "
         "`docDuoc=False` hiện ra trong ảnh chụp; để rỗng thì không thấy gì "
         "cả, và hai chuyện ấy trông giống hệt nhau trên buồng lái.",
         # Lần thứ HAI điều `trung-uong-khong-biet-ty` bắt được chính bản
         # nháp của một phép canh ở đây: đọc `vonNgoai` đòi
         # `thi_bac_ty/` import `bac/config.py`. Trung Ương không được biết
         # ty nào tồn tại, huống hồ đọc cấu hình của một ty.
         #
         # Canh ở tầng đúng: `kiem_von_ngoai_bat_san()` trong selftest.
         "bac/config.py · von_ngoai.py", None),

    Dieu("khong-dem-hai-lan",
         "Cơ hội cỗ máy thứ hai ĐANG LÀM thì không được nộp tờ trình xin "
         "vốn — chúng đã là vốn ngoài trong Danh Mục.",
         "Khâm Thiên Giám có `dat_lenh.py` riêng. Nếu adapter nộp tờ trình "
         "cho một cơ hội nó đang tự làm, cùng một vị thế được tính hai lần: "
         "một lần là vốn ngoài, một lần là vốn vừa cấp. `tranMotCang` khi "
         "ấy tưởng mình chặn ở 30% trong khi thực tế là 60%.",
         # KHÔNG canh được TỪ ĐÂY, cùng lý do `bi-danh-khong-phai-ban-sao`:
         # canh nó đòi `thi_bac_ty/` import `kham_ngoai/`, tức đòi Trung
         # Ương biết một ty tồn tại. Canh ở tầng đúng —
         # `kiem_kham_adapter()` dựng ba cơ hội, hai cái `dangLam`, rồi đòi
         # chỉ một cái đi qua; cấy lỗi ngược làm nó đỏ.
         "kham_ngoai/ty_tien_doan.py", None),

    Dieu("ha-tang-khong-phai-ty",
         "Gói dùng chung của một HỌ không phải ty, và nhận diện ty phải "
         "theo CẤU TRÚC chứ không theo danh sách loại trừ.",
         "`phai_sinh_chung/` vừa ra đời đã bị phép canh coi là ty, rồi điều "
         "`ty-khong-goi-ty` báo `bac` gọi ty khác — trong khi `bac` chỉ đang "
         "dùng hạ tầng của chính họ mình. Danh sách loại trừ đòi người ta "
         "nhớ cập nhật, và lần quên đầu tiên xảy ra ngay ở gói đầu tiên.",
         "tách hạ tầng cho ty Cơ Sở", _ha_tang_khong_phai_ty),

    Dieu("bi-danh-khong-phai-ban-sao",
         "Tách thân hàm ra hạ tầng thì đường cũ phải TRỎ TỚI bản mới, không "
         "được chép sang.",
         "Hai bản sao lệch nhau đúng vào ngày ai đó sửa một bản, và không "
         "lỗi nào báo — chỉ có hai ty đếm mốc ra hai kết quả khác nhau trên "
         "cùng một khung thời gian.",
         # KHÔNG canh được TỪ ĐÂY, và lý do là một điều khác của chính
         # hiến pháp này: canh nó đòi `is` trên bốn bí danh, tức đòi
         # `thi_bac_ty/` import `bac/` và `on_dinh/` — đúng thứ
         # `trung-uong-khong-biet-ty` cấm. Điều ấy đã bắt được bản nháp
         # đầu của chính dòng này.
         #
         # Lách bằng `importlib` với tên dạng chuỗi thì phép canh chạy
         # được, nhưng đó là bẻ phanh cho vừa ý mình — cùng hạng với
         # "tốt hơn nhưng tập trung hơn" mà Cổng Duyệt từ chối.
         #
         # Nên nó được canh ở TẦNG ĐÚNG: `kiem_ha_tang_ho()` trong
         # `scripts/selftest.py`, nơi được phép nhìn cả hai bên.
         "tách hạ tầng cho ty Cơ Sở", None),

    Dieu("basis-khong-phai-thu-nhap",
         "Chỉ ghi vào NET khoản đã có người TRẢ. Chênh lệch giá của một hợp "
         "đồng KHÔNG đáo hạn không phải thu nhập.",
         "Perp không có ngày đáo hạn nên không gì bắt mark hội tụ về giao "
         "ngay. Cộng basis vào NET làm một cặp cash-and-carry lỗ 19 bps "
         "trông như lãi 11 bps — và nó sai theo hướng nguy hiểm nhất: hào "
         "phóng với chính mình.",
         # Cùng lý do với `bi-danh-khong-phai-ban-sao`: canh nó đòi
         # `thi_bac_ty/` import `co_so/`. Được canh ở tầng đúng —
         # `kiem_co_so()` nới rộng basis rồi đòi NET không đổi, và phép
         # cấy lỗi ngược (cộng basis vào NET) làm nó đỏ.
         "co_so/ty_co_so.py", None),

    Dieu("ly-do-tu-choi-phai-mang-ma",
         "Mọi lý do TỪ CHỐI phải mở đầu bằng một MÃ máy đọc được.",
         "Câu để NGƯỜI đọc, mã để MÁY đếm. Chẩn đoán muốn biết «cái gì đang "
         "chặn nhiều nhất» thì nó phải nhận ra từng lý do — mà nhận bằng "
         "cách dò chuỗi trong một câu có số nhúng bên trong (`đã đủ 12 vị "
         "thế`) là dựng một mối nối gãy ngay lần đầu ai đó sửa câu chữ. Gãy "
         "IM LẶNG, vì mối nối hỏng chỉ làm con số đếm nhỏ đi. Đã cắn thật: "
         "«CẦU DAO NGẮT» có dấu cách và chữ hoa nên 520 lần từ chối lớn "
         "nhất của cỗ máy rơi vào ô «không phân loại được».",
         "thi_bac_ty/phan_bo.py · rui_ro_tong.py", _ly_do_deu_mang_ma),

    Dieu("bang-phai-chay-lai-duoc",
         "Băng ghi NGUYÊN LIỆU. Ghi một con số đã dẫn thay cho nguyên liệu "
         "là ghi một cuốn băng không tua lại được.",
         "Băng tồn tại để chạy lại. `BaoGia.tom_tat()` bản đầu ghi "
         "`tuoiGiay` mà bỏ `nguonTsMs` — tuổi là số ĐÃ DẪN, đúng tại thời "
         "điểm ghi và vô nghĩa lúc đọc lại. Hậu quả không phải một sai số "
         "mà là toàn bộ năng lực hậu kiểm chết IM LẶNG: 460.035 cơ hội "
         "trên 188 giờ băng cho ra ĐÚNG 0 lần hậu kiểm, cổng chặn hết vì "
         "«sàn không đóng dấu thời gian», và vòng tiến hoá đứng ở 0 lượt "
         "suốt từ lúc dựng mà không ai biết.",
         # Chỉ canh được nửa GHI ở đây. Nửa ĐỌC (`dung_bao_gia` dẫn lại
         # dấu từ băng cũ) nằm ở `bac/`, và Trung Ương không được import
         # ty — điều `trung-uong-khong-biet-ty` đã bắt được bản đầu của
         # chính phép canh này. Nửa ấy canh ở `kiem_chay_lai()`, nơi phép
         # cấy lỗi ngược (ngừng truyền `luc`) làm nó đỏ.
         "phai_sinh_chung/models.py · bac/chay_lai.py", _bang_chay_lai_duoc),

    Dieu("tu-choi-gioi-hon-phat-hien-nhieu",
         "Đích đúng: quét 13 họ → phát hiện 100 → TỪ CHỐI 95 → rót vào 5.",
         "Mục tiêu KHÔNG phải '13 chiến lược đều kiếm tiền'. Một hệ thống từ "
         "chối giỏi quan trọng hơn một hệ thống phát hiện nhiều.",
         "bản đồ §21", None),
)


#: Đang ở giữa một lượt soát? Xem `soat()`.
_DANG_SOAT = False


def soat() -> dict:
    """Chạy mọi phép canh. Trả về vi phạm, và cả những điều KHÔNG canh được.

    ## Vì sao có chốt chống ĐỆ QUY ở đây

    Hiến pháp này không chỉ đọc mã — điều `ngat-roi-van-quan-sat` **dựng
    một Trung Ương thật rồi quay hai vòng**, vì cách duy nhất để biết «ngắt
    rồi vẫn quét» là ngắt thật rồi xem nó có quét không. Đọc mã bằng AST
    trả lời được «có gọi hàm ấy không», không trả lời được «hành vi ra sao».

    Nhưng ảnh chụp của Trung Ương lại GỌI hiến pháp (`anh_chup` →
    `_hien_phap` → `tom_tat` → `soat`). Nên khi vòng lặp bắt đầu tự chẩn
    đoán, đường đi khép kín lại:

        anh_chup → hiến pháp → mot_vong → hoc → anh_chup → hiến pháp → …

    và Python đệ quy tới chết. Nó ngủ yên suốt bao lâu `hoc()` còn phải
    đợi người bấm nút; vòng tự quay là thứ khép kín cái vòng tròn ấy.

    Chốt này cắt vòng tròn ở chỗ đúng: máy dựng bên trong một lượt soát
    **không được soát lại hiến pháp**. Nó trả về một tóm tắt KHAI RÕ mình
    là ảnh chụp lồng nhau, chứ không trả về 0 vi phạm — số 0 ở đây sẽ là
    một lời nói dối đọc y hệt một tin tốt.
    """
    global _DANG_SOAT
    if _DANG_SOAT:
        return {
            "soDieu": len(DIEU), "soCanhDuoc": None, "soKhongCanhDuoc": None,
            "soViPham": None, "viPham": [], "khongCanhDuoc": [], "dieu": [],
            "long": True,
            "loiNhac": ("ảnh chụp LỒNG trong một lượt soát hiến pháp — cỗ "
                        "máy này do chính hiến pháp dựng ra để thử, nên nó "
                        "KHÔNG soát lại. `soViPham` là None, không phải 0."),
        }
    _DANG_SOAT = True
    try:
        return _soat()
    finally:
        _DANG_SOAT = False


def _soat() -> dict:
    ds = [d.soat() for d in DIEU]
    vi_pham = [x for x in ds if x["canhDuoc"] and not x["dat"]]
    khong_canh = [x for x in ds if not x["canhDuoc"]]
    return {
        "soDieu": len(ds),
        "soCanhDuoc": len(ds) - len(khong_canh),
        "soKhongCanhDuoc": len(khong_canh),
        "soViPham": len(vi_pham),
        "viPham": vi_pham,
        "khongCanhDuoc": [x["ma"] for x in khong_canh],
        "dieu": ds,
        "loiNhac": (
            "Một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì tệ "
            "hơn không có. `soKhongCanhDuoc` in ra ở đây để không ai tưởng "
            "mình được che nhiều hơn thực tế — đó là bài học ba cửa giả, "
            "nâng lên tầm cả hệ thống."),
    }


def tom_tat() -> dict:
    r = soat()
    # `long` phải đi theo tóm tắt: bên gọi dùng nó để KHÔNG giữ lại một
    # ảnh chụp lồng. Lọc mất cờ ấy thì bản rỗng được giữ như bản thật.
    return {k: r[k] for k in ("soDieu", "soCanhDuoc", "soKhongCanhDuoc",
                              "soViPham", "khongCanhDuoc", "loiNhac")} | {
        "viPham": [{"ma": x["ma"], "chiTiet": x["chiTiet"]}
                   for x in r["viPham"]],
        "long": bool(r.get("long"))}
