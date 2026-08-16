"""Kiểm cửa duyệt Champion/Challenger, và tầng bài học từ lịch sử.

    python scripts/kiem-chien-luoc.py

Cửa duyệt là chỗ DUY NHẤT quyết định cái gì được chạy bằng tiền, nên nó phải là
chỗ dễ kiểm nhất chứ không phải chỗ khó nhất. `phan_quyet()` viết thành hàm
thuần chính là để kiểm được bằng số bịa, không cần chạy cả cỗ máy.

Thứ đang gác: **một challenger tồi không được lọt qua bằng bất kỳ đường nào.**
Mỗi phép kiểm dưới đây là một đường lọt đã nghĩ ra được.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("TCT_DATA_DIR", tempfile.mkdtemp(prefix="tct-cl-"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import bai_hoc_lich_su as B, chien_luoc as CL, store  # noqa: E402
from trader.journal import recall  # noqa: E402

sai = 0


def ok(m: str) -> None:
    print(f"  OK   {m}")


def bao(m: str) -> None:
    global sai
    sai += 1
    print(f"  SAI  {m}")


def tk(so=50, kv=0.2, khop=0.1, sut=8.0):
    return {"so": so, "kyVongR": kv, "khopTroi": khop, "sutGiamToiDaPct": sut}


CHA = tk(so=60, kv=0.10, khop=0.05, sut=10.0)

print("\n[1] challenger tốt hơn rõ ràng thì PHẢI qua")
p = CL.phan_quyet(CHA, tk(so=45, kv=0.35, khop=0.10, sut=9.0))
ok("cho qua") if p["qua"] else bao(f"bị chặn oan: {p['lyDo']}")

print("\n[2] các đường lọt phải bị chặn")
truong_hop = [
    ("quá ít lệnh ngoài mẫu", tk(so=5, kv=0.9), "lệnh ngoài mẫu"),
    ("kỳ vọng ÂM dù hơn champion", tk(so=50, kv=-0.05), "không dương"),
    ("chỉ nhỉnh hơn champion tí xíu", tk(so=50, kv=0.12), "không vượt"),
    ("đẹp trong mẫu, rơi ngoài mẫu", tk(so=50, kv=0.30, khop=0.80), "khớp trội"),
    ("kỳ vọng hơn nhưng đau gấp đôi", tk(so=50, kv=0.30, sut=30.0), "sụt giảm"),
    ("không có kỳ vọng để so", tk(so=50, kv=None), "không có kỳ vọng"),
]
for ten, t, dau_hieu in truong_hop:
    p = CL.phan_quyet(CHA, t)
    if p["qua"]:
        bao(f"LỌT: {ten}")
    elif any(dau_hieu in l for l in p["lyDo"]):
        ok(f"chặn đúng lý do — {ten}")
    else:
        bao(f"chặn {ten} nhưng lý do lạ: {p['lyDo']}")

print("\n[3] champion đang lỗ không phải cái cớ để hạ chuẩn")
# Champion -0.5R. Challenger -0.2R: hơn hẳn champion, nhưng vẫn lỗ.
p = CL.phan_quyet(tk(so=60, kv=-0.5), tk(so=50, kv=-0.2))
if p["qua"]:
    bao("LỌT: cho lên một chiến lược vẫn đang lỗ chỉ vì nó đỡ lỗ hơn")
else:
    ok("chặn — thắng một champion đang lỗ thì vẫn là lỗ")

print("\n[4] chưa có champion (lần đầu) vẫn phải đòi kỳ vọng dương")
p = CL.phan_quyet(None, tk(so=50, kv=-0.1))
ok("chặn") if not p["qua"] else bao("LỌT: nhận một chiến lược lỗ làm champion đầu tiên")
p = CL.phan_quyet(None, tk(so=50, kv=0.3))
ok("cho qua khi dương và đủ mẫu") if p["qua"] else bao(f"chặn oan: {p['lyDo']}")

print("\n[5] không có đường vòng: duyệt khi chưa qua cửa phải bị từ chối")
CL.de_xuat("MOCK_RANGE_V1", "Chiến lược biên", {}, "thử")
d = CL.doc()
k = d["challengers"][0]["khoa"]
r = CL.duyet(k)
ok(f"từ chối vì chưa đo: {r.get('viSao')}") if not r["ok"] else bao("LỌT: duyệt được khi chưa đo")

# Gắn phán quyết KHÔNG qua rồi thử duyệt lần nữa
d = CL.doc()
d["challengers"][0]["phanQuyet"] = {"qua": False, "lyDo": ["bịa để kiểm"]}
CL.ghi(d)
r = CL.duyet(k)
ok("từ chối khi phán quyết là KHÔNG QUA") if not r["ok"] else bao("LỌT: duyệt được dù phán quyết là không qua")

print("\n[6] duyệt hợp lệ thì champion phải đổi thật và tăng phiên bản")
d = CL.doc()
cu = d["champion"]["ma"]
d["challengers"][0]["phanQuyet"] = {"qua": True, "lyDo": [], "tomTat": "ok"}
d["challengers"][0]["ketQua"] = tk()
CL.ghi(d)
r = CL.duyet(k)
d = CL.doc()
if r["ok"] and d["champion"]["ma"] == "MOCK_RANGE_V1" and d["champion"]["phienBan"] == 2:
    ok(f"champion đổi {cu} → {d['champion']['ma']}, bản {d['champion']['phienBan']}")
else:
    bao(f"duyệt xong mà champion vẫn là {d['champion']['ma']}")
if d["lichSu"] and d["lichSu"][-1]["thay"] == cu:
    ok("có ghi lịch sử thay ngôi — truy lại được lệnh nào chạy bằng bản nào")
else:
    bao("không ghi lịch sử thay ngôi")
if not d["challengers"]:
    ok("challenger đã lên thì rời khỏi danh sách chờ")
else:
    bao("challenger vẫn nằm trong danh sách sau khi lên champion")

print("\n[7] bài học chạy lại KHÔNG được trộn vào bài học thật")
gia = {
    "symbol": "BTCUSDT",
    "lenh": [{"i": i, "t": 0, "side": "LONG", "entry": 100, "sl": 98, "tp": 104,
              "exit": 104, "lyDo": "TP", "soNenGiu": 5, "pnl": 4, "R": 1.5,
              "regime": "TREND_UP", "regimeKey": "TREND_UP|none", "rr": 2, "von": 100}
             for i in range(30)],
    "thongKe": {"so": 30, "kyVongR": 1.5},
    "theoRegime": {"TREND_UP|none": {"so": 30, "thang": 30, "tyLeThang": 100.0,
                                     "trungBinhR": 1.5, "tongR": 45}},
}
B.duc(gia)
that = store.read_all(store.LESSONS)
cl = store.read_all(store.LESSONS_CHAY_LAI)
if not that and cl:
    ok(f"{len(cl)} bài học vào kho riêng, kho thật vẫn trống")
else:
    bao(f"kho thật có {len(that)} bản ghi — đã bị trộn")

m = recall("TREND_UP|none", "TREND_UP")
if "lessonsFromReplay" in m and "replayNote" in m:
    ok("recall() tách hai kho và có nhãn cảnh báo cho phần mô phỏng")
else:
    bao("recall() không tách hai kho")
if m["lessonsForThisRegime"] == []:
    ok("phần 'bài học thật' vẫn rỗng — đúng, vì chưa có lệnh thật nào")
else:
    bao("phần 'bài học thật' có nội dung từ đâu ra")

print("\n[8] đúc hai lần không được nhân đôi trí nhớ")
n1 = len(store.read_all(store.LESSONS_CHAY_LAI))
B.duc(gia)
n2 = len(store.read_all(store.LESSONS_CHAY_LAI))
ok(f"vẫn {n2} bản ghi") if n1 == n2 else bao(f"{n1} → {n2}, đang nối thêm thay vì ghi đè")

print("\n[9] sổ append-only phải từ chối bị ghi đè")
for kho in (store.TRADES, store.LESSONS, store.THESES):
    try:
        store.write_all(kho, [])
        bao(f"{kho} cho ghi đè — lịch sử có thể bị xoá sạch")
    except ValueError:
        ok(f"{kho} từ chối ghi đè")

print("\n" + "=" * 58)
if sai:
    print(f"  {sai} phép kiểm hỏng.")
    sys.exit(1)
print("  CỬA DUYỆT KHÔNG CÓ ĐƯỜNG LỌT.")
print("=" * 58)
