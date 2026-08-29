"""ĐẤU CHIẾN LƯỢC — đưa một bộ luật ra đấu với champion trên đoạn NGOÀI MẪU.

    python scripts/dau-chien-luoc.py MOCK_KEO_LUI_V1 "Chờ kéo lùi"
    python scripts/dau-chien-luoc.py --tat-ca      đấu mọi bộ luật chưa phải champion
    python scripts/dau-chien-luoc.py --tat-ca --cho BTCUSDT:1h,ETHUSDT:1h,SOLUSDT:1h
    python scripts/dau-chien-luoc.py --tat-ca --cho BTCUSDT:4h,BTCUSDT:1d
    python scripts/dau-chien-luoc.py --tat-ca --cho <ds> --truoc 2025-06-01

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
from trader import data as DATA  # noqa: E402
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
        # NỬA CHẠY ĐƯỢC. Bảng chính đo CẢ HAI CHIỀU, còn sàn spot chỉ bán được
        # thứ đang giữ — `risk.py` chặn SHORT khi `spot_only`. Đo được ngày
        # 30/08: MOCK_KEO_LUI_V1 trên 33 chợ 1d chưa từng dùng cho +0,205R gộp
        # 269 lệnh, khoảng tin KHÔNG chứa 0 — mà tách ra thì SHORT 226 lệnh
        # +0,303R còn LONG 44 lệnh −0,306R. Toàn bộ lợi thế nằm ở nửa bot không
        # đánh được, và cửa duyệt champion đang đọc con số gộp ấy.
        #
        # `cheDoVao: [TREND_UP]` là cách `do-huong.py` cô lập nửa LONG. Không
        # phải mô phỏng y hệt tầng rủi ro, nhưng cùng một quy ước, và có một
        # con số còn hơn không có gì để so.
        chi_long = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi, bo_luat=ma,
                               tham={**th, "cheDoVao": ["TREND_UP"]},
                               tu_nen=moc, bo_qua_kill=True)["thongKe"]
        tk["chiLong"] = {"kyVongR": chi_long["kyVongR"], "so": chi_long["so"]}
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

    # `--truoc <YYYY-MM-DD>`: chỉ giữ nến ĐÓNG TRƯỚC mốc đó.
    #
    # Vì sao cần: bộ máy chỉ có MỘT cửa sổ ngoài mẫu — 30% cuối của chuỗi — và
    # 15 chợ đều dùng chung đúng khoảng thời gian ấy. Crypto tương quan cao,
    # nên "dương ở 11/15 chợ" có thể chỉ là "450 ngày vừa rồi thuận xu hướng"
    # nói mười lăm lần. Cắt mốc là cách dựng một cửa sổ ngoài mẫu KHÁC, ở một
    # quãng thị trường khác, mà không cần tải lại gì.
    #
    # Cắt theo THỜI GIAN chứ không theo số nến: khung chính và khung ngữ cảnh
    # có mật độ khác nhau, nên cắt 70% số nến của mỗi bên là lệch nhau, và
    # khung ngữ cảnh sẽ nhìn thấy tương lai của khung chính.
    # CHỢ CHẾT: đủ nến nhưng nến cuối đã cũ. MKRUSDT có tròn 1500 nến 1d và
    # ngừng ngày 15/09/2025 (đổi tên sang SKY). Nó qua mọi phép đếm, rồi đóng
    # góp một cửa sổ "ngoài mẫu" kết thúc từ một năm trước vào bảng gộp — cùng
    # đúng loại lỗi vừa mắc giữa 4h và 1d, chỉ đổi trục sang coin.
    #
    # Bỏ qua khi mốc cắt đuôi KHÔNG được đặt: có `--truoc` thì cũ là chuyện
    # đương nhiên, chính người gọi vừa yêu cầu điều đó.
    if TRUOC is None:
        _cu_ngay = DATA.qua_cu(nen[chinh], chinh)
        if _cu_ngay is not None:
            print(f"    ⚠ {sym}:{chinh} — nến cuối cách đây {_cu_ngay:.0f} ngày "
                  f"(chợ chết hoặc đổi tên). BỎ QUA: cửa sổ ngoài mẫu của nó "
                  f"kết thúc ở một thời điểm khác hẳn mọi chợ còn lại.")
            return None

    # `--tu` cắt ĐẦU chuỗi, `--truoc` cắt ĐUÔI. Cần cả hai để ép mọi chợ về
    # CÙNG một cửa sổ lịch.
    #
    # Vì sao cần: mỗi chợ tự lấy 30% cuối CỦA RIÊNG NÓ làm ngoài mẫu. Một coin
    # có 1499 ngày dữ liệu thì ngoài mẫu là 450 ngày cuối; một coin lên sàn năm
    # ngoái, 400 ngày dữ liệu, thì ngoài mẫu là 120 ngày cuối. Gộp hai con số ấy
    # lại là gộp hai quãng thời gian khác nhau — đúng lỗi vừa mắc giữa 4h và 1d,
    # chỉ đổi trục từ khung sang coin. Mở rộng ra coin mới làm nó nặng thêm.
    for moc, giu in ((TRUOC, lambda t: t < TRUOC), (TU, lambda t: t >= TU)):
        if moc is None:
            continue
        for tf in list(nen):
            nen[tf] = [x for x in nen[tf] if giu(x.get("t") or 0)]
            if len(nen[tf]) < 300:
                return None

    CONFIG["timeframes"]["primary"] = chinh
    CONFIG["timeframes"]["context"] = ctx
    return nen


# Khung ngữ cảnh mặc định cho mỗi khung chính — luôn là khung dài hơn một bậc.
NGU_CANH = {"5m": "30m", "15m": "1h", "30m": "4h", "1h": "4h", "4h": "1d", "1d": "1d"}

# Mốc cắt (ms). None = dùng cả chuỗi.
def _moc_truoc():
    if "--truoc" not in sys.argv:
        return None
    import datetime as _d
    x = sys.argv[sys.argv.index("--truoc") + 1]
    return int(_d.datetime.fromisoformat(x)
               .replace(tzinfo=_d.timezone.utc).timestamp() * 1000)


def _moc(co: str):
    if co not in sys.argv:
        return None
    import datetime as _d
    x = sys.argv[sys.argv.index(co) + 1]
    return int(_d.datetime.fromisoformat(x)
               .replace(tzinfo=_d.timezone.utc).timestamp() * 1000)


TRUOC = _moc_truoc()
TU = _moc("--tu")



def dau_nhieu_cho(cho: list[str], ma_ds: list[tuple]) -> None:
    """Đấu từng bộ luật trên từng chợ, in bảng gộp. KHÔNG ghi vào sổ chiến lược.

    Cố ý không ghi: sổ chiến lược có đúng một champion, mà champion chỉ có nghĩa
    trên chợ nó đang chạy. Ghi kết quả đa chợ vào đó là trộn hai khái niệm.
    """
    bang: dict = {}
    quang: list[tuple[int, int]] = []
    soNen: list[int] = []
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
        # Quãng THỜI GIAN của chợ này, gom lại để bảng tự khai.
        _t = [x.get("t") for x in nen[chinh] if x.get("t")]
        if _t:
            quang.append((min(_t), max(_t)))
            soNen.append(len(nen[chinh]))
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
    print(f"{'nửa CHẠY ĐƯỢC (chỉ LONG)':20}" + "".join(
        f"{'—':>20}" for _ in cot) + f"{'gộp':>16}")
    for ma, v in bang.items():
        dong, ds = "", []
        for c in cot:
            cl = (v.get(c) or {}).get("chiLong") or {}
            if cl.get("kyVongR") is None or not cl.get("so"):
                dong += f"{'—':>20}"
                continue
            ds.append((cl["kyVongR"], cl["so"]))
            dong += f"{cl['kyVongR']:>+13.3f}/{cl['so']:<6}"
        _n = sum(n for _, n in ds)
        _g = f"{sum(r * n for r, n in ds) / _n:+.3f}" if _n else "—"
        print(f"{ma:20}{dong}{_g:>16}")
    print()
    print("Mỗi ô: kỳ vọng R ngoài mẫu / số lệnh ngoài mẫu.")
    print("Một bộ luật chỉ đáng tin khi DƯƠNG ở nhiều chợ — dương ở đúng một chợ")
    print("là dấu hiệu khớp với lịch sử của riêng chợ đó.")

    # Ghi ra đĩa để lò chưng cất đọc được. Không ghi thì bảng này chỉ tồn tại
    # trong terminal của lượt chạy đó — đúng chỗ đứt mà cả hệ đã sửa một lần.
    from trader.config import DATA_DIR as _DD
    import datetime as _dt
    import json as _json

    # AI ĐƯỢC GHI VÀO KHO CHÍNH THỨC
    #
    # Kho này là bằng-chứng-nhiều-chợ mà lò chưng cất đọc và cửa duyệt champion
    # tra vào. Lượt gõ tay với danh sách chợ tự chọn KHÔNG được thành bằng chứng
    # chính thức chỉ vì nó chạy sau.
    #
    # Đã xảy ra hôm nay: một lượt đo 33 chợ 1d gõ tay đè lên kho, và từ đó mọi
    # câu "dương ở ≥3 chợ" của lò chưng cất nói về một tập chợ khác hẳn tập mà
    # nghi thức khai. Không sai một con số nào, và nói về một hệ khác.
    #
    # Chú thích cũ ở đây đã lường trước chuyện hai lượt cùng ghi một file —
    # nhưng chỉ lo NGUYÊN TỬ, tức lo file cụt. Vấn đề thật không phải file cụt.
    from trader import nghi_thuc as _NT
    _chinh_thuc = {tuple(x.strip() for x in _NT.CHO_4H.split(",")),
                   tuple(x.strip() for x in _NT.CHO_1D.split(","))}
    _la_nghi_thuc = tuple(cot) in _chinh_thuc
    _f = _DD / ("dau-nhieu-cho.json" if _la_nghi_thuc else "dau-nhieu-cho-ngoai.json")
    if not _la_nghi_thuc:
        print(f"  ⓘ danh sách chợ KHÔNG phải của nghi thức ({len(cot)} chợ) — "
              f"ghi sang {_f.name}, kho chính thức giữ nguyên.")
    # `luc` không phải trang trí. Bàn giao đo tuổi kho bằng mtime của file, mà
    # mtime nói "lần ghi cuối", không nói "đo trên dữ liệu tới lúc nào". Một
    # lượt chạy hỏng nửa chừng vẫn chạm file và làm kho trông tươi. Số nến thì
    # nói cỡ mẫu — thiếu nó, "+0,4R" đọc giống nhau ở n=3 và n=300.
    # Ghi qua file tạm rồi đổi tên: hai lượt đấu có thể chạy song song (một gõ
    # tay, một của nghi thức) và cùng ghi đúng file này. `write_text` không
    # nguyên tử, nên chồng nhau để lại JSON cụt — mà lò chưng cất đọc hỏng thì
    # bỏ CẢ nguồn nhiều-chợ, tức mất luôn loại bằng chứng mạnh nhất, im lặng.
    _tam = _f.with_suffix(f".{__import__(chr(111) + chr(115)).getpid()}.tmp")
    _tam.write_text(_json.dumps({
        "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "cho": cot,
        # QUÃNG THỜI GIAN đã đo. Thiếu nó thì hai bảng của hai khung trông như
        # so được với nhau, mà thật ra không.
        #
        # Đã sập: chuỗi 4h có 3000 nến (từ 04/2025) còn 1d có 1500 nến (từ
        # 07/2022), nên cửa sổ ngoài mẫu của 4h là 150 ngày cuối còn của 1d là
        # 450 ngày cuối. Câu "4h −0,047R so với 1d +0,117R trên cùng 15 chợ" vì
        # thế KHÔNG phải so cùng kỳ — và nó đã được dùng làm đối chứng cho một
        # giả thuyết. Sự thật này vốn nằm sẵn trong một chú thích ở
        # `tai-lich-su.py`; chú thích không chặn được gì.
        "quang": ({"tu": _dt.datetime.fromtimestamp(
                       min(a for a, _ in quang) / 1000,
                       _dt.timezone.utc).strftime("%Y-%m-%d"),
                   "den": _dt.datetime.fromtimestamp(
                       max(b for _, b in quang) / 1000,
                       _dt.timezone.utc).strftime("%Y-%m-%d"),
                   "soNen": max(soNen)} if quang else None),
        "ket": {ma: {c: {"kyVongR": v[c].get("kyVongR"), "so": v[c].get("so"),
                         "tyLeThang": v[c].get("tyLeThang"),
                         "khopTroi": v[c].get("khopTroi"),
                         # nửa bot THẬT SỰ đánh được trên sàn spot
                         "chiLong": v[c].get("chiLong")}
                     for c in cot if c in v}
                for ma, v in bang.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    __import__("os").replace(_tam, _f)
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
