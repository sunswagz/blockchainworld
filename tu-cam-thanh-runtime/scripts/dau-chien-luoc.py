"""ĐẤU CHIẾN LƯỢC — đưa một bộ luật ra đấu với champion trên đoạn NGOÀI MẪU.

    python scripts/dau-chien-luoc.py MOCK_KEO_LUI_V1 "Chờ kéo lùi"
    python scripts/dau-chien-luoc.py --tat-ca      đấu mọi bộ luật chưa phải champion

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
