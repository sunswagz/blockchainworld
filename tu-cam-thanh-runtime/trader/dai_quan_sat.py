"""ĐÀI QUAN SÁT TRADER — nghiên cứu trader thật, KHÔNG sao chép họ.

Ranh giới của cả file, nói trước vì mọi thứ dưới đây phục vụ nó: đây là
**trader-research**, không phải copy-trading. Đầu ra không bao giờ là "A đang
LONG nên ta LONG", mà là những mẫu hành vi lặp lại — và mẫu đó vẫn phải đi qua
backtest rồi cửa duyệt champion như mọi ý tưởng khác.

## Nguồn nào dùng được — đo tại máy này, 16/08/2026

    Hyperliquid   leaderboard 41.794 trader · userFills tới 2000 lệnh/địa chỉ
                  · portfolio có chuỗi giá trị tài khoản · KHÔNG cần khoá
    OKX           copytrading/public-lead-traders · có chuỗi pnlRatios · không khoá
    dYdX          indexer công khai; địa chỉ phải là địa chỉ dydx1... thật
    Binance       leaderboard trả 404 — bỏ, đúng như tài liệu thiết kế đã ngờ

Chỉ dùng API công khai được phép. Không cào lén, không cố xuyên qua dữ liệu
riêng tư của ai.

## Hai cái bẫy được chặn thẳng trong mã

**1. PnL cao ≠ trader giỏi.** Dòng đầu leaderboard hôm nay: tài khoản 61,9 triệu
đô, tuần lãi 1,99 triệu — mà allTime **lỗ 397 nghìn**. Xếp hạng theo PnL là xếp
hạng theo vốn lớn cộng may mắn. `cham_diem()` cho PnL đúng 10% trọng số, và
phần lớn điểm nằm ở sụt giảm, ổn định và kỷ luật rủi ro.

**2. Thiên lệch kẻ sống sót.** Chỉ học TOP là học từ những người còn đứng đây.
`lay_mau()` cố tình lấy cả nhóm giữa và nhóm ĐANG LỖ — người thua dạy được
những thứ người thắng không dạy được.
"""
from __future__ import annotations

import statistics
import time
from typing import Any

import httpx

from .bus import bus

UA = {"User-Agent": "Mozilla/5.0 (compatible; tu-cam-thanh/0.1)"}
HL_INFO = "https://api.hyperliquid.xyz/info"
HL_LB = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"
OKX_LEAD = "https://www.okx.com/api/v5/copytrading/public-lead-traders"

# Trọng số điểm chất lượng. Tổng 100. Để tường minh ở đây chứ không rải trong
# thân hàm — đổi một con số trong này là đổi định nghĩa "trader giỏi", và việc
# đó phải nhìn thấy được trong git diff.
TRONG_SO = {
    "loiNhuan": 10,        # PnL — cố tình THẤP
    "roi": 10,
    "sutGiam": 15,         # rút từ chuỗi giá trị tài khoản thật
    "onDinh": 15,          # lãi đều qua nhiều cửa sổ hay ăn một phát
    "hieuChinhRuiRo": 15,  # ROI trên mỗi phần trăm sụt giảm
    "soLenh": 5,
    "thamNien": 10,
    "daDangCheDo": 5,      # CHƯA TÍNH ĐƯỢC — xem ghi chú ở `cham_diem`
    "kyLuatRuiRo": 10,
    "phatThanhLy": 5,
}

HANG = [(90, "MASTER"), (80, "ELITE"), (70, "STRONG"), (60, "WATCH"), (0, "BO_QUA")]


def _f(x: Any, m: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return m


# ── thu thập ──────────────────────────────────────────────────────────────
def leaderboard(client: httpx.Client) -> list[dict]:
    """Toàn bộ bảng xếp hạng Hyperliquid. ~34 MB, nên đừng gọi trong vòng lặp."""
    r = client.get(HL_LB, headers=UA, timeout=120)
    r.raise_for_status()
    rows = r.json()["leaderboardRows"]
    out = []
    for x in rows:
        cua = {k: v for k, v in x.get("windowPerformances") or []}
        out.append({
            "san": "hyperliquid", "diaChi": x.get("ethAddress"),
            "ten": x.get("displayName"),
            "von": _f(x.get("accountValue")),
            "ngay": cua.get("day", {}), "tuan": cua.get("week", {}),
            "thang": cua.get("month", {}), "toanThoi": cua.get("allTime", {}),
        })
    return out


def _hl(client: httpx.Client, body: dict) -> Any:
    r = client.post(HL_INFO, json=body, headers=UA, timeout=45)
    r.raise_for_status()
    return r.json()


def lenh_khop(client: httpx.Client, dia_chi: str) -> list[dict]:
    return _hl(client, {"type": "userFills", "user": dia_chi})


def duong_von(client: httpx.Client, dia_chi: str) -> dict:
    """Chuỗi giá trị tài khoản theo thời gian — nguồn của SỤT GIẢM THẬT.

    Đây là thứ leaderboard không cho, và cũng là thứ tách "giỏi" khỏi "may"
    rõ nhất: hai người cùng ROI 40% mà một người sụt 7% còn một người sụt 38%
    thì họ không làm cùng một nghề.
    """
    return {k: v for k, v in _hl(client, {"type": "portfolio", "user": dia_chi})}


def okx_lead(client: httpx.Client) -> list[dict]:
    r = client.get(OKX_LEAD, params={"instType": "SWAP"}, headers=UA, timeout=30)
    r.raise_for_status()
    d = (r.json().get("data") or [{}])[0]
    out = []
    for x in d.get("ranks") or []:
        ty = [_f(p.get("pnlRatio")) for p in x.get("pnlRatios") or []]
        out.append({
            "san": "okx", "diaChi": x.get("uniqueCode"), "ten": x.get("nickName"),
            "von": _f(x.get("aum")), "soNgayDanDat": _f(x.get("leadDays")),
            "loiNhuan": _f(x.get("pnl")), "tyLe": _f(x.get("pnlRatio")),
            "chuoiTyLe": ty, "soNguoiCopy": _f(x.get("copyTraderNum")),
        })
    return out


# ── chấm điểm ─────────────────────────────────────────────────────────────
def _thang(gt: float, xau: float, tot: float) -> float:
    """Đưa một chỉ số về 0..1 tuyến tính giữa hai mốc, kẹp hai đầu."""
    if tot == xau:
        return 0.0
    return max(0.0, min(1.0, (gt - xau) / (tot - xau)))


def sut_giam(chuoi: list[list]) -> float | None:
    """Sụt giảm sâu nhất tính từ chuỗi giá trị tài khoản, theo %."""
    gt = [_f(v) for _, v in chuoi if _f(v) > 0]
    if len(gt) < 3:
        return None
    dinh, sut = gt[0], 0.0
    for v in gt:
        dinh = max(dinh, v)
        sut = max(sut, (dinh - v) / dinh * 100)
    return round(sut, 2)


def cham_diem(t: dict, chi_tiet: dict | None = None) -> dict:
    """Điểm chất lượng 0..100. **Không xếp theo PnL.**

    `chi_tiet` là dữ liệu sâu (đường vốn, lệnh khớp) nếu đã lấy. Không có thì
    những phần cần nó bị đánh dấu `chuaDo` chứ KHÔNG bị cho điểm 0 — cho 0 là
    phạt người mình chưa buồn đo, và bảng xếp hạng sẽ nghiêng về đúng những
    trader mình lấy được nhiều dữ liệu nhất.
    """
    ct = chi_tiet or {}
    phan: dict[str, Any] = {}
    chua_do: list[str] = []

    tt = t.get("toanThoi") or {}
    thg = t.get("thang") or {}
    tuan = t.get("tuan") or {}

    roi_tt = _f(tt.get("roi"))
    pnl_tt = _f(tt.get("pnl"))

    phan["loiNhuan"] = _thang(pnl_tt, 0, 1_000_000)
    phan["roi"] = _thang(roi_tt, -0.2, 1.0)

    sg = ct.get("sutGiamPct")
    if sg is None:
        chua_do.append("sutGiam")
    else:
        # 5% sụt là rất tốt, 50% là rất tệ.
        phan["sutGiam"] = _thang(-sg, -50, -5)

    # Ổn định: lãi ở bao nhiêu cửa sổ trong bốn. Ăn một phát rồi lỗ dài thì
    # allTime âm và điểm này rơi.
    dem = sum(1 for c in (t.get("ngay"), tuan, thg, tt) if _f((c or {}).get("pnl")) > 0)
    phan["onDinh"] = dem / 4

    if sg is None:
        chua_do.append("hieuChinhRuiRo")
    else:
        # ROI trên mỗi phần trăm sụt giảm — 40%/7% ≈ 5,7 là rất tốt.
        phan["hieuChinhRuiRo"] = _thang(roi_tt * 100 / max(sg, 1.0), 0, 5)

    n = ct.get("soLenh")
    if n is None:
        chua_do.append("soLenh")
    else:
        phan["soLenh"] = _thang(n, 20, 500)

    tn = ct.get("soNgay") or t.get("soNgayDanDat")
    if tn is None:
        chua_do.append("thamNien")
    else:
        phan["thamNien"] = _thang(tn, 30, 365)

    # Đa dạng chế độ thị trường: CHƯA TÍNH ĐƯỢC. Cần ghép từng lệnh với chế độ
    # thị trường tại đúng thời điểm đó, mà chế độ hiện chỉ tính cho BTCUSDT còn
    # trader Hyperliquid vào lệnh trên hàng chục coin. Đánh dấu chưa đo thay vì
    # cho một con số bịa — bịa ở đây sẽ nghiêng bảng xếp hạng theo một chiều
    # không ai kiểm được.
    chua_do.append("daDangCheDo")

    kl = ct.get("kyLuat")
    if kl is None:
        chua_do.append("kyLuatRuiRo")
    else:
        phan["kyLuatRuiRo"] = kl

    tl = ct.get("soLanThanhLy")
    if tl is None:
        chua_do.append("phatThanhLy")
    else:
        phan["phatThanhLy"] = 1.0 if tl == 0 else max(0.0, 1 - tl * 0.34)

    # Chuẩn hoá theo phần ĐÃ ĐO, không theo tổng 100 — nếu không thì càng ít dữ
    # liệu điểm càng thấp, và ta lại đang xếp hạng theo độ chăm chỉ của mình.
    tong_ts = sum(TRONG_SO[k] for k in phan)
    diem = sum(phan[k] * TRONG_SO[k] for k in phan) / tong_ts * 100 if tong_ts else 0.0

    return {
        "diem": round(diem, 1),
        "hang": next(h for m, h in HANG if diem >= m),
        "phan": {k: round(v, 3) for k, v in phan.items()},
        "chuaDo": chua_do,
        "doPhu": round(tong_ts / sum(TRONG_SO.values()) * 100),
    }


# ── giải phẫu hành vi ─────────────────────────────────────────────────────
def ho_so(fills: list[dict]) -> dict:
    """Dựng hồ sơ hành vi từ lệnh khớp. Đây là phần 'giải ngược hành vi'.

    Trả về những thứ đo được thật, và KHÔNG suy diễn thêm. Việc hỏi "vì sao họ
    vào lệnh ở đây" cần ghép với dữ liệu thị trường tại đúng thời điểm — đó là
    bước sau, và nó cần bộ não thật chứ không phải mấy dòng thống kê này.
    """
    if not fills:
        return {"soLenh": 0}

    mo = [f for f in fills if str(f.get("dir", "")).startswith("Open")]
    dong = [f for f in fills if str(f.get("dir", "")).startswith("Close")]
    thanh_ly = [f for f in fills if "Liquidat" in str(f.get("dir", ""))]

    coin: dict[str, int] = {}
    for f in fills:
        coin[f.get("coin", "?")] = coin.get(f.get("coin", "?"), 0) + 1

    long_mo = sum(1 for f in mo if "Long" in str(f.get("dir")))
    chu_dong = sum(1 for f in fills if f.get("crossed"))

    pnl = [_f(f.get("closedPnl")) for f in dong]
    lai = [p for p in pnl if p > 0]
    lo = [p for p in pnl if p < 0]

    # Giữ bao lâu: ghép mở↔đóng theo coin, theo thứ tự thời gian.
    theo_coin: dict[str, list] = {}
    for f in sorted(fills, key=lambda x: x.get("time", 0)):
        theo_coin.setdefault(f.get("coin", "?"), []).append(f)
    giu: list[float] = []
    for ds in theo_coin.values():
        mo_luc = None
        for f in ds:
            d = str(f.get("dir", ""))
            if d.startswith("Open") and mo_luc is None:
                mo_luc = f.get("time")
            elif d.startswith("Close") and mo_luc:
                giu.append((f.get("time", 0) - mo_luc) / 3_600_000)
                mo_luc = None

    tong_lai = sum(lai)
    lon_nhat = max(lai) if lai else 0.0

    return {
        "soLenh": len(fills), "soMo": len(mo), "soDong": len(dong),
        "soLanThanhLy": len(thanh_ly),
        "coinHayDanh": sorted(coin.items(), key=lambda x: -x[1])[:5],
        "tyLeLong": round(long_mo / len(mo), 3) if mo else None,
        "tyLeChuDong": round(chu_dong / len(fills), 3),
        "giuTrungVi_gio": round(statistics.median(giu), 2) if giu else None,
        "giuTrungBinh_gio": round(statistics.fmean(giu), 2) if giu else None,
        "soLenhCoLai": len(lai), "soLenhLo": len(lo),
        "tyLeThang": round(len(lai) / len(pnl) * 100, 1) if pnl else None,
        "laiTrungBinh": round(statistics.fmean(lai), 2) if lai else None,
        "loTrungBinh": round(statistics.fmean(lo), 2) if lo else None,
        # PHÁT HIỆN TRADER ĂN MAY: một lệnh chiếm bao nhiêu phần tổng lãi.
        # Trên 50% nghĩa là thành tích đến từ một cú, không phải một nghề.
        "phanTramLaiTuLenhLonNhat": round(lon_nhat / tong_lai * 100, 1) if tong_lai > 0 else None,
        "tuLuc": min((f.get("time", 0) for f in fills), default=None),
        "denLuc": max((f.get("time", 0) for f in fills), default=None),
    }


def ky_luat(hs: dict) -> float | None:
    """Điểm kỷ luật rủi ro 0..1, rút từ hành vi chứ không từ lời khai.

    Ba dấu hiệu, mỗi cái là một cách người ta tự huỷ:
      · thanh lý       — để sàn đóng hộ thay vì tự cắt
      · lỗ trung bình lớn hơn lãi trung bình nhiều lần
      · thành tích dồn vào một lệnh
    """
    if not hs.get("soDong"):
        return None
    d = 1.0
    if hs.get("soLanThanhLy"):
        d -= min(0.5, hs["soLanThanhLy"] * 0.17)
    lai, lo = hs.get("laiTrungBinh"), hs.get("loTrungBinh")
    if lai and lo:
        ty = lai / abs(lo)
        if ty < 0.7:
            d -= 0.25
        elif ty < 1.0:
            d -= 0.1
    p = hs.get("phanTramLaiTuLenhLonNhat")
    if p is not None and p > 50:
        d -= 0.25
    return round(max(0.0, d), 3)


def an_may(hs: dict) -> dict:
    """Có phải thành tích đến từ may mắn không. Trả cờ + lý do đọc được."""
    ly_do = []
    p = hs.get("phanTramLaiTuLenhLonNhat")
    if p is not None and p > 50:
        ly_do.append(f"{p}% tổng lãi đến từ MỘT lệnh")
    if (hs.get("soDong") or 0) < 30:
        ly_do.append(f"chỉ {hs.get('soDong')} lệnh đã đóng — mẫu quá nhỏ")
    if hs.get("soLanThanhLy"):
        ly_do.append(f"bị thanh lý {hs['soLanThanhLy']} lần")
    return {"nghiNgo": bool(ly_do), "lyDo": ly_do}


# ── phễu ──────────────────────────────────────────────────────────────────
def lay_mau(lb: list[dict], moi_nhom: int = 12) -> dict[str, list[dict]]:
    """Lấy mẫu CÓ CHỦ Ý gồm cả người thua — chống thiên lệch kẻ sống sót.

    Chỉ học TOP là học từ những người còn đứng đây, và bỏ qua toàn bộ thông tin
    nằm ở chỗ người ta gục. Ba nhóm: đỉnh, giữa, và đang lỗ.
    """
    # ROI CAO CŨNG KHÔNG ĐỒNG NGHĨA TRADER GIỎI — người anh em của cái bẫy PnL.
    #
    # Lần chạy đầu, nhóm đỉnh ra ROI trung bình **4.170.644%**. Không ai giao
    # dịch được như vậy: đó là tài khoản khởi điểm gần $0 rồi nạp thêm tiền, nên
    # mẫu số bé tí và ROI hoá vô nghĩa. Xếp hạng theo nó là xếp hạng theo việc
    # ai bắt đầu bằng số vốn nhỏ nhất.
    #
    # Hai hàng rào: ROI phải nằm trong khoảng người thật với tới được, và khối
    # lượng phải đủ lớn so với vốn — người thật giao dịch thì có volume, còn
    # tài khoản chỉ nạp tiền vào thì không.
    def hop_le(t: dict) -> bool:
        tt = t.get("toanThoi") or {}
        roi, vlm = _f(tt.get("roi")), _f(tt.get("vlm"))
        if t["von"] < 50_000 or vlm <= 0:
            return False
        if roi > 20.0:            # >2000% — gần như luôn là hiện vật, không phải thành tích
            return False
        return vlm >= t["von"]     # có giao dịch thật, không chỉ nạp tiền

    co = [t for t in lb if hop_le(t)]
    theo_roi = sorted(co, key=lambda t: -_f((t.get("toanThoi") or {}).get("roi")))
    n = len(theo_roi)
    giua = n // 2
    return {
        "dinh": theo_roi[:moi_nhom],
        "giua": theo_roi[max(0, giua - moi_nhom // 2): giua + moi_nhom // 2],
        "dangLo": [t for t in reversed(theo_roi)
                   if _f((t.get("toanThoi") or {}).get("roi")) < 0][:moi_nhom],
        "tong": n,
    }
