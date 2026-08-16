"""Chạy phễu quan sát trader ở luồng nền, lưu hồ sơ ra đĩa.

Phễu, đúng như tài liệu thiết kế mô tả — và lý do nó phải là phễu rất cụ thể:
leaderboard có **41.794 trader**, mà mỗi hồ sơ sâu tốn 2 lời gọi API. Lấy hết
là 83.588 lời gọi và vài giờ. Nên:

    41.794 trader          leaderboard, một lời gọi ~34 MB
        ↓ lọc vốn ≥ 50k, có volume
    vài nghìn
        ↓ lấy mẫu BA nhóm: đỉnh · giữa · ĐANG LỖ
    ~36 trader
        ↓ lấy đường vốn + lệnh khớp  (2 lời gọi mỗi người)
    hồ sơ đầy đủ + điểm chất lượng

Nhóm "đang lỗ" không phải để cho vui: nó là thứ chặn thiên lệch kẻ sống sót.
Nếu hồ sơ người thua trông giống hệt hồ sơ người thắng ở mọi chỉ số ta đo, thì
điều đó có nghĩa là **ta đang đo sai thứ** — và đó là phát hiện đáng giá hơn
một bảng xếp hạng đẹp.
"""
from __future__ import annotations

import threading
import time
from typing import Any

import httpx

from . import (che_do_da_coin as CD, dai_quan_sat as DQ, dong_thuan as DT,
               giai_phau as GP, nguon, store, trader_thanh_ky_nang as TK)
from .bus import bus

KHO = "trader-ho-so.json"

_trang_thai: dict[str, Any] = {"trangThai": "chưa chạy", "phanTram": 0, "viec": None,
                               "batDau": None, "xong": None, "loi": None}
_luong: threading.Thread | None = None


def trang_thai() -> dict:
    return {**_trang_thai, "kho": tom_tat()}


def tom_tat() -> dict:
    d = store.read_json(KHO, None)
    if not d:
        return {"co": False}
    hs = d.get("traders") or []
    theo_hang: dict[str, int] = {}
    for t in hs:
        theo_hang[t["diem"]["hang"]] = theo_hang.get(t["diem"]["hang"], 0) + 1
    return {
        "co": True, "luc": d.get("luc"), "soTrader": len(hs),
        "tongLeaderboard": d.get("tongLeaderboard"),
        "theoHang": theo_hang,
        "soNghiNgoAnMay": sum(1 for t in hs if t["anMay"]["nghiNgo"]),
        "theoNhom": {n: sum(1 for t in hs if t["nhom"] == n)
                     for n in ("dinh", "giua", "dangLo", "daChay")},
        "dongThuan": (d.get("dongThuan") or {}).get("phanQuyet"),
        "soViTheMo": (d.get("dongThuan") or {}).get("soViThe"),
    }


def ho_so_day_du() -> dict:
    return store.read_json(KHO, {"traders": []})


def _chay(moi_nhom: int) -> None:
    try:
        _trang_thai.update(trangThai="đang chạy", batDau=time.time(), loi=None, phanTram=1,
                           viec="tải leaderboard Hyperliquid (~34 MB)")
        with httpx.Client(follow_redirects=True) as c:
            lb = DQ.leaderboard(c)
            _trang_thai.update(phanTram=15, viec=f"lọc và lấy mẫu từ {len(lb):,} trader")
            mau = DQ.lay_mau(lb, moi_nhom)

            # BỐN nhóm — thêm "daChay" (ví đã cháy). Tài liệu nêu bốn nhóm;
            # bản đầu tôi chỉ làm ba, và nhóm thiếu chính là nhóm dạy được
            # người ta chết vì cái gì.
            can = [(n, t) for n in ("dinh", "giua", "dangLo", "daChay")
                   for t in mau.get(n, [])]
            ra: list[dict] = []
            for i, (nhom, t) in enumerate(can):
                _trang_thai.update(
                    phanTram=15 + round((i / max(1, len(can))) * 80),
                    viec=f"hồ sơ {i + 1}/{len(can)} · {nhom} · {t['diaChi'][:10]}…")
                ct: dict[str, Any] = {}
                try:
                    dv = DQ.duong_von(c, t["diaChi"])
                    lich = (dv.get("allTime") or {}).get("accountValueHistory") or []
                    ct["sutGiamPct"] = DQ.sut_giam(lich)
                    if len(lich) >= 2:
                        ct["soNgay"] = round((lich[-1][0] - lich[0][0]) / 86_400_000, 1)
                    fills = DQ.lenh_khop(c, t["diaChi"])
                    hs = DQ.ho_so(fills)
                    ct["soLenh"] = hs.get("soLenh")
                    ct["soLanThanhLy"] = hs.get("soLanThanhLy")
                    ct["kyLuat"] = DQ.ky_luat(hs)

                    # Dựng chuỗi chế độ cho những coin trader này thật sự đánh.
                    # Chỉ vài coin đầu: dựng chuỗi tốn ~10 giây/coin, mà đuôi
                    # dài thường là những coin họ đánh đúng một lần.
                    #
                    # Cửa sổ BÁM THEO DỮ LIỆU của chính trader đó, không để cố
                    # định. Lần đầu tôi để cứng 30 ngày và 10/12 trader ra "0
                    # vòng có chế độ" — lệnh của họ cũ hơn thế. Cửa sổ cố định
                    # nghĩa là ai giao dịch thưa thì vô hình, và bảng xếp hạng
                    # lại nghiêng về người khớp với lựa chọn kỹ thuật của mình.
                    # Cửa sổ tính từ VÒNG cũ nhất, không phải LỆNH KHỚP cũ nhất.
                    #
                    # Đo được: nhiều trader có `doPhu` coin 100% mà `soCoCheDo`
                    # vẫn 0 — chuỗi có đủ coin, nhưng mốc thời gian của vòng nằm
                    # ngoài cửa sổ. Lệnh khớp cũ nhất và vòng ĐÓNG TRỌN cũ nhất
                    # là hai mốc khác nhau, và mốc cần là mốc thứ hai.
                    vong_thu = GP._ghep(fills)
                    cu = min((v["moLuc"] for v in vong_thu), default=None) or hs.get("tuLuc")
                    ngay = 30
                    if cu:
                        # Trần 150 ngày. Nhờ lấy chế độ mỗi 3 nến nên 150 ngày
                        # ≈ 1.200 lát mỗi coin, vẫn chạy được; để thấp hơn thì
                        # trader giao dịch thưa bị vô hình, và đó là kiểu mất
                        # dữ liệu do lựa chọn kỹ thuật của mình chứ không phải
                        # do dữ liệu thiếu.
                        ngay = min(150, max(30, int((time.time() * 1000 - cu) / 86_400_000) + 3))
                    # Dựng chuỗi cho coin CÓ VÒNG ĐÓNG TRỌN, không phải coin
                    # nhiều lệnh nhất.
                    #
                    # Lỗi bản đầu: chọn theo số lệnh khớp. Một trader có 1.282
                    # lệnh HYPE nhưng đó là một vị thế lớn mở/đóng từng phần và
                    # chưa đóng hẳn, còn 14 vòng hoàn chỉnh của anh ta lại nằm
                    # ở những coin khác. Kết quả: dựng chuỗi cho đúng coin
                    # không dùng được, và `soCoCheDo` ra 0 — trông y như dữ
                    # liệu hỏng chứ không như một lựa chọn sai của mình.
                    dem_coin: dict[str, int] = {}
                    for v in vong_thu:
                        dem_coin[v["coin"]] = dem_coin.get(v["coin"], 0) + 1

                    # Dựng cho tới khi PHỦ ĐỦ, không phải "5 coin đầu".
                    #
                    # Đo được: vòng của một trader rải rất mỏng — 16 vòng trên 6
                    # coin, coin nhiều nhất chỉ 4 vòng. Lấy cứng 5 coin thì ai
                    # rải trên 20 coin sẽ mất gần hết. Trần 12 coin để một trader
                    # rải cực mỏng không nuốt hết thời gian của cả mẻ.
                    tong_vong = len(vong_thu) or 1
                    phu_coin = 0
                    for coin in sorted(dem_coin, key=lambda k: -dem_coin[k])[:12]:
                        if CD.dung_chuoi(c, coin, ngay):
                            phu_coin += dem_coin[coin]
                        if phu_coin / tong_vong >= 0.9:
                            break
                    gp = GP.giai_phau(fills)

                    # HAI con số phủ, và cái thứ hai mới là cái thật.
                    #
                    # Bản trước tôi chỉ báo "phủ coin" rồi gọi nó là phủ chế độ:
                    # nó hiện 100% trong khi số vòng tra được chế độ là 0. Một
                    # con số đúng về mặt định nghĩa mà sai về mặt nghĩa — đúng
                    # loại nói dối mà cả hệ thống này được dựng để chặn.
                    co_cd = sum(1 for v in (gp.get("_vong") or []) if v.get("cheDoVao"))
                    gp["doPhuCoin"] = round(phu_coin / tong_vong * 100, 1)
                    gp["doPhuCheDo"] = round(co_cd / tong_vong * 100, 1)
                    ct["doPhuCheDo"] = gp["doPhuCheDo"]
                    ct["daDangCheDo"] = (gp.get("daDangCheDo") or {}).get("diem")
                    vi_the = DQ.hl_vi_the(c, t["diaChi"])
                except Exception as e:  # noqa: BLE001 — một trader hỏng không được kéo cả mẻ
                    hs = {"soLenh": 0, "loi": f"{type(e).__name__}"}
                    gp = {"soVong": 0, "loi": f"{type(e).__name__}"}
                    vi_the = []
                ra.append({
                    **t, "nhom": nhom, "hoSo": hs, "giaiPhau": gp,
                    "viThe": vi_the,
                    "diem": DQ.cham_diem(t, ct),
                    "anMay": DQ.an_may(hs),
                })
                time.sleep(0.25)   # đừng nện API công khai của người ta

            _trang_thai.update(phanTram=92, viec="lấy lead trader OKX (nhiều trang)")
            try:
                okx = DQ.okx_lead(c, so_trang=8)
                # Vị thế đang mở của vài lead trader đầu — nguồn THỨ HAI cho
                # Elite Positioning, để chỉ số không chỉ dựa vào một sàn.
                for x in okx[:10]:
                    try:
                        x["viThe"] = DQ.okx_vi_the(c, x["diaChi"])
                    except Exception:  # noqa: BLE001
                        x["viThe"] = []
                    time.sleep(0.2)
            except Exception:  # noqa: BLE001
                okx = []

            _trang_thai.update(phanTram=96, viec="đồng thuận + chen chúc")
            ps = (nguon.kho() or {}).get("phaiSinh")
            cs = DT.chi_so(ra + okx, "BTC")
            dong_thuan = {**cs, "phanQuyet": DT.phan_quyet(cs, ps)}
            chuyen_gia = {cd: DT.chuyen_gia_cho_che_do(ra, cd)
                          for cd in ("TREND_UP", "TREND_DOWN", "RANGE", "BREAKOUT")}
            cheo = GP.ma_tran_cheo(ra)

        ra.sort(key=lambda x: -x["diem"]["diem"])
        TK.viet_tat_ca(ra)
        # `_vong` nặng và chỉ dùng để dựng ma trận chéo — bỏ trước khi ghi
        # đĩa, nếu không file hồ sơ phình lên hàng chục MB.
        for t in ra:
            (t.get("giaiPhau") or {}).pop("_vong", None)
        store.write_json(KHO, {
            "luc": time.time(), "tongLeaderboard": mau["tong"],
            "tongDaChay": mau.get("tongDaChay"),
            "traders": ra, "okx": okx,
            "dongThuan": dong_thuan, "chuyenGiaTheoCheDo": chuyen_gia,
            "maTranCheo": cheo,
        })
        _trang_thai.update(trangThai="xong", phanTram=100, xong=time.time(),
                           viec=f"{len(ra)} hồ sơ · {len(okx)} lead trader OKX")
        bus.emit("hoc", "quan-sat-xong",
                 f"dựng {len(ra)} hồ sơ trader từ {mau['tong']:,} ứng viên")
    except Exception as e:  # noqa: BLE001
        _trang_thai.update(trangThai="lỗi", loi=f"{type(e).__name__}: {e}", xong=time.time())
        bus.log("hoc", "quan-sat-loi", f"phễu quan sát hỏng: {e}")


def bat_dau(moi_nhom: int = 12) -> dict:
    global _luong
    if _trang_thai["trangThai"] == "đang chạy":
        return {"ok": False, "vi_sao": "đang chạy"}
    _luong = threading.Thread(target=_chay, args=(moi_nhom,),
                              name="quan-sat-trader", daemon=True)
    _luong.start()
    return {"ok": True}
