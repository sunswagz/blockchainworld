"""Buồng lái — FastAPI, CHỈ sống ở localhost.

Buồng lái có nút điều khiển và đọc được cấu hình, nên nó **không bao giờ lên
site**. Cùng lý do `tu-cam-thanh-runtime` giữ buồng lái ở `:5182` và
`kham-thien-giam-runtime` ở `:5186`.

    cung tĩnh (5187)     quan sát. lên GitHub Pages. không nút nào.
    buồng lái (5188)     điều khiển. chỉ ở máy. không lên đâu cả.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .bus import bus
from .config import CONFIG, WEB_DIR, che_hieu_luc, ly_do_khong_that, san_co_khoa
from .sach import sach
from .snapshot import ghi_lat_cat
from .vong import runtime

app = FastAPI(title="Thị Bạc Ty", docs_url=None, redoc_url=None)


@app.on_event("startup")
def _bat() -> None:
    runtime.bat()


@app.on_event("shutdown")
def _dung() -> None:
    runtime.dung()


@app.get("/api/trang-thai")
def trang_thai() -> JSONResponse:
    return JSONResponse(sach(runtime.anh_chup()))


@app.get("/api/cau-hinh")
def cau_hinh() -> JSONResponse:
    """Cấu hình đang có hiệu lực. KHÔNG trả về bất cứ khoá nào.

    Chỉ trả về `có khoá hay không`, không bao giờ trả giá trị. Buồng lái chạy
    ở localhost nhưng localhost vẫn là một trình duyệt, và một tiện ích mở
    rộng đọc được tab là đọc được khoá.
    """
    return JSONResponse(sach({
        "che": CONFIG.get("che"),
        "cheHieuLuc": che_hieu_luc(),
        "cuaDangDong": ly_do_khong_that(),
        "sanCoKhoa": san_co_khoa(),
        "port": CONFIG["port"],
        "nhipGiay": CONFIG["nhipGiay"],
        "quet": CONFIG["quet"],
        "san": CONFIG["san"],
        "ruiRo": CONFIG["ruiRo"],
    }))


@app.get("/api/nhat-ky")
def nhat_ky(n: int = 120) -> JSONResponse:
    return JSONResponse(sach({"tong": bus.tong(), "dong": bus.gan_day(n)}))


@app.get("/api/gan-day")
def gan_day(n: int = 50) -> JSONResponse:
    """Cơ hội đã ghi sổ gần đây — đọc từ SQLite, không từ bộ nhớ."""
    return JSONResponse(sach({"coHoi": runtime.so.gan_day(n)}))


@app.get("/api/do-dai")
def do_dai(ma: str, sanLong: str, sanShort: str, gio: float = 24.0) -> JSONResponse:
    """Chênh lệch của một cặp DAI tới đâu — thứ phân biệt cú loé với mỏ thật."""
    return JSONResponse(sach(runtime.so.do_dai(ma, sanLong, sanShort, gio)))


@app.post("/api/tam-dung")
def tam_dung() -> JSONResponse:
    runtime.tamDung = not runtime.tamDung
    bus.ghi("tạm dừng" if runtime.tamDung else "chạy tiếp", loai="he")
    return JSONResponse({"tamDung": runtime.tamDung})


@app.post("/api/quet-ngay")
async def quet_ngay() -> JSONResponse:
    """Quét một lượt ngay, không chờ hết nhịp."""
    try:
        await runtime.mot_vong()
    except Exception as e:                          # noqa: BLE001
        return JSONResponse({"xong": False, "loi": f"{type(e).__name__}: {e}"},
                            status_code=200)
    return JSONResponse({"xong": True, "vong": runtime.vong,
                         "soCoHoi": len(runtime.coHoi)})


# ── băng ghi · chạy lại · tiến hoá ────────────────────────────────────────
@app.get("/api/bang")
def api_bang(tuNgay: str | None = None) -> JSONResponse:
    """Băng có bao nhiêu khung, và có LÀNH không.

    `dem_bang` đếm mà không giữ khung nào lại: cả băng một ngày là hàng trăm
    MB đối tượng Python, và dựng chúng lên chỉ để đọc ra một số nguyên là
    cách chắc chắn nhất làm treo buồng lái.
    """
    from .bang import dem_bang, may_ghi as mg
    bao = dem_bang(tuNgay)
    return JSONResponse(sach({"soKhung": bao.soKhung, "dangGhi": mg.bat,
                              "khungDaGhi": mg.soKhung, "bao": bao.tom_tat()}))


@app.post("/api/chay-lai")
def api_chay_lai(tuNgay: str | None = None, giuGio: float | None = None
                 ) -> JSONResponse:
    """Chạy lại băng với tham số hiện tại (hoặc cửa sổ giữ truyền vào)."""
    from .bang import doc_bang
    from .chay_lai import mot_luot
    from .tien_hoa import tham_so_hien_tai
    ts = tham_so_hien_tai()
    if giuGio is not None:
        ts.giuGio = float(giuGio)
        ts.ten = f"giữ {giuGio:g}h"
    return JSONResponse(sach(mot_luot(doc_bang(tuNgay), ts,
                                      CONFIG["san"]).tom_tat()))


@app.post("/api/doi-chieu")
def api_doi_chieu(nut: str, gtA: float, gtB: float,
                  tuNgay: str | None = None) -> JSONResponse:
    """So HAI giá trị của MỘT núm trên CÙNG băng. Đây mới là backtest."""
    from .bang import doc_bang
    from .chay_lai import doi_chieu
    from .tien_hoa import NUT_VAN, dat_nut, tham_so_hien_tai
    if nut not in NUT_VAN:
        return JSONResponse({"loi": f"núm {nut!r} không vặn được — cửa an "
                                    f"toàn không nằm trong NUT_VAN",
                             "numVanDuoc": sorted(NUT_VAN)}, status_code=200)
    goc = tham_so_hien_tai()
    a = dat_nut(goc, nut, gtA, f"A: {nut}={gtA:g}")
    b = dat_nut(goc, nut, gtB, f"B: {nut}={gtB:g}")
    return JSONResponse(sach(doi_chieu(doc_bang(tuNgay), a, b, CONFIG["san"])))


@app.post("/api/tien-hoa")
def api_tien_hoa(thu: bool = True) -> JSONResponse:
    """Chạy một lượt vòng tiến hoá bằng tay.

    Mặc định `thu=true` — xem sẽ làm gì mà không ghi gì. Muốn ghi thật thì
    phải truyền `?thu=false`, và đó là chủ ý: một nút bấm nhầm không được
    phép vặn tham số của cỗ máy.
    """
    from .tien_hoa import mot_luot
    return JSONResponse(sach(mot_luot(thu=thu).tom_tat()))


@app.get("/api/duong-tien-hoa")
def api_duong_tien_hoa() -> JSONResponse:
    """Sổ tiến hoá gộp — có mạnh hơn thật không, bằng số."""
    from .tien_hoa import duong_tien_hoa
    return JSONResponse(sach(duong_tien_hoa()))


# ══════════════════════════════════════════════════════════════════════════
#  THỊ BẠC TY — bộ máy đứng trên ty này
# ══════════════════════════════════════════════════════════════════════════

def _tu():
    """Trung Ương, hoặc None nếu đang tắt. Mọi đường dưới đây gọi qua đây."""
    return getattr(runtime, "trungUong", None)


def _tat() -> JSONResponse:
    return JSONResponse({"tat": True,
                         "loiNhac": "Trung Ương đang TẮT "
                                    "(CONFIG['trungUong']['bat'])."},
                        status_code=409)


@app.get("/api/trung-uong")
def api_trung_uong() -> JSONResponse:
    """Cả chín tầng trong một lần gọi."""
    tu = _tu()
    return _tat() if tu is None else JSONResponse(sach(tu.anh_chup()))


@app.get("/api/pheu")
def api_pheu(chienLuoc: str | None = None) -> JSONResponse:
    """Phễu từ cơ hội thô tới vị thế — thước duy nhất nói cỗ máy có học không."""
    tu = _tu()
    if tu is None:
        return _tat()
    return JSONResponse(sach({
        "dayDu": tu.pheu_day_du(),
        "soDangKy": tu.so_dang_ky.pheu(chienLuoc),
        "chienLuoc": chienLuoc,
    }))


@app.get("/api/so-cai")
def api_so_cai(n: int = 100, loai: str | None = None) -> JSONResponse:
    """Sổ cái gần đây. Chỉ đọc — sửa sổ cái chỉ có một đường là `dao()`."""
    tu = _tu()
    if tu is None:
        return _tat()
    return JSONResponse(sach({"dong": tu.so_cai.gan_day(min(int(n), 500), loai),
                              "tomTat": tu.so_cai.tom_tat()}))


@app.get("/api/to-trinh/{ma}")
def api_to_trinh(ma: str) -> JSONResponse:
    """Cả đời một tờ trình: nó đã đi qua những cửa nào, và tiền đã đi đâu."""
    tu = _tu()
    if tu is None:
        return _tat()
    p = tu.so_dang_ky.phieu(ma)
    if p is None:
        return JSONResponse({"coKhong": False, "ma": ma}, status_code=404)
    return JSONResponse(sach({**p, "butToan": tu.so_cai.theo_to_trinh(ma)}))


@app.post("/api/hoc")
def api_hoc(ghiSo: bool = False) -> JSONResponse:
    """Chẩn cả bộ máy và ĐỀ XUẤT vặn tham số phân bổ.

    Mặc định `ghiSo=false` — xem mà không để lại dấu. Và dù `ghiSo=true` thì
    nó vẫn chỉ GHI ĐỀ XUẤT: đổi tham số phân bổ là đổi cách chia tiền giữa
    các ty, mà chuyện đó không chạy lại được nên không tự nhận được.
    """
    tu = _tu()
    return _tat() if tu is None else JSONResponse(sach(tu.hoc(ghiSo=ghiSo)))


@app.post("/api/chay-lai-he")
def api_chay_lai_he(nut: str, gtA: float, gtB: float) -> JSONResponse:
    """Chạy lại quyết định PHÂN BỔ trên tờ trình đã ghi, với hai giá trị núm.

    Không đo lãi lỗ và không giả vờ đo được: cơ hội không được cấp vốn thì
    không được mở, nên nó không có kết cục. Cái đo được là HÌNH DẠNG phân bổ
    — rót bao nhiêu, vào cơ hội tốt đến đâu, dồn vào một cảng bao nhiêu.
    """
    tu = _tu()
    if tu is None:
        return _tat()
    from thi_bac_ty.chay_lai_he import doi_chieu, thu_hoach
    from thi_bac_ty.trung_uong import _dat_nut
    goc = tu.tham_so()
    tt, hong = thu_hoach(tu.so_dang_ky)
    return JSONResponse(sach(doi_chieu(
        tt, _dat_nut(goc, nut, gtA), _dat_nut(goc, nut, gtB),
        tu.danh_muc.vonBanDauUsd, hong)))


@app.get("/api/ban-tham-so")
def api_ban_tham_so(n: int = 30) -> JSONResponse:
    """Lịch sử các bản tham số. Bản nào đang chạy, ai đổi, vì sao, đo được gì."""
    tu = _tu()
    if tu is None:
        return _tat()
    return JSONResponse(sach({"tomTat": tu.kho_tham_so.tom_tat(),
                              "lichSu": tu.kho_tham_so.lich_su(int(n))}))


@app.get("/api/ban-tham-so/khac-biet")
def api_khac_biet(a: int, b: int) -> JSONResponse:
    """Bản `b` đổi những núm nào so với bản `a`."""
    tu = _tu()
    if tu is None:
        return _tat()
    return JSONResponse(sach({"a": a, "b": b,
                              "khacBiet": tu.kho_tham_so.khac_biet(a, b)}))


@app.post("/api/ap-dung-tham-so")
def api_ap_dung(nguoi: str) -> JSONResponse:
    """Áp dụng đề xuất đã QUA CỔNG DUYỆT ở lượt `hoc()` gần nhất.

    Bắt buộc khai tên người, và không có mặc định. Máy đo, máy đề xuất, máy
    chặn — máy không tự ký. Chạy `POST /api/hoc` trước, và nhớ rằng phần lớn
    lượt học kết thúc bằng "không đề xuất gì": đó là kết quả hợp lệ.
    """
    tu = _tu()
    return _tat() if tu is None else JSONResponse(sach(tu.ap_dung(nguoi)))


@app.post("/api/quay-lui-tham-so")
def api_quay_lui(veSo: int, nguoi: str, vi: str = "") -> JSONResponse:
    """Quay về nội dung một bản cũ, bằng cách ghi một bản MỚI.

    Không xoá bản sai. Cùng luật với `so_cai.dao()`: một lịch sử sửa được
    thì không còn là lịch sử.
    """
    tu = _tu()
    if tu is None:
        return _tat()
    return JSONResponse(sach(tu.quay_lui(int(veSo), nguoi, vi)))


@app.get("/api/hien-phap")
def api_hien_phap(day_du: bool = False) -> JSONResponse:
    """Luật vận hành, và điều nào đang THẬT SỰ được canh.

    `day_du=true` trả cả `cau` và `vi` của từng điều — `vi` là chuyện đã xảy
    ra dạy ra luật ấy, và nó là phần đáng đọc nhất.
    """
    from thi_bac_ty.hien_phap import soat, tom_tat
    return JSONResponse(sach(soat() if day_du else tom_tat()))


@app.get("/api/dong-co-chua-co")
def api_dong_co_chua_co(day_du: bool = False) -> JSONResponse:
    """Engine chưa dựng, và điều kiện chặn của từng cái — CHẠY ĐƯỢC.

    `day_du=true` trả cả từng điều kiện kèm chi tiết. Ba trạng thái:
    `CHAN` (không quét được), `QUET_DUOC` (quét được, chưa thực thi được),
    `SAN_SANG`.
    """
    from dong_co_chua_co.so_dang_ky import soat, tom_tat
    return JSONResponse(sach(soat() if day_du else tom_tat()))


@app.post("/api/cau-dao/dong-lai")
def api_dong_cau_dao(ma: str, nguoi: str) -> JSONResponse:
    """Đóng lại một lý do ngắt. **Bắt buộc có tên người.**

    `nguoi` không có mặc định ở đây cũng như ở `CauDao.dong_lai()`: máy phát
    hiện sự cố nhanh hơn người, nhưng máy không phân biệt được "sự cố đã qua"
    với "sự cố vẫn còn nhưng tín hiệu tạm im".
    """
    tu = _tu()
    if tu is None:
        return _tat()
    if not (nguoi or "").strip():
        return JSONResponse({"xong": False,
                             "vi": "phải khai tên người đóng cầu dao"},
                            status_code=400)
    xong = tu.cau_dao.dong_lai(ma, nguoi.strip(), tu.so_cai)
    return JSONResponse(sach({"xong": xong, "ma": ma, "nguoi": nguoi,
                              "cauDao": tu.cau_dao.tom_tat()}))


@app.post("/api/lat-cat")
def lat_cat() -> JSONResponse:
    duong = ghi_lat_cat(runtime)
    return JSONResponse({"daGhi": duong is not None, "duong": str(duong or "")})


@app.get("/")
def trang_chu() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.middleware("http")
async def _khong_giu_ban_cu(yc, tiep):
    """Buồng lái KHÔNG được phục vụ bản cũ từ cache trình duyệt.

    Trang này chỉ chạy ở localhost và được sửa rất liên tay. Một bản `app.js`
    cũ kẹt trong cache là cả giờ đồng hồ đi tìm một lỗ hổng không tồn tại —
    mã trên đĩa đã đúng, chỉ trình duyệt là chưa biết.
    """
    tl = await tiep(yc)
    tl.headers["Cache-Control"] = "no-store, must-revalidate"
    return tl


app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="web")
