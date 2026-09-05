"""Ty BIÊN ĐỘ — cấp thanh khoản V3 trên một dải, CHỈ khi đo được σ.

Ty thứ mười. Ba việc như mọi ty, và việc thứ tư (kế toán); cộng một việc
riêng: nó theo dõi VỊ THẾ NGƯỜI đang giữ ở OKX và khuyên — vì chương trình
thưởng đòi đặt ở OKX, và ty này không có ví.

## Vì sao không phải `lp_amm/` mở rộng

`lp_amm/` đứng trên một câu: «IL không đo được từ một ảnh chụp», và từ chối
cặp biến động. Câu ấy đúng. Ty này đứng trên câu tiếp theo: «IL đo được từ
một ảnh chụp cộng một σ» — và mọi thứ nó làm là lấy cho được σ (băng giá
gốc, băng giá chuỗi), rồi đưa σ vào `mo_hinh.py`. Không có σ thì nó nói
KHÔNG, y như `lp_amm/`. Hai ty, hai câu, không cãi nhau.

## Cỗ máy này KHÔNG đặt lệnh, và không có đường nào để đặt

Nó không cầm khoá, không ký, không nối OKX. Nó nói «vào dải này, cỡ này,
vì thế này» và người làm ở app. Đó là chủ ý của cả Thị Bạc Ty (bảy việc
một ty không được làm), và ở đây còn thêm một lý do: luật thưởng bắt thêm
thanh khoản qua trang OKX, mà đường ấy chỉ có người đi được.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from dataclasses import dataclass, field, replace

from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh, xin_theo_suc_chua

from . import bang_gia, config as cfgmod, lich
from .kinh_nghiem import SoKinhNghiem
from .mo_hinh import (GIO_NAM, NGAY_GIAO_DICH_NAM, KetQuaDai,
                      apr_phi_tu_khoi_luong, apr_tu_apy, can_dai, dai_doi_xung,
                      dai_theo_tick, hieu_suat_von, phan_chia_thanh_khoan,
                      rong_theo_sigma, thanh_khoan_tu_do_la)
from .nguon import UA_TRINH_DUYET, NguonGiaGoc, NguonRpcPool, NguonRss
from .quyet_dinh import CHO, GIU, VAO, BoiCanh, QuyetDinh, quyet
from .tin_tuc import SoTin
from .theo_doi import SoViThe
from .theo_doi_chuoi import DocViTheChuoi, thanh_vi_the

MA_CHIEN_LUOC = cfgmod.MA_CHIEN_LUOC
HO = cfgmod.HO
_VON_TOI_THIEU = 200.0

PHI_CON_THIEU = (
    "phan-phoi-thanh-khoan-pool-chua-doc",   # khi chưa có RPC
    "truot-gia-khi-vao-ra",
    "thue",
    "gia-token-thuong",
    "troi-gia-chuoi-ngoai-gio-chua-do",
)
SUC_CHUA_CON_THIEU = ("do-sau-that-quanh-gia", "phan-tram-pool-ta-chiem")

NHAN = {
    "khong-sigma": "chưa đo được σ", "gia-cu": "giá cũ",
    "sat-su-kien": "sát sự kiện", "gap-mo-cua": "giá chuỗi lệch giá gốc",
    "ngoai-gio-khong-doi-dai": "sàn Mỹ đóng", "tvl-mong": "TVL mỏng",
    "phi-duoi-lvr": "phí không đủ trả LVR", "sap-het-thuong": "thưởng sắp hết",
    "van-dai-cao": "xác suất văng cao", "khong-gia": "chưa có giá",
    "khong-apr": "chưa có APR", "chua-vao": "quyết định không phải VÀO",
}

NHIP_GIA_GOC_GIAY = 6 * 3600.0
NHIP_GIA_GOC_TRONG_PHIEN_GIAY = 300.0
NHIP_TIN_GIAY = 3600.0


@dataclass
class DanhGiaViThe:
    viThe: dict
    trangThai: dict
    dai: dict | None
    quyetDinh: dict

    def tom_tat(self) -> dict:
        return {"viThe": self.viThe, "trangThai": self.trangThai,
                "dai": self.dai, "quyetDinh": self.quyetDinh}


@dataclass
class CoHoiV3:
    pool: dict
    ma: str
    kyHieu: str
    gia: dict
    sigma: dict
    phien: dict
    tauNam: float
    dai: KetQuaDai | None
    quyetDinh: QuyetDinh
    aprPhi: float | None
    aprThuong: float | None
    nguonApr: str
    gioThuongConLai: float | None
    sucChuaUsd: float | None
    vonXinUsd: float
    bienDong: dict
    tin: list
    viThe: list = field(default_factory=list)
    thieu: tuple = ()
    duyet: bool = False
    lyDoMa: tuple = ()

    @property
    def netMoiGioBps(self) -> float:
        if self.dai is None or self.dai.netBps is None:
            return 0.0
        return self.dai.netBps / max(float(self.pool.get("giuGio") or 1.0), 1e-9)

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "kyHieu": self.kyHieu, "pool": self.pool,
                "gia": self.gia, "sigma": self.sigma, "phien": self.phien,
                "tauNam": self.tauNam,
                "dai": None if self.dai is None else self.dai.tom_tat(),
                "quyetDinh": self.quyetDinh.tom_tat(),
                "aprPhi": self.aprPhi, "aprThuong": self.aprThuong,
                "nguonApr": self.nguonApr,
                "gioThuongConLai": self.gioThuongConLai,
                "sucChuaUsd": self.sucChuaUsd, "vonXinUsd": self.vonXinUsd,
                "bienDong": self.bienDong, "tin": self.tin,
                "viThe": [v.tom_tat() for v in self.viThe],
                "thieu": list(self.thieu), "duyet": self.duyet,
                "lyDoMa": [list(x) for x in self.lyDoMa]}


def gio_thuong_con_lai(cfg: dict, now: dt.datetime) -> float | None:
    ct = cfg.get("chuongTrinh") or {}
    if not ct.get("ketThuc"):
        return None
    try:
        het = lich.doc_gio_vn(ct["ketThuc"])
    except ValueError:
        return None
    return max(0.0, (het - now.astimezone(lich.VN)).total_seconds() / 3600.0)


def apr_cua_pool(pool: dict, cfg: dict, gioThuong: float | None,
                 poolRpc: dict | None = None, vonUsd: float = 500.0,
                 hs: float | None = None) -> tuple:
    """`(aprPhi, aprThuong, nguon, heSoTapTrung)` — tỉ lệ/năm, và NGUỒN của
    con số, vì ba đường cho ba độ tin khác hẳn nhau:

        rpc+khoi-luong   phần phí của TA tính từ L thật của pool  ← đo được
        khoi-luong       phí/TVL của pool, nhân hiệu suất GIẢ ĐỊNH  ← nửa đo
        apy-hien-thi     APY OKX hiện × (1 − giả định phần thưởng)  ← giả định
    """
    tvl = pool.get("tvlUsd")
    phiBps = float(pool.get("phiBps") or 5.0)
    vol = pool.get("khoiLuongNgayUsd")
    apy = pool.get("apyHienThiPhanTram")
    # APY hiển thị là lãi KÉP (cờ `apyLaLaiKep`) → APR đơn tương đương để
    # mọi phép nhân theo thời gian phía dưới không lạc quan (Bài 4).
    if apy is not None and cfg.get("apyLaLaiKep", True):
        apy = apr_tu_apy(float(apy) / 100.0) * 100.0
    dangThuong = gioThuong is not None and gioThuong > 0
    gd = float(cfg.get("giaDinhPhanThuong") or 0.0)
    if poolRpc and poolRpc.get("thanhKhoan") and vol and hs and poolRpc.get("gia"):
        # L của ta ở cỡ vốn xin, trong dải hiệu suất `hs` → phần phí thật.
        # L_pool tính theo đơn vị thô của Uniswap; L của ta cũng phải quy
        # về đơn vị ấy: L_thô = L_người × 10^((d0+d1)/2). Hai thập phân
        # đọc từ chuỗi, không đoán.
        d0 = int(poolRpc["token0"]["thapPhan"])
        d1 = int(poolRpc["token1"]["thapPhan"])
        P = float(poolRpc["gia"])
        # Dải đối xứng có hiệu suất `hs`: (Pa/Pb)^¼ = 1 − 1/hs
        r4 = 1.0 - 1.0 / hs
        r = r4 ** 4                       # Pa/Pb
        Pa, Pb = P * r ** 0.5, P / r ** 0.5
        Lta = thanh_khoan_tu_do_la(vonUsd, P, Pa, Pb)
        if not poolRpc.get("coLaToken0"):
            # người tính giá USD mỗi cổ; pool tính token1 mỗi token0 — cùng
            # L nếu cổ là token0; nếu cổ là token1 thì quy đổi qua √giá.
            Lta = Lta * P
        LtaTho = Lta * 10 ** ((d0 + d1) / 2.0)
        phan = phan_chia_thanh_khoan(LtaTho, float(poolRpc["thanhKhoan"])) or 0.0
        aprPhi = phan * float(vol) * (phiBps / 10_000.0) * 365.0 / vonUsd
        aprThuong = None
        if apy is not None and dangThuong:
            aprThuong = max(0.0, float(apy) / 100.0 - (
                apr_phi_tu_khoi_luong(vol, tvl, phiBps) or 0.0))
        return aprPhi, aprThuong, "rpc+khoi-luong", hs
    # Không đọc được L của pool thì GIẢ ĐỊNH pool tập trung NHƯ TA: APR
    # của vị thế = APR pool, không nhân hiệu suất. Giả định ngược lại (pool
    # toàn dải) nhân APR lên 40–100 lần và đó là cách nhanh nhất để một
    # bảng xếp hạng nói dối. Sai theo hướng thận trọng, có khai.
    tt = hs if hs else 1.0
    if vol is not None and tvl:
        aprPhi = apr_phi_tu_khoi_luong(vol, tvl, phiBps)
        aprThuong = None
        if apy is not None and dangThuong:
            aprThuong = max(0.0, float(apy) / 100.0 - (aprPhi or 0.0))
        return aprPhi, aprThuong, "khoi-luong", tt
    if apy is not None:
        a = float(apy) / 100.0
        if dangThuong:
            return a * (1.0 - gd), a * gd, "apy-hien-thi-gia-dinh", tt
        return a * (1.0 - gd), 0.0, "apy-hien-thi-het-thuong", tt
    return None, None, "khong-co", tt


def tim_dai(P: float, sigma: float, tauNam: float, nut: dict, gioGiu: float,
            aprPhi, aprThuong, gioThuong, heSoTapTrung, gasUsd, vonUsd,
            poolRpc: dict | None = None, phiBps: float = 5.0) -> KetQuaDai:
    """Bắt đầu ở `heSoDai`, NỚI dần (×1,25, tối đa 6 nấc) tới khi P(văng)
    xuống dưới trần. Không tìm được thì trả dải rộng nhất — và P(văng)
    của nó vẫn cao, để luật `van-dai-cao` nói ra.

    Có thập phân từ RPC thì kéo hai mép về tick hợp lệ của mức phí — đó
    là dải thật trên chuỗi, và người dán vào OKX không phải tự làm tròn."""
    k = float(nut["heSoDai"])
    tran = float(nut["xacSuatVangToiDa"])
    tauDai = max(tauNam, 0.5 / NGAY_GIAO_DICH_NAM)
    kd = None
    for _ in range(7):
        rong = rong_theo_sigma(sigma, tauDai, k)
        Pa, Pb = dai_doi_xung(P, rong)
        if poolRpc and poolRpc.get("token0") and poolRpc.get("token1"):
            d0, d1 = int(poolRpc["token0"]["thapPhan"]), int(poolRpc["token1"]["thapPhan"])
            if not poolRpc.get("coLaToken0"):
                d0, d1 = d1, d0
            Pa, Pb = dai_theo_tick(Pa, Pb, phiBps, d0, d1)
        kd = can_dai(P, Pa, Pb, sigma, tauNam, gioGiu, aprPhi, aprThuong,
                     gioThuong, heSoTapTrung, gasUsd, vonUsd)
        if kd.xacSuatVang["tong"] <= tran:
            break
        k *= 1.25
    return kd


def can_pool(pool: dict, cfg: dict, bcPhien: lich.BoiCanhPhien,
             sigmaInfo: dict, giaInfo: dict, soViThe: SoViThe,
             poolRpc: dict | None = None, bienDong: dict | None = None,
             tin: list | None = None, now: dt.datetime | None = None,
             coNangTin: list | None = None,
             viTheThem: list | None = None) -> CoHoiV3:
    now = now or dt.datetime.now(dt.timezone.utc)
    nut, cua = cfg["nut"], cfg["cua"]
    ma = cfgmod.ma_goc(pool["kyHieu"])
    thieu = []
    sigma = sigmaInfo.get("sigma")
    soPhien = int(sigmaInfo.get("soPhien") or 0)
    coSigma = sigma is not None and soPhien >= int(cua["soPhienToiThieuChoSigma"])
    if not coSigma:
        thieu.append("sigma")
    gia = giaInfo.get("gia")
    if gia is None:
        thieu.append("gia")
    giuGio = float(nut["giuGio"])
    den = now + dt.timedelta(hours=giuGio)
    tau = lich.so_ngay_giao_dich(now, den) / NGAY_GIAO_DICH_NAM
    gioThuong = gio_thuong_con_lai(cfg, now)
    gas = (cfg.get("gasVaoRaUsd") or {}).get("gia")
    vonSan = float(cfg["von"]["moiCoHoiUsd"])
    tvl = pool.get("tvlUsd")
    sucChua = None if not tvl else float(tvl) * float(cua["phanTvlToiDa"])
    vonXin = xin_theo_suc_chua(vonSan, sucChua, float(cfg["von"]["phanSucChuaXin"]),
                               float(cfg["von"]["tranMotLanUsd"]))

    # Hiệu suất của dải đề xuất cần cho đường RPC; ước sơ bộ từ σ.
    hsSoBo = None
    if coSigma and gia:
        rong = rong_theo_sigma(sigma, max(tau, 0.5 / NGAY_GIAO_DICH_NAM),
                               float(nut["heSoDai"]))
        Pa0, Pb0 = dai_doi_xung(gia, rong)
        hsSoBo = hieu_suat_von(Pa0, Pb0)
    aprPhi, aprThuong, nguonApr, heSoTT = apr_cua_pool(
        pool, cfg, gioThuong, poolRpc, vonXin, hsSoBo)
    if aprPhi is None:
        thieu.append("apr")

    kd = None
    if coSigma and gia:
        kd = tim_dai(gia, sigma, tau, nut, giuGio, aprPhi, aprThuong,
                     gioThuong, heSoTT, gas, vonXin, poolRpc,
                     float(pool.get("phiBps") or 5.0))
    # sự kiện gần nhất liên quan mã này (7 ngày tới, đã sắp xếp)
    sk = [s for s in bcPhien.su_kien_trong(24.0 * 7.0)
          if s.loai in ("fomc", "ket-qua-kinh-doanh")
          and (not s.ma or s.ma.upper() in (ma.upper(), ma.upper().rstrip("X")))]
    gioSk = tenSk = None
    if sk:
        gioSk = (sk[0].luc - bcPhien.luc).total_seconds() / 3600.0
        tenSk = sk[0].ten
    if coNangTin:
        # cờ nặng trong tin 24 giờ qua được coi như sự kiện ĐANG diễn ra
        gioSk, tenSk = 0.0, "tin: " + coNangTin[0].get("tieuDe", "")[:60]
    lech = None
    if giaInfo.get("giaChuoi") and giaInfo.get("giaGoc"):
        lech = abs(giaInfo["giaChuoi"] / giaInfo["giaGoc"] - 1.0) * 100.0
    thuongLon = (aprThuong or 0.0) > (aprPhi or 0.0)

    bc = BoiCanh(kyHieu=pool["kyHieu"], dangGiu=False,
                 trangThaiPhien=bcPhien.trangThai, coSigma=coSigma,
                 soPhienSigma=soPhien, sigma=sigma,
                 giaTuoiGiay=giaInfo.get("tuoiGiay"),
                 tuoiGiaToiDaGiay=float(cua["tuoiGiaToiDaGiay"]),
                 xacSuatVang=None if kd is None else kd.xacSuatVang["tong"],
                 tiLePhiTrenLvr=None if kd is None else kd.tiLePhiTrenLvr,
                 netBps=None if kd is None else kd.netBps,
                 gioToiSuKien=gioSk, tenSuKien=tenSk or "",
                 gioToiHetThuong=gioThuong, thuongChiemPhanLon=thuongLon,
                 tvlUsd=tvl, lechGiaChuoiSoGocPct=lech, nut=nut, cua=cua)
    qd = quyet(bc)

    # vị thế người đang giữ trong pool này: ghi tay + đọc từ chuỗi
    dsVt = []
    for v in list(soViThe.dang_mo(pool["kyHieu"])) + list(viTheThem or ()):
        tt = v.danh_gia(gia) if gia else {"trongDai": None}
        kdV = None
        if coSigma and gia:
            conLai = max(1.0, giuGio - (tt.get("gioGiu") or 0.0))
            tauV = lich.so_ngay_giao_dich(now, now + dt.timedelta(hours=conLai)) / NGAY_GIAO_DICH_NAM
            try:
                kdV = can_dai(gia, v.Pa, v.Pb, sigma, tauV, conLai, aprPhi,
                              aprThuong, gioThuong, heSoTT, 0.0, v.vonUsd)
            except ValueError:
                kdV = None
        bcV = replace(bc, dangGiu=True, trongDai=tt.get("trongDai"),
                      xacSuatVang=None if kdV is None else kdV.xacSuatVang["tong"],
                      tiLePhiTrenLvr=None if kdV is None else kdV.tiLePhiTrenLvr,
                      netBps=None if kdV is None else kdV.netBps)
        dsVt.append(DanhGiaViThe(v.tom_tat(), tt,
                                 None if kdV is None else kdV.tom_tat(),
                                 quyet(bcV).tom_tat()))

    co = CoHoiV3(pool=dict(pool, giuGio=giuGio, apyLaLaiKep=bool(cfg.get("apyLaLaiKep", True))),
                 ma=ma, kyHieu=pool["kyHieu"],
                 gia=giaInfo, sigma=sigmaInfo, phien=bcPhien.tom_tat(),
                 tauNam=tau, dai=kd, quyetDinh=qd, aprPhi=aprPhi,
                 aprThuong=aprThuong, nguonApr=nguonApr,
                 gioThuongConLai=gioThuong, sucChuaUsd=sucChua,
                 vonXinUsd=vonXin, bienDong=bienDong or {}, tin=tin or [],
                 viThe=dsVt, thieu=tuple(thieu))
    ly = [(m, l) for m, _, l in qd.luatKhop if m != qd.luatQuyet or qd.biChan]
    if qd.hanhDong == VAO and kd is not None and kd.netBps is not None:
        return replace(co, duyet=True, lyDoMa=())
    if gia is None:
        ly.insert(0, ("khong-gia", "chưa có giá nào cho mã này"))
    if aprPhi is None:
        ly.insert(0, ("khong-apr", "chưa có APR — khai apyHienThi hoặc khoiLuong"))
    if not ly:
        ly = [("chua-vao", f"quyết định là {qd.hanhDong}: {qd.lyDo}")]
    return replace(co, duyet=False, lyDoMa=tuple(ly))


def _chay(coro):
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures as _cf
    with _cf.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


class TyBienDo(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("cấp thanh khoản V3 trên một dải — cặp BIẾN ĐỘNG, chỉ khi đo "
            "được σ; máy khuyên, người đặt ở OKX")
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, client_factory=None, cauHinh: dict | None = None,
                 thuMucBang=None, khongMang: bool = False,
                 vongNgay: bool = True) -> None:
        super().__init__()
        self.cfg = cauHinh or cfgmod.nap()
        self.thuMucBang = thuMucBang
        self.khongMang = khongMang
        self._cf = client_factory
        self.nguonGoc = NguonGiaGoc()
        self.nguonRpc = NguonRpcPool(self.cfg.get("rpc") or [])
        self.nguonTin = NguonRss()
        self.nguonVi = DocViTheChuoi(self.cfg.get("rpc") or [])
        #: vị thế đọc từ chuỗi, theo kyHieu — làm mới mỗi lượt quét
        self.viTheChuoi: dict = {}
        self.viTheChuoiLoi: str | None = None
        self.soViThe = SoViThe()
        self.soTin = SoTin(giuNgay=int((self.cfg.get("tin") or {}).get("giuNgay") or 14))
        self.soKinhNghiem = SoKinhNghiem()
        from .hoc_lieu import SoHocLieu
        self.soHocLieu = SoHocLieu()
        self.poolRpc: dict = {}
        self.coHoi: list = []
        self.lanMoi: dict = self._nap_lan_moi()
        self.quetCuoiLuc: str | None = None
        self.vongNgay = None
        if vongNgay:
            from .ngay import VongNgay      # nhập muộn: ngay.py không nhập file này
            self.vongNgay = VongNgay(self)

    # ── nguồn ────────────────────────────────────────────────────────────
    def _duong_lan_moi(self):
        return cfgmod.THU_MUC / "lam-moi.json"

    def _nap_lan_moi(self) -> dict:
        p = self._duong_lan_moi()
        try:
            return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        except ValueError:
            return {}

    def _ghi_lan_moi(self) -> None:
        p = self._duong_lan_moi()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.lanMoi), encoding="utf-8")

    def _den_han(self, khoa: str, nhip: float) -> bool:
        return (time.time() - float(self.lanMoi.get(khoa) or 0.0)) >= nhip

    async def _lam_moi(self) -> None:
        import httpx
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(self.cfg.get("hetGioHoiGiay") or 20.0),
            headers={"User-Agent": UA_TRINH_DUYET}))
        goc = self.cfg.get("coPhieuGoc") or {}
        now = dt.datetime.now(dt.timezone.utc)
        # Trong phiên Mỹ giá đổi theo phút → hỏi mỗi 5 phút để có giá tức
        # thời; ngoài phiên chỉ có giá đóng cửa → 6 giờ là thừa.
        nhipGoc = (NHIP_GIA_GOC_TRONG_PHIEN_GIAY
                   if lich.boi_canh(now).trangThai == lich.MO_CUA
                   else NHIP_GIA_GOC_GIAY)
        async with lam() as c:
            await self._doc_vi(c)
            for pool in self.cfg.get("pool") or []:
                ma = cfgmod.ma_goc(pool["kyHieu"])
                ky = goc.get(ma)
                if ky and self._den_han(f"goc:{ma}", nhipGoc):
                    ds = await self.nguonGoc.doc(c, ky)
                    if ds:
                        bang_gia.ghi_goc(ma, ds, self.thuMucBang)
                        tuc = self.nguonGoc.tucThoi.get(ky)
                        if tuc is not None:
                            bang_gia.ghi_goc_tuc_thoi(ma, tuc[0], tuc[1], self.thuMucBang)
                        self.lanMoi[f"goc:{ma}"] = time.time()
                if pool.get("diaChi"):
                    ds = await self.nguonRpc.doc(c, pool["diaChi"], ma)
                    if ds:
                        self.lanMoi[f"rpc:{ma}"] = time.time()
                        self.poolRpc[pool["kyHieu"]] = ds[0]
                        if ds[0].get("gia"):
                            bang_gia.ghi_chuoi(ma, now, ds[0]["gia"], "rpc",
                                               self.thuMucBang)
                if ky and self._den_han(f"tin:{ma}", NHIP_TIN_GIAY):
                    tk = ky.upper()
                    for mau in (self.cfg.get("tin") or {}).get("rss") or []:
                        ds = await self.nguonTin.doc(c, mau.format(ma=tk), ma)
                        if ds:
                            self.soTin.them(ds)
                    self.lanMoi[f"tin:{ma}"] = time.time()
        self._ghi_lan_moi()

    async def _doc_vi(self, c) -> None:
        """NFT vị thế trong ví người → `self.viTheChuoi`. Hợp đồng quản lý
        chưa biết thì suy từ `txMau` MỘT lần rồi ghi lại vào cau-hinh.json."""
        vi = self.cfg.get("vi") or {}
        dia = (vi.get("diaChi") or "").strip()
        if not dia:
            self.viTheChuoiLoi = None
            return
        ql = (vi.get("quanLyViThe") or "").strip()
        if not ql and vi.get("txMau"):
            ql = await self.nguonVi.quan_ly_tu_tx(c, vi["txMau"].strip()) or ""
            if ql:
                self.cfg["vi"]["quanLyViThe"] = ql
                try:
                    ch = cfgmod.nap()
                    ch.setdefault("vi", {})["quanLyViThe"] = ql
                    cfgmod.ghi(ch)
                except OSError:
                    pass
        macDinh = (self.cfg.get("uniswapXLayer") or {}).get("quanLyViThe") or ""
        if not ql and macDinh:
            # Không có tx mẫu thì dùng Uniswap V3 chính thức trên X Layer —
            # có nguồn, có ngày, và ghi rõ là mặc định để người đọc biết vì
            # sao 0 vị thế có thể là «sai hợp đồng» chứ không phải «ví trống».
            ql = macDinh
            self.cfg["vi"]["quanLyViTheDangDung"] = "mac-dinh-uniswap-chinh-thuc"
        elif ql:
            self.cfg["vi"]["quanLyViTheDangDung"] = "khai-hoac-suy-tu-tx"
        if not ql:
            self.viTheChuoiLoi = ("chưa biết hợp đồng quản lý vị thế — dán `txMau` (hash một "
                                  "giao dịch THÊM thanh khoản) hoặc `quanLyViThe`"
                                  + (f" · {self.nguonVi.loiCuoiChiTiet}" if self.nguonVi.loiCuoiChiTiet else ""))
            return
        ds = await self.nguonVi.doc(c, dia, ql)
        if not ds and not self.nguonVi.suc_khoe.songSot:
            self.viTheChuoiLoi = self.nguonVi.loiCuoiChiTiet or "RPC không trả lời"
            return
        self.viTheChuoiLoi = None
        gom: dict = {}
        for d in ds:
            gom.setdefault(d["kyHieu"], []).append(thanh_vi_the(d))
        self.viTheChuoi = gom
        self.lanMoi["vi:" + dia[:10]] = time.time()

    def dat_vi(self, than: dict) -> dict:
        """Người đặt/đổi địa chỉ ví (chỉ đọc). Ghi vào cau-hinh.json để sống
        qua khởi động lại; không nhận bất kỳ trường nào trông như khoá."""
        cam = [k for k in than if "khoa" in k.lower() or "private" in k.lower() or "secret" in k.lower()]
        if cam:
            raise ValueError(f"ty này không nhận khoá: {cam}")
        dia = str(than.get("diaChi") or "").strip()
        if dia and not (dia.startswith("0x") and len(dia) == 42):
            raise ValueError("địa chỉ ví phải là 0x + 40 ký tự hex")
        tx = str(than.get("txMau") or "").strip()
        if tx and not (tx.startswith("0x") and len(tx) == 66):
            raise ValueError("tx mẫu phải là 0x + 64 ký tự hex")
        ql = str(than.get("quanLyViThe") or "").strip()
        if ql and not (ql.startswith("0x") and len(ql) == 42):
            raise ValueError("hợp đồng quản lý vị thế phải là 0x + 40 ký tự hex")
        ch = cfgmod.nap()
        ch.setdefault("vi", {})
        ch["vi"]["diaChi"] = dia or None
        if tx:
            ch["vi"]["txMau"] = tx
            ch["vi"]["quanLyViThe"] = None      # tx mới → suy lại
        if ql:
            ch["vi"]["quanLyViThe"] = ql
        cfgmod.ghi(ch)
        self.cfg["vi"] = dict(ch["vi"])
        self.viTheChuoi = {}
        self.viTheChuoiLoi = None
        for k in [k for k in self.lanMoi if k.startswith("vi:")]:
            self.lanMoi.pop(k, None)
        return dict(self.cfg["vi"])

    def tri_thuc_tom_tat(self) -> dict:
        from .hoc_lieu import nap_tri_thuc, tom_tat_tri_thuc
        return tom_tat_tri_thuc(nap_tri_thuc(), self.soHocLieu)

    def them_hoc_lieu(self, than: dict) -> dict:
        return self.soHocLieu.them(str(than.get("ten") or "bài"), str(than.get("noiDung") or ""),
                                   str(than.get("nguon") or ""))

    def boc_hoc_lieu(self, ma: str) -> dict:
        from pathlib import Path
        from .hoc_lieu import boc_bang_cli, soat_bai
        b = self.soHocLieu.bai.get(ma)
        if not b:
            raise KeyError(ma)
        kq, loi = boc_bang_cli(Path(b["duong"]).read_text(encoding="utf-8"), b.get("ten") or ma)
        if kq is None:
            raise RuntimeError(loi)
        self.soHocLieu.ghi_boc(ma, kq, "claude-cli")
        return soat_bai(dict(kq, ma=ma))

    def dat_muc_tieu(self, than: dict) -> dict:
        """Hồ sơ mục tiêu của NGƯỜI — ghi vào cau-hinh.json. Số phải là số."""
        ra = dict(self.cfg.get("mucTieu") or {})
        for k in ("chiPhiThangUsd", "sutVonChiuDuocPct"):
            if k in than:
                v = than.get(k)
                if v is not None:
                    v = float(v)
                    if v < 0:
                        raise ValueError(f"{k} không âm được")
                ra[k] = v
        if "taiSanUuTien" in than:
            ra["taiSanUuTien"] = [str(x).strip().upper() for x in (than.get("taiSanUuTien") or []) if str(x).strip()]
        if "khongDonBay" in than:
            ra["khongDonBay"] = bool(than["khongDonBay"])
        ch = cfgmod.nap()
        ch["mucTieu"] = ra
        cfgmod.ghi(ch)
        self.cfg["mucTieu"] = ra
        return ra

    def vi_tom_tat(self) -> dict:
        vi = self.cfg.get("vi") or {}
        ds = [v for xs in self.viTheChuoi.values() for v in xs]
        theoDoi = {p["kyHieu"] for p in self.cfg.get("pool") or []}
        return {"diaChi": vi.get("diaChi"), "quanLyViThe": vi.get("quanLyViThe"),
                "quanLyViTheDangDung": vi.get("quanLyViTheDangDung"),
                "macDinh": (self.cfg.get("uniswapXLayer") or {}).get("quanLyViThe"),
                "txMau": vi.get("txMau"), "loi": self.viTheChuoiLoi,
                "soViThe": len(ds),
                "giaTriUsd": sum(v.vonUsd for v in ds),
                "phiChoThuUsd": (sum(v.phiChoThuUsd for v in ds if v.phiChoThuUsd is not None)
                                 if any(v.phiChoThuUsd is not None for v in ds) else None),
                "ngoaiDanhMuc": [v.tom_tat() for v in ds if v.kyHieu not in theoDoi],
                "soNftTrongVi": self.nguonVi.soNftTrongVi,
                "soNftDaSoi": self.nguonVi.soNftDaSoi,
                "soNftRong": self.nguonVi.soNftRong,
                "sucKhoe": self.nguonVi.suc_khoe.tom_tat()}

    # ── ba việc ──────────────────────────────────────────────────────────
    def quet(self) -> list:
        if not self.khongMang:
            try:
                _chay(self._lam_moi())
            except Exception as e:                            # noqa: BLE001
                self.loiCuoi = f"làm mới nguồn: {type(e).__name__}: {e}"
        self.coHoi = self.can_tat_ca()
        self.quetCuoiLuc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        self._ghi_kinh_nghiem()
        if self.vongNgay is not None:
            try:
                self.vongNgay.chay_neu_den_han()
            except Exception as e:                            # noqa: BLE001
                self.loiCuoi = f"vòng ngày: {type(e).__name__}: {e}"
        return list(self.coHoi)

    def can_tat_ca(self, now: dt.datetime | None = None) -> list:
        now = now or dt.datetime.now(dt.timezone.utc)
        het = None
        ct = self.cfg.get("chuongTrinh") or {}
        if ct.get("ketThuc"):
            try:
                het = lich.doc_gio_vn(ct["ketThuc"])
            except ValueError:
                het = None
        bc = lich.boi_canh(now, ketQuaKinhDoanh=self.cfg.get("ketQuaKinhDoanh") or {},
                           hetThuong=het)
        ra = []
        for pool in self.cfg.get("pool") or []:
            ma = cfgmod.ma_goc(pool["kyHieu"])
            si = bang_gia.sigma(ma, 60, int(self.cfg["cua"]["soPhienToiThieuChoSigma"]),
                                self.thuMucBang)
            gi = bang_gia.gia_moi_nhat(ma, self.thuMucBang, now)
            d = bang_gia.nap(ma, self.thuMucBang)
            gi["giaGoc"] = d["goc"][-1]["dong"] if d["goc"] else None
            gi["giaChuoi"] = d["chuoi"][-1]["gia"] if d["chuoi"] else None
            ky = (self.cfg.get("coPhieuGoc") or {}).get(ma)
            tk = ky.upper() if ky else ma.upper()
            ra.append(can_pool(pool, self.cfg, bc, si, gi, self.soViThe,
                               self.poolRpc.get(pool["kyHieu"]),
                               bang_gia.bien_dong_lien_quan(ma, self.thuMucBang),
                               self.soTin.moi_nhat(tk, 5), now,
                               self.soTin.co_nang_gan_day(tk, 24.0),
                               self.viTheChuoi.get(pool["kyHieu"], [])))
        ra.sort(key=lambda c: -(c.dai.netBps if (c.dai and c.dai.netBps is not None) else -1e18))
        return ra

    def _ghi_kinh_nghiem(self) -> None:
        for co in self.coHoi:
            if co.dai is None or co.gia.get("gia") is None:
                continue
            bc = {"trangThaiPhien": co.phien.get("trangThai"),
                  "tiLePhiTrenLvr": co.dai.tiLePhiTrenLvr,
                  "xacSuatVang": co.dai.xacSuatVang["tong"],
                  "sigma": co.sigma.get("sigma"), "nguonApr": co.nguonApr}
            try:
                self.soKinhNghiem.ghi_quyet_dinh(
                    co.kyHieu, co.quyetDinh.hanhDong, co.quyetDinh.luatQuyet,
                    bc, co.dai.tom_tat(), co.gia["gia"], float(co.pool["giuGio"]))
            except Exception as e:                            # noqa: BLE001
                self.loiCuoi = f"ghi kinh nghiệm: {type(e).__name__}: {e}"

    def xet(self, co: CoHoiV3):
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co: CoHoiV3) -> ToTrinh:
        return xuat_to_trinh(co)

    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Phí chảy liên tục theo APR phí của VỊ THẾ khi giá còn trong dải
        đề xuất của lượt quét mới nhất; ra ngoài dải thì đòi ĐÓNG. IL chưa
        vào kế toán — khai ra."""
        from thi_bac_ty.ke_toan import KetToanVong
        dtg = max(0.0, float(denGiay) - float(tuGiay))
        if dtg <= 0:
            return KetToanVong(vi="chưa qua giây nào")
        ky = toTrinh.get("taiSan")
        co = next((c for c in self.coHoi if c.kyHieu == ky), None)
        if co is None or co.dai is None or co.aprPhi is None or not co.gia.get("gia"):
            return KetToanVong(doDuoc=False,
                               vi=f"không thấy {ky} trong lượt quét gần nhất, "
                                  f"hoặc chưa có σ/APR — chưa đo được, khác 0")
        von = sum(abs(float(getattr(c, "vonUsd", 0.0) or 0.0)) for c in viThe)
        P = co.gia["gia"]
        if not (co.dai.Pa < P < co.dai.Pb):
            return KetToanVong(thuUsd=0.0, dongLai=True,
                               lyDoDong=f"giá {P:.2f} ra ngoài dải "
                                        f"[{co.dai.Pa:.2f}, {co.dai.Pb:.2f}]",
                               vi="vị thế đông cứng — 0 phí, IL đã hiện thực")
        apr = co.aprPhi * (co.dai.hieuSuat if co.nguonApr != "rpc+khoi-luong" else 1.0)
        thu = von * apr * dtg / (GIO_NAM * 3600.0)
        return KetToanVong(thuUsd=thu,
                           vi=f"phí V3 {ky}: APR {apr:.1%} ({co.nguonApr}) × "
                              f"{dtg / 3600:.3f}h trên {von:.2f} USD — IL CHƯA "
                              f"trừ, thưởng KHÔNG tính")

    # ── việc RIÊNG của ty này: báo cáo, lát cắt, sổ người ─────────────
    #
    # Buồng lái và `bac/snapshot.py` gọi QUA ty (`runtime.tyPhu`), không
    # import gói này — hiến pháp `ty-khong-goi-ty` áp cả chiều ngược lại.

    def bao_cao(self, now: dt.datetime | None = None) -> dict:
        from .hom_nay import dung
        return dung(self, now, coHoi=self.coHoi or None)

    def bao_cao_van_ban(self, now: dt.datetime | None = None) -> str:
        from .hom_nay import van_ban
        from .lam_sach import lam_sach
        return van_ban(lam_sach(self.bao_cao(now)))

    def ghi_lat_cat(self, cung):
        from .lat_cat import ghi_cua_ty
        return ghi_cua_ty(self, cung)

    def hoc(self) -> dict:
        if self.vongNgay is None:
            raise RuntimeError("ty chưa gắn vòng ngày")
        return self.vongNgay.hoc()

    def mo_vi_the(self, than: dict):
        return self.soViThe.mo(str(than["kyHieu"]), float(than["Pa"]), float(than["Pb"]),
                               float(than["vonUsd"]), float(than["giaMo"]),
                               str(than.get("ghiChu") or ""),
                               str(than.get("maQuyetDinh") or ""))

    def dong_vi_the(self, ma: str, than: dict):
        return self.soViThe.dong(
            ma, float(than["giaDong"]),
            None if than.get("phiThuUsd") is None else float(than["phiThuUsd"]),
            None if than.get("thuongThuUsd") is None else float(than["thuongThuUsd"]),
            str(than.get("lyDoDong") or ""))

    def tom_tat(self) -> dict:
        return {**super().tom_tat(),
                "nguon": {"goc": self.nguonGoc.suc_khoe.tom_tat(),
                          "rpc": self.nguonRpc.suc_khoe.tom_tat(),
                          "tin": self.nguonTin.suc_khoe.tom_tat()},
                "soPool": len(self.cfg.get("pool") or []),
                "soCoHoi": len(self.coHoi),
                "soVao": sum(1 for c in self.coHoi if c.quyetDinh.hanhDong == VAO),
                "viThe": self.soViThe.tom_tat(),
                "vi": self.vi_tom_tat(),
                "kinhNghiem": self.soKinhNghiem.tom_tat(),
                "tin": self.soTin.tom_tat(),
                "quetCuoiLuc": self.quetCuoiLuc}


def _rui_ro(co: CoHoiV3) -> RuiRo:
    xv = co.dai.xacSuatVang["tong"] if co.dai else None
    return RuiRo(thiTruong=None if xv is None else min(1.0, 0.4 + 0.5 * xv),
                 thanhKhoan=(0.6 if (co.pool.get("tvlUsd") or 0) < 50_000 else 0.35),
                 giaoThuc=0.45, cang=0.20, thucThi=0.40, cauNoi=0.0)


def _tin_cay(co: CoHoiV3) -> float:
    # Thang này cũng là ĐỘ TIN CẬY DỮ LIỆU ở tầng chỉ huy: dưới 0,60 thì
    # nút VÀO bị khoá (`hom_nay.TIN_CAY_KHOA`). Ba mức giá: giá pool đọc
    # từ RPC là chuẩn; giá sàn gốc ĐANG giao dịch gần chuẩn; giá đóng cửa
    # hôm qua là số của quá khứ.
    d = 1.0
    if co.nguonApr.startswith("apy-hien-thi"):
        d -= 0.30      # phí gốc tách bằng giả định, chưa đo
    elif co.nguonApr == "khoi-luong":
        d -= 0.15      # có khối lượng nhưng chưa có L của pool
    if (co.sigma.get("soPhien") or 0) < 30:
        d -= 0.15
    if co.sigma.get("nguon") == "chuoi":
        d -= 0.10
    if co.gia.get("nguon") == "goc":
        d -= 0.10      # giá đóng cửa, không phải giá đang có
    elif co.gia.get("nguon") == "goc-tuc-thoi":
        d -= 0.05      # giá sàn gốc đang giao dịch, chưa phải giá pool
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co: CoHoiV3) -> ToTrinh:
    kd = co.dai
    p = co.pool
    thieu = list(PHI_CON_THIEU)
    if co.nguonApr == "rpc+khoi-luong":
        thieu.remove("phan-phoi-thanh-khoan-pool-chua-doc")
    if co.nguonApr.startswith("apy-hien-thi"):
        thieu.append("phi-goc-tach-tu-apy-bang-GIA-DINH")
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=co.kyHieu,
        chan=(Chan("CAP_THANH_KHOAN", "okx-defi/uniswap-v3", co.kyHieu,
                   co.vonXinUsd, "lp", "X Layer"),),
        vonCanUsd=co.vonXinUsd, vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaUsd,
        grossBps=((kd.phiBps or 0.0) + (kd.thuongBps or 0.0)) if kd else 0.0,
        phiUocBps=((kd.gasBps or 0.0) - (kd.ilKyVongBps or 0.0)) if kd else 0.0,
        netUocBps=(kd.netBps or 0.0) if kd else 0.0,
        giuGio=float(p.get("giuGio") or 72.0),
        khoaVonDenGio=0.0, thanhKhoanThoatUsd=co.sucChuaUsd,
        ruiRo=_rui_ro(co), tuoiDuLieuGiay=co.gia.get("tuoiGiay"),
        tinCay=_tin_cay(co), moHinhPhiDuChua=False, phiConThieu=tuple(thieu),
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang="USD", cang=("okx-defi/uniswap-v3",), chuoi=("X Layer",),
        bangChung=(
            f"{co.kyHieu} · gia {co.gia.get('gia')} ({co.gia.get('nguon')}) · "
            f"sigma {co.sigma.get('sigma')} tu {co.sigma.get('soPhien')} phien ({co.sigma.get('nguon')})",
            (f"dai [{kd.Pa:.4g}, {kd.Pb:.4g}] rong ±{kd.rong:.1%} · hieu suat {kd.hieuSuat:.1f}x · "
             f"P(vang) {kd.xacSuatVang['tong']:.0%} (CAN TREN) · IL ky vong {kd.ilKyVongBps:.0f} bps"
             if kd else "chua dung duoc dai"),
            f"APR phi {co.aprPhi} · thuong {co.aprThuong} · nguon {co.nguonApr} · "
            f"thuong con {co.gioThuongConLai} gio",
            f"quyet dinh {co.quyetDinh.hanhDong} theo luat {co.quyetDinh.luatQuyet}: {co.quyetDinh.lyDo}",
            f"phien {co.phien.get('trangThai')} · tau {co.tauNam * NGAY_GIAO_DICH_NAM:.2f} ngay giao dich",
        ))
