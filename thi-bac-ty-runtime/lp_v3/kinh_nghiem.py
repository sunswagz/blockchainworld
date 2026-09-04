"""SỔ KINH NGHIỆM — quyết định → kết cục → bài học. Đây là «cầu tuyết».

Cầu tuyết lăn được vì mỗi vòng nó CÓ THÊM một lớp và KHÔNG MẤT lớp cũ. Ở
đây lớp là một cặp (quyết định, kết cục):

    quyết định   máy nói gì, lúc nào, trên bối cảnh nào, với con số dự nào
    kết cục      sau cửa sổ giữ, chuyện gì THẬT SỰ xảy ra — đo từ băng giá
                 (phiên giấy) hoặc từ sổ vị thế (người đã làm theo)
    bài học      gom kết cục theo từng chiều — luật nào, phiên nào, mã nào,
                 phí/LVR ở khoảng nào — và chỉ nói khi ĐỦ MẪU

## Ba luật của sổ

1. **Mọi quyết định đều được chấm, kể cả CHỜ.** Một máy chỉ chấm những lần
   nó bảo VÀO là máy không bao giờ biết mình đã bỏ lỡ gì. Quyết định CHỜ
   được chấm bằng «nếu vào dải đề xuất thì đã ra sao».

2. **Bài học phải mang n và độ tin.** `n = 3` với trung bình +400 bps không
   phải bài học; nó là ba con số. Ngưỡng: n ≥ 5 và |trung bình| ≥ 2 sai số
   chuẩn. Dưới ngưỡng thì vẫn hiện, gắn nhãn «chưa đủ mẫu» — giấu đi là
   giấu luôn cái đang tích.

3. **Bài học quý nhất là khoảng cách giữa MÔ HÌNH và THỰC TẾ**: IL dự so IL
   đo, P(văng) dự so tần suất văng thật. Mọi con số khác ở ty này đứng trên
   hai cái đó, và nếu chúng lệch có hệ thống thì phải sửa mô hình, không
   phải vặn ngưỡng.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import uuid
from pathlib import Path

from .config import THU_MUC

DUONG_SO = THU_MUC / "kinh-nghiem.jsonl"
DUONG_BAI_HOC = THU_MUC / "bai-hoc.json"

TOI_THIEU_MAU = 5
DO_TIN_TOI_THIEU = 2.0


def _bay_gio() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z")


def _doc_luc(s: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


class SoKinhNghiem:
    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or DUONG_SO
        self.quyetDinh: dict[str, dict] = {}
        self.ketCuc: dict[str, dict] = {}
        self._nap()

    def _nap(self) -> None:
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(dong)
            except ValueError:
                continue
            if d.get("loai") == "quyet-dinh":
                self.quyetDinh[d["ma"]] = d
            elif d.get("loai") == "ket-cuc":
                self.ketCuc[d["maQuyetDinh"]] = d

    def _ghi(self, d: dict) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        with self.duong.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def ghi_quyet_dinh(self, kyHieu: str, hanhDong: str, luat: str,
                       boiCanh: dict, dai: dict | None, gia: float | None,
                       giuGio: float, luc: str | None = None) -> str:
        """Ghi một quyết định. Cùng mã + cùng hành động + cùng dải trong
        cùng giờ thì KHÔNG ghi lại — ty quét mỗi 5 phút, và 12 bản chép của
        một quyết định là một mẫu số nói dối (cùng bài học với cửa chống
        trùng của Sổ Đăng Ký)."""
        luc = luc or _bay_gio()
        dau = f"{kyHieu}|{hanhDong}|{luc[:13]}|{(dai or {}).get('Pa')}|{(dai or {}).get('Pb')}"
        for q in self.quyetDinh.values():
            if q.get("dau") == dau:
                return q["ma"]
        d = {"loai": "quyet-dinh", "ma": uuid.uuid4().hex[:10], "luc": luc,
             "kyHieu": kyHieu, "hanhDong": hanhDong, "luat": luat,
             "boiCanh": boiCanh, "dai": dai, "gia": gia, "giuGio": giuGio,
             "dau": dau}
        self.quyetDinh[d["ma"]] = d
        self._ghi(d)
        return d["ma"]

    def ghi_ket_cuc(self, maQuyetDinh: str, kq: dict, nguon: str) -> None:
        """`nguon` là `giay` (chấm từ băng giá) hay `that` (sổ vị thế)."""
        if maQuyetDinh not in self.quyetDinh:
            raise KeyError(f"không có quyết định {maQuyetDinh!r}")
        d = {"loai": "ket-cuc", "maQuyetDinh": maQuyetDinh, "luc": _bay_gio(),
             "nguon": nguon, **kq}
        self.ketCuc[maQuyetDinh] = d
        self._ghi(d)

    def chua_cham(self, now: dt.datetime | None = None) -> list:
        """Quyết định đã QUA HẾT cửa sổ giữ mà chưa có kết cục."""
        now = now or dt.datetime.now(dt.timezone.utc)
        ra = []
        for q in self.quyetDinh.values():
            if q["ma"] in self.ketCuc:
                continue
            t = _doc_luc(q["luc"])
            if t is None:
                continue
            if (now - t).total_seconds() / 3600.0 >= float(q.get("giuGio") or 0):
                ra.append(q)
        return ra

    def cap(self) -> list:
        """`[(quyết định, kết cục)]` — chỉ những cặp đã đủ hai vế."""
        return [(self.quyetDinh[m], k) for m, k in self.ketCuc.items()
                if m in self.quyetDinh]

    def tom_tat(self) -> dict:
        return {"soQuyetDinh": len(self.quyetDinh), "soKetCuc": len(self.ketCuc),
                "soChuaCham": len(self.chua_cham())}


# ── chấm điểm phiên giấy từ băng giá ─────────────────────────────────────

def cham_giay(q: dict, giaTheoGio: list) -> dict | None:
    """Chấm một quyết định bằng đường giá trong cửa sổ giữ.

    `giaTheoGio`: `[(datetime, giá)]` từ lúc quyết định tới hết cửa sổ, đã
    sắp xếp. Cần ít nhất 2 điểm. Với dải đề xuất (Pa, Pb) và giá lúc quyết:

        vangDai         có điểm nào ra ngoài dải không
        phanTrongDai    tỉ lệ điểm còn trong dải
        ilBps           IL tại điểm cuối (hoặc tại điểm văng đầu tiên —
                        vị thế đông cứng từ đó)
        phiBps          phí dự × phần trong dải THẬT (phí không có đường
                        đo riêng, đây là phần mô hình còn lại)
        netBps          phí + IL
        neuVao          net nếu ĐÃ vào — chấm cả quyết định CHỜ

    Không có dải thì không chấm được: trả None, và quyết định ấy ở lại
    danh sách «chưa chấm» chứ không bị lặng lẽ cho 0.
    """
    from .mo_hinh import il_tai_gia, thanh_khoan_tu_do_la

    dai = q.get("dai") or {}
    Pa, Pb, P0 = dai.get("Pa"), dai.get("Pb"), q.get("gia")
    if not (Pa and Pb and P0) or len(giaTheoGio) < 2:
        return None
    L = thanh_khoan_tu_do_la(1.0, P0, Pa, Pb)
    trong = 0
    giaCuoi = giaTheoGio[-1][1]
    vang = False
    for _, g in giaTheoGio:
        if Pa < g < Pb:
            trong += 1
        elif not vang:
            vang = True
            giaCuoi = g
    phan = trong / len(giaTheoGio)
    il = il_tai_gia(L, P0, giaCuoi, Pa, Pb) * 10_000.0
    phiDu = dai.get("phiBps")
    thuongDu = dai.get("thuongBps")
    phanDu = float(dai.get("phanTrongDai") or 1.0) or 1.0
    phi = None if phiDu is None else phiDu / phanDu * phan
    thuong = None if thuongDu is None else thuongDu / phanDu * phan
    net = None if phi is None else phi + (thuong or 0.0) + il
    return {"vangDai": vang, "phanTrongDai": phan, "ilBps": il,
            "phiBps": phi, "thuongBps": thuong, "netBps": net,
            "giaCuoi": giaTheoGio[-1][1],
            "giaDoiPct": (giaTheoGio[-1][1] / P0 - 1.0) * 100.0,
            "soDiem": len(giaTheoGio)}


# ── bài học ──────────────────────────────────────────────────────────────

def _thong_ke(xs: list) -> dict:
    n = len(xs)
    if n == 0:
        return {"n": 0}
    tb = sum(xs) / n
    if n < 2:
        return {"n": n, "trungBinh": tb, "saiSoChuan": None, "doTin": None}
    ps = sum((x - tb) ** 2 for x in xs) / (n - 1)
    se = math.sqrt(ps / n)
    return {"n": n, "trungBinh": tb, "saiSoChuan": se,
            "doTin": (abs(tb) / se) if se > 0 else None}


def _nhom_phi_lvr(v) -> str:
    if v is None:
        return "khong-do"
    return "<1.5" if v < 1.5 else ("1.5-3" if v < 3.0 else ">=3")


def _nhom_vang(v) -> str:
    if v is None:
        return "khong-do"
    return "<0.3" if v < 0.3 else ("0.3-0.6" if v < 0.6 else ">=0.6")


def bai_hoc(cap: list) -> dict:
    """Gom kết cục theo từng chiều; mỗi dòng mang n, trung bình, độ tin,
    và nhãn ĐỦ / CHƯA ĐỦ mẫu. Cộng thêm hai phép so mô hình–thực tế."""
    chieu = {"luat": {}, "phien": {}, "kyHieu": {}, "phiTrenLvr": {},
             "xacSuatVang": {}, "hanhDong": {}}
    ilDu, ilDo, vangDu, vangDo = [], [], [], []
    for q, k in cap:
        net = k.get("netBps")
        if net is None:
            continue
        bc = q.get("boiCanh") or {}
        dai = q.get("dai") or {}
        khoa = {
            "luat": q.get("luat", "?"),
            "phien": bc.get("trangThaiPhien", "?"),
            "kyHieu": q.get("kyHieu", "?"),
            "phiTrenLvr": _nhom_phi_lvr(bc.get("tiLePhiTrenLvr")),
            "xacSuatVang": _nhom_vang(bc.get("xacSuatVang")),
            "hanhDong": q.get("hanhDong", "?"),
        }
        for c, kh in khoa.items():
            chieu[c].setdefault(kh, []).append(net)
        if dai.get("ilKyVongBps") is not None and k.get("ilBps") is not None:
            ilDu.append(dai["ilKyVongBps"])
            ilDo.append(k["ilBps"])
        xv = (dai.get("xacSuatVang") or {}).get("tong")
        if xv is not None and k.get("vangDai") is not None:
            vangDu.append(float(xv))
            vangDo.append(1.0 if k["vangDai"] else 0.0)

    ra = {"luc": _bay_gio(), "soCap": len(cap), "chieu": {}, "moHinh": {}}
    for c, nhom in chieu.items():
        ds = []
        for kh, xs in nhom.items():
            tk = _thong_ke(xs)
            du = (tk["n"] >= TOI_THIEU_MAU and tk.get("doTin") is not None
                  and tk["doTin"] >= DO_TIN_TOI_THIEU)
            ds.append({"nhom": kh, **tk, "duMau": du,
                       "cau": _cau(c, kh, tk, du)})
        ds.sort(key=lambda d: -(d.get("n") or 0))
        ra["chieu"][c] = ds
    if ilDu:
        lech = [b - a for a, b in zip(ilDu, ilDo)]
        tk = _thong_ke(lech)
        ra["moHinh"]["il"] = {**tk, "cau": (
            f"IL đo trung bình {'cao' if tk['trungBinh'] < 0 else 'thấp'} hơn "
            f"IL dự {abs(tk['trungBinh']):.0f} bps (n={tk['n']})"
            + (" — LỆCH CÓ HỆ THỐNG, xem lại σ hoặc τ"
               if tk.get("doTin") and tk["doTin"] >= DO_TIN_TOI_THIEU
               and tk["n"] >= TOI_THIEU_MAU else " — chưa đủ để kết luận"))}
    if vangDu:
        n = len(vangDu)
        ra["moHinh"]["vang"] = {
            "n": n, "duTrungBinh": sum(vangDu) / n,
            "doTrungBinh": sum(vangDo) / n,
            "cau": (f"P(văng) dự trung bình {sum(vangDu) / n:.0%}, văng thật "
                    f"{sum(vangDo) / n:.0%} (n={n}) — dự là CẬN TRÊN nên "
                    f"dự ≥ thật là đúng chiều; dự < thật là mô hình lạc quan")}
    return ra


def _cau(chieu: str, nhom: str, tk: dict, du: bool) -> str:
    if tk["n"] == 0:
        return ""
    ten = {"luat": "luật", "phien": "phiên", "kyHieu": "mã",
           "phiTrenLvr": "phí/LVR", "xacSuatVang": "P(văng) dự",
           "hanhDong": "hành động"}[chieu]
    return (f"{ten} {nhom}: NET trung bình {tk['trungBinh']:+.0f} bps trên "
            f"{tk['n']} lần" + (" — ĐỦ MẪU" if du else " — chưa đủ mẫu"))


def ghi_bai_hoc(bh: dict, duong: Path | None = None) -> Path:
    p = duong or DUONG_BAI_HOC
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(bh, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def nap_bai_hoc(duong: Path | None = None) -> dict | None:
    p = duong or DUONG_BAI_HOC
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None
