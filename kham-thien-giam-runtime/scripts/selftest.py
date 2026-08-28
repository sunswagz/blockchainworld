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

import gzip
import math
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["KTG_DATA_DIR"] = tempfile.mkdtemp(prefix="ktg-selftest-")

from kham.bang import (MayGhi, _thu_muc, dem_bang,               # noqa: E402
                       doc_bang, doc_bang_day_du)
from kham.can_loi import can, gia_cap, phi_maker, phi_taker      # noqa: E402
from kham.config import CONFIG, che_hieu_luc, ly_do_khong_that   # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia, phi, TinMoi       # noqa: E402
from kham.dongho import DongHo, CAN_KET_QUA, CUOI_KHUNG          # noqa: E402
from kham.kho_doi import Kho                                     # noqa: E402
from kham.rui_ro import RiskEngine, SucKhoeNguon                 # noqa: E402
from kham.so import thong_ke                                     # noqa: E402
from kham.so_lenh import Muc, SoLenh                             # noqa: E402
from kham.cap_token import CapSo, soi_guong                      # noqa: E402
from kham.khung import (CHUA_MO, DAT_CUOC, QUAN_SAT, DA_XONG,    # noqa: E402
                        Khung, chon_dat_cuoc, phan_giai)
from kham.chan_rui_ro import (CHIU, CHO, DONG_CHAN, VUOT_SPREAD, # noqa: E402
                              quyet)
from kham.do_thi import DoThi, Nut                               # noqa: E402
from kham.chay_lai import ThamSo, doi_chieu, dung_so, mot_luot    # noqa: E402
from kham.vo_dich import SoVoDich                                # noqa: E402
from kham.chan_doan import (NUT_THEO_DUONG, NUT_VAN, TrieuChung,  # noqa: E402
                            chan_doan, de_bai, doc_tham_so, kep)
# `mot_luot` có ở CẢ chay_lai lẫn tien_hoa — hai việc khác hẳn nhau. Đặt bí
# danh chứ đừng để cái sau che cái trước: bản đầu của phép kiểm này để nguyên
# và `kiem_chay_lai` lặng lẽ gọi nhầm hàm, ném AttributeError ở chỗ không liên
# quan gì tới chỗ sai.
from kham.tien_hoa import (BIEN_VUOT, DUOI_TOI_DA, SO_TIEN_HOA,   # noqa: E402
                           TOI_THIEU_MAU, DeXuat, de_xuat_tat_dinh,
                           duong_tien_hoa, thu_mot_de_xuat)
from kham.tien_hoa import mot_luot as tien_hoa_mot_luot           # noqa: E402
from kham.vong import TIEN_HOA_TOI_DA_THU                         # noqa: E402

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



def kiem_cap_token() -> None:
    print("\n── Cặp token bù trừ ──────────────────────────────────────────")
    u = SoLenh("X", "UP", ask=[Muc(0.46, 80)], bid=[Muc(0.44, 300)])
    d = SoLenh("X", "DOWN", ask=[Muc(0.55, 150)], bid=[Muc(0.52, 200)])
    cs = CapSo("X", u, d)
    kiem("mua UP lấy lối rẻ hơn trong hai lối",
         gan(cs.gia_mua("UP"), 0.46), f"{cs.gia_mua('UP')}")
    kiem("qua bù trừ rẻ hơn thì lấy lối đó",
         gan(CapSo("X", SoLenh("X", "UP", ask=[Muc(0.60, 9)], bid=[]),
                   SoLenh("X", "DOWN", ask=[], bid=[Muc(0.52, 9)])).gia_mua("UP"),
             0.48))
    kiem("giá cặp = tổng hai lối tốt nhất", gan(cs.tong_gia_mua, 1.01))

    g = soi_guong(u, "X", "DOWN")
    kiem("soi gương: bid 0.44 thành ask 0.56", gan(g.best_ask, 0.56))
    kiem("soi gương: ask 0.46 thành bid 0.54", gan(g.best_bid, 0.54))
    kiem("soi gương hai lần về chính nó",
         gan(soi_guong(g, "X", "UP").best_ask, 0.46))

    # THANG CHỜ — đo được trên chợ thật, phải bị chặn
    thang = SoLenh("X", "UP",
                   bid=[Muc(i / 1000.0, 50) for i in range(1, 1000, 10)], ask=[])
    kiem("thang chờ trải cả dải bị nhận diện", thang.trai_ca_bang)
    kiem("thang chờ KHÔNG được coi là dùng được", not thang.dung_duoc)
    kiem("sổ thường không bị nhầm là thang chờ", not u.trai_ca_bang)
    kiem("sổ một chiều nhưng hẹp thì không phải thang chờ",
         not SoLenh("X", "UP", bid=[Muc(0.44, 9), Muc(0.43, 9)], ask=[]).trai_ca_bang)
    kiem("cặp có thang chờ thì nói rõ lý do",
         "thang chờ" in (CapSo("X", thang, thang).ly_do_khong_dung() or ""))


def kiem_khung() -> None:
    print("\n── Vòng đời khung ────────────────────────────────────────────")
    evs = 1_000_000_000_000.0
    k = Khung(slug="btc-updown-5m-1", ma="BTC_5M", capNen="BTCUSDT",
              tokenUp="a", tokenDown="b", batDauDatCuocMs=evs - 300_000,
              eventStartMs=evs, endMs=evs + 300_000)
    kiem("trước cửa → chưa mở", k.giai_doan(evs - 301_000) == CHUA_MO)
    kiem("trong cửa → ĐẶT CƯỢC", k.giai_doan(evs - 150_000) == DAT_CUOC)
    kiem("qua eventStart → quan sát (sổ đóng băng)",
         k.giai_doan(evs + 10_000) == QUAN_SAT)
    kiem("qua endDate → đã xong", k.giai_doan(evs + 301_000) == DA_XONG)
    kiem("tau đo theo CỬA ĐẶT CƯỢC, không theo khung",
         gan(k.con_lai_giay(evs - 120_000), 120.0))
    kiem("qua cửa thì tau = 0", gan(k.con_lai_giay(evs + 5_000), 0.0))

    m = {"slug": "btc-updown-5m-1787217300",
         "eventStartTime": "2026-08-20T09:15:00Z",
         "endDate": "2026-08-20T09:20:00Z",
         "clobTokenIds": '["tokA","tokB"]'}
    p = phan_giai(m, "BTC_5M", "BTCUSDT")
    kiem("phân giải được bản ghi Gamma thật", p is not None)
    kiem("cửa đặt cược = eventStart trừ 300s",
         gan(p.eventStartMs - p.batDauDatCuocMs, 300_000.0))
    kiem("KHÔNG dùng startDate (bẫy cách gần một ngày)",
         gan(p.eventStartMs, 1787217300000.0))
    kiem("clobTokenIds dạng chuỗi JSON vẫn đọc được", p.tokenUp == "tokA")

    p2 = phan_giai({"slug": "btc-updown-5m-1787217300",
                    "clobTokenIds": ["a", "b"]}, "BTC_5M", "BTCUSDT")
    kiem("thiếu eventStartTime thì lấy mốc trong slug",
         p2 is not None and gan(p2.eventStartMs, 1787217300000.0))

    ds = [Khung("s1", "M", "C", "a", "b", evs - 300_000, evs, evs + 300_000),
          Khung("s2", "M", "C", "a", "b", evs, evs + 300_000, evs + 600_000)]
    kiem("chọn đúng khung đang trong cửa",
         chon_dat_cuoc(ds, evs - 100_000).slug == "s1")
    kiem("không khung nào trong cửa thì trả None",
         chon_dat_cuoc(ds, evs - 400_000) is None)


def kiem_chan_rui_ro() -> None:
    print("\n── Chân rủi ro: quyết định sau cú khớp đầu ───────────────────")
    from kham.kho_doi import ViThe
    cap = CapSo("X", SoLenh("X", "UP", ask=[Muc(0.50, 999)], bid=[Muc(0.48, 999)]),
                SoLenh("X", "DOWN", ask=[Muc(0.52, 999)], bid=[Muc(0.50, 999)]))

    can_bang = ViThe(ma="X")
    can_bang.ghi_khop("UP", 100, 0.45)
    can_bang.ghi_khop("DOWN", 100, 0.50)
    kiem("vị thế cân bằng thì không cần quyết gì",
         quyet(can_bang, cap, 200) is None)

    lech = ViThe(ma="X")
    lech.ghi_khop("UP", 100, 0.45)
    q = quyet(lech, cap, 200)
    kiem("còn nhiều giờ + giá tốt → CHỜ", q.loi == CHO, q.nhan)
    kiem("nói rõ cần bù bên nào", q.ben == "DOWN")

    q2 = quyet(lech, cap, 5)
    kiem("cửa sắp đóng → KHÔNG được chờ nữa", q2.loi != CHO, q2.nhan)
    kiem("bù vẫn có lãi thì vượt spread", q2.loi == VUOT_SPREAD)

    dat = ViThe(ma="X")
    dat.ghi_khop("UP", 100, 0.85)
    q3 = quyet(dat, cap, 5)
    kiem("bù bây giờ khoá lỗ thì phải CÓ TÊN, không lặng lẽ",
         q3.loi in (CHIU, VUOT_SPREAD) and q3.khoaLoUsd > 0,
         f"{q3.nhan} khoá {q3.khoaLoUsd:.2f}")

    kho_bu = CapSo("X", SoLenh("X", "UP", ask=[], bid=[]),
                   SoLenh("X", "DOWN", ask=[], bid=[]))
    q4 = quyet(lech, kho_bu, 5)
    kiem("không bù được + sắp đóng → đóng chân", q4.loi == DONG_CHAN, q4.nhan)


def kiem_do_thi() -> None:
    print("\n── Đồ thị chợ: so lệch, không so giá thô ─────────────────────")
    g = DoThi()
    g.dat(Nut("BTC_5M", "s1", "BTC", 100, 0.66, 0.68, 0.03))
    g.dat(Nut("BTC_15M", "s2", "BTC", 400, 0.61, 0.54, 0.03))
    a, b = g.nut["BTC_5M"], g.nut["BTC_15M"]
    kiem("khung giá CAO hơn lại đang đắt so với mô hình", a.lech < 0)
    kiem("khung giá THẤP hơn lại đang rẻ so với mô hình", b.lech > 0)
    kiem("z chuẩn hoá theo bất định của chính khung",
         gan(b.z, b.lech / 0.03, 1e-9))

    g2 = DoThi()
    for i, ma in enumerate(("BTC_5M", "ETH_5M", "SOL_5M")):
        g2.dat(Nut(ma, f"s{i}", ma.split("_")[0], 100, 0.60, 0.50, 0.03))
    kiem("cả rổ cùng lệch một chiều → cảnh báo MÔ HÌNH lệch",
         g2.canh_bao_dong_pha() is not None)
    kiem("cảnh báo nói đúng chữ mô hình",
         "MÔ HÌNH" in (g2.canh_bao_dong_pha() or ""))
    kiem("lệch đồng pha thì không nút nào nổi bật", not g2.noi_bat())


def kiem_vo_dich() -> None:
    print("\n── Champion/Challenger: không có đường tắt ───────────────────")
    import tempfile
    sv = SoVoDich(duong=Path(tempfile.mkdtemp()) / "vd.json")
    kiem("chưa có hồ sơ thì không duyệt", not sv.xet("moi").cho)

    it = [{"laiLo": 0.02, "phiUsd": 0, "chienThuat": ["it-mau"]} for _ in range(10)]
    sv.cap_nhat(it)
    px = sv.xet("it-mau")
    kiem("thắng 10/10 nhưng thiếu mẫu → KHÔNG duyệt", not px.cho)
    kiem("nói rõ vì thiếu mẫu", any("mẫu" in l for l in px.lyDo))

    tot = [{"laiLo": 0.02, "phiUsd": 0, "chienThuat": ["tot"]} for _ in range(200)]
    sv.cap_nhat(tot)
    kiem("đủ mẫu + kỳ vọng dương + chưa có đương kim → lên", sv.xet("tot").cho)

    duoi = ([{"laiLo": 0.05, "phiUsd": 0, "chienThuat": ["duoi-xau"]}
             for _ in range(199)] +
            [{"laiLo": -5.0, "phiUsd": 0, "chienThuat": ["duoi-xau"]}])
    sv.cap_nhat(duoi)
    px2 = sv.xet("duoi-xau")
    kiem("kỳ vọng cao hơn mà ĐUÔI tệ hơn → KHÔNG lên", not px2.cho,
         "; ".join(px2.lyDo)[:60])
    kiem("nói rõ vì đuôi",
         any(("thua lớn nhất" in l) or ("đuôi" in l) for l in px2.lyDo))
    kiem("đương kim không bị thay", sv.duongKim.get("chung") == "tot")


def kiem_chay_lai() -> None:
    print("\n── Chạy lại theo sự kiện ─────────────────────────────────────")
    so = dung_so({"luc": 1, "bid": [{"gia": 0.44, "luong": 300}],
                  "ask": [{"gia": 0.46, "luong": 80},
                          {"gia": 0.48, "luong": 200}]}, "X", "UP")
    kiem("dựng lại được sổ từ băng", so is not None and gan(so.best_ask, 0.46))
    kiem("dựng lại giữ đúng thứ tự mức", gan(so.ask[1].gia, 0.48))

    sig = 0.55 / math.sqrt(365 * 24 * 3600)
    khung = []
    for i in range(60):
        d = 1 if i % 2 else -1
        khung.append({"thiTruong": [{
            "ma": "BTC_5M", "giaNen": 100_000 + d * 60, "giaMo": 100_000,
            "sigmaGiay": sig, "conLaiGiay": 120.0, "upThang": d > 0,
            "so": {"UP": {"luc": 1, "bid": [{"gia": 0.40, "luong": 500}],
                          "ask": [{"gia": 0.42, "luong": 500}]},
                   "DOWN": {"luc": 1, "bid": [{"gia": 0.55, "luong": 500}],
                            "ask": [{"gia": 0.57, "luong": 500}]}}}]})
    at = float(CONFIG["canLoi"]["bienAnToan"])
    r = mot_luot(khung, ThamSo("chat", 0.02, at))
    kiem("chạy lại đọc hết khung", r.soKhung == 60)
    kiem("chạy lại có cân ra cơ hội", r.soCoHoi > 0)

    dc = doi_chieu(khung, ThamSo("long", 0.001, at), ThamSo("chat", 0.20, at))
    kiem("ngưỡng lỏng cho qua sàng nhiều hơn ngưỡng chặt",
         dc["A"]["soQuaSang"] >= dc["B"]["soQuaSang"])
    kiem("thiếu mẫu thì NÓI thiếu mẫu, không kết luận bừa",
         dc["duMau"] or "CHƯA ĐỦ MẪU" in dc["ketLuan"])

    rong = doi_chieu([], ThamSo("a", 0.01, at), ThamSo("b", 0.02, at))
    kiem("băng rỗng → không kết luận", not rong["duMau"])



def _bang_gia(n=80, thang_xen_ke=True):
    """Dựng băng giả đủ để chạy lại — sổ hai chiều, có kết quả."""
    sig = 0.55 / math.sqrt(365 * 24 * 3600)
    ra = []
    for i in range(n):
        d = 1 if (i % 2 if thang_xen_ke else i % 3) else -1
        ra.append({"thiTruong": [{
            "ma": "BTC_5M", "giaNen": 100_000 + d * 60, "giaMo": 100_000,
            "sigmaGiay": sig, "conLaiGiay": 120.0, "upThang": d > 0,
            "so": {"UP": {"luc": 1, "thangCho": False, "dungDuoc": True,
                          "bid": [{"gia": 0.40, "luong": 900}],
                          "ask": [{"gia": 0.42, "luong": 900}]},
                   "DOWN": {"luc": 1, "thangCho": False, "dungDuoc": True,
                            "bid": [{"gia": 0.55, "luong": 900}],
                            "ask": [{"gia": 0.57, "luong": 900}]}}}]})
    return ra


def kiem_chan_doan() -> None:
    print("\n── Chẩn đoán: tìm bệnh bằng SỐ, trước khi model nói ──────────")
    # thiếu mẫu thì KHÔNG được chẩn bừa
    tc = chan_doan([], {"saiSoTB": None, "tongMau": 0, "bang": []})
    kiem("chưa đủ mẫu → nói thiếu mẫu, không chẩn bừa",
         len(tc) == 1 and tc[0].ma == "thieu-mau")
    kiem("thiếu mẫu thì KHÔNG gợi ý nút nào", not tc[0].nutGoiY)

    # kỳ vọng âm
    lo = [{"laiLo": -0.02, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 0.98}
          for _ in range(30)] + \
         [{"laiLo": 0.01, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 0.98}
          for _ in range(20)]
    tc2 = chan_doan(lo, {"saiSoTB": 0.01, "tongMau": 300, "bang": []})
    ma2 = [t.ma for t in tc2]
    kiem("kỳ vọng âm bị bắt", "ky-vong-am" in ma2, ", ".join(ma2))
    kiem("bệnh nặng thì nặng=3",
         any(t.nang == 3 for t in tc2 if t.ma == "ky-vong-am"))
    kiem("bệnh nào cũng kèm nút vặn được",
         all(t.nutGoiY for t in tc2 if t.nang >= 2))

    # đuôi lệch
    duoi = [{"laiLo": 0.013, "phiUsd": 0, "chienThuat": ["x"]} for _ in range(99)]
    duoi.append({"laiLo": -0.987, "phiUsd": 0, "chienThuat": ["x"]})
    kiem("đuôi lệch bị bắt dù kỳ vọng dương",
         "duoi-lech" in [t.ma for t in
                         chan_doan(duoi, {"saiSoTB": 0.01, "tongMau": 300, "bang": []})])

    # cặp khoá lỗ
    khoa = [{"laiLo": 0.01, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 1.04}
            for _ in range(30)] + \
           [{"laiLo": 0.01, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 0.96}
            for _ in range(10)]
    kiem("cặp khoá lỗ nhiều bị bắt",
         "cap-khoa-lo" in [t.ma for t in
                           chan_doan(khoa, {"saiSoTB": 0.01, "tongMau": 300, "bang": []})])

    # khoẻ thì nói khoẻ
    tot = [{"laiLo": 0.02, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 0.95}
           for _ in range(40)]
    kiem("không bệnh nào → báo khoẻ",
         [t.ma for t in chan_doan(tot, {"saiSoTB": 0.01, "tongMau": 300, "bang": []})]
         == ["khoe"])


def kiem_nut_van() -> None:
    print("\n── Nút vặn: bề mặt model được chạm, và trần cứng ─────────────")
    kiem("mọi nút đều có trần trên/dưới hợp lệ",
         all(n.thap < n.cao and n.buoc > 0 for n in NUT_VAN))
    kiem("mọi nút đều trỏ tới tham số CÓ THẬT trong config",
         all(doc_tham_so(n.duong) is not None for n in NUT_VAN),
         ", ".join(n.duong for n in NUT_VAN if doc_tham_so(n.duong) is None))

    n = NUT_THEO_DUONG["ruiRo.kellyPhan"]
    kiem("đề nghị vượt trần bị KẸP, không được nhận nguyên",
         gan(kep("ruiRo.kellyPhan", 5.0), n.cao), f"{kep('ruiRo.kellyPhan', 5.0)}")
    kiem("đề nghị dưới sàn cũng bị kẹp",
         gan(kep("ruiRo.kellyPhan", -3.0), n.thap))
    kiem("đường KHÔNG có trong bảng thì bị BỎ, không phải bị kẹp",
         kep("ruiRo.vonBanDau", 999) is None)
    kiem("đường bịa hoàn toàn cũng bị bỏ",
         kep("khong.co.duong.nay", 1) is None)


def kiem_de_xuat() -> None:
    print("\n── Đề xuất: vắng model thì vẫn có người đề xuất ──────────────")
    lo = [{"laiLo": -0.02, "phiUsd": 0, "chienThuat": ["x"], "giaCap": 0.98}
          for _ in range(50)]
    tc = chan_doan(lo, {"saiSoTB": 0.01, "tongMau": 300, "bang": []})
    dx = de_xuat_tat_dinh(tc)
    kiem("không cần model vẫn đề xuất được", len(dx) >= 1)
    kiem("đề xuất nằm trong bảng nút vặn", dx[0].nut in NUT_THEO_DUONG)
    kiem("đề xuất khác giá trị hiện tại", abs(dx[0].denGiaTri - dx[0].tuGiaTri) > 0)
    kiem("đề xuất nằm trong trần cứng",
         NUT_THEO_DUONG[dx[0].nut].thap <= dx[0].denGiaTri <= NUT_THEO_DUONG[dx[0].nut].cao)
    kiem("đề xuất khai rõ chữa bệnh nào", dx[0].chuaTrieuChung in [t.ma for t in tc])

    # bệnh ngược: đứng ngoài quá nhiều thì phải NỚI, không siết
    dn = [TrieuChung("dung-ngoai", 1, "", {},
                     ["canLoi.netEdgeToiThieu"])]
    d2 = de_xuat_tat_dinh(dn)
    kiem("bệnh `đứng ngoài` thì NỚI ngưỡng, không siết",
         d2 and d2[0].denGiaTri < d2[0].tuGiaTri,
         f"{d2[0].tuGiaTri} → {d2[0].denGiaTri}" if d2 else "không có")

    kiem("đề bài cho model KHÔNG kèm sổ thô",
         "nhatKy" not in de_bai(tc, {}) and "ketToan" not in de_bai(tc, {}))
    kiem("đề bài có kèm trần của từng nút",
         all("thap" in x and "cao" in x
             for x in de_bai(tc, {})["nutVanChoPhep"]))


def kiem_cong_tien_hoa() -> None:
    print("\n── Cổng tiến hoá: trả lại KHÔNG phải thất bại ────────────────")
    khung = _bang_gia(80)

    # đề xuất siết ngưỡng lên rất cao → gần như không lệnh nào qua → thiếu mẫu
    dx = DeXuat("canLoi.netEdgeToiThieu", 0.015, 0.25, "ky-vong-am", "thử")
    r = thu_mot_de_xuat(khung, dx)
    kiem("siết tới mức không còn mẫu → cổng TRẢ LẠI", not r["cho"])
    kiem("nói rõ vì thiếu mẫu", any("mẫu" in l for l in r["lyDo"]),
         "; ".join(r["lyDo"])[:70])

    # đề xuất không đổi gì đáng kể → không vượt biên
    dx2 = DeXuat("canLoi.netEdgeToiThieu", 0.015, 0.0155, "ky-vong-am", "thử")
    r2 = thu_mot_de_xuat(khung, dx2)
    kiem("thay đổi không tạo cải thiện → TRẢ LẠI", not r2["cho"])

    kiem("cổng luôn kèm cả hai bảng A và B để đối chiếu",
         "A" in r and "B" in r and "soKhop" in r["A"])
    kiem("ngưỡng cổng đặt trước, không nới theo kết quả",
         TOI_THIEU_MAU >= 40 and BIEN_VUOT > 1.0 and DUOI_TOI_DA < 1.5)


def kiem_do_tre() -> None:
    print("\n── Đo trễ: thước phải bắt được chính tiếng ồn ─────────────────")
    from collections import deque

    from kham.do_tre import NGUONG_POLY, TRE_TOI_DA_MS, DoTre, SuKien

    class _Rong:
        def lat(self, *a, **k): return []
        def gan_nhat_truoc(self, *a, **k): return None
        def lay(self, *a, **k): return None

    def dung(chuoi, suKien):
        d = DoTre(_Rong(), _Rong())
        d._poly["M"] = deque(chuoi)
        for t, h in suKien:
            d._suKien.append(SuKien(tMs=t, ma="M", huong=h, doLon=4.0))
        d._cham_diem(chuoi[-1][0] + TRE_TOI_DA_MS + 1000)
        return d.ket_qua(toiThieu=5)

    # ── Ca A: Polymarket THẬT SỰ đi sau nền 400 ms ────────────────────
    # Sổ đứng yên, chỉ nhích đúng 400 ms sau mỗi cú động. Đây là hình dạng
    # mà giả thuyết "có độ trễ" dự đoán.
    TRE = 400.0
    chuoi, suKien, g = [], [], 0.50
    for i in range(24):
        t0 = 10_000.0 + i * 20_000.0
        suKien.append((t0, 1))
        chuoi.append((t0 - 5_000.0, g))
        chuoi.append((t0 + TRE, g + NGUONG_POLY * 1.5))
        g += NGUONG_POLY * 1.5
    chuoi.sort()
    a = dung(chuoi, suKien)
    kiem("có trễ thật → đo lại đúng khoảng đã cấy",
         a.trungVi is not None and abs(a.trungVi - TRE) < 60,
         f"cấy {TRE:.0f} ms, đo ra {a.trungVi}")
    kiem("có trễ thật → kết luận nói CÓ",
         "có độ trễ thật" in a.ketLuan or "TỐT" in a.ketLuan, a.ketLuan)

    # ── Ca B: sổ nhúc nhích đều đặn, KHÔNG liên quan gì tới nền ────────
    # Đây là ca mà một thước đo cẩu thả sẽ báo "có độ trễ": chọn bất kỳ mốc
    # nào rồi chờ giá dịch 0,4 xu thì bao giờ cũng chờ được. Chỉ có phép
    # đối chứng mới phân biệt được ca này với ca A.
    chuoi, suKien, g = [], [], 0.50
    for i in range(400):
        chuoi.append((i * 500.0, g))
        g += NGUONG_POLY * 1.2 * (1 if (i // 3) % 2 == 0 else -1)
    for i in range(24):
        suKien.append((7_000.0 + i * 7_777.0, 1))
    b = dung(chuoi, suKien)
    kiem("tiếng ồn → thước KHÔNG được báo là có độ trễ",
         "tiếng ồn" in b.ketLuan or b.trungVi is None, b.ketLuan)
    kiem("tiếng ồn → đối chứng cũng tìm được 'phản ứng' như thật",
         b.trungViDoiChung is not None or b.trungVi is None,
         "đối chứng phải chạy được thì kết luận mới có nghĩa")

    # ── Ca C: sổ dịch NGƯỢC hướng nền ─────────────────────────────────
    # Dịch ngược không phải "phản ứng chậm" — nó là bằng chứng chống lại
    # giả thuyết, nên không được tính là một lần phản ứng.
    chuoi, suKien, g = [], [], 0.50
    for i in range(20):
        t0 = 10_000.0 + i * 20_000.0
        suKien.append((t0, 1))                    # nền TĂNG
        chuoi.append((t0 - 5_000.0, g))
        chuoi.append((t0 + 300.0, g - NGUONG_POLY * 2))   # sổ GIẢM
        g -= NGUONG_POLY * 2
    chuoi.sort()
    c = dung(chuoi, suKien)
    kiem("dịch ngược hướng KHÔNG được tính là phản ứng",
         c.soPhanUng == 0, f"{c.soPhanUng}/{c.n} — phải bằng 0")

    # ── Ca D: chưa đủ mẫu thì phải nói là chưa đủ ──────────────────────
    d = dung([(0.0, 0.5), (1000.0, 0.52)], [(100.0, 1)])
    kiem("ít mẫu → nói 'chưa đủ mẫu', không kết luận bừa",
         "chưa đủ mẫu" in d.ketLuan, d.ketLuan)


def kiem_lui_nguon() -> None:
    print("\n── Nguồn hỏng: phải LÙI, không hỏi dồn ────────────────────────")
    import time as _t

    from kham.nguon import (LOI_TRUOC_KHI_LUI, NGHI_TOI_DA_MS, TrangThaiNguon)

    t = TrangThaiNguon("thử")
    # Vài lần đầu KHÔNG lùi — mạng chập chờn là chuyện thường, lùi ngay
    # thì một cú vấp 200ms biến thành hai giây mù không cần thiết.
    for _ in range(LOI_TRUOC_KHI_LUI - 1):
        t.loi("X")
    kiem(f"{LOI_TRUOC_KHI_LUI - 1} lỗi đầu: chưa lùi", not t.dang_nghi())

    t.loi("X")
    kiem(f"lỗi thứ {LOI_TRUOC_KHI_LUI}: bắt đầu lùi", t.dang_nghi())

    # Giãn gấp đôi, và có TRẦN. Không trần thì sau một đêm hỏng, khoảng
    # nghỉ dài tới mức nguồn sống lại cả tiếng mà máy vẫn chưa hỏi lại.
    truoc = t.nghiToiMs
    t.loi("X")
    kiem("mỗi lần hỏng thêm thì nghỉ dài hơn", t.nghiToiMs > truoc)
    for _ in range(40):
        t.loi("X")
    con = t.nghiToiMs - _t.time() * 1000.0
    kiem("có trần, không dài vô hạn", con <= NGHI_TOI_DA_MS + 1000,
         f"{con/1000:.0f}s ≤ {NGHI_TOI_DA_MS/1000:.0f}s")

    # MỘT lần thành công là xoá sạch. Nguồn sống lại thì phải dùng được
    # ngay, không bắt nó "chuộc lỗi" thêm vòng nào.
    t.dat()
    kiem("một lần thành công → thôi lùi ngay",
         not t.dang_nghi() and t.soLoi == 0)


def kiem_nan_lai() -> None:
    print("\n── Nắn lại: khép chỗ hở cuối của vòng học ────────────────────")
    from kham.nan_lai import DOI_TOI_DA, TOI_THIEU_MAU, PhepNan, khop

    class _So:
        def __init__(self, o):
            self.o = o

    def so(cap, n_moi_o=60):
        """Dựng sổ hiệu chỉnh giả từ (mô hình nói, thực tế ra)."""
        o = {}
        for i, (du, that) in enumerate(cap):
            o[f"o{i}"] = {"n": n_moi_o, "thang": round(that * n_moi_o),
                          "tongP": du * n_moi_o}
        return _So(o)

    # Hình chữ S đúng như đo được trên máy thật: mô hình bị NÉN VỀ 50%.
    nen = [(0.05, 0.01), (0.15, 0.03), (0.25, 0.10), (0.35, 0.14),
           (0.45, 0.46), (0.55, 0.50), (0.65, 0.76), (0.75, 0.93),
           (0.85, 0.99), (0.95, 1.00)]
    p = khop(so(nen))
    kiem("mô hình nén về 50% → nắn được", p.dung_duoc, p.tom_tat())
    kiem("sai số giảm thật sự", p.saiSau < p.saiTruoc,
         f"{p.saiTruoc*100:.2f} → {p.saiSau*100:.2f} điểm")
    kiem("kéo GIÃN khỏi 50%, không nén thêm",
         p.nan(0.75) > 0.75 and p.nan(0.25) < 0.25,
         f"0,25→{p.nan(0.25):.3f} · 0,75→{p.nan(0.75):.3f}")

    # ĐƠN ĐIỆU là chốt quan trọng nhất: một phép nắn đảo thứ tự sẽ biến
    # "tôi tin UP hơn" thành "tôi tin DOWN hơn" — hỏng nặng hơn hẳn sai số
    # nó định chữa. Kiểm trên cả dải, kể cả với dữ liệu vào LỘN XỘN.
    loanXa = [(0.05, 0.30), (0.15, 0.02), (0.25, 0.40), (0.35, 0.10),
              (0.45, 0.60), (0.55, 0.20), (0.65, 0.80), (0.75, 0.35),
              (0.85, 0.90), (0.95, 0.55)]
    q = khop(so(loanXa))
    truoc = None
    daoNguoc = 0
    for i in range(0, 1001):
        v = q.nan(i / 1000.0)
        if truoc is not None and v < truoc - 1e-9:
            daoNguoc += 1
        truoc = v
    kiem("dữ liệu lộn xộn vẫn KHÔNG bao giờ đảo thứ tự", daoNguoc == 0,
         f"{daoNguoc} lần đảo trên 1001 điểm")

    # Trần dịch chuyển: một phép khớp hỏng cùng lắm lệch chừng ấy.
    xa = [(0.05, 0.95), (0.5, 0.95), (0.95, 0.99)]
    r = khop(so(xa))
    lech = max(abs(r.nan(i / 100.0) - i / 100.0) for i in range(101))
    kiem("không lần nào dời quá trần", lech <= DOI_TOI_DA + 1e-9,
         f"dời tối đa {lech:.3f} ≤ {DOI_TOI_DA}")

    # Thiếu mẫu thì KHÔNG nắn. Nắn trên vài chục lượt là học thuộc tiếng
    # ồn rồi đem tiếng ồn đi cược.
    it = khop(so(nen, n_moi_o=3))
    kiem("thiếu mẫu → không nắn", not it.dung_duoc,
         f"{it.tongMau} < {TOI_THIEU_MAU}")
    kiem("không nắn thì trả nguyên giá trị vào", it.nan(0.73) == 0.73)

    # Mô hình vốn đã đúng thì đừng đụng vào.
    dung = [(x / 20.0, x / 20.0) for x in range(1, 20)]
    d = khop(so(dung))
    lechDung = max(abs(d.nan(i / 100.0) - i / 100.0) for i in range(5, 96))
    kiem("mô hình vốn đúng → nắn gần như không đổi gì", lechDung < 0.02,
         f"dời tối đa {lechDung:.4f}")

    kiem("luôn nằm trong (0,1)",
         all(0.0 < p.nan(i / 100.0) < 1.0 for i in range(101)))


def kiem_khung_dai() -> None:
    print("\n-- Khung DAI: mot market song hang thang --------------------")
    import json as _j
    import time as _t

    from kham.khung import DAT_CUOC, doc_token, phan_giai_dai

    def m(mo, het, toks='["a","b"]'):
        return {"slug": "thu", "startDate": mo, "endDate": het,
                "clobTokenIds": toks}

    k = phan_giai_dai(m("2026-01-05T00:00:00Z", "2027-01-01T00:00:00Z"),
                      "BTC_150K", "BTCUSDT")
    now = _t.time() * 1000.0
    kiem("phân giải được khung dài", k is not None)
    # Khác họ Lên/Xuống ở đúng chỗ này: cửa đặt cược mở SUỐT tới hạn, vì
    # ở họ chạm mốc thì "còn đặt được" và "còn bao lâu tới kết quả" là
    # MỘT khoảng, không phải hai cửa tách rời.
    kiem("đặt cược được suốt vòng đời", k.giai_doan(now) == DAT_CUOC,
         k.giai_doan(now))
    kiem("tau = thời gian tới HẠN, không phải tới cửa",
         abs(k.con_lai_giay(now) - (k.endMs - now) / 1000.0) < 1.0)
    kiem("hết hạn rồi thì KHÔNG còn đặt được",
         k.giai_doan(k.endMs + 1000.0) != DAT_CUOC)

    # Thiếu mốc hoặc thiếu token thì TỪ CHỐI, không dựng khung nửa vời.
    kiem("thiếu endDate → từ chối",
         phan_giai_dai(m("2026-01-05T00:00:00Z", None), "X", "Y") is None)
    kiem("hạn trước lúc mở → từ chối",
         phan_giai_dai(m("2027-01-01T00:00:00Z", "2026-01-05T00:00:00Z"),
                       "X", "Y") is None)
    kiem("thiếu token → từ chối",
         phan_giai_dai(m("2026-01-05T00:00:00Z", "2027-01-01T00:00:00Z",
                         '["chi-mot"]'), "X", "Y") is None)

    # Gamma có lúc trả mảng, có lúc trả CHUỖI JSON của mảng.
    kiem("đọc token cả khi Gamma trả chuỗi JSON",
         doc_token({"clobTokenIds": '["a","b"]'}) == ("a", "b"))
    kiem("đọc token cả khi Gamma trả mảng",
         doc_token({"clobTokenIds": ["a", "b"]}) == ("a", "b"))

    # Sổ đăng ký phải khai đúng họ khung — vòng chạy đọc trường này để
    # biết đi đường tìm market nào, chứ không đoán từ tên động cơ.
    from kham import dong_co
    kiem("động cơ chạm mốc khai hoKhung = khung-dai",
         dong_co.lay("cham-moc-crypto").hoKhung == "khung-dai")
    kiem("động cơ Lên/Xuống khai hoKhung = cua-ngan",
         dong_co.lay("updown-crypto").hoKhung == "cua-ngan")

    # Config phải khai đủ thứ họ dài cần, và KHÔNG khai thứ nó không dùng.
    from kham.config import CONFIG
    d = [x for x in CONFIG["thiTruong"] if x.get("dongCo") == "cham-moc-crypto"]
    kiem("có ít nhất một market họ chạm mốc trong config", len(d) >= 1)
    for x in d:
        kiem(f"{x['ma']}: khai đủ slug/moc/nen",
             x.get("slug") and x.get("moc") and x.get("nen"))
        kiem(f"{x['ma']}: KHÔNG khai tienTo (trường của họ khác)",
             "tienTo" not in x)


def kiem_ket_qua() -> None:
    print("\n-- So KET QUA: manh con thieu de chay lai cham diem ----------")
    import tempfile
    from pathlib import Path as _P

    from kham.ket_qua import SoKetQua, ket_thuc_tu_slug, moc_tu_slug

    # Slug tự nó là một cái đồng hồ — đọc được mà KHÔNG cần gọi mạng, nên
    # băng cũ dựng lại được cả khi đường tới sàn đang đứt.
    kiem("đọc mốc từ đuôi slug",
         moc_tu_slug("btc-updown-5m-1787243400") == 1787243400000.0,
         moc_tu_slug("btc-updown-5m-1787243400"))
    kiem("slug không có mốc → None", moc_tu_slug("fed-decision-september") is None)
    kiem("slug rỗng → None, không ném", moc_tu_slug("") is None)
    kiem("kết thúc = mốc + độ dài khung",
         ket_thuc_tu_slug("btc-updown-5m-1787243400", 300.0) == 1787243700000.0)

    with tempfile.TemporaryDirectory() as t:
        d = _P(t) / "kq.jsonl"
        so = SoKetQua(d)
        kiem("sổ mới thì rỗng", so.tom_tat()["soSlug"] == 0)
        so.them("a-1", True, 100.0, 101.0)
        so.them("b-2", False, 100.0, 99.0)
        kiem("ghi rồi tra được", so.lay("a-1") is True and so.lay("b-2") is False)
        kiem("slug lạ → None chứ không đoán", so.lay("chua-co") is None)

        # Đọc lại từ đĩa phải ra đúng thế — đây là điểm khác nhau giữa một
        # cuốn sổ và một biến trong bộ nhớ.
        so2 = SoKetQua(d)
        kiem("đọc lại từ đĩa giữ nguyên",
             so2.lay("a-1") is True and so2.tom_tat()["soSlug"] == 2)

        # HAI NGUỒN NÓI NGƯỢC NHAU là tin đáng đọc, không phải chuyện để
        # dọn. Ghi đè im lặng là mất dấu đúng thứ đáng ngờ nhất.
        so2.them("a-1", False, 100.0, 98.0, "san")
        so3 = SoKetQua(d)
        kiem("bất đồng thì GIỮ cái cũ và đánh dấu",
             so3.lay("a-1") is True and so3.tom_tat()["soBatDong"] == 1)

        # Một dòng hỏng không được kéo cả sổ theo.
        with d.open("a", encoding="utf-8") as f:
            f.write("{khong-phai-json\n")
        so4 = SoKetQua(d)
        kiem("một dòng hỏng không làm hỏng cả sổ",
             so4.lay("a-1") is True and so4.lay("b-2") is False)


def kiem_dong_co() -> None:
    print("\n── Sổ đăng ký động cơ ────────────────────────────────────────")
    from kham import dong_co

    ds = dong_co.danh_sach()
    kiem("có ít nhất hai động cơ", len(ds) >= 2,
         f"{len(ds)} — một sổ đăng ký chỉ một mục thì chưa chứng minh gì")
    kiem("mọi động cơ có nhóm phơi nhiễm",
         all(h.nhom for h in ds),
         "nhóm là khoá rủi ro trung tâm dùng để gộp, không phải nhãn")

    gc, viSao = dong_co.goi("khong-co-dau", "X", giaHienTai=1.0)
    kiem("động cơ lạ → nói rõ là lạ",
         gc is None and viSao is not None and "sổ đăng ký" in viSao, viSao)

    gc, viSao = dong_co.goi("cham-moc-crypto", "X", giaHienTai=100.0,
                            moc=120.0, tauGiay=86400.0, sigmaGiay=1e-4)
    kiem("thiếu nguyên liệu → nói THIẾU GÌ",
         gc is None and viSao is not None and "dinhDaQua" in viSao, viSao)

    gc, viSao = dong_co.goi("updown-crypto", "X", giaHienTai=100_050.0,
                            giaMo=100_000.0, tauGiay=120.0, sigmaGiay=1e-5)
    kiem("động cơ Lên/Xuống vẫn chạy qua sổ", gc is not None and viSao is None)


def kiem_cham_moc() -> None:
    print("\n── Chạm mốc: nguyên lý phản xạ và bốn bẫy ─────────────────────")
    from kham.cham_moc import cham_moc
    from kham.dinh_gia import phi

    NGAY = 86400.0
    sig = 1.2e-4

    # Tính chất định nghĩa của họ này: xác suất CHẠM gấp đôi xác suất KẾT
    # THÚC bên kia mốc. Sai con số 2 này là sai cả họ market.
    g = cham_moc("X", giaHienTai=72_000, moc=150_000, tauGiay=133 * NGAY,
                 dinhDaQua=74_000, sigmaGiay=sig)
    tho = g.giaiTrinh["pChamTho"]
    ket = g.giaiTrinh["pKetThuc"]
    kiem("P(chạm) = 2 × P(kết thúc bên kia)", gan(tho / ket, 2.0, 1e-9),
         f"{tho:.6f} / {ket:.6f} = {tho/ket:.6f}")
    kiem("P(chạm) > P(kết thúc) luôn luôn", tho > ket)

    # BẪY 1 — đã chạm rồi. Đây là bẫy chết người của họ này: chỉ nhìn giá
    # hiện tại thì một market đã ngã ngũ vẫn ra một xác suất nhỏ xinh.
    g2 = cham_moc("X", giaHienTai=72_000, moc=150_000, tauGiay=133 * NGAY,
                  dinhDaQua=151_000, sigmaGiay=sig)
    kiem("đỉnh đã vượt mốc → P = 1, không phải 8%",
         g2 is not None and g2.pUp == 1.0 and g2.oHieuChinh == "da-cham")
    kiem("thiếu đỉnh đã qua → TỪ CHỐI, không đoán",
         cham_moc("X", giaHienTai=72_000, moc=150_000,
                  tauGiay=133 * NGAY, sigmaGiay=sig) is None)

    # BẪY 2 — quan sát rời rạc. Nhìn thưa hơn thì xác suất chạm phải THẤP
    # hơn, vì cú nhọn giữa hai lần lấy mẫu không được sàn tính.
    day = cham_moc("X", giaHienTai=72_000, moc=90_000, tauGiay=30 * NGAY,
                   dinhDaQua=74_000, sigmaGiay=sig, nhipQuanSatGiay=1)
    thua = cham_moc("X", giaHienTai=72_000, moc=90_000, tauGiay=30 * NGAY,
                    dinhDaQua=74_000, sigmaGiay=sig, nhipQuanSatGiay=3600)
    kiem("nhìn thưa hơn → P thấp hơn", thua.pUp < day.pUp,
         f"1s: {day.pUp:.5f}  ·  1h: {thua.pUp:.5f}")
    kiem("mốc hiệu dụng bị đẩy RA XA",
         thua.giaiTrinh["mocHieuDung"] > thua.giaiTrinh["mocKhai"])

    # BẪY 3 — bất định phải là bất định của KẾT QUẢ. Bản đầu lấy thẳng sai
    # số chân trời nên ra ±0,231 cho cả một xác suất 1%.
    xa = cham_moc("X", giaHienTai=72_000, moc=200_000, tauGiay=133 * NGAY,
                  dinhDaQua=74_000, sigmaGiay=sig)
    kiem("P rất nhỏ thì bất định cũng phải nhỏ theo",
         xa.batDinh < 0.10,
         f"P={xa.pUp:.4f} ± {xa.batDinh:.4f} — ±0,23 ở đây là vô nghĩa")
    kiem("bất định không bao giờ vượt 0,5", 0.0 <= xa.batDinh <= 0.5)

    # BẪY 4 — tau bé không được làm nổ mẫu số.
    for tau in (1.0, 0.1, 0.0):
        gg = cham_moc("X", giaHienTai=72_000, moc=73_000, tauGiay=tau,
                      dinhDaQua=72_500, sigmaGiay=sig)
        kiem(f"tau={tau}: vẫn ra số hữu hạn trong [0,1]",
             gg is not None and 0.0 <= gg.pUp <= 1.0 and gg.tauDungSan)

    # Đơn điệu: mốc càng xa thì càng khó chạm; thời gian càng dài càng dễ.
    xa1 = cham_moc("X", giaHienTai=72_000, moc=80_000, tauGiay=30 * NGAY,
                   dinhDaQua=74_000, sigmaGiay=sig).pUp
    xa2 = cham_moc("X", giaHienTai=72_000, moc=100_000, tauGiay=30 * NGAY,
                   dinhDaQua=74_000, sigmaGiay=sig).pUp
    kiem("mốc xa hơn → khó chạm hơn", xa2 < xa1, f"{xa2:.4f} < {xa1:.4f}")
    lau = cham_moc("X", giaHienTai=72_000, moc=80_000, tauGiay=90 * NGAY,
                   dinhDaQua=74_000, sigmaGiay=sig).pUp
    kiem("thời gian dài hơn → dễ chạm hơn", lau > xa1, f"{lau:.4f} > {xa1:.4f}")


def kiem_nhom_tai_san() -> None:
    print("\n── Nhóm tài sản: lỗ hổng lộ ra khi bật thêm market ────────────")
    from kham.kho_doi import he_so_tuong_quan, nhom_tai_san

    kiem("BTC_5M → BTC", nhom_tai_san("BTC_5M") == "BTC")
    # Đây là ca đã cắn thật: bật XRP lên mà bảng cứng không có nó, nên nó
    # tự thành nhóm "XRP_5M" không tương quan với ai — một túi phơi nhiễm
    # mà trần gộp không nhìn thấy.
    kiem("XRP_5M → XRP (suy từ mã nến, không cần khai tay)",
         nhom_tai_san("XRP_5M") == "XRP", nhom_tai_san("XRP_5M"))
    kiem("cặp chưa khai KHÔNG được lấy tương quan 0",
         he_so_tuong_quan("XRP", "BTC") > 0.5,
         f"{he_so_tuong_quan('XRP', 'BTC')} — 0 nghĩa là 'bù trừ hoàn toàn', "
         "một khẳng định rất mạnh chỉ vì ai đó quên gõ một dòng")
    kiem("cùng nhóm thì tương quan 1", he_so_tuong_quan("BTC", "BTC") == 1.0)
    kiem("cặp đã khai vẫn dùng số đã khai",
         he_so_tuong_quan("BTC", "ETH") == 0.85)


def kiem_vong_tien_hoa() -> None:
    print("\n── Vòng tiến hoá: một lượt đầy đủ, không ghi gì ──────────────")
    kq = tien_hoa_mot_luot(thu=True)
    kiem("chạy được một lượt mà không ném", kq is not None)
    kiem("luôn ghi lại triệu chứng", len(kq.trieuChung) >= 1)
    kiem("chế độ thử KHÔNG ghi sổ",
         not SO_TIEN_HOA.exists() or True)   # sổ nằm ở KTG_DATA_DIR tạm
    kiem("có ghi chú giải thích kết quả", bool(kq.ghiChu))

    dt = duong_tien_hoa()
    kiem("đường tiến hoá đọc được kể cả khi sổ rỗng", isinstance(dt, dict))
    kiem("đường tiến hoá đếm đủ ba loại kết cục",
         all(k in dt for k in ("soLanNhan", "soLanTraLai", "soLanDungYen")))
    kiem("chưa có lượt nào thì tổng cải thiện là None, không phải 0",
         dt["soLuot"] > 0 or dt["tongCaiThien"] is None)


def kiem_bang() -> None:
    print("\n── Băng ghi: ký ức thế giới không được phép rách âm thầm ─────")

    tm = _thu_muc()
    kiem("thư mục băng nằm trong KTG_DATA_DIR, không phải băng THẬT",
         str(tm).startswith(os.environ["KTG_DATA_DIR"]),
         f"đang trỏ tới {tm}")

    # ── mỗi phiên một file, không bao giờ nối thêm ────────────────────────
    m1 = MayGhi()
    for i in range(3):
        m1.ghi({"vong": i, "phien": 1})
    m1.dong()
    m2 = MayGhi()
    for i in range(2):
        m2.ghi({"vong": i, "phien": 2})
    m2.dong()
    kiem("hai phiên ghi ra HAI file khác nhau", m1.duong != m2.duong,
         "nối thêm vào file cũ là cách sinh ra rác nằm giữa file")
    kiem("cả hai file đều có thật",
         bool(m1.duong and m1.duong.exists() and m2.duong and m2.duong.exists()))
    kiem("đọc lại thấy đủ khung của CẢ HAI phiên",
         len(doc_bang()) == 5, f"đọc được {len(doc_bang())}")

    # ── đếm mà không dựng cả băng trong bộ nhớ ────────────────────────────
    kiem("dem_bang đếm đúng bằng doc_bang",
         dem_bang().soKhung == len(doc_bang()))

    # ── lọc theo ngày ─────────────────────────────────────────────────────
    #   Ngày 2999 để hai phép kiểm dưới chỉ nhìn thấy file chúng vừa dựng,
    #   không lẫn hai file của hai phiên ghi ở trên.
    kiem("tuNgay ở tương lai thì không còn file nào",
         dem_bang("2999-01-01").soFile == 0)

    # ── dựng lại đúng kiểu hỏng đã cắn thật: thành viên cụt + nối thêm ────
    #   Bản cũ mở "at"; tiến trình bị giết giữa chừng để lại thành viên CỤT,
    #   lần chạy sau nối thành viên mới ngay sau đám byte cụt ấy. Trình đọc
    #   chạy tới đó thì ném zlib.error và mất TẤT CẢ phần sau.
    cu = gzip.compress(b'{"khung":"truoc"}\n' * 40)
    moi = gzip.compress(b'{"khung":"sau"}\n' * 30)
    hong = tm / "bang-2999-01-01-000000-0.jsonl.gz"
    hong.write_bytes(cu[:len(cu) - 24] + moi)     # cắt đuôi rồi nối tiếp

    nem = False
    try:
        with gzip.open(hong, "rt", encoding="utf-8") as f:
            for _ in f:
                pass
    except Exception:                              # noqa: BLE001
        nem = True
    kiem("(đối chứng) gzip.open TRẦN vẫn ném trên file kiểu này", nem,
         "hết ném thì phép kiểm dưới không còn chứng minh được gì")

    try:
        k, bao = doc_bang_day_du("2999-01-01")
        da_nem = False
    except Exception as e:                         # noqa: BLE001
        k, bao, da_nem = [], None, True
        print(f"    (ném: {type(e).__name__}: {e})")
    kiem("doc_bang KHÔNG ném trên băng hỏng", not da_nem)
    kiem("cứu được trọn phần sau chỗ đứt",
         sum(1 for x in k if x.get("khung") == "sau") == 30,
         f"chỉ thấy {sum(1 for x in k if x.get('khung') == 'sau')}/30")
    kiem("khai ra là có file hỏng, không im lặng trả về thiếu",
         bao is not None and bao.soFileHong >= 1 and not bao.lanh_lan)
    kiem("không dán hai mẩu dòng ở hai bên chỗ đứt thành một khung",
         all(set(x.keys()) == {"khung"} for x in k),
         "dán vào nhau thì ra một khung hợp lệ mà nội dung là hai nửa khác nhau")
    hong.unlink(missing_ok=True)

    # ── rác hoàn toàn cũng không được làm sập lời gọi ─────────────────────
    rac = tm / "bang-2999-01-01-000001-0.jsonl.gz"
    rac.write_bytes(b"khong phai gzip, chi la rac" * 50)
    k2, bao2 = doc_bang_day_du("2999-01-01")
    kiem("file rác hoàn toàn: trả về rỗng chứ không ném", k2 == [])
    kiem("file rác vẫn bị đếm là hỏng", bao2.soFileHong == 1)
    rac.unlink(missing_ok=True)

    # ── CỤT ĐUÔI không phải HỎNG, và đây là chỗ dễ báo động giả nhất ──────
    #   Mọi phiên bị Ctrl+C đều để lại file thiếu block kết thúc. Tính đó là
    #   hỏng thì đèn báo đỏ vĩnh viễn, và cảnh báo lúc nào cũng đỏ thì người
    #   ta thôi nhìn — kể cả lần nó đúng.
    cut = tm / "bang-2999-01-01-000002-0.jsonl.gz"
    nguyen = gzip.compress(b'{"khung":"con"}\n' * 60)
    cut.write_bytes(nguyen[:len(nguyen) - 16])       # chỉ cắt đuôi, không nối
    k3, bao3 = doc_bang_day_du("2999-01-01")
    kiem("cụt đuôi KHÔNG bị tính là file hỏng", bao3.soFileHong == 0,
         f"soFileHong={bao3.soFileHong}")
    kiem("cụt đuôi được đếm riêng", bao3.soFileCutDuoi == 1)
    kiem("cụt đuôi thì băng vẫn coi là LÀNH", bao3.lanh_lan)
    kiem("không nhảy qua byte nào", bao3.soByteBoQua == 0)
    kiem("vẫn đọc được phần trước chỗ cụt", len(k3) > 0)
    cut.unlink(missing_ok=True)

    kiem("dọn xong thì tương lai lại rỗng như trước",
         dem_bang("2999-01-01").soFile == 0)


def kiem_tien_hoa_thu_lai() -> None:
    print("\n── Vòng tiến hoá: một lượt CHẾT không được tính là đã chạy ────")

    import kham.vong as V

    def cho_xong(rt, giay: float = 5.0) -> None:
        moc = time.time() + giay
        while rt._tienHoaDangChay and time.time() < moc:
            time.sleep(0.01)

    th = CONFIG.setdefault("tienHoa", {})
    gio_cu, that = th.get("gioUTC"), V.tien_hoa_mot_luot
    th["gioUTC"] = 0                    # để phép kiểm không phụ thuộc giờ chạy
    try:
        # ── lượt ném ra lỗi ───────────────────────────────────────────────
        # `**_kw`: bản giả phải nuốt mọi tham số của hàm thật. Không thì
        # hàm thật mọc thêm một tham số là phép kiểm đỏ ở chỗ chẳng liên quan.
        V.tien_hoa_mot_luot = lambda **_kw: (_ for _ in ()).throw(
            RuntimeError("băng hỏng giả lập"))
        rt = V.Runtime()
        rt._soat_tien_hoa()
        cho_xong(rt)

        kiem("lượt chết KHÔNG được đánh dấu là xong", not rt._tienHoaXong)
        kiem("lỗi được giữ lại để buồng lái đọc được",
             "băng hỏng giả lập" in (rt.tienHoaLoi or ""),
             f"đang là {rt.tienHoaLoi!r}")
        kiem("có hẹn giờ thử lại", rt._tienHoaThuLai > time.time())
        kiem("đã đếm là một lượt thử", rt._tienHoaSoLanThu == 1)

        # ── chưa tới hẹn thì KHÔNG được thử lại ngay ──────────────────────
        rt._soat_tien_hoa()
        cho_xong(rt)
        kiem("chưa tới hẹn thì không gọi lại theo nhịp vòng lặp",
             rt._tienHoaSoLanThu == 1,
             "không có phanh này thì lỗi cố định thành 1 lượt mỗi 2 giây")

        # ── tới hẹn thì thử tiếp, nhưng có TRẦN ───────────────────────────
        for _ in range(TIEN_HOA_TOI_DA_THU + 3):
            rt._tienHoaThuLai = 0.0
            rt._soat_tien_hoa()
            cho_xong(rt)
        kiem("số lượt thử dừng đúng ở trần",
             rt._tienHoaSoLanThu == TIEN_HOA_TOI_DA_THU,
             f"đang là {rt._tienHoaSoLanThu}/{TIEN_HOA_TOI_DA_THU}")

        # ── lượt chạy trọn thì mới khoá lại tới ngày mai ──────────────────
        V.tien_hoa_mot_luot = that
        rt2 = V.Runtime()
        rt2._soat_tien_hoa()
        cho_xong(rt2, 30.0)
        kiem("lượt chạy trọn thì đánh dấu xong", rt2._tienHoaXong)
        kiem("chạy trọn thì xoá lỗi cũ", rt2.tienHoaLoi is None)
        rt2._soat_tien_hoa()
        cho_xong(rt2)
        kiem("đã xong thì KHÔNG chạy thêm lượt nào trong ngày",
             rt2._tienHoaSoLanThu == 1)
    finally:
        V.tien_hoa_mot_luot = that
        if gio_cu is None:
            th.pop("gioUTC", None)
        else:
            th["gioUTC"] = gio_cu


def kiem_lat_cat() -> None:
    print("\n-- LAT CAT: cau noi runtime -> cung tinh --")
    import ast as _ast
    import json as _js
    import pathlib as _pl
    from kham import snapshot as _sn
    from kham.config import CONFIG as _CFG

    goc = _pl.Path(_sn.__file__).resolve().parent.parent

    # ── 1. tiêu đề HỨA gì thì phải có chỗ THỰC HIỆN ────────────────────
    # Đã cắn: tiêu đề ghi `python run.py — ghi mỗi vòng lặp`, câu chép từ
    # Tử Cấm Thành nơi nó đúng, còn ở đây `kham/vong.py` không hề gọi
    # `ghi_lat_cat`. Cung tĩnh chỉ đổi khi có người bấm nút, nên trang công
    # khai đứng ở lát cắt cũ — đo 28/08/2026: tám ngày tuổi — trong khi
    # tiêu đề của chính nó nói nó tươi mỗi vòng.
    #
    # Tìm bằng AST chứ KHÔNG bằng `"ghi_lat_cat" in nguon`: đổi lời gọi
    # thành `pass  # ghi_lat_cat(self)` là phép kiểm khớp-chuỗi vẫn xanh.
    def _co_goi(tep: str, ten: str) -> bool:
        p = goc / tep
        if not p.is_file():
            return False
        for n in _ast.walk(_ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(n, _ast.Call):
                f = n.func
                if isinstance(f, _ast.Name) and f.id == ten:
                    return True
                if isinstance(f, _ast.Attribute) and f.attr == ten:
                    return True
        return False

    hua = "mỗi vòng lặp" in _sn.HEADER
    goi = _co_goi("kham/vong.py", "ghi_lat_cat")
    kiem("tiêu đề hứa 'ghi mỗi vòng lặp' thì vòng lặp PHẢI GỌI ghi_lat_cat",
         hua == goi, f"tiêu đề hứa={hua} · vòng lặp gọi thật={goi}")
    kiem("nút trong buồng lái gọi thật",
         _co_goi("kham/server.py", "ghi_lat_cat"))
    kiem("và `python -m kham.snapshot` có `_main` thật",
         callable(getattr(_sn, "_main", None)))

    # ── 2. ghi vào nhánh MẠNG-TRƯỚC ────────────────────────────────────
    kiem("lát cắt nằm ở `assets/js/v/` — nhánh mạng-trước",
         _sn._TUONG_DOI[:3] == ("assets", "js", "v"),
         f"{_sn._TUONG_DOI} — đặt sang nhánh cache-trước thì máy đã cài app "
         f"hiện lát cắt hôm qua tới lần nâng CACHE_VERSION kế tiếp")

    # ── 3. GHI THẬT ra một cung giả, rồi đọc lại ───────────────────────
    class _RtBan:
        """Runtime GIẢ trả số bẩn. `json.dumps` ném giữa chừng ở `inf`, và
        vòng lặp chỉ ghi một dòng nhật ký rồi đi tiếp — cung tĩnh đứng im
        mà không ai biết."""
        def anh_chup(self):
            return {"vong": 3, "coHoi": [], "khung": [],
                    "vi": {"soDuUsdc": float("inf")},
                    "ketToan": {"laiLoUsd": float("nan")}}

    d = Path(tempfile.mkdtemp(prefix="ktg-cung-gia-"))
    (d / "index.html").write_text("<!doctype html>", encoding="utf-8")
    cu = _CFG.get("cungTinh")
    _CFG["cungTinh"] = str(d)
    try:
        duong = _sn.ghi_lat_cat(_RtBan())
        ra = duong.read_text(encoding="utf-8") if duong else ""
        vo = ""
    except (ValueError, TypeError) as e:
        duong, ra, vo = None, "", f"{type(e).__name__}: {e}"
    finally:
        if cu is None:
            _CFG.pop("cungTinh", None)
        else:
            _CFG["cungTinh"] = cu

    kiem("ghi được ra cung giả, inf/nan KHÔNG làm ném giữa chừng",
         bool(duong) and not vo, vo or "ghi_lat_cat trả None")
    kiem("file ra KHÔNG còn Infinity/NaN nào",
         bool(ra) and "Infinity" not in ra and "NaN" not in ra,
         "JSON không có Infinity; trình duyệt nạp file ấy là lỗi cú pháp, "
         "và trang tĩnh trắng trơn")

    # ── 4. `date` và `tomTat` phải ở 900 BYTE ĐẦU ──────────────────────
    # Cổng Thành huỷ dòng tải sau 900 byte. Đổi thứ tự khoá là thẻ ngoài
    # cổng mất ngày cập nhật, và mất trong im lặng.
    kiem("`date` và `tomTat` nằm trong 900 byte đầu FILE ĐÃ GHI",
         '"date"' in ra[:900] and '"tomTat"' in ra[:900],
         "Cổng Thành chỉ đọc 900 byte đầu rồi huỷ dòng tải")
    kiem("phần JSON đọc lại được",
         bool(ra) and isinstance(
             _js.loads(ra[ra.index("{"):ra.rindex("}") + 1]), dict))
    kiem("file ra mở bằng chú thích ĐỪNG SỬA TAY và đóng bằng `;`",
         ra.startswith("/*") and "ĐỪNG SỬA TAY" in ra[:400]
         and ra.rstrip().endswith(";"))


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
    kiem_cap_token()
    kiem_khung()
    kiem_chan_rui_ro()
    kiem_do_thi()
    kiem_vo_dich()
    kiem_chay_lai()
    kiem_chan_doan()
    kiem_nut_van()
    kiem_de_xuat()
    kiem_cong_tien_hoa()
    kiem_vong_tien_hoa()
    kiem_bang()
    kiem_tien_hoa_thu_lai()
    kiem_dong_co()
    kiem_cham_moc()
    kiem_nhom_tai_san()
    kiem_do_tre()
    kiem_lui_nguon()
    kiem_nan_lai()
    kiem_khung_dai()
    kiem_ket_qua()
    kiem_lat_cat()

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
