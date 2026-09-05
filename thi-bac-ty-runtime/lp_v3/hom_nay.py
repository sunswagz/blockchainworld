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

    return {
        "luc": now.isoformat(), "lucVn": now.strftime("%H:%M %d/%m/%Y"),
        "phien": bc.tom_tat(),
        "thuong": _thuong(cfg, now, co),
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
        "pool": [_mot_pool(c) for c in co],
        "viThe": viThe,
        "baiHoc": _bai_hoc_gon(nap_bai_hoc()),
        "kinhNghiem": ty.soKinhNghiem.tom_tat(),
        "tienHoa": _tien_hoa_gon(),
        "nut": cfg.get("nut"),
    }


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


def _mot_pool(c) -> dict:
    kd = c.dai
    d = {"kyHieu": c.kyHieu, "hanhDong": c.quyetDinh.hanhDong,
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
