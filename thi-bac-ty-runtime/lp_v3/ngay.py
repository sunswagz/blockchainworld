"""VÒNG NGÀY — ba mốc, mỗi mốc một việc, và mốc tối là mốc HỌC.

    sang        07:00 VN    bản tin sáng: phiên hôm nay, sự kiện, thưởng,
                            từng pool nên làm gì
    truoc-mo    60 phút trước sàn Mỹ mở (20:30 hoặc 21:30 VN)
                            soát lại trước cú «bắt kịp» lúc mở cửa
    sau-dong    30 phút sau đóng cửa (03:30 hoặc 04:30 VN)
                            CHẤM quyết định đã hết cửa sổ · gom BÀI HỌC ·
                            chạy MỘT lượt tiến hoá · ghi báo cáo ngày

Mốc nào đến hạn thì chạy ở lượt quét kế tiếp — không có bộ hẹn giờ riêng,
vì bộ hẹn giờ riêng là một tiến trình nữa để chết mà không ai hay (Thị Bạc
Ty đã chết 70,8 giờ như thế). Mốc bỏ lỡ (máy tắt) chạy bù ở lượt đầu tiên
sau khi bật, và báo cáo ghi rõ là chạy bù.

Sổ mốc: `data/lp-v3/vong-ngay.json` — `{mốc: ngày đã chạy gần nhất}`.
Báo cáo: `data/lp-v3/bao-cao/YYYY-MM-DD-<mốc>.md` và `.json`.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from . import bang_gia, hom_nay, lich
from .lam_sach import lam_sach as sach
from .config import THU_MUC
from .kinh_nghiem import bai_hoc, cham_giay, ghi_bai_hoc

DUONG_SO_MOC = THU_MUC / "vong-ngay.json"
THU_MUC_BAO_CAO = THU_MUC / "bao-cao"
MOC = ("sang", "truoc-mo", "sau-dong")


def gio_moc(moc: str, ngay: dt.date) -> dt.datetime | None:
    """Giờ VN của mốc trong ngày `ngay` (ngày theo lịch VN). Mốc gắn với
    phiên Mỹ thì lấy phiên có mốc rơi vào ngày ấy; không có → None."""
    if moc == "sang":
        return dt.datetime.combine(ngay, dt.time(7, 0), lich.VN)
    if moc == "truoc-mo":
        ph = lich.phien_my(ngay)
        return None if ph is None else ph[0] - dt.timedelta(minutes=60)
    if moc == "sau-dong":
        # phiên đóng lúc 03:00/04:00 VN của ngày kế → mốc thuộc ngày kế
        ph = lich.phien_my(ngay - dt.timedelta(days=1))
        return None if ph is None else ph[1] + dt.timedelta(minutes=30)
    raise ValueError(moc)


class VongNgay:
    def __init__(self, ty, duongSoMoc: Path | None = None,
                 thuMucBaoCao: Path | None = None) -> None:
        self.ty = ty
        self.duongSoMoc = duongSoMoc or DUONG_SO_MOC
        self.thuMucBaoCao = thuMucBaoCao or THU_MUC_BAO_CAO
        self.daChay = self._nap()
        self.lanCuoi: dict = {}

    def _nap(self) -> dict:
        try:
            return (json.loads(self.duongSoMoc.read_text(encoding="utf-8"))
                    if self.duongSoMoc.exists() else {})
        except ValueError:
            return {}

    def _ghi(self) -> None:
        self.duongSoMoc.parent.mkdir(parents=True, exist_ok=True)
        self.duongSoMoc.write_text(json.dumps(self.daChay), encoding="utf-8")

    def den_han(self, now: dt.datetime | None = None) -> list:
        """Mốc nào đã tới giờ hôm nay (hoặc hôm qua, chưa chạy) — trả về
        `[(mốc, ngày, chạyBù)]`."""
        now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(lich.VN)
        ra = []
        for moc in MOC:
            for lui in (0, 1):
                ngay = now.date() - dt.timedelta(days=lui)
                g = gio_moc(moc, ngay)
                if g is None or g > now:
                    continue
                if self.daChay.get(moc) == ngay.isoformat():
                    continue
                if lui == 1 and self.daChay.get(moc, "") >= ngay.isoformat():
                    continue
                ra.append((moc, ngay, lui == 1 or (now - g) > dt.timedelta(hours=2)))
                break
        return ra

    def chay_neu_den_han(self, now: dt.datetime | None = None) -> list:
        ra = []
        for moc, ngay, bu in self.den_han(now):
            ra.append(self.chay(moc, ngay, bu, now))
        return ra

    def chay(self, moc: str, ngay: dt.date, chayBu: bool = False,
             now: dt.datetime | None = None) -> dict:
        now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(lich.VN)
        bc = hom_nay.dung(self.ty, now)
        hoc = None
        if moc == "sau-dong":
            hoc = self.hoc(now)
        bc["moc"] = moc
        bc["ngay"] = ngay.isoformat()
        bc["chayBu"] = chayBu
        bc["hoc"] = hoc
        self.thuMucBaoCao.mkdir(parents=True, exist_ok=True)
        ten = f"{ngay.isoformat()}-{moc}"
        (self.thuMucBaoCao / f"{ten}.json").write_text(
            json.dumps(sach(bc), ensure_ascii=False, indent=1), encoding="utf-8")
        vb = hom_nay.van_ban(bc)
        if chayBu:
            vb = f"(CHẠY BÙ lúc {now.strftime('%H:%M %d/%m')} — mốc {moc} của ngày {ngay})\n" + vb
        if hoc:
            vb += "\n" + "-" * 72 + f"\nHỌC: chấm {hoc['soCham']} quyết định · " \
                  f"{hoc['soChuaCham']} chưa chấm được (thiếu giá) · " \
                  f"bài học {hoc['soCap']} cặp" \
                  + (f"\nTIẾN HOÁ: {hoc['tienHoa']}" if hoc.get("tienHoa") else "")
        (self.thuMucBaoCao / f"{ten}.md").write_text(vb, encoding="utf-8")
        self.daChay[moc] = ngay.isoformat()
        self.lanCuoi[moc] = now.isoformat()
        self._ghi()
        return bc

    # ── học ─────────────────────────────────────────────────────────────
    def hoc(self, now: dt.datetime | None = None) -> dict:
        """Chấm mọi quyết định đã hết cửa sổ, gom bài học, một lượt tiến hoá."""
        now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
        so = self.ty.soKinhNghiem
        cham = chua = 0
        for q in so.chua_cham(now):
            kq = cham_giay(q, self._duong_gia(q, now))
            if kq is None:
                chua += 1
                continue
            so.ghi_ket_cuc(q["ma"], kq, "giay")
            cham += 1
        # kết cục THẬT từ sổ vị thế ghi đè phiên giấy cho cùng quyết định
        from .theo_doi import ket_cuc
        for v in self.ty.soViThe.da_dong():
            if v.maQuyetDinh and v.maQuyetDinh in so.quyetDinh:
                kc = ket_cuc(v)
                if kc and (v.maQuyetDinh not in so.ketCuc
                           or so.ketCuc[v.maQuyetDinh].get("nguon") != "that"):
                    so.ghi_ket_cuc(v.maQuyetDinh, {
                        "vangDai": kc["vangDai"], "ilBps": kc["ilBps"],
                        "netBps": kc["laiLoBps"], "phiBps": None,
                        "phanTrongDai": None, "giaDoiPct": kc["giaDoiPct"]}, "that")
        bh = bai_hoc(so.cap())
        ghi_bai_hoc(bh)
        th = self._tien_hoa()
        return {"soCham": cham, "soChuaCham": chua, "soCap": bh["soCap"],
                "tienHoa": th}

    def _duong_gia(self, q: dict, now: dt.datetime) -> list:
        """`[(t, giá)]` từ lúc quyết định tới hết cửa sổ: mẫu chuỗi + đóng
        cửa gốc, gộp và sắp xếp."""
        from .config import ma_goc
        ma = ma_goc(q["kyHieu"])
        try:
            t0 = dt.datetime.fromisoformat(q["luc"].replace("Z", "+00:00"))
        except ValueError:
            return []
        t1 = t0 + dt.timedelta(hours=float(q.get("giuGio") or 0))
        d = bang_gia.nap(ma, self.ty.thuMucBang)
        ds = [(t0, float(q["gia"]))]
        for x in d["chuoi"]:
            try:
                t = dt.datetime.fromisoformat(x["luc"].replace("Z", "+00:00"))
            except ValueError:
                continue
            if t0 < t <= t1:
                ds.append((t, x["gia"]))
        for x in d["goc"]:
            try:
                t = dt.datetime.fromisoformat(x["ngay"]).replace(hour=21, tzinfo=dt.timezone.utc)
            except ValueError:
                continue
            if t0 < t <= t1:
                ds.append((t, x["dong"]))
        ds.sort(key=lambda p: p[0])
        return ds

    def _tien_hoa(self) -> str | None:
        from . import tien_hoa
        from .config import ghi as ghi_cau_hinh, ma_goc, nap as nap_cau_hinh
        cfg = self.ty.cfg
        ds = [ma_goc(p["kyHieu"]) for p in cfg.get("pool") or []]
        bang = tien_hoa.bang_tu_dia(ds, self.ty.thuMucBang)
        apr = {}
        for c in self.ty.coHoi:
            if c.aprPhi is not None:
                apr[c.ma] = c.aprPhi
        if not any(len(g) > tien_hoa.SO_PHIEN_SIGMA + 5 for g in bang.values()):
            return "băng chưa đủ dày để chạy lại"
        ra = tien_hoa.mot_luot(dict(cfg["nut"]), bang, apr)
        ra["tuVan"] = bool(cfg.get("tuVanTienHoa"))
        if ra.get("nhan") and ra["tuVan"]:
            ch = nap_cau_hinh()
            ch.setdefault("nut", {})[ra["nhan"]["nut"]] = ra["nhan"]["den"]
            ghi_cau_hinh(ch)
            self.ty.cfg["nut"][ra["nhan"]["nut"]] = ra["nhan"]["den"]
            ra["ketLuan"] += " — ĐÃ ÁP DỤNG (tuVanTienHoa bật)"
        elif ra.get("nhan"):
            ra["ketLuan"] += " — CHỜ NGƯỜI (tuVanTienHoa tắt)"
        tien_hoa.ghi_so(ra)
        return ra["ketLuan"]
