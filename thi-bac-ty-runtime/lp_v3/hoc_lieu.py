"""HỌC LIỆU — ty học từ bài giảng, và học thành QUY TẮC có phép canh.

Một bài học (transcript, bài phân tích, tài liệu) đi qua ba bước:

    THÊM     lưu nguyên văn vào `data/lp-v3/hoc-lieu/<ma>.md` + một dòng sổ
    BÓC      agent riêng của ty (claude CLI, quota gói — không khoá API) đọc
             nguyên văn và trả JSON theo KHUÔN dưới: luận điểm, quy tắc,
             câu hỏi, đánh giá sao. Không có CLI thì người bóc tay cùng khuôn.
    GẮN      mỗi quy tắc bóc ra được ĐỐI CHIẾU với sổ luật, núm, trường báo
             cáo đang có: `da-co` (đã là luật/núm/trường), `thieu-phep-canh`
             (đúng nhưng chưa có gì canh), `y-tuong` (chưa đo được).

Bước ba là điểm của cả file — cùng tinh thần `hien_phap.py`: một nguyên
tắc chỉ nằm trong văn xuôi thì không giữ được gì. Học xong mà không gắn
được vào phép canh nào thì phải khai ra là chưa gắn được.

Tri thức đã bóc và GHIM (đã người soát) nằm ở `lp_v3/tri_thuc.json` — trong
kho mã, commit được, đọc chung mọi máy. Học liệu người vừa thêm nằm ở
`data/` cho tới khi được soát và ghim.

## Luận điểm KHÔNG phải quy tắc

«Bitcoin có thể tạo dòng tiền» là luận điểm: có thể kiểm chứng on-chain,
chưa kiểm. «Không thấy APY cao là vào» là quy tắc: gắn được vào
`quyet_dinh.SO_LUAT` (`phi-duoi-lvr`, `sap-het-thuong`). Sổ giữ hai thứ
riêng, và tính sao riêng — bài nhiều luận điểm ít quy tắc là bài triết lý.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

from .config import THU_MUC

GOC = Path(__file__).resolve().parent
DUONG_TRI_THUC = GOC / "tri_thuc.json"
THU_MUC_HOC_LIEU = THU_MUC / "hoc-lieu"
DUONG_SO = THU_MUC / "hoc-lieu.jsonl"

TRANG_THAI_QUY_TAC = ("da-co", "thieu-phep-canh", "y-tuong")
LOAI_LUAN_DIEM = ("kiem-chung-duoc", "narrative", "nguyen-tac")

#: Những chỗ một quy tắc GẮN được. Mỗi mục là (tên, hàm liệt kê mã đang có)
#: — đối chiếu bằng mã, không bằng câu, để đổi tên luật là phép soát đỏ.
def _ma_luat() -> set:
    from .quyet_dinh import MA_LUAT
    return set(MA_LUAT)


def _ma_nut() -> set:
    from .tien_hoa import NUT_VAN
    return set(NUT_VAN)


def _ma_cua() -> set:
    from .config import CUA_AN_TOAN
    return set(CUA_AN_TOAN)


TRUONG_BAO_CAO = {
    "hanhDongNgay", "dieuKien", "tinCay", "khoaVao", "diem", "apyTach", "netBps",
    "tiLePhiTrenLvr", "ilKyVongBps", "lvrBps", "xacSuatVang", "vonLp", "pnlUocUsd",
    "phiChoThuUsd", "cheDoRuiRo", "thiTruongGoc", "tinAnhHuong", "kinhNghiem",
    "baiHoc", "tienHoa", "sucChuaUsd", "vonXinUsd", "thuong", "vi",
    # Bài 2: KPI vốn
    "mucTieu", "hieuQuaVon", "dongTienUocThangUsd", "dongTienDaVeTayThangUsd", "diemTuDo", "ilUsd",
    # Bài 3: đích đến
    "giaiDoanTuDo", "dongTienTheoThang", "dongTienTruot6ThangUsd", "doOnDinhDongTien", "coSoTuDo",
    # Bài 4: kiểm toán năm hoá, mốc HOLD, ba nguồn lợi nhuận, doanh nghiệp nhỏ
    "aprTuongDuongPct", "apyLaLaiKep", "alphaSoHoldUsd", "tachLoiNhuan", "business", "donBayUsd",
    # Bài 5: hữu cơ, vòng quay, lãi nền, Lego rủi ro
    "tiLeHuuCo", "vongQuay", "soLaiNenPct", "laiSuatNen", "chuoiPhuThuoc",
}

KHUON_JSON = {
    "ten": "tên bài, ngắn",
    "nguon": "khoá học / tác giả / mốc thời gian trong video",
    "tomTat": "3–5 câu: ông ấy dạy gì",
    "danhGia": {"kyThuatLp": 1, "quanLyVon": 1, "tuDuyHeThong": 1,
                "tradeDuoc": 1, "giaTriChoHeThong": 1},
    "luanDiem": [{"cau": "…", "loai": "kiem-chung-duoc|narrative|nguyen-tac",
                  "ghi": "kiểm chứng bằng cách nào, hoặc vì sao chỉ là narrative"}],
    "quyTac": [{"ma": "kebab-case", "cau": "quy tắc viết dạng LÀM/KHÔNG LÀM gì khi nào",
                "gan": {"luat": ["mã luật trong SO_LUAT"], "nut": ["núm"],
                        "truong": ["trường báo cáo"]},
                "ghi": "vì sao gắn vào đó, hoặc vì sao chưa gắn được"}],
    "cauHoiChoHeThong": ["câu hỏi người vận hành cần bảng trả lời được"],
    "khongLay": ["điều trong bài KHÔNG đưa vào hệ thống, và vì sao"],
}


def _bay_gio() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def gan_quy_tac(qt: dict) -> dict:
    """Đối chiếu một quy tắc với luật · núm · cửa · trường đang có → trạng thái.

    `da-co` khi ít nhất một mã GẮN có thật. Mã gắn mà KHÔNG tồn tại thì bị
    kê ra — quy tắc trỏ vào một luật đã đổi tên là quy tắc mồ côi, và mồ côi
    phải hiện ra chứ không được đếm là đã có.
    """
    g = qt.get("gan") or {}
    co, moCoi = [], []
    for k, tap in (("luat", _ma_luat()), ("nut", _ma_nut()), ("cua", _ma_cua()),
                   ("truong", TRUONG_BAO_CAO)):
        for m in g.get(k) or []:
            (co if m in tap else moCoi).append(f"{k}:{m}")
    tt = qt.get("trangThai")
    if co:
        tt = "da-co"
    elif tt not in TRANG_THAI_QUY_TAC:
        tt = "thieu-phep-canh" if qt.get("doDuoc", True) else "y-tuong"
    return {**qt, "trangThai": tt, "daGan": co, "moCoi": moCoi}


def soat_bai(bai: dict) -> dict:
    """Soát một bài đã bóc: gắn từng quy tắc, đếm, và kê chỗ sai khuôn."""
    loi = []
    for k in ("ten", "tomTat", "luanDiem", "quyTac"):
        if k not in bai:
            loi.append(f"thiếu `{k}`")
    ld = []
    for x in bai.get("luanDiem") or []:
        if x.get("loai") not in LOAI_LUAN_DIEM:
            loi.append(f"luận điểm «{str(x.get('cau'))[:40]}» loại {x.get('loai')!r} lạ")
        ld.append(dict(x, trangThai=x.get("trangThai") or "chua-kiem"))
    qt = [gan_quy_tac(x) for x in (bai.get("quyTac") or [])]
    dem = {t: sum(1 for x in qt if x["trangThai"] == t) for t in TRANG_THAI_QUY_TAC}
    moCoi = [m for x in qt for m in x["moCoi"]]
    return {**bai, "luanDiem": ld, "quyTac": qt, "demQuyTac": dem,
            "moCoi": moCoi, "loiKhuon": loi}


def nap_tri_thuc(duong: Path | None = None) -> list:
    p = duong or DUONG_TRI_THUC
    if not p.exists():
        return []
    try:
        ds = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return []
    return [soat_bai(b) for b in (ds.get("bai") or [])]


class SoHocLieu:
    """Học liệu người thêm ở máy — chưa ghim vào kho mã."""

    def __init__(self, duong: Path | None = None, thuMuc: Path | None = None) -> None:
        self.duong = duong or DUONG_SO
        self.thuMuc = thuMuc or THU_MUC_HOC_LIEU
        self.bai: dict = {}
        self._nap()

    def _nap(self) -> None:
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(dong)
            except ValueError:
                continue
            if d.get("loai") == "them":
                self.bai[d["ma"]] = {"ma": d["ma"], "ten": d.get("ten"), "nguon": d.get("nguon"),
                                     "luc": d.get("luc"), "duong": d.get("duong"), "boc": None}
            elif d.get("loai") == "boc" and d.get("ma") in self.bai:
                self.bai[d["ma"]]["boc"] = d.get("ketQua")
                self.bai[d["ma"]]["bocLuc"] = d.get("luc")
                self.bai[d["ma"]]["bocBang"] = d.get("bang")

    def _ghi(self, d: dict) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        with self.duong.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def them(self, ten: str, noiDung: str, nguon: str = "") -> dict:
        if not (noiDung or "").strip():
            raise ValueError("nội dung rỗng")
        ma = re.sub(r"[^a-z0-9]+", "-", (ten or "bai").lower()).strip("-")[:40] or "bai"
        ma = f"{ma}-{uuid.uuid4().hex[:6]}"
        self.thuMuc.mkdir(parents=True, exist_ok=True)
        p = self.thuMuc / f"{ma}.md"
        p.write_text(noiDung, encoding="utf-8")
        d = {"loai": "them", "ma": ma, "ten": ten, "nguon": nguon, "luc": _bay_gio(),
             "duong": str(p), "soChu": len(noiDung)}
        self._ghi(d)
        self.bai[ma] = {"ma": ma, "ten": ten, "nguon": nguon, "luc": d["luc"], "duong": str(p), "boc": None}
        return self.bai[ma]

    def ghi_boc(self, ma: str, ketQua: dict, bang: str) -> dict:
        if ma not in self.bai:
            raise KeyError(ma)
        self._ghi({"loai": "boc", "ma": ma, "luc": _bay_gio(), "bang": bang, "ketQua": ketQua})
        self.bai[ma]["boc"] = ketQua
        self.bai[ma]["bocLuc"] = _bay_gio()
        self.bai[ma]["bocBang"] = bang
        return self.bai[ma]

    def chua_boc(self) -> list:
        return [b for b in self.bai.values() if not b.get("boc")]

    def tom_tat(self) -> dict:
        return {"soBai": len(self.bai), "soChuaBoc": len(self.chua_boc())}


# ── agent riêng: claude CLI, quota gói ────────────────────────────────

_UNG_VIEN_CLI = (
    os.environ.get("CLAUDE_CLI") or "",
    "claude",
    str(Path.home() / ".local" / "bin" / "claude.exe"),
    str(Path.home() / ".local" / "bin" / "claude"),
    str(Path(os.environ.get("LOCALAPPDATA", "") or ".") / "Programs" / "claude" / "claude.exe"),
    str(Path.home() / "AppData/Roaming/npm/claude.cmd"),
)
#: Bốn chốt chép từ `tu-cam-thanh-runtime/trader/cli_claude.py`, vì đây là thứ
#: tiêu quota của người: tắt hết công cụ (agent chỉ đọc bài, không được chạy
#: lệnh trên máy), cắt phần mở đầu động (tiết kiệm nửa token nạp), prompt đi
#: qua STDIN (Windows chặn dòng lệnh ~32.767 ký tự — một transcript đã vượt),
#: chạy ở thư mục tạm (CLI quét cwd để dựng ngữ cảnh, không cho nó đọc repo).
TAT_CONG_CU = ("Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Task,TodoWrite,"
               "NotebookEdit,Agent,Artifact,SlashCommand")


def tim_claude_cli() -> str | None:
    """Đường tới `claude` CLI. Ưu tiên biến môi trường; rồi PATH; rồi bản
    đi kèm tiện ích VS Code (glob theo phiên bản — đừng ghim số)."""
    for u in _UNG_VIEN_CLI:
        if u and (shutil.which(u) or Path(u).exists()):
            return shutil.which(u) or u
    goc = Path.home() / ".vscode" / "extensions"
    if goc.exists():
        ung = sorted(goc.glob("anthropic.claude-code-*/resources/native-binary/claude.exe"))
        if ung:
            return str(ung[-1])
    return None


def loi_nhac_boc(noiDung: str, ten: str) -> str:
    return (
        "Bạn là agent học của ty Bể Thanh Khoản (Thị Bạc Ty). Đọc bài dưới và bóc thành "
        "JSON THUẦN (không markdown, không lời dẫn) theo đúng khuôn này:\n"
        + json.dumps(KHUON_JSON, ensure_ascii=False, indent=1)
        + "\n\nLuật bóc:\n"
        "- luanDiem là điều tác giả KHẲNG ĐỊNH; quyTac là điều hệ thống LÀM/KHÔNG LÀM. Không lẫn.\n"
        "- `gan.luat` chỉ được dùng các mã: " + ", ".join(sorted(_ma_luat())) + ".\n"
        "- `gan.nut` chỉ được dùng: " + ", ".join(sorted(_ma_nut())) + ".\n"
        "- `gan.truong` chỉ được dùng: " + ", ".join(sorted(TRUONG_BAO_CAO)) + ".\n"
        "- Không gắn được thì để mảng rỗng và nói vì sao ở `ghi`. Đừng bịa mã.\n"
        "- Đánh giá sao 1–5, số nguyên. Lời hứa kiếm tiền của tác giả là `narrative`.\n"
        f"\nTÊN BÀI: {ten}\n\nBÀI:\n" + noiDung[:60_000]
    )


def boc_bang_cli(noiDung: str, ten: str, cli: str | None = None,
                 hetGioGiay: float = 240.0) -> tuple[dict | None, str]:
    """Gọi claude CLI một lượt, trả `(json, lỗi)`. Không CLI → (None, lý do)."""
    import tempfile
    cli = cli or tim_claude_cli()
    if not cli:
        return None, "không thấy claude CLI (đặt CLAUDE_CLI=đường dẫn claude.exe)"
    tmp = tempfile.mkdtemp(prefix="lp-v3-hoc-")
    try:
        r = subprocess.run(
            [cli, "-p", "--exclude-dynamic-system-prompt-sections",
             "--disallowed-tools", TAT_CONG_CU, "--output-format", "json"],
            input=loi_nhac_boc(noiDung, ten), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=hetGioGiay, cwd=tmp)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        return None, f"CLI thoát {r.returncode}: {(r.stderr or r.stdout)[-400:]}"
    van = r.stdout.strip()
    try:
        vo = json.loads(van)
        if isinstance(vo, dict):
            if vo.get("is_error"):
                return None, f"CLI báo lỗi: {str(vo.get('result'))[:200]}"
            van = str(vo.get("result") or van)
    except ValueError:
        pass
    m = re.search(r"\{.*\}", van, re.S)
    if not m:
        return None, "CLI không trả JSON"
    try:
        return json.loads(m.group(0)), ""
    except ValueError as e:
        return None, f"JSON hỏng: {e}"


def tom_tat_tri_thuc(bais: list, soHocLieu: SoHocLieu | None = None) -> dict:
    """Một dòng cho báo cáo: bao nhiêu bài, bao nhiêu quy tắc đã gắn / chưa,
    quy tắc mồ côi, học liệu chờ bóc."""
    dem = {t: 0 for t in TRANG_THAI_QUY_TAC}
    moCoi = []
    for b in bais:
        for t in TRANG_THAI_QUY_TAC:
            dem[t] += (b.get("demQuyTac") or {}).get(t, 0)
        moCoi += b.get("moCoi") or []
    thieu = [{"bai": b.get("ten"), "ma": q["ma"], "cau": q["cau"], "ghi": q.get("ghi", "")}
             for b in bais for q in b.get("quyTac") or [] if q["trangThai"] != "da-co"]
    return {"soBai": len(bais), "demQuyTac": dem, "moCoi": moCoi,
            "chuaGan": thieu[:12],
            "bai": [{"ma": b.get("ma"), "ten": b.get("ten"), "nguon": b.get("nguon"),
                     "danhGia": b.get("danhGia"), "demQuyTac": b.get("demQuyTac"),
                     "soLuanDiem": len(b.get("luanDiem") or [])} for b in bais],
            "hocLieu": soHocLieu.tom_tat() if soHocLieu else None,
            "cli": tim_claude_cli() is not None}


def _main(argv: list) -> int:
    """`python -m lp_v3.hoc_lieu them <file.md> [tên] [nguồn]` · `boc <mã>` · `soat`"""
    so = SoHocLieu()
    if not argv or argv[0] == "soat":
        tt = tom_tat_tri_thuc(nap_tri_thuc(), so)
        print(json.dumps(tt, ensure_ascii=False, indent=1))
        return 0
    if argv[0] == "them":
        p = Path(argv[1])
        b = so.them(argv[2] if len(argv) > 2 else p.stem, p.read_text(encoding="utf-8"),
                    argv[3] if len(argv) > 3 else "")
        print("đã thêm", b["ma"], "→ bóc bằng: python -m lp_v3.hoc_lieu boc", b["ma"])
        return 0
    if argv[0] == "boc":
        b = so.bai.get(argv[1])
        if not b:
            print("không có bài", argv[1]); return 1
        kq, loi = boc_bang_cli(Path(b["duong"]).read_text(encoding="utf-8"), b["ten"] or b["ma"])
        if kq is None:
            print("bóc hỏng:", loi); return 1
        so.ghi_boc(b["ma"], kq, "claude-cli")
        s = soat_bai(dict(kq, ma=b["ma"]))
        print(json.dumps({"demQuyTac": s["demQuyTac"], "moCoi": s["moCoi"], "loiKhuon": s["loiKhuon"]},
                         ensure_ascii=False, indent=1))
        print("→ soát rồi ghim vào lp_v3/tri_thuc.json để dùng chung mọi máy")
        return 0
    print(__doc__); return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
