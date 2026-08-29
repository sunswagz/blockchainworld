"""ĐO MẪU GIÁ — mỗi mẫu kinh điển thật sự đáng bao nhiêu trên chính thị trường này.

    python scripts/do-mau-gia.py            đo trên khung đang cấu hình
    python scripts/do-mau-gia.py --ghi      đo xong ghi vào data/mau-gia.json
    python scripts/do-mau-gia.py --cho BTCUSDT:4h,ETHUSDT:4h,SOLUSDT:4h --ghi

Sách vở nói "vai-đầu-vai đúng 83%". Câu đó không có cỡ mẫu, không có sàn, không
có khung thời gian, không nói đúng tới ĐÂU và sai thì mất bao nhiêu. Script này
thay nó bằng số đo trên đúng cây nến mà bot sẽ giao dịch.

CÁCH CHẤM

Mỗi mẫu tự khai điểm vào, stop và mục tiêu. Chạy tới trước từ nến xác nhận:
chạm mục tiêu trước ⇒ +RR của mẫu; chạm stop trước ⇒ −1R; hết cửa sổ ⇒ chấm
theo giá đóng. Phí và trượt giá trừ ở cả hai đầu, y như bản chạy thật — bỏ
chúng ra thì mọi mẫu đều đẹp hơn thực tế đúng một khoảng bằng nhau, và thứ tự
xếp hạng vẫn sai vì mẫu có stop hẹp chịu thiệt nặng hơn.

BA CHỖ DỄ TỰ LỪA, ĐÃ CHẶN

**1. Đếm trùng.** Một hình vai-đầu-vai giữ nguyên qua 10 nến sẽ được nhận diện
10 lần. Không gộp lại thì một mẫu duy nhất thành 10 mẫu và cỡ mẫu phồng lên gấp
mười. Ở đây hai lần cùng tên phải cách nhau ít nhất `CACH_NHAU` nến.

**2. Mẫu chưa xác nhận.** `mau_gia.py` chỉ trả mẫu đã phá mức xác nhận. Nếu
nhận diện cả mẫu "đang hình thành" thì đang chấm điểm chính cái mình vẽ ra.

**3. Kết luận trên cỡ mẫu nhỏ.** Dưới `TOI_THIEU` lần xuất hiện thì in ra
nhưng ghi rõ CHƯA ĐỦ, và lò chưng cất sẽ không lấy.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import mau_gia  # noqa: E402
from trader.config import CONFIG, DATA_DIR, ROOT  # noqa: E402

NL = chr(10)
GHI = "--ghi" in sys.argv
CUA_SO = 120        # nến quá khứ đưa cho bộ nhận diện
GIU = 48            # nến tối đa giữ một lệnh, giống bản chạy thật
CACH_NHAU = 12      # hai lần cùng tên phải cách nhau ngần này nến
TOI_THIEU = 15      # dưới ngần này lần xuất hiện thì chưa kết luận


def _cho_ds() -> list[str]:
    """Danh sách chợ cần đo, dạng SYMBOL:khung.

    Mặc định là chợ trong cấu hình. `--cho` mở ra nhiều chợ, và đó là cách DUY
    NHẤT để mấy mẫu hiếm nói được gì: `CỐC_TAY_CẦM` xuất hiện 12 lần trên 3000
    nến BTC — dưới ngưỡng 15 nên vĩnh viễn "chưa đủ dữ liệu", mà đo thêm 10 năm
    BTC cũng chỉ nhích chút. Trải qua 15 chợ thì thành 150+, và 15 chợ độc lập
    còn khó khớp trội hơn một chợ dài.
    """
    if "--cho" in sys.argv:
        return [x.strip() for x in sys.argv[sys.argv.index("--cho") + 1].split(",")
                if x.strip()]
    return [f"{CONFIG['symbol']}:{CONFIG['timeframes']['primary']}"]


def _nap(cho: str | None = None) -> list[dict]:
    # Khung VÀ chợ đều phải theo dữ liệu, không ghi cứng. Bản đầu cố định "1h";
    # khi bản chạy thật sang 4h thì bảng mẫu giá vẫn nói về 1h mà không gì lộ ra.
    # Bản sau vẫn ghi cứng "BTCUSDT" — cùng lỗi, chỉ đổi trục.
    cho = cho or _cho_ds()[0]
    sym, _, tf = cho.partition(":")
    tf = tf or CONFIG["timeframes"]["primary"]
    f = ROOT / "data" / "lich-su" / f"{sym}-{tf}.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("candles") or d.get("nen") or next(iter(d.values()))
    return d


def _cham(nen: list[dict], m: dict, i: int, drag_bps: float) -> dict | None:
    """Chạy tới trước từ nến xác nhận, xem stop hay mục tiêu tới trước."""
    vao, stop, dich = m["vao"], m["stop"], m["mucTieu"]
    rui = abs(vao - stop)
    if not rui:
        return None
    long = m["huong"] == "LONG"
    drag = vao * drag_bps / 10_000
    # Chi phí trừ ở cả hai đầu: vào bị trượt bất lợi, ra cũng vậy.
    vao_that = vao + drag if long else vao - drag
    rui_that = abs(vao_that - stop)
    if not rui_that:
        return None

    # Cùng một lượt đi tới trước, chấm SONG SONG nhiều luật thoát:
    #
    #   "mẫu"  mục tiêu do chính mẫu khai (measured move kinh điển)
    #   1.0R · 1.5R · 2.0R   mục tiêu CỐ ĐỊNH, dùng đúng stop của mẫu
    #
    # Tách ra mới trả lời được câu hỏi đúng. Một mẫu lỗ có thể vì hình học của
    # nó không đoán được gì, HOẶC vì luật đặt mục tiêu kinh điển đặt đích gần
    # hơn cả stop của chính nó. Hai chuyện đó cần hai cách sửa khác hẳn nhau,
    # và gộp lại thì chỉ biết "mẫu này lỗ" — câu không dùng được vào việc gì.
    co_dinh = (1.0, 1.5, 2.0)
    xong = {}
    mfe = 0.0
    for k, c in enumerate(nen[i + 1: i + 1 + GIU], start=1):
        if long:
            mfe = max(mfe, (c["h"] - vao_that) / rui_that)
            dinh_stop = c["l"] <= stop
            cham_mau = c["h"] >= dich
            r_mau = (dich - drag - vao_that) / rui_that
        else:
            mfe = max(mfe, (vao_that - c["l"]) / rui_that)
            dinh_stop = c["h"] >= stop
            cham_mau = c["l"] <= dich
            r_mau = (vao_that - dich - drag) / rui_that

        for muc in co_dinh:
            if muc in xong:
                continue
            if dinh_stop and mfe < muc:
                xong[muc] = -1.0
            elif mfe >= muc:
                xong[muc] = muc - (drag / rui_that)
        if "mau" not in xong:
            if dinh_stop and not cham_mau:
                xong["mau"] = (-1.0, k, "STOP")
            elif cham_mau:
                xong["mau"] = (r_mau, k, "ĐÍCH")
        if len(xong) == len(co_dinh) + 1:
            break

    if "mau" not in xong:
        cuoi = nen[min(i + GIU, len(nen) - 1)]["c"]
        r = ((cuoi - drag - vao_that) if long else (vao_that - cuoi - drag)) / rui_that
        xong["mau"] = (r, GIU, "HẾT_HẠN")
    for muc in co_dinh:
        xong.setdefault(muc, -1.0 if mfe < muc else muc)

    r, k, ly = xong["mau"]
    return {"R": r, "nen": k, "ly": ly, "mfe": mfe,
            "coDinh": {str(m): xong[m] for m in co_dinh}}


def main() -> int:
    r = CONFIG["risk"]
    drag_bps = r["feeBps"] + r["slippageBps"]
    cho_ds = _cho_ds()

    ket: dict[str, list] = defaultdict(list)
    bo_trung = 0
    da_do: list[str] = []
    tong_nen = 0

    for cho in cho_ds:
        nen = _nap(cho)
        if len(nen) < CUA_SO + GIU + 10:
            print(f"  bỏ qua {cho} — chưa đủ nến lịch sử")
            continue
        da_do.append(cho)
        tong_nen += len(nen)
        print(f"  {cho} · {len(nen)} nến")

        # `lan_cuoi` phải đặt lại MỖI CHỢ. Dùng chung thì chỉ số nến của chợ sau
        # bị so với chỉ số của chợ trước, và luật "hai lần cùng tên phải cách
        # nhau 12 nến" loại bừa những lần xuất hiện hoàn toàn hợp lệ.
        lan_cuoi: dict[str, int] = {}
        for i in range(CUA_SO, len(nen) - GIU - 1):
            for m in mau_gia.nhan_dien(nen[i - CUA_SO: i + 1]):
                ten = m["ten"]
                if i - lan_cuoi.get(ten, -10 ** 9) < CACH_NHAU:
                    bo_trung += 1
                    continue
                o = _cham(nen, m, i, drag_bps)
                if o is None:
                    continue
                lan_cuoi[ten] = i
                ket[ten].append({**o, "rr": m["rr"], "loai": m["loai"],
                                 "huong": m["huong"], "cho": cho})

    if not da_do:
        print("Chưa đủ nến lịch sử. Chạy: python scripts/tai-lich-su.py --so 4000")
        return 1
    print(f"{chr(10)}{len(da_do)} chợ · {tong_nen} nến · cửa sổ {CUA_SO} · giữ tối đa "
          f"{GIU} nến · chi phí {drag_bps}bps mỗi đầu{chr(10)}")

    if not ket:
        print("Không nhận diện được mẫu nào — kiểm lại dung sai trong mau_gia.py")
        return 1

    hang = []
    for ten, ds in ket.items():
        n = len(ds)
        rs = [x["R"] for x in ds]
        kv = sum(rs) / n
        thang = sum(1 for x in rs if x > 0)
        dich = sum(1 for x in ds if x["ly"] == "ĐÍCH")
        stop = sum(1 for x in ds if x["ly"] == "STOP")
        mfe = sorted(x["mfe"] for x in ds)
        cd = {}
        for m in ("1.0", "1.5", "2.0"):
            xs = [x["coDinh"][m] for x in ds if x.get("coDinh") and m in x["coDinh"]]
            cd[m] = round(sum(xs) / len(xs), 3) if xs else None
        hang.append({
            "coDinh": cd,
            "ten": ten, "loai": ds[0]["loai"], "so": n,
            "kyVongR": round(kv, 3),
            "tyLeThang": round(thang / n * 100, 1),
            "chamDich": round(dich / n * 100, 1),
            "dinhStop": round(stop / n * 100, 1),
            "rrTrungBinh": round(sum(x["rr"] or 0 for x in ds) / n, 2),
            "mfeTrungVi": round(mfe[n // 2], 2),
            "nenTrungBinh": round(sum(x["nen"] for x in ds) / n, 1),
            "duMau": n >= TOI_THIEU,
        })

    hang.sort(key=lambda x: (-x["so"] if not x["duMau"] else 0, -x["kyVongR"]))
    print(f"{'mẫu':22}{'n':>5}{'mục tiêu MẪU':>14}{'RR':>6}{'thắng':>8}"
          f"{'MFE giữa':>10}   mục tiêu CỐ ĐỊNH: 1.0R    1.5R    2.0R")
    print("─" * 108)
    for h in hang:
        sao = "  ← CHƯA ĐỦ MẪU" if not h["duMau"] else ""
        cd = h["coDinh"]
        c1 = f"{cd['1.0']:+.3f}" if cd.get("1.0") is not None else "   —  "
        c15 = f"{cd['1.5']:+.3f}" if cd.get("1.5") is not None else "   —  "
        c2 = f"{cd['2.0']:+.3f}" if cd.get("2.0") is not None else "   —  "
        print(f"{h['ten']:22}{h['so']:>5}{h['kyVongR']:>+14.3f}{h['rrTrungBinh']:>6.2f}"
              f"{h['tyLeThang']:>7.1f}%{h['mfeTrungVi']:>10.2f}"
              f"{c1:>22}{c15:>8}{c2:>8}{sao}")

    du = [h for h in hang if h["duMau"]]
    print(f"\n{len(hang)} mẫu nhận diện được · {len(du)} mẫu đủ cỡ mẫu (≥{TOI_THIEU}) · "
          f"bỏ {bo_trung} lần nhận diện trùng trong {CACH_NHAU} nến")
    if du:
        tot = max(du, key=lambda h: h["kyVongR"])
        xau = min(du, key=lambda h: h["kyVongR"])
        print(f"tốt nhất {tot['ten']} {tot['kyVongR']:+.3f}R · "
              f"tệ nhất {xau['ten']} {xau['kyVongR']:+.3f}R")
        duong = [h for h in du if h["kyVongR"] > 0]
        print(f"{len(duong)}/{len(du)} mẫu đủ mẫu có kỳ vọng DƯƠNG sau phí")

    # BỘ DÒ HỎNG phải hiện ra ở đây, không nằm im trong bộ nhớ.
    #
    # Một bộ dò ném lỗi cho ra 0 lần xuất hiện, và "0 lần" đọc y hệt "mẫu này
    # hiếm": bảng vẫn đủ dòng, vẫn có cỡ mẫu, vẫn xanh. Với 22.997 lần xuất hiện
    # trên 15 chợ, đây là nguồn bằng chứng lớn thứ hai của cả hệ.
    if mau_gia.LOI_DO:
        print(f"{NL}⚠ BỘ DÒ NÉM LỖI — những mẫu này đang bị đếm THIẾU:")
        for ten, so in sorted(mau_gia.LOI_DO.items(), key=lambda x: -x[1]):
            print(f"    {ten:22} {so:>7} lần · ví dụ: {mau_gia.LOI_DO_VIDU.get(ten)}")
    else:
        print(f"{NL}không bộ dò nào ném lỗi trong lượt này.")

    if GHI:
        f = DATA_DIR / "mau-gia.json"
        # `luc` từng là None ghi cứng: khoá có mặt nên phép canh "kho phải đóng
        # dấu" cho qua, mà giá trị thì vô dụng. Khai một trường rồi để trống còn
        # tệ hơn không khai — nó làm phép canh báo xanh.
        f.write_text(json.dumps({
            "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "cho": da_do, "khung": CONFIG["timeframes"]["primary"],
            "nen": tong_nen, "cuaSo": CUA_SO,
            "giu": GIU, "toiThieu": TOI_THIEU, "mau": hang,
            "loiDo": dict(mau_gia.LOI_DO)},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nđã ghi {f}")
    else:
        print("\n(chưa ghi — thêm --ghi để lưu cho lò chưng cất)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
