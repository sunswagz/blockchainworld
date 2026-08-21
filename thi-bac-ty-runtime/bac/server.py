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
