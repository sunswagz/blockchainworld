"""ĐỒNG THUẬN CỦA TRADER GIỎI — và lý do KHÔNG được đi theo nó một cách mù quáng.

Ba phần, và phần thứ hai mới là phần đáng giá:

1. ELITE POSITIONING INDEX — đếm, có trọng số VỐN, và có trọng số CHẤT LƯỢNG
2. **Cảnh báo chen chúc** — "70% trader LONG ⇒ LONG" là đúng cái sai mà tài
   liệu thiết kế cấm. Khi tất cả cùng một phía, phía đó đã hết người mua.
3. Chọn CHUYÊN GIA theo chế độ hiện tại — không hỏi người giỏi xu hướng lúc
   thị trường đi ngang.

Điểm quan trọng nhất: hàm `phan_quyet()` có quyền trả **DUNG_THEO** kể cả khi
đồng thuận rất mạnh. Một chỉ số đồng thuận mà không bao giờ nói "đừng theo" thì
chỉ là một cái máy khuếch đại đám đông đội lốt phân tích.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

TRONG_SO_HANG = {"MASTER": 4.0, "ELITE": 3.0, "STRONG": 2.0, "WATCH": 1.0, "BO_QUA": 0.0}


def _f(x: Any, m: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return m


def chi_so(traders: list[dict], coin: str = "BTC") -> dict:
    """Ba cách đếm cho cùng một câu hỏi — và chúng thường không đồng ý với nhau.

    Đếm theo ĐẦU NGƯỜI, theo VỐN, theo CHẤT LƯỢNG. Chỗ ba con số này lệch nhau
    chính là thông tin: nếu đầu người nghiêng LONG mà vốn nghiêng SHORT thì
    nghĩa là số đông nhỏ đang đối đầu với vài người lớn.
    """
    dem = {"LONG": 0, "SHORT": 0}
    von = {"LONG": 0.0, "SHORT": 0.0}
    chat = {"LONG": 0.0, "SHORT": 0.0}
    theo_hang: dict[str, dict[str, int]] = defaultdict(lambda: {"LONG": 0, "SHORT": 0})
    gop: list[dict] = []

    for t in traders:
        for p in t.get("viThe") or []:
            if p.get("coin") != coin:
                continue
            sz = _f(p.get("sz"))
            if sz == 0:
                continue
            huong = "LONG" if sz > 0 else "SHORT"
            gt = abs(_f(p.get("giaTriUsd")))
            hang = (t.get("diem") or {}).get("hang", "BO_QUA")
            dem[huong] += 1
            von[huong] += gt
            chat[huong] += TRONG_SO_HANG.get(hang, 0.0)
            theo_hang[hang][huong] += 1
            gop.append({"diaChi": t.get("diaChi"), "hang": hang, "huong": huong,
                        "giaTriUsd": round(gt, 2),
                        "diem": (t.get("diem") or {}).get("diem")})

    tong_dem = dem["LONG"] + dem["SHORT"]
    tong_von = von["LONG"] + von["SHORT"]
    tong_chat = chat["LONG"] + chat["SHORT"]

    def ty(a: float, b: float) -> float | None:
        return round(a / b * 100, 1) if b else None

    return {
        "coin": coin, "soViThe": tong_dem,
        "theoDauNguoi": {**dem, "phanTramLong": ty(dem["LONG"], tong_dem)},
        "theoVon": {"LONG": round(von["LONG"], 2), "SHORT": round(von["SHORT"], 2),
                    "phanTramLong": ty(von["LONG"], tong_von)},
        "theoChatLuong": {"LONG": round(chat["LONG"], 1), "SHORT": round(chat["SHORT"], 1),
                          "phanTramLong": ty(chat["LONG"], tong_chat)},
        "theoHang": {k: dict(v) for k, v in theo_hang.items()},
        "viThe": sorted(gop, key=lambda x: -x["giaTriUsd"])[:20],
    }


def canh_bao_chen_chuc(cs: dict, phai_sinh: dict | None) -> dict:
    """Đồng thuận mạnh CỘNG thị trường đã nóng = giao dịch chen chúc.

    Đây là chốt chặn quan trọng nhất của cả module, và nó tồn tại vì một lý do
    rất cụ thể: khi 70% người giỏi đã LONG, phần lớn lực mua đã tiêu rồi. Cộng
    thêm funding cao và open interest cao thì cú quét ngược không phải rủi ro
    xa — nó là cách thị trường lấy lại thanh khoản.
    """
    cb: list[str] = []
    ps = phai_sinh or {}
    p_long = (cs.get("theoChatLuong") or {}).get("phanTramLong")
    if p_long is None or cs.get("soViThe", 0) < 5:
        return {"chenChuc": False, "viSao": ["chưa đủ vị thế để nói gì"], "phanTramLong": p_long}

    lech = abs(p_long - 50)
    if lech >= 20:
        cb.append(f"đồng thuận mạnh một phía: {p_long}% nghiêng LONG theo trọng số chất lượng")

    fund = ps.get("fundingNamHoa")
    if fund is not None:
        if p_long > 60 and fund > 15:
            cb.append(f"funding {fund}%/năm — phe long đang TRẢ RẤT ĐẮT để giữ vị thế")
        if p_long < 40 and fund < -5:
            cb.append(f"funding {fund}%/năm — phe short đang trả để giữ")

    oi = ps.get("oiDoi24hPct")
    if oi is not None and oi > 5 and lech >= 20:
        cb.append(f"open interest tăng {oi}% trong 24h cùng lúc đồng thuận dồn một phía")

    ts = ps.get("toanSan") or {}
    if ts.get("long") is not None:
        bl = ts["long"] * 100
        if (p_long > 60 and bl > 65) or (p_long < 40 and bl < 35):
            cb.append(f"toàn sàn cũng nghiêng cùng chiều ({bl:.0f}% long) — "
                      f"cả người giỏi lẫn đám đông đứng chung một bên")

    return {
        "chenChuc": len(cb) >= 2,
        "viSao": cb or ["không thấy dấu hiệu chen chúc"],
        "phanTramLong": p_long,
        "doLech": round(lech, 1),
    }


def phan_quyet(cs: dict, phai_sinh: dict | None) -> dict:
    """Đọc đồng thuận thành một câu — và câu đó ĐƯỢC PHÉP là "đừng theo".

    Không bao giờ trả về một lệnh mua/bán. Đây là BỐI CẢNH cho bộ não, không
    phải tín hiệu: mọi ý tưởng vẫn phải đi qua backtest rồi cửa duyệt champion.
    """
    cc = canh_bao_chen_chuc(cs, phai_sinh)
    n = cs.get("soViThe", 0)
    if n < 5:
        return {"ketLuan": "CHUA_DU_DU_LIEU",
                "cau": f"chỉ {n} vị thế mở trong mẫu — chưa nói được gì.",
                "chenChuc": cc}

    dn = (cs.get("theoDauNguoi") or {}).get("phanTramLong")
    cl = (cs.get("theoChatLuong") or {}).get("phanTramLong")
    v = (cs.get("theoVon") or {}).get("phanTramLong")

    if cc["chenChuc"]:
        return {"ketLuan": "DUNG_THEO",
                "cau": ("Đồng thuận mạnh NHƯNG thị trường đã chen chúc. Đây là lúc "
                        "đám đông giỏi và đám đông thường đứng cùng một bên — "
                        "đi theo là mua lại chính rủi ro họ đang mang."),
                "chenChuc": cc}

    # Ba cách đếm lệch nhau là thông tin, không phải nhiễu.
    if None not in (dn, cl, v) and (max(dn, cl, v) - min(dn, cl, v)) > 25:
        return {"ketLuan": "MAU_THUAN",
                "cau": (f"Ba cách đếm không đồng ý: đầu người {dn}%, vốn {v}%, "
                        f"chất lượng {cl}% nghiêng LONG. Số đông nhỏ đang đối đầu "
                        f"với vài người lớn — đừng đọc thành một phía."),
                "chenChuc": cc}

    # Không có trọng số chất lượng thì KHÔNG kết luận. Bản đầu viết
    # `(cl or 50) > 50` — khi `cl` là None thì nó thành `50 > 50` ⇒ False ⇒
    # trả về "NGHIENG_SHORT". Tức là bịa ra một hướng từ dữ liệu không có, và
    # câu trả về vẫn kèm "(None%)" nên nhìn thì thấy vô lý mà máy vẫn khẳng
    # định. Đúng cái tội cả hệ thống này được dựng để chặn.
    if cl is None:
        return {"ketLuan": "CHUA_DU_DU_LIEU",
                "cau": ("Không tính được trọng số chất lượng — mẫu chưa có trader nào "
                        "đủ hạng để cân. Không kết luận hướng."),
                "chenChuc": cc}

    if abs(cl - 50) < 12:
        return {"ketLuan": "TRUNG_TINH",
                "cau": f"Người giỏi cũng chia hai phía ({cl}% long). Không có tín hiệu.",
                "chenChuc": cc}

    huong = "LONG" if cl > 50 else "SHORT"
    return {"ketLuan": f"NGHIENG_{huong}",
            "cau": (f"Nhóm chất lượng cao nghiêng {huong} ({cl}%), chưa thấy dấu hiệu "
                    f"chen chúc. Đây là BỐI CẢNH, không phải lệnh vào."),
            "chenChuc": cc}


def chuyen_gia_cho_che_do(traders: list[dict], che_do: str, toi_thieu: int = 5) -> dict:
    """Khi thị trường đang ở chế độ này thì nên hỏi ai.

    Không hỏi người giỏi xu hướng lúc thị trường đi ngang — đó là toàn bộ ý
    của mục 16 trong tài liệu. Ai không có đủ mẫu ở chế độ này thì KHÔNG có
    tên trong danh sách, kể cả khi điểm tổng của họ rất cao.
    """
    ra = []
    for t in traders:
        dd = ((t.get("giaiPhau") or {}).get("daDangCheDo") or {}).get("chiTiet") or {}
        g = dd.get(che_do)
        if not g or g["so"] < toi_thieu:
            continue
        ra.append({
            "diaChi": t.get("diaChi"), "hang": (t.get("diem") or {}).get("hang"),
            "diemTong": (t.get("diem") or {}).get("diem"),
            "phongCach": ((t.get("giaiPhau") or {}).get("phongCach") or {}).get("phongCach"),
            "soVong": g["so"], "tyLeThang": g["tyLeThang"], "pnl": g["pnl"],
        })
    ra.sort(key=lambda x: -x["pnl"])
    return {
        "cheDo": che_do, "soChuyenGia": len(ra), "chuyenGia": ra[:8],
        "ghiChu": (f"Chỉ tính trader có ≥{toi_thieu} vòng ở chế độ này. Điểm tổng cao "
                   f"mà chưa từng giao dịch ở đây thì không có tên — giỏi ở chỗ khác "
                   f"không phải giỏi ở đây."),
    }
