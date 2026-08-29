"""ĐẤU CHIẾN LƯỢC — đưa một bộ luật ra đấu với champion trên đoạn NGOÀI MẪU.

    python scripts/dau-chien-luoc.py MOCK_KEO_LUI_V1 "Chờ kéo lùi"
    python scripts/dau-chien-luoc.py --tat-ca      đấu mọi bộ luật chưa phải champion
    python scripts/dau-chien-luoc.py --tat-ca --cho BTCUSDT:1h,ETHUSDT:1h,SOLUSDT:1h
    python scripts/dau-chien-luoc.py --tat-ca --cho BTCUSDT:4h,BTCUSDT:1d

Đi đúng đường mà buồng lái đi: `chien_luoc.de_xuat` → `chien_luoc.danh_gia` →
cửa duyệt `phan_quyet`. Không có đường tắt nào ở đây, và cố ý không có tham số
`--duyet`: cho một chiến lược lên chạy bằng tiền là việc phải bấm tay ở buồng
lái sau khi đã đọc phán quyết.

VÌ SAO CẦN

Đo được cho tới lúc này: chiến lược cầm quyền có kỳ vọng **−0,666R qua 44 lệnh**
chạy lại, 77% lệnh chết ở stop. Cầu dao chế độ chặn được chỗ lỗ nặng nhất, nhưng
chặn không làm cho một chiến lược lỗ thành có lợi thế. Việc còn lại chỉ có thể
làm bằng cách đem một chiến lược KHÁC ra đo trên cùng đoạn dữ liệu — không phải
bằng cách chỉnh tham số của chính nó, vì tham số chỉ xoay quanh cùng một giả
thuyết đã được chứng minh là sai.

VÌ SAO ĐẤU TRÊN NHIỀU CHỢ (`--cho`)

Mọi con số của hệ này từng đứng trên MỘT tài sản, MỘT khung. Một chiến lược ăn
được ở BTC 1h mà chết ở ETH và SOL không phải chiến lược có lợi thế — nó là một
bộ tham số khớp với lịch sử BTC. Đấu trên nhiều chợ biến chuyện đó thành thứ
nhìn thấy được ngay trong bảng, thay vì phát hiện ra sau khi đã chạy bằng tiền.

Mỗi chợ được đo RIÊNG rồi mới gộp: gộp lệnh của ba coin thành một rổ là để coin
nhiều lệnh nhất quyết định hộ, và một coin thắng đậm che được hai coin thua.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import chien_luoc, huanluyen as HL  # noqa: E402
from trader.brain import BO_LUAT  # noqa: E402
from trader.config import CONFIG  # noqa: E402

TEN_MAC_DINH = {
    "MOCK_RULES_V1": "Thuận xu hướng",
    "MOCK_RANGE_V1": "Mua đáy biên",
    "MOCK_KEO_LUI_V1": "Chờ kéo lùi",
    "MOCK_BUNG_NEN_V1": "Bung nén",
}


def _chay_factory(nen, chuoi, moc, symbol):
    def chay(ma: str, th: dict) -> dict:
        trong = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi, bo_luat=ma,
                            tham=th, tu_nen=0, den_nen=moc, bo_qua_kill=True)
        ngoai = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi, bo_luat=ma,
                            tham=th, tu_nen=moc, bo_qua_kill=True)
        tk = dict(ngoai["thongKe"])
        tr = trong["thongKe"]["kyVongR"]
        tk["khopTroi"] = (round(tr - tk["kyVongR"], 3)
                          if (tr is not None and tk["kyVongR"] is not None) else None)
        tk["trongMau"] = trong["thongKe"]
        tk["boLuat"] = ma
        return tk
    return chay


def _nap_cho(sym: str, chinh: str, ctx: str):
    """Nạp một CHỢ = (coin, khung chính, khung ngữ cảnh).

    Phải ghi đè `CONFIG["timeframes"]` vì `huanluyen.nap_nen` và `_van_tay` đọc
    thẳng từ đó. Vân tay có kèm khung, nên mỗi chợ có cache chuỗi riêng và không
    lẫn sang nhau — chỗ này mà sai thì kết quả của ETH sẽ là chuỗi của BTC, trả
    về trong một giây và trông rất hợp lý.
    """
    import datetime as _dt
    import json as _json
    from trader.config import ROOT as _ROOT

    kho = _ROOT / "data" / "lich-su"
    nen = {}
    for tf in (chinh, ctx):
        f = kho / f"{sym}-{tf}.json"
        if not f.exists():
            return None
        nen[tf] = _json.loads(f.read_text(encoding="utf-8"))
    CONFIG["timeframes"]["primary"] = chinh
    CONFIG["timeframes"]["context"] = ctx
    return nen


# Khung ngữ cảnh mặc định cho mỗi khung chính — luôn là khung dài hơn một bậc.
NGU_CANH = {"5m": "30m", "15m": "1h", "30m": "4h", "1h": "4h", "4h": "1d", "1d": "1d"}


def dau_nhieu_cho(cho: list[str], ma_ds: list[tuple]) -> None:
    """Đấu từng bộ luật trên từng chợ, in bảng gộp. KHÔNG ghi vào sổ chiến lược.

    Cố ý không ghi: sổ chiến lược có đúng một champion, mà champion chỉ có nghĩa
    trên chợ nó đang chạy. Ghi kết quả đa chợ vào đó là trộn hai khái niệm.
    """
    bang: dict = {}
    for ten_cho in cho:
        sym, _, chinh = ten_cho.partition(":")
        chinh = chinh or CONFIG["timeframes"]["primary"]
        ctx = NGU_CANH.get(chinh, "4h")
        nen = _nap_cho(sym, chinh, ctx)
        if nen is None:
            print(f"  bỏ qua {ten_cho} — chưa tải nến {chinh}/{ctx}")
            continue
        moc = int(len(nen[chinh]) * 0.7)
        chuoi, tu_dau = HL.lay_chuoi(nen, sym)
        print(f"  {ten_cho} (ngữ cảnh {ctx}) · {len(nen[chinh])} nến · "
              f"chuỗi {len(chuoi)} điểm ({tu_dau})")
        chay = _chay_factory(nen, chuoi, moc, sym)
        for ma, _ in ma_ds:
            if ma not in BO_LUAT:
                continue
            tk = chay(ma, {})
            bang.setdefault(ma, {})[ten_cho] = tk

    if not bang:
        print("  không chợ nào đo được")
        return
    print()
    cot = [c for c in cho if any(c in v for v in bang.values())]
    print(f"{'bộ luật':20}" + "".join(f"{c:>20}" for c in cot) + f"{'thắng mấy chợ':>16}")
    print("─" * (20 + 20 * len(cot) + 16))
    for ma, v in bang.items():
        dong, duong = "", 0
        for c in cot:
            tk = v.get(c)
            if not tk or tk.get("kyVongR") is None:
                dong += f"{'—':>20}"
                continue
            duong += 1 if tk["kyVongR"] > 0 else 0
            dong += f"{tk['kyVongR']:>+13.3f}/{tk['so']:<6}"
        print(f"{ma:20}{dong}{f'{duong}/{len(cot)}':>16}")
    print()
    print("Mỗi ô: kỳ vọng R ngoài mẫu / số lệnh ngoài mẫu.")
    print("Một bộ luật chỉ đáng tin khi DƯƠNG ở nhiều chợ — dương ở đúng một chợ")
    print("là dấu hiệu khớp với lịch sử của riêng chợ đó.")

    # Ghi ra đĩa để lò chưng cất đọc được. Không ghi thì bảng này chỉ tồn tại
    # trong terminal của lượt chạy đó — đúng chỗ đứt mà cả hệ đã sửa một lần.
    from trader.config import DATA_DIR as _DD
    import datetime as _dt
    import json as _json
    _f = _DD / "dau-nhieu-cho.json"
    # `luc` không phải trang trí. Bàn giao đo tuổi kho bằng mtime của file, mà
    # mtime nói "lần ghi cuối", không nói "đo trên dữ liệu tới lúc nào". Một
    # lượt chạy hỏng nửa chừng vẫn chạm file và làm kho trông tươi. Số nến thì
    # nói cỡ mẫu — thiếu nó, "+0,4R" đọc giống nhau ở n=3 và n=300.
    _f.write_text(_json.dumps({
        "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "cho": cot,
        "ket": {ma: {c: {"kyVongR": v[c].get("kyVongR"), "so": v[c].get("so"),
                         "tyLeThang": v[c].get("tyLeThang"),
                         "khopTroi": v[c].get("khopTroi")}
                     for c in cot if c in v}
                for ma, v in bang.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"đã ghi {_f.name}")


def _in(nhan: str, tk: dict) -> None:
    lt = tk.get("theoLyDoThoat") or {}
    tong = sum(lt.values()) or 1
    tm = tk.get("trongMau") or {}
    print(f"  {nhan}")
    print(f"    trong mẫu : {tm.get('so', '—'):>3} lệnh · kỳ vọng {tm.get('kyVongR')}R"
          f" · thắng {tm.get('tyLeThang')}%")
    print(f"    NGOÀI MẪU : {tk.get('so', 0):>3} lệnh · kỳ vọng {tk.get('kyVongR')}R"
          f" · thắng {tk.get('tyLeThang')}% · sụt giảm {tk.get('sutGiamToiDaPct')}%")
    print(f"    khớp trội {tk.get('khopTroi')} · chuỗi thua {tk.get('chuoiThuaDaiNhat')}"
          f" · SL {lt.get('SL', 0)}/{tong} ({lt.get('SL', 0) / tong * 100:.0f}% chết ở stop)"
          f" · TP {lt.get('TP', 0)}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tat_ca = "--tat-ca" in sys.argv

    if "--cho" in sys.argv:
        cho = [x.strip() for x in sys.argv[sys.argv.index("--cho") + 1].split(",") if x.strip()]
        d0 = chien_luoc.doc()
        ds0 = ([(m, TEN_MAC_DINH.get(m, m)) for m in BO_LUAT] if tat_ca
               else [(args[0], "")] if args else [])
        if not ds0:
            print(__doc__)
            return 2
        print(f"ĐẤU NHIỀU CHỢ · champion hiện tại {d0['champion']['ma']}\n")
        dau_nhieu_cho(cho, ds0)
        return 0

    nen = HL.nap_nen()
    if nen is None:
        print("Chưa có nến lịch sử. Chạy: python scripts/tai-lich-su.py --so 4000")
        return 1
    tf = CONFIG["timeframes"]["primary"]
    moc = int(len(nen[tf]) * 0.7)
    chuoi, tu_dau = HL.lay_chuoi(nen, "BTCUSDT")
    print(f"{len(nen[tf])} nến {tf} · mốc chia {moc} (70/30) · chuỗi {len(chuoi)} điểm ({tu_dau})\n")

    d = chien_luoc.doc()
    cha_ma = d["champion"]["ma"]
    if tat_ca:
        ds = [(m, TEN_MAC_DINH.get(m, m)) for m in BO_LUAT if m != cha_ma]
    elif args:
        ds = [(args[0], args[1] if len(args) > 1 else TEN_MAC_DINH.get(args[0], args[0]))]
    else:
        print(__doc__)
        return 2

    chay = _chay_factory(nen, chuoi, moc, "BTCUSDT")
    print(f"champion hiện tại: {cha_ma}\n")

    for ma, ten in ds:
        if ma not in BO_LUAT:
            print(f"  bỏ qua «{ma}» — không có trong BO_LUAT")
            continue
        dx = chien_luoc.de_xuat(ma, ten, {}, "đấu tự động")
        khoa = dx.get("khoa") or f"{ma}#mặc-định"
        kq = chien_luoc.danh_gia(khoa, chay)
        if not kq.get("ok"):
            print(f"  {ma}: không đo được — {kq.get('viSao')}")
            continue

        print(f"── {ma} · «{ten}»")
        _in("champion " + cha_ma, kq["champion"])
        _in("thách đấu " + ma, kq["challenger"])
        pq = kq["phanQuyet"]
        print(f"    ⇒ {pq['tomTat']}")
        for l in pq["lyDo"]:
            print(f"       × {l}")
        print()

    print("Không có gì được đưa lên champion — việc đó bấm tay ở buồng lái, "
          "sau khi đã đọc phán quyết.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
