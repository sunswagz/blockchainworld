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
                       doc_bang, doc_bang_day_du, NguonKhung)
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
from kham.chay_lai import mot_luot as chay_lai_mot_luot          # noqa: E402
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
    re.ghi_lai_lo(-re.tranLoNgayUsd - 1)
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

    # ── biên đương kim cũng phải đóng ở CẢ HAI DẤU ───────────────────
    #
    # Cùng khuôn với `tien_hoa`: `td < dk * 1,15` lật ngược khi `dk` âm,
    # nên đương kim −$10 cho một thách đấu −$11 lên ngôi. Hai chỗ một
    # khuôn, nên canh cả hai.
    from kham.vo_dich import BIEN_VUOT as BV

    def len_ngoi(dk_: float, td_: float) -> bool:
        return not (td_ <= dk_ + abs(dk_) * (BV - 1.0))

    kiem("đương kim dương: hơn chưa đủ biên thì GIỮ NGÔI",
         not len_ngoi(10.0, 11.0))
    kiem("đương kim dương: hơn đủ biên thì ĐỔI NGÔI", len_ngoi(10.0, 12.0))
    kiem("đương kim ÂM: thách đấu TỆ HƠN không được lên ngôi",
         not len_ngoi(-10.0, -11.0))
    kiem("đương kim ÂM: khá hơn đủ biên thì ĐỔI NGÔI",
         len_ngoi(-10.0, -8.0))

    GOC_MA = Path(__file__).resolve().parent.parent
    vd = (GOC_MA / "kham" / "vo_dich.py").read_text(encoding="utf-8")
    ma = chr(10).join(d.split("#", 1)[0] for d in vd.splitlines())
    kiem("vo_dich.py KHÔNG còn nhân thẳng `dk.kyVong * BIEN_VUOT`",
         "dk.kyVong * BIEN_VUOT" not in ma)
    kiem("mà dùng biên theo ĐỘ LỚN",
         "abs(dk.kyVong) * (BIEN_VUOT - 1.0)" in ma)

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
            "ma": "BTC_5M", "giaiDoan": "quan-sat",
            "giaNen": 100_000 + d * 60, "giaMo": 100_000,
            "sigmaGiay": sig, "conLaiGiay": 120.0, "upThang": d > 0,
            "so": {"UP": {"luc": 1, "bid": [{"gia": 0.40, "luong": 500}],
                          "ask": [{"gia": 0.42, "luong": 500}]},
                   # Sổ DOWN là ẢNH SOI GƯƠNG của sổ UP: mua UP ≡ bán
                   # DOWN nên UP_bid + DOWN_ask = 1. Bản trước để
                   # 0,55/0,57 cạnh UP 0,40/0,42 — một cặp sổ KHÔNG THỂ
                   # tồn tại trên sàn thật.
                   "DOWN": {"luc": 1, "bid": [{"gia": 0.58, "luong": 500}],
                            "ask": [{"gia": 0.60, "luong": 500}]}}}]})
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
        # `quan-sat`: đây là loại dòng DUY NHẤT chấm điểm được. Dòng
        # cửa đặt cược mang `giaMo` không phải strike, và `chay_lai`
        # cố ý từ chối chúng.
        ra.append({"thiTruong": [{
            "ma": "BTC_5M", "giaiDoan": "quan-sat",
            "giaNen": 100_000 + d * 60, "giaMo": 100_000,
            "sigmaGiay": sig, "conLaiGiay": 120.0, "upThang": d > 0,
            "so": {"UP": {"luc": 1, "thangCho": False, "dungDuoc": True,
                          "bid": [{"gia": 0.40, "luong": 900}],
                          "ask": [{"gia": 0.42, "luong": 900}]},
                   "DOWN": {"luc": 1, "thangCho": False, "dungDuoc": True,
                            # Sổ DOWN phải là ẢNH SOI GƯƠNG của sổ UP:
                            # mua UP ≡ bán DOWN, nên UP_ask + DOWN_bid = 1.
                            # Bản trước để 0,55/0,57 cạnh UP 0,40/0,42 —
                            # một cặp sổ KHÔNG THỂ tồn tại trên sàn thật,
                            # và một fixture không thể tồn tại thì phép
                            # kiểm dựng trên nó chứng minh được rất ít.
                            "bid": [{"gia": 0.58, "luong": 900}],
                            "ask": [{"gia": 0.60, "luong": 900}]}}}]})
    return ra


def _bang_sat_bien(n=60):
    """Băng đặt lợi thế SÁT BIÊN, mỗi khung một slug riêng.

    `_bang_gia` để giá lệch xa nên xác suất gần 1 và mọi bộ tham số đều
    qua sàng như nhau — dùng nó để đo một nút chỉ dịch xác suất vài điểm
    thì phép kiểm xanh vì lý do sai. Ở đây giá chỉ lệch 60 đô với 120
    giây còn lại (pUp quãng 0,65) và giá chào quét dần qua vùng quyết
    định, nên một cú nắn vài điểm LÀ đủ để đổi câu trả lời.
    """
    sig = 0.55 / math.sqrt(365 * 24 * 3600)
    ra = []
    for i in range(n):
        ask = 0.50 + (i % 30) * 0.01
        ra.append({"thiTruong": [{
            "ma": "BTC_5M", "giaiDoan": "quan-sat",
            "slug": f"btc-updown-5m-{1787243400 + i * 300}",
            "giaNen": 100_060, "giaMo": 100_000, "sigmaGiay": sig,
            "conLaiGiay": 120.0, "upThang": True,
            "so": {"UP": {"luc": 1, "thangCho": False, "dungDuoc": True,
                          "bid": [{"gia": round(ask - 0.02, 4), "luong": 900}],
                          "ask": [{"gia": round(ask, 4), "luong": 900}]},
                   "DOWN": {"luc": 1, "thangCho": False, "dungDuoc": True,
                            "bid": [{"gia": round(0.96 - ask, 4), "luong": 900}],
                            "ask": [{"gia": round(0.98 - ask, 4), "luong": 900}]}}}]})
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


def kiem_cong_chay_may_dang_chay() -> None:
    """Cổng phải chạy lại ĐÚNG cỗ máy đang chạy — tức là có phép nắn.

    Vòng chạy thật nắn `gc.pUp` bằng `self.phepNan` trước khi cân lợi.
    Cổng thì dựng `ThamSo` không có `phepNan`, nên nó đo một cỗ máy thô.
    Hai tầng hậu quả, tầng dưới nặng hơn: nút `nanLai.heSoGiamChan` vặn
    kiểu gì cũng không đổi kết quả (lượt chạy có nắn đâu mà giảm chấn),
    và "đương nhiệm" mà cổng đo không phải đương nhiệm.
    """
    print("\n-- Cong phai do CO MAY DANG CHAY, khong phai may tho -------")

    import kham.tien_hoa as TH
    from kham.chan_doan import doc_tham_so
    from kham.config import CONFIG as _CF
    from kham.nan_lai import khop

    class _So:
        def __init__(self, o):
            self.o = o

    # Sổ hiệu chỉnh hình chữ S — mô hình bị nén về 50%, đúng hình đo được
    # trên máy thật. Đủ mẫu để `khop()` cho ra một phép nắn dùng được.
    nen = [(0.05, 0.01), (0.15, 0.03), (0.25, 0.10), (0.35, 0.14),
           (0.45, 0.46), (0.55, 0.50), (0.65, 0.76), (0.75, 0.93),
           (0.85, 0.99), (0.95, 1.00)]
    o = {}
    for i, (du, that) in enumerate(nen):
        o[f"o{i}"] = {"n": 60, "thang": round(that * 60), "tongP": du * 60}
    hc_gia = _So(o)

    cu_hc = TH.HieuChinh
    TH.HieuChinh = lambda *a, **k: hc_gia
    cu_gc = (_CF.get("nanLai") or {}).get("heSoGiamChan")
    try:
        pn = khop(hc_gia)
        kiem("dựng được phép nắn dùng được để thử cổng", pn.dung_duoc,
             f"sai {pn.saiTruoc:.4f} → {pn.saiSau:.4f}")

        # Băng phải đặt lợi thế SÁT BIÊN mới đo được nút này. Băng chuẩn
        # của bộ kiểm có giá lệch xa, xác suất gần 1, nên nắn kiểu gì
        # cũng qua sàng như nhau và phép kiểm sẽ xanh vì lý do sai.
        khung = _bang_sat_bien(60)
        ts_tho = ThamSo("thô", 0.005, 0.005)
        ts_nan = ThamSo("nắn", 0.005, 0.005, phepNan=pn)
        k_tho, k_nan = mot_luot(khung, ts_tho), mot_luot(khung, ts_nan)
        kiem("phép nắn có tác dụng thật lên lượt chạy lại",
             (k_tho.soQuaSang, round(k_tho.tongLaiLo, 6))
             != (k_nan.soQuaSang, round(k_nan.tongLaiLo, 6)),
             f"thô {k_tho.soQuaSang}/{k_tho.tongLaiLo:.4f} vs "
             f"nắn {k_nan.soQuaSang}/{k_nan.tongLaiLo:.4f}")

        # Và cổng, khi thử chính nút giảm chấn, phải đo ra HAI bên khác nhau.
        _CF.setdefault("nanLai", {})["heSoGiamChan"] = 0.30
        hien = doc_tham_so("nanLai.heSoGiamChan")
        kiem("đọc được nút giảm chấn từ config", hien == 0.30, hien)

        dx = DeXuat("nanLai.heSoGiamChan", 0.30, 1.00, "mo-hinh-lech", "thử")
        r = thu_mot_de_xuat(khung, dx)
        A, B = r["A"], r["B"]
        kiem("vặn giảm chấn thì cổng đo ra HAI bên KHÁC nhau",
             (A["soQuaSang"], round(A["kyVong"], 8))
             != (B["soQuaSang"], round(B["kyVong"], 8)),
             f"A {A['soQuaSang']}/{A['kyVong']:.6f} · "
             f"B {B['soQuaSang']}/{B['kyVong']:.6f} — bằng nhau nghĩa là "
             "cổng đang chạy một cỗ máy không có phép nắn")
        kiem("cổng trả về phán quyết đầy đủ",
             isinstance(r.get("cho"), bool) and "lyDo" in r)
    finally:
        TH.HieuChinh = cu_hc
        if cu_gc is None:
            (_CF.get("nanLai") or {}).pop("heSoGiamChan", None)
        else:
            _CF["nanLai"]["heSoGiamChan"] = cu_gc


def kiem_do_ung_vien() -> None:
    """Cùng một bệnh, đã trả lại rồi thì phải ra ứng viên KHÁC.

    Bản trước của người đề xuất tất định là một vòng lặp chết: triệu
    chứng nặng nhất → nút gợi ý đầu tiên → một bước → trả về ngay. Tức là
    ĐÚNG MỘT ứng viên, mỗi ngày, mãi mãi. Đã đo tận mắt hai lượt liên tiếp
    trên băng thật đề nghị y hệt nhau và bị cổng trả lại y hệt nhau. Sổ
    tiến hoá dài thêm mỗi ngày một dòng giống hệt dòng trước.
    """
    print("\n-- De xuat: da tra lai roi thi phai do cho khac -----------")

    tc = [TrieuChung("mo-hinh-lech", 2, "", {"chieu": "RỤT RÈ QUÁ"},
                     ["nanLai.heSoGiamChan", "dinhGia.batDinhToiThieu"])]

    d1 = de_xuat_tat_dinh(tc, set())
    kiem("có ứng viên đầu tiên", len(d1) == 1)
    kiem("nút giảm chấn được với tới",
         d1[0].nut == "nanLai.heSoGiamChan",
         f"đề xuất {d1[0].nut} — nút này từng nằm trong bảng mà "
         "KHÔNG triệu chứng nào trỏ tới, nên không ai vặn được")
    kiem("chữa lệch bằng giảm chấn là đi XA HƠN, không phải rút về",
         d1[0].denGiaTri > d1[0].tuGiaTri,
         f"{d1[0].tuGiaTri} → {d1[0].denGiaTri}")

    # Đã trả lại ứng viên đó → phải ra một ứng viên khác, không lặp lại.
    da = {(d1[0].nut, round(d1[0].denGiaTri, 10))}
    d2 = de_xuat_tat_dinh(tc, da)
    kiem("không đề nghị lại thứ vừa bị trả lại", len(d2) == 1 and
         (d2[0].nut, round(d2[0].denGiaTri, 10)) not in da,
         f"{d2[0].nut}={d2[0].denGiaTri}" if d2 else "rỗng")

    # Dò cạn dần: gom hết ứng viên bằng cách trả lại từng cái một.
    da2, thay = set(), []
    for _ in range(40):
        d = de_xuat_tat_dinh(tc, da2)
        if not d:
            break
        thay.append((d[0].nut, d[0].denGiaTri))
        da2.add((d[0].nut, round(d[0].denGiaTri, 10)))
    kiem("dò được NHIỀU ứng viên chứ không phải một", len(thay) >= 4,
         f"{len(thay)} ứng viên: {thay[:5]}")
    kiem("dò tới cả nút thứ hai, không kẹt ở nút đầu",
         len({n for n, _ in thay}) >= 2, str({n for n, _ in thay}))
    kiem("hết ứng viên thì trả RỖNG, không lặp lại cái cũ",
         de_xuat_tat_dinh(tc, da2) == [])

    # Giá trị đề xuất phải bám lưới bước, không mang rác dấu phẩy động.
    xau = [v for _n, v in thay if len(repr(float(v))) > 8]
    kiem("mọi giá trị đề xuất đều bám lưới bước", not xau,
         f"còn {xau[:3]} — hai lượt cùng một chỗ mà ra hai chuỗi khác "
         "nhau thì trí nhớ đã-thử-gì không nhận ra chúng là một")


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

    # ── biên phải đóng ở CẢ HAI DẤU ──────────────────────────────────
    #
    # `B < A * BIEN_VUOT` đúng khi A dương và LẬT NGƯỢC khi A âm: đương
    # nhiệm −$10 thì A×1,1 = −$11, nên ứng viên −$10,5 — TỆ HƠN — lọt
    # qua. Biên "phải hơn 10%" thành "được kém tới 10%", và nó lật đúng
    # vào lúc cần cổng nhất: khi cỗ máy đang lỗ.
    def qua(a: float, b: float) -> bool:
        """Cổng có cho ứng viên `b` qua không, với đương nhiệm `a`."""
        return not (b <= a + abs(a) * (BIEN_VUOT - 1.0))

    kiem("A dương: hơn chưa đủ biên thì TRẢ LẠI", not qua(10.0, 10.5))
    kiem("A dương: hơn đủ biên thì NHẬN", qua(10.0, 11.5))
    kiem("A ÂM: ứng viên TỆ HƠN phải TRẢ LẠI", not qua(-10.0, -10.5))
    kiem("A ÂM: khá hơn chưa đủ biên thì TRẢ LẠI", not qua(-10.0, -9.5))
    kiem("A ÂM: khá hơn đủ biên thì NHẬN", qua(-10.0, -8.5))
    kiem("A = 0: ứng viên 0 KHÔNG được qua với biên bằng không",
         not qua(0.0, 0.0))
    kiem("A = 0: ứng viên dương thì NHẬN", qua(0.0, 5.0))

    # Và mã nguồn phải thật sự dùng công thức ấy, không phải nhân thẳng.
    GOC_MA = Path(__file__).resolve().parent.parent
    th = (GOC_MA / "kham" / "tien_hoa.py").read_text(encoding="utf-8")
    ma = chr(10).join(d.split("#", 1)[0] for d in th.splitlines())
    kiem("mã KHÔNG còn nhân thẳng `A * BIEN_VUOT`",
         'kyVong"] * BIEN_VUOT' not in ma)
    kiem("mà dùng biên theo ĐỘ LỚN",
         'abs(A["kyVong"]) * (BIEN_VUOT - 1.0)' in ma)


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


def _tao_lap_thu(lc) -> list:
    """Chạy riêng ngón `tạo lập` với một lát cắt đồng hồ cho trước.

    Dùng để chứng minh: lát cắt sai giai đoạn thì ngón nghề câm, không
    báo lỗi, không để lại dấu vết nào.
    """
    from kham.chien_thuat import BoiCanh as _BC
    from kham.chien_thuat import tao_lap as _tl
    from kham.dinh_gia import dinh_gia as _dg
    from kham.so_lenh import Muc as _M
    from kham.so_lenh import SoLenh as _S

    gc = _dg("BTC_5M", 100_060.0, 100_000.0, 60.0,
             0.55 / math.sqrt(365 * 24 * 3600))
    if gc is None:
        return []
    su = _S(ma="BTC_5M", ben="UP", bid=[_M(0.55, 900.0)],
            ask=[_M(0.57, 900.0)], nhanLucMs=0.0)
    sd = _S(ma="BTC_5M", ben="DOWN", bid=[_M(0.41, 900.0)],
            ask=[_M(0.43, 900.0)], nhanLucMs=0.0)
    from kham.kho_doi import Kho as _K
    return _tl(_BC(ma="BTC_5M", gia=gc, soUp=su, soDown=sd, dongHo=lc,
                   viThe=_K().lay("BTC_5M"))) or []


def kiem_bootstrap_theo_khoi() -> None:
    """Bốn lát cắt của MỘT khung không phải bốn quan sát độc lập.

    Chúng chia chung một kết quả. Lấy lại theo từng cặp là giả vờ có gấp
    bốn số quan sát thực, và khoảng tin hẹp đi theo căn của cái giả vờ ấy
    — tức cổng dễ NHẬN một thay đổi chỉ là tiếng ồn, ở đúng chỗ ghi vào
    `config.json`.

    Cùng cái bẫy đã cắn ở `chay_lai` (đếm mỗi cửa sổ 44 lần, ra lãi 2,9
    triệu đô) và ở `do-cho-that.py` (1.006 dòng hoá ra 14 cửa sổ).
    """
    print("\n-- Bootstrap phai lay lai theo KHUNG, khong theo cap ------")

    import random as _rd

    from kham.hoc_offline import khoang_tin_theo_khoi

    rd = _rd.Random(1)
    hieu, moc = [], []
    for k in range(100):
        goc = rd.gauss(0, 0.01)          # sai lệch CHUNG của cả khung
        for _ in range(4):
            hieu.append(goc + rd.gauss(0, 0.0005))
            moc.append(k)

    a = khoang_tin_theo_khoi(hieu, moc)
    b = khoang_tin_theo_khoi(hieu, None)
    kiem("đếm đúng số khung", a[2] == 100, a[2])
    kiem("không có mốc thì mỗi cặp là một khối", b[2] == 400, b[2])
    kiem("khoảng tin theo KHỐI RỘNG HƠN theo cặp",
         (a[1] - a[0]) > (b[1] - b[0]) * 1.5,
         f"khối {a[1]-a[0]:.5f} vs cặp {b[1]-b[0]:.5f} — chênh chính là "
         "phần độ chắc chắn tự cho mình")
    kiem("dãy rỗng thì không ném", khoang_tin_theo_khoi([], None) == (0.0, 0.0, 0))

    # Và hai công cụ VẶN phải gọi nó.
    GOC_MA = Path(__file__).resolve().parent.parent
    for ten in ("tu-nang-cap.py",):
        ma = (GOC_MA / "scripts" / ten).read_text(encoding="utf-8")
        kiem(f"{ten} dùng bootstrap theo khối",
             "khoang_tin_theo_khoi" in ma and "_mocChot" in ma,
             "bootstrap theo cặp ở đây là nới cổng mà không ai khai")


def kiem_cong_cu_van_dung_bo_uoc_chung() -> None:
    """Script nào GHI CONFIG thì phải đo bằng bộ ước của runtime.

    Đây là ranh giới đáng canh nhất trong cả cung: một script chỉ ĐO thì
    trôi ra khỏi runtime cũng chỉ làm sai một phép đo; một script VẶN
    THAM SỐ mà trôi thì nó ghi một con số sai vào `config.json` và con
    số ấy chạy thật.

    Đã cắn: cửa sổ σ được vặn 300s → 900s trên lưới phút trong khi
    runtime chạy bộ ước mẫu thô — σ chạy thật chỉ bằng 0,875 lần σ đã
    tuning.
    """
    print("\n-- Cong cu VAN phai dung bo uoc cua runtime --------------")

    import importlib.util as _iu

    GOC_MA = Path(__file__).resolve().parent.parent
    from kham.hoc_offline import sigma_tai as chuan

    for ten in ("tien-hoa-mo-hinh.py", "tu-nang-cap.py"):
        f = GOC_MA / "scripts" / ten
        kiem(f"{ten} có mặt", f.exists())
        if not f.exists():
            continue
        ma = f.read_text(encoding="utf-8")
        # Dò bằng AST, không dò chuỗi nguyên văn. Bản trước tìm đúng câu
        # `from kham.hoc_offline import sigma_tai` và vỡ ngay khi có thêm
        # một tên nữa trên cùng dòng nhập — một phép canh gãy vì lý do
        # không liên quan gì tới thứ nó canh.
        import ast as _a
        nhap = set()
        for _n in _a.walk(_a.parse(ma)):
            if isinstance(_n, _a.ImportFrom) and _n.module == "kham.hoc_offline":
                nhap.update(x.name for x in _n.names)
        kiem(f"{ten} nhập bộ ước chung",
             "sigma_tai" in nhap,
             "script GHI CONFIG mà tự tính σ là vặn nút của cỗ máy khác")
        kiem(f"{ten} KHÔNG tự tính lại σ",
             "pstdev" not in ma and "sqrt(60" not in ma, ma.count("pstdev"))

        sp = _iu.spec_from_file_location("_x_" + ten.replace("-", "_"), f)
        m = _iu.module_from_spec(sp)
        sp.loader.exec_module(m)
        T = 1_787_243_400_000
        nen = {int(T - (20 - i) * 60_000):
               70_000.0 * (1 + 0.0005 * math.sin(i * 1.7)) for i in range(21)}
        m.quen_sigma() if hasattr(m, "quen_sigma") else None
        a = m.sigma_tai(nen, T, 900.0)
        from kham.hoc_offline import quen_sigma as _qs
        _qs()
        b = chuan(nen, T, 900.0)
        kiem(f"{ten} cho ra ĐÚNG con số của bộ ước chung",
             a is not None and b is not None and abs(a - b) < 1e-15,
             f"{a} vs {b}")


def kiem_mot_bo_uoc_sigma() -> None:
    """CHỈ MỘT bộ ước σ. Hai bản sao là hai chỗ để chúng trôi ra khỏi nhau.

    Đã cắn đúng thế: `tu-nang-cap.py` vặn cửa sổ σ bằng cách chấm trên
    lưới phút, trong khi runtime chạy một bộ ước khác (mẫu thô, chia
    `sqrt(dt)`). Tham số chọn cho bộ này lắp vào bộ kia, và σ chạy thật
    chỉ bằng 0,875 lần σ đã tuning. Cái trôi ấy LẶNG: mỗi bản vẫn chạy
    được, không phép kiểm nào đỏ.

    Nay `hoc_offline.sigma_tai` gọi thẳng `DoBienDong`. Phép kiểm này
    đòi hai đường cho ra con số Y HỆT — không phải "gần bằng".
    """
    print("\n-- Chi MOT bo uoc sigma, hai duong phai trung khop -------")

    from kham.dinh_gia import DoBienDong as _DBD
    from kham.hoc_offline import quen_sigma, sigma_tai

    T = 1_787_243_400_000
    for bien in (1.3, 0.7, 2.1):
        nen = {int(T - (20 - i) * 60_000):
               70_000.0 * (1 + 0.0004 * math.sin(i * bien))
               for i in range(21)}
        quen_sigma()
        a = sigma_tai(nen, T, 900.0)
        b = _DBD()
        b.mo_dau([(t, g) for t, g in nen.items() if t <= T])
        c = b.sigma_giay()
        kiem(f"hai đường trùng khớp (biến {bien})",
             a is not None and c is not None and abs(a - c) < 1e-15,
             f"{a} vs {c}")

    # `sigma_giay` phải tự cắt theo cửa sổ, không dựa vào `them()` đã dọn.
    b2 = _DBD()
    b2.mo_dau([(T - (40 - i) * 60_000.0, 70_000.0 + i * 5.0) for i in range(40)])

    kiem("nạp 40 nến vào cửa sổ 900s thì chỉ dùng 16",
         b2.sigma_giay() is not None and b2.so_mau == 40,
         "giữ đủ nến nhưng chỉ TÍNH trên cửa sổ")
    # b3 phải nhận ĐÚNG 16 nến CUỐI của b2, không phải 16 nến đầu của
    # một dãy khác: log-return của một dãy cộng đều không phải hằng số,
    # nên hai dãy khác mức giá cho hai σ khác nhau — và đó là phép kiểm
    # tự dựng sai đề, không phải mã sai.
    day = [(T - (40 - i) * 60_000.0, 70_000.0 + i * 5.0) for i in range(40)]
    b3 = _DBD()
    b3.mo_dau(day[-16:])
    kiem("và cho ra đúng con số của 16 nến CUỐI ấy",
         abs((b2.sigma_giay() or 0) - (b3.sigma_giay() or 0)) < 1e-15,
         f"{b2.sigma_giay()} vs {b3.sigma_giay()}")


def kiem_sigma_luoi_phut() -> None:
    """σ chạy thật phải đo CÙNG CÁCH với σ đã tuning ngoại tuyến.

    Bản đầu lấy log-return giữa hai mẫu liên tiếp rồi chia `sqrt(dt)`.
    Nhưng giá nền tới từ REST hỏi vòng 2 giây, và đo trên băng thật:
    **36,4% mẫu có giá y hệt mẫu trước**. Mỗi mẫu lặp là một return bằng
    0 tiêm vào phương sai, nên σ chạy thật chỉ bằng 0,875 lần (trung vị,
    19 quãng) σ đo trên lưới phút — σ bị dìm thì mô hình TỰ TIN QUÁ.

    Nặng hơn con số: `tu-nang-cap.py` vặn `bienDongCuaSoGiay` 300→900
    bằng cách chấm trên LƯỚI PHÚT. Tham số ấy được chọn cho một bộ ước
    KHÁC với bộ ước đang chạy.
    """
    print("\n-- Sigma chay that do CUNG CACH voi sigma tuning ---------")

    from kham.config import CONFIG as _CFG
    from kham.dinh_gia import DoBienDong as _DBD

    b = _DBD()
    cu = (_CFG.get("dinhGia") or {}).get("bienDongCuaSoGiay")
    try:
        _CFG["dinhGia"]["bienDongCuaSoGiay"] = 900
        kiem("cửa sổ đọc CONFIG động", b.cuaSoGiay == 900.0, b.cuaSoGiay)
        _CFG["dinhGia"]["bienDongCuaSoGiay"] = 300
        kiem("đổi CONFIG thì bộ ước thấy ngay", b.cuaSoGiay == 300.0,
             "chốt lúc import là nút vặn mà không nhúc nhích")
        _CFG["dinhGia"]["bienDongCuaSoGiay"] = 900

        T = time.time() * 1000.0
        # Mẫu LẶP: giá đứng im ở nhịp 2 giây trong cùng một phút.
        b2 = _DBD()
        for i in range(60):
            b2.them(70_000.0, T - (60 - i) * 2_000.0)
        kiem("mẫu lặp trong cùng phút chỉ thành MỘT nến",
             b2.so_mau <= 3, f"{b2.so_mau} nến từ 60 mẫu 2 giây")

        b3 = _DBD()
        for i in range(20):
            b3.them(70_000.0 * (1 + 0.0004 * math.sin(i)),
                    T - (20 - i) * 60_000.0)
        kiem("đủ nến phút thì có σ", b3.sigma_giay() is not None)
        # 16 chứ không 15: cửa sổ giữ mốc `>= han` nên nó bao cả hai đầu —
        # 15 khoảng thì 16 mốc. Chốt ở dải để phép kiểm không đỏ vì một
        # sai lệch một đơn vị mà chính nó hiểu nhầm.
        kiem("số nến khớp cửa sổ 900 giây", 15 <= b3.so_mau <= 16,
             f"{b3.so_mau} nến cho cửa sổ 900s")

        b4 = _DBD()
        for i in range(4):
            b4.them(70_000.0 + i, T - (4 - i) * 60_000.0)
        kiem("thiếu nến thì trả None, KHÔNG lùi về bộ ước mẫu thô",
             b4.sigma_giay() is None,
             "lùi về là lặng lẽ dùng lại đúng bộ ước vừa bị bác")

        b5 = _DBD()
        b5.mo_dau([(T - (20 - i) * 60_000.0, 70_000.0 + i * 3.0)
                   for i in range(20)])
        kiem("nạp mồi cho σ có ngay từ vòng đầu",
             b5.so_mau == 20 and b5.sigma_giay() is not None, b5.so_mau)
    finally:
        if cu is not None:
            _CFG["dinhGia"]["bienDongCuaSoGiay"] = cu


def kiem_nho_gia_mo_khung() -> None:
    """Strike của một khung là HẰNG SỐ — đừng hỏi lại 750 lần.

    Vòng lặp gọi `gia_mo_khung` mỗi 2 giây cho mỗi market. 5 market ×
    một khung 5 phút = 750 lời gọi REST cho đúng một con số không đổi.
    Nặng, và nguy: mỗi lời gọi là một cơ hội hỏng, mà hỏng thì
    `_mot_thi_truong` thoát sớm — mất một dòng băng, đúng vào những phút
    quý nhất khi đường tới chợ vừa thông.
    """
    print("\n-- Nho gia mo khung: hoi MOT lan cho moi moc -------------")

    from kham.nguon import Nguon

    ng = Nguon.__new__(Nguon)
    ng.trangThai = {}
    ng._nhoMoKhung = {}
    dem = [0]

    def gia_lay(ten, url, tham=None):
        dem[0] += 1
        return [[int(tham["startTime"]), "70000.5", "1", "1", "1"]]

    ng._lay = gia_lay
    T = 1_787_243_400_000.0
    a = ng.gia_mo_khung("BTCUSDT", T)
    for _ in range(20):
        ng.gia_mo_khung("BTCUSDT", T)
    kiem("hỏi mạng đúng MỘT lần cho 21 lượt gọi", dem[0] == 1, f"{dem[0]} lần")
    kiem("trả đúng giá mở", a == 70000.5, a)

    ng.gia_mo_khung("BTCUSDT", T + 300_000.0)
    kiem("mốc KHÁC thì hỏi lại", dem[0] == 2, dem[0])
    ng.gia_mo_khung("ETHUSDT", T)
    kiem("cặp KHÁC thì hỏi lại", dem[0] == 3, dem[0])

    # Mọi mốc trong cùng một PHÚT là một mốc — hàm làm tròn xuống phút.
    ng.gia_mo_khung("BTCUSDT", T + 30_000.0)
    kiem("cùng một phút thì KHÔNG hỏi lại", dem[0] == 3, dem[0])


def kiem_cong_tien_ngan_mach() -> None:
    """Băng không có dòng khung ăn thua thì cổng tiền BỎ QUA phần chạy lại.

    `chay_lai` chỉ chấm được dòng `quan-sat`. Không có dòng nào thì ba
    lượt quét băng phía sau CHẮC CHẮN trả về 0 khớp — mỗi lượt vài chục
    giây trên băng thật, mỗi ngày, để tới đúng cái chỗ đã biết trước.

    Ngắn mạch phải kèm LỜI KHAI: một vòng bỏ qua việc mà không nói vì
    sao thì đọc y hệt một vòng hỏng.
    """
    print("\n-- Cong tien ngan mach khi khong co gi de cham -----------")

    from kham.tien_hoa import _dem_bo_qua

    dc = [{"thiTruong": [{"ma": "BTC_5M", "giaiDoan": "dat-cuoc",
                          "so": {"UP": {"thangCho": True}}}]} for _ in range(5)]
    qs = [{"thiTruong": [{"ma": "BTC_5M", "giaiDoan": "quan-sat",
                          "so": {"UP": {}}}]} for _ in range(3)]

    d = _dem_bo_qua(dc)
    kiem("băng toàn cửa đặt cược → đếm 0 dòng ăn thua",
         d.get("_soQuanSat") == 0, d)
    kiem("vẫn đếm được lý do đứng ngoài", d.get("thang-cho") == 5, d)

    d2 = _dem_bo_qua(dc + qs)
    kiem("có dòng ăn thua thì đếm đúng", d2.get("_soQuanSat") == 3, d2)

    # Và khoá đếm ấy KHÔNG được rơi vào bảng triệu chứng: nó là số liệu
    # nội bộ, không phải một lý do đứng ngoài.
    from kham.chan_doan import chan_doan
    t = chan_doan([{"laiLo": -1.0} for _ in range(40)],
                  {"saiSoTB": 0.01, "tongMau": 500, "bang": []},
                  {k: v for k, v in d2.items() if not k.startswith("_")})
    ma = [x.ma for x in t]
    kiem("chẩn đoán vẫn chạy bình thường với bảng đã lọc", bool(ma), ma)


def kiem_tu_nang_cap() -> None:
    """Vòng tự nâng cấp: ba tập tách rời, và biên siết theo số ứng viên.

    Chỗ nguy hiểm nhất của mọi vòng tự tối ưu: lặp N lần trên CÙNG một
    tập kiểm thì tập ấy thôi còn là ngoài mẫu — mỗi vòng lại dùng nó để
    CHỌN. Không lộ ra ở đâu, mọi con số vẫn đẹp dần.

    Chốt là chia BA tập theo THỜI GIAN: HỌC khớp nắn, CHỌN xếp hạng ứng
    viên, CHỐT chỉ GẬT hay LẮC về đúng ứng viên đã chọn. Đã thấy nó cứu
    một bàn thua: cùng một ứng viên, chạy lại vài phút sau với dữ liệu
    mới hơn thì tập CHỐT lắc — thay đổi ấy mỏng tới mức vài phút dữ liệu
    là lật.
    """
    print("\n-- Tu nang cap: ba tap tach roi, bien siet ---------------")

    GOC_MA = Path(__file__).resolve().parent.parent
    f = GOC_MA / "scripts" / "tu-nang-cap.py"
    kiem("có file tự nâng cấp", f.exists())
    if not f.exists():
        return
    # Nạp module thay vì bóc bằng AST: `CHIA_HOC, CHIA_CHON = 0.50, 0.75`
    # là gán BỘ ĐÔI, và một phép bóc chỉ nhận `Name = Constant` sẽ không
    # thấy nó rồi báo `None` — báo oan, đúng lớp lỗi đã cắn nhiều lần.
    import importlib.util as _iu
    sp = _iu.spec_from_file_location("_tnc", f)
    m = _iu.module_from_spec(sp)
    sp.loader.exec_module(m)

    kiem("ba tập chia theo thời gian, không chồng lấn",
         0.0 < m.CHIA_HOC < m.CHIA_CHON < 1.0,
         f"{m.CHIA_HOC} / {m.CHIA_CHON}")
    kiem("tập CHỐT không rỗng", (1.0 - m.CHIA_CHON) >= 0.15,
         f"CHỐT chiếm {(1.0-m.CHIA_CHON):.0%} — nhỏ quá thì nó gật bừa")
    b2, b60 = m._bien(2), m._bien(60)
    kiem("biên SIẾT theo số ứng viên", b60 > b2,
         f"2 ứng viên → {b2:.5f} · 60 ứng viên → {b60:.5f}")
    kiem("biên luôn dưới 1 (vẫn đòi khá hơn)", b60 < 1.0, b60)

    kiem("nút `batDinhToiThieu` KHÔNG nằm trong danh sách nút mô hình",
         "dinhGia.batDinhToiThieu" not in m.NUT_MO_HINH,
         "nó chạm `batDinh` chứ không chạm `pUp` — vặn nó ở đây là vặn mù")
    kiem("bốn nút mô hình đều có trong bảng vặn",
         all(d in NUT_THEO_DUONG for d in m.NUT_MO_HINH), m.NUT_MO_HINH)


def kiem_ghi_config_tai_cho() -> None:
    """`ghi_config` sửa ĐÚNG MỘT SỐ, không viết lại cả file.

    Bản đầu nạp JSON rồi `json.dumps(indent=2)` đè lại: giữ được khoá chú
    thích nhưng mất sạch bố cục xếp tay — dòng trống ngăn nhóm, bốn
    market viết gọn hai dòng mỗi cái. Một lượt vặn đổi đúng một con số mà
    `git diff` ra 55 thêm / 32 xoá.

    Và đây là việc chạy MỖI NGÀY. Config bị xáo lại hằng ngày thì
    `git log` của nó hết đọc được — mà đó chính là biên niên sử của vòng
    tiến hoá.
    """
    print("\n-- ghi_config sua DUNG MOT SO ---------------------------")

    import json as _json
    import shutil as _sh
    import tempfile as _tf
    from pathlib import Path as _P

    import kham.tien_hoa as _TH

    goc = _P(__file__).resolve().parent.parent / "config.json"
    with _tf.TemporaryDirectory() as t:
        d = _P(t)
        _sh.copy2(goc, d / "config.json")
        truoc = (d / "config.json").read_text(encoding="utf-8")
        cuRoot = _TH.ROOT
        _TH.ROOT = d
        # `ghi_config` đổi CẢ CONFIG trong bộ nhớ, không chỉ file. Không
        # trả lại thì mọi phép kiểm SAU đây chạy với cửa sổ σ 60 giây —
        # và chúng đỏ vì một lý do không liên quan gì tới thứ chúng kiểm.
        from kham.config import CONFIG as _CFG
        cuGiaTri = (_CFG.get("dinhGia") or {}).get("bienDongCuaSoGiay")
        try:
            cu = _json.loads(truoc)["dinhGia"]["bienDongCuaSoGiay"]
            moi = 60 if cu != 60 else 120
            kiem("ghi được", _TH.ghi_config("dinhGia.bienDongCuaSoGiay", moi))
            sau = (d / "config.json").read_text(encoding="utf-8")
            kiem("giá trị đã đổi thật",
                 _json.loads(sau)["dinhGia"]["bienDongCuaSoGiay"] == moi)

            a = truoc.splitlines()
            b = sau.splitlines()
            kiem("số dòng KHÔNG đổi", len(a) == len(b), f"{len(a)} → {len(b)}")
            khac = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
            kiem("đúng MỘT dòng đổi", len(khac) == 1,
                 f"{len(khac)} dòng đổi — viết lại cả file là xoá bố cục")
            if khac:
                kiem("dòng đổi đúng là dòng của khoá ấy",
                     "bienDongCuaSoGiay" in a[khac[0]], a[khac[0]].strip())

            # Khoá không tồn tại thì phải TỪ CHỐI, không được ghi bừa.
            kiem("khoá lạ thì từ chối",
                 not _TH.ghi_config("dinhGia.khongCoKhoaNay", 1))
            kiem("và file không bị đụng",
                 (d / "config.json").read_text(encoding="utf-8") == sau)
        finally:
            _TH.ROOT = cuRoot
            if cuGiaTri is not None:
                _CFG["dinhGia"]["bienDongCuaSoGiay"] = cuGiaTri


def kiem_chan_mo_hinh_khong_can_lenh() -> None:
    """Bệnh của MÔ HÌNH phải chẩn được khi CHƯA có lệnh nào kết toán.

    `chan_doan` từng `return` ngay ở cửa "chưa đủ 20 lệnh". Nhưng bệnh
    của mô hình đọc thẳng từ bảng hiệu chỉnh, và bảng ấy dựng được mà
    không cần chạm vào chợ — `scripts/hoc-tu-binance.py` dựng 40.276 mẫu
    từ nến Binance trong khi sổ kết toán rỗng trơn.

    "Chưa đủ lệnh để chẩn CHIẾN THUẬT" không có nghĩa là "chưa biết gì về
    MÔ HÌNH". Trộn hai câu đó là vứt đi một phép đo đã có sẵn.
    """
    print("\n-- Chan benh MO HINH khong can lenh nao ------------------")

    from kham.chan_doan import chan_doan as _cd

    hcXau = {"saiSoTB": 0.11, "tongMau": 40_276,
             "bang": [{"o": "10-20", "n": 500, "duDoan": 0.15,
                       "thucTe": 0.30, "lech": 0.15},
                      {"o": "80-90", "n": 500, "duDoan": 0.85,
                       "thucTe": 0.70, "lech": -0.15}]}
    t = _cd([], hcXau)
    ma = [x.ma for x in t]
    kiem("sổ kết toán rỗng vẫn báo thiếu mẫu", "thieu-mau" in ma, ma)
    kiem("VÀ vẫn chẩn được bệnh mô hình", "mo-hinh-lech" in ma,
         f"{ma} — bảng 40.276 mẫu bị vứt vì chưa lệnh nào kết toán")

    mh = next(x for x in t if x.ma == "mo-hinh-lech")
    kiem("bệnh mô hình trỏ tới nút giảm chấn trước tiên",
         mh.nutGoiY and mh.nutGoiY[0] == "nanLai.heSoGiamChan", mh.nutGoiY)

    # Bảng LÀNH thì không được bịa bệnh ra.
    hcLanh = {"saiSoTB": 0.028, "tongMau": 40_276, "bang": []}
    ma2 = [x.ma for x in _cd([], hcLanh)]
    kiem("bảng hiệu chỉnh lành thì KHÔNG bịa bệnh", "mo-hinh-lech" not in ma2,
         ma2)


def kiem_hoc_khong_nhin_trom() -> None:
    """Lát cắt học từ nến 1 phút KHÔNG được lấy giá của tương lai.

    `scripts/hoc-tu-binance.py` dựng sổ hiệu chỉnh từ nến Binance: với
    mỗi khung [T, T+300] nó lấy giá tại thời điểm còn τ giây, rồi so dự
    đoán với kết quả `giá(T+300) > giá(T)`.

    Nến 1 phút chỉ cho biết giá tại các mốc PHÚT. Bản đầu tra giá bằng
    `floor(t) + 1 phút` — làm tròn LÊN — nên:

        τ=240 → t=T+60s  (đúng mốc phút) → lấy giá T+120s, muộn 60 giây
        τ=30  → t=T+270s (giữa phút)     → lấy giá T+300s, ĐÚNG ĐÁP ÁN

    Nó hiện ra thành hai ô đầu và cuối bảng hiệu chỉnh khớp gần như hoàn
    hảo (lệch −0,000 và −0,008) trên 3.476 mẫu, và trông y hệt một mô
    hình giỏi.

    Nay chỉ lấy những τ rơi đúng ranh giới phút, và tra thẳng.
    """
    print("\n-- Hoc tu Binance: KHONG duoc nhin trom -----------------")

    import ast as _ast

    GOC_MA = Path(__file__).resolve().parent.parent
    ma = (GOC_MA / "scripts" / "hoc-tu-binance.py").read_text(encoding="utf-8")

    # Đọc bằng CÂY CÚ PHÁP, không bằng regex: mẫu regex ở đây phải mang
    # dấu gạch chéo ngược, mà file này đi qua nhiều lớp shell và gạch
    # chéo bị nuốt một lớp mỗi lần.
    lat: list = []
    for nut in _ast.walk(_ast.parse(ma)):
        if (isinstance(nut, _ast.Assign) and nut.targets
                and isinstance(nut.targets[0], _ast.Name)
                and nut.targets[0].id == "LAT_CAT"):
            lat = [float(x.value) for x in nut.value.elts]
    kiem("đọc được bảng lát cắt", bool(lat), lat)
    if not lat:
        return
    kiem("có lát cắt để kiểm", len(lat) >= 3, lat)

    # Mọi lát cắt phải rơi đúng ranh giới phút của khung 5 phút.
    le = [t for t in lat if int((300.0 - t) * 1000.0) % 60_000]
    kiem("mọi lát cắt rơi đúng ranh giới phút", not le,
         f"{le} nằm giữa phút — tra giá ở đó là hoặc lấy giá cũ, hoặc "
         "lấy giá của TƯƠNG LAI")

    kiem("τ=30 đã bị bỏ (nó lấy đúng giá kết toán)", 30.0 not in lat, lat)

    # Và mã phải TỪ CHỐI mốc giữa phút thay vì làm tròn lên.
    kiem("mã bỏ qua mốc giữa phút, không làm tròn LÊN",
         "if t % int(PHUT):" in ma and "// PHUT * PHUT) + int(PHUT))" not in ma,
         "làm tròn lên là lấy giá của tương lai")

    # Và nó phải dựng lại từ đầu, không cộng dồn lên sổ cũ.
    kiem("dựng lại sổ từ đầu, không cộng dồn", "hc.o = {}" in ma,
         "chạy hai lần mà cộng dồn thì `n` phình lên, và `n` mở Kelly")
    kiem("xoá sổ thô trước khi dựng lại", "tho.unlink()" in ma,
         "`ghi_tho` nối thêm; không xoá thì phần đuôi ngoài mẫu chứa "
         "đúng thứ phần đầu đã thấy")


def kiem_duong_quyet_dinh() -> None:
    """Gọi THẬT `_mot_thi_truong` — ở khung ăn thua, không phải cửa đặt cược.

    Phép kiểm này tồn tại vì đường ra quyết định vừa bị đổi cửa, và
    không phép nào chạm tới nó: nó cần giá Binance, sổ lệnh WebSocket và
    một khung đúng giai đoạn, nên cả bộ kiểm chạy-không-mạng đi vòng.

    Cùng bài học với `kiem_tien_hoa_chay_that`: một hàm không ai gọi thật
    thì chữ ký sai, giai đoạn sai, mốc sai đều xanh hết.

    Ba điều phải đúng:
      1. bám khung ở giai đoạn QUAN_SAT, không phải DAT_CUOC
      2. strike lấy ở `eventStartMs`, không phải `batDauDatCuocMs`
      3. τ đếm tới `endMs`, không tới `eventStartMs`
    """
    print("\n-- Duong ra quyet dinh: goi THAT, o dung cua --------------")

    import kham.vong as V
    from kham.khung import QUAN_SAT, Khung
    from kham.so_lenh import Muc, SoLenh

    # Dựng quanh GIỜ THẬT, không quanh một mốc bịa.
    #
    # `dong_ho.lat_cat()` đọc đồng hồ MÁY chứ không đọc `now` truyền vào,
    # nên một khung đặt ở mốc bịa sẽ luôn cho lát cắt "đã khoá" — và ở
    # trạng thái đó bốn trong sáu ngón nghề lặng lẽ trả về rỗng. Phép
    # kiểm chạy trên mốc bịa vẫn xanh mà không kiểm được gì.
    T = time.time() * 1000.0 - 240_000.0
    now = T + 240_000.0          # trong khung ăn thua, còn 60 giây
    k = Khung(slug=f"btc-updown-5m-{int(T // 1000)}", ma="BTC_5M",
              capNen="BTCUSDT",
              tokenUp="u", tokenDown="d",
              batDauDatCuocMs=T - 300_000.0, eventStartMs=T,
              endMs=T + 300_000.0, daiSongGiay=300.0)
    kiem("khung dựng đúng giai đoạn để thử", k.giai_doan(now) == QUAN_SAT,
         k.giai_doan(now))
    kiem("τ đếm tới endMs, không tới eventStartMs",
         abs(k.con_lai_an_thua_giay(now) - 60.0) < 1.0
         and k.con_lai_giay(now) == 0.0,
         f"{k.con_lai_an_thua_giay(now)} vs {k.con_lai_giay(now)}")

    def so(gia_bid, gia_ask, ben):
        return SoLenh(ma="BTC_5M", ben=ben,
                      bid=[Muc(gia_bid, 900.0)], ask=[Muc(gia_ask, 900.0)],
                      nhanLucMs=now)

    xin_mo: list[float] = []

    class _Song:
        def lay(self, token):
            return so(0.55, 0.57, "UP") if token == "u" else so(0.41, 0.43, "DOWN")

    dem = [0]

    class _Nguon:
        def gia_binance(self, cap):
            # Phải NHÚC NHÍCH: giá đứng im thì σ = 0 và  trả
            # None, nên vòng thoát sớm với lý do "chưa đủ mẫu" — một lý do
            # đúng chữ nhưng sai nguyên nhân, và nó che mất thứ đang kiểm.
            dem[0] += 1
            return 100_060.0 + (7.0 if dem[0] % 2 else -5.0)
        def gia_mo_khung(self, cap, ms):
            xin_mo.append(ms)
            return 100_000.0

        def nen_gan_day(self, cap, soNen=20):
            # NẠP MỒI cho `DoBienDong`. Bộ ước nay chạy trên LƯỚI PHÚT,
            # nên 20 nhịp hai giây của phép kiểm chỉ cho 1–2 nến phút —
            # không đủ, và không đủ thì vòng thoát sớm với lý do đúng
            # chữ nhưng che mất thứ đang kiểm.
            return [(T - (soNen - i) * 60_000.0,
                     100_000.0 + (37.0 if i % 2 else -29.0))
                    for i in range(soNen)]

        trangThai: dict = {}

    cuSong, cuNguon = V.dong_song, V.nguon
    V.dong_song, V.nguon = _Song(), _Nguon()
    try:
        rt = V.Runtime.__new__(V.Runtime)
        rt.kho = V.Kho()
        rt.risk = V.RiskEngine(rt.kho)
        rt.cong = V.CongLenh(rt.kho)
        rt.hieuChinh = V.HieuChinh()
        rt.so = V.So()
        rt.ketToan = V.KetToan(rt.kho, rt.hieuChinh, rt.so, rt.risk)
        rt.phepNan = V.nan_lai.khop(rt.hieuChinh)
        rt.bienDong = {}
        rt.khungHienTai = {}
        rt.khungQuanSat = {"BTC_5M": k}
        rt.capSo, rt.giaChuan, rt.giaNen = {}, {}, {}
        rt.coHoi, rt.quyetChan, rt.boQua = [], {}, {}
        rt._thanPhien = {}
        rt.batTat = None
        rt.lanNga = {}

        tt = {"ma": "BTC_5M", "nen": "BTCUSDT", "dongCo": "updown-crypto"}
        ghi: list = []
        # σ cần ít nhất 12 mẫu — nuôi bằng chính giá Binance giả.
        for i in range(20):
            rt._mot_thi_truong(tt, now - (20 - i) * 2000.0, [])
        rt._mot_thi_truong(tt, now, ghi)

        kiem("strike xin ở eventStartMs, KHÔNG ở batDauDatCuocMs",
             xin_mo and all(abs(x - T) < 1e-6 for x in xin_mo),
             f"đã xin {sorted(set(xin_mo))[:3]}, chờ {T}")
        kiem("có ghi được dòng băng", len(ghi) == 1, len(ghi))
        if ghi:
            d = ghi[0]
            kiem("dòng băng khai đúng giai đoạn", d.get("giaiDoan") == QUAN_SAT,
                 d.get("giaiDoan"))
            kiem("dòng băng mang strike thật", d.get("giaMo") == 100_000.0)
            kiem("dòng băng mang τ của khung ăn thua",
                 abs(d.get("conLaiGiay", -1) - 60.0) < 1.0, d.get("conLaiGiay"))
        kiem("có cân ra cơ hội ở cửa này", len(rt.coHoi) >= 1,
             f"{len(rt.coHoi)} cơ hội · bỏ qua {rt.boQua}")

        # Lát cắt đồng hồ phải đếm tới endMs. Chỗ này từng bị bỏ sót lúc
        # đổi cửa và nó hỏng rất lặng: trỏ vào eventStartMs thì trong khung
        # ăn thua giai đoạn LUÔN là "đã khoá", và bốn trong sáu ngón nghề
        # — vốn soi `bc.dongHo.giaiDoan` — không bao giờ được gọi tới.
        from kham.dongho import dong_ho as _dh
        lc = _dh.lat_cat(k.endMs, k.daiSongGiay, tuoiDuLieuMs=0.0)
        kiem("lát cắt đồng hồ KHÔNG báo đã khoá giữa khung ăn thua",
             not lc.da_khoa and lc.conLaiGiay > 0,
             f"giai đoạn {lc.giaiDoan}, còn {lc.conLaiGiay:.0f}s")
        lcSai = _dh.lat_cat(k.eventStartMs, k.daiSongGiay, tuoiDuLieuMs=0.0)
        kiem("bằng chứng: trỏ vào eventStartMs thì ĐÃ KHOÁ",
             lcSai.da_khoa and lcSai.conLaiGiay == 0.0, lcSai.giaiDoan)
        kiem("và ở trạng thái ĐÃ KHOÁ thì ngón `tạo lập` câm",
             not _tao_lap_thu(lcSai), "bốn trong sáu ngón soi giai đoạn")

        # Và ở CỬA ĐẶT CƯỢC thì phải đứng ngoài.
        rt2 = V.Runtime.__new__(V.Runtime)
        for a in ("kho", "risk", "cong", "hieuChinh", "so", "ketToan",
                  "phepNan", "bienDong", "capSo", "giaChuan", "giaNen",
                  "quyetChan", "boQua", "_thanPhien", "batTat", "lanNga"):
            setattr(rt2, a, getattr(rt, a))
        rt2.coHoi = []
        rt2.khungHienTai = {"BTC_5M": k}
        rt2.khungQuanSat = {}
        ghi2: list = []
        rt2._mot_thi_truong(tt, T - 60_000.0, ghi2)   # trong cửa đặt cược
        kiem("ở cửa đặt cược thì ĐỨNG NGOÀI, không ghi dòng nào",
             not ghi2 and not rt2.coHoi,
             f"{len(ghi2)} dòng, {len(rt2.coHoi)} cơ hội")
    finally:
        V.dong_song, V.nguon = cuSong, cuNguon


def kiem_giai_doan_bang() -> None:
    """Dòng cửa ĐẶT CƯỢC và dòng cửa ĂN THUA không được lẫn vào nhau.

    Băng nay có hai loại dòng và chúng KHÔNG cùng nghĩa:

        "dat-cuoc"  `giaMo` là giá lúc T−300, KHÔNG phải strike;
                    `conLaiGiay` đếm tới T.
        "quan-sat"  `giaMo` là STRIKE THẬT (giá lúc T);
                    `conLaiGiay` đếm tới T+300.

    Trộn hai loại vào cùng một phép tính là dựng một con số không nói về
    thứ gì cả — cùng hình dạng lỗi mà `_giai_nen` phải tránh khi nó từ
    chối dán hai mẩu dòng ở hai bên chỗ đứt.

    Và dòng CŨ không có trường ấy: toàn bộ băng tám ngày đầu là cửa đặt
    cược, nên thiếu thì phải đọc là "dat-cuoc" — đúng, không phải đoán.
    """
    print("\n-- Hai loai dong bang khong duoc lan --------------------")

    from kham.bang import giai_doan_cua

    kiem("dòng cũ (thiếu trường) đọc là cửa đặt cược",
         giai_doan_cua({"ma": "BTC_5M"}) == "dat-cuoc")
    kiem("dòng khai quan-sat đọc đúng",
         giai_doan_cua({"giaiDoan": "quan-sat"}) == "quan-sat")

    # Băng trộn: một nửa dòng là CỬA ĐẶT CƯỢC. `chay_lai` phải BỎ chúng
    # và NÓI RA, không được lặng lẽ chấm lẫn — ở đó `giaMo` là giá lúc
    # T−300 chứ không phải strike.
    khung = _bang_sat_bien(20)
    tron = []
    for k in khung:
        tt = dict(k["thiTruong"][0])
        dc = dict(tt)
        dc["giaiDoan"] = "dat-cuoc"
        dc["giaMo"] = 99_940       # giá lúc T−300, KHÔNG phải strike
        tron.append({"luc": 0, "thiTruong": [tt, dc]})

    ts = ThamSo(ten="t", netEdgeToiThieu=0.005, bienAnToan=0.005)
    a = mot_luot(khung, ts)
    b = mot_luot(tron, ts)
    kiem("thêm dòng cửa đặt cược KHÔNG đổi kết quả chạy lại",
         (a.soQuaSang, round(a.tongLaiLo, 6))
         == (b.soQuaSang, round(b.tongLaiLo, 6)),
         f"{a.soQuaSang}/{a.tongLaiLo:.4f} vs {b.soQuaSang}/{b.tongLaiLo:.4f}")
    kiem("và nó NÓI RA là đã bỏ bao nhiêu dòng",
         b.boQua.get("dòng cửa đặt cược — mô hình không định giá được ở đó",
                     0) == len(khung),
         dict(b.boQua))


def kiem_lo_ngay_rong() -> None:
    """Trần "lỗ ngày" phải nhảy vì THUA, không vì BẬN.

    Bản đầu cộng dồn mỗi lần lỗ và không bao giờ trừ đi lần lãi. Với một
    cỗ máy đặt hàng chục lệnh một ngày thì tổng các lần lỗ luôn lớn bất
    kể ngày tốt hay xấu — nên cái trần mang tên "lỗ ngày" thực ra chặn
    theo ĐỘ BẬN.

    Đo được trên phiên phát lại: ngắt ở khung 5.000 vì "chạm trần lỗ ngày
    $500" trong khi vốn đang $12.896 trên $10.000 — chặn một ngày LÃI
    29%, rồi bảy ngày băng còn lại không đặt nổi một lệnh.
    """
    print("\n-- Tran lo ngay: do THUA rong, khong do do ban -----------")

    from kham.kho_doi import Kho as _Kho
    from kham.rui_ro import RiskEngine as _RE

    r = _RE(_Kho())
    r.vonBanDau = r.von = r.dinhVon = 10_000.0

    # Ngày rất BẬN nhưng có lãi: thua 400, lãi 900 → ròng +500.
    for _ in range(8):
        r.ghi_lai_lo(-50.0)
        r.ghi_lai_lo(+112.5)
    kiem("ngày bận mà LÃI thì không ngắt", not r.ngatKhanCap,
         f"lỗ gộp ${r.loGopNgayUsd:.0f} vượt trần ${r.tranLoNgayUsd:.0f} "
         "nhưng ròng đang dương — ngắt ở đây là chặn theo độ bận")
    kiem("vẫn thấy được độ chao qua lỗ GỘP", r.loGopNgayUsd == 400.0,
         r.loGopNgayUsd)
    kiem("mức thua ròng bằng 0 khi ngày đang lãi", r.loNgayUsd == 0.0)
    kiem("lãi ròng ngày cộng đúng", abs(r.laiRongNgayUsd - 500.0) < 1e-9,
         r.laiRongNgayUsd)

    # Ngày THUA thật thì phải ngắt.
    r2 = _RE(_Kho())
    r2.vonBanDau = r2.von = r2.dinhVon = 10_000.0
    r2.ghi_lai_lo(-499.0)
    kiem("thua 499 trên trần 500 thì chưa ngắt", not r2.ngatKhanCap)
    r2.ghi_lai_lo(-2.0)
    kiem("thua 501 thì NGẮT", r2.ngatKhanCap, r2.lyDoNgat)


def kiem_dong_ho_rui_ro() -> None:
    """`RiskEngine` phải nhận đồng hồ từ ngoài, không lấy từ tường.

    Trần lỗ NGÀY cần một ranh giới ngày. Chạy lại băng tám ngày bằng đồng
    hồ tường thì với nó mãi mãi là một ngày: bộ đếm cộng dồn suốt, chạm
    trần, cờ ngắt bật, và cờ ấy dính. Một cỗ máy rủi ro lấy ngày từ đồng
    hồ tường thì KHÔNG hậu kiểm được.
    """
    print("\n-- Dong ho rui ro phai nhan tu ngoai ---------------------")

    from kham.kho_doi import Kho as _Kho
    from kham.rui_ro import RiskEngine as _RE

    moc = [1787000000.0]
    r = _RE(_Kho(), dongHo=lambda: moc[0])
    r.vonBanDau = r.von = r.dinhVon = 10_000.0
    ngay1 = r.ngay

    r.ghi_lai_lo(-300.0)
    kiem("lỗ 300 chưa chạm trần 500", not r.ngatKhanCap)
    kiem("ghi đúng mức thua ròng", r.loNgayUsd == 300.0, r.loNgayUsd)

    moc[0] += 86_400.0          # sang ngày mới
    kiem("đồng hồ nhích một ngày thì đổi ngày",
         r.sang_ngay_moi() and r.ngay != ngay1, f"{ngay1} → {r.ngay}")
    kiem("bộ đếm ngày về 0", r.loNgayUsd == 0.0 and r.loGopNgayUsd == 0.0)

    r.ghi_lai_lo(-300.0)
    kiem("lỗ 300 của NGÀY MỚI vẫn chưa ngắt", not r.ngatKhanCap,
         "cộng dồn qua ngày là biến trần ngày thành trần cả đời")

    # Và ranh giới ngày phải trôi kể cả khi KHÔNG có lệnh nào kết toán.
    moc[0] += 86_400.0
    kiem("sang ngày được cả khi không kết toán gì", r.sang_ngay_moi())


def kiem_treo_tra_han_muc() -> None:
    """Khung không ra kết quả thì phải TRẢ LẠI hạn mức, không giữ mãi.

    `RiskEngine` đọc `Kho` để tính "market này đã dùng bao nhiêu trên
    trần". Bản đầu của `KetToan.soat` bỏ theo dõi bằng đúng một dòng
    `del self.cho[slug]` — vị thế nằm lại trong `Kho` vĩnh viễn, nên
    market ấy CHẾT cho tới lúc khởi động lại: mọi lệnh sau đều bị từ
    chối vì "đã dùng $X, chạm trần", trong khi tiền ấy không còn làm
    việc gì.

    Không lỗi nào báo, không con số nào đỏ. Đã thấy tận mắt trên phiên
    phát lại: khớp đứng hẳn ở 398 lệnh trong khi cửa sổ vẫn mở thêm hàng
    nghìn — 12 khung thiếu kết quả trên 2.627 là đủ khoá cả bốn market.

    Và nó KHÔNG được ghi thành lỗ: cổ phần vẫn trên sàn và vẫn sẽ ngã
    ngũ. Thứ mất là khả năng chấm điểm, không phải tiền. Nên có sổ TREO.
    """
    print("\n-- Bo theo doi phai TRA LAI han muc ----------------------")

    from kham.dinh_gia import HieuChinh as _HC
    from kham.ket_toan import ChoKetToan as _CKT
    from kham.ket_toan import KetToan as _KT
    from kham.kho_doi import Kho as _Kho
    from kham.so import So as _So

    kho = _Kho()
    kt = _KT(kho, _HC(), _So())
    v = kho.lay("BTC_5M")
    v.ghi_khop("UP", 150.0, 0.40)
    truoc = v.tienUp + v.tienDown
    kiem("dựng được một vị thế để thử", truoc > 0, truoc)

    c = _CKT(ma="BTC_5M", slug="btc-updown-5m-1787243400",
             ketThucMs=0.0, giaMo=100.0, capNen="btcusdt",
             tokenUp="u", tokenDown="d", soLanHoi=99)
    kt.cho[c.slug] = c
    kt._bo_theo_doi(c.slug, c)

    v2 = kho.lay("BTC_5M")
    kiem("bỏ theo dõi thì tồn kho về 0",
         v2.coUp == 0 and v2.tienUp == 0,
         f"còn {v2.coUp} cổ / ${v2.tienUp:.2f} — market này đã chết")
    kiem("khung ra khỏi danh sách chờ", c.slug not in kt.cho)
    kiem("số tiền treo được ghi lại, không biến mất",
         abs(kt.tienTreoUsd - truoc) < 1e-9,
         f"{kt.tienTreoUsd} vs {truoc}")
    kiem("đếm được số khung treo", kt.soTreo == 1)
    kiem("sổ kết toán KHÔNG có dòng nào — treo không phải lỗ",
         len(kt.xong) == 0,
         "cổ phần vẫn trên sàn; ghi thành lỗ là bịa một con số")
    d = kt.tom_tat()
    kiem("buồng lái thấy được số treo",
         d.get("soTreo") == 1 and d.get("tienTreoUsd") == truoc, d.get("soTreo"))


def kiem_tran_theo_von() -> None:
    """Thêm tiền vào thì cỗ máy phải ĐỔI HÀNH VI, không chỉ đổi con số.

    Ba trần rủi ro từng khai bằng đô-la, và cả ba là con số hợp lý cho
    đúng một tài khoản 1.000 đô. Nạp 10.000 đô vào thì chúng đứng yên:
    vẫn $100 mỗi market, và cầu dao ngày vẫn ngắt ở $50 — tức 0,51% vốn.
    Đo được trên phiên giấy thật: ngắt sau đúng HAI cửa sổ.
    """
    print("\n-- Tran rui ro phai co gian theo von ----------------------")

    from kham.kho_doi import Kho as _Kho
    from kham.rui_ro import RiskEngine as _RE

    r = _RE(_Kho())
    goc = (r.tranMoiThiTruongUsd, r.tranMoiTaiSanUsd, r.tranLoNgayUsd)
    kiem("vốn 1.000 giữ NGUYÊN ba trần cũ ($100/$200/$50)",
         goc == (100.0, 200.0, 50.0), str(goc))

    r.vonBanDau = 10_000.0
    moi = (r.tranMoiThiTruongUsd, r.tranMoiTaiSanUsd, r.tranLoNgayUsd)
    kiem("gấp 10 vốn thì gấp 10 cả ba trần",
         moi == (1000.0, 2000.0, 500.0),
         f"{moi} — trần đứng yên nghĩa là thêm tiền KHÔNG đổi hành vi")

    r2 = _RE(_Kho())
    r2.vonBanDau = 10_000.0
    r2.von = r2.dinhVon = 10_000.0
    r2.ghi_lai_lo(-499.0)
    kiem("lỗ 499 trên vốn 10.000 CHƯA ngắt cầu dao", not r2.ngatKhanCap)
    r2.ghi_lai_lo(-2.0)
    kiem("lỗ 501 thì ngắt", r2.ngatKhanCap, r2.lyDoNgat)


def kiem_phien_phat_lai() -> None:
    """Cả cỗ máy chạy trên băng: có lệnh, có kết toán, có lãi lỗ.

    Đây là phép kiểm phân biệt "các mảnh đều đúng" với "cái VÒNG khép".
    Cùng hình dạng lỗi đã cắn hồi dựng cung: có đủ `HieuChinh`, `So`,
    `thong_ke()` mà không dòng nào gọi chúng.
    """
    print("\n-- Phien phat lai: ca co may chay tren bang --------------")

    import tempfile
    from pathlib import Path as _P

    import kham.ket_qua as _KQ
    import kham.phat_lai as _PL

    khung = _bang_sat_bien(40)
    # Băng phải mang `luc` để sổ kết toán ghi đúng mốc thời gian của nó.
    # `_bang_sat_bien` đã sinh ra dòng khung ăn thua — loại duy nhất mà
    # phiên phát lại nhận.
    for i, k in enumerate(khung):
        k["luc"] = 1787243400000.0 + i * 2000.0

    with tempfile.TemporaryDirectory() as t:
        d = _P(t)
        so_kq = _KQ.SoKetQua(d / "kq.jsonl")
        for k in khung:
            for tt in k["thiTruong"]:
                so_kq.them(tt["slug"], bool(tt["upThang"]), 100.0, 101.0)

        p = _PL.PhienPhatLai(von=50_000.0, thuMucSo=d)
        p._kqThat = so_kq
        kq = p.chay(khung)

        kiem("vốn ban đầu đặt được tuỳ ý", kq.von0 == 50_000.0, kq.von0)
        kiem("ba trần theo vốn mới, không theo config",
             p.risk.tranMoiThiTruongUsd == 5000.0,
             p.risk.tranMoiThiTruongUsd)
        kiem("có thấy cửa sổ", kq.soCuaSo >= 5, kq.soCuaSo)
        kiem("có khớp lệnh thật", kq.soKhop >= 1,
             f"{kq.soKhop} khớp / {kq.soLenh} lệnh · bỏ qua {dict(kq.boQua)}")
        kiem("có kết toán", kq.soKetToan >= 1, kq.soKetToan)
        kiem("vốn cuối = vốn đầu + lãi lỗ",
             abs(kq.von - (kq.von0 + kq.tongLaiLo)) < 1e-6,
             f"{kq.von} vs {kq.von0 + kq.tongLaiLo}")
        kiem("thắng + thua = số cửa sổ kết toán",
             kq.soThang + kq.soThua == kq.soKetToan)
        kiem("đường vốn dài bằng số lần kết toán",
             len(kq.duongVon) == kq.soKetToan)
        kiem("phí luôn dương khi có khớp", kq.tongPhi > 0 or kq.soKhop == 0)

        # SỔ SÁCH KHÔNG ĐƯỢC LẪN VÀO SỔ THẬT.
        kiem("sổ kết toán ghi vào thư mục riêng",
             str(p.so.duong).startswith(str(d)), str(p.so.duong))
        kiem("sổ hiệu chỉnh ghi vào thư mục riêng",
             str(p.hieuChinh.duong).startswith(str(d)), str(p.hieuChinh.duong))
        kiem("sổ kết toán có dòng thật", len(p.so.doc()) == kq.soKetToan)


def kiem_khoa_cau_hinh_co_that() -> None:
    """Mọi khoá config đọc bằng `[...]` phải CÓ THẬT trong config.json.

    Dựng lên từ một lỗi đã cắn rất sâu, rồi cắn lại lần thứ hai trong
    cùng một phiên:

        nguon.py   `_NG['gamma']`  — khoá thật là `polymarketGamma`
        run.py     `CONFIG['ruiRo']['tranLoNgayUsd']` — khoá đã đổi tên

    Cả hai nằm trong f-string nên ném `KeyError` NGAY lúc dựng chuỗi. Cái
    đầu giết trọn vòng lặp mỗi hai giây suốt nhiều giờ trong khi buồng
    lái vẫn xanh; cái sau giết runtime trước cả khi mở cổng. Không phép
    kiểm nào chạm tới, vì cả hai nằm trên đường chỉ sống lúc chạy thật.

    Luật rút ra và nay canh được: **đọc config bằng `[...]` là một lời
    hứa rằng khoá ấy tồn tại.** Không chắc thì dùng `.get` kèm mặc định.

    ## Dò bằng CÂY CÚ PHÁP, không bằng regex

    Bản regex đầu tiên báo oan ngay dòng chú thích trong `vong.py` kể lại
    chính lỗi này — một khoá được NHẮC TỚI trong lời giải thích bị tính
    thành một khoá được ĐỌC. Cắt chú thích bằng regex thì lại không cắt
    được chuỗi tài liệu, mà cắt cả chuỗi thì mất luôn `'gamma'` — nó
    cũng là một chuỗi. Cây cú pháp không có chỗ mơ hồ đó: chú thích
    không vào cây, và chuỗi tài liệu là một câu lệnh chứ không phải một
    phép lấy chỉ số.
    """
    print("\n-- Khoa cau hinh: co that hay chi go cho co ---------------")

    import ast as _ast

    from kham.config import CONFIG as _CF

    GOC_MA = Path(__file__).resolve().parent.parent

    def _chuoi(nut):
        return nut.value if isinstance(nut, _ast.Constant) and \
            isinstance(nut.value, str) else None

    thieu, soCho = [], 0
    for f in sorted(GOC_MA.glob("kham/*.py")) + [GOC_MA / "run.py"]:
        cay = _ast.parse(f.read_text(encoding="utf-8"), filename=f.name)
        for nut in _ast.walk(cay):
            if not isinstance(nut, _ast.Subscript):
                continue
            k = _chuoi(nut.slice)
            if k is None:
                continue
            goc = nut.value
            # `_NG['x']` — bảng nguồn.
            if isinstance(goc, _ast.Name) and goc.id == "_NG":
                soCho += 1
                if k not in (_CF.get("nguon") or {}):
                    thieu.append(f"{f.name}: nguon.{k}")
                continue
            # `CONFIG['a']` và `CONFIG['a']['b']`.
            if isinstance(goc, _ast.Name) and goc.id == "CONFIG":
                soCho += 1
                if k not in _CF:
                    thieu.append(f"{f.name}: {k}")
                continue
            if isinstance(goc, _ast.Subscript) and \
                    isinstance(goc.value, _ast.Name) and goc.value.id == "CONFIG":
                a = _chuoi(goc.slice)
                if a is None:
                    continue
                soCho += 1
                d = _CF.get(a)
                if isinstance(d, dict) and k not in d:
                    thieu.append(f"{f.name}: {a}.{k}")

    kiem("có tìm thấy chỗ nào để kiểm", soCho >= 20, f"{soCho} chỗ")
    kiem("mọi khoá config đọc bằng [...] đều có thật", not thieu,
         f"thiếu {thieu[:4]} — `[...]` trong f-string ném KeyError ngay "
         "lúc dựng chuỗi, và cú ném ấy giết cả vòng lặp hoặc cả runtime")


def kiem_lan_nga_khong_giet_vong() -> None:
    """Một làn ngã thì các làn SAU vẫn phải chạy.

    Bản đầu xâu mọi làn trên một mạch thẳng, nên một `KeyError` ở làn tìm
    khung làm mất sạch: không ghi băng, không kết toán, không khớp lại
    phép nắn, không lượt tiến hoá nào. Mà buồng lái vẫn đếm vòng và vẫn
    xanh — một cỗ máy chết trông y hệt một cỗ máy đang chạy.
    """
    print("\n-- Mot lan nga thi cac lan sau van chay -------------------")

    import kham.vong as V

    rt = V.Runtime.__new__(V.Runtime)
    rt.lanNga = {}
    daChay = []

    def nga():
        raise KeyError("gamma")

    kiem("làn ngã trả về False", V.Runtime._lan(rt, "thử", nga) is False)
    kiem("ghi lại tên làn và lý do",
         "thử" in rt.lanNga and "KeyError" in rt.lanNga["thử"], rt.lanNga)
    kiem("làn sau vẫn chạy được",
         V.Runtime._lan(rt, "sau", lambda: daChay.append(1)) is True
         and daChay == [1])
    kiem("làn chạy trót lọt thì KHÔNG ghi vào sổ ngã", "sau" not in rt.lanNga)


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


def kiem_ghi_ket_qua_vo_dieu_kien() -> None:
    """Kết quả một khung phải vào sổ KỂ CẢ khi mình không đoán gì.

    Kết quả là sự thật về thế giới, không phải sản phẩm của một lượt
    đoán. Trước bản này nó nằm trong nhánh `pDuDoanUp is not None`, nên
    khung nào thiếu nguyên liệu định giá là mất kết quả vĩnh viễn — mà
    `chay_lai` chấm điểm bằng cách tra đúng cuốn sổ ấy, cho mọi bộ tham
    số về sau. Phép kiểm này đỏ nếu ai gộp nó trở lại vào nhánh cũ.
    """
    print("\n-- Ket qua vao so ke ca khi khong du doan -----------------")

    import tempfile
    from pathlib import Path as _P

    import kham.ket_qua as KQ
    import kham.ket_toan as KT
    from kham.ket_toan import ChoKetToan, KetToan
    from kham.so import So

    with tempfile.TemporaryDirectory() as t:
        cu = KT.so_ket_qua
        KT.so_ket_qua = KQ.SoKetQua(_P(t) / "kq.jsonl")
        try:
            # Sổ hiệu chỉnh RIÊNG: cuốn chung trong thư mục tạm nay có
            # thể đã bị một lượt học offline ghi đầy, và phép kiểm này
            # khẳng định `tong_mau == 0`.
            kt = KetToan(Kho(), HieuChinh(_P(t) / "hc.json"),
                         So(_P(t) / "so.jsonl"))
            # Khung KHÔNG có dự đoán: thiếu nguyên liệu định giá.
            c = ChoKetToan(ma="BTC_5M", slug="btc-updown-5m-1787243400",
                           ketThucMs=1787243700000.0, giaMo=100.0,
                           capNen="btcusdt", tokenUp="u", tokenDown="d",
                           pDuDoanUp=None)
            kt._ghi_so(c, True, None, True, False)
            kiem("không dự đoán vẫn ghi được kết quả",
                 KT.so_ket_qua.lay(c.slug) is True,
                 "mất dòng này là mất khả năng chấm cả cửa sổ, mãi mãi")
            kiem("không dự đoán thì KHÔNG đụng sổ hiệu chỉnh",
                 kt.hieuChinh.tong_mau == 0,
                 "hiệu chỉnh chấm chính mô hình, không có đoán thì không có gì chấm")

            # Khung CÓ dự đoán: cả hai sổ đều phải nhận.
            c2 = ChoKetToan(ma="BTC_5M", slug="btc-updown-5m-1787243700",
                            ketThucMs=1787244000000.0, giaMo=100.0,
                            capNen="btcusdt", tokenUp="u", tokenDown="d",
                            pDuDoanUp=0.62)
            kt._ghi_so(c2, False, None, True, False)
            kiem("có dự đoán thì cả hai sổ cùng nhận",
                 KT.so_ket_qua.lay(c2.slug) is False and kt.hieuChinh.tong_mau == 1)
        finally:
            KT.so_ket_qua = cu


def kiem_nguon_mau() -> None:
    print("\n-- Nguon mau: THAT va MO PHONG khong duoc lan ---------------")
    from kham.chan_doan import chan_doan

    hc = {"saiSoTB": 0.06, "tongMau": 2542, "bang": []}

    # Nhãn phải THEO XUỐNG tận từng triệu chứng, không chỉ nằm ở đâu đó
    # cấp trên. Một chẩn đoán dựng trên mẫu mô phỏng lạc quan có hệ thống
    # — không trượt thêm, không khớp một phần, không chọn lọc bất lợi —
    # nên người đọc phải thấy nhãn ngay chỗ đọc, không phải đi tra.
    t = chan_doan([], hc, {}, nguonMau="chay-lai")
    kiem("mẫu mô phỏng → triệu chứng mang nhãn",
         t and t[0].bangChung.get("nguonMau") == "chay-lai",
         t[0].bangChung if t else None)

    t2 = chan_doan([], hc, {})
    kiem("mặc định là mẫu THẬT",
         t2 and t2[0].bangChung.get("nguonMau") == "that")

    # Đủ mẫu thì phải chẩn được bệnh thật, không dừng ở "thiếu mẫu".
    lo = [{"laiLo": -1.0} for _ in range(40)]
    t3 = chan_doan(lo, hc, {}, nguonMau="chay-lai")
    ma = [x.ma for x in t3]
    kiem("đủ mẫu + lỗ đều → chẩn ra kỳ vọng âm", "ky-vong-am" in ma, ma)
    kiem("đủ mẫu thì KHÔNG còn báo thiếu mẫu", "thieu-mau" not in ma, ma)


def kiem_tien_hoa_chay_that() -> None:
    print("\n-- Vong tien hoa: GOI THAT mot luot, khong thay bang lambda ---")
    from kham.tien_hoa import mot_luot

    # Phép kiểm này tồn tại vì một lỗi đã lọt: tôi thêm một tham số vào
    # `chan_doan()` rồi dán nhầm nó sang lời gọi `de_bai()`. Cả bộ kiểm
    # vẫn XANH 281/281, còn `mot_luot()` thì ném `TypeError` ngay dòng đầu
    # — vì không phép nào gọi nó THẬT. Mọi phép kiểm quanh vòng tiến hoá
    # đều thay nó bằng một `lambda`, tức là kiểm cái lịch chạy chứ không
    # kiểm cái được chạy.
    #
    # Hàm này là chỗ cả vòng tự tiến hoá đi qua. Nó phải được gọi thật,
    # dù chỉ trên băng rỗng: chữ ký sai thì gãy ngay đây.
    kq = mot_luot(thu=True)
    kiem("gọi thật mot_luot(thu=True) không ném", kq is not None)
    d = kq.tom_tat()
    for khoa in ("luc", "soKhungBang", "soLenhKetToan", "trieuChung",
                 "deXuat", "ghiChu", "nguonMau"):
        kiem(f"kết quả có khoá `{khoa}`", khoa in d, sorted(d)[:8])
    kiem("băng rỗng → nguồn mẫu vẫn là THẬT", d["nguonMau"] == "that",
         d["nguonMau"])
    kiem("băng rỗng → vẫn báo thiếu mẫu",
         any(t.get("ma") == "thieu-mau" for t in d["trieuChung"]),
         [t.get("ma") for t in d["trieuChung"]])
    # Bất biến thật KHÔNG phải "không đề xuất gì". Chẩn đoán nay đọc được
    # cả bảng hiệu chỉnh — dựng được mà không cần một lệnh nào — nên nó
    # CÓ THỂ đề xuất vặn nút mô hình. Thứ không bao giờ được phép xảy ra
    # là NHẬN: cổng đo trên băng rỗng thì không có gì để so, và một tham
    # số đổi mà không đo được là đúng thứ cả cung này dựng lên để chặn.
    kiem("băng rỗng → KHÔNG BAO GIỜ nhận đề xuất nào",
         d["nhan"] is None, d["nhan"])


def kiem_huong_de_xuat() -> None:
    print("\n-- De xuat phai di DUNG HUONG benh -------------------------")
    from kham.chan_doan import TrieuChung
    from kham.tien_hoa import de_xuat_tat_dinh

    def thu(nhan):
        tc = [TrieuChung("mo-hinh-lech", 2, "x", {"chieu": nhan},
                         ["dinhGia.batDinhToiThieu"])]
        dx = de_xuat_tat_dinh(tc)
        return dx[0].tom_tat() if dx else None

    # Đã thấy tận mắt trên băng thật: chẩn ra "thiên RỤT RÈ QUÁ" rồi đề
    # xuất SIẾT bất định chặt thêm — đúng ngược hướng bệnh. Cổng trả lại
    # nên không hại gì, nhưng một người đề xuất chỉ biết đi MỘT chiều thì
    # mãi mãi không tìm ra chiều kia, và vòng đứng yên vì lý do sai.
    a = thu("RỤT RÈ QUÁ")
    kiem("rụt rè quá → NỚI bất định ra", a and a["den"] < a["tu"],
         f"{a['tu']} → {a['den']}" if a else None)

    b = thu("TỰ TIN QUÁ")
    kiem("tự tin quá → SIẾT bất định vào", b and b["den"] > b["tu"],
         f"{b['tu']} → {b['den']}" if b else None)

    c = thu("hai chiều lẫn lộn")
    kiem("lẫn lộn → vẫn đề xuất, không đứng im", c is not None)

    # `dung-ngoai` là bệnh ngược, và nó KHÔNG được lẫn với luật trên.
    tc = [TrieuChung("dung-ngoai", 2, "x", {},
                     ["canLoi.netEdgeToiThieu"])]
    dx = de_xuat_tat_dinh(tc)
    d = dx[0].tom_tat() if dx else None
    kiem("đứng ngoài quá → NỚI ngưỡng lợi thế", d and d["den"] < d["tu"],
         f"{d['tu']} → {d['den']}" if d else None)


def kiem_cong_phan_biet() -> None:
    print("\n-- Cong phai PHAN BIET duoc hai cau hinh --------------------")
    from kham.chan_doan import TrieuChung
    from kham.ket_qua import so_ket_qua
    from kham.tien_hoa import DeXuat, thu_mot_de_xuat

    # Băng giả: một cửa sổ, sổ hai bên có hàng, mô hình lệch xa giá chợ.
    def muc(g, l):
        return {"gia": g, "luong": l}

    khung = []
    for i in range(80):
        slug = f"btc-updown-5m-{1787000000 + i * 300}"
        so_ket_qua.o[slug] = {"slug": slug, "upThang": i % 3 != 0}
        khung.append({"thiTruong": [{
            "ma": "BTC_5M", "slug": slug, "giaiDoan": "quan-sat",
            "giaNen": 70000.0 + i, "giaMo": 70000.0,
            "sigmaGiay": 1.0e-5, "conLaiGiay": 120.0,
            "so": {
                "UP": {"bid": [muc(0.40, 900)], "ask": [muc(0.42, 900)]},
                # ảnh soi gương của sổ UP — xem `CapSo.nhat_quan`
                "DOWN": {"bid": [muc(0.58, 900)], "ask": [muc(0.60, 900)]},
            }}]})

    dx = DeXuat(nut="dinhGia.batDinhToiThieu", tuGiaTri=0.005,
                denGiaTri=0.30, chuaTrieuChung="mo-hinh-lech", lyLe="thử")
    kq = thu_mot_de_xuat(khung, dx)
    A, B = kq["A"], kq["B"]

    # Đây là bất biến CHÍNH. Bản đầu đặt config sang giá trị mới rồi chạy
    # cả hai lượt với hai `ThamSo` giống hệt nhau — tức so một thứ với
    # chính nó, nên A luôn bằng B và tám trong mười nút KHÔNG BAO GIỜ qua
    # nổi cổng. Cổng vẫn chạy, vẫn in phán quyết; chỉ là phán quyết vô
    # nghĩa, và không có gì trên đời lộ ra điều đó.
    kiem("đổi bất định 0,005 → 0,30 thì HAI lượt phải khác nhau",
         A["soQuaSang"] != B["soQuaSang"] or A["tongLaiLo"] != B["tongLaiLo"],
         f"A qua sàng {A['soQuaSang']} / B {B['soQuaSang']}")

    kiem("cổng trả về phán quyết đọc được",
         isinstance(kq.get("cho"), bool) and kq.get("lyDo") is not None,
         kq.get("lyDo"))

    # Và config phải được TRẢ LẠI nguyên trạng dù đi nhánh nào.
    from kham.config import CONFIG
    kiem("config trả lại nguyên trạng sau khi thử",
         abs(float(CONFIG["dinhGia"]["batDinhToiThieu"]) - 0.30) > 1e-9,
         CONFIG["dinhGia"]["batDinhToiThieu"])


def kiem_giam_chan_dong() -> None:
    print("\n-- Nut van duoc thi phai VAN duoc that ----------------------")
    from kham.chan_doan import NUT_THEO_DUONG, kep
    from kham.config import CONFIG
    from kham.dinh_gia import HieuChinh
    from kham.nan_lai import khop

    kiem("giảm chấn nằm trong bảng vặn",
         "nanLai.heSoGiamChan" in NUT_THEO_DUONG)
    kiem("vượt trần thì bị kẹp", kep("nanLai.heSoGiamChan", 1.5) == 1.0)
    kiem("dưới sàn thì bị kẹp", kep("nanLai.heSoGiamChan", 0.1) == 0.30)

    # Bẫy: hằng số đọc CONFIG lúc nạp module thì cổng sẽ thử giá trị mới,
    # đo ra "không khác gì" — vì phép nắn vẫn dùng giá trị cũ — rồi trả
    # lại. Nút có mặt trong bảng mà vặn không nhúc nhích là kiểu hỏng im
    # lặng tệ nhất: mọi thứ chạy, chỉ kết quả là vô nghĩa.
    # Sổ GIẢ, không dùng sổ thật: môi trường kiểm trỏ `KTG_DATA_DIR` sang
    # thư mục tạm nên `HieuChinh()` rỗng, và phép kiểm sẽ lặng lẽ đi tắt
    # qua đúng ba khẳng định quan trọng nhất. Một phép kiểm bỏ qua phần
    # đáng kiểm mà vẫn in dấu ✓ thì tệ hơn không có.
    class _SoGia:
        def __init__(self, cap):
            self.o = {}
            for i, (du, that) in enumerate(cap):
                self.o[f"o{i}"] = {"n": 80, "thang": round(that * 80),
                                   "tongP": du * 80}

    nen = [(0.05, 0.01), (0.15, 0.03), (0.25, 0.10), (0.35, 0.14),
           (0.45, 0.46), (0.55, 0.50), (0.65, 0.76), (0.75, 0.93),
           (0.85, 0.99), (0.95, 1.00)]
    pn = khop(_SoGia(nen))
    kiem("khớp được đường nắn từ sổ giả", pn.dung_duoc)
    cu = CONFIG["nanLai"]["heSoGiamChan"]
    try:
        CONFIG["nanLai"]["heSoGiamChan"] = 0.30
        thap = pn.nan(0.75)
        CONFIG["nanLai"]["heSoGiamChan"] = 1.00
        cao = pn.nan(0.75)
    finally:
        CONFIG["nanLai"]["heSoGiamChan"] = cu
    kiem("đổi giảm chấn thì kết quả nắn ĐỔI THEO", abs(cao - thap) > 1e-6,
         f"0,30 → {thap:.4f} · 1,00 → {cao:.4f}")
    kiem("giảm chấn cao hơn thì nắn mạnh hơn", cao > thap)
    kiem("tóm tắt khai đúng hệ số đang dùng",
         abs(pn.tom_tat()["heSoGiamChan"] - cu) < 1e-9)


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

    # Chụp sổ TRƯỚC khi chạy. Bản trước viết
    #     not SO_TIEN_HOA.exists() or True
    # — `or True` làm phép kiểm không bao giờ trượt được. Ai đó gặp trở
    # ngại (sổ nằm ở KTG_DATA_DIR tạm nên có thể đã tồn tại) rồi vô hiệu
    # hoá phép kiểm thay vì sửa nó. Mà "chế độ thử không ghi gì" là cả
    # cơ sở của cờ `--thu`: nếu nó sai thì một lượt CHẠY THỬ ghi thật
    # vào sổ tiến hoá, và không ai biết.
    #
    # Cách đúng: so bytes trước/sau. Đúng dù sổ có sẵn hay chưa.
    truocSo = SO_TIEN_HOA.read_bytes() if SO_TIEN_HOA.exists() else None

    kq = tien_hoa_mot_luot(thu=True)
    kiem("chạy được một lượt mà không ném", kq is not None)
    kiem("luôn ghi lại triệu chứng", len(kq.trieuChung) >= 1)

    sauSo = SO_TIEN_HOA.read_bytes() if SO_TIEN_HOA.exists() else None
    kiem("chế độ thử KHÔNG ghi sổ — không đổi một byte nào",
         sauSo == truocSo,
         f"trước {len(truocSo or b'')} byte, sau {len(sauSo or b'')} byte")
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


def kiem_nguon_khung() -> None:
    """Băng phải ĐỌC LẠI ĐƯỢC, và thứ chỉ đọc được một lần phải bị chặn.

    Hai chỗ hỏng khác nhau, cùng một hậu quả: cổng tiến hoá quét băng hai
    lượt ở hai trạng thái config, nên lượt thứ hai mà thấy băng rỗng thì
    cổng phán "chưa đủ mẫu" — một câu đúng ngữ pháp, sai sự thật, và
    không kèm một dòng đỏ nào.
    """
    print("\n── Nguồn khung: quét lại được, và cạn thì phải nói ───────────")

    # Thư mục băng tạm đã có khung của phép kiểm trước, nên đo THÊM
    # bao nhiêu chứ đừng đo tổng — một phép kiểm chỉ đúng khi chạy một
    # mình thì sớm muộn cũng đỏ vì lý do không liên quan.
    truoc = dem_bang().soKhung
    m = MayGhi()
    for i in range(6):
        m.ghi({"vong": i, "thiTruong": []})
    m.dong()

    ng = NguonKhung()
    a = list(ng)
    kiem("lượt quét đầu đọc được khung", len(a) == truoc + 6,
         f"đọc {len(a)}, chờ {truoc + 6}")
    kiem("soKhung khớp với lượt vừa quét", ng.soKhung == len(a),
         f"{ng.soKhung} vs {len(a)}")
    b = list(ng)
    kiem("lượt quét THỨ HAI đọc lại đủ, không cạn", len(b) == len(a),
         f"lượt 1 {len(a)} khung, lượt 2 {len(b)} khung — "
         "đây chính là chỗ cổng tiến hoá nói dối nếu hỏng")
    kiem("đếm được số lượt đã quét", ng.soLuot == 2)
    kiem("iter() trả về đối tượng KHÁC, nên không phải iterator một lần",
         iter(ng) is not ng)

    ts = ThamSo(ten="t", netEdgeToiThieu=0.0, bienAnToan=0.0)

    # Danh sách và NguonKhung: đều phải chạy được.
    for ten, nguon in (("danh sách", list(ng)), ("NguonKhung", NguonKhung())):
        try:
            chay_lai_mot_luot(nguon, ts)
            dat = True
        except TypeError:
            dat = False
        kiem(f"chay_lai nhận {ten}", dat)

    # Generator: phải bị chặn TO TIẾNG, không được âm thầm trả 0.
    def sinh():
        yield from ({"vong": i, "thiTruong": []} for i in range(3))

    g = sinh()
    da_chan = False
    try:
        chay_lai_mot_luot(g, ts)
    except TypeError as e:
        da_chan = "một lần" in str(e)
    kiem("chay_lai CHẶN generator dùng một lần", da_chan,
         "im lặng nhận nó là cách sinh ra một cổng phán bừa")

    # Và bằng chứng vì sao phải chặn: quét lượt hai trên generator ra 0.
    g2 = sinh()
    n1 = len(list(g2))
    n2 = len(list(g2))
    kiem("bằng chứng: generator quét lượt hai ra RỖNG",
         n1 == 3 and n2 == 0, f"{n1} rồi {n2}")


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
    # `_chay_tien_hoa` nay gọi `_hoc_offline` TRƯỚC, và việc ấy đi mạng
    # (lấy 10.000 nến Binance) rồi ghi đè sổ hiệu chỉnh. Bộ kiểm này chạy
    # KHÔNG mạng và đang kiểm chuyện khác hẳn — chặn nó lại, và chặn ở
    # đây chứ không nới điều kiện trong mã thật.
    hoc_cu = V.Runtime._hoc_offline
    V.Runtime._hoc_offline = lambda self: None
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
        V.Runtime._hoc_offline = hoc_cu
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


def kiem_bus_gop_dong_lap() -> None:
    """Dòng lặp phải GỘP, không được đẩy dòng hiếm ra khỏi đệm.

    Đo thật trên buồng lái đang chạy: 78 trong 80 dòng là ĐÚNG NĂM câu
    lặp lại, tất cả nói một chuyện (mất đường tới chợ). Cái trần đệm khi
    ấy chỉ quyết định dòng nào bị đẩy ra — và dòng bị đẩy ra luôn là
    dòng HIẾM, tức dòng đáng đọc nhất. Đúng cơ chế đã giấu
    `KeyError: 'gamma'` suốt mấy tiếng.
    """
    print("\n── Nhật ký: gộp dòng lặp, giữ dòng hiếm ───────────────────────")

    from kham.bus import Bus

    b = Bus(tran=10)
    b.ghi("chuyện HIẾM, chỉ nói một lần", loai="loi")
    for _ in range(50):
        b.ghi("mất đường tới chợ", loai="canh")

    d = b.gan_day(50)
    muc = [e["muc"] for e in d]
    kiem("50 lần kêu chỉ chiếm 1 dòng",
         muc.count("mất đường tới chợ") == 1, muc)
    kiem("dòng HIẾM không bị đẩy ra",
         "chuyện HIẾM, chỉ nói một lần" in muc, muc)
    lap = [e for e in d if e["muc"] == "mất đường tới chợ"][0]
    kiem("dòng gộp tự khai số lần", lap.get("soLan") == 50, lap.get("soLan"))
    kiem("giữ mốc BẮT ĐẦU, không phải mốc kêu gần nhất",
         lap.get("tuLuc") and lap["tuLuc"] <= lap["luc"], lap)
    kiem("dòng gộp nằm CUỐI (mới nhất)", d[-1]["muc"] == "mất đường tới chợ")
    kiem("stt vẫn tăng đều", [e["stt"] for e in d] == sorted(e["stt"] for e in d))
    kiem("tổng đếm vẫn đếm ĐỦ 51 lần ghi", b.tong() == 51, b.tong())

    # Hai câu KHÁC nhau thì không được gộp vào nhau.
    b2 = Bus(tran=20)
    b2.ghi("A", loai="canh")
    b2.ghi("B", loai="canh")
    b2.ghi("A", loai="canh")
    m2 = [e["muc"] for e in b2.gan_day(20)]
    kiem("hai câu khác nhau không dính vào nhau", m2 == ["B", "A"], m2)

    # Cùng câu nhưng KHÁC loại là hai chuyện khác nhau.
    b3 = Bus(tran=20)
    b3.ghi("x", loai="canh")
    b3.ghi("x", loai="loi")
    kiem("cùng câu khác loại thì KHÔNG gộp", len(b3.gan_day(20)) == 2)

    # Kêu lại sau khi đã im lâu phải là dòng MỚI — "im rồi lại kêu" là tin.
    b4 = Bus(tran=200)
    b4.ghi("dai", loai="canh")
    for i in range(Bus._GOP_TRONG + 1):
        b4.ghi(f"chuyện khác {i}", loai="tin")
    b4.ghi("dai", loai="canh")
    m4 = [e["muc"] for e in b4.gan_day(200)]
    kiem("im lâu rồi kêu lại thì ghi dòng MỚI", m4.count("dai") == 2, m4[:3])

    # Buồng lái phải IN số lần ra, không thì gộp xong lại thành giấu.
    GOC_MA = Path(__file__).resolve().parent.parent
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("app.js có in `soLan` ra màn hình", "soLan" in js)


def kiem_dich_vu_hoi_cong() -> None:
    """Câu "nó có đang chạy không" phải hỏi CỔNG, và không được SỬA gì.

    Ba lỗi chồng nhau, đo được thật 30/08/2026: pid.txt ghi một tiến
    trình đã chết, cổng 5186 do một tiến trình khác giữ và runtime vẫn
    sống khoẻ, còn `trang-thai.ps1` in "KHÔNG chạy" rồi XOÁ LUÔN pid.txt
    — tức là câu hỏi chỉ đọc lại phá mất tay nắm duy nhất của dung.ps1.
    Hệ quả nặng nhất: cổng cửa của `bat.ps1` cũng đọc pid.txt, nên nó
    sẵn sàng dựng runtime THỨ HAI ghi chung một quyển sổ.
    """
    print("\n── Dịch vụ: hỏi CỔNG, và đường chỉ đọc không được sửa ────────")

    N = chr(10)
    GOC_MA = Path(__file__).resolve().parent.parent
    dv = GOC_MA / "dichvu"
    ten = ("bat.ps1", "dung.ps1", "trang-thai.ps1")
    doc = {t: (dv / t).read_text(encoding="utf-8-sig") for t in ten}

    kiem("có chung.ps1 để ba script dùng chung", (dv / "chung.ps1").exists())
    chung = (dv / "chung.ps1").read_text(encoding="utf-8-sig")
    kiem("chung.ps1 hỏi cổng chứ không chỉ hỏi pid",
         "Get-NetTCPConnection" in chung and "Ai-Giu-Cong" in chung)
    kiem("cổng đọc từ config.json, không chép số vào script",
         "config.json" in chung and "function Doc-Cong" in chung)

    for t in ten:
        kiem(f"{t} KHÔNG tự định nghĩa lại Lay-Pid",
             "function Lay-Pid" not in doc[t])
        kiem(f"{t} nạp chung.ps1", "chung.ps1" in doc[t])

    # Đường CHỈ ĐỌC thì không được có động từ sửa. Đây là cả cái lỗi.
    #
    # CẮT CHÚ THÍCH TRƯỚC KHI DÒ. Bản đầu dò thẳng vào văn bản và báo
    # hỏng ngay — thứ nó bắt được là câu chú thích *"không Remove-Item,
    # không Stop-Process"* mà tôi vừa viết để giải thích luật. Chú thích
    # giải thích một thứ bị tính là chính thứ đó; đã cắn nhiều lần rồi.
    def khong_chu_thich(vb: str) -> str:
        ra = []
        for d in vb.splitlines():
            t = d.split("#", 1)[0]
            if t.strip():
                ra.append(t)
        return N.join(ra)

    ma = khong_chu_thich(doc["trang-thai.ps1"])
    kiem("phép dò này CÓ cắt được chú thích", "Remove-Item" in doc["trang-thai.ps1"]
         and "Remove-Item" not in ma)
    for dv_ in ("Remove-Item", "Stop-Process", "Start-Process", "Set-Content",
                "Out-File"):
        kiem(f"trang-thai.ps1 không có `{dv_}`", dv_ not in ma, dv_)

    kiem("bat.ps1 hỏi CỔNG trước khi dựng thêm một cái nữa",
         "Lay-Runtime" in doc["bat.ps1"])
    kiem("dung.ps1 giết theo CỔNG, không giết theo pid.txt",
         "Lay-Runtime" in doc["dung.ps1"]
         and "Stop-Process -Id $tt.Id" in doc["dung.ps1"])
    kiem("dung.ps1 kiểm lại sau khi giết: cổng còn ai giữ không",
         doc["dung.ps1"].count("Lay-Runtime") >= 2)
    kiem("trang-thai.ps1 dán tuổi lên nhật ký",
         "LastWriteTime" in doc["trang-thai.ps1"]
         and "CŨ HƠN TIẾN TRÌNH" in doc["trang-thai.ps1"])

    # BOM: file .ps1 không BOM thì PowerShell 5.1 đọc chữ Việt bằng ANSI
    # và script không parse nổi. Đã cắn thật, ghi ngay đầu mỗi file.
    for t in ten + ("chung.ps1",):
        kiem(f"{t} lưu UTF-8 CÓ BOM",
             (dv / t).read_bytes()[:3] == b"\xef\xbb\xbf")

def kiem_bao_cao_doc_hien_ra() -> None:
    """Báo cáo ĐỌC phải tới được buồng lái, và None ≠ sạch.

    `BaoCaoDoc` tính rất kỹ — phân biệt "cụt đuôi" (bình thường sau mỗi
    lần tắt máy) với "đứt giữa" (mất dữ liệu thật) — rồi VỨT ĐI. Buồng
    lái chỉ hiện thống kê GHI, nên đo được trên máy 30/08/2026: hai file
    băng đứt giữa và 200.695 byte phải nhảy qua nằm trên đĩa suốt mà
    không chỗ nào nói ra. Một phép đo đã tính xong mà không ai đọc được
    thì bằng chưa đo.
    """
    print("\n── Băng: báo cáo ĐỌC phải hiện ra ───────────────────────────")

    import kham.bang as B

    cu = B._BAO_CAO_CUOI
    try:
        B._BAO_CAO_CUOI = None
        kiem("chưa quét lượt nào thì trả None, KHÔNG trả bản sạch giả",
             B.bao_cao_doc_cuoi() is None)

        bao = B.BaoCaoDoc(soFile=3, soFileHong=1, soFileCutDuoi=2,
                          soKhung=100, soByteBoQua=999)
        bao.fileHong.append("bang-2026-08-20.jsonl.gz")

        # Lượt quét CÓ LỌC NGÀY không được ghi đè: nó không mở file cũ,
        # nên báo cáo của nó nói "sạch" về những file nó chưa hề nhìn.
        B._nho_bao_cao(bao, "2026-08-29")
        kiem("lượt quét lọc ngày KHÔNG ghi đè báo cáo đầy đủ",
             B.bao_cao_doc_cuoi() is None)

        B._nho_bao_cao(bao, None)
        r = B.bao_cao_doc_cuoi()
        kiem("lượt quét đầy đủ thì có ghi lại", r is not None)
        kiem("giữ đủ số đứt giữa", r["soFileHong"] == 1, r)
        kiem("giữ đủ số byte nhảy qua", r["soByteBoQua"] == 999, r)
        kiem("kể TÊN file hỏng, không chỉ đếm",
             r["fileHong"] == ["bang-2026-08-20.jsonl.gz"], r)
        kiem("có mốc thời gian để biết nó cũ tới đâu", bool(r.get("luc")))
        kiem("trả BẢN SAO, sửa bên ngoài không đụng bản gốc",
             (r.pop("soFile") is not None)
             and B.bao_cao_doc_cuoi()["soFile"] == 3)

        # Cụt đuôi KHÔNG phải hỏng — gộp hai thứ là đèn đỏ vĩnh viễn.
        b2 = B.BaoCaoDoc(soFile=3, soFileHong=0, soFileCutDuoi=3, soKhung=9)
        B._nho_bao_cao(b2, None)
        kiem("chỉ cụt đuôi thì vẫn là LÀNH LẶN",
             B.bao_cao_doc_cuoi()["lanhLan"] is True)
    finally:
        B._BAO_CAO_CUOI = cu

    GOC_MA = Path(__file__).resolve().parent.parent
    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    kiem("vong.py gắn báo cáo đọc vào khối `bang`",
         "bao_cao_doc_cuoi()" in vg)
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("app.js vẽ báo cáo đọc ra", "b.doc" in js and "soFileHong" in js)
    kiem("app.js nói rõ CHƯA ĐO khác với SẠCH",
         "Chưa lượt quét băng đầy đủ nào" in js)

def kiem_tien_do_khong_phai_loi() -> None:
    """Dòng tiến độ bình thường không được mang mức ERROR.

    `dichvu/chay-nen.py` bắt stdout thành INFO và stderr thành ERROR.
    Đó là mặc định ĐÚNG cho tiến trình nền — traceback lạc ra stderr thì
    đúng là lỗi thật. Nhưng `tien_hoa._buoc` in bảy dòng tiến độ mỗi lượt
    ra stderr, nên nhật ký thật có:

        ERROR    [tiến hoá 2/7] đo: 87214 khung, sổ thật 1 lệnh  (+14s)

    Chẳng có gì hỏng ở đó. Mà `trang-thai.ps1` in mười dòng cuối, nên
    mười dòng ấy toàn ERROR vô nghĩa — rồi lần nhật ký ghi một ERROR
    THẬT, nó nằm lẫn vào. Mức báo động dùng sai chỗ thì thôi mang nghĩa.
    """
    print("\n── Tiến độ không được đội lốt lỗi ────────────────────────────")

    N = chr(10)
    GOC_MA = Path(__file__).resolve().parent.parent

    def khong_chu_thich(vb: str) -> str:
        # Cắt chú thích trước khi dò: chính đoạn văn giải thích lỗi này
        # có chữ `sys.stderr` trong đó.
        import io, tokenize
        try:
            ra, cu = [], None
            for t in tokenize.generate_tokens(io.StringIO(vb).readline):
                if t.type in (tokenize.COMMENT, tokenize.STRING):
                    continue
                ra.append(t.string)
                _ = cu
            return " ".join(ra)
        except Exception:
            return vb

    # Cấm IN ra stderr. `__init__.py` có nhắc `_sys.stderr` để đặt lại mã
    # hoá luồng — đó không phải in, và bắt cả nó là bắt nhầm.
    xau = []
    for f in sorted((GOC_MA / "kham").glob("*.py")):
        ma = khong_chu_thich(f.read_text(encoding="utf-8"))
        if "file = sys . stderr" in ma or "file = stderr" in ma:
            xau.append(f.name)
    kiem("không module `kham/` nào IN thẳng ra stderr", not xau, xau)

    # Phép dò tự kiểm chính nó: một mẫu có `file=sys.stderr` NẰM TRONG
    # chú thích thì không được bị bắt. Chú thích giải thích một thứ bị
    # tính là chính thứ đó — đã cắn nhiều lần trong repo này.
    mau = ("# ví dụ: print(x, file=sys.stderr)" + N
           + '"""tài liệu nhắc file=sys.stderr"""' + N
           + "print(1)" + N)
    kiem("phép dò CÓ cắt được chú thích và chuỗi tài liệu",
         "file = sys . stderr" not in khong_chu_thich(mau))
    kiem("nhưng vẫn bắt được lời gọi THẬT",
         "file = sys . stderr" in khong_chu_thich("print(1, file=sys.stderr)"))

    cn = (GOC_MA / "dichvu" / "chay-nen.py").read_text(encoding="utf-8")
    kiem("chay-nen.py vẫn giữ stderr → ERROR (traceback thì đúng là lỗi)",
         "_Ong(logging.ERROR)" in cn)
    kiem("và stdout → INFO", "_Ong(logging.INFO)" in cn)

def kiem_phat_lai_khai_that() -> None:
    """Phiên giấy phải khai đúng: khoảng tin, phép nắn, và bộ đếm.

    Ba chỗ nói sai, đo thật trên phiên chạy hết băng 30/08/2026:

    1. In "+3,30%" trên BẢY cửa sổ mà không một khoảng tin nào. Lấy lại
       theo cửa sổ thì khoảng tin là [−$130,75, +$183,26] — CHỨA 0.
       Con số ấy đọc như kết luận nhưng là tiếng ồn.
    2. `soLanKhopNan` mang tên "số lần khớp lại" mà đếm số lần GỌI, nên
       báo cáo nói "khớp lại 7 lần" trong khi nó khớp lại ĐÚNG 0 lần.
    3. `chay()` trả về mà không khớp lại lần cuối, nên `phepNan` in ra
       là bản 0 mẫu lúc khai sinh trong khi sổ đã có 17 mẫu — báo cáo
       đọc một cỗ máy không phải cỗ máy vừa chạy.
    """
    print("\n── Phiên giấy phải khai đúng những gì nó đã làm ──────────────")

    from kham.phat_lai import KetQuaPhien, NHIP_KHOP_NAN, PhienPhatLai

    kq = KetQuaPhien()
    kiem("có sổ lãi lỗ TỪNG cửa sổ để lấy lại khoảng tin",
         hasattr(kq, "laiLoTungCuaSo") and kq.laiLoTungCuaSo == [])

    GOC_MA = Path(__file__).resolve().parent.parent
    sc = (GOC_MA / "scripts" / "chay-phat-lai.py").read_text(encoding="utf-8")
    kiem("báo cáo in khoảng tin 95%", "khoảng tin 95%" in sc)
    kiem("và nói thẳng khi khoảng tin CHỨA 0", "CHỨA 0" in sc)
    kiem("lấy lại THEO CỬA SỔ, không theo dòng",
         "laiLoTungCuaSo" in sc)
    kiem("khai phép nắn ở CUỐI phiên, không chỉ ở đầu",
         "phép nắn cuối phiên" in sc)
    # `--von` có đổi được gì không: câu này PHẢI trả lời. Đo được:
    # $1.000 và $100.000 cho ĐÚNG cùng 20 lệnh và cùng $23,59 — vì
    # Kelly TẮT (sổ hiệu chỉnh của phiên khởi đầu rỗng, cố ý) nên cỡ
    # lệnh ghim ở lô sàn. Không nói ra thì `--von=100000` cho +0,02%
    # và người đọc kết luận "máy kiếm kém trên vốn lớn".
    kiem("báo cáo khai Kelly bật hay tắt", "Kelly" in sc)
    kiem("và nói rõ khi TẮT thì cỡ lệnh KHÔNG theo vốn",
         "KHÔNG theo vốn" in sc)
    kiem("và nói máy chạy THẬT thì khác", "Máy CHẠY THẬT thì khác" in sc)
    kiem("và nói rõ lãi lỗ là của mô hình THÔ khi nắn chưa bật",
         "mô hình THÔ" in sc)

    # Bộ đếm phải đếm đúng việc mang tên nó.
    ph = PhienPhatLai.__new__(PhienPhatLai)
    ph.soLanKhopNan = 0
    ph._soLanGoiKhop = 0
    ph.hieuChinh = None
    goi = [0]

    import kham.phat_lai as PL
    cu = PL.khop_nan
    try:
        def gia(_hc):
            goi[0] += 1
            return "phep-nan-gia"
        PL.khop_nan = gia
        for _ in range(NHIP_KHOP_NAN * 2):
            PhienPhatLai._khop_lai_nan(ph)
    finally:
        PL.khop_nan = cu

    kiem("gọi 2×nhịp thì khớp lại ĐÚNG 2 lần", goi[0] == 2, goi[0])
    kiem("`soLanKhopNan` đếm lần KHỚP, không đếm lần gọi",
         ph.soLanKhopNan == 2, ph.soLanKhopNan)
    kiem("số lần gọi được đếm riêng",
         ph._soLanGoiKhop == NHIP_KHOP_NAN * 2, ph._soLanGoiKhop)

    pl = (GOC_MA / "kham" / "phat_lai.py").read_text(encoding="utf-8")
    than = pl[pl.index("def chay("):]
    kiem("`chay()` khớp lại lần cuối TRƯỚC khi trả kết quả",
         than.index("khop_nan(self.hieuChinh)") < than.index("return self.kq"))

def kiem_co_dong_lenh() -> None:
    """Cờ gõ sai phải DỪNG, không được nuốt im lặng.

    Mười script đo đạc từng có mười bộ đọc cờ giống hệt nhau, và cả mười
    hỏng theo cùng một kiểu: cờ nào không thấy thì trả mặc định, cờ LẠ
    thì không ai nói gì. `--vốn=10000` (có dấu), `--von 10000` (dấu cách),
    `--capital=10000` — cả ba chạy ngon lành ở giá trị MẶC ĐỊNH rồi in ra
    một báo cáo trông hoàn toàn hợp lệ.

    Với một bộ dụng cụ ĐO thì đó là lỗi nặng: phép đo báo cáo một cấu
    hình khác cấu hình người ta yêu cầu, và không dấu vết nào để lần.
    """
    print("\n── Cờ dòng lệnh: gõ sai phải DỪNG ────────────────────────────")

    from kham import tham_so

    khai = {"von": "vốn", "quet": tham_so.BAT}

    def thu(av):
        try:
            return tham_so.doc(khai, argv=av, ten="thu"), None
        except SystemExit as e:
            return None, e.code

    co, _ = thu(["--von=555"])
    kiem("cờ đúng thì đọc được", co.lay("von") == "555")
    kiem("và đổi ra số được", co.so("von") == 555.0)
    co, _ = thu([])
    kiem("vắng cờ thì trả mặc định", co.lay("von", "9") == "9")
    kiem("cờ bật/tắt vắng thì False", co.co("quet") is False)
    co, _ = thu(["--quet"])
    kiem("cờ bật/tắt có mặt thì True", co.co("quet") is True)

    # Năm kiểu gõ sai — cả năm phải DỪNG với mã 2.
    for av, vi in ((["--vốn=555"], "cờ có dấu tiếng Việt"),
                   (["--capital=5"], "cờ tên khác hẳn"),
                   (["--von"], "cờ cần giá trị mà không cho"),
                   (["--quet=1"], "cờ bật/tắt mà lại gán giá trị"),
                   (["bua"], "tham số trần không có `--`")):
        _, ma = thu(av)
        kiem(f"DỪNG khi {vi}", ma == 2, (av, ma))

    _, ma = thu(["--help"])
    kiem("--help thì in bảng cờ rồi thoát ÊM (mã 0)", ma == 0, ma)

    co, _ = thu(["--von=aaa"])
    try:
        co.so("von")
        dung = False
    except SystemExit as e:
        dung = e.code == 2
    kiem("giá trị sai kiểu thì DỪNG, không lặng lẽ lùi về mặc định", dung)

    try:
        co.lay("chua-khai")
        nem = False
    except KeyError:
        nem = True
    kiem("hỏi một cờ chưa khai thì ném — lỗi của người viết script", nem)

    # Không script nào được giữ bộ đọc cờ riêng nữa.
    GOC_MA = Path(__file__).resolve().parent.parent
    rieng, thieu = [], []
    for f in sorted((GOC_MA / "scripts").glob("*.py")):
        # `kiem-*.mjs` là JavaScript, không dính. Nhưng `kiem-*.py` thì
        # vẫn là phép ĐO viết bằng Python và chịu đúng kỷ luật ấy —
        # `kiem-nan-ngoai-mau.py` còn đưa ra khuyến nghị vặn nút.
        if f.name in ("selftest.py", "sinh-icon.py"):
            continue
        ma = f.read_text(encoding="utf-8")
        if "def _tham(" in ma or "def _tham_so(" in ma:
            rieng.append(f.name)
        if "in sys.argv" in ma:
            rieng.append(f.name)
        if "tham_so.doc(" not in ma:
            thieu.append(f.name)
    kiem("không script nào giữ bộ đọc cờ riêng", not rieng, rieng)
    kiem("mọi script đo đạc đều khai cờ qua `tham_so.doc`", not thieu, thieu)

def kiem_doc_bang_quet() -> None:
    """KHÔNG GIAO DỊCH không phải HOÀ VỐN.

    `chay-demo.py --quet` in bảng "chợ giỏi tới đâu thì bot hết lãi" và
    rút ra w* — con số chính script gọi là "quyết định cả cung này có
    tương lai hay không". Bảng đo thật ngày 30/08/2026:

        0.90   202 kết toán   +$90,28
        0.95     0 kết toán    $0,00   ← không cơ hội nào qua cổng rủi ro
        1.00     0 kết toán    $0,00

    Phép dò đổi dấu đọc số 0 ấy thành "hoà vốn ở w = 0,95" rồi in ra
    "chợ giỏi hơn mức đó thì bot LỖ". Bot không lỗ ở đó — nó ĐỨNG
    NGOÀI. Hai chuyện khác hẳn nhau, và cái sai đẩy w* lên CAO hơn
    thật, tức về phía lạc quan.
    """
    print("\n── Bảng quét: không giao dịch ≠ hoà vốn ──────────────────────")

    import ast as _ast

    GOC_MA = Path(__file__).resolve().parent.parent
    src = (GOC_MA / "scripts" / "chay-demo.py").read_text(encoding="utf-8")
    cay = _ast.parse(src)
    ham = next((n for n in cay.body
                if isinstance(n, _ast.FunctionDef) and n.name == "doc_quet"), None)
    kiem("`doc_quet` tách ra được thành hàm thuần", ham is not None)
    if ham is None:
        return
    ns: dict = {}
    exec(compile(_ast.Module(body=[ham], type_ignores=[]),
                 "<doc_quet>", "exec"), ns)
    dq = ns["doc_quet"]

    kiem("dương → âm thì đúng là hoà vốn",
         dq([(0.0, 10, 500.0), (0.5, 10, 100.0), (0.8, 10, -50.0)])
         == (0.8, None))
    kiem("dương → 0 lệnh thì KHÔNG phải hoà vốn, mà là đứng ngoài",
         dq([(0.0, 10, 500.0), (0.9, 10, 90.0),
             (0.95, 0, 0.0), (1.0, 0, 0.0)]) == (None, 0.95),
         dq([(0.0, 10, 500.0), (0.9, 10, 90.0),
             (0.95, 0, 0.0), (1.0, 0, 0.0)]))
    kiem("lãi suốt dãy thì không có mốc nào",
         dq([(0.0, 10, 500.0), (1.0, 10, 300.0)]) == (None, None))
    # Hàng "không giao dịch" nằm GIỮA không được xoá dấu vết mức lãi
    # trước nó — nếu xoá thì lần đổi dấu sau đó bị bỏ sót.
    kiem("hàng 0 lệnh ở giữa không làm mất lần đổi dấu sau đó",
         dq([(0.0, 10, 500.0), (0.5, 0, 0.0),
             (0.8, 10, 200.0), (0.9, 10, -5.0)]) == (0.9, 0.5))

    kiem("bảng dán nhãn ⟨không giao dịch⟩ ngay trên hàng ấy",
         "không giao dịch" in src)
    kiem("và câu kết nói ĐỨNG NGOÀI chứ không nói LỖ",
         "ĐỨNG NGOÀI" in src)

def kiem_so_phien_khong_tich_lai() -> None:
    """Sổ của phiên phát lại phải SẠCH mỗi lần chạy.

    `So.ghi` luôn nối thêm — đúng cho sổ thật, sai cho phiên phát lại,
    vì phiên ấy chạy đi chạy lại trên CÙNG một cuộn băng. Đo trên đĩa
    30/08/2026: 33 dòng sổ, chỉ 6 mốc thời gian riêng biệt, một mốc lặp
    8 lần, tổng lãi lỗ đọc từ file $165,89 — gấp năm lần sự thật $32,99.

    Báo cáo trong phiên vẫn đúng (nó đếm trên `kq`), nhưng thứ CÒN LẠI
    TRÊN ĐĨA là thuốc độc. Đúng bẫy đã cắn ở `chay_lai`: đếm mỗi cửa sổ
    44 lần → +2,9 triệu đô trên tài khoản 1.000 đô.
    """
    print("\n── Sổ phiên phát lại: sạch mỗi lần chạy ──────────────────────")

    import tempfile

    from kham.config import DATA_DIR
    from kham.phat_lai import _don_so_phien

    with tempfile.TemporaryDirectory() as d:
        tm = Path(d)
        (tm / "ket-toan.jsonl").write_text('{"laiLo": 1}' + chr(10),
                                           encoding="utf-8")
        (tm / "hieu-chinh.json").write_text("{}", encoding="utf-8")
        (tm / "khac.txt").write_text("giữ nguyên", encoding="utf-8")
        _don_so_phien(tm)
        kiem("xoá sổ kết toán của phiên trước",
             not (tm / "ket-toan.jsonl").exists())
        kiem("xoá cả sổ hiệu chỉnh — giữ lại là NHÌN TRỘM TƯƠNG LAI",
             not (tm / "hieu-chinh.json").exists())
        kiem("không đụng file khác trong thư mục",
             (tm / "khac.txt").exists())
        lai = None
        try:
            _don_so_phien(tm)   # gọi lại khi đã sạch
        except Exception as e:  # noqa: BLE001
            lai = repr(e)
        kiem("gọi lại lúc đã sạch thì im lặng, không ném", lai is None, lai)

    # Chặn cứng: một lỗi truyền `thuMucSo` sai là xoá sạch sổ kết toán
    # THẬT. Cửa này phải đóng, và phải đóng bằng ngoại lệ chứ không phải
    # bằng lời dặn trong tài liệu.
    # Chụp trạng thái sổ thật TRƯỚC, để câu "vẫn còn nguyên" là một
    # phép đo chứ không phải một hằng đúng.
    fThat = Path(DATA_DIR) / "ket-toan.jsonl"
    truoc = fThat.read_bytes() if fThat.exists() else None

    nem = False
    try:
        _don_so_phien(Path(DATA_DIR))
    except RuntimeError:
        nem = True
    except Exception:
        nem = False
    kiem("TỪ CHỐI xoá khi trỏ vào thư mục sổ THẬT", nem)

    sau = fThat.read_bytes() if fThat.exists() else None
    kiem("sổ thật KHÔNG suy suyển một byte nào", sau == truoc,
         f"trước {len(truoc or b'')} byte, sau {len(sau or b'')} byte")

    GOC_MA = Path(__file__).resolve().parent.parent
    pl = (GOC_MA / "kham" / "phat_lai.py").read_text(encoding="utf-8")
    kiem("phiên gọi dọn sổ ngay lúc khai sinh",
         "_don_so_phien(tm)" in pl)

def kiem_khong_co_phep_kiem_gia() -> None:
    """Không phép kiểm nào được LUÔN ĐÚNG. Bộ kiểm tự soi chính nó.

    Một phép kiểm không bao giờ trượt được thì tệ hơn không có phép kiểm:
    nó xanh vĩnh viễn và làm người đọc tin rằng thứ nó nhắc tới đã được
    canh. Tìm được hai cái, và cái nặng là:

        kiem("chế độ thử KHÔNG ghi sổ",
             not SO_TIEN_HOA.exists() or True)

    `or True` — ai đó gặp trở ngại rồi vô hiệu hoá phép kiểm thay vì sửa
    nó. Mà "chế độ thử không ghi gì" là cả cơ sở của cờ `--thu`: nếu nó
    sai thì một lượt CHẠY THỬ ghi thật vào sổ tiến hoá.

    Đây là bản trong-nhà của luật đã ghi ở [thước đo hỏng thì điểm đẹp]:
    phiếu 7/7 có thể là thước gãy. Nên bộ kiểm phải tự soi được mình.
    """
    print("\n── Bộ kiểm tự soi: không phép kiểm nào luôn đúng ─────────────")

    import ast as _ast

    def luon_dung(n) -> bool:
        """Biểu thức LUÔN đúng bất kể chương trình chạy ra sao?"""
        if isinstance(n, _ast.Constant):
            return bool(n.value)
        if isinstance(n, _ast.BoolOp) and isinstance(n.op, _ast.Or):
            # `X or True`
            if any(isinstance(x, _ast.Constant) and bool(x.value)
                   for x in n.values):
                return True
            # `A or not A`
            dump = [_ast.dump(x) for x in n.values]
            for i, x in enumerate(n.values):
                if isinstance(x, _ast.UnaryOp) and isinstance(x.op, _ast.Not):
                    if _ast.dump(x.operand) in dump[:i] + dump[i + 1:]:
                        return True
        return False

    goc = Path(__file__).resolve()
    cay = _ast.parse(goc.read_text(encoding="utf-8"))
    xau = []
    for n in _ast.walk(cay):
        if not (isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                and n.func.id == "kiem"):
            continue
        if len(n.args) >= 2 and luon_dung(n.args[1]):
            nhan = (n.args[0].value if isinstance(n.args[0], _ast.Constant)
                    else "?")
            xau.append(f"dòng {n.lineno}: {str(nhan)[:50]}")
    kiem("không phép kiểm nào luôn đúng", not xau, "; ".join(xau))

    # Và phép dò tự chứng minh nó BẮT ĐƯỢC — không thì nó lại đúng là
    # thứ nó đi tìm.
    def dò(ma: str) -> bool:
        c = _ast.parse(ma).body[0].value
        return luon_dung(c.args[1])

    kiem("bắt được `True`", dò('kiem("x", True)'))
    kiem("bắt được `X or True`", dò('kiem("x", a.b() or True)'))
    kiem("bắt được `not A or A`", dò('kiem("x", not p.exists() or p.exists())'))
    kiem("KHÔNG bắt nhầm phép so thật", not dò('kiem("x", a == b)'))
    kiem("KHÔNG bắt nhầm `A or B` khác nhau",
         not dò('kiem("x", a.exists() or b.exists())'))
    kiem("KHÔNG bắt nhầm `X or False`", not dò('kiem("x", a() or False)'))

def kiem_phi_khong_bien_mat() -> None:
    """Phí phải bị TRỪ khỏi lãi lỗ, ở cả đường thật lẫn đường giấy.

    `dat_lenh` tính phí đúng, in phí ra nhật ký (`phí $0.0900`), rồi thả
    nó xuống đất: `ghi_khop` không nhận phí, `tienUp/tienDown` là tiền
    HÀNG, và `ket_toan._ghi_so` ghi thẳng `phiUsd=0.0`. Hệ quả:

      · sổ kết toán khai tổng phí = $0 vĩnh viễn
      · lãi lỗ đẹp hơn sự thật đúng bằng khoản phí
      · `risk.ghi_lai_lo` nhận con số đẹp ấy ⇒ cầu dao lỗ ngày mù phí

    Cỡ lỗi: phiên giấy chạy hết băng trả $2,93 phí trên $32,99 lãi — 9%.
    Và nó KHÔNG phải chuyện tương lai: chế độ giấy cũng tính phí thật.

    Nghịch lý làm lộ ra: `phat_lai.py` (mô phỏng) TRỪ phí đúng, còn
    đường chạy thật thì không — nên máy thật sẽ báo đẹp hơn chính bản
    mô phỏng của nó trên cùng những lệnh ấy.
    """
    print("\n── Phí không được biến mất khỏi lãi lỗ ──────────────────────")

    from kham.kho_doi import ViThe

    v = ViThe(ma="BTC_5M")
    v.ghi_khop("UP", 100, 0.40, 0.80)
    v.ghi_khop("UP", 100, 0.42, 0.84)
    kiem("phí cộng dồn qua nhiều lần khớp",
         abs(v.phiUsd - 1.64) < 1e-9, v.phiUsd)
    kiem("tiền vào vẫn là tiền HÀNG, không lẫn phí",
         abs(v.tienUp - 82.0) < 1e-9, v.tienUp)
    kiem("trả về khi thắng là số cổ × $1 (gộp, chưa trừ gì)",
         abs(v.gia_tri_khi_ket_qua(True) - 200.0) < 1e-9)
    kiem("lãi lỗ RÒNG đã trừ phí",
         abs(v.lai_lo_khi_ket_qua(True) - (200.0 - 82.0 - 1.64)) < 1e-9,
         v.lai_lo_khi_ket_qua(True))
    kiem("thua cũng phải trừ phí",
         abs(v.lai_lo_khi_ket_qua(False) - (0.0 - 82.0 - 1.64)) < 1e-9,
         v.lai_lo_khi_ket_qua(False))
    kiem("không truyền phí thì mặc định 0 (chỗ chỉ đo phơi nhiễm)",
         ViThe(ma="x").phiUsd == 0.0)

    GOC_MA = Path(__file__).resolve().parent.parent

    def khong_chu_thich(vb: str) -> str:
        return chr(10).join(d.split("#", 1)[0] for d in vb.splitlines())

    dl = khong_chu_thich((GOC_MA / "kham" / "dat_lenh.py")
                         .read_text(encoding="utf-8"))
    kiem("đường đặt lệnh TRUYỀN phí vào vị thế",
         "ghi_khop(l.ben, l.soCoKhop, l.giaKhop, l.phiUsd)" in dl)

    kt = khong_chu_thich((GOC_MA / "kham" / "ket_toan.py")
                         .read_text(encoding="utf-8"))
    kiem("kết toán ghi phí THẬT, không ghi 0", "phiUsd=v.phiUsd" in kt)
    kiem("và KHÔNG còn ghi cứng phiUsd=0.0", "phiUsd=0.0" not in kt)
    kiem("dọn vị thế thì dọn cả phí — không rớt sang cửa sổ sau",
         kt.count("v.phiUsd = 0.0") >= 2, kt.count("v.phiUsd = 0.0"))

    # Bất biến CHUNG cho cả hai đường: một dòng sổ phải tự nhất quán.
    # Đây là thứ nối `ket_toan` (thật) với `phat_lai` (giấy) về một
    # định nghĩa duy nhất của chữ "lãi lỗ".
    import json as _json

    from kham.config import DATA_DIR
    lech = []
    for ten in ("ket-toan.jsonl",):
        for thu in (Path(DATA_DIR) / ten,
                    GOC_MA / "data" / "phat-lai" / ten):
            if not thu.exists():
                continue
            for d in thu.read_text(encoding="utf-8").splitlines():
                if not d.strip():
                    continue
                try:
                    g = _json.loads(d)
                except ValueError:
                    continue
                if not all(k in g for k in
                           ("laiLo", "tienRa", "tienVao", "phiUsd")):
                    continue
                if abs(g["laiLo"] - (g["tienRa"] - g["tienVao"]
                                     - g["phiUsd"])) > 1e-6:
                    lech.append(f"{thu.name}: {g.get('luc')}")
    kiem("mọi dòng sổ đã ghi đều thoả laiLo = tienRa − tienVao − phiUsd",
         not lech, lech[:3])

def kiem_phien_giay_dung_giai_doan() -> None:
    """Phiên giấy phải tính GIAI ĐOẠN, không đóng cứng một chuỗi lạ.

    `phat_lai` từng truyền `giaiDoan="dat-cuoc"` — một chuỗi KHÔNG nằm
    trong bốn giai đoạn hợp lệ. Hai chiến thuật soi thẳng trường ấy:

        tao-lap      đòi giaiDoan ∈ (gom, giua)
        can-ket-qua  đòi giaiDoan ∈ (cuoi, can-ket)

    nên cả hai lặng lẽ trả rỗng suốt phiên. Đếm được: trong 1.018 lượt
    gọi, chỉ `lech-gia`, `phong-ho`, `cap-*` đề xuất — hai ngón nghề kia
    ĐÚNG 0 lần. Con số lãi lỗ của phiên giấy vì thế là của một cỗ máy
    KHÁC cỗ máy đang chạy thật (+$32,99 → +$23,59 sau khi sửa).

    Đây đúng lỗi `vong.py` đã sửa ở bước 7 và ghi chú dài dòng. Sửa một
    nơi mà không quét tìm bản sao thì nó ở lại nơi kia.
    """
    print("\n── Phiên giấy phải tính giai đoạn thật ──────────────────────")

    from kham.dongho import (CAN_KET_QUA, CUOI_KHUNG, GIUA_KHUNG,
                             GOM_THANH_KHOAN, giai_doan_theo_thoi_gian)

    hople = {GOM_THANH_KHOAN, GIUA_KHUNG, CUOI_KHUNG, CAN_KET_QUA}
    kiem("`dat-cuoc` KHÔNG phải một giai đoạn hợp lệ",
         "dat-cuoc" not in hople)

    # Đi hết một khung 300s: phải chạm được cả hai đầu mà hai chiến
    # thuật kia cần, không thì chúng vẫn im.
    thay = {giai_doan_theo_thoi_gian(t, 300.0) for t in range(300, 0, -1)}
    kiem("có giai đoạn `tao-lap` dùng được",
         bool(thay & {GOM_THANH_KHOAN, GIUA_KHUNG}), sorted(thay))
    kiem("có giai đoạn `can-ket-qua` dùng được",
         bool(thay & {CUOI_KHUNG, CAN_KET_QUA}), sorted(thay))

    GOC_MA = Path(__file__).resolve().parent.parent

    def khong_chu_thich(vb: str) -> str:
        return chr(10).join(d.split("#", 1)[0] for d in vb.splitlines())

    pl = khong_chu_thich((GOC_MA / "kham" / "phat_lai.py")
                         .read_text(encoding="utf-8"))
    kiem("phat_lai KHÔNG còn đóng cứng giaiDoan",
         'giaiDoan="dat-cuoc"' not in pl)
    kiem("mà gọi chung một phép tính với đường thật",
         "giai_doan_theo_thoi_gian(tau, tong)" in pl)
    kiem("`tongGiay` là ĐỘ DÀI KHUNG, không phải max(tau, 1)",
         "max(tau, 1.0)" not in pl and "_dai_song_giay(ma)" in pl)

    # Và phép tính ấy phải là MỘT chỗ — `dongho` giữ bản gốc.
    dh = khong_chu_thich((GOC_MA / "kham" / "dongho.py")
                         .read_text(encoding="utf-8"))
    kiem("dongho xuất tên công khai cho phép tính giai đoạn",
         "def giai_doan_theo_thoi_gian" in dh)
    kiem("và nó gọi lại `_giai_doan` chứ không chép logic",
         "return _giai_doan(conLaiGiay, tongGiay)" in dh)

def kiem_quyet_chan_la_loi_khuyen() -> None:
    """`quyet_chan` là LỜI KHUYÊN — và điều đó phải được nói ra.

    `vong._mot_thi_truong` gọi nó mỗi vòng, cất vào `self.quyetChan[ma]`,
    gửi qua API và vào cả ẢNH CHỤP CÔNG KHAI — rồi không chỗ nào huỷ
    lệnh, nâng giá, vượt spread hay đóng chân theo nó. Buồng lái cũng
    KHÔNG vẽ nó ra. Một phép tính đi suốt đường ống rồi chết ở cuối.

    Không sửa thành hành động: nối `DONG_CHAN` / `VUOT_SPREAD` / `HUY`
    vào là đổi hành vi giao dịch thật, phải là quyết định có chủ ý và đo
    được. Nhưng cái TÊN `quyet` đọc như thể có ai thi hành, nên chỗ nào
    nói ra sự thật ấy thì phải giữ được — bằng phép canh, không bằng
    lòng tin.
    """
    print("\n── `quyet_chan` phải tự khai là lời khuyên ──────────────────")

    GOC_MA = Path(__file__).resolve().parent.parent

    crr = (GOC_MA / "kham" / "chan_rui_ro.py").read_text(encoding="utf-8")
    kiem("chan_rui_ro nói rõ đây là LỜI KHUYÊN",
         "LỜI KHUYÊN, KHÔNG PHẢI HÀNH ĐỘNG" in crr)
    kiem("và kể ba lớp đã che phần nguy hiểm",
         all(x in crr for x in ("capChuaKhopToiDaUsd", "cap_theo_thoi",
                                "tự tất toán")))
    kiem("và nói rõ ca nào KHÔNG được che",
         "không ai bán bên thiếu" in crr)

    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    kiem("chỗ gọi cũng ghi, không bắt người đọc đi tra",
         "LỜI KHUYÊN, không phải hành động" in vg)

    # Nếu có ngày ai nối nó vào thật, phép canh này phải TRƯỢT để người
    # ấy buộc phải quay lại sửa cả tài liệu — chứ không lặng lẽ đi qua.
    than = vg[vg.index("qc = quyet_chan("):]
    than = than[:than.index("# 7.")] if "# 7." in than else than[:400]
    ma = chr(10).join(d.split("#", 1)[0] for d in than.splitlines())
    kiem("hiện tại `qc` KHÔNG dẫn tới hành động nào",
         not any(x in ma for x in ("dat_lenh", "huy(", "dong_chan",
                                   "vuot_spread")), ma[:120])

    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("buồng lái VẼ lời khuyên ra", "T.quyetChan" in js)
    kiem("và dán nhãn để không ai tưởng bot tự làm",
         "bot KHÔNG tự làm" in js)

def kiem_quet_vi_khai_nga() -> None:
    """Ví ngã phải hiện ra, không được biến mất không dấu vết.

    `DaiQuanVi.quet` từng là `except Exception: continue` trần. Một
    `KeyError` trong `_mot_vi` làm MỌI ví trượt im lặng, và buồng lái
    hiện "Chưa quét ví nào. Lượt quét cách nhau 30 phút, nên trống ở đây
    chỉ có nghĩa là chưa tới lượt." — một câu AN ỦI SAI, đúng lúc mọi
    thứ đang hỏng.

    Cùng hình dạng lỗi đã giấu `KeyError: gamma` suốt mấy tiếng, và cùng
    cách chữa đã dùng cho nó: vẫn đi tiếp, nhưng GHI LẠI và KHAI RA.
    """
    print("\n── Quét ví: ngã thì phải khai ─────────────────────────────────")

    import kham.vi as V

    v = V.DaiQuanVi()
    cu = V.nguon.hoat_dong_vi
    try:
        def no(*a, **k):
            raise KeyError("gamma")
        V.nguon.hoat_dong_vi = no
        r = v.quet(["0xAAA", "0xBBB"])
    finally:
        V.nguon.hoat_dong_vi = cu

    kiem("một ví hỏng không giết cả lượt quét", isinstance(r, dict))
    kiem("ghi lại ĐỦ hai ví ngã", len(v.nga) == 2, v.nga)
    kiem("và ghi cả LÝ DO, không chỉ tên",
         all("KeyError" in x for x in v.nga.values()), v.nga)
    kiem("`tom_tat` khai ra cho buồng lái đọc",
         v.tom_tat().get("nga") == v.nga)

    # Lượt sau sạch thì sổ ngã phải RỖNG lại — không thì một lỗi cũ ám
    # mãi và người đọc thôi tin cái đèn ấy.
    v.quet([])
    kiem("lượt quét sau sạch thì sổ ngã rỗng lại", v.nga == {}, v.nga)

    GOC_MA = Path(__file__).resolve().parent.parent
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("buồng lái vẽ danh sách ví ngã", "v.nga" in js)
    kiem("và KHÔNG còn an ủi sai khi mọi ví đều ngã",
         "không phải vì chưa tới lượt" in js)

def kiem_rui_ro_nho_qua_khoi_dong_lai() -> None:
    """Khởi động lại KHÔNG được xoá sạch trí nhớ rủi ro.

    `RiskEngine.__init__` đặt `von = vonBanDau` từ config và không đọc
    gì. Đo được trên máy: sổ ghi một lệnh lỗ $49,95 mà buồng lái vẫn
    khai `von 1.000` và `sutVonPct 0,0%`.

    Ba cầu dao dựa trên đúng những con số ấy — trần lỗ ngày, trần sụt
    vốn, và cỡ lệnh Kelly. Nên một bot vừa chạm trần lỗ ngày, bị khởi
    động lại (sập, cập nhật, hay người bấm), có NGAY một ngân sách lỗ
    mới nguyên. Lỗ hổng kiểm soát rủi ro kinh điển, và nó im lặng:
    buồng lái hiện những con số đẹp và đúng cú pháp.
    """
    print("\n── Rủi ro phải NHỚ qua khởi động lại ────────────────────────")

    import time as _t

    from kham.kho_doi import Kho
    from kham.rui_ro import RiskEngine

    hn = _t.strftime("%Y-%m-%d", _t.gmtime())
    ds = [{"luc": "2026-08-01T10:00:00Z", "laiLo": 120.0},
          {"luc": "2026-08-01T11:00:00Z", "laiLo": -60.0},
          {"luc": hn + "T10:00:00Z", "laiLo": -30.0},
          {"luc": hn + "T11:00:00Z", "laiLo": 10.0}]

    r = RiskEngine(Kho())
    v0 = r.vonBanDau
    nap = r.nap_tu_so(ds)
    kiem("vốn dựng lại đúng tổng lãi lỗ",
         abs(r.von - (v0 + 40.0)) < 1e-9, r.von)
    kiem("ĐỈNH vốn là đỉnh của cả đường, không phải giá trị cuối",
         abs(r.dinhVon - (v0 + 120.0)) < 1e-9, r.dinhVon)
    kiem("sụt vốn đo từ đỉnh ấy", r.sutVonPct > 0.0, r.sutVonPct)
    kiem("lỗ NGÀY chỉ tính dòng của hôm nay",
         abs(r.loNgayUsd - 20.0) < 1e-9, r.loNgayUsd)
    kiem("lỗ gộp ngày vẫn đếm riêng độ chao",
         abs(r.loGopNgayUsd - 30.0) < 1e-9, r.loGopNgayUsd)
    kiem("trả về bản tóm tắt để chỗ gọi KHAI RA",
         nap["soDong"] == 4 and "von" in nap, nap)

    # Dòng sổ CŨ không được tính vào lỗ ngày — ngày lấy từ mốc trong sổ,
    # không lấy đồng hồ máy. Lấy đồng hồ thì đọc lại một sổ cũ là mọi
    # dòng đều thành "hôm nay" và cầu dao ngắt oan ngay lúc khởi động.
    r2 = RiskEngine(Kho())
    r2.nap_tu_so([{"luc": "2020-01-01T00:00:00Z", "laiLo": -999.0}])
    kiem("dòng sổ CŨ không rơi vào lỗ ngày", r2.loNgayUsd == 0.0,
         r2.loNgayUsd)
    kiem("nhưng vẫn trừ vào vốn", r2.von < v0, r2.von)

    # Ca quan trọng nhất: sổ cho thấy ĐÃ quá trần thì cầu dao phải ngắt
    # NGAY lúc nạp, chứ không đợi lệnh kế tiếp — vì có thể không bao giờ
    # có lệnh kế tiếp nào để soát.
    r3 = RiskEngine(Kho())
    qua = r3.tranLoNgayUsd * 2.0 + 1.0
    r3.nap_tu_so([{"luc": hn + "T09:00:00Z", "laiLo": -qua}])
    kiem("sổ đã quá trần lỗ ngày ⇒ cầu dao NGẮT ngay lúc nạp",
         r3.ngatKhanCap, (r3.ngatKhanCap, r3.lyDoNgat))

    # Sổ rỗng thì phải y hệt lúc khai sinh, không được lệch một xu.
    r4 = RiskEngine(Kho())
    r4.nap_tu_so([])
    kiem("sổ rỗng thì trạng thái y hệt khai sinh",
         r4.von == v0 and r4.dinhVon == v0 and not r4.ngatKhanCap)

    # Dòng rác không được làm sập lúc khởi động.
    r5 = RiskEngine(Kho())
    r5.nap_tu_so([{"luc": "x", "laiLo": "khong-phai-so"}, {"laiLo": 5.0}])
    kiem("dòng rác bị bỏ qua, không ném", abs(r5.von - (v0 + 5.0)) < 1e-9,
         r5.von)

    GOC_MA = Path(__file__).resolve().parent.parent
    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    kiem("runtime gọi nạp lúc khởi động", "risk.nap_tu_so(self.so.doc())" in vg)
    kiem("và KÊU khi không dựng lại được",
         "KHÔNG dựng lại được rủi ro từ sổ" in vg)

def kiem_tran_theo_von_dau_ngay() -> None:
    """Ba trần phải neo vào VỐN ĐẦU NGÀY, không vào một hằng số config.

    `_tran` từng tính `vonBanDau * pct`. `vonBanDau` là hằng số trong
    config, không bao giờ đổi — nên tài khoản mất nửa vốn thì trần "5%
    lỗ ngày" vẫn là $50, tức 10% của số còn lại. **Rủi ro lớn lên đúng
    lúc tài khoản yếu đi**, ngược hẳn ý nghĩa của một trần phần trăm.

    Nhưng cũng KHÔNG được neo vào vốn hiện tại: trần lỗ ngày chạy theo
    vốn đang lỗ dần thì nó lùi xa mãi. Một cái trần đuổi theo chính mình
    thì không phải trần.
    """
    print("\n── Trần neo vào VỐN ĐẦU NGÀY ────────────────────────────────")

    import time as _t

    from kham.kho_doi import Kho
    from kham.rui_ro import RiskEngine

    hn = _t.strftime("%Y-%m-%d", _t.gmtime())

    r = RiskEngine(Kho())
    # `vonDauNgay` cố ý LƯỜI: chưa chốt thì là None và `_tran` rơi về
    # `vonBanDau`. Phải thế, vì nhiều chỗ đặt `vonBanDau` SAU khi dựng
    # (`PhienPhatLai(von=...)`); chốt cứng lúc dựng thì `--von=10000`
    # chạy với trần của tài khoản 1.000 đô, im lặng.
    kiem("tài khoản mới: gốc chưa chốt, rơi về vốn ban đầu",
         r.vonDauNgay is None and r.tom_tat()["vonDauNgay"] == r.vonBanDau)
    r2b = RiskEngine(Kho())
    r2b.vonBanDau = 10_000.0
    kiem("nên đặt vốn SAU khi dựng vẫn co giãn trần",
         r2b.tranLoNgayUsd == 500.0, r2b.tranLoNgayUsd)
    tranMoi = r.tranLoNgayUsd
    kiem("và ba trần y hệt như trước", tranMoi == r.vonBanDau * 0.05,
         tranMoi)

    # Vốn đầu ngày phải TRỪ ĐI lãi lỗ đã xảy ra trong ngày. Lấy thẳng
    # `von` là sai: khoản lỗ hôm nay đã nằm trong nó, nên trần sẽ co lại
    # theo chính khoản lỗ nó đang đo.
    r2 = RiskEngine(Kho())
    r2.nap_tu_so([{"luc": "2026-08-01T10:00:00Z", "laiLo": -500.0},
                  {"luc": hn + "T10:00:00Z", "laiLo": -30.0}])
    kiem("vốn đầu ngày KHÔNG gồm lãi lỗ của hôm nay",
         abs(r2.vonDauNgay - 500.0) < 1e-9, r2.vonDauNgay)
    kiem("trần co theo tài khoản đã teo",
         abs(r2.tranLoNgayUsd - 25.0) < 1e-9, r2.tranLoNgayUsd)
    kiem("và cầu dao NGẮT — bản cũ để trần $50 nên không ngắt",
         r2.ngatKhanCap, r2.lyDoNgat)

    # Trong NGÀY thì gốc phải đứng yên, không nhúc nhích theo từng lệnh.
    r3 = RiskEngine(Kho())
    goc = r3.vonDauNgay
    tran = r3.tranLoNgayUsd
    r3.ghi_lai_lo(-10.0)
    r3.ghi_lai_lo(-10.0)
    kiem("gốc đứng yên trong ngày", r3.vonDauNgay == goc, r3.vonDauNgay)
    kiem("nên trần cũng đứng yên — không lùi xa theo khoản lỗ",
         r3.tranLoNgayUsd == tran, r3.tranLoNgayUsd)

    # Sang ngày mới thì chốt lại gốc.
    r3.ngay = "1999-01-01"
    kiem("sang ngày mới trả True", r3.sang_ngay_moi() is True)
    kiem("và chốt lại gốc theo vốn hiện tại",
         abs(r3.vonDauNgay - r3.von) < 1e-9, (r3.vonDauNgay, r3.von))
    kiem("trần ngày mới nhỏ hơn vì tài khoản đã teo",
         r3.tranLoNgayUsd < tran, (r3.tranLoNgayUsd, tran))

    # Tài khoản LỚN lên thì trần cũng lớn lên — đó mới là ý của một
    # trần theo phần trăm.
    r4 = RiskEngine(Kho())
    r4.nap_tu_so([{"luc": "2026-08-01T10:00:00Z", "laiLo": 1000.0}])
    kiem("tài khoản gấp đôi thì trần gấp đôi",
         abs(r4.tranLoNgayUsd - 2 * tranMoi) < 1e-9, r4.tranLoNgayUsd)
    kiem("trần mỗi thị trường cũng theo",
         r4.tranMoiThiTruongUsd > RiskEngine(Kho()).tranMoiThiTruongUsd)

    # Vốn âm không được sinh ra trần âm.
    r5 = RiskEngine(Kho())
    r5.vonDauNgay = -100.0
    kiem("vốn âm thì trần bằng 0, không âm", r5.tranLoNgayUsd == 0.0,
         r5.tranLoNgayUsd)

    kiem("buồng lái đọc được gốc ấy", "vonDauNgay" in r.tom_tat())

def kiem_cham_moc_tu_choi_sigma_ngan() -> None:
    """Động cơ chạm mốc phải TỪ CHỐI khi σ đo trên cửa sổ quá ngắn.

    Runtime dùng MỘT cửa sổ σ cho mọi market: 900 giây. Với khung 5 phút
    thì hợp lý. Với `BTC_150K` — chân trời bốn tháng — đó là 900 giây nói
    về 10,7 triệu giây, tỉ lệ 1 : 11.900.

    Đo trên 30 ngày BTC, σ quy năm:

        cửa sổ 900s    trung vị 0,209 · min 0,000 · max 2,239
        cửa sổ 7 ngày  trung vị 0,263 · min 0,203 · max 0,595

    Cửa sổ ngắn vừa THIÊN THẤP (−21%) vừa nhiễu gấp hai nghìn lần. Cắm
    vào chân trời bốn tháng thì P(chạm) nhảy từ ~0% tới ~100% chỉ vì mười
    lăm phút vừa rồi tình cờ lặng hay tình cờ động.

    Từ chối, đúng nguyên tắc của chính module ấy: "None khi thiếu nguyên
    liệu — không bịa". Một σ nhiễu như thế KHÔNG phải nguyên liệu, dù nó
    là một số thực hợp lệ.
    """
    print("\n── Chạm mốc: từ chối khi σ quá ngắn so với chân trời ────────")

    import math as _m

    from kham.cham_moc import cham_moc

    KW = dict(ma="BTC_150K", giaHienTai=78016.0, moc=150000.0,
              dinhDaQua=80000.0,
              sigmaGiay=0.209 / _m.sqrt(365 * 86400.0), lenTren=True)

    kiem("KHÔNG truyền cửa sổ thì cư xử y như trước",
         cham_moc(tauGiay=124 * 86400.0, **KW) is not None)
    kiem("truyền cửa sổ 900s + chân trời 124 ngày ⇒ TỪ CHỐI",
         cham_moc(tauGiay=124 * 86400.0, cuaSoSigmaGiay=900.0, **KW) is None)
    kiem("khung 5 phút KHÔNG bị chặn oan",
         cham_moc(tauGiay=300.0, cuaSoSigmaGiay=900.0, **KW) is not None)

    # Mép: τ = 50×cửa sổ phải QUA, nhích lên là chặn. Một cái cổng mà
    # không ai biết mép nó ở đâu thì không kiểm được.
    kiem("đúng mép 50× thì vẫn qua",
         cham_moc(tauGiay=50.0 * 900.0, cuaSoSigmaGiay=900.0, **KW)
         is not None)
    kiem("nhích qua mép là chặn",
         cham_moc(tauGiay=50.0 * 900.0 + 1.0, cuaSoSigmaGiay=900.0, **KW)
         is None)
    kiem("cửa sổ 0 hoặc âm thì KHÔNG chặn (coi như không khai)",
         cham_moc(tauGiay=124 * 86400.0, cuaSoSigmaGiay=0.0, **KW)
         is not None)

    GOC_MA = Path(__file__).resolve().parent.parent
    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    kiem("runtime TRUYỀN cửa sổ σ vào động cơ",
         "cuaSoSigmaGiay=bd.cuaSoGiay" in vg)
    kiem("và nói rõ LÝ DO chứ không để `None` câm",
         "Từ chối định giá" in vg and "lệch" in vg)

    cm = (GOC_MA / "kham" / "cham_moc.py").read_text(encoding="utf-8")
    kiem("`cham_moc` khai luôn CHIỀU và CỠ của sai lệch bỏ trôi",
         "+40,6%" in cm and "CAO HƠN" in cm)

def kiem_nut_van_khong_bi_dong_bang() -> None:
    """Nút trong bảng vặn phải đọc CONFIG lúc GỌI, không chốt lúc nạp.

    Bẫy này đã cắn thật một lần: `dinhGia.bienDongCuaSoGiay` nằm trong
    bảng vặn của vòng tiến hoá, nhưng `DoBienDong` chốt nó thành hằng số
    lúc import. Cổng thử một giá trị mới, đo ra 'không khác gì' — vì bộ
    ước vẫn dùng giá trị cũ — rồi trả lại. Một nút nằm trong bảng mà
    không ai vặn được thì bằng không có, và tệ hơn: nó làm cổng tiến hoá
    kết luận SAI về chính nút ấy, rồi ghi kết luận sai đó vào sổ.

    `nan_lai` hiện có ba hằng số cùng dạng (`DOI_TOI_DA`, `TOI_THIEU_MAU`,
    `TOI_THIEU_MOI_O`). Hiện KHÔNG sao vì không nút nào trỏ tới chúng —
    nhưng `doiToiDa` là một nút rất hợp lý để ai đó thêm vào ngày mai.

    Nên canh cả LỚP lỗi: soi mã, tìm mọi gán ở CẤP MODULE đọc một khoá
    config mà khoá ấy nằm trong bảng vặn.
    """
    print("\n── Nút vặn được không được đông thành hằng số ───────────────")

    import ast as _ast

    from kham.chan_doan import NUT_VAN

    GOC_MA = Path(__file__).resolve().parent.parent
    nut = {}
    for n in NUT_VAN:
        duong = getattr(n, "duong", None) or getattr(n, "ten", None)
        if duong and "." in duong:
            khu, la = duong.split(".", 1)
            nut.setdefault(khu, set()).add(la)
    kiem("đọc được bảng nút vặn", len(nut) >= 3, sorted(nut))

    def khu_cua(cay):
        """Tên module-level nào đang trỏ vào khu config nào."""
        ra = {}
        for n in cay.body:
            if not isinstance(n, _ast.Assign) or len(n.targets) != 1:
                continue
            t = n.targets[0]
            if not isinstance(t, _ast.Name):
                continue
            for x in _ast.walk(n.value):
                if (isinstance(x, _ast.Constant)
                        and isinstance(x.value, str) and x.value in nut):
                    ra[t.id] = x.value
        return ra

    def khoa_doc(n):
        """Các khoá chuỗi mà biểu thức này đọc, kèm tên đối tượng."""
        ra = []
        for x in _ast.walk(n):
            if (isinstance(x, _ast.Subscript)
                    and isinstance(x.value, _ast.Name)
                    and isinstance(x.slice, _ast.Constant)
                    and isinstance(x.slice.value, str)):
                ra.append((x.value.id, x.slice.value))
            if (isinstance(x, _ast.Call)
                    and isinstance(x.func, _ast.Attribute)
                    and x.func.attr == "get"
                    and isinstance(x.func.value, _ast.Name)
                    and x.args and isinstance(x.args[0], _ast.Constant)
                    and isinstance(x.args[0].value, str)):
                ra.append((x.func.value.id, x.args[0].value))
        return ra

    dong = []
    for f in sorted((GOC_MA / "kham").glob("*.py")):
        cay = _ast.parse(f.read_text(encoding="utf-8"))
        ten_khu = khu_cua(cay)
        if not ten_khu:
            continue
        for n in cay.body:
            if not isinstance(n, _ast.Assign) or len(n.targets) != 1:
                continue
            t = n.targets[0]
            if not isinstance(t, _ast.Name):
                continue
            for obj, khoa in khoa_doc(n.value):
                khu = ten_khu.get(obj)
                if khu and khoa in nut.get(khu, ()):
                    dong.append(f"{f.name}:{n.lineno} {t.id} = {khu}.{khoa}")

    kiem("không nút vặn nào bị chốt thành hằng số lúc nạp module",
         not dong, dong)

    # Phép dò phải tự chứng minh nó BẮT ĐƯỢC, không thì nó chỉ là một
    # dòng xanh vĩnh viễn — đúng thứ `kiem_khong_co_phep_kiem_gia` đi tìm.
    mau = _ast.parse(
        '_NL = CONFIG.get("nanLai") or {}' + chr(10)
        + 'X = float(_NL.get("heSoGiamChan", 1.0))')
    tk = khu_cua(mau)
    bat = [(o, k) for n in mau.body if isinstance(n, _ast.Assign)
           for o, k in khoa_doc(n.value)
           if tk.get(o) and k in nut.get(tk[o], ())]
    kiem("phép dò CÓ bắt được một ca dựng sẵn", bool(bat), bat)

    # Và KHÔNG bắt nhầm chỗ đọc lúc GỌI (trong thân hàm).
    mau2 = _ast.parse(
        '_NL = CONFIG.get("nanLai") or {}' + chr(10)
        + 'def f():' + chr(10)
        + '    return float(_NL.get("heSoGiamChan", 1.0))')
    tk2 = khu_cua(mau2)
    bat2 = [(o, k) for n in mau2.body if isinstance(n, _ast.Assign)
            for o, k in khoa_doc(n.value)
            if tk2.get(o) and k in nut.get(tk2[o], ())]
    kiem("KHÔNG bắt nhầm chỗ đọc trong thân hàm", not bat2, bat2)

def kiem_hai_so_phai_nhat_quan() -> None:
    """Hai sổ lệch soi gương thì KHÔNG được dùng — gần nửa lãi là từ đó.

    Mua UP ≡ bán DOWN, nên sổ DOWN thật và ảnh soi gương của sổ UP phải
    khớp. `lech_soi_guong` đo được điều đó từ đầu, và nó chỉ được VẼ lên
    buồng lái rồi thôi — trong khi chính docstring của nó gọi tình huống
    lệch là "thứ hỏng im lặng".

    Đo trên 1.018 dòng khung ăn thua ĐÃ BẮT ĐƯỢC:

        trung vị 0,000 · p75 0,010 · p90 0,030 · max 0,570
        vượt 1c: 25,6% · vượt 2c: 12,1% · vượt 10c: 6,4%
        chênh MỐC hai sổ: trung vị 0,23s · max 290s

    Gần năm phút giữa hai lát cắt, trên một khung sống đúng năm phút.

    Và chỗ quyết định — đối chiếu với chênh MỐC THỜI GIAN hai sổ:

        lệch ≤ 2c (895 dòng): chênh mốc trung vị    0,22 s
        lệch > 2c (123 dòng): chênh mốc trung vị  114,45 s

    Ngưỡng 10c chứ không phải 2c: phép đo này lẫn hai chuyện CÙNG HÌNH
    DẠNG — dữ liệu lệch giờ, và chênh lệch giá THẬT giữa hai token (thứ
    `cap-tuc-thi` sinh ra để bắt). Chặn ở 2c là chặn luôn cơ hội thật.

    KHÔNG chọn ngưỡng theo lãi lỗ. Thử các ngưỡng cho ra 23,59 / 41,81 /
    16,17 / 13,15 / 10,43 đô — không đơn điệu, và ngưỡng LỎNG nhất lại
    cho lãi cao nhất, vì chặn một dòng giải phóng sức chứa cho dòng sau.
    Trên 6 cửa sổ với khoảng tin ±150 đô thì đó là nhiễu.
    """
    print("\n── Hai sổ phải nói về CÙNG MỘT LÚC ──────────────────────────")

    from kham.cap_token import CapSo
    from kham.config import CONFIG
    from kham.so_lenh import Muc, SoLenh

    def so(ma, ben, bid, ask):
        return SoLenh(ma=ma, ben=ben,
                      bid=[Muc(*x) for x in bid],
                      ask=[Muc(*x) for x in ask],
                      nhanLucMs=0.0)

    # UP: bid 0,40 / ask 0,42  ⇒  ảnh soi gương DOWN: bid 0,58 / ask 0,60
    up = so("X", "UP", [(0.40, 100)], [(0.42, 100)])
    hop = so("X", "DOWN", [(0.58, 100)], [(0.60, 100)])
    lech = so("X", "DOWN", [(0.20, 100)], [(0.22, 100)])   # lệch 38c

    a = CapSo("X", up, hop)
    # `x or 9` là bẫy: lệch BẰNG 0 là kết quả ĐÚNG, mà 0 lại falsy nên
    # `0.0 or 9` cho ra 9. Đúng cái bệnh "số 0 nghĩa là không có gì" mà
    # cả ngày hôm nay đi sửa — và nó cắn vào chính phép kiểm này.
    kiem("hai sổ khớp ⇒ lệch soi gương 0",
         a.lech_soi_guong() is not None
         and abs(a.lech_soi_guong()) < 1e-9, a.lech_soi_guong())
    kiem("và NHẤT QUÁN", a.nhat_quan is True)
    kiem("và dùng được", a.dung_duoc is True)
    kiem("không có lý do từ chối", a.ly_do_khong_dung() is None)

    b = CapSo("X", up, lech)
    kiem("hai sổ lệch 38c ⇒ đo ra đúng",
         abs((b.lech_soi_guong() or 0) - 0.38) < 1e-9, b.lech_soi_guong())
    kiem("KHÔNG nhất quán", b.nhat_quan is False)
    kiem("và KHÔNG dùng được — đây là chỗ bản trước bỏ sót",
         b.dung_duoc is False)
    ly = b.ly_do_khong_dung() or ""
    kiem("lý do nói rõ đây là lợi thế MA", "lợi thế MA" in ly, ly[:70])

    # Lệch cỡ MỘT CƠ HỘI THẬT (5c) phải được qua — nếu không thì cổng
    # này bóp chết đúng chiến thuật `cap-tuc-thi`.
    vua = so("X", "DOWN", [(0.53, 100)], [(0.55, 100)])   # lệch 5c
    kiem("lệch 5c — cỡ một cơ hội thật — vẫn ĐƯỢC QUA",
         CapSo("X", up, vua).nhat_quan is True,
         CapSo("X", up, vua).lech_soi_guong())

    # Ngưỡng phải đọc CONFIG lúc GỌI — nới ra thì cùng cặp sổ ấy qua được.
    cu = (CONFIG.get("capToken") or {}).get("lechSoiGuongToiDa")
    try:
        CONFIG.setdefault("capToken", {})["lechSoiGuongToiDa"] = 0.90
        kiem("nới ngưỡng thì CÙNG cặp sổ ấy qua được (đọc lúc gọi)",
             CapSo("X", up, lech).nhat_quan is True)
    finally:
        if cu is None:
            (CONFIG.get("capToken") or {}).pop("lechSoiGuongToiDa", None)
        else:
            CONFIG["capToken"]["lechSoiGuongToiDa"] = cu
    kiem("trả ngưỡng về rồi thì chặn lại như cũ",
         CapSo("X", up, lech).nhat_quan is False)

    # Phiên giấy phải dùng CHUNG phép kiểm, không tự viết lại.
    GOC_MA = Path(__file__).resolve().parent.parent
    pl = (GOC_MA / "kham" / "phat_lai.py").read_text(encoding="utf-8")
    ma = chr(10).join(d.split("#", 1)[0] for d in pl.splitlines())
    kiem("phiên giấy gọi `CapSo.dung_duoc`", "capSo.dung_duoc" in ma)
    kiem("và KHÔNG còn tự viết phép kiểm riêng",
         "su.dung_duoc or sd.dung_duoc" not in ma)

def kiem_don_bang_qua_han() -> None:
    """Hạn giữ băng phải THẬT SỰ CHẠY, không chỉ nằm trong config.

    `MayGhi.don_cu` có từ đầu, thực thi đúng `bang.ngayGiuLai` khai trong
    config — và KHÔNG AI GỌI NÓ. Một chính sách nằm trong config và trong
    mã mà không bao giờ chạy là một lời hứa hệ thống không giữ.

    Hệ quả đo được: 29 MB băng sau mười ngày, lớn mãi không dừng, trong
    khi `doc_bang` trên TÁM ngày băng đã là 77 giây và 3,4 GB thường trú.
    """
    print("\n── Hạn giữ băng phải thật sự chạy ───────────────────────────")

    import os
    import tempfile
    import time as _t

    import kham.bang as B

    GOC_MA = Path(__file__).resolve().parent.parent
    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    ma = chr(10).join(d.split("#", 1)[0] for d in vg.splitlines())
    kiem("vòng chạy CÓ gọi dọn băng", "may_ghi.don_cu()" in ma)
    kiem("và chỉ mỗi ngày một lần, không mỗi vòng",
         "_ngayDonBang" in ma)
    kiem("gọi trong làn có bảo vệ — một lần dọn hỏng không giết vòng lặp",
         'self._lan("dọn băng"' in ma)

    with tempfile.TemporaryDirectory() as d:
        tm = Path(d)
        cu = B._thu_muc
        try:
            B._thu_muc = lambda: tm
            gia_cu = tm / "bang-2020-01-01.jsonl.gz"
            gia_moi = tm / "bang-2099-01-01.jsonl.gz"
            khac = tm / "khong-phai-bang.txt"
            for f in (gia_cu, gia_moi, khac):
                f.write_bytes(b"x")
            gio = _t.time()
            os.utime(gia_cu, (gio - 400 * 86400, gio - 400 * 86400))

            mg = B.MayGhi.__new__(B.MayGhi)
            mg.duong = gia_moi          # file ĐANG MỞ
            n = B.MayGhi.don_cu(mg)

            kiem("xoá đúng file quá hạn", n == 1 and not gia_cu.exists())
            kiem("KHÔNG xoá file đang mở", gia_moi.exists())
            kiem("KHÔNG đụng file không phải băng", khac.exists())

            n2 = B.MayGhi.don_cu(mg)
            kiem("gọi lại khi đã sạch thì xoá 0, không ném", n2 == 0)
        finally:
            B._thu_muc = cu

def kiem_canh_bao_duoi_di_theo_du_lieu() -> None:
    """Câu cảnh báo đuôi phải đi TRONG dữ liệu, chỉ có MỘT bản.

    `so.dong_canh_bao` có sẵn từ đầu và KHÔNG AI GỌI — trong khi
    `web/app.js` chép tay đúng câu ấy bằng JavaScript. Hai bản của một
    câu thì sớm muộn lệch nhau, và câu này là thứ chặn người đọc hiểu sai
    con số nguy hiểm nhất trong cả hệ: TỈ LỆ THẮNG.

    Một chiến thuật thắng 99,7% mà mỗi lần thua xoá 76 lần thắng thì tỉ
    lệ thắng KHÔNG nói gì về an toàn. `can_ket_qua` mở đầu docstring bằng
    đúng chuyện ấy.
    """
    print("\n── Cảnh báo đuôi: một bản, đi trong dữ liệu ─────────────────")

    from kham.so import thong_ke

    kiem("sổ rỗng ⇒ không có câu cảnh báo",
         thong_ke([]).get("canhBao") is None)
    kiem("đuôi bình thường ⇒ không cảnh báo",
         thong_ke([{"laiLo": 1.0}, {"laiLo": -1.0}]).get("canhBao") is None)

    tk = thong_ke([{"laiLo": 1.0}] * 100 + [{"laiLo": -90.0}])
    c = tk.get("canhBao") or ""
    kiem("đuôi lệch ⇒ CÓ câu cảnh báo", bool(c), c[:60])
    kiem("câu ấy nêu cả tỉ lệ thắng lẫn số lần bị xoá",
         "99.0%" in c and "90 lần thắng" in c, c)
    kiem("và nói thẳng tỉ lệ thắng không nói gì về an toàn",
         "không nói lên điều gì về an toàn" in c)

    GOC_MA = Path(__file__).resolve().parent.parent
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("buồng lái DÙNG câu từ dữ liệu", "tk.canhBao" in js)
    kiem("và KHÔNG còn dựng lại câu ấy bằng JavaScript",
         "MỘT lần thua lớn nhất xoá" not in js)

def kiem_nut_o_mep_phai_lo_ra() -> None:
    """Nút nằm ở MÉP dải vặn phải TỰ LỘ, không đợi ai chạy tay.

    Một nút ở mép nghĩa là cái MÉP đang quyết định, không phải dữ liệu.
    Đã cắn thật: `dinhGia.bienDongCuaSoGiay` có mép trên BẰNG ĐÚNG giá
    trị đang dùng (900). Một nút như thế không bao giờ tăng được, và mọi
    lượt tiến hoá kết luận "giữ nguyên" — nghe như dữ liệu đã nói, thật
    ra là cái lồng đã nói.

    `tien-hoa-mo-hinh` CÓ phát hiện chuyện này, nhưng chỉ khi ai đó chạy
    tay. Buồng lái chạy suốt ngày; đưa nó ra đó thì nó tự lộ.
    """
    print("\n── Nút ở mép dải vặn phải tự lộ ra ──────────────────────────")

    from kham.chan_doan import nut_o_mep
    from kham.config import CONFIG

    kiem("hiện tại không nút nào ở mép", nut_o_mep() == [], nut_o_mep())

    cu = CONFIG["ruiRo"]["kellyPhan"]
    try:
        CONFIG["ruiRo"]["kellyPhan"] = 0.40      # mép TRÊN
        r = nut_o_mep()
        kiem("đặt một nút lên mép trên thì phát hiện được",
             any(x["duong"] == "ruiRo.kellyPhan" and x["ben"] == "trên"
                 for x in r), r)
        CONFIG["ruiRo"]["kellyPhan"] = 0.05      # mép DƯỚI
        r = nut_o_mep()
        kiem("mép dưới cũng phát hiện được",
             any(x["duong"] == "ruiRo.kellyPhan" and x["ben"] == "dưới"
                 for x in r), r)
        CONFIG["ruiRo"]["kellyPhan"] = 0.25      # giữa dải
        kiem("giá trị giữa dải thì KHÔNG báo",
             not any(x["duong"] == "ruiRo.kellyPhan" for x in nut_o_mep()))
    finally:
        CONFIG["ruiRo"]["kellyPhan"] = cu

    GOC_MA = Path(__file__).resolve().parent.parent
    vg = (GOC_MA / "kham" / "vong.py").read_text(encoding="utf-8")
    kiem("buồng lái nhận được danh sách ấy", '"nutOMep": nut_o_mep()' in vg)
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("và VẼ nó ra", "T.nutOMep" in js)
    kiem("kèm câu nói rõ mép đang quyết định",
         "mép đang quyết định" in js)

def kiem_so_ket_qua_khai_nguon() -> None:
    """Sổ kết quả phải khai NGUỒN, không chỉ số lượng.

    Đo trên máy: 4.503 khung, **100% nguồn `tu-tinh`** — không một dòng
    nào do sàn xác nhận. Nghĩa là toàn bộ điểm Brier, toàn bộ điểm kỹ
    năng, cả vòng tiến hoá đều đứng trên một sự thật do CHÍNH MÌNH tính
    ra.

    Với market lên/xuống thì phép tính ấy đơn giản và gần như chắc đúng
    (so giá Binance ở hai mốc). Nhưng "gần như chắc đúng" không phải "đã
    đối chiếu", và `can_ket_qua` liệt kê "sai nguồn giá resolution" là
    một trong những rủi ro vận hành mà không mô hình nào bắt được.

    Buồng lái khai "4.503 khung (2.303 UP / 2.200 DOWN)" mà không nói
    dòng nào được sàn xác nhận — con số nền của cả hệ, thiếu đúng phần
    đáng ngờ nhất.
    """
    print("\n── Sổ kết quả phải khai NGUỒN của sự thật ───────────────────")

    import tempfile

    from kham.ket_qua import SoKetQua

    with tempfile.TemporaryDirectory() as d:
        so = SoKetQua(duong=Path(d) / "kq.jsonl")
        so.them("a-1", True, nguon="tu-tinh")
        so.them("a-2", False, nguon="tu-tinh")
        so.them("a-3", True, nguon="san")
        t = so.tom_tat()
        kiem("đếm đủ số khung", t["soSlug"] == 3, t)
        kiem("tách được số do SÀN xác nhận", t["soTheoSan"] == 1, t)
        kiem("và số tự tính", t["soTuTinh"] == 2, t)
        kiem("hai phần cộng lại bằng tổng",
             t["soTheoSan"] + t["soTuTinh"] == t["soSlug"])

        # Bất đồng vẫn phải được giữ — hai nguồn nói ngược nhau là TIN.
        so.them("a-3", False, nguon="tu-tinh")
        kiem("hai nguồn nói ngược thì đánh dấu BẤT ĐỒNG",
             so.tom_tat()["soBatDong"] == 1, so.tom_tat())
        kiem("và GIỮ kết quả cũ, không ghi đè im lặng",
             so.lay("a-3") is True)

    GOC_MA = Path(__file__).resolve().parent.parent
    js = (GOC_MA / "web" / "app.js").read_text(encoding="utf-8")
    kiem("buồng lái vẽ nguồn ra", "kq.soTheoSan" in js)
    kiem("và kêu to khi CHƯA dòng nào được sàn xác nhận",
         "CHƯA MỘT DÒNG NÀO" in js)

def kiem_doi_chung_cong_bang() -> None:
    """Nhóm đối chứng phải dùng CÙNG mẫu số với nhánh thật.

    `do_tre` đo Binance động trước bao lâu thì Polymarket đổi giá, và nó
    có nhóm đối chứng — mốc thời gian rút NGẪU NHIÊN, cùng số sự kiện.
    Đúng cách, vì chọn bất kỳ mốc nào rồi chờ giá dịch 0,4 xu thì bao giờ
    cũng chờ được, nên không có đối chứng thì mọi con số đều vô nghĩa.

    Nhưng hai bên đếm mẫu số khác nhau:

        thật       len(tre) / len(xong)   ← MỌI cú động
        đối chứng  len(tre) / n           ← chỉ cú ĐÁNH GIÁ ĐƯỢC

    Cú có đệm sổ mỏng bị đối chứng loại khỏi mẫu số, trong khi nhánh thật
    tính chúng vào — ở đó chúng thành "không phản ứng kịp" và KÉO TỈ LỆ
    THẬT XUỐNG. Lệch theo chiều làm tín hiệu thật trông kém hơn, tức
    chiều an toàn; nhưng một nhóm đối chứng KHÔNG CÔNG BẰNG thì không
    phải nhóm đối chứng, và cái so ấy là toàn bộ lý do nó tồn tại.
    """
    print("\n── Nhóm đối chứng phải cùng mẫu số với nhánh thật ───────────")

    from kham.do_tre import DoTre

    class _SK:
        def __init__(self, ma, huong):
            self.ma, self.huong, self.treMs = ma, huong, 0.0

    d = DoTre.__new__(DoTre)
    xong = [_SK("A", 1), _SK("B", 1), _SK("C", 1)]
    poly = {
        "A": [(i * 100.0, 0.50 + (0.02 if i > 50 else 0.0))
              for i in range(200)],
        "B": [(0.0, 0.5)],       # đệm quá mỏng — không đánh giá được
        "C": [],                 # không có đệm
    }
    n, _tv, _ty = DoTre._doi_chung(d, xong, poly)
    kiem("đối chứng đếm CẢ cú không đánh giá được", n == 3, n)

    GOC_MA = Path(__file__).resolve().parent.parent
    dt = (GOC_MA / "kham" / "do_tre.py").read_text(encoding="utf-8")
    ma = chr(10).join(x.split("#", 1)[0] for x in dt.splitlines())
    i = ma.index("def _doi_chung")
    than = ma[i:ma.index("def ", i + 10)]
    # `n += 1` phải đứng TRƯỚC mọi `continue` trong vòng lặp.
    kiem("`n += 1` đứng trước mọi lệnh bỏ qua",
         than.index("n += 1") < than.index("continue"),
         "đặt sau `continue` là loại cú không đánh giá được ra khỏi mẫu số")

    kiem("nhánh thật vẫn chia cho MỌI cú động",
         "len(tre) / len(xong)" in ma)

def kiem_tran_phoi_nhiem_gop() -> None:
    """Bốn cược tương quan là MỘT cược — và phải có trần cho nó.

    `Kho.phoi_nhiem_gop()` tính phơi nhiễm crypto gộp bằng chuẩn bậc hai
    có ma trận tương quan, và docstring của nó nói thẳng: "Trần đặt trên
    từng market không hề chặn được tình huống đó."

    Rồi KHÔNG AI CHẶN theo nó — nó chỉ được vẽ lên buồng lái.

    Khác `quyet_chan` (nơi ba lớp khác đã che phần nguy hiểm), ở đây
    KHÔNG có lớp nào khác: trần mỗi market không che, mà trần mỗi NHÓM
    cũng không, vì bốn crypto nằm ở BỐN nhóm khác nhau — mỗi cái đều
    "trong hạn mức" trong khi cả rổ là một cược duy nhất vào beta crypto.
    """
    print("\n── Trần phơi nhiễm GỘP: bốn cược tương quan là một ─────────")

    from kham.kho_doi import Kho
    from kham.rui_ro import RiskEngine

    kho = Kho()
    r = RiskEngine(kho)
    kiem("có trần cho phơi nhiễm gộp", r.tranPhoiNhiemGopUsd > 0,
         r.tranPhoiNhiemGopUsd)
    kiem("và nó BẰNG trần mỗi nhóm tài sản — cả rổ tương quan là một nhóm",
         abs(r.tranPhoiNhiemGopUsd - r.tranMoiTaiSanUsd) < 1e-9)

    # Bốn market, mỗi cái $90 — dưới trần mỗi market ($100) VÀ dưới trần
    # mỗi nhóm ($200, và mỗi cái một nhóm riêng). Từng cái đều "trong
    # hạn mức"; cả rổ thì không.
    for ma in ("BTC_5M", "ETH_5M", "SOL_5M", "XRP_5M"):
        kho.lay(ma).ghi_khop("UP", 180.0, 0.50)
    gop = kho.phoi_nhiem_gop()
    kiem("từng market đều dưới trần riêng",
         all((kho.lay(m).tienUp + kho.lay(m).tienDown) < r.tranMoiThiTruongUsd
             for m in ("BTC_5M", "ETH_5M", "SOL_5M", "XRP_5M")),
         [kho.lay(m).tienUp for m in ("BTC_5M", "ETH_5M")])
    kiem("nhưng phơi nhiễm GỘP vượt trần",
         gop > r.tranPhoiNhiemGopUsd, (gop, r.tranPhoiNhiemGopUsd))

    # Hai chiều NGƯỢC nhau phải bù trừ — nếu không thì trần này chỉ là
    # một phép cộng đội lốt phép đo rủi ro.
    kho2 = Kho()
    kho2.lay("BTC_5M").ghi_khop("UP", 180.0, 0.50)
    kho2.lay("ETH_5M").ghi_khop("DOWN", 180.0, 0.50)
    kiem("hai chiều ngược nhau thì phơi nhiễm gộp NHỎ đi",
         kho2.phoi_nhiem_gop() < gop,
         (kho2.phoi_nhiem_gop(), gop))

    GOC_MA = Path(__file__).resolve().parent.parent
    rr = (GOC_MA / "kham" / "rui_ro.py").read_text(encoding="utf-8")
    ma = chr(10).join(x.split("#", 1)[0] for x in rr.splitlines())
    kiem("cổng rủi ro THẬT SỰ đọc phơi nhiễm gộp",
         "self.kho.phoi_nhiem_gop()" in ma)
    kiem("và từ chối khi chạm trần",
         "phơi nhiễm crypto GỘP" in rr)

def kiem_chan_lenh_tu_trang_khac() -> None:
    """POST điều khiển phải đến TỪ CHÍNH buồng lái, không từ trang khác.

    Mọi lối POST của buồng lái — `tam-dung`, `cau-dao`, `chien-thuat/{ma}`,
    `huy/{lenhId}`, `tien-hoa`, `chay-lai` — đều KHÔNG thân, KHÔNG xác
    thực. Nghĩa là bất kỳ trang web nào người vận hành mở trong cùng trình
    duyệt đều gọi được:

        fetch("http://localhost:5186/api/tam-dung",
              {method: "POST", mode: "no-cors"})

    Đây là "simple request" nên trình duyệt KHÔNG hỏi preflight. Trang kia
    không đọc được phản hồi, nhưng TÁC DỤNG PHỤ ĐÃ XẢY RA: bot dừng, cầu
    dao lật, chiến thuật tắt, lệnh bị huỷ.

    Nghe ở 127.0.0.1 KHÔNG cứu được — chính trình duyệt trên máy ấy là kẻ
    gửi. Đã thử thật trên runtime đang chạy: trước khi vá, POST kèm
    `Origin: http://evil.example` trả về HTTP 200.
    """
    print("\n── POST điều khiển phải từ chính buồng lái ──────────────────")

    GOC_MA = Path(__file__).resolve().parent.parent
    sv = (GOC_MA / "kham" / "server.py").read_text(encoding="utf-8")
    ma = chr(10).join(x.split("#", 1)[0] for x in sv.splitlines())

    kiem("có chốt chặn cho lệnh đổi trạng thái",
         "@app.middleware" in ma and "_chan_lenh_tu_trang_khac" in ma)
    kiem("GET / HEAD / OPTIONS KHÔNG bị chặn",
         '("GET", "HEAD", "OPTIONS")' in ma)
    kiem("chặn theo `Origin`", 'headers.get("origin")' in ma)
    kiem("và trả 403 chứ không im lặng bỏ qua", "status_code=403" in ma)
    kiem("GHI LẠI mỗi lần từ chối — một cú thử là tin đáng đọc",
         "TỪ CHỐI lệnh POST từ trang khác" in sv)

    # Danh sách Origin phải dựng TỪ CỔNG trong config, không chép số.
    kiem("danh sách Origin dựng từ cổng trong config",
         'CONFIG["port"]' in ma and "_origin_cho_phep" in ma)

    import kham.server as SV
    from kham.config import CONFIG
    ds = SV._origin_cho_phep()
    c = CONFIG["port"]
    kiem("cho phép localhost", f"http://localhost:{c}" in ds, sorted(ds))
    kiem("cho phép 127.0.0.1", f"http://127.0.0.1:{c}" in ds, sorted(ds))
    kiem("KHÔNG cho phép trang lạ", "http://evil.example" not in ds)
    kiem("KHÔNG cho phép đúng host mà SAI CỔNG",
         "http://localhost:1234" not in ds)

def kiem_ban_thu_mot_cho() -> None:
    """Bộ máy chấm của các phép thử chỉ được có MỘT bản.

    Năm script `thu-*` từng có năm bản sao của đúng bộ máy này —
    `nen_ohlc`, `_lay_nen`, `_brier`, `cap_du_doan`, `cham`, `uoc_tron`.
    Chúng ra đời bằng cách chép khung của nhau (tôi chép, hôm nay).

    Ở đây nguy hiểm hơn chỗ khác vì đây là THƯỚC. Thước lệch thì mọi kết
    luận đo bằng nó đều lệch, và không con số nào tự khai chuyện ấy — cả
    năm script vẫn in ra bảng đẹp như thường.
    """
    print("\n── Bàn thử: một bộ máy chấm, không phải năm ─────────────────")

    import ast as _a

    GOC_MA = Path(__file__).resolve().parent.parent
    CHUNG = {"nen_ohlc", "_lay_nen", "_brier", "cap_du_doan", "cham",
             "uoc_tron"}

    kiem("có `kham/ban_thu.py`", (GOC_MA / "kham" / "ban_thu.py").exists())
    bt = _a.parse((GOC_MA / "kham" / "ban_thu.py").read_text(encoding="utf-8"))
    co = {n.name for n in bt.body if isinstance(n, _a.FunctionDef)}
    kiem("bàn thử có đủ sáu hàm chung", CHUNG <= co, sorted(CHUNG - co))

    xau = []
    for f in sorted((GOC_MA / "scripts").glob("thu-*.py")):
        cay = _a.parse(f.read_text(encoding="utf-8"))
        lai = {n.name for n in cay.body
               if isinstance(n, _a.FunctionDef)} & CHUNG
        if lai:
            xau.append(f"{f.name}: {sorted(lai)}")
    kiem("không script `thu-*` nào giữ bản sao riêng", not xau, xau)

    # Ba luật của bàn thử phải nằm TRONG nó, không nằm trong trí nhớ ai.
    doc = (GOC_MA / "kham" / "ban_thu.py").read_text(encoding="utf-8")
    kiem("bàn thử nói rõ ba tập tách theo THỜI GIAN",
         "tách theo THỜI GIAN" in doc)
    kiem("và nói bốn lát τ chia chung MỘT kết quả",
         "MỘT kết quả" in doc)
    kiem("và vì sao chỉ nhận τ đúng mốc phút",
         "nhìn trộm" in doc)

    # `cham` phải NHẬN `ma` chứ không đọc biến toàn cục của script gọi.
    from kham.ban_thu import cap_du_doan, cham
    import inspect as _i
    kiem("`cham` nhận mã thị trường qua tham số",
         "ma" in _i.signature(cham).parameters)
    kiem("`cap_du_doan` cũng vậy",
         "ma" in _i.signature(cap_du_doan).parameters)

def kiem_khong_co_file_lac() -> None:
    """Gốc runtime chỉ được có `run.py`. Bản chép lạc phải tự lộ.

    Trong lúc làm việc, một lệnh `cp a.py b.py <thư-mục>/` chép NHIỀU
    file vào một chỗ, và chỉ cần gõ sai đích một lần là có một bản sao
    lạc nằm im. Đã xảy ra BA lần trong một ngày: `scripts/phat_lai.py`,
    `cap_token.py`, `rui_ro.py` ở gốc runtime.

    Bản sao lạc không vô hại. Nó là mã CŨ mang đúng tên mã mới, và tuỳ
    `sys.path` mà Python có thể nạp nhầm nó — lúc ấy cỗ máy chạy bằng
    một phiên bản không ai biết là đang chạy. Lần đầu bắt được là nhờ
    phép canh cờ dòng lệnh kêu lên, tình cờ.

    Đừng bắt ai phải nhớ. Canh nó.
    """
    print("\n── Không có bản chép lạc trong cây ──────────────────────────")

    GOC_MA = Path(__file__).resolve().parent.parent

    goc = {f.name for f in GOC_MA.glob("*.py")}
    kiem("gốc runtime chỉ có `run.py`", goc == {"run.py"}, sorted(goc))

    # Một module `kham/` mang đúng tên ấy mà nằm ở `scripts/` là bản lạc.
    ten_kham = {f.stem for f in (GOC_MA / "kham").glob("*.py")}
    lac = sorted(f.name for f in (GOC_MA / "scripts").glob("*.py")
                 if f.stem in ten_kham)
    kiem("không module `kham/` nào bị chép lạc sang `scripts/`",
         not lac, lac)

    # Và ngược lại.
    ten_sc = {f.stem for f in (GOC_MA / "scripts").glob("*.py")}
    lac2 = sorted(f.name for f in (GOC_MA / "kham").glob("*.py")
                  if f.stem in ten_sc)
    kiem("không script nào bị chép lạc sang `kham/`", not lac2, lac2)

def kiem_doi_token_khong_phai_dut() -> None:
    """Đăng ký lại token KHÔNG phải đứt kết nối — đừng đếm nó.

    Mỗi khung 5 phút là một cặp asset_id MỚI, nên `dong_song` phải đăng
    ký lại khoảng **288 lần một ngày** trong lúc mọi thứ hoàn toàn bình
    thường. Bản trước `_mot_phien` chỉ `return` khi danh sách đổi, và
    vòng nối lại đếm mọi lần trở về là một lần nối lại — nên buồng lái
    hiện "nối lại 288 lần" sau một ngày yên ả, kèm một giây chờ mỗi lần.

    Chính docstring của `_mot_phien` cảnh báo đúng chuyện này ở ca
    `_ChuaCoToken`: "báo động giả thì người ta tắt cả báo động thật".
    Cùng cái bẫy, khác lối vào.
    """
    print("\n── Đăng ký lại token không phải đứt kết nối ─────────────────")

    import ast as _a

    GOC_MA = Path(__file__).resolve().parent.parent
    src = (GOC_MA / "kham" / "dong_song.py").read_text(encoding="utf-8")
    ma = chr(10).join(x.split("#", 1)[0] for x in src.splitlines())

    kiem("có ngoại lệ riêng cho việc đổi token",
         "class _DoiToken" in ma)
    kiem("danh sách đổi thì NÉM nó, không `return` trơn",
         "raise _DoiToken()" in ma)
    kiem("vòng nối lại bắt riêng ca ấy", "except _DoiToken" in ma)

    # Ca ấy KHÔNG được đi qua `soLanNoiLai += 1`.
    cay = _a.parse(src)
    vong = next(n for n in _a.walk(cay)
                if isinstance(n, _a.FunctionDef) and n.name == "_vong")
    xu = [h for n in _a.walk(vong) if isinstance(n, _a.Try)
          for h in n.handlers
          if isinstance(h.type, _a.Name) and h.type.id == "_DoiToken"]
    kiem("có đúng một nhánh bắt `_DoiToken`", len(xu) == 1, len(xu))
    if xu:
        than = _a.unparse(_a.Module(body=xu[0].body, type_ignores=[]))
        kiem("nhánh ấy KHÔNG đếm nối lại", "soLanNoiLai" not in than, than)
        kiem("và KHÔNG ngủ", "sleep" not in than, than)
        kiem("mà đi tiếp ngay", "continue" in than, than)

    # `_ChuaCoToken` cũng phải giữ nguyên tính chất ấy — nó là ca gốc.
    xu2 = [h for n in _a.walk(vong) if isinstance(n, _a.Try)
           for h in n.handlers
           if isinstance(h.type, _a.Name) and h.type.id == "_ChuaCoToken"]
    # HAI lớp dòng chảy phải cư xử GIỐNG NHAU ở cùng tình huống. Danh
    # sách mã Binance lấy từ config nên gần như không đổi — nhưng để hai
    # lớp khác nhau là một chỗ lệch chờ ngày ai đó thêm một market.
    src2 = (GOC_MA / "kham" / "dong_song_nen.py").read_text(encoding="utf-8")
    ma2 = chr(10).join(x.split("#", 1)[0] for x in src2.splitlines())
    kiem("dòng NỀN cũng tách riêng ca đổi danh sách",
         "class _DoiMa" in ma2 and "raise _DoiMa()" in ma2
         and "except _DoiMa" in ma2)

    kiem("`_ChuaCoToken` vẫn không đếm nối lại",
         xu2 and "soLanNoiLai" not in _a.unparse(
             _a.Module(body=xu2[0].body, type_ignores=[])))

def kiem_cau_dao_chan_that() -> None:
    """Cầu dao ngắt thì KHÔNG một lệnh nào đi qua. Kiểm đầu-cuối.

    Cầu dao là lớp phòng thủ CUỐI CÙNG, và nó chưa hề có phép kiểm chạy
    hết đường ống. `duyet` có đọc `ngatKhanCap` — nhưng "có một dòng `if`"
    và "không lệnh nào lọt" là hai khẳng định khác nhau, và chỉ khẳng định
    thứ hai mới đáng tin.

    Chạy thật trên băng đầy đủ trước khi viết phép kiểm này: ngắt từ đầu
    phiên → 0 khớp, 0 kết toán, $0,00, và 3.694 lần từ chối đều ghi lý do
    "CẦU DAO". Ở đây dựng lại điều đó trên băng giả cho nhanh.
    """
    print("\n── Cầu dao ngắt: không một lệnh nào đi qua ─────────────────")

    import tempfile

    from kham.phat_lai import PhienPhatLai

    khung = _bang_gia(120)
    tam = Path(tempfile.mkdtemp(prefix="ktg-caudao-"))

    # 1. KHÔNG ngắt — phải có lệnh, không thì phép kiểm dưới vô nghĩa.
    a = PhienPhatLai(von=1000.0, thuMucSo=tam / "mo")
    ka = a.chay(khung)
    kiem("phiên đối chứng CÓ khớp lệnh", ka.soKhop > 0, ka.soKhop)

    # 2. Ngắt từ đầu — không được có lệnh nào.
    b = PhienPhatLai(von=1000.0, thuMucSo=tam / "ngat")
    b.risk.ngat("thử: ngắt từ đầu phiên")
    kb = b.chay(khung)
    kiem("ngắt từ đầu ⇒ KHÔNG khớp lệnh nào", kb.soKhop == 0, kb.soKhop)
    kiem("và không kết toán gì", kb.soKetToan == 0, kb.soKetToan)
    kiem("và lãi lỗ đúng bằng 0", kb.tongLaiLo == 0.0, kb.tongLaiLo)
    kiem("mọi lần từ chối đều ghi lý do CẦU DAO",
         all("CẦU DAO" in ly for ly in kb.lyDoTuChoi),
         list(kb.lyDoTuChoi)[:2])

    # 3. Cầu dao KHÔNG tự mở lại — đó là cả điểm của nó.
    kiem("cầu dao vẫn ngắt sau khi chạy hết băng", b.risk.ngatKhanCap)
    b.risk.mo_lai()
    kiem("chỉ người mở mới mở được", not b.risk.ngatKhanCap)

def kiem_lenh_that_khong_thoat_duoc() -> None:
    """Không lệnh thật nào thoát ra được — kiểm HÀNH VI, không chỉ cấu hình.

    `kiem_cua_lenh_that` xác nhận ba cổng đang đóng trong config. Đó là
    một khẳng định về CẤU HÌNH. Câu đáng tin hơn là câu về HÀNH VI: bật
    `che = "that"` lên mà thiếu cổng thì lệnh có thật sự rơi về sổ giấy
    không, hay nó vẫn đi ra sàn?

    Đây là phép kiểm quan trọng nhất trong cả bộ, vì nó canh đúng ranh
    giới giữa tiền giả và tiền thật.
    """
    print("\n── Không lệnh thật nào thoát ra được ───────────────────────")

    from kham.can_loi import CoHoi
    from kham.config import CONFIG, che_hieu_luc
    from kham.dat_lenh import CongLenh
    from kham.kho_doi import Kho
    from kham.so_lenh import Muc, SoLenh

    so = SoLenh(ma="BTC_5M", ben="UP",
                bid=[Muc(0.40, 900)], ask=[Muc(0.42, 900)], nhanLucMs=0.0)
    ch = CoHoi(ma="BTC_5M", ben="UP", chienThuat="thử", fairValue=0.55,
               giaCho=0.42, vwap=0.42, soCo=100.0, grossEdge=0.13,
               phi=0.008, truotGia=0.0008, batDinhMoHinh=0.015,
               bienAnToan=0.008, netEdge=0.09, sucChua=900.0,
               xacSuatKhop=0.95, nuaDoiMs=5000.0, laMaker=False,
               dayDu=True, ghiChu=[])

    cu = dict(CONFIG.get("datLenh") or {})
    cuChe = CONFIG.get("che")
    try:
        # Bật `che = "that"` mà KHÔNG mở hai cổng còn lại.
        CONFIG["che"] = "that"
        CONFIG.setdefault("datLenh", {})["choPhepLenhThat"] = False
        CONFIG["datLenh"]["toiXacNhanDaDocRuiRo"] = False
        kiem("khai `that` mà thiếu cổng ⇒ chế độ hiệu lực vẫn là `giay`",
             che_hieu_luc() == "giay", che_hieu_luc())
        c = CongLenh(Kho())
        l = c.dat(ch, 100.0, so)
        kiem("và lệnh đi đường GIẤY", l.duong == "giay", l.duong)
        kiem("khớp trên sổ giấy chứ không ra sàn", l.soCoKhop > 0, l.soCoKhop)

        # Mở thêm MỘT cổng vẫn chưa đủ.
        CONFIG["datLenh"]["choPhepLenhThat"] = True
        kiem("mở một cổng vẫn chưa đủ", che_hieu_luc() == "giay",
             che_hieu_luc())
        kiem("và vẫn đi đường giấy",
             CongLenh(Kho()).dat(ch, 100.0, so).duong == "giay")

        # Mở hai — cổng thứ ba là KHOÁ VÍ, không nằm trong config.
        CONFIG["datLenh"]["toiXacNhanDaDocRuiRo"] = True
        kiem("mở hai cổng config vẫn chưa đủ — còn khoá ví",
             che_hieu_luc() == "giay", che_hieu_luc())
    finally:
        CONFIG["che"] = cuChe
        CONFIG["datLenh"] = cu

    kiem("dọn xong thì chế độ trở lại như cũ", che_hieu_luc() == "giay")

    # Adapter có HAI lớp, và đó là chỗ hay: nó tự kiểm cổng TRƯỚC, rồi
    # mới tới `NotImplementedError`. Nghĩa là kể cả khi ai đó gọi thẳng
    # adapter, bỏ qua `CongLenh`, thì vẫn có một cửa nữa.
    from kham.sdk_polymarket import AdapterPolymarket

    def nem_gi():
        try:
            AdapterPolymarket().dat_lenh(ma="BTC_5M", ben="UP", soCo=1.0,
                                         gia=0.5, laMaker=False)
        except Exception as e:  # noqa: BLE001
            return type(e).__name__, str(e)
        return None, ""

    ten, loi = nem_gi()
    kiem("gọi THẲNG adapter khi cổng đóng ⇒ vẫn ném",
         ten is not None, ten)
    kiem("và ném ra đúng lý do: cửa chưa mở",
         ten == "RuntimeError" and "chưa mở đủ cửa" in loi, (ten, loi[:60]))
    kiem("kể tên từng cửa đang đóng, không nói chung chung",
         "choPhepLenhThat" in loi and "che" in loi, loi[:90])

    # Mở hết ba cổng trong bộ nhớ — lớp CUỐI vẫn phải chặn.
    import os as _os

    from kham.config import CONFIG as _C
    cu2, cuChe2 = dict(_C.get("datLenh") or {}), _C.get("che")
    cuKhoa = _os.environ.get("POLYMARKET_PRIVATE_KEY")
    try:
        _C["che"] = "that"
        _C.setdefault("datLenh", {})["choPhepLenhThat"] = True
        _C["datLenh"]["toiXacNhanDaDocRuiRo"] = True
        _os.environ["POLYMARKET_PRIVATE_KEY"] = "0x" + "0" * 64
        from kham.config import che_hieu_luc as _chl, ly_do_khong_that as _lkt
        kiem("mở hết ba cổng thì chế độ hiệu lực THÀNH `that`",
             _chl() == "that", _chl())
        kiem("và không còn cửa nào đóng", _lkt() == [], _lkt())

        ten2, l2 = nem_gi()
        # Lớp thứ BA, và nó nằm ngoài cả config lẫn khoá ví: gói
        # `polymarket-client` chưa được cài. Sau nó mới tới
        # `NotImplementedError` trong `dat_lenh`.
        kiem("MỞ HẾT ba cổng thì VẪN không đặt được lệnh",
             ten2 is not None, ten2)
        kiem("lý do là một trong hai lớp cuối: chưa cài gói, hoặc chưa cài mã",
             ten2 == "NotImplementedError"
             or (ten2 == "RuntimeError" and "polymarket-client" in l2),
             (ten2, l2[:70]))
    finally:
        _C["che"] = cuChe2
        _C["datLenh"] = cu2
        if cuKhoa is None:
            _os.environ.pop("POLYMARKET_PRIVATE_KEY", None)
        else:
            _os.environ["POLYMARKET_PRIVATE_KEY"] = cuKhoa

    kiem("dọn xong thì khoá ví KHÔNG còn trong môi trường",
         cuKhoa is not None
         or "POLYMARKET_PRIVATE_KEY" not in _os.environ)

def kiem_tien_hoa_mot_luot_moi_ngay() -> None:
    """Khởi động lại KHÔNG được cấp thêm một lượt tiến hoá.

    `_ngayTienHoa` và `_tienHoaXong` chỉ nằm trong bộ nhớ, nên mỗi lần
    khởi động lại là một lượt tiến hoá MỚI. Đo trên sổ thật:

        29/08:  31 lượt      ← ngày có nhiều lần khởi động lại
        28/08:   6 lượt
        21/08:   7 lượt
        22/08:   1 lượt

    Không chỉ tốn hai phút CPU mỗi lượt. Nặng hơn nhiều: nhịp "mỗi ngày
    MỘT lượt" là quyết định có chủ ý, ghi thẳng trong config — *"cổng
    chặn bắt được tệ hơn nhưng không bắt được khác đi mà rối hơn, nên tốc
    độ tiến hoá phải chậm hơn tốc độ một người kịp nhìn"*.

    Chạy 31 lượt trong một ngày là cho cái cổng ấy 31 lần rút thay vì 1,
    tức thổi tỉ lệ NHẬN NHẦM lên 31 lần. Cùng họ với `nap_tu_so`: sự thật
    nằm trên đĩa mà không ai hỏi.
    """
    print("\n── Mỗi ngày MỘT lượt tiến hoá, kể cả khi khởi động lại ─────")

    import datetime as _dt
    import json as _json

    import kham.vong as V
    from kham.tien_hoa import SO_TIEN_HOA

    hn = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    cu = SO_TIEN_HOA.read_text(encoding="utf-8") if SO_TIEN_HOA.exists() else None
    try:
        # Sổ RỖNG ⇒ chưa chạy, phải cho chạy.
        SO_TIEN_HOA.parent.mkdir(parents=True, exist_ok=True)
        SO_TIEN_HOA.write_text("", encoding="utf-8")
        r = V.Runtime()
        kiem("sổ rỗng ⇒ chưa đánh dấu đã chạy", not r._tienHoaXong)

        # Sổ có dòng của HÔM NAY ⇒ đã chạy, không chạy lại.
        SO_TIEN_HOA.write_text(
            _json.dumps({"luc": hn + "T02:05:00Z", "ghiChu": "thử"}) + chr(10),
            encoding="utf-8")
        r2 = V.Runtime()
        kiem("sổ có dòng HÔM NAY ⇒ đánh dấu đã chạy", r2._tienHoaXong)
        kiem("và nhớ đúng ngày", r2._ngayTienHoa == hn, r2._ngayTienHoa)

        # Sổ chỉ có dòng CŨ ⇒ vẫn phải chạy hôm nay.
        SO_TIEN_HOA.write_text(
            _json.dumps({"luc": "2020-01-01T02:05:00Z"}) + chr(10),
            encoding="utf-8")
        r3 = V.Runtime()
        kiem("sổ chỉ có dòng CŨ ⇒ hôm nay vẫn phải chạy",
             not r3._tienHoaXong)

        # Sổ hỏng ⇒ KHÔNG được chặn lượt, và phải kêu.
        SO_TIEN_HOA.write_text("{khong-phai-json" + chr(10), encoding="utf-8")
        r4 = V.Runtime()
        kiem("sổ hỏng thì vẫn cho chạy, không im lặng khoá",
             not r4._tienHoaXong)
    finally:
        if cu is None:
            SO_TIEN_HOA.unlink(missing_ok=True)
        else:
            SO_TIEN_HOA.write_text(cu, encoding="utf-8")

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
    kiem_cong_chay_may_dang_chay()
    kiem_do_ung_vien()
    kiem_cong_tien_hoa()
    kiem_vong_tien_hoa()
    kiem_bang()
    kiem_nguon_khung()
    kiem_tien_hoa_thu_lai()
    kiem_dong_co()
    kiem_cham_moc()
    kiem_nhom_tai_san()
    kiem_do_tre()
    kiem_bootstrap_theo_khoi()
    kiem_cong_cu_van_dung_bo_uoc_chung()
    kiem_mot_bo_uoc_sigma()
    kiem_sigma_luoi_phut()
    kiem_nho_gia_mo_khung()
    kiem_cong_tien_ngan_mach()
    kiem_tu_nang_cap()
    kiem_ghi_config_tai_cho()
    kiem_chan_mo_hinh_khong_can_lenh()
    kiem_hoc_khong_nhin_trom()
    kiem_duong_quyet_dinh()
    kiem_giai_doan_bang()
    kiem_lo_ngay_rong()
    kiem_dong_ho_rui_ro()
    kiem_treo_tra_han_muc()
    kiem_tran_theo_von()
    kiem_phien_phat_lai()
    kiem_khoa_cau_hinh_co_that()
    kiem_lan_nga_khong_giet_vong()
    kiem_bus_gop_dong_lap()
    kiem_dich_vu_hoi_cong()
    kiem_bao_cao_doc_hien_ra()
    kiem_tien_do_khong_phai_loi()
    kiem_phat_lai_khai_that()
    kiem_co_dong_lenh()
    kiem_doc_bang_quet()
    kiem_so_phien_khong_tich_lai()
    kiem_khong_co_phep_kiem_gia()
    kiem_phi_khong_bien_mat()
    kiem_phien_giay_dung_giai_doan()
    kiem_quyet_chan_la_loi_khuyen()
    kiem_quet_vi_khai_nga()
    kiem_rui_ro_nho_qua_khoi_dong_lai()
    kiem_tran_theo_von_dau_ngay()
    kiem_cham_moc_tu_choi_sigma_ngan()
    kiem_nut_van_khong_bi_dong_bang()
    kiem_hai_so_phai_nhat_quan()
    kiem_don_bang_qua_han()
    kiem_canh_bao_duoi_di_theo_du_lieu()
    kiem_nut_o_mep_phai_lo_ra()
    kiem_so_ket_qua_khai_nguon()
    kiem_doi_chung_cong_bang()
    kiem_tran_phoi_nhiem_gop()
    kiem_chan_lenh_tu_trang_khac()
    kiem_ban_thu_mot_cho()
    kiem_khong_co_file_lac()
    kiem_doi_token_khong_phai_dut()
    kiem_cau_dao_chan_that()
    kiem_lenh_that_khong_thoat_duoc()
    kiem_tien_hoa_mot_luot_moi_ngay()
    kiem_lui_nguon()
    kiem_nan_lai()
    kiem_khung_dai()
    kiem_ket_qua()
    kiem_ghi_ket_qua_vo_dieu_kien()
    kiem_nguon_mau()
    kiem_tien_hoa_chay_that()
    kiem_huong_de_xuat()
    kiem_cong_phan_biet()
    kiem_giam_chan_dong()
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
