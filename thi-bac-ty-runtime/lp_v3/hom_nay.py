"""«HÔM NAY NÊN LÀM GÌ» — một trang, đọc trong hai phút, chạy KHÔNG cần mạng.

    python -m lp_v3.hom_nay              in ra màn hình
    python -m lp_v3.hom_nay --json       dạng máy đọc
    python -m lp_v3.hom_nay --luc "2026-09-05 10:00"   đứng ở một giờ khác

Hàm `dung()` là nguồn duy nhất của báo cáo: CLI, vòng ngày và buồng lái
đều gọi nó, nên ba nơi không bao giờ nói ba câu khác nhau về cùng một giờ.

Trang này nói được gì thì nói, và **thiếu gì thì nói thiếu gì** — dòng
«nguồn đang mù» nằm ngay đầu, trước mọi con số, vì một bảng đẹp dựng trên
một nguồn chết là kiểu hỏng cả repo này sinh ra để chặn.
"""
from __future__ import annotations

import datetime as dt
import json
import sys

from . import bang_gia, config as cfgmod, lich
from .kinh_nghiem import nap_bai_hoc
from .quyet_dinh import CHO, GIU, VAO


def dung(ty, now: dt.datetime | None = None, coHoi: list | None = None) -> dict:
    """Báo cáo có cấu trúc. `ty` là `TyBienDo`; `coHoi` để tái dùng lượt
    quét vừa có thay vì cân lại."""
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(lich.VN)
    co = coHoi if coHoi is not None else ty.can_tat_ca(now)
    cfg = ty.cfg
    bc = lich.boi_canh(now, ketQuaKinhDoanh=cfg.get("ketQuaKinhDoanh") or {},
                       hetThuong=_het_thuong(cfg))
    mu = []
    for ten, ng, tien in (("giá gốc Yahoo", ty.nguonGoc, "goc:"),
                          ("RPC X Layer", ty.nguonRpc, "rpc:"),
                          ("tin RSS", ty.nguonTin, "tin:")):
        sk = ng.suc_khoe
        if sk.tongLuot and not sk.songSot:
            mu.append(f"{ten}: {sk.soLoi}/{sk.tongLuot} lượt lỗi — {sk.loiCuoi}")
        elif not sk.tongLuot:
            # Nhịp làm mới ghi trên ĐĨA (`lam-moi.json`) nên tiến trình
            # khác — runtime nền — có thể vừa hỏi xong; tiến trình này
            # thấy đủ nhịp mà không hỏi. Nói đúng câu ấy, đừng nói «mù».
            gan = max((float(v) for k, v in (ty.lanMoi or {}).items()
                       if k.startswith(tien)), default=0.0)
            if gan:
                mu.append(f"{ten}: tiến trình này chưa hỏi; tiến trình khác hỏi "
                          f"lần cuối {dt.datetime.fromtimestamp(gan, lich.VN).strftime('%H:%M %d/%m')}")
            else:
                mu.append(f"{ten}: chưa hỏi lần nào (chạy `python run.py` hoặc "
                          f"`python -m lp_v3.hom_nay --moi`)")
    thieuDiaChi = [p["kyHieu"] for p in cfg.get("pool") or [] if not p.get("diaChi")]
    thieuVol = [p["kyHieu"] for p in cfg.get("pool") or []
                if p.get("khoiLuongNgayUsd") is None]

    hanhDong = {}
    for c in co:
        hanhDong.setdefault(c.quyetDinh.hanhDong, []).append(c.kyHieu)
    viThe = []
    for c in co:
        for v in c.viThe:
            viThe.append({"kyHieu": c.kyHieu, **v.tom_tat()})

    thuong = _thuong(cfg, now, co)
    pools = [_mot_pool(c) for c in co]
    viTheDs = []
    for c in co:
        for v in c.viThe:
            viTheDs.append({"kyHieu": c.kyHieu, **v.tom_tat()})
    return {
        "hanhDongNgay": _hanh_dong_ngay(co, pools, bc, thuong),
        "vonLp": _von_lp(viTheDs, cfg, ty),
        "mucTieu": cfg.get("mucTieu") or {},
        "cheDoRuiRo": _che_do_rui_ro(bc, thuong),
        "tinAnhHuong": _tin_anh_huong(co),
        "luc": now.isoformat(), "lucVn": now.strftime("%H:%M %d/%m/%Y"),
        "phien": bc.tom_tat(),
        "thuong": thuong,
        "cheDo": _che_do(thuong, bc),
        "thiTruongGoc": _thi_truong_goc(bc),
        "vongNgay": _vong_ngay(ty, now),
        "vi": ty.vi_tom_tat() if hasattr(ty, "vi_tom_tat") else None,
        "triThuc": ty.tri_thuc_tom_tat() if hasattr(ty, "tri_thuc_tom_tat") else None,
        "nhip": _nhip(cfg),
        "nguonMu": mu, "thieuDiaChi": thieuDiaChi, "thieuKhoiLuong": thieuVol,
        "giaDinh": [
            f"phần thưởng trong APY hiển thị = {cfg.get('giaDinhPhanThuong'):.0%} "
            f"(GIẢ ĐỊNH; khai `khoiLuongNgayUsd` để tách thật)",
            "pool tập trung NHƯ TA: phí vị thế = APR pool, không nhân hiệu "
            "suất (thận trọng; dán địa chỉ pool để đọc L thật)",
            "P(văng) là CẬN TRÊN; τ đếm theo ngày giao dịch Mỹ, phần trôi "
            "ngoài giờ trên chuỗi CHƯA đo",
        ],
        "tomTatHanhDong": {k: v for k, v in hanhDong.items()},
        "pool": pools,
        "viThe": viTheDs,
        "baiHoc": _bai_hoc_gon(nap_bai_hoc()),
        "kinhNghiem": ty.soKinhNghiem.tom_tat(),
        "tienHoa": _tien_hoa_gon(),
        "nut": cfg.get("nut"),
    }


#: Dưới ngần này độ tin cậy dữ liệu thì KHOÁ nút vào, dù mọi số khác đẹp.
TIN_CAY_KHOA = 0.60

NHAN_LUAT = {
    "khong-sigma": "chưa đo được σ", "gia-cu": "giá đã cũ",
    "sat-su-kien": "sát sự kiện", "gap-mo-cua": "giá chuỗi lệch giá gốc",
    "ngoai-gio-khong-doi-dai": "sàn cổ phiếu Mỹ đóng", "tvl-mong": "TVL mỏng",
    "phi-duoi-lvr": "phí không trả nổi LVR", "sap-het-thuong": "thưởng sắp kết thúc",
    "van-dai-cao": "xác suất văng dải cao", "dai-qua-rong": "dải quá rộng",
    "vao-duoc": "đủ điều kiện", "giu": "đang giữ", "ngoai-dai": "giá ra ngoài dải",
    "chua-du-so": "chưa đủ số",
}


def _hanh_dong_ngay(co, pools, bc, thuong) -> dict:
    """MỘT quyết định cấp hệ, ba lý do đứng đầu, và điều kiện để nó đổi.

    Thứ tự: đang giữ mà có pool đòi RÚT/ĐỔI/NỚI → đó là việc gấp nhất;
    có pool VÀO được → VÀO; còn lại → CHỜ. Lý do gom theo LUẬT CHẶN đứng
    đầu ở nhiều pool nhất — người đọc thấy «vì sao cả bảng đỏ» trong một
    dòng, không phải chín dòng.
    """
    from .quyet_dinh import CHO, GIU, VAO
    gap = [(c.kyHieu, v.quyetDinh["hanhDong"], v.quyetDinh["lyDo"])
           for c in co for v in c.viThe
           if v.quyetDinh.get("hanhDong") not in (GIU, CHO)]
    vao = [p for p in pools if p["hanhDong"] == VAO and not p.get("khoaVao")]
    dem = {}
    for c in co:
        if c.quyetDinh.hanhDong == VAO:
            continue
        m = c.quyetDinh.luatQuyet
        dem[m] = dem.get(m, 0) + 1
    lyDo = [{"luat": m, "cau": NHAN_LUAT.get(m, m), "soPool": n}
            for m, n in sorted(dem.items(), key=lambda kv: -kv[1])[:3]]
    if gap:
        hd, cau = gap[0][1], f"{gap[0][0]}: {gap[0][2]}"
        tieu = f"{len(gap)} vị thế cần động tay"
    elif vao:
        hd, tieu = VAO, f"{len(vao)} pool đủ điều kiện"
        cau = "Vào cỡ THỬ ở " + ", ".join(p["kyHieu"] for p in vao[:3]) + "; giữ, không đổi dải trong chương trình thưởng."
    else:
        hd, tieu, cau = CHO, "Không mở vị thế LP mới", (
            "Chờ — " + "; ".join(x["cau"] for x in lyDo) if lyDo else "Chờ dữ liệu.")

    # điều kiện mở khoá CHỜ → VÀO, mỗi điều một phép đo
    moCua = bc.trangThai == lich.MO_CUA
    lech = [c.gia.get("giaChuoi") / c.gia.get("giaGoc") - 1.0 for c in co
            if c.gia.get("giaChuoi") and c.gia.get("giaGoc")]
    lechOk = None if not lech else all(abs(x) < 0.015 for x in lech)
    nguong = float((co[0].pool.get("nutTiLe") if co else None) or 1.5)
    phiOk = any((p.get("dai") or {}).get("tiLePhiTrenLvr") is not None
                and p["dai"]["tiLePhiTrenLvr"] >= nguong for p in pools)
    conGio = thuong.get("conGio")
    thuongOk = True if conGio is None else conGio > 24.0
    duLieuOk = any((p.get("tinCay") or 0) >= TIN_CAY_KHOA for p in pools)
    sk = [s for s in bc.su_kien_trong(24.0) if s.loai in ("fomc", "ket-qua-kinh-doanh")]
    suKienOk = not sk
    dieuKien = [
        {"ten": "Sàn cổ phiếu Mỹ mở", "dat": moCua,
         "ghi": "" if moCua else (f"mở sau {bc.gioToiMo:.1f} giờ" if bc.gioToiMo is not None else "")},
        {"ten": "Giá chuỗi lệch giá gốc < 1,5%", "dat": lechOk,
         "ghi": "chưa đo — cần địa chỉ pool" if lechOk is None else ""},
        {"ten": "Phí/LVR đạt ngưỡng ở ít nhất một pool", "dat": phiOk, "ghi": ""},
        {"ten": "Thưởng còn > 24 giờ hoặc không cần thưởng", "dat": thuongOk,
         "ghi": "" if thuongOk else f"còn {conGio:.0f} giờ"},
        {"ten": f"Độ tin cậy dữ liệu ≥ {TIN_CAY_KHOA:.0%} ở ít nhất một pool", "dat": duLieuOk, "ghi": ""},
        {"ten": "Không sự kiện FOMC / kết quả kinh doanh trong 24 giờ", "dat": suKienOk,
         "ghi": "" if suKienOk else sk[0].ten},
    ]
    return {"hanhDong": hd, "tieuDe": tieu, "cau": cau, "lyDo": lyDo,
            "dieuKien": dieuKien, "soDat": sum(1 for d in dieuKien if d["dat"]),
            "soDieuKien": len(dieuKien), "viTheGap": gap[:5]}


def _von_lp(viThe: list, cfg: dict | None = None, ty=None) -> dict:
    """Bảng KPI vốn (Bài 2): NAV LP, phí chưa thu, IL, PnL ước, hiệu quả vốn
    theo vị thế, dòng tiền ròng quy tháng và ĐIỂM TỰ DO = dòng tiền / chi
    phí sống. Không có vị thế hay chưa khai chi phí thì None — không 0."""
    von = sum(float((v.get("viThe") or {}).get("vonUsd") or 0.0) for v in viThe)
    phi = [((v.get("viThe") or {}).get("phiChoThuUsd")) for v in viThe]
    il = []
    for v in viThe:
        tt = v.get("trangThai") or {}
        vt = v.get("viThe") or {}
        if tt.get("ilPct") is not None and vt.get("vonUsd"):
            il.append(tt["ilPct"] / 100.0 * float(vt["vonUsd"]))
    coPhi = [x for x in phi if x is not None]
    hq = [{"kyHieu": v.get("kyHieu"), "tokenId": (v.get("viThe") or {}).get("tokenId"),
           "hieuQuaVonThangPct": (v.get("trangThai") or {}).get("hieuQuaVonThangPct"),
           "vonUsd": (v.get("viThe") or {}).get("vonUsd")}
          for v in viThe if (v.get("trangThai") or {}).get("hieuQuaVonThangPct") is not None]
    hq.sort(key=lambda x: -(x["hieuQuaVonThangPct"] or 0))
    # dòng tiền ròng quy THÁNG: từng vị thế (phí + IL) / giờ giữ × 720
    dong = []
    for v in viThe:
        vt, tt = v.get("viThe") or {}, v.get("trangThai") or {}
        g = tt.get("gioGiu")
        if vt.get("phiChoThuUsd") is None or not g or g <= 1.0:
            continue
        ilv = (tt["ilPct"] / 100.0 * float(vt["vonUsd"])) if (tt.get("ilPct") is not None and vt.get("vonUsd")) else 0.0
        dong.append((vt["phiChoThuUsd"] + ilv) * 720.0 / g)
    dongUoc = sum(dong) if dong else None
    # ĐÃ VỀ TAY (Bài 2: investment income ≠ cash flow): chỉ phí + thưởng
    # người đã ghi khi ĐÓNG vị thế trong 30 ngày qua. Điểm tự do tính trên
    # số này, KHÔNG trên phí chưa thu — phí chưa thu là lãi trên giấy.
    daVeTay = None
    if ty is not None and hasattr(ty, "soViThe"):
        han = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
        tong, co = 0.0, False
        for v in ty.soViThe.da_dong():
            try:
                t = dt.datetime.fromisoformat(str(v.dongLuc).replace("Z", "+00:00"))
            except ValueError:
                continue
            if t < han:
                continue
            if v.phiThuUsd is not None or v.thuongThuUsd is not None:
                co = True
                tong += float(v.phiThuUsd or 0.0) + float(v.thuongThuUsd or 0.0)
        daVeTay = tong if co else None
    chiPhi = ((cfg or {}).get("mucTieu") or {}).get("chiPhiThangUsd")
    tuDo = None
    if daVeTay is not None and chiPhi:
        tuDo = daVeTay / float(chiPhi)
    return {"soViThe": len(viThe), "vonUsd": von,
            "phiChoThuUsd": sum(coPhi) if coPhi else None,
            "ilUsd": sum(il) if il else None,
            "pnlUocUsd": (sum(coPhi) + sum(il)) if (coPhi or il) else None,
            "trongDai": sum(1 for v in viThe if (v.get("trangThai") or {}).get("trongDai")),
            "hieuQuaVon": hq,
            "dongTienUocThangUsd": dongUoc,
            "dongTienDaVeTayThangUsd": daVeTay,
            "chiPhiThangUsd": chiPhi,
            "diemTuDo": tuDo}


def _che_do_rui_ro(bc, thuong) -> dict:
    con = thuong.get("conGio")
    ly = []
    if bc.trangThai != lich.MO_CUA:
        ly.append("sàn gốc đóng")
    if con is not None and 0 < con <= 24:
        ly.append("thưởng còn dưới 24 giờ")
    if bc.su_kien_trong(24.0):
        ly.append("có sự kiện trong 24 giờ")
    if not bc.lichConHan:
        ly.append("lịch nghỉ chưa phủ năm nay")
    return {"ma": "THAN_TRONG" if ly else "BINH_THUONG",
            "ten": "THẬN TRỌNG" if ly else "BÌNH THƯỜNG", "lyDo": ly}


def _tin_anh_huong(co) -> list:
    """Tin gắn với pool chịu ảnh hưởng, kèm mức tác động từ CỜ — không đọc
    hiểu tin, chỉ nói tin này chạm mã nào."""
    from .tin_tuc import CO_NANG
    ra, thay = [], set()
    for c in co:
        for t in c.tin or []:
            lk = t.get("lienKet") or t.get("tieuDe")
            if lk in thay:
                continue
            thay.add(lk)
            cờ = t.get("co") or []
            muc = "CAO" if any(x in CO_NANG for x in cờ) else ("TRUNG BÌNH" if cờ else "THẤP")
            ra.append({"luc": t.get("luc"), "tieuDe": t.get("tieuDe"), "pool": c.kyHieu,
                       "co": cờ, "tacDong": muc})
    ra.sort(key=lambda x: (x["tacDong"] != "CAO", x["tacDong"] != "TRUNG BÌNH", str(x.get("luc"))), reverse=False)
    return ra[:12]


def _diem_co_hoi(c, tinCay: float, ruiRo) -> float | None:
    """Điểm 0–100 để XẾP HẠNG radar — không phải dự báo lợi nhuận.

    Bốn phần: phí/LVR (35), độ tin cậy dữ liệu (25), 1 − rủi ro (25), NET
    kỳ vọng (15). Không có dải thì chỉ còn phần tin cậy và rủi ro — pool
    chưa đo đứng cuối bảng theo cấu tạo, đúng ý «không xếp SPCXx cùng
    hạng với pool đủ số».
    """
    kd = c.dai
    rr = 1.0 - (ruiRo if ruiRo is not None else 0.6)
    if kd is None or kd.tiLePhiTrenLvr is None or kd.netBps is None:
        return round(100.0 * (0.25 * tinCay + 0.25 * rr) * 0.6, 1)
    phi = min(1.0, max(0.0, kd.tiLePhiTrenLvr / 3.0))
    net = min(1.0, max(0.0, kd.netBps / 300.0))
    return round(100.0 * (0.35 * phi + 0.25 * tinCay + 0.25 * rr + 0.15 * net), 1)


def _che_do(thuong: dict, bc) -> dict:
    """Chế độ vận hành — MỘT chữ nói cả cách máy đang nghĩ.

    CAMPAIGN_HUNTER khi chương trình thưởng còn chạy: không đuổi APY, thu
    dữ liệu từng giờ, vào cỡ thử, hạn chế đổi dải (luật chụp ngẫu nhiên của
    OKX), rút hoặc cân lại đúng giờ hết. BINH_THUONG khi không có thưởng:
    xếp hạng bằng phí gốc so LVR, không hơn không kém.
    """
    con = thuong.get("conGio")
    if con is not None and con > 0:
        return {"ma": "CAMPAIGN_HUNTER", "ten": "Săn chương trình thưởng",
                "loiKhuyen": (
                    f"Thưởng còn {con:.0f} giờ. Không đuổi APY hiển thị; thu số "
                    f"từng giờ, chỉ vào cỡ THỬ ở pool có phí/LVR đủ, hạn chế đổi "
                    f"dải vì OKX chụp ngẫu nhiên — đổi lúc chụp là mất thưởng giờ "
                    f"ấy. Tới giờ hết: thu phí, rồi cân lại bằng phí gốc.")}
    return {"ma": "BINH_THUONG", "ten": "Bình thường",
            "loiKhuyen": "Không có thưởng: xếp hạng bằng phí gốc so với LVR; "
                         "APY hiển thị cũ là số của một thế giới đã qua."}


def _thi_truong_goc(bc) -> dict:
    """Thị trường GỐC (sàn Mỹ) mở hay đóng, trong khi token chạy 24/7.

    Đóng → giá chuỗi không có neo, khám phá giá dồn vào cú mở cửa: rủi ro
    khoảng trống ↑, tin cậy dải ↓, không đổi dải. Đây là lý do máy không
    dùng cùng một dải bất kể Nasdaq đang mở hay đóng.
    """
    tt = bc.trangThai
    if tt == lich.MO_CUA:
        return {"trangThai": "MO", "cau": "Sàn Mỹ ĐANG MỞ — giá token có neo, "
                "đây là lúc duy nhất dải đề xuất đáng tin", "ruiRo": []}
    if tt == lich.TRUOC_MO:
        return {"trangThai": "SAP_MO",
                "cau": f"Sàn Mỹ mở sau {bc.gioToiMo:.1f} giờ — cú «bắt kịp» lúc "
                       f"mở là lúc arbitrageur ăn LP; chờ 30 phút sau mở",
                "ruiRo": ["khoang-trong-mo-cua", "lvr-don-mot-khoanh-khac"]}
    ke = (f"mở lại sau {bc.gioToiMo:.0f} giờ" if bc.gioToiMo is not None
          else "chưa có phiên kế")
    return {"trangThai": "DONG",
            "cau": f"Sàn Mỹ ĐÓNG ({ke}) trong khi token giao dịch 24/7 → giá chuỗi "
                   f"không neo, rủi ro khoảng trống ↑, tin cậy dải ↓ — KHÔNG vào mới, "
                   f"KHÔNG đổi dải",
            "ruiRo": ["gia-chuoi-khong-neo", "khoang-trong-mo-cua",
                      "tin-cay-dai-thap", "lech-oracle-dex"]}


def _vong_ngay(ty, now) -> dict | None:
    vn = getattr(ty, "vongNgay", None)
    if vn is None:
        return None
    from .ngay import MOC, gio_moc
    ke = []
    for moc in MOC:
        for lui in range(0, 7):      # qua cả cuối tuần dài + ngày nghỉ
            g = gio_moc(moc, now.date() + dt.timedelta(days=lui))
            if g is not None and g > now:
                ke.append({"moc": moc, "luc": g.isoformat(),
                           "conGio": (g - now).total_seconds() / 3600.0})
                break
    return {"daChay": dict(vn.daChay), "lanCuoi": dict(vn.lanCuoi), "mocKe": ke}


def _nhip(cfg) -> list:
    """Một ngày của ty — nhịp nào làm việc gì, đọc từ hằng số thật."""
    from .ty_bien_do import (NHIP_GIA_GOC_GIAY, NHIP_GIA_GOC_TRONG_PHIEN_GIAY,
                             NHIP_TIN_GIAY)
    return [
        {"nhip": f"mỗi {int(cfg.get('nhipGiay') or 300) // 60} phút",
         "viec": "cân lại mọi pool · giá pool qua RPC (khi có địa chỉ) · ghi quyết định"},
        {"nhip": f"mỗi {int(NHIP_GIA_GOC_TRONG_PHIEN_GIAY // 60)} phút trong phiên Mỹ, "
                 f"{int(NHIP_GIA_GOC_GIAY // 3600)} giờ ngoài phiên",
         "viec": "giá cổ phiếu gốc + giá đang giao dịch (Yahoo)"},
        {"nhip": f"mỗi {int(NHIP_TIN_GIAY // 3600)} giờ", "viec": "tin RSS theo mã, gắn cờ"},
        {"nhip": "07:00 VN", "viec": "bản tin sáng"},
        {"nhip": "60 phút trước sàn Mỹ mở", "viec": "soát lại trước cú bắt kịp"},
        {"nhip": "30 phút sau sàn Mỹ đóng",
         "viec": "CHẤM quyết định hết cửa sổ · gom bài học · một lượt tiến hoá"},
    ]


def _het_thuong(cfg):
    ct = cfg.get("chuongTrinh") or {}
    try:
        return lich.doc_gio_vn(ct["ketThuc"]) if ct.get("ketThuc") else None
    except ValueError:
        return None


def _thuong(cfg, now, co) -> dict:
    ct = cfg.get("chuongTrinh") or {}
    het = _het_thuong(cfg)
    ra = {"ten": ct.get("ten"), "ketThuc": ct.get("ketThuc"),
          "conGio": None if het is None else max(0.0, (het - now).total_seconds() / 3600.0),
          "luat": ct.get("luat")}
    # Kiểm chéo quỹ thưởng với APY hiển thị: tổng thưởng/giờ suy từ APY × TVL
    # của các pool đang theo, so với quỹ/giờ. Lệch xa là một trong hai số
    # không mô tả cái ta tưởng.
    quy = float(ct.get("quyUsd") or 0.0)
    try:
        bd = lich.doc_gio_vn(ct["batDau"]) if ct.get("batDau") else None
    except ValueError:
        bd = None
    if quy and bd and het:
        gio = (het - bd).total_seconds() / 3600.0
        ra["quyMoiGioUsd"] = quy / gio if gio > 0 else None
        tong = 0.0
        for c in co:
            tvl = c.pool.get("tvlUsd") or 0.0
            if c.aprThuong:
                tong += tvl * c.aprThuong / (365.0 * 24.0)
        ra["thuongMoiGioSuyTuApyUsd"] = tong
        if ra["quyMoiGioUsd"]:
            ra["kiemCheo"] = (
                f"APY hiển thị của {len(co)} pool đang theo suy ra "
                f"${tong:,.0f}/giờ thưởng, quỹ là ${ra['quyMoiGioUsd']:,.0f}/giờ "
                f"→ {tong / ra['quyMoiGioUsd']:.0%} quỹ nằm ở các pool này "
                f"(phần còn lại ở pool khác, hoặc APY hiển thị KHÔNG phải "
                f"toàn thưởng)")
    return ra


def _tom_tat_pool(c) -> str:
    """Một câu người đọc được, thay cho bảng số — đúng thứ người vận hành
    muốn thấy đầu tiên ở mỗi hồ sơ."""
    kd, q = c.dai, c.quyetDinh
    apy = c.pool.get("apyHienThiPhanTram")
    if q.hanhDong == "VAO" and kd:
        from .ty_bien_do import _tin_cay
        if _tin_cay(c) < TIN_CAY_KHOA:
            return (f"Đủ luật để VÀO nhưng độ tin cậy dữ liệu {_tin_cay(c):.0%} < "
                    f"{TIN_CAY_KHOA:.0%} — KHOÁ nút vào; khai khối lượng/địa chỉ pool để mở.")
        return (f"CÓ THỂ VÀO ${c.vonXinUsd:,.0f} ở dải {kd.Pa:.2f}–{kd.Pb:.2f} "
                f"(±{kd.rong:.1%}): phí/LVR {kd.tiLePhiTrenLvr:.2f}, P(văng) ≤ "
                f"{kd.xacSuatVang['tong']:.0%}, NET kỳ vọng {kd.netBps:+.0f} bps trong "
                f"{c.pool.get('giuGio', 72):.0f} giờ.")
    dau = (f"Thấy APY {apy:.0f}% nhưng " if apy is not None else "")
    if q.hanhDong in ("GIU",):
        return dau + f"đang giữ: {q.lyDo}"
    if q.hanhDong in ("RUT", "NOI_RONG", "THU_HEP", "DOI_DAI"):
        return dau + f"khuyên {q.hanhDong.replace('_', ' ')}: {q.lyDo}"
    them = ""
    if kd and kd.tiLePhiTrenLvr is not None and kd.tiLePhiTrenLvr < 1.5:
        them = (f" Kể cả tính thưởng, phí/LVR chỉ {kd.tiLePhiTrenLvr:.2f} ở dải "
                f"±{kd.rong:.1%} — APY không trả nổi tổn thất so với σ {c.sigma.get('sigma', 0):.0%}.")
    return dau + f"KHÔNG khuyến nghị vào lúc này: {q.lyDo}." + them


def _mot_pool(c) -> dict:
    from .ty_bien_do import _rui_ro, _tin_cay
    kd = c.dai
    apy = c.pool.get("apyHienThiPhanTram")
    rr = _rui_ro(c)
    tinCay = _tin_cay(c) if (c.sigma.get("sigma") is not None and c.gia.get("gia")) else min(
        0.35, _tin_cay(c))
    d = {"kyHieu": c.kyHieu, "hanhDong": c.quyetDinh.hanhDong,
         "tomTat": _tom_tat_pool(c),
         "tinCay": tinCay, "khoaVao": tinCay < TIN_CAY_KHOA,
         "diem": _diem_co_hoi(c, tinCay, rr.cao_nhat()),
         "thieuGi": list(c.thieu),
         "diemRuiRo": rr.cao_nhat(), "ruiRo": rr.tom_tat(),
         "apyTach": {"hienThiPct": apy,
                     "phiPct": None if c.aprPhi is None else c.aprPhi * 100.0,
                     "thuongPct": None if c.aprThuong is None else c.aprThuong * 100.0,
                     "giaDinh": c.nguonApr.startswith("apy-hien-thi"),
                     "nguon": c.nguonApr},
         "thiTruongGoc": ("MO" if c.phien.get("trangThai") == lich.MO_CUA
                          else "SAP_MO" if c.phien.get("trangThai") == lich.TRUOC_MO
                          else "DONG"),
         "coSanGoc": c.sigma.get("nguon") != "chuoi" and c.sigma.get("sigma") is not None
                     or c.gia.get("nguon") in ("goc", "goc-tuc-thoi"),
         "luat": c.quyetDinh.luatQuyet, "lyDo": c.quyetDinh.lyDo,
         "biChan": c.quyetDinh.biChan,
         "gia": c.gia.get("gia"), "nguonGia": c.gia.get("nguon"),
         "tuoiGiaGio": None if c.gia.get("tuoiGiay") is None else c.gia["tuoiGiay"] / 3600.0,
         "sigma": c.sigma.get("sigma"), "soPhien": c.sigma.get("soPhien"),
         "nguonSigma": c.sigma.get("nguon"),
         "tvlUsd": c.pool.get("tvlUsd"), "apyHienThi": c.pool.get("apyHienThiPhanTram"),
         "aprPhi": c.aprPhi, "aprThuong": c.aprThuong, "nguonApr": c.nguonApr,
         "vonXinUsd": c.vonXinUsd, "sucChuaUsd": c.sucChuaUsd,
         "bienDong": c.bienDong, "thieu": list(c.thieu),
         "tin": [{"tieuDe": t.get("tieuDe"), "co": t.get("co"), "luc": t.get("luc")}
                 for t in (c.tin or [])[:3]],
         "luatKhop": [{"ma": a, "hanhDong": b, "lyDo": l}
                      for a, b, l in c.quyetDinh.luatKhop][:5]}
    if kd:
        d["dai"] = {"Pa": kd.Pa, "Pb": kd.Pb, "rongPct": kd.rong * 100.0,
                    "hieuSuat": kd.hieuSuat, "pVang": kd.xacSuatVang["tong"],
                    "ilKyVongBps": kd.ilKyVongBps, "lvrBps": kd.lvrBps,
                    "phiBps": kd.phiBps, "thuongBps": kd.thuongBps,
                    "netBps": kd.netBps, "tiLePhiTrenLvr": kd.tiLePhiTrenLvr,
                    "giuGio": c.pool.get("giuGio"), "ghiChu": list(kd.ghiChu)}
    return d


def _bai_hoc_gon(bh: dict | None) -> dict | None:
    if not bh:
        return None
    du, chua = [], 0
    for c, ds in (bh.get("chieu") or {}).items():
        for d in ds:
            if d.get("duMau"):
                du.append(d["cau"])
            else:
                chua += 1
    return {"luc": bh.get("luc"), "soCap": bh.get("soCap"),
            "duMau": du, "soChuaDuMau": chua,
            "moHinh": {k: v.get("cau") for k, v in (bh.get("moHinh") or {}).items()}}


def _tien_hoa_gon() -> dict | None:
    from .tien_hoa import doc_so
    so = doc_so(n=3)
    if not so:
        return None
    return {"soLuot": len(so), "gan": [x.get("ketLuan") for x in so]}


# ── văn bản ──────────────────────────────────────────────────────────────

def _bps(v):
    return "—" if v is None else f"{v:+,.0f} bps"


def _pct(v, n=1):
    return "—" if v is None else f"{v * 100:.{n}f}%"


def van_ban(bc: dict) -> str:
    o = []
    ph = bc["phien"]
    o.append(f"BỂ THANH KHOẢN — {bc['lucVn']} (giờ VN)")
    o.append("=" * 72)
    o.append(f"Phiên Mỹ: {ph['trangThai']}"
             + (f" · mở sau {ph['gioToiMo']:.1f} giờ" if ph.get("gioToiMo") is not None else "")
             + (f" · đóng sau {ph['gioToiDong']:.1f} giờ" if ph.get("gioToiDong") is not None else "")
             + ("" if ph.get("lichConHan") else "  ⚠ LỊCH NGHỈ CHƯA PHỦ NĂM NAY"))
    th = bc["thuong"]
    if th.get("conGio") is not None:
        o.append(f"Thưởng «{th['ten']}»: còn {th['conGio']:.0f} giờ (hết {th['ketThuc']} VN)")
        if th.get("kiemCheo"):
            o.append("  " + th["kiemCheo"])
    sk = ph.get("suKien") or []
    if sk:
        o.append("Sự kiện 7 ngày tới: " + " · ".join(
            f"{s['ten']} ({s['luc'][5:16].replace('T', ' ')})" for s in sk[:6]))
    if bc["nguonMu"]:
        o.append("")
        o.append("NGUỒN ĐANG MÙ:")
        for m in bc["nguonMu"]:
            o.append("  ✗ " + m)
    if bc["thieuDiaChi"]:
        o.append(f"Chưa dán địa chỉ pool ({len(bc['thieuDiaChi'])}): không đọc được "
                 f"L/giá thật — phần phí là GIẢ ĐỊNH")
    o.append("")
    o.append("GIẢ ĐỊNH ĐANG DÙNG: " + " | ".join(bc["giaDinh"]))
    o.append("")
    o.append("HÀNH ĐỘNG: " + " · ".join(f"{k}: {', '.join(v)}"
                                       for k, v in bc["tomTatHanhDong"].items()))
    o.append("-" * 72)
    for p in bc["pool"]:
        o.append(f"{p['kyHieu']:<12} {p['hanhDong']:<9} [{p['luat']}] {p['lyDo']}")
        gia = "—" if p["gia"] is None else f"{p['gia']:.2f} ({p['nguonGia']}, {p['tuoiGiaGio']:.0f}h)"
        sig = "—" if p["sigma"] is None else f"{p['sigma']:.0%} ({p['soPhien']} phiên, {p['nguonSigma']})"
        o.append(f"    giá {gia} · σ {sig} · TVL ${(p['tvlUsd'] or 0):,.0f} · "
                 f"APY hiện {p['apyHienThi']}% · APR phí {_pct(p['aprPhi'])} + thưởng "
                 f"{_pct(p['aprThuong'])} [{p['nguonApr']}]")
        d = p.get("dai")
        if d:
            o.append(f"    dải [{d['Pa']:.2f} – {d['Pb']:.2f}] ±{d['rongPct']:.1f}% · hiệu suất "
                     f"{d['hieuSuat']:.0f}× · P(văng) ≤ {d['pVang']:.0%} · phí/LVR "
                     f"{d['tiLePhiTrenLvr'] if d['tiLePhiTrenLvr'] is None else round(d['tiLePhiTrenLvr'], 2)}")
            o.append(f"    trong {d['giuGio']:.0f}h trên ${p['vonXinUsd']:,.0f}: phí {_bps(d['phiBps'])} "
                     f"+ thưởng {_bps(d['thuongBps'])} + IL {_bps(d['ilKyVongBps'])} "
                     f"= NET {_bps(d['netBps'])}")
        bd = p.get("bienDong") or {}
        if bd.get("trangThai"):
            o.append(f"    biến động: 1 ngày {bd.get('doi1NgayPct', 0):+.1f}% · 5 ngày "
                     f"{bd.get('doi5NgayPct', 0):+.1f}% · σ10/σ60 = {bd.get('tiLeNoCo', 0):.2f} "
                     f"({ {'NO': 'đang NỞ', 'CO': 'đang CO', 'ON': 'ổn'}[bd['trangThai']] })")
        for t in p.get("tin") or []:
            o.append(f"    tin: {t['tieuDe'][:80]}" + (f"  [{', '.join(t['co'])}]" if t.get("co") else ""))
        if p["nguonGia"] == "goc" and p["hanhDong"] == VAO:
            o.append("    ⚠ giá là giá ĐÓNG CỬA — lúc vào, dịch dải theo giá đang hiện ở OKX")
        elif p["nguonGia"] == "goc-tuc-thoi" and p["hanhDong"] == VAO:
            o.append("    ⚠ giá là giá sàn GỐC đang giao dịch — pool trên chuỗi có thể lệch, "
                     "so với giá OKX trước khi đặt")
    vi = bc.get("vi") or {}
    if vi.get("diaChi"):
        o.append("-" * 72)
        o.append(f"VÍ {vi['diaChi'][:8]}…{vi['diaChi'][-4:]} (chỉ đọc): "
                 + (f"{vi.get('soViThe', 0)} vị thế trên chuỗi · giá trị ${vi.get('giaTriUsd') or 0:,.0f}"
                    + (f" · phí chưa thu ${vi['phiChoThuUsd']:,.2f}" if vi.get("phiChoThuUsd") is not None else "")
                    if not vi.get("loi") else f"✗ {vi['loi']}"))
    if bc["viThe"]:
        o.append("-" * 72)
        o.append("VỊ THẾ ĐANG GIỮ:")
        for v in bc["viThe"]:
            vt, tt, q = v["viThe"], v["trangThai"], v["quyetDinh"]
            o.append(f"  {v['kyHieu']} [{vt['Pa']:.2f}–{vt['Pb']:.2f}] ${vt['vonUsd']:,.0f} · "
                     f"{'TRONG dải' if tt.get('trongDai') else 'NGOÀI dải' if tt.get('trongDai') is False else '?'}"
                     f" · IL {tt.get('ilPct', 0):+.2f}% · giữ {tt.get('gioGiu', 0):.0f}h → "
                     f"{q['hanhDong']} [{q['luatQuyet']}] {q['lyDo']}")
    bh = bc.get("baiHoc")
    o.append("-" * 72)
    if bh:
        o.append(f"BÀI HỌC ({bh['soCap']} cặp quyết định–kết cục, "
                 f"{len(bh['duMau'])} đủ mẫu, {bh['soChuaDuMau']} đang tích):")
        for c in bh["duMau"][:8]:
            o.append("  ★ " + c)
        for k, c in (bh.get("moHinh") or {}).items():
            o.append("  ◦ " + c)
    else:
        kn = bc.get("kinhNghiem") or {}
        o.append(f"BÀI HỌC: chưa có — {kn.get('soQuyetDinh', 0)} quyết định đã ghi, "
                 f"{kn.get('soKetCuc', 0)} đã chấm. Cầu tuyết bắt đầu lăn sau cửa sổ giữ "
                 f"đầu tiên ({(bc.get('nut') or {}).get('giuGio', 72):.0f} giờ).")
    th2 = bc.get("tienHoa")
    if th2:
        o.append("TIẾN HOÁ: " + " | ".join(str(x) for x in th2["gan"]))
    o.append(f"NÚM: {bc.get('nut')}")
    return "\n".join(o)


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    from .ty_bien_do import TyBienDo
    now = None
    if "--luc" in argv:
        now = lich.doc_gio_vn(argv[argv.index("--luc") + 1])
    ty = TyBienDo(khongMang="--moi" not in argv)
    if "--moi" in argv:
        ty.quet()
    bc = dung(ty, now)
    if "--json" in argv:
        from .lam_sach import lam_sach
        print(json.dumps(lam_sach(bc), ensure_ascii=False, indent=1))
    else:
        print(van_ban(bc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
