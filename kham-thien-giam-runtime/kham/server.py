"""Buồng lái — FastAPI, CHỈ sống ở localhost.

Buồng lái này có nút điều khiển và đọc được cấu hình, nên nó **không bao giờ
lên site**. Đúng cùng lý do `tu-cam-thanh-runtime` giữ buồng lái ở
`localhost:5182`: một trang công khai mà bấm được nút đặt lệnh, hoặc gọi được
model, là khoá đã ra tới trình duyệt.

Cung tĩnh và buồng lái cố ý là HAI giao diện khác nhau:

    cung tĩnh (5185)     quan sát. lên GitHub Pages. không nút nào.
    buồng lái (5186)     điều khiển. chỉ ở máy. không lên đâu cả.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .bang import doc_bang, may_ghi
from .chay_lai import ThamSo, doi_chieu, mot_luot
from .bus import bus
from .config import CONFIG, WEB_DIR, che_hieu_luc, ly_do_khong_that, nao_cham_bat
from .sach import sach
from .snapshot import ghi_lat_cat
from .vong import runtime

app = FastAPI(title="Khâm Thiên Giám", docs_url=None, redoc_url=None)


@app.on_event("startup")
def _bat() -> None:
    runtime.bat()


@app.on_event("shutdown")
def _dung() -> None:
    runtime.dung()


# ── trạng thái ────────────────────────────────────────────────────────────
@app.get("/api/trang-thai")
def trang_thai() -> JSONResponse:
    return JSONResponse(sach(runtime.anh_chup()))


@app.get("/api/cau-hinh")
def cau_hinh() -> JSONResponse:
    """Cấu hình đang có hiệu lực. KHÔNG trả về bất cứ khoá nào.

    Chỉ trả về `có khoá hay không`, không bao giờ trả về giá trị. Buồng lái
    chạy ở localhost nhưng localhost vẫn là một trình duyệt, và một tiện ích
    mở rộng đọc được tab là đọc được khoá.
    """
    return JSONResponse(sach({
        "che": CONFIG.get("che"),
        "cheHieuLuc": che_hieu_luc(),
        "cuaDangDong": ly_do_khong_that(),
        "coKhoaModel": nao_cham_bat(),
        "port": CONFIG["port"],
        "nhipGiay": CONFIG["loopSeconds"],
        "phi": CONFIG["phi"],
        "canLoi": CONFIG["canLoi"],
        "khoDoi": CONFIG["khoDoi"],
        "ruiRo": CONFIG["ruiRo"],
        "dinhGia": CONFIG["dinhGia"],
        "thiTruong": CONFIG["thiTruong"],
    }))


@app.get("/api/nhat-ky")
def nhat_ky(n: int = 200) -> JSONResponse:
    return JSONResponse(sach({"tong": bus.tong(), "dong": bus.gan_day(n)}))


# ── điều khiển ────────────────────────────────────────────────────────────
@app.post("/api/tam-dung")
def tam_dung() -> JSONResponse:
    runtime.tamDung = not runtime.tamDung
    bus.ghi("tạm dừng" if runtime.tamDung else "chạy tiếp", loai="he")
    return JSONResponse({"tamDung": runtime.tamDung})


@app.post("/api/chien-thuat/{ma}")
def bat_tat(ma: str) -> JSONResponse:
    if ma not in runtime.batTat:
        return JSONResponse({"loi": "không có chiến thuật này"}, status_code=404)
    runtime.batTat[ma] = not runtime.batTat[ma]
    bus.ghi(f"chiến thuật {ma}: {'bật' if runtime.batTat[ma] else 'tắt'}", loai="he")
    return JSONResponse({"ma": ma, "bat": runtime.batTat[ma]})


@app.post("/api/cau-dao")
def cau_dao(mo: bool = False) -> JSONResponse:
    """Ngắt hoặc mở lại cầu dao. Ngắt thì tức thì; mở lại phải cố ý."""
    if mo:
        runtime.risk.mo_lai()
        bus.ghi("cầu dao mở lại bằng tay", loai="he")
    else:
        runtime.risk.ngat("ngắt bằng tay từ buồng lái")
        bus.ghi("CẦU DAO NGẮT bằng tay", loai="canh")
    return JSONResponse(sach(runtime.risk.tom_tat()))


@app.post("/api/huy/{lenhId}")
def huy(lenhId: str) -> JSONResponse:
    return JSONResponse({"huy": runtime.cong.huy(lenhId)})


# ── băng ghi ──────────────────────────────────────────────────────────────
@app.get("/api/bang")
def bang(tuNgay: str | None = None) -> JSONResponse:
    k = doc_bang(tuNgay)
    return JSONResponse({"soKhung": len(k), "dangGhi": may_ghi.bat,
                         "khungDaGhi": may_ghi.soKhung})


@app.post("/api/chay-lai")
def api_chay_lai(tuNgay: str | None = None, nguong: float | None = None) -> JSONResponse:
    """Chạy lại băng với ngưỡng net edge hiện tại (hoặc ngưỡng truyền vào)."""
    cl = CONFIG["canLoi"]
    ts = ThamSo(ten="hien-tai",
                netEdgeToiThieu=nguong if nguong is not None else float(cl["netEdgeToiThieu"]),
                bienAnToan=float(cl["bienAnToan"]))
    return JSONResponse(sach(mot_luot(doc_bang(tuNgay), ts).tom_tat()))


@app.post("/api/doi-chieu")
def api_doi_chieu(nguongA: float, nguongB: float,
                  tuNgay: str | None = None) -> JSONResponse:
    """So HAI bộ tham số trên CÙNG băng — đây mới là backtest."""
    cl = CONFIG["canLoi"]
    at = float(cl["bienAnToan"])
    a = ThamSo(ten=f"A(net>={nguongA})", netEdgeToiThieu=nguongA, bienAnToan=at)
    b = ThamSo(ten=f"B(net>={nguongB})", netEdgeToiThieu=nguongB, bienAnToan=at)
    return JSONResponse(sach(doi_chieu(doc_bang(tuNgay), a, b)))


@app.post("/api/vo-dich/{ma}")
def api_vo_dich(ma: str, nhom: str = "chung") -> JSONResponse:
    """Xét một chiến thuật lên đương kim. KHÔNG có đường tắt."""
    from .vo_dich import so_vo_dich
    px = so_vo_dich.xet(ma, nhom)
    return JSONResponse(sach({"cho": px.cho, "lyDo": px.lyDo,
                              "soVoDich": so_vo_dich.tom_tat()}))


# ── ghi ra cung tĩnh ──────────────────────────────────────────────────────
@app.post("/api/lat-cat")
def lat_cat() -> JSONResponse:
    duong = ghi_lat_cat(runtime)
    return JSONResponse({"daGhi": duong is not None, "duong": str(duong or "")})


# ── giao diện ─────────────────────────────────────────────────────────────
@app.get("/")
def trang_chu() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="web")
