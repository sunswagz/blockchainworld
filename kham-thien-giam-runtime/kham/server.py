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

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse as _JR
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .bang import NguonKhung, dem_bang, may_ghi
from .chay_lai import ThamSo, doi_chieu, mot_luot
from .bus import bus
from .config import CONFIG, WEB_DIR, che_hieu_luc, ly_do_khong_that, nao_cham_bat
from .sach import sach
from .snapshot import ghi_lat_cat
from .vong import runtime

app = FastAPI(title="Khâm Thiên Giám", docs_url=None, redoc_url=None)


#: Origin được phép gửi lệnh ĐỔI TRẠNG THÁI.
def _origin_cho_phep() -> set[str]:
    c = CONFIG["port"]
    return {f"http://localhost:{c}", f"http://127.0.0.1:{c}",
            f"http://[::1]:{c}"}


@app.middleware("http")
async def _chan_lenh_tu_trang_khac(request: Request, call_next):
    """Chặn POST đến từ một trang KHÁC. Đây là lỗ hổng thật, không phải giả định.

    Mọi lối POST ở đây — `tam-dung`, `cau-dao`, `chien-thuat/{ma}`,
    `huy/{lenhId}`, `tien-hoa`, `chay-lai` — đều KHÔNG thân, KHÔNG xác
    thực. Nghĩa là bất kỳ trang web nào người vận hành mở trong cùng trình
    duyệt đều gọi được:

        fetch("http://localhost:5186/api/tam-dung",
              {method: "POST", mode: "no-cors"})

    Đây là "simple request" nên trình duyệt KHÔNG hỏi preflight; trang kia
    không đọc được phản hồi, nhưng **tác dụng phụ đã xảy ra**: bot dừng,
    cầu dao lật, chiến thuật tắt, lệnh bị huỷ. Buồng lái nghe ở 127.0.0.1
    không cứu được — chính trình duyệt trên máy ấy là kẻ gửi.

    Cách chặn: trình duyệt LUÔN gửi `Origin` cho POST khác trang. Nên:

      · có `Origin` mà không nằm trong danh sách  → TỪ CHỐI
      · có `Origin` đúng (buồng lái tự gọi)        → cho qua
      · KHÔNG có `Origin` (curl, script, dịch vụ)  → cho qua

    Ca thứ ba nghe như một lỗ, nhưng không phải: thứ ta chặn là TRÌNH
    DUYỆT bị lừa. Một chương trình chạy trên máy này vốn đã làm được mọi
    thứ nó muốn mà chẳng cần hỏi buồng lái.

    GET không chặn: nó chỉ đọc, và `/api/cau-hinh` đã cố ý không bao giờ
    trả về khoá nào.
    """
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        o = request.headers.get("origin")
        if o and o not in _origin_cho_phep():
            bus.ghi(f"TỪ CHỐI lệnh POST từ trang khác: {o} → "
                    f"{request.url.path}", loai="canh")
            return _JR(status_code=403, content={
                "loi": "lệnh đổi trạng thái phải đến từ chính buồng lái",
                "origin": o})
    return await call_next(request)


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
    runtime.ghi_dieu_khien()          # quyết định của NGƯỜI phải sống sót
    bus.ghi("tạm dừng" if runtime.tamDung else "chạy tiếp", loai="he")
    return JSONResponse({"tamDung": runtime.tamDung})


@app.post("/api/chien-thuat/{ma}")
def bat_tat(ma: str) -> JSONResponse:
    if ma not in runtime.batTat:
        return JSONResponse({"loi": "không có chiến thuật này"}, status_code=404)
    runtime.batTat[ma] = not runtime.batTat[ma]
    runtime.ghi_dieu_khien()          # quyết định của NGƯỜI phải sống sót
    bus.ghi(f"chiến thuật {ma}: {'bật' if runtime.batTat[ma] else 'tắt'}", loai="he")
    return JSONResponse({"ma": ma, "bat": runtime.batTat[ma]})


@app.post("/api/cau-dao")
def cau_dao(mo: bool = False) -> JSONResponse:
    """Ngắt hoặc mở lại cầu dao. Ngắt thì tức thì; mở lại phải cố ý."""
    if mo:
        runtime.risk.mo_lai()
        bus.ghi("cầu dao mở lại bằng tay", loai="he")
    else:
        runtime.risk.ngat("ngắt bằng tay từ buồng lái", loai="tay")
        bus.ghi("CẦU DAO NGẮT bằng tay", loai="canh")
    return JSONResponse(sach(runtime.risk.tom_tat()))


@app.post("/api/huy/{lenhId}")
def huy(lenhId: str) -> JSONResponse:
    return JSONResponse({"huy": runtime.cong.huy(lenhId)})


# ── băng ghi ──────────────────────────────────────────────────────────────
@app.get("/api/bang")
def bang(tuNgay: str | None = None) -> JSONResponse:
    """Băng có bao nhiêu khung, và có LÀNH không.

    `dem_bang` đếm mà không giữ khung nào lại: bản trước gọi `doc_bang()` rồi
    `len()`, tức dựng cả gigabyte đối tượng Python trên một luồng của buồng
    lái để đọc ra một số nguyên.

    Trả kèm `bao` — số file hỏng, số dòng mất, số byte phải bỏ qua. Băng hỏng
    mà bảng vẫn hiện một con số tròn trịa thì mọi phép hậu kiểm sau đó đều
    đúng công thức trên dữ liệu bị cắt, và không ai biết.
    """
    bao = dem_bang(tuNgay)
    return JSONResponse({"soKhung": bao.soKhung, "dangGhi": may_ghi.bat,
                         "khungDaGhi": may_ghi.soKhung,
                         "bao": bao.tom_tat()})


@app.post("/api/chay-lai")
def api_chay_lai(tuNgay: str | None = None, nguong: float | None = None) -> JSONResponse:
    """Chạy lại băng với ngưỡng net edge hiện tại (hoặc ngưỡng truyền vào)."""
    cl = CONFIG["canLoi"]
    ts = ThamSo(ten="hien-tai",
                netEdgeToiThieu=nguong if nguong is not None else float(cl["netEdgeToiThieu"]),
                bienAnToan=float(cl["bienAnToan"]))
    return JSONResponse(sach(mot_luot(NguonKhung(tuNgay), ts).tom_tat()))


@app.post("/api/doi-chieu")
def api_doi_chieu(nguongA: float, nguongB: float,
                  tuNgay: str | None = None) -> JSONResponse:
    """So HAI bộ tham số trên CÙNG băng — đây mới là backtest."""
    cl = CONFIG["canLoi"]
    at = float(cl["bienAnToan"])
    a = ThamSo(ten=f"A(net>={nguongA})", netEdgeToiThieu=nguongA, bienAnToan=at)
    b = ThamSo(ten=f"B(net>={nguongB})", netEdgeToiThieu=nguongB, bienAnToan=at)
    return JSONResponse(sach(doi_chieu(NguonKhung(tuNgay), a, b)))


@app.post("/api/vo-dich/{ma}")
def api_vo_dich(ma: str, nhom: str = "chung") -> JSONResponse:
    """Xét một chiến thuật lên đương kim. KHÔNG có đường tắt."""
    from .vo_dich import so_vo_dich
    px = so_vo_dich.xet(ma, nhom)
    return JSONResponse(sach({"cho": px.cho, "lyDo": px.lyDo,
                              "soVoDich": so_vo_dich.tom_tat()}))


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


# ── ghi ra cung tĩnh ──────────────────────────────────────────────────────
@app.post("/api/lat-cat")
def lat_cat() -> JSONResponse:
    duong = ghi_lat_cat(runtime)
    return JSONResponse({"daGhi": duong is not None, "duong": str(duong or "")})


# ── giao diện ─────────────────────────────────────────────────────────────
@app.get("/")
def trang_chu() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.middleware("http")
async def _khong_giu_ban_cu(yc, tiep):
    """Buồng lái KHÔNG được phép phục vụ bản cũ từ cache trình duyệt.

    Trang này chỉ chạy ở localhost và được sửa rất liên tay. Một bản
    `app.js` cũ kẹt trong cache là cả giờ đồng hồ đi tìm một lỗ hổng
    không tồn tại — mã trên đĩa đã đúng, chỉ trình duyệt là chưa biết.
    Không có lợi ích nào từ cache ở đây để đánh đổi lấy chuyện đó.
    """
    tl = await tiep(yc)
    tl.headers["Cache-Control"] = "no-store, must-revalidate"
    return tl


app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="web")
