"""Phép kiểm số học — chạy được KHÔNG CẦN MẠNG.

    python scripts/selftest.py

Kiểm đúng những chỗ hỏng IM LẶNG: số vẫn ra, bảng vẫn xanh, chỉ có kết quả là
sai. Đây là loại lỗi đã cắn tu-cam-thanh-runtime bốn lần, nên ở đây làm trước.

Không phép kiểm nào ở đây gọi mạng, và không phép kiểm nào ghi vào sổ thật —
`KTG_DATA_DIR` được trỏ sang thư mục tạm trước khi import. Bài học từ Tử Cấm
Thành: selftest ở đó dựng những lệnh thắng để kiểm phần kế toán, rồi 14/17
lệnh trong sổ thật là hàng giả và bảng điều khiển khoe "thắng 82,4%" trong khi
bot chưa tự vào lệnh nào.
"""
from __future__ import annotations

import math
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["KTG_DATA_DIR"] = tempfile.mkdtemp(prefix="ktg-selftest-")

from kham.can_loi import can, gia_cap, phi_maker, phi_taker      # noqa: E402
from kham.config import CONFIG, che_hieu_luc, ly_do_khong_that   # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia, phi, TinMoi       # noqa: E402
from kham.dongho import DongHo, CAN_KET_QUA, CUOI_KHUNG          # noqa: E402
from kham.kho_doi import Kho                                     # noqa: E402
from kham.rui_ro import RiskEngine, SucKhoeNguon                 # noqa: E402
from kham.so import thong_ke                                     # noqa: E402
from kham.so_lenh import Muc, SoLenh                             # noqa: E402

_loi: list[str] = []
_dat = 0


def kiem(nhan: str, dieuKien: bool, chiTiet: str = "") -> None:
    global _dat
    if dieuKien:
        _dat += 1
        print(f"  ✓ {nhan}")
    else:
        _loi.append(nhan + (f" — {chiTiet}" if chiTiet else ""))
        print(f"  ✗ {nhan}" + (f"  ({chiTiet})" if chiTiet else ""))


def gan(a: float, b: float, sai: float = 1e-6) -> bool:
    return abs(a - b) <= sai


SO_MAU = SoLenh("BTC_5M", "UP",
                ask=[Muc(0.46, 80), Muc(0.48, 200), Muc(0.50, 400), Muc(0.53, 1000)],
                bid=[Muc(0.44, 300), Muc(0.42, 500)])


def kiem_so_lenh() -> None:
    print("\n── Sổ lệnh: VWAP theo khối lượng ─────────────────────────────")
    s = SO_MAU

    kiem("best ask đúng", gan(s.best_ask, 0.46))
    kiem("spread đúng", gan(s.spread, 0.02))

    # ĐÚNG bốn con số ghi trong docstring của so_lenh.py. Chúng nằm ở đây vì
    # bản viết tay đầu tiên nhẩm sai (0.4859 thay vì 0.4894) — một ví dụ sai
    # trong tài liệu còn tệ hơn không có ví dụ nào.
    r680 = s.vwap_mua(680)
    kiem("VWAP 680 cổ = 0.4894 (số trong docstring)",
         gan(r680.vwap, 0.489412, 1e-5), f"thực tế {r680.vwap:.6f}")
    kiem("edge thật 680 cổ = 6,1c",
         gan(0.55 - r680.vwap, 0.0606, 1e-4), f"{0.55 - r680.vwap:.4f}")

    r1680 = s.vwap_mua(1680)
    kiem("VWAP cả sổ 1680 cổ = 0.5136",
         gan(r1680.vwap, 0.513571, 1e-5), f"thực tế {r1680.vwap:.6f}")
    kiem("edge thật cả sổ = 3,6c",
         gan(0.55 - r1680.vwap, 0.0364, 1e-4))

    kiem("VWAP đơn điệu tăng theo khối lượng",
         all(s.vwap_mua(a).vwap <= s.vwap_mua(b).vwap + 1e-12
             for a, b in zip((80, 280, 680), (280, 680, 1680))))

    r = s.vwap_mua(3000)
    kiem("sổ mỏng thì báo thiếu, không bịa", (not r.dayDu) and gan(r.khop, 1680))

    # sức chứa phải KHỚP NGƯỢC: gom đúng ngần ấy thì VWAP không vượt hạn
    sc = s.suc_chua(0.49)
    kiem("sức chứa khớp ngược với VWAP",
         s.vwap_mua(sc).vwap <= 0.49 + 1e-9, f"{sc:.1f} cổ")
    kiem("sức chứa = 0 khi hạn dưới best ask", gan(s.suc_chua(0.45), 0.0))
    kiem("sức chứa = cả sổ khi hạn rất cao", gan(s.suc_chua(0.99), 1680.0))

    # Microprice nghiêng về phía ÍT hàng. Bid dày (300) so với ask (80) nghĩa
    # là áp lực mua lớn, giá bị đẩy LÊN phía ask — nên microprice phải NẰM
    # TRÊN mid. Bản đầu của phép kiểm này khẳng định ngược lại và bắt nhầm
    # code; giữ lại cả hai chiều để lần sau không ai lẫn nữa.
    kiem("microprice nằm TRÊN mid khi bid dày hơn ask",
         s.vi_gia > s.giua, f"vi_gia {s.vi_gia:.4f} vs giữa {s.giua:.4f}")
    dao = SoLenh("X", "UP", ask=[Muc(0.46, 300)], bid=[Muc(0.44, 80)])
    kiem("đảo lại: ask dày hơn thì microprice nằm DƯỚI mid",
         dao.vi_gia < dao.giua, f"{dao.vi_gia:.4f} vs {dao.giua:.4f}")
    kiem("imbalance dương khi bid dày hơn", s.lech() > 0)
    kiem("imbalance âm khi ask dày hơn", dao.lech() < 0)


def kiem_dong_ho() -> None:
    print("\n── Đồng hồ chợ: giai đoạn theo cả hai lối đo ─────────────────")
    import time
    d = DongHo()
    now = time.time() * 1000.0

    # Bẫy đã vấp: khung 15 phút còn 60 giây bị gọi là "giữa khung", vì giai
    # đoạn cuối chỉ tồn tại ở 45 giây tuyệt đối.
    kiem("khung 15p còn 60s là CUỐI khung, không phải giữa",
         d.lat_cat(now + 60_000, 900).giaiDoan == CUOI_KHUNG,
         d.lat_cat(now + 60_000, 900).nhan)
    kiem("khung 5p còn 60s cũng là cuối khung",
         d.lat_cat(now + 60_000, 300).giaiDoan == CUOI_KHUNG)
    kiem("khung 15p còn 14s là CẬN KẾT QUẢ (tuyệt đối thắng tỉ lệ)",
         d.lat_cat(now + 14_000, 900).giaiDoan == CAN_KET_QUA)
    kiem("khung 15p còn 450s là giữa khung",
         d.lat_cat(now + 450_000, 900).nhan == "giữa khung")
    kiem("hết giờ thì đã khoá", d.lat_cat(now - 1000, 300).da_khoa)


def kiem_dinh_gia() -> None:
    print("\n── Định giá: bốn bẫy số học ──────────────────────────────────")
    sig = 0.55 / math.sqrt(365 * 24 * 3600)

    kiem("Phi(0) = 0.5", gan(phi(0.0), 0.5))
    kiem("Phi đối xứng", gan(phi(1.0) + phi(-1.0), 1.0))

    # BẪY 1 — tau về 0 không được cho ra 0 hay 1
    eps = float(CONFIG["dinhGia"]["matPhangCanKetQua"])
    for tau in (1.0, 0.2, 0.0):
        g = dinh_gia("X", 100_050, 100_000, tau, sig)
        kiem(f"tau={tau}: P kẹp trong [{eps}, {1-eps}]",
             g is not None and eps - 1e-9 <= g.pUp <= 1 - eps + 1e-9,
             f"{g.pUp if g else None}")
    kiem("tau nhỏ thì có cờ tauDungSan",
         dinh_gia("X", 100_050, 100_000, 0.2, sig).tauDungSan)

    # Không có chắn thì công thức trần trụi cho ra đúng 1.0
    z_tran = math.log(100_050 / 100_000) / (sig * math.sqrt(0.2))
    kiem("không chắn thì công thức trần cho ra 1.0 (chứng minh bẫy có thật)",
         gan(phi(z_tran), 1.0, 1e-12))

    # BẪY 2 — bất định phải đi kèm và phải BỐC LÊN ở lằn ranh
    xa = dinh_gia("X", 100_050, 100_000, 3.0, sig)
    gan_ranh = dinh_gia("X", 100_000.5, 100_000, 3.0, sig)
    kiem("ngay lằn ranh + sắp hết giờ → bất định LỚN",
         gan_ranh.batDinh > 0.15, f"{gan_ranh.batDinh:.4f}")
    kiem("xa lằn ranh + sắp hết giờ → bất định nhỏ",
         xa.batDinh < 0.10, f"{xa.batDinh:.4f}")
    kiem("ngay lằn ranh thì mô hình tự nhận là KHÔNG rõ ràng",
         not gan_ranh.ro_rang)
    kiem("rủi ro nhảy giá tăng khi tau giảm (ở lằn ranh)",
         dinh_gia("X", 100_000.5, 100_000, 1.0, sig).ruiRoNhay >
         dinh_gia("X", 100_000.5, 100_000, 300.0, sig).ruiRoNhay)

    # BẪY 3 — năm dấu hiệu cùng một cú không được đếm thành năm
    th = {"btc_return": 0.30, "btc_momentum": 0.28, "btc_gia_lech": 0.25,
          "eth_theo": 0.22, "sol_theo": 0.20}
    tong, gt = TinMoi().gop(th)
    kiem("gộp tín hiệu nhỏ hơn hẳn tổng thô",
         tong < sum(th.values()) * 0.65, f"{tong:.3f} vs {sum(th.values()):.3f}")
    kiem("chỉ đếm 2 họ chứ không phải 5 tín hiệu", gt["soHo"] == 2)
    kiem("tín hiệu mạnh nhất mỗi họ giữ trọn trọng số",
         sum(1 for c in gt["chiTiet"] if c["trongSo"] == 1.0) == 2)

    # BẪY 4 — Kelly khoá tới khi đủ mẫu
    h = HieuChinh(duong=Path(os.environ["KTG_DATA_DIR"]) / "hc.json")
    kiem("chưa có mẫu thì Kelly bị khoá", not h.du_de_dung_kelly())
    for i in range(int(CONFIG["dinhGia"]["toiThieuMauHieuChinh"]) + 10):
        h.them(0.60, i % 100 < 52)
    kiem("đủ mẫu thì Kelly mở", h.du_de_dung_kelly())
    kiem("đo được mô hình lệch bao nhiêu",
         h.sai_so_tuyet_doi_tb() is not None and h.sai_so_tuyet_doi_tb() < 0.1)

    kiem("thiếu sigma thì trả None chứ không bịa 0.5",
         dinh_gia("X", 100_050, 100_000, 100, None) is None)


def kiem_can_loi() -> None:
    print("\n── Cân lợi: net edge và phí ──────────────────────────────────")

    kiem("phí taker cao nhất ở giữa bảng giá",
         phi_taker(0.50, 1) > phi_taker(0.10, 1) and
         phi_taker(0.50, 1) > phi_taker(0.90, 1))
    kiem("phí taker đối xứng quanh 50c",
         gan(phi_taker(0.30, 1), phi_taker(0.70, 1)))
    kiem("phí taker gần 0 ở 98,7c", phi_taker(0.987, 1) < 0.0005)
    kiem("phí maker bằng 0", gan(phi_maker(0.5, 1000), 0.0))

    c80 = can("X", "UP", "t", 0.55, 0.02, SO_MAU, 80)
    c1680 = can("X", "UP", "t", 0.55, 0.02, SO_MAU, 1680)
    kiem("net edge giảm khi lô to lên",
         c1680.netEdge < c80.netEdge, f"{c1680.netEdge:+.4f} < {c80.netEdge:+.4f}")
    kiem("lô cả sổ làm net edge thành ÂM (edge 9c biến mất)",
         c1680.netEdge < 0, f"{c1680.netEdge:+.4f}")
    kiem("net luôn nhỏ hơn gross (năm khoản trừ đều có tác dụng)",
         c80.netEdge < c80.grossEdge)
    kiem("maker rẻ hơn taker",
         can("X", "UP", "t", 0.55, 0.02, SO_MAU, 280, laMaker=True).phi <
         can("X", "UP", "t", 0.55, 0.02, SO_MAU, 280).phi)
    kiem("maker khớp khó hơn taker",
         can("X", "UP", "t", 0.55, 0.02, SO_MAU, 280, laMaker=True).xacSuatKhop <
         can("X", "UP", "t", 0.55, 0.02, SO_MAU, 280).xacSuatKhop)
    kiem("bất định lớn ăn hết lợi thế",
         can("X", "UP", "t", 0.55, 0.30, SO_MAU, 280).netEdge < 0)

    # sức chứa phải là chỗ net edge vừa chạm 0
    kiem("gom đúng sức chứa thì net vẫn không âm",
         can("X", "UP", "t", 0.55, 0.02, SO_MAU,
             max(1.0, c80.sucChua)).netEdge >= -1e-3)


def kiem_gia_cap() -> None:
    print("\n── Giá cặp: cặp khoá lỗ ──────────────────────────────────────")
    dat_up = SoLenh("X", "UP", ask=[Muc(0.55, 300)], bid=[])
    dat_dn = SoLenh("X", "DOWN", ask=[Muc(0.49, 300)], bid=[])
    gc = gia_cap("X", dat_up, dat_dn, 235)
    kiem("cặp 1,04$ bị nhận diện là KHOÁ LỖ", gc.khoa_lo)
    kiem("gross cặp âm đúng 4c", gan(gc.grossCap, -0.04, 1e-9))
    kiem("net cặp còn âm hơn gross (phí)", gc.netCap < gc.grossCap)

    re_up = SoLenh("X", "UP", ask=[Muc(0.49, 300)], bid=[])
    re_dn = SoLenh("X", "DOWN", ask=[Muc(0.27, 300)], bid=[])
    g2 = gia_cap("X", re_up, re_dn, 100)
    kiem("cặp 0,76$ không phải khoá lỗ", not g2.khoa_lo)
    kiem("cặp 0,76$ cho gross +24c", gan(g2.grossCap, 0.24, 1e-9))

    # số cặp phải là phần NHỎ HƠN, không phải trung bình
    mong = SoLenh("X", "DOWN", ask=[Muc(0.27, 40)], bid=[])
    g3 = gia_cap("X", re_up, mong, 100)
    kiem("chân mỏng quyết định số cặp, không lấy trung bình",
         gan(g3.soCap, 40.0), f"{g3.soCap}")


def kiem_kho_doi() -> None:
    print("\n── Kho đối: ba phần tồn kho ──────────────────────────────────")
    k = Kho()
    v = k.lay("BTC_5M")
    v.ghi_khop("UP", 260, 0.55)
    v.ghi_khop("DOWN", 235, 0.49)

    kiem("đã ghép cặp = min(UP, DOWN) = 235", gan(v.daGhepCap, 235))
    kiem("định hướng = 260 - 235 = 25", gan(v.dinhHuong, 25))
    kiem("giá cặp = 1,04$ tính từ GIÁ VỐN", gan(v.giaCap, 1.04, 1e-9))
    kiem("cặp này đang khoá lỗ", v.capKhoaLo)
    kiem("lỗ khoá = 4c x 235 = $9,40", gan(v.loKhoaUsd, 9.40, 1e-9))
    kiem("chưa phòng hộ đo bằng ĐÔ chứ không bằng cổ",
         gan(v.chuaPhongHoUsd, 25 * 0.55, 1e-9))

    # kế toán kết quả phải khớp
    kiem("UP thắng: nhận 260, đã trả 258,15 → +1,85",
         gan(v.lai_lo_khi_ket_qua(True), 260 - (260*0.55 + 235*0.49), 1e-9))
    kiem("DOWN thắng: nhận 235 → lỗ",
         v.lai_lo_khi_ket_qua(False) < 0)

    # tương quan: bốn market cùng long không được coi là bốn cược nhỏ
    for ma in ("BTC_5M", "BTC_15M", "ETH_5M", "SOL_5M"):
        x = k.lay(ma)
        x.coUp, x.tienUp = 0, 0.0
        x.coDown, x.tienDown = 0, 0.0
        x.ghi_khop("UP", 100, 0.50)
    gop = k.phoi_nhiem_gop()
    tong_le = sum(abs(x) for x in k.phoi_nhiem_theo_nhom().values())
    kiem("phơi nhiễm gộp gần bằng TỔNG khi tương quan cao",
         gop > tong_le * 0.9, f"gộp {gop:.1f} vs tổng {tong_le:.1f}")


def kiem_rui_ro() -> None:
    print("\n── Risk Engine: quyền phủ quyết ──────────────────────────────")
    k = Kho()
    re = RiskEngine(k)
    ch = can("BTC_5M", "UP", "t", 0.55, 0.02, SO_MAU, 600)
    lanh = SucKhoeNguon(200, 150, 80)

    kiem("cơ hội tốt + nguồn lành → CHO", re.duyet(ch, lanh, 200, False).cho)
    kiem("sổ lệnh cũ 4s → TỪ CHỐI",
         re.duyet(ch, SucKhoeNguon(4000, 150, 80), 200, False).tu_choi)
    kiem("đồng hồ lệch 2s → TỪ CHỐI",
         re.duyet(ch, SucKhoeNguon(200, 150, 2000), 200, False).tu_choi)
    kiem("mất nguồn → TỪ CHỐI",
         re.duyet(ch, SucKhoeNguon(200, 150, 80, ["binance"]), 200, False).tu_choi)
    kiem("sắp hết giờ → TỪ CHỐI mở vị thế mới",
         re.duyet(ch, lanh, 10, False).tu_choi)

    xau = can("BTC_5M", "UP", "t", 0.50, 0.02, SO_MAU, 600)
    kiem("net edge âm → TỪ CHỐI", re.duyet(xau, lanh, 200, False).tu_choi)

    # chưa hiệu chỉnh thì KHÔNG được dùng Kelly
    chua = re.duyet(ch, lanh, 200, False)
    du = re.duyet(ch, lanh, 200, True)
    kiem("chưa đủ mẫu → giữ lô sàn, không dùng Kelly",
         chua.soCoChoPhep <= float(CONFIG["canLoi"]["sucChuaToiThieu"]) + 1e-9)
    kiem("đủ mẫu → Kelly cho phép lớn hơn lô sàn",
         du.soCoChoPhep > chua.soCoChoPhep, f"{du.soCoChoPhep:.0f} vs {chua.soCoChoPhep:.0f}")

    # tin cậy cao KHÔNG được nới rủi ro
    tin_cao = can("BTC_5M", "UP", "t", 0.95, 0.01, SO_MAU, 600)
    pq = re.duyet(tin_cao, lanh, 200, False)
    kiem("mô hình rất tự tin vẫn KHÔNG vượt lô sàn khi chưa hiệu chỉnh",
         pq.soCoChoPhep <= float(CONFIG["canLoi"]["sucChuaToiThieu"]) + 1e-9,
         f"{pq.soCoChoPhep:.0f} cổ")

    # cầu dao
    re.ghi_lai_lo(-float(CONFIG["ruiRo"]["tranLoNgayUsd"]) - 1)
    kiem("chạm trần lỗ ngày → cầu dao NGẮT", re.ngatKhanCap)
    kiem("cầu dao ngắt thì mọi lệnh bị chặn", re.duyet(ch, lanh, 200, True).tu_choi)
    re.mo_lai()
    kiem("cầu dao không tự phục hồi, phải mở tay", not re.ngatKhanCap)


def kiem_thong_ke() -> None:
    print("\n── Thống kê: tỉ lệ thắng không đi một mình ───────────────────")
    # Hình cận-kết-quả: mua ở 98,7c, thắng ăn 1,3c, thua mất 98,7c.
    #
    # Điểm hoà vốn:  1,3 x p = 98,7 x (1-p)  =>  p = 98,7%
    #
    # Đây mới là bài học thật, và nó sắc hơn câu "tỉ lệ thắng cao vẫn lỗ":
    # tỉ lệ thắng 99% CÓ lãi, nhưng lãi mỏng tới mức chỉ cần tụt 1 điểm phần
    # trăm là lật thành lỗ. Toàn bộ chiến lược sống trên một dải rộng đúng
    # một điểm phần trăm — mà tỉ lệ thắng đo được từ vài trăm lượt thì sai số
    # còn rộng hơn thế.
    def bo(pct_thang: int) -> list[dict]:
        return ([{"laiLo": 0.013, "phiUsd": 0} for _ in range(pct_thang)] +
                [{"laiLo": -0.987, "phiUsd": 0} for _ in range(100 - pct_thang)])

    t99 = thong_ke(bo(99))
    t98 = thong_ke(bo(98))
    kiem("tỉ lệ thắng 99%", gan(t99["tiLeThang"], 0.99))
    kiem("99% thắng → kỳ vọng dương, nhưng mỏng dính",
         0 < t99["kyVong"] < 0.005, f"{t99['kyVong']:+.5f}")
    kiem("tụt xuống 98% → kỳ vọng thành ÂM",
         t98["kyVong"] < 0, f"{t98['kyVong']:+.5f}")
    kiem("một lần thua xoá ~76 lần thắng",
         74 < t99["xoaBaoNhieuLanThang"] < 78, f"{t99['xoaBaoNhieuLanThang']:.1f}")
    kiem("cả hai đều bị gắn cảnh báo đuôi",
         t99["canhBaoDuoi"] and t98["canhBaoDuoi"])
    kiem("chưa có dữ liệu thì nói chưa có, không bịa 0",
         thong_ke([])["chuaCo"])


def kiem_cua_lenh_that() -> None:
    print("\n── Ba cửa của lệnh thật ──────────────────────────────────────")
    thieu = ly_do_khong_that()
    kiem("mặc định: KHÔNG đủ điều kiện đặt lệnh thật", len(thieu) > 0)
    kiem("nói rõ từng cửa đang đóng", len(thieu) >= 3, f"{len(thieu)} cửa")
    kiem("chế độ hiệu lực không bao giờ là 'that' khi thiếu cửa",
         che_hieu_luc() in ("quan-sat", "giay"), che_hieu_luc())
    kiem("config khai `giay` chứ không phải `that`",
         CONFIG.get("che") != "that", CONFIG.get("che"))
    kiem("cờ choPhepLenhThat mặc định tắt",
         not CONFIG["datLenh"]["choPhepLenhThat"])
    kiem("cờ xác nhận đã đọc rủi ro mặc định tắt",
         not CONFIG["datLenh"]["toiXacNhanDaDocRuiRo"])


def main() -> int:
    print("=" * 70)
    print("  KHÂM THIÊN GIÁM — phép kiểm số học (không cần mạng)")
    print("=" * 70)
    print(f"  hệ số phí taker đang dùng: {CONFIG['phi']['takerHeSo']}")
    print("  ĐỐI CHIẾU docs.polymarket.com/trading/fees trước khi chạy tiền thật")

    kiem_so_lenh()
    kiem_dong_ho()
    kiem_dinh_gia()
    kiem_can_loi()
    kiem_gia_cap()
    kiem_kho_doi()
    kiem_rui_ro()
    kiem_thong_ke()
    kiem_cua_lenh_that()

    print("\n" + "=" * 70)
    if _loi:
        print(f"  {_dat} đạt · {len(_loi)} HỎNG")
        for l in _loi:
            print(f"    ✗ {l}")
        return 1
    print(f"  {_dat}/{_dat} đạt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
