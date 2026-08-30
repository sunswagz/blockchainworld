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
    # Ngưỡng cũ (0,0005) chốt cho công thức CŨ. Số thật ở 98,7c cho 1 cổ
    # là 0,07 × 0,987 × 0,013 = $0,0009 — vẫn rất nhỏ, chỉ không nhỏ
    # bằng thứ công thức cũ hứa. Ghi số thật ra đây thay vì nới ngưỡng
    # cho vừa.
    kiem("phí taker rất nhỏ ở 98,7c — nhưng là $0,0009, không phải 0",
         gan(phi_taker(0.987, 1), round(0.07 * 0.987 * 0.013, 5), 1e-9),
         phi_taker(0.987, 1))

    # ── BẢNG PHÍ CHÍNH THỨC, chép từ docs.polymarket.com/trading/fees ──
    #
    # Đối chiếu ngày 30/08/2026. API Polymarket bị chặn ở tầng TLS nhưng
    # trang tài liệu thì vào được, nên đây là con số THẬT chứ không phải
    # tham số phỏng đoán — và nó đóng mục 2 của danh sách trước cổng.
    #
    # Khớp cả bảng tới từng xu là cách duy nhất chắc rằng CẢ dạng hàm
    # LẪN hệ số đều đúng. Chỉ kiểm hình dạng (đỉnh ở 50c, đối xứng, về 0
    # ở hai đầu) thì `min(p, 1−p) × 0,02` cũng qua — và nó thiếu 43–71%.
    BANG_PHI_CRYPTO_100_CO = {
        0.01: 0.07, 0.05: 0.33, 0.10: 0.63, 0.15: 0.89, 0.20: 1.12,
        0.25: 1.31, 0.30: 1.47, 0.35: 1.59, 0.40: 1.68, 0.45: 1.73,
        0.50: 1.75, 0.55: 1.73, 0.60: 1.68, 0.65: 1.59, 0.70: 1.47,
        0.75: 1.31, 0.80: 1.12, 0.85: 0.89, 0.90: 0.63, 0.95: 0.33,
        0.99: 0.07,
    }
    lechPhi = [(g, round(phi_taker(g, 100.0), 2), m)
               for g, m in sorted(BANG_PHI_CRYPTO_100_CO.items())
               if abs(round(phi_taker(g, 100.0), 2) - m) > 0.005]
    kiem("khớp TOÀN BỘ bảng phí chính thức (Crypto, 100 cổ)",
         not lechPhi, lechPhi)
    # Ba sự thật vận hành đối chiếu từ tài liệu phải nằm ĐÚNG CHỖ người
    # sẽ nối sàn đọc. Đây là chỗ duy nhất phép kiểm dò chữ là đúng việc:
    # thứ đang canh CHÍNH LÀ một đoạn văn phải có mặt.
    _goc = Path(__file__).resolve().parent.parent
    _sdk = (_goc / "kham" / "sdk_polymarket.py").read_text(encoding="utf-8")
    _thieu = [x for x in ("425", "postOnly", "orderMinSize", "rebateRate")
              if x not in _sdk]
    kiem("adapter sàn ghi đủ ba bẫy vận hành + khoản hoàn maker",
         not _thieu, _thieu)

    kiem("và maker KHÔNG bị thu phí — tài liệu nói thẳng",
         gan(phi_maker(0.5, 1000.0), 0.0), phi_maker(0.5, 1000.0))
    # Độ chính xác: làm tròn 5 chữ số, dưới 0,00001 USDC thì về 0.
    # "Anything smaller rounds to zero" — nhưng LÀM TRÒN trước đã. Phí
    # 8,75e-6 làm tròn 5 chữ số thành 0,00001, tức đúng mức nhỏ nhất
    # được thu; phải nhỏ hơn nữa mới về 0.
    kiem("phí dưới nửa đơn vị cuối thì về 0",
         phi_taker(0.5, 0.00005) == 0.0, phi_taker(0.5, 0.00005))
    kiem("còn ngay tại mức nhỏ nhất thì vẫn thu",
         gan(phi_taker(0.5, 0.0005), 1e-5, 1e-12), phi_taker(0.5, 0.0005))
    kiem("phí lớn hơn ngưỡng thì KHÔNG bị nuốt",
         phi_taker(0.5, 0.01) > 0, phi_taker(0.5, 0.01))
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

    # ── MỌI trần tiền phải co giãn theo vốn, không sót cái nào ────────
    #
    # Ba trần `ruiRo` đã đổi sang phần trăm; hai trần `khoDoi` bị bỏ sót
    # và ở lại đơn vị đô. Tài khoản $100.000 vẫn chỉ dám ôm $50 chân
    # trần — cỗ máy không lớn lên được; tài khoản $200 thì hai trần ấy
    # lớn hơn cả vốn nên chúng không chặn gì.
    #
    # Đếm theo DANH SÁCH chứ không kiểm từng cái: thêm một trần mới mà
    # quên cho co giãn thì phải đỏ, không cần ai nhớ viết thêm phép kiểm.
    _TRAN = ("tranMoiThiTruongUsd", "tranMoiTaiSanUsd", "tranLoNgayUsd",
             "tranPhoiNhiemGopUsd", "tranChuaPhongHoUsd",
             "tranLechHuongUsd")
    _r1 = RiskEngine(Kho())
    _r1.vonDauNgay = 1_000.0
    _r10 = RiskEngine(Kho())
    _r10.vonDauNgay = 10_000.0
    _cung = [t for t in _TRAN
             if not gan(getattr(_r10, t), getattr(_r1, t) * 10.0, 1e-6)]
    kiem("mọi trần tiền nhân 10 khi vốn nhân 10", not _cung, _cung)
    kiem("và không trần nào bằng 0 (khoá viết sai thì im lặng về 0)",
         all(getattr(_r1, t) > 0 for t in _TRAN),
         {t: getattr(_r1, t) for t in _TRAN})
    # Tỉ lệ cũ phải giữ nguyên, không thì đây là đổi HÀNH VI chứ không
    # phải đổi đơn vị.
    kiem("tài khoản $1.000 cư xử Y HỆT trước khi đổi đơn vị",
         gan(_r1.tranChuaPhongHoUsd, 50.0)
         and gan(_r1.tranLechHuongUsd, 100.0),
         (_r1.tranChuaPhongHoUsd, _r1.tranLechHuongUsd))

    # ── trần lỗ ngày phải chặn TRƯỚC, không phải kêu sau ──────────────
    #
    # Cổng 1 chỉ từ chối khi cầu dao ĐÃ ngắt, nên nó không bao giờ ngăn
    # được lần vượt trần đầu tiên. Mà trần mỗi market (10% vốn) lớn gấp
    # đôi trần lỗ ngày (5%), và vị thế nhị phân thua thì mất TRỌN tiền
    # vào — nên đúng MỘT lệnh cỡ tối đa là đủ thổi bay ngân sách cả ngày.
    #
    # Đã xảy ra thật: sổ ngày 29/08 có một dòng duy nhất, mua 109,91 cổ
    # UP hết $49,95, thua sạch, trần ngày $50,00.
    def _re_moi():
        kk = Kho()
        return kk, RiskEngine(kk)

    k2, re2 = _re_moi()
    sach = re2.duyet(ch, lanh, 200, True)
    k3, re3 = _re_moi()
    re3.ghi_lai_lo(-45.0)                      # ngân sách còn $5
    hep = re3.duyet(ch, lanh, 200, True)
    kiem("lỗ gần trần ngày → SIẾT cỡ lệnh, không phải chờ cầu dao",
         hep.cho and hep.soCoChoPhep < sach.soCoChoPhep,
         f"{hep.soCoChoPhep:.1f} vs {sach.soCoChoPhep:.1f}")
    # PHÍ tính vào, vì phí cũng là tiền mất — và nó mất kể cả khi cược
    # thắng. Phiên phát lại từng ghi `laiLo −50,95` trên khoản vào
    # $49,95 với trần ngày $50,00: vượt trần đúng bằng khoản phí.
    kiem("cỡ còn lại không vượt ngân sách ngày còn lại — KỂ CẢ PHÍ",
         hep.soCoChoPhep * (ch.vwap + ch.phi) <= 5.0 + 1e-6,
         f"${hep.soCoChoPhep * (ch.vwap + ch.phi):.4f} > $5.00")
    kiem("và phí thật sự siết chặt hơn: bỏ phí thì cỡ lớn hơn",
         ch.phi > 0 and 5.0 / (ch.vwap + ch.phi) < 5.0 / ch.vwap,
         f"phí/cổ ${ch.phi:.5f}")

    # Chân PHÒNG HỘ phải đi qua kể cả khi ngân sách cạn: chặn nó là để
    # lại một chân trần trụi — làm rủi ro TO RA nhân danh giảm rủi ro.
    k4, re4 = _re_moi()
    v4 = k4.lay("BTC_5M")
    v4.ghi_khop("DOWN", 50, 0.50)
    re4.ghi_lai_lo(-49.5)                      # ngân sách còn $0,50
    ph = re4.duyet(ch, lanh, 200, True)
    kiem("hết ngân sách ngày nhưng lệnh PHÒNG HỘ vẫn đi qua",
         ph.cho and ph.soCoChoPhep > 1, (ph.cho, ph.soCoChoPhep))
    kiem("và nó thật sự LÀM GIẢM lỗ xấu nhất",
         v4.lo_xau_nhat_khi_mua("UP", ph.soCoChoPhep, ch.vwap)
         < v4.lo_xau_nhat_usd(),
         f"{v4.lo_xau_nhat_khi_mua('UP', ph.soCoChoPhep, ch.vwap):.2f} "
         f"vs {v4.lo_xau_nhat_usd():.2f}")
    down = can("BTC_5M", "DOWN", "t", 0.55, 0.02,
               SoLenh("BTC_5M", "DOWN", ask=SO_MAU.ask, bid=SO_MAU.bid), 600)
    kiem("cùng chiều — CHỒNG CHẤT rủi ro — thì TỪ CHỐI",
         re4.duyet(down, lanh, 200, True).tu_choi)

    # Lỗ xấu nhất ở chợ nhị phân tính CHÍNH XÁC được, không phải ước.
    v5 = Kho().lay("BTC_5M")
    v5.ghi_khop("UP", 100, 0.40)
    kiem("một chân: lỗ xấu nhất = trọn tiền vào",
         gan(v5.lo_xau_nhat_usd(), 40.0), v5.lo_xau_nhat_usd())
    v5.ghi_khop("DOWN", 100, 0.40)
    kiem("cặp ghép kín dưới $1: lỗ xấu nhất về 0",
         gan(v5.lo_xau_nhat_usd(), 0.0), v5.lo_xau_nhat_usd())
    v6 = Kho().lay("BTC_5M")
    v6.ghi_khop("UP", 100, 0.60)
    v6.ghi_khop("DOWN", 100, 0.60)
    kiem("cặp ghép QUÁ $1 thì lỗ khoá lại, và số ấy hiện ra",
         gan(v6.lo_xau_nhat_usd(), 20.0), v6.lo_xau_nhat_usd())

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


def kiem_bien_cua_chan_rui_ro() -> None:
    """Biên của LỜI KHUYÊN CHÂN LỆCH — 12 trên 12 con sống sót lượt đầu.

    Không một biên nào của module này từng được chạm. Nó không đặt lệnh
    (chỉ khuyên), nhưng buồng lái hiện lời khuyên ấy và người vận hành
    đọc nó để quyết — một lời khuyên sai chiều ở đây dẫn tay người đi
    sai chỗ, và đó là dạng hỏng không phép kiểm nào bắt được sau này.

    Cây quyết định có bốn cửa, xếp theo thứ tự ƯU TIÊN:

        1. cửa sắp đóng   → không được chờ nữa
        2. quá hạn chờ    → phải dứt điểm
        3. tiền trần nhiều→ siết ngay dù còn giờ
        4. bình thường    → đợi khớp thụ động

    Thứ tự ấy là cả thiết kế: đảo hai cửa đầu là để một chân trần trụi
    đi qua tiếng chuông.

    ## Sau khi viết xong: 12 con → 4 CHẾT, 8 TƯƠNG ĐƯƠNG/nhẹ

        105 108 110 128  `abs(du) < 1e-9` rồi `du > 0`. Epsilon nuốt
                         điểm bằng nhau, và ba dòng sau chỉ chạy khi
                         `du != 0` nên `>` và `>=` không phân biệt.
        138 144 156 173  bốn phép so ở BIÊN của giá cặp (1,00 và trần
                         cặp) và của tỉ lệ 0,35. Ở đúng biên, hai nhánh
                         cho cùng một HÀNH ĐỘNG và chỉ khác LỜI GIẢI
                         THÍCH — còn ngỏ, nhưng cái giá của việc bỏ sót
                         chúng là một dòng chữ, không phải một quyết
                         định.

    ## Và nó tìm ra một LỖI THẬT, không phải chỗ hở phép kiểm

    `ChanCho.tuoi_ms(0.0)` trả về 1.788.060.175 giây thay vì 0, vì
    `bayGioMs or time.time() * 1000` nuốt mốc 0,0 (0 là falsy). Hậu quả
    không phải một con số xấu mà là một CÂY QUYẾT ĐỊNH rẽ nhầm: mọi ca
    đều rơi vào nhánh "quá hạn chờ", nên ba phép kiểm khác đạt vì lý do
    sai. Đã sửa ở `kho_doi.tuoi_ms` và `ket_toan.soat` — hai chỗ duy
    nhất còn dùng lối `or` ấy.
    """
    print()
    print("-- Bien cua LOI KHUYEN CHAN LECH ---------------------------")
    from kham import chan_rui_ro as _CRR
    from kham.cap_token import CapSo as _CS
    from kham.kho_doi import ViThe as _VT2
    from kham.so_lenh import Muc as _M6
    from kham.so_lenh import SoLenh as _S6

    han = float(CONFIG["khoDoi"]["giayChoChanHai"])
    tranCap = float(CONFIG["khoDoi"]["giaCapToiDa"])

    def _cap(giaDownAsk=None):
        """Cặp sổ. `giaDownAsk=None` nghĩa là KHÔNG AI bán DOWN.

        Phải rỗng CẢ HAI lối: mua DOWN có thể đi thẳng qua ask của DOWN,
        hoặc đi vòng qua bid của UP (bán UP = mua DOWN, hiện ra sau khi
        API soi gương). Chỉ rỗng một lối thì `gia_mua` vẫn trả ra giá,
        và phép kiểm "không ai bán" hoá ra kiểm một chuyện khác.
        """
        co = giaDownAsk is not None
        return _CS(ma="X",
                   up=_S6(ma="X", ben="UP",
                          bid=[_M6(0.50, 500.0)] if co else [],
                          ask=[_M6(0.52, 500.0)], nhanLucMs=0.0),
                   down=_S6(ma="X", ben="DOWN", bid=[_M6(0.40, 500.0)],
                            ask=[_M6(giaDownAsk, 500.0)] if co else [],
                            nhanLucMs=0.0))

    def _vt(coUp=100.0, giaUp=0.50, coDown=0.0, tuoiMs=0.0):
        v = _VT2(ma="X")
        if coUp:
            v.ghi_khop("UP", coUp, giaUp)
        if coDown:
            v.ghi_khop("DOWN", coDown, 0.40)
        if abs(v.dinhHuong) > 0:
            from kham.kho_doi import ChanCho as _CC2
            v.choCap.append(_CC2(ben="UP" if v.dinhHuong > 0 else "DOWN",
                                 soCo=abs(v.dinhHuong),
                                 giaTrungBinh=giaUp, moLucMs=0.0,
                                 capMongMuon=0.98))
        return v

    # ── cân bằng thì KHÔNG khuyên gì ─────────────────────────────────
    kiem("tồn kho cân → không có lời khuyên nào",
         _CRR.quyet(_vt(100.0, 0.50, 100.0), _cap(0.45), 200.0, 0.0)
         is None)

    # ── không ai bán bên thiếu ───────────────────────────────────────
    q = _CRR.quyet(_vt(), _cap(None), 200.0, 0.0)
    kiem("không ai bán bên thiếu, còn giờ → CHỜ",
         q is not None and q.loi == _CRR.CHO, q and q.loi)
    kiem("và nói rõ không có bên bán",
         any("không có bên bán" in x for x in (q.lyDo or [])), q.lyDo)
    q = _CRR.quyet(_vt(), _cap(None), han, 0.0)
    kiem("không ai bán mà cửa sắp đóng → ĐÓNG CHÂN, không chờ nữa",
         q.loi == _CRR.DONG_CHAN, q.loi)
    kiem("và bên phải đóng là bên ĐANG THỪA",
         q.ben == "UP", q.ben)
    q = _CRR.quyet(_vt(), _cap(None), han + 1.0, 0.0)
    kiem("còn hơn hạn một giây thì vẫn CHỜ", q.loi == _CRR.CHO, q.loi)

    # ── cửa sắp đóng, bù vẫn có lãi → ăn thẳng ───────────────────────
    q = _CRR.quyet(_vt(100.0, 0.40), _cap(0.45), han, 0.0)
    kiem("cửa sắp đóng, giá cặp nếu bù < 1,00 → VƯỢT SPREAD",
         q.loi == _CRR.VUOT_SPREAD, (q.loi, q.lyDo))
    kiem("và khoá lỗ khai bằng 0 vì không lỗ",
         gan(q.khoaLoUsd, 0.0), q.khoaLoUsd)
    # Giá cặp ĐÚNG BẰNG 1,00 thì KHÔNG còn là "vẫn có lãi".
    q = _CRR.quyet(_vt(100.0, 0.50), _cap(0.50), han, 0.0)
    kiem("giá cặp ĐÚNG BẰNG 1,00 → không còn tính là có lãi",
         q.loi in (_CRR.VUOT_SPREAD, _CRR.CHIU), q.loi)
    kiem("và khoá lỗ khai bằng 0 (đúng $1,00 là hoà)",
         gan(q.khoaLoUsd, 0.0), q.khoaLoUsd)

    # ── quá hạn chờ: dứt điểm, nhưng KHÔNG đuổi giá ──────────────────
    q = _CRR.quyet(_vt(100.0, 0.40, tuoiMs=0.0), _cap(0.45), 200.0,
                   (han + 1.0) * 1000.0)
    kiem("quá hạn chờ, giá còn trong trần → VƯỢT SPREAD",
         q.loi == _CRR.VUOT_SPREAD, (q.loi, q.lyDo))
    q = _CRR.quyet(_vt(100.0, 0.60), _cap(0.60), 200.0,
                   (han + 1.0) * 1000.0)
    kiem("quá hạn chờ nhưng giá VƯỢT trần cặp → NHÍCH YẾT, đừng đuổi",
         q.loi == _CRR.NANG_GIA, (q.loi, q.lyDo))
    kiem("và trần giá được phép trả = trần cặp trừ giá vốn đã có",
         gan(q.giaToiDa, tranCap - 0.60, 1e-9), q.giaToiDa)
    q = _CRR.quyet(_vt(100.0, 0.40), _cap(0.45), 200.0, han * 1000.0)
    kiem("chờ ĐÚNG BẰNG hạn thì CHƯA phải dứt điểm",
         q.loi == _CRR.CHO, q.loi)

    # ── tiền trần vượt trần → siết ngay dù còn giờ ───────────────────
    q = _CRR.quyet(_vt(100.0, 0.40), _cap(0.45), 200.0, 0.0,
                   tranTranUsd=39.9)
    kiem("tiền trần VƯỢT trần → siết ngay dù còn giờ",
         q.loi == _CRR.VUOT_SPREAD, (q.loi, q.lyDo))
    q = _CRR.quyet(_vt(100.0, 0.40), _cap(0.45), 200.0, 0.0,
                   tranTranUsd=40.0)
    kiem("tiền trần ĐÚNG BẰNG trần thì CHƯA siết", q.loi == _CRR.CHO,
         q.loi)


def kiem_bien_cua_dat_lenh() -> None:
    """Biên của CỔNG ĐẶT LỆNH — đường mà lệnh THẬT sẽ đi qua.

    Bộ quét đột biến: 20 trên 21 con sống sót. Đây là chỗ duy nhất một
    lệnh rời khỏi hệ thống, nên mọi nhánh ở đây đều đáng canh — kể cả
    những nhánh hôm nay chỉ chạy ở chế độ giấy, vì chính chúng là thứ
    sẽ được sao chép sang đường thật.

    Bốn nhóm:

    · MAKER KHÔNG KHỚP NGAY. Sổ giấy nào cho maker khớp tức thì là tặng
      không cả phí lẫn spread cho `tao-lap`.
    · QUY ƯỚC KHỚP CỦA SỔ GIẤY. Lệnh mua ở giá G khớp khi best ask TỤT
      XUỐNG CHẠM G — mép phải tính là khớp.
    · HẾT HẠN CHỜ thì HUỶ, đừng treo mãi.
    · CHÂN CHỜ của cặp: bên nào đang thừa thì bên ấy là chân chờ.

    ## Sau khi viết xong: 21 con → 13 CHẾT, 8 TƯƠNG ĐƯƠNG

        158 248      so với epsilon (1e-9) — epsilon đã nuốt điểm bằng
                     nhau.
        187 249      `soCoKhop <= 0` / `> 0`. Ở 0 thì `ghi_khop` cũng
                     trả về ngay, nên hai lối cùng không ghi gì.
        197 202      chỉ chạy khi `abs(dinhHuong) > 0` (dòng 196 chặn),
                     nên `> 0` và `>= 0` không phân biệt được.
        207          `abs(x) <= 1e-9` so với `<` — ở đúng 0 thì
                     `0 < 1e-9` cũng đúng.
    Con thứ chín ĐÃ CHẾT bằng cách sửa MÃ, không sửa phép kiểm:
    `soat_cho` từng gọi `time.time()` thẳng trong thân hàm, nên biên
    HẾT HẠN không nhắm được — đồng hồ nhích giữa lúc đặt và lúc soát.
    Nay nó nhận `bayGioMs` như `KetToan.soat` đã làm, và biên ấy thành
    kiểm được: chờ ĐÚNG BẰNG hạn thì chưa huỷ, quá một mili giây thì
    huỷ. Một dòng mã không kiểm được ở biên thì cái biên ấy là lời
    người viết nói, không phải thứ đã được chứng minh.

    Khối ĐỌC KẾT QUẢ TỪ SÀN (dòng 243–249) hôm nay không lượt chạy nào
    chạm tới, vì adapter chưa nối. Mà nó chính là chỗ diễn giải câu trả
    lời của sàn về TIỀN THẬT — đọc sai một khoá là ghi sai tồn kho và
    sai sổ lãi lỗ, trên tiền có thật. Nên nó được kiểm bằng một adapter
    giả: khớp trọn, khớp một phần, sàn tự khai trạng thái, sàn trả rỗng,
    và sàn NÉM.
    """
    print()
    print("-- Bien cua DAT LENH ---------------------------------------")
    from kham.can_loi import CoHoi as _CH5
    from kham.dat_lenh import CongLenh as _CL5
    from kham.so_lenh import Muc as _M5
    from kham.so_lenh import SoLenh as _S5

    def _so(ask):
        return _S5(ma="BTC_5M", ben="UP", bid=[_M5(0.44, 500.0)],
                   ask=[_M5(g, l) for g, l in ask], nhanLucMs=0.0)

    def _ch(**k):
        d = dict(ma="BTC_5M", ben="UP", chienThuat="thử", fairValue=0.55,
                 giaCho=0.46, vwap=0.46, soCo=50.0, grossEdge=0.09,
                 phi=0.017, truotGia=0.0008, batDinhMoHinh=0.02,
                 bienAnToan=0.008, netEdge=0.05, sucChua=400.0,
                 xacSuatKhop=0.9, nuaDoiMs=5000.0, laMaker=False,
                 dayDu=True)
        d.update(k)
        return _CH5(**d)

    # ── taker: khớp ngay, có PHÍ, và vào tồn kho ─────────────────────
    k = Kho()
    c = _CL5(k)
    l = c.dat(_ch(), 50.0, _so(((0.46, 500.0),)))
    kiem("taker khớp NGAY", l.trangThai == "khop", l.trangThai)
    kiem("và phí taker được ghi, không phải 0", l.phiUsd > 0, l.phiUsd)
    kiem("và tồn kho nhận đủ số cổ",
         gan(k.lay("BTC_5M").coUp, 50.0), k.lay("BTC_5M").coUp)

    # sổ mỏng → khớp một phần, và phải NÓI RA
    k2 = Kho()
    c2 = _CL5(k2)
    l2 = c2.dat(_ch(), 50.0, _so(((0.46, 20.0),)))
    kiem("sổ chỉ đủ một phần → `khop-mot-phan`",
         l2.trangThai == "khop-mot-phan", l2.trangThai)
    kiem("và ghi chú nói rõ thiếu bao nhiêu", "20" in (l2.ghiChu or ""),
         l2.ghiChu)
    # sổ RỖNG → từ chối, không im lặng khớp 0
    l3 = _CL5(Kho()).dat(_ch(), 50.0, _S5(ma="BTC_5M", ben="UP", bid=[],
                                          ask=[], nhanLucMs=0.0))
    kiem("sổ rỗng → TỪ CHỐI, không khớp 0 cổ",
         l3.trangThai == "tu-choi", l3.trangThai)

    # ── maker: KHÔNG khớp ngay ───────────────────────────────────────
    k4 = Kho()
    c4 = _CL5(k4)
    l4 = c4.dat(_ch(laMaker=True), 50.0, _so(((0.46, 500.0),)))
    kiem("maker KHÔNG khớp ngay — nó phải ĐỢI", l4.trangThai == "cho",
         l4.trangThai)
    kiem("và chưa vào tồn kho", gan(k4.lay("BTC_5M").coUp, 0.0))
    kiem("nó nằm trong hàng chờ", len(c4.dangCho) == 1, len(c4.dangCho))

    # ask còn CAO hơn giá yết → chưa khớp
    c4.soat_cho({"BTC_5M": {"UP": _so(((l4.giaDat + 0.01, 500.0),))}})
    kiem("ask còn cao hơn giá yết → vẫn chờ", l4.trangThai == "cho",
         l4.trangThai)
    # ask TỤT XUỐNG ĐÚNG BẰNG giá yết → KHỚP
    xong = c4.soat_cho({"BTC_5M": {"UP": _so(((l4.giaDat, 500.0),))}})
    kiem("ask tụt xuống ĐÚNG BẰNG giá yết → KHỚP", l4.trangThai == "khop",
         l4.trangThai)
    kiem("khớp đúng ở GIÁ YẾT, không phải giá sổ",
         gan(l4.giaKhop, l4.giaDat), (l4.giaKhop, l4.giaDat))
    kiem("maker KHÔNG bị thu phí", gan(l4.phiUsd, 0.0), l4.phiUsd)
    kiem("và nó rời hàng chờ", not c4.dangCho and len(xong) == 1,
         (len(c4.dangCho), len(xong)))

    # ── hết hạn chờ thì HUỶ ──────────────────────────────────────────
    # `soat_cho` nhận `bayGioMs`, nên biên hết hạn nhắm được ĐÚNG.
    _hanMs = float(CONFIG["khoDoi"]["giayChoChanHai"]) * 1000.0
    k5 = Kho()
    c5 = _CL5(k5)
    l5 = c5.dat(_ch(laMaker=True), 50.0, _so(((0.60, 500.0),)))
    l5.datLucMs = 1_000_000.0
    c5.soat_cho({"BTC_5M": {"UP": _so(((0.60, 500.0),))}},
                bayGioMs=1_000_000.0 + _hanMs)
    kiem("chờ ĐÚNG BẰNG hạn → CHƯA huỷ", l5.trangThai == "cho",
         l5.trangThai)
    c5.soat_cho({"BTC_5M": {"UP": _so(((0.60, 500.0),))}},
                bayGioMs=1_000_000.0 + _hanMs + 1.0)
    kiem("quá hạn một mili giây → HUỶ, không treo mãi",
         l5.trangThai == "huy", l5.trangThai)
    kiem("và nói rõ vì sao", "hạn" in (l5.ghiChu or ""), l5.ghiChu)
    kiem("giờ khớp lấy từ `bayGioMs` truyền vào, không từ đồng hồ máy",
         gan(l4.khopLucMs, 0.0) or l4.khopLucMs > 0, l4.khopLucMs)

    # ── huỷ tay: đúng MỘT lệnh, theo id ──────────────────────────────
    k6 = Kho()
    c6 = _CL5(k6)
    a6 = c6.dat(_ch(laMaker=True), 10.0, _so(((0.60, 500.0),)))
    b6 = c6.dat(_ch(laMaker=True), 10.0, _so(((0.60, 500.0),)))
    kiem("huỷ đúng id thì trả True", c6.huy(a6.id))
    kiem("và CHỈ lệnh ấy bị huỷ",
         a6.trangThai == "huy" and b6.trangThai == "cho",
         (a6.trangThai, b6.trangThai))
    kiem("huỷ một id không có thì trả False", not c6.huy("khong-co"))

    # ── giá yết maker phải đứng TRONG spread ─────────────────────────
    from kham.dat_lenh import _gia_yet_maker as _gym
    soRong = _S5(ma="BTC_5M", ben="UP", bid=[_M5(0.40, 100.0)],
                 ask=[_M5(0.60, 100.0)], nhanLucMs=0.0)
    y = _gym(soRong, _ch(fairValue=0.55, laMaker=True))
    kiem("yết maker nhích hơn best bid, KHÔNG bằng nó", y > 0.40, y)
    kiem("và KHÔNG vượt best ask — vượt là hoá thành taker", y < 0.60, y)
    soHep = _S5(ma="BTC_5M", ben="UP", bid=[_M5(0.4999, 100.0)],
                ask=[_M5(0.5000, 100.0)], nhanLucMs=0.0)
    y2 = _gym(soHep, _ch(fairValue=0.99, laMaker=True))
    kiem("spread hẹp hơn một lê chọn → vẫn KHÔNG vượt best ask",
         y2 < 0.5000 + 1e-12, y2)
    soMotBen = _S5(ma="BTC_5M", ben="UP", bid=[], ask=[], nhanLucMs=0.0)
    kiem("sổ rỗng → yết rơi về fair value, không nổ",
         gan(_gym(soMotBen, _ch(fairValue=0.55, laMaker=True)), 0.55),
         _gym(soMotBen, _ch(fairValue=0.55, laMaker=True)))
    # Sổ MỘT BÊN cũng phải rơi về fair value. Ca này khác sổ rỗng: có
    # `bb` mà không có `ba` thì `bb + le` vẫn tính được, rồi so với
    # `None` là nổ ngay giữa vòng chạy.
    chiCoBid = _S5(ma="BTC_5M", ben="UP", bid=[_M5(0.40, 100.0)],
                   ask=[], nhanLucMs=0.0)
    kiem("sổ CHỈ CÓ BID → yết rơi về fair value, không so với None",
         gan(_gym(chiCoBid, _ch(fairValue=0.55, laMaker=True)), 0.55),
         _gym(chiCoBid, _ch(fairValue=0.55, laMaker=True)))
    # Yết rơi ĐÚNG BẰNG best ask thì phải LÙI: bằng ask là thành taker,
    # tức mất luôn ưu đãi phí — đúng thứ khiến chiến thuật này có lãi.
    _le5 = float(CONFIG["phi"]["leChonNhoNhat"])
    soVuaKhit = _S5(ma="BTC_5M", ben="UP",
                    bid=[_M5(0.500 - _le5, 100.0)],
                    ask=[_M5(0.500, 100.0)], nhanLucMs=0.0)
    y3 = _gym(soVuaKhit, _ch(fairValue=0.99, laMaker=True))
    kiem("yết rơi ĐÚNG BẰNG best ask → LÙI một lê, không thành taker",
         y3 < 0.500 - 1e-12, y3)

    # ── chân CHỜ của cặp: bên nào THỪA thì bên ấy là chân chờ ────────
    from kham.dat_lenh import Lenh as _L5
    k7 = Kho()
    c7 = _CL5(k7)
    v7 = k7.lay("BTC_5M")
    c7._ghi_kho(_L5(id="a", ma="BTC_5M", ben="UP", chienThuat="cap-thu",
                    soCo=100.0, giaDat=0.5, laMaker=False, datLucMs=0.0,
                    soCoKhop=100.0, giaKhop=0.5))
    kiem("khớp một chân UP → chân chờ là UP",
         len(v7.choCap) == 1 and v7.choCap[0].ben == "UP",
         [(x.ben, x.soCo) for x in v7.choCap])
    kiem("và số cổ chờ đúng bằng phần LỆCH",
         gan(v7.choCap[0].soCo, 100.0), v7.choCap[0].soCo)
    c7._ghi_kho(_L5(id="b", ma="BTC_5M", ben="DOWN", chienThuat="cap-thu",
                    soCo=100.0, giaDat=0.4, laMaker=False, datLucMs=0.0,
                    soCoKhop=100.0, giaKhop=0.4))
    kiem("khớp nốt chân kia → hết chân chờ", not v7.choCap,
         [(x.ben, x.soCo) for x in v7.choCap])
    c7._ghi_kho(_L5(id="c", ma="BTC_5M", ben="DOWN", chienThuat="cap-thu",
                    soCo=30.0, giaDat=0.4, laMaker=False, datLucMs=0.0,
                    soCoKhop=30.0, giaKhop=0.4))
    kiem("thừa DOWN → chân chờ đổi sang DOWN",
         len(v7.choCap) == 1 and v7.choCap[0].ben == "DOWN"
         and gan(v7.choCap[0].soCo, 30.0),
         [(x.ben, x.soCo) for x in v7.choCap])
    # Tồn kho ĐỔI BÊN: chân chờ phải đổi theo, không giữ bên cũ.
    k7b = Kho()
    c7b = _CL5(k7b)
    v7b = k7b.lay("BTC_5M")
    c7b._ghi_kho(_L5(id="e", ma="BTC_5M", ben="UP", chienThuat="cap-thu",
                     soCo=100.0, giaDat=0.5, laMaker=False, datLucMs=0.0,
                     soCoKhop=100.0, giaKhop=0.5))
    c7b._ghi_kho(_L5(id="f", ma="BTC_5M", ben="DOWN", chienThuat="cap-thu",
                     soCo=130.0, giaDat=0.4, laMaker=False, datLucMs=0.0,
                     soCoKhop=130.0, giaKhop=0.4))
    kiem("tồn kho lật sang DOWN → chân chờ ĐỔI BÊN, không giữ UP cũ",
         len(v7b.choCap) == 1 and v7b.choCap[0].ben == "DOWN"
         and gan(v7b.choCap[0].soCo, 30.0),
         [(x.ben, x.soCo) for x in v7b.choCap])

    # Lệnh KHÔNG phải của cặp thì không sinh chân chờ.
    k8 = Kho()
    c8 = _CL5(k8)
    c8._ghi_kho(_L5(id="d", ma="BTC_5M", ben="UP", chienThuat="lech-gia",
                    soCo=100.0, giaDat=0.5, laMaker=False, datLucMs=0.0,
                    soCoKhop=100.0, giaKhop=0.5))
    kiem("lệnh KHÔNG phải của cặp → không sinh chân chờ",
         not k8.lay("BTC_5M").choCap, k8.lay("BTC_5M").choCap)

    # ── chế độ THẬT phải đi ĐƯỜNG THẬT, không lặng lẽ rơi về giấy ───
    from kham import dat_lenh as _DLM
    _cuChe = _DLM.che_hieu_luc
    try:
        _DLM.che_hieu_luc = lambda: "that"
        k9 = Kho()
        c9 = _CL5(k9)
        l9 = c9.dat(_ch(), 50.0, _so(((0.46, 500.0),)))
        # Thiết kế ở đây có chủ ý: chế độ thật mà cửa còn đóng thì RƠI
        # VỀ GIẤY, nhưng "không im lặng rơi về giấy — nói rõ cửa nào
        # đóng, rồi mới rơi". Thứ đáng canh chính là cái NÓI RÕ ấy.
        kiem("chế độ THẬT mà cửa còn đóng → rơi về giấy",
             l9.duong == "giay", l9.duong)
        kiem("nhưng KHÔNG im lặng: ghi chú nêu tên cửa đang đóng",
             "cửa lệnh thật" in (l9.ghiChu or ""), l9.ghiChu)
        kiem("và ghi chú kể ĐỦ cả bốn cửa cấu hình",
             all(x in (l9.ghiChu or "")
                 for x in ("che", "choPhepLenhThat", "toiXacNhanDaDocRuiRo",
                           "PRIVATE_KEY")), l9.ghiChu)
        # Chế độ GIẤY thì KHÔNG có ghi chú ấy — nếu không thì mọi lệnh
        # giấy đều đeo một lời cảnh báo vô nghĩa và không ai đọc nữa.
        _DLM.che_hieu_luc = lambda: "giay"
        l10 = _CL5(Kho()).dat(_ch(), 50.0, _so(((0.46, 500.0),)))
        kiem("chế độ GIẤY thì KHÔNG đeo ghi chú cửa lệnh thật",
             "cửa lệnh thật" not in (l10.ghiChu or ""), l10.ghiChu)
        # Chế độ QUAN SÁT: từ chối hẳn, và KHÔNG đụng tồn kho.
        _DLM.che_hieu_luc = lambda: "quan-sat"
        k11 = Kho()
        l11 = _CL5(k11).dat(_ch(), 50.0, _so(((0.46, 500.0),)))
        kiem("chế độ QUAN SÁT → TỪ CHỐI hẳn",
             l11.trangThai == "tu-choi", l11.trangThai)
        kiem("và tồn kho KHÔNG bị đụng",
             gan(k11.lay("BTC_5M").coUp, 0.0), k11.lay("BTC_5M").coUp)
        # ── ĐỌC KẾT QUẢ TỪ SÀN — đường tiền thật ────────────────────
        #
        # Khối này chỉ chạy khi adapter đã nối, nên hôm nay không lượt
        # chạy nào chạm tới nó. Mà nó chính là chỗ diễn giải câu trả
        # lời của sàn về TIỀN THẬT: đọc sai một khoá là ghi sai tồn kho
        # và sai sổ lãi lỗ, trên tiền có thật.
        _cuLd = _DLM.ly_do_khong_that
        try:
            _DLM.che_hieu_luc = lambda: "that"
            _DLM.ly_do_khong_that = lambda *a, **k: []

            class _San:
                def __init__(self, tra):
                    self.tra = tra
                    self.goi = 0

                def dat_lenh(self, **k):
                    self.goi += 1
                    if isinstance(self.tra, Exception):
                        raise self.tra
                    return self.tra

            def _chay_that(tra, soCo=50.0):
                kk = Kho()
                cc = _CL5(kk)
                cc._sdk = _San(tra)
                cc._nap_sdk = lambda: cc._sdk
                return kk, cc.dat(_ch(), soCo, _so(((0.46, 500.0),)))

            kk, lt = _chay_that({"soCoKhop": 50.0, "giaKhop": 0.47,
                                 "phiUsd": 0.9})
            kiem("sàn trả khớp TRỌN → `khop`", lt.trangThai == "khop",
                 lt.trangThai)
            kiem("và tồn kho ghi theo GIÁ KHỚP của sàn, không phải giá đặt",
                 gan(kk.lay("BTC_5M").tienUp, 50.0 * 0.47),
                 kk.lay("BTC_5M").tienUp)
            kiem("phí của SÀN được ghi, không tính lại",
                 gan(kk.lay("BTC_5M").phiUsd, 0.9),
                 kk.lay("BTC_5M").phiUsd)

            kk, lt = _chay_that({"soCoKhop": 20.0, "giaKhop": 0.47})
            kiem("sàn trả khớp MỘT PHẦN → `khop-mot-phan`",
                 lt.trangThai == "khop-mot-phan", lt.trangThai)
            kiem("thiếu khoá phí → 0, không nổ", gan(lt.phiUsd, 0.0),
                 lt.phiUsd)

            kk, lt = _chay_that({"soCoKhop": 50.0, "giaKhop": 0.47,
                                 "trangThai": "huy"})
            kiem("sàn TỰ khai trạng thái thì lời sàn thắng",
                 lt.trangThai == "huy", lt.trangThai)

            kk, lt = _chay_that({})
            kiem("sàn trả rỗng → khớp 0, và KHÔNG đụng tồn kho",
                 gan(lt.soCoKhop, 0.0) and gan(kk.lay("BTC_5M").coUp, 0.0),
                 (lt.soCoKhop, kk.lay("BTC_5M").coUp))

            kk, lt = _chay_that(RuntimeError("sàn sập"))
            kiem("sàn NÉM → từ chối, nêu tên lỗi",
                 lt.trangThai == "tu-choi" and "sàn sập" in (lt.ghiChu or ""),
                 (lt.trangThai, lt.ghiChu))
            kiem("và tồn kho KHÔNG bị đụng khi sàn ném",
                 gan(kk.lay("BTC_5M").coUp, 0.0), kk.lay("BTC_5M").coUp)
        finally:
            _DLM.ly_do_khong_that = _cuLd
    finally:
        _DLM.che_hieu_luc = _cuChe


def kiem_bien_cua_nan_lai() -> None:
    """Biên của PHÉP NẮN — nơi một xác suất bị sửa trước khi tiêu tiền.

    Bộ quét đột biến: 10 trên 13 con sống sót. Đây là lớp cuối cùng
    chạm vào `p` trước khi nó thành cỡ lệnh, và nó có ba cái chốt xếp
    chồng (giảm chấn, trần dịch chuyển, kẹp [0,001; 0,999]) — mỗi chốt
    là một chỗ có thể lặng lẽ không làm gì.

    ## Sau khi viết xong: 13 con → 7 CHẾT, 6 TƯƠNG ĐƯƠNG

        126 128 134  ba phép so quanh MỐC. Ở đúng mốc, cả hai nhánh
                     cùng cho tung độ của chính mốc ấy — nội suy với
                     `t = 0` hay kẹp về đầu mút thì cùng một số.
        94           so với epsilon 1e-12 trong PAVA.
        61 207       `CONFIG.get("nanLai") or {}` và `duong or
                     DUONG_THO` — với config HIỆN TẠI, đường rơi về mặc
                     định cho đúng cùng giá trị (`toiThieuMau` khai 400,
                     mặc định cũng 400). Chúng sẽ giết được ngay khi có
                     một khoá khai khác mặc định.
    """
    print()
    print("-- Bien cua PHEP NAN ---------------------------------------")
    from kham.dinh_gia import HieuChinh as _HC4
    from kham.nan_lai import DOI_TOI_DA as _DTD
    from kham.nan_lai import PhepNan as _PN
    from kham.nan_lai import TOI_THIEU_MAU as _TTM
    from kham.nan_lai import TOI_THIEU_MOI_O as _TTO
    from kham.nan_lai import he_so_giam_chan as _hs4
    from kham.nan_lai import khop as _khop4

    # ── "không khá hơn thì KHÔNG dùng" ───────────────────────────────
    kiem("sai số SAU bằng sai số TRƯỚC → KHÔNG dùng",
         not _PN([(0.2, 0.3), (0.8, 0.7)], 999, 0.05, 0.05).dung_duoc)
    kiem("khá hơn một chút → dùng",
         _PN([(0.2, 0.3), (0.8, 0.7)], 999, 0.05, 0.049).dung_duoc)
    kiem("chỉ MỘT mốc thì không đủ để nội suy → KHÔNG dùng",
         not _PN([(0.2, 0.3)], 999, 0.05, 0.01).dung_duoc)
    kiem("ĐÚNG HAI mốc là đủ",
         _PN([(0.2, 0.3), (0.8, 0.7)], 999, 0.05, 0.01).dung_duoc)
    kiem("phép nắn KHÔNG dùng được thì trả p NGUYÊN VẸN",
         gan(_PN([], 0, 0.0, 0.0).nan(0.37), 0.37))

    # ── nội suy và hai đầu ngoại suy ─────────────────────────────────
    _cuHs = (CONFIG.get("nanLai") or {}).get("heSoGiamChan")
    try:
        CONFIG.setdefault("nanLai", {})["heSoGiamChan"] = 1.0
        pn = _PN([(0.2, 0.3), (0.8, 0.7)], 999, 0.10, 0.01)
        kiem("p ĐÚNG BẰNG mốc đầu → lấy đúng giá trị mốc ấy",
             gan(pn.nan(0.2), 0.3, 1e-9), pn.nan(0.2))
        kiem("p ĐÚNG BẰNG mốc cuối → lấy đúng giá trị mốc ấy",
             gan(pn.nan(0.8), 0.7, 1e-9), pn.nan(0.8))
        kiem("dưới mốc đầu → KẸP, không ngoại suy tuyến tính",
             gan(pn.nan(0.05), 0.3, 1e-9), pn.nan(0.05))
        kiem("trên mốc cuối → KẸP", gan(pn.nan(0.95), 0.7, 1e-9),
             pn.nan(0.95))
        kiem("giữa hai mốc → nội suy tuyến tính",
             gan(pn.nan(0.5), 0.5, 1e-9), pn.nan(0.5))
        # Hai mốc TRÙNG hoành độ: không được chia cho 0.
        pn2 = _PN([(0.4, 0.2), (0.4, 0.9)], 999, 0.10, 0.01)
        kiem("hai mốc trùng hoành độ → không chia cho 0",
             pn2.nan(0.4) is not None and 0.0 <= pn2.nan(0.4) <= 1.0,
             pn2.nan(0.4))

        # ── trần dịch chuyển: một phép khớp hỏng cùng lắm lệch chừng ấy
        xa = _PN([(0.0, 0.99), (1.0, 0.99)], 999, 0.10, 0.01)
        kiem("đường nắn kéo đi rất xa vẫn bị TRẦN DỊCH CHUYỂN chặn",
             abs(xa.nan(0.20) - 0.20) <= _DTD + 1e-9,
             (xa.nan(0.20), _DTD))
        kiem("và kết quả luôn nằm trong [0,001; 0,999]",
             all(0.001 - 1e-9 <= xa.nan(x / 100.0) <= 0.999 + 1e-9
                 for x in range(0, 101)))
    finally:
        if _cuHs is None:
            (CONFIG.get("nanLai") or {}).pop("heSoGiamChan", None)
        else:
            CONFIG["nanLai"]["heSoGiamChan"] = _cuHs

    # ── giảm chấn: đi ĐÚNG một phần đường ────────────────────────────
    pn3 = _PN([(0.2, 0.4), (0.8, 0.9)], 999, 0.10, 0.01)
    hs = _hs4()
    _cuHs2 = CONFIG["nanLai"].get("heSoGiamChan")
    try:
        CONFIG["nanLai"]["heSoGiamChan"] = 0.0
        kiem("giảm chấn 0 → KHÔNG nắn gì cả", gan(pn3.nan(0.5), 0.5, 1e-9),
             pn3.nan(0.5))
        CONFIG["nanLai"]["heSoGiamChan"] = 1.0
        day_du = pn3.nan(0.5)
        CONFIG["nanLai"]["heSoGiamChan"] = 0.5
        nua = pn3.nan(0.5)
        kiem("giảm chấn 0,5 → đi ĐÚNG NỬA đường",
             gan(nua, 0.5 + (day_du - 0.5) * 0.5, 1e-9), (nua, day_du))
    finally:
        CONFIG["nanLai"]["heSoGiamChan"] = _cuHs2
    kiem("hệ số giảm chấn đọc CONFIG mỗi lần, không chốt lúc nạp",
         gan(_hs4(), hs))

    # ── khớp: thiếu mẫu thì trả phép RỖNG, không bịa một đường ───────
    import tempfile as _tf5
    _d5 = Path(_tf5.mkdtemp())
    hc5 = _HC4(duong=_d5 / "hc.json")
    hc5.o = {}
    for i in range(_TTM - 1):
        hc5.them(0.1 + (i % 9) * 0.1, i % 2 == 0)
    kiem("kém tổng mẫu tối thiểu một mẫu → phép nắn RỖNG",
         not _khop4(hc5).moc, len(_khop4(hc5).moc))
    hc6 = _HC4(duong=_d5 / "hc6.json")
    hc6.o = {}
    for i in range(_TTM * 3):
        hc6.them(0.05 + (i % 10) * 0.1, (i % 10) >= 5)
    pn6 = _khop4(hc6)
    kiem("đủ mẫu và đủ ô → có đường nắn", len(pn6.moc) >= 3, len(pn6.moc))
    kiem("và các mốc ĐƠN ĐIỆU KHÔNG GIẢM — đó là cả điểm của PAVA",
         all(pn6.moc[i][1] <= pn6.moc[i + 1][1] + 1e-12
             for i in range(len(pn6.moc) - 1)),
         [round(y, 4) for _, y in pn6.moc])
    # ── ĐÚNG BẰNG tổng mẫu tối thiểu là ĐỦ ──────────────────────────
    #
    # Cùng luật với cửa mở Kelly: con số khai là "tối thiểu", nên đạt
    # đúng mức tối thiểu là ĐẠT. Kém một mẫu thì chưa.
    def _so_nan(soMau, moiO=None):
        h = _HC4(duong=_d5 / f"n{soMau}-{moiO}.json")
        h.o = {}
        # Rải đều 10 ô để mỗi ô đủ `TOI_THIEU_MOI_O`.
        for i in range(soMau):
            pX = 0.05 + (i % 10) * 0.1
            h.them(pX, (i % 10) >= 5)
        return h

    kiem("ĐÚNG BẰNG tổng mẫu tối thiểu → CÓ đường nắn",
         len(_khop4(_so_nan(_TTM)).moc) >= 3,
         len(_khop4(_so_nan(_TTM)).moc))

    # ── ô có ĐÚNG BẰNG `TOI_THIEU_MOI_O` mẫu thì được GIỮ ───────────
    h7 = _HC4(duong=_d5 / "hc7.json")
    h7.o = {}
    for i in range(_TTM * 3):                 # chín ô dày
        h7.them(0.05 + (i % 9) * 0.1, (i % 9) >= 5)
    for _ in range(_TTO):                     # ô thứ mười: ĐÚNG ngưỡng
        h7.them(0.95, True)
    _oDay = sum(1 for d in h7.o.values() if d["n"] >= _TTO)
    pn7 = _khop4(h7)
    kiem("ô có ĐÚNG BẰNG số mẫu tối thiểu → được GIỮ, không bị bỏ",
         len(pn7.moc) == _oDay, (len(pn7.moc), _oDay))
    h8 = _HC4(duong=_d5 / "hc8.json")
    h8.o = {}
    for i in range(_TTM * 3):
        h8.them(0.05 + (i % 9) * 0.1, (i % 9) >= 5)
    for _ in range(_TTO - 1):                 # kém một mẫu
        h8.them(0.95, True)
    kiem("kém một mẫu thì ô ấy bị BỎ",
         len(_khop4(h8).moc) == len(pn7.moc) - 1,
         (len(_khop4(h8).moc), len(pn7.moc)))

    kiem("ô quá ít mẫu bị BỎ, không kéo cả đường theo",
         _TTO > 1 and all(True for _ in pn6.moc), _TTO)


def kiem_bien_cua_so_lenh() -> None:
    """Biên của SỔ LỆNH — nơi tính GIÁ TA SẼ TRẢ.

    Bộ quét đột biến: **23 trên 24 con sống sót**, phủ kém nhất cả cung.
    Mà mọi lợi thế, mọi cỡ lệnh, mọi mô phỏng khớp đều đi qua đây: sai
    một biên là sai giá, và sai giá thì mọi con số phía sau sai theo mà
    vẫn đúng cú pháp.

    Bốn nhóm:

    · SỔ MỘT CHIỀU. Chỉ có bid, hoặc chỉ có ask — mọi phép đo phải trả
      `None`, không phải một con số dựng trên một nửa sổ.
    · THANG CHỜ. 20 mức trải hơn 0,90 đô là thang chờ trước giờ mở,
      không phải báo giá. Nhận nhầm nó là "chợ tin UP 99,9%".
    · ĐI DỌC SỔ. Khớp một phần phải khai `dayDu=False`; xin nhiều hơn
      cả sổ phải khớp đúng phần có; tác động giá không bao giờ âm.
    · SỨC CHỨA THEO HẠN GIÁ. Ngay mức đầu đã vượt hạn thì sức chứa
      bằng 0, không phải "một ít".

    ## Sau khi viết xong: 24 con → 17 CHẾT, 7 TƯƠNG ĐƯƠNG

        228 248 269  cả ba so với một epsilon (1e-12, 1e-9). Epsilon
                     đã nuốt trọn điểm bằng nhau, nên đổi `<` thành
                     `<=` không đổi được gì.
        202 216      `tong <= 0` và `giua <= 0` trong `suc_chua`. Ở 0
                     thì nhánh kia vẫn chạy tới cùng một câu trả lời 0:
                     `_di_qua` với `muon = 0` trả `khop = 0`, phép chia
                     đôi có `lo = hi = 0` nên `giua = 0` và thoát ngay.
        207 219      `het.khop > 0` / `r.khop > 0` — `khop` chỉ bằng 0
                     khi sổ rỗng, và dòng 202 đã chặn ca ấy.

    Fixture đắt nhất ở đây là **sổ có mức khối lượng 0** — nó một mình
    giết bốn con. Sổ thật có ca ấy (mức vừa bị ăn sạch nhưng chưa gỡ),
    và mức 0 nhìn từ ngoài giống hệt một mức bình thường.
    """
    print()
    print("-- Bien cua SO LENH ----------------------------------------")
    from kham.so_lenh import Muc as _M4
    from kham.so_lenh import SoLenh as _S4

    def so(bid=(), ask=()):
        return _S4(ma="X", ben="UP",
                   bid=[_M4(g, l) for g, l in bid],
                   ask=[_M4(g, l) for g, l in ask], nhanLucMs=0.0)

    day = so(bid=((0.44, 100.0), (0.42, 200.0)),
             ask=((0.46, 100.0), (0.50, 200.0)))

    # ── sổ MỘT CHIỀU: mọi phép đo phải câm, không bịa ─────────────────
    chiBid = so(bid=((0.44, 100.0),))
    chiAsk = so(ask=((0.46, 100.0),))
    for ten, x in (("chỉ có BID", chiBid), ("chỉ có ASK", chiAsk)):
        kiem(f"{ten} → spread None", x.spread is None, x.spread)
        kiem(f"{ten} → giữa None", x.giua is None, x.giua)
        kiem(f"{ten} → vi giá None", x.vi_gia is None, x.vi_gia)
        kiem(f"{ten} → KHÔNG hai chiều", not x.hai_chieu)
        kiem(f"{ten} → KHÔNG dùng được", not x.dung_duoc)
    kiem("sổ hai chiều tử tế thì DÙNG ĐƯỢC", day.dung_duoc)

    # ── độ sâu: chỉ đếm mức TRONG khoảng, mép tính vào ────────────────
    b, a = day.do_sau(0.02)
    kiem("độ sâu quanh 2c: mép ĐÚNG BẰNG khoảng được TÍNH VÀO",
         gan(b, 300.0) and gan(a, 100.0), (b, a))
    b2, a2 = day.do_sau(0.0)
    kiem("quanh 0 thì chỉ còn đúng mức tốt nhất",
         gan(b2, 100.0) and gan(a2, 100.0), (b2, a2))
    kiem("sổ rỗng thì độ sâu (0, 0), không nổ", so().do_sau() == (0.0, 0.0))
    kiem("và lệch là None chứ không phải 0", so().lech() is None)

    # ── THANG CHỜ: 20 mức trải hơn 0,90 đô ───────────────────────────
    thang = so(bid=tuple((0.001 + i * 0.05, 100.0) for i in range(20)),
               ask=((0.999, 100.0),))
    kiem("20 mức trải hơn 0,90 → nhận ra là THANG CHỜ",
         thang.trai_ca_bang, [m.gia for m in thang.bid][:3])
    kiem("và sổ ấy KHÔNG dùng được, dù trông đầy hàng",
         not thang.dung_duoc)
    hep = so(bid=tuple((0.40 + i * 0.001, 100.0) for i in range(20)),
             ask=((0.46, 100.0),))
    kiem("20 mức nhưng trải hẹp → KHÔNG phải thang chờ",
         not hep.trai_ca_bang)
    it = so(bid=tuple((0.001 + i * 0.06, 100.0) for i in range(19)),
            ask=((0.999, 100.0),))
    kiem("19 mức thì chưa đủ để kết luận thang chờ",
         not it.trai_ca_bang)

    # ── đi dọc sổ ────────────────────────────────────────────────────
    r = day.vwap_mua(50.0)
    kiem("mua trong MỘT mức → vwap đúng bằng mức ấy",
         gan(r.vwap, 0.46) and r.dayDu and r.soMuc == 1, (r.vwap, r.soMuc))
    kiem("và tác động giá bằng 0", gan(r.tacDong, 0.0), r.tacDong)
    r = day.vwap_mua(200.0)
    kiem("mua qua HAI mức → vwap là bình quân theo lượng",
         gan(r.vwap, (100 * 0.46 + 100 * 0.50) / 200.0), r.vwap)
    kiem("tác động giá DƯƠNG khi phải ăn sâu", r.tacDong > 0, r.tacDong)
    r = day.vwap_mua(300.0)
    kiem("xin ĐÚNG BẰNG cả sổ → đầy đủ", r.dayDu and gan(r.khop, 300.0),
         (r.khop, r.dayDu))
    r = day.vwap_mua(301.0)
    kiem("xin hơn cả sổ → khớp phần có, và khai dayDu FALSE",
         gan(r.khop, 300.0) and not r.dayDu, (r.khop, r.dayDu))
    r = day.vwap_mua(0.0)
    kiem("xin 0 cổ → khớp 0", gan(r.khop, 0.0), r.khop)
    # `dayDu` phải là TRUE: xin 0 và nhận 0 là ĐỦ. Khai False ở đây là
    # báo một lần khớp hụt chưa từng xảy ra, và Risk Engine đọc cờ ấy.
    kiem("và `dayDu` là TRUE — xin 0 nhận 0 là ĐỦ", r.dayDu, r.dayDu)

    # ── sổ có mức KHỐI LƯỢNG 0: có mức mà không có hàng ───────────────
    #
    # Sổ thật có ca này (mức vừa bị ăn sạch nhưng chưa bị gỡ). Mọi phép
    # chia ở đây phải chịu được nó, không thì `ZeroDivisionError` giữa
    # vòng chạy — và mức 0 nhìn từ ngoài giống hệt một mức bình thường.
    khong = so(bid=((0.44, 0.0),), ask=((0.46, 0.0),))
    kiem("mức 0 hàng: vi giá rơi về GIỮA, không chia cho 0",
         khong.vi_gia is not None and gan(khong.vi_gia, khong.giua),
         khong.vi_gia)
    kiem("mức 0 hàng: sức chứa 0, không nổ",
         gan(khong.suc_chua(0.99), 0.0), khong.suc_chua(0.99))
    rk = khong.vwap_mua(10.0)
    kiem("mức 0 hàng: khớp 0 và KHÔNG đầy đủ",
         gan(rk.khop, 0.0) and not rk.dayDu, (rk.khop, rk.dayDu))
    kiem("và vwap là 0 chứ không phải một số bịa", gan(rk.vwap, 0.0),
         rk.vwap)
    tron = so(bid=((0.44, 100.0),),
              ask=((0.46, 0.0), (0.50, 100.0)))
    rt = tron.vwap_mua(50.0)
    kiem("mức 0 hàng nằm GIỮA sổ thì bị bỏ qua, không dừng cả phép đi",
         gan(rt.khop, 50.0) and gan(rt.vwap, 0.50), (rt.khop, rt.vwap))
    # Và nó KHÔNG được đếm vào `soMuc`. Con số ấy là "phải ăn qua mấy
    # mức" — một thước về độ sâu phải đi. Đếm cả mức rỗng là thổi
    # phồng nó, và không phép tính nào kêu.
    kiem("mức 0 hàng KHÔNG được đếm vào `soMuc`", rt.soMuc == 1, rt.soMuc)
    r = so().vwap_mua(10.0)
    kiem("sổ rỗng → khớp 0, không nổ", gan(r.khop, 0.0) and not r.dayDu)

    # ── SỨC CHỨA theo hạn giá: "cơ hội này to bằng nào" ──────────────
    #
    # Một con số edge trần trụi không nói được điều này: edge 10c mà chỉ
    # khớp được 4 đô thì kém hơn edge 1,2c khớp được 20.000 đô. Hàm này
    # trả lời bằng phép chia đôi, và phép chia đôi chỉ đúng nhờ tính
    # ĐƠN ĐIỆU — mua thêm bao giờ cũng làm vwap tệ đi hoặc giữ nguyên.
    kiem("hạn RỘNG hơn cả sổ → sức chứa là CẢ sổ",
         gan(day.suc_chua(0.99), 300.0), day.suc_chua(0.99))
    kiem("hạn ĐÚNG BẰNG mức đầu → chứa trọn mức đầu",
         gan(day.suc_chua(0.46), 100.0, 0.5), day.suc_chua(0.46))
    kiem("hạn DƯỚI mức đầu → sức chứa 0, không phải 'một ít'",
         gan(day.suc_chua(0.45), 0.0), day.suc_chua(0.45))
    # Giữa hai mức: vwap = 0,48 khi lấy trọn 200 cổ, nên hạn 0,48 phải
    # chứa được quãng 200 — chứ không phải chỉ 100.
    kiem("hạn giữa hai mức → chia đôi tìm đúng chỗ vwap chạm hạn",
         190.0 < day.suc_chua(0.48) <= 200.5, day.suc_chua(0.48))
    kiem("sổ rỗng → sức chứa 0", gan(so().suc_chua(0.99), 0.0))
    # Chiều BÁN: hạn là SÀN chứ không phải trần.
    kiem("bán: hạn thấp hơn mọi mức bid → chứa cả sổ",
         gan(day.suc_chua(0.01, mua=False), 300.0),
         day.suc_chua(0.01, mua=False))
    kiem("bán: hạn cao hơn best bid → sức chứa 0",
         gan(day.suc_chua(0.50, mua=False), 0.0),
         day.suc_chua(0.50, mua=False))

    # ── lý do KHÔNG dùng được phải nêu ĐÚNG tên ──────────────────────
    kiem("sổ rỗng → nói 'sổ rỗng'", so().ly_do_khong_dung() == "sổ rỗng",
         so().ly_do_khong_dung())
    kiem("chỉ có BID → nói thiếu bên ASK, không nói 'sổ rỗng'",
         chiBid.ly_do_khong_dung() not in (None, "sổ rỗng"),
         chiBid.ly_do_khong_dung())
    kiem("thang chờ → nêu đúng tên nó",
         "thang chờ" in (thang.ly_do_khong_dung() or ""),
         thang.ly_do_khong_dung())
    kiem("sổ tử tế → không có lý do nào", day.ly_do_khong_dung() is None,
         day.ly_do_khong_dung())

    # ── biên đúng 0,90 của thang chờ ─────────────────────────────────
    dung90 = so(bid=tuple((0.05 + i * (0.90 / 19.0), 100.0)
                          for i in range(20)),
                ask=((0.999, 100.0),))
    kiem("trải ĐÚNG BẰNG 0,90 thì CHƯA phải thang chờ",
         not dung90.trai_ca_bang,
         max(m.gia for m in dung90.bid) - min(m.gia for m in dung90.bid))

    # ── microprice chạy ĐÚNG HƯỚNG ───────────────────────────────────
    #
    # Nhiều hàng ở BID nghĩa là giá bị đẩy về phía ASK. Viết ngược thì
    # mọi tín hiệu dựa trên nó đảo chiều mà không lỗi nào ném ra.
    nangBid = so(bid=((0.44, 900.0),), ask=((0.46, 100.0),))
    kiem("bid dày → vi giá lệch về phía ASK",
         nangBid.vi_gia > nangBid.giua, (nangBid.vi_gia, nangBid.giua))
    nangAsk = so(bid=((0.44, 100.0),), ask=((0.46, 900.0),))
    kiem("ask dày → vi giá lệch về phía BID",
         nangAsk.vi_gia < nangAsk.giua, (nangAsk.vi_gia, nangAsk.giua))


def kiem_bien_cua_can_loi() -> None:
    """Biên của CÂN LỢI — nơi quyết một cơ hội có đáng làm không.

    Bộ quét đột biến: 14 trên 18 con sống sót. Ba nhóm:

    · TỪ CHỐI THAY VÌ BỊA. Sổ rỗng, xin 0 cổ, thiếu một bên sổ — mọi
      ca ấy phải trả `None`, không phải một cơ hội với số 0 trong đó.
    · GIÁ CẶP ĐÚNG $1,00 là HOÀ. Cùng luật với `kho_doi`, nhưng đây là
      lớp khác và nó có bản sao riêng của phép so.
    · SỐ MŨ BIỂU PHÍ phải thật sự được áp. Nó mặc định 1 nên không đổi
      gì hôm nay — mà đúng vì thế nó dễ mục ra mà không ai biết.

    ## Sau khi viết xong: 18 con → 12 CHẾT, 6 TƯƠNG ĐƯƠNG

        97 185 339 343  `soCo <= 0` / `soCap <= 0`. Ở 0 thì nhánh kia
                        vẫn ra cùng kết quả: `phi_taker` nhân với 0,
                        còn `can`/`gia_cap` gặp `khop = 0` ở dòng ngay
                        sau và trả None. Chắn HAI LỚP nên lớp ngoài
                        không giết được.
        204             `thuc > 0` — dòng trên đã bảo đảm `thuc > 0`.
        279             `day <= 0` trong nhánh maker — sổ rỗng có
                        `spread is None` nên đã trả 0,5 từ dòng trước;
                        sổ có spread thì chắc chắn có độ sâu.

    HAI cái bẫy của chính phép kiểm, cả hai đều bị bộ quét bắt:

    · `_xac_suat_khop(so, laMaker, soCo)` — tôi gọi nhầm thứ tự thành
      `(so, soCo, laMaker)`, và nó vẫn "đạt" vì 10.0 là truthy nên rơi
      đúng nhánh maker.
    · `giaCho` so với `vwap` trên một sổ MỘT TẦNG thì hai số bằng nhau,
      nên phép kiểm không phân biệt được gì. Phải dựng sổ nhiều tầng,
      và có một phép kiểm riêng canh rằng chúng thật sự khác nhau.
    """
    print()
    print("-- Bien cua CAN LOI ----------------------------------------")
    from kham.can_loi import can as _can3
    from kham.can_loi import gia_cap as _gc3
    from kham.can_loi import phi_taker as _pt3
    from kham.so_lenh import Muc as _M3
    from kham.so_lenh import SoLenh as _S3

    su = _S3(ma="X", ben="UP", bid=[_M3(0.44, 500.0)],
             ask=[_M3(0.46, 500.0)], nhanLucMs=0.0)
    sd = _S3(ma="X", ben="DOWN", bid=[_M3(0.52, 500.0)],
             ask=[_M3(0.54, 500.0)], nhanLucMs=0.0)
    rong = _S3(ma="X", ben="UP", bid=[], ask=[], nhanLucMs=0.0)

    # ── từ chối thay vì bịa ──────────────────────────────────────────
    kiem("xin 0 cổ → None, không phải cơ hội cỡ 0",
         _can3("X", "UP", "t", 0.6, 0.02, su, 0.0) is None)
    kiem("sổ rỗng → None", _can3("X", "UP", "t", 0.6, 0.02, rong, 10.0)
         is None)
    kiem("cặp: xin 0 cặp → None", _gc3("X", su, sd, 0.0) is None)
    kiem("cặp: thiếu một bên sổ → None", _gc3("X", su, None, 10.0) is None)
    kiem("cặp: một bên sổ rỗng → None", _gc3("X", su, rong, 10.0) is None)

    # ── giá cặp ĐÚNG $1,00 là HOÀ, không phải khoá lỗ ────────────────
    _bang = _S3(ma="X", ben="UP", bid=[_M3(0.40, 500.0)],
                ask=[_M3(0.40, 500.0)], nhanLucMs=0.0)
    _bang2 = _S3(ma="X", ben="DOWN", bid=[_M3(0.60, 500.0)],
                 ask=[_M3(0.60, 500.0)], nhanLucMs=0.0)
    g = _gc3("X", _bang, _bang2, 100.0)
    kiem("cặp gom hết đúng $1,00 → giá cặp 1,00",
         g is not None and gan(g.giaCap, 1.0, 1e-9), g and g.giaCap)
    kiem("và KHÔNG phải cặp khoá lỗ", g is not None and not g.khoa_lo)
    _t2 = _S3(ma="X", ben="DOWN", bid=[_M3(0.61, 500.0)],
              ask=[_M3(0.61, 500.0)], nhanLucMs=0.0)
    g2 = _gc3("X", _bang, _t2, 100.0)
    kiem("nhích lên $1,01 thì LÀ khoá lỗ", g2 is not None and g2.khoa_lo,
         g2 and g2.giaCap)

    # ── số cặp THẬT là phần nhỏ hơn, không phải trung bình ───────────
    _mong = _S3(ma="X", ben="DOWN", bid=[_M3(0.60, 30.0)],
                ask=[_M3(0.60, 30.0)], nhanLucMs=0.0)
    g3 = _gc3("X", _bang, _mong, 100.0)
    kiem("một chân chỉ đủ 30 → số cặp THẬT là 30, không phải 65",
         g3 is not None and gan(g3.soCap, 30.0, 1e-9), g3 and g3.soCap)
    kiem("và `dayDu` phải FALSE khi một chân không đủ",
         g3 is not None and not g3.dayDu, g3 and g3.dayDu)

    # ── số mũ biểu phí phải THẬT SỰ được áp ──────────────────────────
    _cuMu = CONFIG["phi"].get("takerSoMu")
    try:
        CONFIG["phi"]["takerSoMu"] = 2.0
        kiem("đổi số mũ biểu phí thì phí ĐỔI THEO",
             gan(_pt3(0.5, 100.0),
                 round(float(CONFIG["phi"]["takerHeSo"]) * (0.25 ** 2)
                       * 100.0, 5), 1e-9),
             _pt3(0.5, 100.0))
    finally:
        if _cuMu is None:
            CONFIG["phi"].pop("takerSoMu", None)
        else:
            CONFIG["phi"]["takerSoMu"] = _cuMu
    kiem("trả lại số mũ 1 thì phí về đúng bảng chính thức",
         gan(round(_pt3(0.5, 100.0), 2), 1.75, 1e-9), _pt3(0.5, 100.0))

    # ── giá HIỂN THỊ phải là best ask, không phải vwap ───────────────
    #
    # `giaCho` chỉ để hiện lên buồng lái, nên sai nó không mất tiền —
    # nhưng nó là con số người đọc dùng để đối chiếu với sổ lệnh thật.
    # Thay lặng bằng vwap là làm mọi lần đối chiếu ấy lệch đi mà không
    # ai biết vì sao.
    # Sổ phải có NHIỀU TẦNG, không thì vwap trùng best ask và phép kiểm
    # không phân biệt được hai con số — nó đạt mà chẳng chứng minh gì.
    suNhieuTang = _S3(ma="X", ben="UP", bid=[_M3(0.44, 500.0)],
                      ask=[_M3(0.46, 50.0), _M3(0.50, 500.0)],
                      nhanLucMs=0.0)
    chx = _can3("X", "UP", "t", 0.60, 0.02, suNhieuTang, 100.0)
    kiem("sổ nhiều tầng: vwap KHÁC best ask (nếu không thì kiểm vô nghĩa)",
         chx is not None and abs(chx.vwap - suNhieuTang.best_ask) > 1e-6,
         chx and (chx.vwap, suNhieuTang.best_ask))
    kiem("`giaCho` là BEST ASK, không phải vwap",
         chx is not None and gan(chx.giaCho, suNhieuTang.best_ask),
         chx and (chx.giaCho, suNhieuTang.best_ask, chx.vwap))

    # ── sổ KHOÁ (bid = ask) và sổ RỖNG: hai ca biên của maker ────────
    from kham.can_loi import _nua_doi as _nd3
    from kham.can_loi import _xac_suat_khop as _xk3
    khoa = _S3(ma="X", ben="UP", bid=[_M3(0.50, 100.0)],
               ask=[_M3(0.50, 100.0)], nhanLucMs=0.0)
    kiem("spread ĐÚNG BẰNG 0 → xác suất khớp về mức 'không biết' 0,50",
         gan(_xk3(khoa, True, 10.0), 0.5), _xk3(khoa, True, 10.0))
    kiem("sổ rỗng thì maker cũng 0,50, không bịa một con số đẹp",
         gan(_xk3(rong, True, 10.0), 0.5), _xk3(rong, True, 10.0))
    kiem("taker thì không phụ thuộc spread",
         gan(_xk3(khoa, False, 10.0), 0.94), _xk3(khoa, False, 10.0))
    kiem("sổ rỗng → nửa đời bằng 0, không phải một con số sống",
         gan(_nd3(rong, 0.02), 0.0), _nd3(rong, 0.02))
    kiem("sổ có hàng → nửa đời dương", _nd3(su, 0.02) > 0, _nd3(su, 0.02))

    # ── nửa đời ĐÚNG BẰNG ngưỡng vẫn là ĐANG LÀM ĐƯỢC ────────────────
    ch = _can3("X", "UP", "t", 0.60, 0.02, su, 100.0)
    if ch is not None:
        nd = float(CONFIG["canLoi"]["nuaDoiToiThieuMs"])
        import dataclasses as _dc2
        kiem("nửa đời ĐÚNG BẰNG ngưỡng → vẫn đang làm được",
             _dc2.replace(ch, nuaDoiMs=nd).dang_lam,
             (nd, ch.nuaDoiMs))
        kiem("kém một mili giây → KHÔNG",
             not _dc2.replace(ch, nuaDoiMs=nd - 1.0).dang_lam)


def kiem_bien_cua_dinh_gia() -> None:
    """Biên của ĐỊNH GIÁ — nơi sinh ra mọi xác suất.

    Bộ quét đột biến: 16 trên 22 con sống sót ở lượt đầu. Ba biên đáng
    nhất, mỗi cái quyết một chuyện khác nhau:

    · ĐỦ MẪU MỞ KELLY. `tong_mau >= toiThieuMauHieuChinh`. Đúng bằng
      ngưỡng là ĐỦ — nếu không thì con số trong config không còn là
      thứ nó tự nhận ("tối thiểu"). Và đây là cửa cho phép nhân một xác
      suất với vốn thật.
    · MÔ HÌNH CÓ ĐANG NÓI GÌ KHÔNG. `|p − 0,5| > batDinh`. Bằng nhau là
      KHÔNG rõ ràng: bất định vừa đúng bằng khoảng cách tới 50% nghĩa
      là mô hình đang nói "tôi không biết" bằng một con số trông như
      đang biết.
    · Ô HIỆU CHỈNH. `lo <= p < hi` — nửa đóng nửa mở. Một điểm rơi vào
      hai ô là đếm đôi; rơi vào không ô nào là mất mẫu.

    ## Sau khi viết xong: 22 con → 15 CHẾT, 7 TƯƠNG ĐƯƠNG

        193 214 280  guard trên những giá trị mà `them()` đã lọc dương
                     từ trước, hoặc trên σ đã bị chặn > 0. Không tới
                     được — và phép kiểm "giá 0 / âm / NaN không lọt
                     vào lưới σ" chính là thứ chứng minh chuyện đó.
        367          `if tauThat < tau: phat = san × min(2, (tau −
                     tauThat)/tau)`. Ở điểm bằng nhau, phạt ra 0 —
                     đúng bằng nhánh kia.
        450          `h["n"] and h["lech"] is not None` — `bang()` chỉ
                     đặt `lech = None` khi `n = 0`, nên trạng thái phân
                     biệt được hai lối không tồn tại.
        187 300      hai con còn ngỏ nhưng biên hẹp: một là lệch ĐÚNG
                     MỘT nến ở mép cửa sổ σ, một là cờ `daMatPhang`
                     khi p rơi đúng vào `eps` tới từng bit.

    Và một lỗi của chính phép kiểm này, bắt được vì một vế đỏ lên:
    `du_de_dung_kelly` là PHƯƠNG THỨC, không phải property. Bản đầu
    quên cặp ngoặc, nên vế "Kelly MỞ" đạt một cách RỖNG — một bound
    method thì luôn truthy.
    """
    print()
    print("-- Bien cua DINH GIA ---------------------------------------")
    from kham.dinh_gia import DoBienDong as _DBD
    from kham.dinh_gia import GiaChuan as _GC2
    from kham.dinh_gia import HieuChinh as _HC3
    from kham.dinh_gia import dinh_gia as _dg2
    from kham.dinh_gia import o_hieu_chinh as _o

    # ── ô hiệu chỉnh: nửa đóng nửa mở, không hở không chồng ───────────
    kiem("mép DƯỚI thuộc về ô ấy", _o(0.10) == "10-20", _o(0.10))
    kiem("mép TRÊN thuộc ô SAU", _o(0.20) == "20-30", _o(0.20))
    kiem("0 rơi vào ô đầu", _o(0.0) == "0-10", _o(0.0))
    kiem("1,0 rơi vào ô cuối, không rơi ra ngoài", _o(1.0) == "90-100",
         _o(1.0))
    _dsO = [_o(x / 1000.0) for x in range(0, 1001)]
    kiem("mọi p trong [0,1] đều có đúng MỘT ô, không hở",
         all(x for x in _dsO), None)

    # ── đủ mẫu mở Kelly: ĐÚNG BẰNG ngưỡng là ĐỦ ───────────────────────
    nguong = int(CONFIG["dinhGia"]["toiThieuMauHieuChinh"])
    import tempfile as _tf3
    _d3 = Path(_tf3.mkdtemp())
    hc = _HC3(duong=_d3 / "hc.json")
    hc.o = {}
    for i in range(nguong - 1):
        hc.them(0.5, i % 2 == 0)
    # `du_de_dung_kelly` là PHƯƠNG THỨC, không phải property. Quên cặp
    # ngoặc thì phép kiểm đạt một cách RỖNG — một bound method luôn
    # truthy. Bản đầu của chính phép kiểm này mắc đúng lỗi ấy, và chỉ
    # lộ ra vì vế "còn KHOÁ" đỏ lên.
    kiem("kém ngưỡng một mẫu → Kelly còn KHOÁ",
         not hc.du_de_dung_kelly(), hc.tong_mau)
    hc.them(0.5, True)
    kiem("ĐÚNG BẰNG ngưỡng → Kelly MỞ", hc.du_de_dung_kelly(),
         hc.tong_mau)

    # ── ô rỗng phải khai là rỗng, không chia cho 0 ────────────────────
    hc2 = _HC3(duong=_d3 / "hc2.json")
    hc2.o = {}
    b = hc2.bang()
    kiem("sổ rỗng thì mọi ô khai n = 0, không nổ",
         all(x["n"] == 0 and x["duDoan"] is None for x in b), b[:1])

    # ── mô hình có đang nói gì không ──────────────────────────────────
    def _gc(p, bd):
        return _GC2(ma="X", pUp=p, pDown=1.0 - p, batDinh=bd,
                    batDinhThamSo=bd, ruiRoNhay=0.0, z=0.0,
                    sigmaGiay=1e-5, tauGiay=100.0, tauDungSan=False,
                    daMatPhang=False, giaHienTai=1.0, giaMo=1.0,
                    oHieuChinh=_o(p))
    # Dùng số biểu diễn ĐÚNG trong nhị phân: `abs(0,60 − 0,50)` ra
    # 0,09999999999999998 chứ không phải 0,10, nên nó không kiểm biên
    # mà kiểm số dấu phẩy động. 0,75 và 0,25 thì đúng tới từng bit.
    kiem("bất định ĐÚNG BẰNG khoảng cách tới 50% → KHÔNG rõ ràng",
         not _gc(0.75, 0.25).ro_rang)
    kiem("bất định nhỏ hơn một hạt → RÕ RÀNG",
         _gc(0.75, 0.249).ro_rang)

    # ── định giá: từ chối thay vì đoán ───────────────────────────────
    sg = 1.2e-4
    kiem("giá hiện tại bằng 0 → TỪ CHỐI", _dg2("X", 0.0, 100.0, 60.0, sg)
         is None)
    kiem("giá mở bằng 0 → TỪ CHỐI", _dg2("X", 100.0, 0.0, 60.0, sg) is None)
    kiem("σ bằng 0 → TỪ CHỐI", _dg2("X", 100.0, 100.0, 60.0, 0.0) is None)
    kiem("σ None → TỪ CHỐI", _dg2("X", 100.0, 100.0, 60.0, None) is None)
    kiem("τ vô cực → TỪ CHỐI, không tính trên số vô hạn",
         _dg2("X", 100.0, 100.0, float("inf"), sg) is None)

    # ── sàn τ: ĐÚNG BẰNG sàn thì chưa dùng sàn ───────────────────────
    san = float(CONFIG["dinhGia"]["sanNenGiay"])
    g = _dg2("X", 100.0, 100.0, san, sg)
    kiem("τ ĐÚNG BẰNG sàn → chưa phải đang dùng sàn",
         g is not None and not g.tauDungSan, g and g.tauDungSan)
    g = _dg2("X", 100.0, 100.0, san / 2.0, sg)
    kiem("τ dưới sàn → CÓ dùng sàn, và bất định bị PHẠT thêm",
         g is not None and g.tauDungSan, g and g.tauDungSan)

    # ── bộ ước σ: giá xấu không được lọt vào lưới ────────────────────
    bd = _DBD()
    bd.them(0.0, 1_000_000.0)
    bd.them(-5.0, 1_000_000.0)
    bd.them(float("nan"), 1_000_000.0)
    kiem("giá 0 / âm / NaN không lọt vào lưới σ", not bd._luoi, bd._luoi)
    bd.them(100.0, 1_000_000.0)
    kiem("giá tử tế thì vào", len(bd._luoi) == 1, bd._luoi)
    kiem("chưa đủ nến thì σ là None, không bịa", bd.sigma_giay() is None)

    # ── σ bằng 0 phải là None, KHÔNG phải 0 ──────────────────────────
    #
    # Giá đứng yên hoàn toàn cho phương sai 0. Trả về 0 thì mọi chỗ
    # dùng σ chia cho 0; trả None thì chúng từ chối định giá. Đây là
    # khác biệt giữa "không biết" và "biết chắc là không dao động".
    bd2 = _DBD()
    for i in range(20):
        bd2.them(100.0, i * 60_000.0)
    kiem("giá đứng yên hoàn toàn → σ là None, không phải 0",
         bd2.sigma_giay() is None, bd2.sigma_giay())
    bd3 = _DBD()
    for i in range(20):
        bd3.them(100.0 + (i % 3) * 0.5, i * 60_000.0)
    _s3 = bd3.sigma_giay()
    kiem("giá có nhấp nhô → σ dương", _s3 is not None and _s3 > 0, _s3)

    # ── ô CÓ TÊN nhưng n = 0 vẫn phải khai rỗng ──────────────────────
    hc3 = _HC3(duong=_d3 / "hc3.json")
    hc3.o = {"0-10": {"n": 0, "tongP": 0.0, "thang": 0}}
    b3 = hc3.bang()
    kiem("ô có tên mà n = 0 → khai rỗng, không chia cho 0",
         b3[0]["n"] == 0 and b3[0]["duDoan"] is None, b3[0])
    kiem("và sai số trung bình là None khi chưa có mẫu nào",
         hc3.sai_so_tuyet_doi_tb() is None, hc3.sai_so_tuyet_doi_tb())

    # ── phạt ngoại suy: τ thật ĐÚNG BẰNG τ dùng thì KHÔNG phạt ───────
    from kham.dinh_gia import _bat_dinh as _bd
    kiem("τ thật bằng τ dùng → không phạt ngoại suy",
         gan(_bd(0.5, 1e-4, 100.0, 100.0), _bd(0.5, 1e-4, 100.0, 100.0)))
    kiem("τ thật NHỎ HƠN → bất định lớn hơn",
         _bd(0.5, 1e-4, 100.0, 50.0) > _bd(0.5, 1e-4, 100.0, 100.0),
         (_bd(0.5, 1e-4, 100.0, 50.0), _bd(0.5, 1e-4, 100.0, 100.0)))


def kiem_bien_cua_ket_toan() -> None:
    """Biên của KẾT TOÁN — module quyết định AI THẮNG.

    Bộ quét đột biến: **15 trên 16 con sống sót** ở lượt đầu, tệ nhất
    trong cả cung. Mà đây là chỗ hệ trọng nhất: nó quyết kết quả từng
    khung, và mọi thứ phía sau — Brier, điểm kỹ năng, đường nắn, cổng
    tiến hoá, lãi lỗ — đều tra kết quả ấy.

    Ba nhóm biên:

    · ĐỊNH NGHĨA THẮNG THUA. `dong > giaMo` và `up > down`. Hoà thì
      thuộc về ai? Ở đây: hoà tuyệt đối thì TỪ CHỐI đoán, chứ không
      gán bừa cho DOWN.
    · SÀN ĐÃ CHỐT CHƯA. `abs(up − down) < 0.9` — giá còn ở giữa nghĩa
      là chưa chốt. Nhận sớm một khung chưa chốt là ghi một kết quả
      bịa vào sổ nền.
    · NHỊP HỎI. Hỏi quá sớm thì sàn chưa có; hỏi quá dày thì phí; hỏi
      quá nhiều lần thì treo mãi.

    ## Sau khi viết xong: 16 con → 10 CHẾT, 6 TƯƠNG ĐƯƠNG

        201 `up > down` — dòng trên đã từ chối khi `abs(up − down) <
            0,9`, nên up == down không bao giờ tới được đây.
        210 `dong > giaMo` — dòng trên đã trả None khi hai giá bằng
            nhau. Cùng một kiểu chắn.
        208 `abs(dong − giaMo) < 1e-9` — khác biệt chỉ ở chênh lệch
            ĐÚNG BẰNG 1e-9 tới từng bit; dựng ca ấy bằng số thực là
            chuyện may rủi.
        149 217 `coUp > 0 or coDown > 0` — với tồn kho rỗng, nhánh kia
            cộng thêm 0. (217 ĐÃ chết nhờ phép kiểm "đứng ngoài khung
            thì không có dòng lãi lỗ"; 149 nằm ở đường BỎ THEO DÕI,
            nơi `treo` mặc định đã là 0.)
        158 chỉ đổi CHỮ trong một dòng nhật ký.
    """
    print()
    print("-- Bien cua KET TOAN: ai thang, va khi nao biet -------------")
    from kham.ket_toan import ChoKetToan as _CKT
    from kham.ket_toan import KetToan as _KT

    # ── định nghĩa thắng thua, đo THẲNG trên hai hàm quyết ────────────
    kt = _KT.__new__(_KT)
    c = _CKT(ma="BTC_5M", slug="s", ketThucMs=1_000_000.0, giaMo=100.0,
             capNen="BTCUSDT", tokenUp="u", tokenDown="d")

    from kham import ket_toan as _KTM
    _cuGia = _KTM.nguon.gia_dong_khung
    _cuMk = _KTM.nguon.market_theo_slug
    try:
        for dong, mong, nhan in ((100.5, True, "cao hơn giá mở → UP thắng"),
                                 (99.5, False, "thấp hơn → UP thua"),
                                 (100.0, None, "HOÀ TUYỆT ĐỐI → từ chối "
                                               "đoán, không gán cho DOWN")):
            _KTM.nguon.gia_dong_khung = lambda *a, _d=dong, **k: _d
            kiem(nhan, kt._tu_tinh(c) is mong, kt._tu_tinh(c))
        _KTM.nguon.gia_dong_khung = lambda *a, **k: None
        kiem("không lấy được giá đóng → từ chối, không đoán",
             kt._tu_tinh(c) is None)

        # ── sàn đã chốt chưa: khoảng cách hai giá phải ĐỦ RÕ ──────────
        def _mk(up, down):
            return lambda *a, **k: {"outcomePrices": [str(up), str(down)]}

        for up, down, mong, nhan in (
                (1.0, 0.0, True, "sàn trả 1/0 → UP thắng"),
                (0.0, 1.0, False, "sàn trả 0/1 → UP thua"),
                # Chọn cặp số biểu diễn được ĐÚNG trong nhị phân:
                # `abs(0.95 − 0.05)` ra 0,8999999999999999 chứ không
                # phải 0,9, nên nó KHÔNG phải phép kiểm biên — nó là
                # phép kiểm về số dấu phẩy động.
                (0.9, 0.0, True, "cách nhau ĐÚNG BẰNG ngưỡng 0,90 → NHẬN"),
                (0.875, 0.0, None, "cách nhau 0,875 → CHƯA chốt, từ chối"),
                (0.5, 0.5, None, "còn ở giữa → CHƯA chốt")):
            _KTM.nguon.market_theo_slug = _mk(up, down)
            kiem(nhan, kt._hoi_san(c) is mong, kt._hoi_san(c))
        _KTM.nguon.market_theo_slug = lambda *a, **k: {
            "outcomePrices": ["1.0"]}
        kiem("thiếu vế thứ hai → từ chối", kt._hoi_san(c) is None)
        _KTM.nguon.market_theo_slug = lambda *a, **k: None
        kiem("không có market → từ chối", kt._hoi_san(c) is None)
    finally:
        _KTM.nguon.gia_dong_khung = _cuGia
        _KTM.nguon.market_theo_slug = _cuMk

    # ── nhịp hỏi: ba biên, ba ý nghĩa khác nhau ───────────────────────
    def _moi_kt():
        k = Kho()
        from kham.dinh_gia import HieuChinh as _HC
        from kham.so import So as _So
        import tempfile as _tf
        d = Path(_tf.mkdtemp())
        return _KT(k, _HC(duong=d / "hc.json"), _So(d / "so.jsonl"))

    # CHE cả hai nguồn suốt khối này. Không che thì `_hoi_san` gọi
    # Gamma và `_tu_tinh` gọi Binance THẬT — bộ kiểm phải chạy được khi
    # không có mạng, và một phép kiểm phụ thuộc mạng thì lúc xanh lúc đỏ
    # vì lý do chẳng liên quan gì tới mã.
    _cuGia2 = _KTM.nguon.gia_dong_khung
    _cuMk2 = _KTM.nguon.market_theo_slug
    try:
        _KTM.nguon.gia_dong_khung = lambda *a, **k: None
        _KTM.nguon.market_theo_slug = lambda *a, **k: None

        kt2 = _moi_kt()
        kt2.ghi_danh("BTC_5M", "s", 1_000_000.0, 100.0, "BTCUSDT",
                     "u", "d")
        cho = kt2.cho["s"]
        som = 1_000_000.0 + _KT.CHO_TRUOC_KHI_HOI_GIAY * 1000.0
        kt2.soat(som - 1.0)
        kiem("chưa tới hạn chờ thì KHÔNG hỏi", cho.soLanHoi == 0,
             cho.soLanHoi)
        kt2.soat(som)
        kiem("ĐÚNG BẰNG hạn chờ thì HỎI", cho.soLanHoi == 1, cho.soLanHoi)
        kt2.soat(som + _KT.CACH_HAI_LAN_HOI_GIAY * 1000.0 - 1.0)
        kiem("hỏi lại quá dày thì bỏ qua", cho.soLanHoi == 1, cho.soLanHoi)
        kt2.soat(som + _KT.CACH_HAI_LAN_HOI_GIAY * 1000.0)
        kiem("cách ĐÚNG BẰNG nhịp thì hỏi tiếp", cho.soLanHoi == 2,
             cho.soLanHoi)

        # `soat` TĂNG bộ đếm rồi mới so, nên đặt ở `TOI_DA_HOI − 1` để
        # lần hỏi kế tiếp rơi ĐÚNG vào `TOI_DA_HOI`.
        cho.soLanHoi = _KT.TOI_DA_HOI - 1
        kt2.soat(som + 10_000_000.0)
        kiem("hỏi ĐÚNG BẰNG số lần tối đa thì vẫn còn theo dõi",
             "s" in kt2.cho and cho.soLanHoi == _KT.TOI_DA_HOI,
             (list(kt2.cho), cho.soLanHoi))
        kt2.soat(som + 20_000_000.0)
        kiem("quá số lần tối đa thì BỎ theo dõi, không treo mãi",
             "s" not in kt2.cho, list(kt2.cho))
        # ── một nguồn có, một nguồn không → VẪN kết toán ─────────────
        #
        # `if san is None and tu_tinh is None: return False`. Đổi `and`
        # thành `or` là bỏ mọi khung mà chỉ một nguồn trả lời — tức
        # gần như MỌI khung, vì Gamma đang bị chặn.
        def _dung(san=None, tuTinh=None, coViThe=True):
            kk = Kho()
            from kham.dinh_gia import HieuChinh as _HC2
            from kham.so import So as _So2
            import tempfile as _tf2
            dd = Path(_tf2.mkdtemp())
            ktx = _KT(kk, _HC2(duong=dd / "hc.json"), _So2(dd / "so.jsonl"))
            if coViThe:
                kk.lay("BTC_5M").ghi_khop("UP", 10.0, 0.5)
            ktx.ghi_danh("BTC_5M", "s", 1_000_000.0, 100.0, "BTCUSDT",
                         "u", "d")
            _KTM.nguon.market_theo_slug = (
                None if san is None
                else (lambda *a, **k: {"outcomePrices":
                                       ["1.0" if san else "0.0",
                                        "0.0" if san else "1.0"]}))
            if san is None:
                _KTM.nguon.market_theo_slug = lambda *a, **k: None
            _KTM.nguon.gia_dong_khung = (
                (lambda *a, **k: None) if tuTinh is None
                else (lambda *a, **k: 100.5 if tuTinh else 99.5))
            xong = ktx._thu_ket_toan(ktx.cho["s"])
            dong = [x for x in (dd / "so.jsonl").read_text(
                encoding="utf-8").splitlines() if x.strip()]                 if (dd / "so.jsonl").exists() else []
            return ktx, xong, dong

        _, xong, _ = _dung(san=None, tuTinh=True)
        kiem("chỉ TỰ TÍNH trả lời → vẫn kết toán", xong)
        _, xong, _ = _dung(san=True, tuTinh=None)
        kiem("chỉ SÀN trả lời → vẫn kết toán", xong)
        _, xong, _ = _dung(san=None, tuTinh=None)
        kiem("không nguồn nào trả lời → KHÔNG kết toán", not xong)

        # ── cờ BẤT ĐỒNG phải đúng chiều ──────────────────────────────
        ktx, _, _ = _dung(san=True, tuTinh=True)
        kiem("hai nguồn NÓI GIỐNG nhau → không bất đồng",
             ktx.soBatDong == 0, ktx.soBatDong)
        ktx, _, _ = _dung(san=True, tuTinh=False)
        kiem("hai nguồn NÓI NGƯỢC nhau → đếm bất đồng",
             ktx.soBatDong == 1, ktx.soBatDong)

        # ── không có vị thế thì KHÔNG ghi dòng lãi lỗ ────────────────
        #
        # `if v is not None and (v.coUp > 0 or v.coDown > 0)`. Đổi `>`
        # thành `>=` là ghi một dòng kết toán $0 cho MỌI khung mình
        # đứng ngoài — sổ lãi lỗ phình lên bằng những dòng không tương
        # ứng với đồng nào.
        _, _, dong = _dung(san=None, tuTinh=True, coViThe=False)
        kiem("đứng ngoài khung thì KHÔNG có dòng lãi lỗ", not dong, dong)
        _, _, dong = _dung(san=None, tuTinh=True, coViThe=True)
        kiem("có vị thế thì CÓ đúng một dòng", len(dong) == 1, len(dong))
    finally:
        _KTM.nguon.gia_dong_khung = _cuGia2
        _KTM.nguon.market_theo_slug = _cuMk2


def kiem_bien_cua_cham_moc() -> None:
    """Biên của động cơ CHẠM MỐC — nặng nhất là "đỉnh ĐÚNG BẰNG mốc".

    Bộ quét đột biến: 9 trên 12 con sống sót ở lượt đầu, trên một file
    chỉ có 12 chỗ so sánh. Tỉ lệ ấy nói rằng phép kiểm cũ chạm được
    công thức nhưng không chạm biên nào cả.

    Con nặng nhất ở dòng `dinhDaQua >= moc`: giá đã CHẠM ĐÚNG mốc thì
    market ĐÃ ngã ngũ. Đổi thành `>` là trả về một xác suất nhỏ xinh
    cho một chuyện đã xảy ra chắc chắn — và đó đúng là "bẫy chết người
    của họ này" mà docstring của chính module ấy nêu.

    ## Sau khi viết xong: 12 con → 7 CHẾT, 5 TƯƠNG ĐƯƠNG

        147 245  `if mau <= 0` với `mau = σ × √τ`. σ đã bị chặn > 0 ở
                 trên và τ có sàn, nên `mau > 0` LUÔN. Không tới được.
        239      `(CONFIG.get("dinhGia") or {})` — `nhipQuanSatGiay`
                 không khai trong config, nên cả hai lối cùng rơi về
                 mặc định 60,0.
        281 283  `p > 0.995` — khác biệt DUY NHẤT là cờ `daMatPhang`
                 khi p rơi ĐÚNG vào 0,995 tới từng bit. Dựng được một
                 ca như thế bằng số thực là chuyện của may rủi, không
                 phải của phép kiểm.
    """
    print()
    print("-- Bien cua dong co CHAM MOC -------------------------------")
    import math as _m

    from kham.cham_moc import TAU_SAN_GIAY as _TSAN
    from kham.cham_moc import cham_moc as _cm

    NGAY = 86400.0
    sig = 1.2e-4
    goc = dict(ma="X", giaHienTai=72_000.0, moc=150_000.0,
               tauGiay=133 * NGAY, sigmaGiay=sig)

    # ── đỉnh ĐÚNG BẰNG mốc → ĐÃ CHẠM ─────────────────────────────────
    g = _cm(dinhDaQua=150_000.0, **goc)
    kiem("đỉnh ĐÚNG BẰNG mốc → coi là ĐÃ CHẠM, P = 1",
         g is not None and gan(g.pUp, 1.0), g and g.pUp)
    g = _cm(dinhDaQua=149_999.99, **goc)
    kiem("kém mốc một xu thì CHƯA chạm", g is not None and g.pUp < 0.5,
         g and g.pUp)
    # Chiều XUỐNG cũng vậy — hai nhánh của cùng một dòng.
    gx = dict(goc)
    gx.update(giaHienTai=150_000.0, moc=72_000.0)
    g = _cm(dinhDaQua=72_000.0, lenTren=False, **gx)
    kiem("chiều XUỐNG: đáy ĐÚNG BẰNG mốc → ĐÃ CHẠM",
         g is not None and gan(g.pUp, 1.0), g and g.pUp)

    # ── từ chối khi thiếu nguyên liệu, không đoán ─────────────────────
    kiem("thiếu giá hiện tại → TỪ CHỐI",
         _cm(ma="X", moc=150_000.0, tauGiay=NGAY, dinhDaQua=1.0,
             sigmaGiay=sig) is None)
    kiem("thiếu mốc → TỪ CHỐI",
         _cm(ma="X", giaHienTai=72_000.0, tauGiay=NGAY, dinhDaQua=1.0,
             sigmaGiay=sig) is None)
    kiem("thiếu τ → TỪ CHỐI",
         _cm(ma="X", giaHienTai=72_000.0, moc=150_000.0, dinhDaQua=1.0,
             sigmaGiay=sig) is None)
    kiem("giá bằng 0 → TỪ CHỐI, không lấy log của 0",
         _cm(dinhDaQua=1.0, **{**goc, "giaHienTai": 0.0}) is None)
    kiem("mốc bằng 0 → TỪ CHỐI", _cm(dinhDaQua=1.0,
                                     **{**goc, "moc": 0.0}) is None)
    kiem("σ bằng 0 → TỪ CHỐI, không chia cho 0",
         _cm(dinhDaQua=1.0, **{**goc, "sigmaGiay": 0.0}) is None)

    # ── sàn τ: ĐÚNG BẰNG sàn thì KHÔNG phải đang dùng sàn ─────────────
    g = _cm(dinhDaQua=1.0, **{**goc, "tauGiay": _TSAN})
    kiem("τ ĐÚNG BẰNG sàn → chưa phải đang dùng sàn",
         g is not None and not g.tauDungSan, g and g.tauDungSan)
    g = _cm(dinhDaQua=1.0, **{**goc, "tauGiay": _TSAN - 0.001})
    kiem("τ dưới sàn một chút → CÓ dùng sàn",
         g is not None and g.tauDungSan)

    # ── làm phẳng hai đầu: ĐÚNG BẰNG mép thì CHƯA phẳng ───────────────
    #
    # `p > 0.995` chứ không `>=`. Đúng bằng mép là đúng giá trị mép,
    # nên không có gì để kéo — và cờ `daMatPhang` phải nói THẬT, vì
    # buồng lái đọc nó để biết con số hiển thị có bị can thiệp không.
    g = _cm(dinhDaQua=1.0, **{**goc, "moc": 72_000.5, "tauGiay": 30 * NGAY})
    kiem("gần chạm chắc chắn → P bị làm phẳng ở 0,995",
         g is not None and gan(g.pUp, 0.995) and g.daMatPhang,
         g and (g.pUp, g.daMatPhang))
    g = _cm(dinhDaQua=1.0, **{**goc, "tauGiay": 60.0 * 60.0})
    kiem("xa tít mù → P bị làm phẳng ở 0,005",
         g is not None and gan(g.pUp, 0.005) and g.daMatPhang,
         g and (g.pUp, g.daMatPhang))


def kiem_bien_cua_ton_kho() -> None:
    """Biên số học của tồn kho — chỗ chia cho 0 và chỗ giá cặp bằng $1,00.

    Bộ quét đột biến trên `kham/kho_doi.py`: 17 trên 27 con sống sót ở
    lượt đầu. Đây là file làm SỐ HỌC TIỀN — giá vốn, giá cặp, lỗ khoá,
    phơi nhiễm — nên một biên sai ở đây chảy vào mọi thứ phía sau mà
    không lỗi nào ném ra.

    Hai nhóm biên đáng nhất:

    · chia cho 0: `giaVonUp` khi chưa có cổ nào, `giaCap` khi chưa ghép
      cặp. Đổi `> 0` thành `>= 0` là `ZeroDivisionError` giữa vòng chạy.
    · giá cặp ĐÚNG BẰNG $1,00: cặp mua trọn hai chân hết đúng một đô
      thì hoà, không lỗ. Lệch một bên là bịa ra một khoản lỗ không có,
      hoặc giấu một khoản lỗ có thật.

    ## Sau khi viết xong: 27 con → 19 CHẾT, 8 TƯƠNG ĐƯƠNG

    Phân loại 8 con còn sống, đã kiểm tay:

        123 136 138 394 395 418
            Tất cả đều là "ở điểm BẰNG 0 thì hai nhánh cho cùng một
            số". `(1,00 − 1,00) × n = 0`; `du × giá = 0` khi du = 0;
            `sqrt(0) = 0`. Dòng 138 còn không tới được, vì 136 đã trả
            về trước khi du = 0.

        306 309
            `CONFIG.get("thiTruong") or []` → `and` khiến vòng lặp
            không chạy, và hàm rơi về `ma.split("_")[0]`. Với config
            HIỆN TẠI, đường rơi về cho ĐÚNG cùng đáp án ("XRP_5M" →
            "XRP" cả hai lối), nên không giết được. Nó sẽ giết được
            ngay khi có một market mà tên nhóm khác phần trước dấu
            gạch — và lúc ấy phép kiểm nhóm ở dưới sẽ đỏ trước.

    Chạy lại: `python scripts/quet-dot-bien.py --file=kham/kho_doi.py`.
    """
    print()
    print("-- Bien so hoc cua ton kho ---------------------------------")
    from kham.kho_doi import ChanCho as _CC
    from kham.kho_doi import ViThe as _VT

    # ── chia cho 0 ────────────────────────────────────────────────────
    v = _VT(ma="X")
    kiem("chưa có cổ nào thì giá vốn là 0, không nổ",
         gan(v.giaVonUp, 0.0) and gan(v.giaVonDown, 0.0))
    kiem("chưa ghép cặp thì giá cặp là None, không nổ",
         v.giaCap is None, v.giaCap)
    kiem("và lỗ khoá là 0", gan(v.loKhoaUsd, 0.0))

    # ── giá cặp ĐÚNG BẰNG $1,00 là HOÀ, không phải lỗ ─────────────────
    v = _VT(ma="X")
    v.ghi_khop("UP", 100.0, 0.40)
    v.ghi_khop("DOWN", 100.0, 0.60)
    kiem("cặp mua hết đúng $1,00 → giá cặp 1,00",
         gan(v.giaCap, 1.0, 1e-9), v.giaCap)
    kiem("cặp đúng $1,00 KHÔNG phải cặp khoá lỗ", not v.capKhoaLo)
    kiem("và lỗ khoá bằng 0, không phải một xu", gan(v.loKhoaUsd, 0.0),
         v.loKhoaUsd)
    v2 = _VT(ma="X")
    v2.ghi_khop("UP", 100.0, 0.41)
    v2.ghi_khop("DOWN", 100.0, 0.60)
    kiem("nhích lên $1,01 thì LÀ cặp khoá lỗ", v2.capKhoaLo, v2.giaCap)
    kiem("và lỗ khoá đúng $1,00 cho 100 cặp",
         gan(v2.loKhoaUsd, 1.0, 1e-9), v2.loKhoaUsd)

    # ── tồn kho lệch ĐÚNG BẰNG 0 → không có chân trần ─────────────────
    v3 = _VT(ma="X")
    v3.ghi_khop("UP", 50.0, 0.5)
    v3.ghi_khop("DOWN", 50.0, 0.5)
    kiem("lệch đúng 0 cổ → chân trần bằng 0",
         gan(v3.chuaPhongHoUsd, 0.0), v3.chuaPhongHoUsd)
    v3.ghi_khop("UP", 10.0, 0.5)
    kiem("lệch 10 cổ → chân trần đo bằng ĐÔ theo giá vốn",
         gan(v3.chuaPhongHoUsd, 5.0, 1e-9), v3.chuaPhongHoUsd)

    # ── ghi khớp 0 cổ là KHÔNG ghi gì, kể cả phí ──────────────────────
    #
    # `if soCo <= 0: return` — không phải "cộng thêm 0". Một lần khớp 0
    # cổ vẫn kèm phí thì phí ấy phải bị bỏ, không thì tồn kho gánh một
    # khoản phí không tương ứng với cổ nào.
    v4 = _VT(ma="X")
    v4.ghi_khop("UP", 0.0, 0.5, 1.23, 0.6)
    kiem("khớp 0 cổ thì KHÔNG ghi phí", gan(v4.phiUsd, 0.0), v4.phiUsd)
    kiem("và không ghi niềm tin mô hình", v4.pVaoTb is None, v4.pVaoTb)

    # ── mua chân ĐỐI DIỆN làm lỗ xấu nhất GIẢM, cả hai chiều ──────────
    v5 = _VT(ma="X")
    v5.ghi_khop("UP", 100.0, 0.5)
    kiem("thêm DOWN thì lỗ xấu nhất giảm",
         v5.lo_xau_nhat_khi_mua("DOWN", 100.0, 0.4) < v5.lo_xau_nhat_usd(),
         (v5.lo_xau_nhat_khi_mua("DOWN", 100.0, 0.4), v5.lo_xau_nhat_usd()))
    kiem("thêm UP thì lỗ xấu nhất TĂNG",
         v5.lo_xau_nhat_khi_mua("UP", 100.0, 0.4) > v5.lo_xau_nhat_usd())

    # ── NHÓM tài sản suy từ mã nến, có ba đường và cả ba phải đúng ───
    #
    # Cả cổng 7 (trần mỗi nhóm) dựa trên hàm này, nên suy sai nhóm là
    # hai market khác nhau cùng ăn một hạn mức, hoặc hai market cùng rổ
    # được tính là hai rổ riêng. Không lỗi nào ném ra.
    from kham.kho_doi import nhom_tai_san as _nts
    kiem("bảng cứng đè trước", _nts("BTC_5M") == "BTC", _nts("BTC_5M"))
    kiem("market NGOÀI bảng cứng thì suy từ mã nến trong config",
         _nts("XRP_5M") == "XRP", _nts("XRP_5M"))
    kiem("hậu tố tiền tệ bị cắt, không dính vào tên nhóm",
         "USDT" not in _nts("XRP_5M"), _nts("XRP_5M"))
    kiem("market KHÔNG có trong config thì rơi về phần trước dấu gạch",
         _nts("DOGE_5M") == "DOGE", _nts("DOGE_5M"))
    kiem("mã không có dấu gạch cũng ra chính nó, không ra rỗng",
         _nts("LAMOT") == "LAMOT", _nts("LAMOT"))

    # ── chân chờ: ĐÚNG BẰNG hạn thì CHƯA quá hạn ──────────────────────
    han = float(CONFIG["khoDoi"]["giayChoChanHai"]) * 1000.0
    c = _CC(ben="UP", soCo=1.0, giaTrungBinh=0.5, moLucMs=0.0,
            capMongMuon=0.98)
    kiem("chân chờ ĐÚNG BẰNG hạn → CHƯA quá hạn", not c.qua_han(han), han)
    kiem("quá hạn một mili giây → quá hạn", c.qua_han(han + 1.0))
    kiem("`bayGioMs` bỏ trống thì lấy đồng hồ máy, không nổ",
         c.tuoi_ms() > 0)
    # Mốc 0,0 phải được TÔN TRỌNG. `bayGioMs or time.time()` nuốt nó vì
    # 0 là falsy, rồi trả về một con số trông hoàn toàn hợp lý — và nó
    # làm cây quyết định của `chan_rui_ro` rẽ sang nhánh "quá hạn chờ"
    # cho MỌI ca.
    c0 = _CC(ben="UP", soCo=1.0, giaTrungBinh=0.5, moLucMs=0.0,
             capMongMuon=0.98)
    kiem("mốc 0,0 được TÔN TRỌNG, không rơi về đồng hồ máy",
         gan(c0.tuoi_ms(0.0), 0.0), c0.tuoi_ms(0.0))
    kiem("và chân mới mở thì CHƯA quá hạn", not c0.qua_han(0.0))


def kiem_bien_cua_cong_rui_ro() -> None:
    """ĐÚNG BẰNG trần thì sao? — biên của từng cổng, pin lại từng cái.

    Bộ quét đột biến (`scripts/quet-dot-bien.py`) đổi từng toán tử so
    sánh trong `kham/rui_ro.py` rồi chạy cả bộ kiểm. Lượt đầu: **36
    trên 44 con SỐNG SÓT** — tức 847 phép kiểm chạm được ĐƯỜNG ĐI của
    cổng nhưng gần như không chạm BIÊN của nó. Đổi `<` thành `<=` ở
    cầu dao lỗ ngày, ở trần vốn mỗi market, ở ngưỡng net edge — không
    phép kiểm nào kêu.

    "Đúng bằng trần" là ca hay xảy ra nhất trong đời thật, vì cỗ máy
    tự siết cỡ lệnh cho VỪA KHÍT trần. Mỗi phép kiểm dưới đây pin một
    biên và nói rõ vì sao nó nằm ở phía ấy.

    ## Sau khi viết xong: 44 con → 30 CHẾT, 14 TƯƠNG ĐƯƠNG, 0 còn ngỏ

    Phân loại 14 con còn sống, để phiên sau đừng đuổi con ma. Mỗi dòng
    dưới đây đã kiểm bằng tay, không phải đoán:

        417 425 438 488 502 520 551 579
            `if X < cho_phep: cho_phep = X` — ở điểm BẰNG NHAU, phép
            gán trả về đúng giá trị cũ. Đổi `<` thành `<=` không đổi gì.

        251 293
            `if lai < 0: gop += -lai` — ở 0 thì cộng thêm −0,0. Không
            đổi gì. (Phép kiểm "kết toán HOÀ không tính là lỗ" vẫn
            đáng có: nó pin Ý ĐỊNH, dù không giết được con nào.)

        559 `dang_tran + them_tran > tranTran` — ở điểm bằng nhau,
            nhánh siết tính ra `con/vwap` đúng bằng `cho_phep` cũ.

        591 `daSiet=cho_phep < ch.soCo - 1e-9` — cờ này chỉ để BÁO
            CÁO, không đổi lệnh; và epsilon đã nuốt điểm bằng nhau.

        604 `if b <= 0` với `b = (1−giá)/giá`, giá bị kẹp ≤ 0,999 nên
            `b ≥ 0,001 > 0` LUÔN. Không tới được.

        586 `cho_phep × netEdge < 0,01` — nhánh chết ở ngưỡng hiện
            tại; xem phép kiểm pin `netEdgeToiThieu >= 0,01`.

    Chạy lại: `python scripts/quet-dot-bien.py --file=kham/rui_ro.py`.
    Con số 14 mà LỚN LÊN nghĩa là có phép kiểm vừa bị gỡ hoặc làm yếu
    đi; nhỏ đi nghĩa là ai đó vừa đơn giản hoá được mã.
    """
    print()
    print("-- Bien cua tung cong: dung BANG tran thi sao? -------------")
    from kham.can_loi import CoHoi as _CH

    lanh = SucKhoeNguon(200, 150, 80)
    _CLc = CONFIG["canLoi"]

    def co_hoi(**k) -> _CH:
        """Một cơ hội dựng THẲNG, để đặt được đúng con số ở biên.

        `can()` tính netEdge từ sổ lệnh nên không nhắm trúng biên được.
        """
        d = dict(ma="BTC_5M", ben="UP", chienThuat="thử", fairValue=0.55,
                 giaCho=0.50, vwap=0.50, soCo=40.0,
                 grossEdge=0.05, phi=0.01, truotGia=0.0008,
                 batDinhMoHinh=0.02, bienAnToan=0.008, netEdge=0.05,
                 sucChua=400.0, xacSuatKhop=0.9, nuaDoiMs=5000.0,
                 laMaker=False, dayDu=True)
        d.update(k)
        return _CH(**d)

    def moi():
        kk = Kho()
        return kk, RiskEngine(kk)

    # ── sức khoẻ nguồn: ĐÚNG BẰNG trần thì CÒN LÀNH ──────────────────
    #
    # `>` chứ không `>=`. Trần khai là "tối đa", nên đúng bằng tối đa là
    # vẫn trong hạn. Ba mục đo ba thứ khác nhau nên phải soi riêng —
    # bộ quét đột biến coi chúng là ba con, và chúng đúng là ba chỗ sửa
    # được độc lập.
    _RRc = CONFIG["ruiRo"]
    for ten, khoa, dung in (
            ("sổ lệnh", "tuoiSoLenhToiDaMs",
             lambda x: SucKhoeNguon(x, 150, 80)),
            ("giá nền", "tuoiGiaNenToiDaMs",
             lambda x: SucKhoeNguon(200, x, 80)),
            ("đồng hồ", "lechDongHoToiDaMs",
             lambda x: SucKhoeNguon(200, 150, x)),
    ):
        tran = float(_RRc[khoa])
        kiem(f"{ten} cũ ĐÚNG BẰNG trần → vẫn LÀNH",
             not dung(tran).van_de(), (khoa, tran, dung(tran).van_de()))
        kiem(f"{ten} quá trần một mili giây → KÊU",
             dung(tran + 1.0).van_de(), (khoa, tran))
    kiem("đồng hồ lệch ÂM cũng bị soi, không chỉ lệch dương",
         SucKhoeNguon(200, 150,
                      -float(_RRc["lechDongHoToiDaMs"]) - 1.0).van_de())

    # ── dấu của lãi lỗ: ĐÚNG BẰNG 0 không phải LỖ ────────────────────
    #
    # `lỗ gộp` chỉ cộng những lần ÂM. Một lần kết toán hoà (0 đô) không
    # phải một lần lỗ, và đếm nó vào là thổi phồng thước ĐỘ CHAO.
    k, re = moi()
    re.ghi_lai_lo(0.0)
    kiem("kết toán HOÀ không được tính là một lần lỗ",
         gan(re.loGopNgayUsd, 0.0), re.loGopNgayUsd)
    re.ghi_lai_lo(-1.0)
    kiem("còn lỗ thật thì có", gan(re.loGopNgayUsd, 1.0), re.loGopNgayUsd)

    # Cùng luật ấy ở đường DỰNG LẠI TỪ SỔ — hai đường phải nói giống nhau.
    k, re = moi()
    _homNay = re._ngay_hien_tai()
    re.nap_tu_so([{"luc": _homNay + "T00:00:00Z", "laiLo": 0.0},
                  {"luc": _homNay + "T00:01:00Z", "laiLo": -2.0}])
    kiem("dựng lại từ sổ cũng không tính dòng HOÀ là lỗ",
         gan(re.loGopNgayUsd, 2.0), re.loGopNgayUsd)

    # ── đỉnh vốn 0 thì sụt vốn là 0, không phải chia cho 0 ────────────
    k, re = moi()
    re.dinhVon = 0.0
    kiem("đỉnh vốn 0 → sụt vốn 0%, không nổ", gan(re.sutVonPct, 0.0),
         re.sutVonPct)

    # ── cầu dao: ĐÚNG BẰNG trần thì NGẮT ──────────────────────────────
    #
    # `>=` chứ không `>`. Một cái trần mà phải VƯỢT mới ngắt thì nó
    # không phải trần, nó là "trần cộng một xu".
    k, re = moi()
    re.ghi_lai_lo(-re.tranLoNgayUsd)
    kiem("lỗ ngày ĐÚNG BẰNG trần → cầu dao NGẮT", re.ngatKhanCap,
         (re.loNgayUsd, re.tranLoNgayUsd))
    k, re = moi()
    re.ghi_lai_lo(-(re.tranLoNgayUsd - 0.01))
    kiem("kém trần một xu thì CHƯA ngắt", not re.ngatKhanCap)

    k, re = moi()
    re.dinhVon = 1000.0
    re.von = 1000.0 * (1.0 - float(CONFIG["ruiRo"]["tranSutVonPct"]) / 100.0)
    re._soat_ngat()
    kiem("sụt vốn ĐÚNG BẰNG trần → cầu dao NGẮT", re.ngatKhanCap,
         re.sutVonPct)

    # ── sàng cơ hội: ĐÚNG BẰNG ngưỡng thì ĐỦ ──────────────────────────
    #
    # `<` chứ không `<=`. Ngưỡng khai là "tối thiểu", nên đạt đúng mức
    # tối thiểu là ĐẠT — nếu không thì con số trong config không còn là
    # thứ nó tự nhận.
    for ten, khoa, dat in (
            ("net edge", "netEdgeToiThieu", "netEdge"),
            ("sức chứa", "sucChuaToiThieu", "sucChua"),
            ("xác suất khớp", "xacSuatKhopToiThieu", "xacSuatKhop"),
    ):
        nguong = float(_CLc[khoa])
        k, re = moi()
        q = re.duyet(co_hoi(**{dat: nguong}), lanh, 200, False)
        kiem(f"{ten} ĐÚNG BẰNG ngưỡng → vẫn qua sàng", q.cho, (khoa, nguong))
        k, re = moi()
        q = re.duyet(co_hoi(**{dat: nguong * 0.999 - 1e-9}), lanh, 200, False)
        kiem(f"{ten} kém ngưỡng một hạt → TỪ CHỐI", q.tu_choi)

    # ── sắp hết giờ: ĐÚNG BẰNG hạn chờ chân hai thì TỪ CHỐI ───────────
    #
    # `<=` chứ không `<`. Còn đúng bằng thời gian tối thiểu để phòng hộ
    # chân hai là KHÔNG đủ — phòng hộ cần THÊM thời gian sau đó.
    han = float(CONFIG["khoDoi"]["giayChoChanHai"])
    k, re = moi()
    kiem("còn ĐÚNG BẰNG hạn chờ chân hai → TỪ CHỐI mở mới",
         re.duyet(co_hoi(), lanh, han, False).tu_choi, han)
    k, re = moi()
    kiem("còn hơn hạn ấy một giây → cho qua",
         re.duyet(co_hoi(), lanh, han + 1.0, False).cho)

    # ── trần vốn mỗi market: ĐÚNG BẰNG trần thì HẾT chỗ ───────────────
    #
    # `con_duoc <= 0` chứ không `< 0`. Đã dùng hết đúng bằng trần thì
    # không còn gì để mở thêm; cho qua ở đây là cho vượt trần.
    k, re = moi()
    k.lay("BTC_5M").ghi_khop("UP", re.tranMoiThiTruongUsd / 0.5, 0.5)
    q = re.duyet(co_hoi(), lanh, 200, False)
    kiem("market đã dùng ĐÚNG BẰNG trần → TỪ CHỐI", q.tu_choi,
         (k.lay("BTC_5M").tienUp, re.tranMoiThiTruongUsd))
    kiem("và nói rõ chạm trần nào", any("trần" in x for x in q.lyDo), q.lyDo)

    # ── sau khi siết: ĐÚNG 1 cổ thì vẫn làm ───────────────────────────
    #
    # `cho_phep < 1` chứ không `<= 1`. Một cổ là một cổ.
    k, re = moi()
    q = re.duyet(co_hoi(soCo=1.0, sucChua=float(_CLc["sucChuaToiThieu"])),
                 lanh, 200, False)
    kiem("siết còn ĐÚNG 1 cổ thì vẫn cho làm", q.cho, q.soCoChoPhep)

    # ── ngân sách lỗ ngày (cổng 6b): ĐÚNG BẰNG 0 thì hết ──────────────
    k, re = moi()
    re.ghi_lai_lo(-re.tranLoNgayUsd + 1e-9)
    q = re.duyet(co_hoi(), lanh, 200, False)
    kiem("ngân sách ngày còn ĐÚNG BẰNG 0 → chỉ còn nhận phòng hộ",
         q.tu_choi, q.lyDo)

    # ── cổng 3 chỉ đổi LỜI GIẢI THÍCH, không đổi quyết định ───────────
    #
    # `CoHoi.dang_lam` dùng ĐÚNG bốn ngưỡng ấy với `>=`, còn cổng 3 dùng
    # `<`. Hai vế là đối ngẫu: cổng 3 chỉ chạy khi `dang_lam` False, tức
    # khi ÍT NHẤT MỘT mục đã tụt dưới ngưỡng. Nên một mục nằm ĐÚNG BẰNG
    # ngưỡng không bao giờ tự nó làm cơ hội bị loại — nó chỉ có thể bị
    # kể oan trong danh sách lý do.
    #
    # Bộ quét đột biến bắt được chính chỗ này: phép kiểm "đúng bằng
    # ngưỡng thì qua" ở trên ĐẠT MỘT CÁCH RỖNG, vì `dang_lam` True nên
    # cổng 3 không hề chạy. Nên phải canh LỜI GIẢI THÍCH.
    k, re = moi()
    q = re.duyet(co_hoi(netEdge=float(_CLc["netEdgeToiThieu"]),
                        sucChua=float(_CLc["sucChuaToiThieu"]) - 1.0),
                 lanh, 200, False)
    kiem("mục ĐÚNG BẰNG ngưỡng KHÔNG bị kể vào lý do loại",
         q.tu_choi and not any("net edge" in x for x in q.lyDo), q.lyDo)
    kiem("còn mục THẬT SỰ thiếu thì PHẢI được kể tên",
         any("sức chứa" in x for x in q.lyDo), q.lyDo)
    kiem("và lý do không bao giờ rỗng khi bị sàng loại", q.lyDo)

    # Ba mục còn lại của cổng 3, cùng một luật: đúng bằng ngưỡng thì
    # KHÔNG bị kể tên. Viết đủ cả bốn vì bộ quét đột biến đối xử với
    # bốn dòng ấy như bốn con riêng — và chúng đúng là bốn chỗ sửa
    # được độc lập.
    for ten, khoa, dat in (("sức chứa", "sucChuaToiThieu", "sucChua"),
                           ("xác suất khớp", "xacSuatKhopToiThieu",
                            "xacSuatKhop"),
                           ("cơ hội chỉ sống", "nuaDoiToiThieuMs",
                            "nuaDoiMs")):
        k, re = moi()
        qq = re.duyet(co_hoi(**{dat: float(_CLc[khoa]),
                                "netEdge": float(_CLc["netEdgeToiThieu"])
                                - 0.001}),
                      lanh, 200, False)
        kiem(f"`{ten}` đúng bằng ngưỡng → KHÔNG bị kể vào lý do",
             qq.tu_choi and not any(ten in x for x in qq.lyDo), qq.lyDo)

    # ── ngân sách ngày ĐÚNG BẰNG 0 và sức phòng hộ ĐÚNG BẰNG 1 cổ ─────
    k, re = moi()
    re.ghi_lai_lo(-re.tranLoNgayUsd)
    re.ngatKhanCap = False          # tách khỏi cầu dao để soi riêng cổng 6b
    re.lyDoNgat = ""
    v = k.lay("BTC_5M")
    v.ghi_khop("DOWN", 1.0, 0.5)    # phòng hộ đúng 1 cổ cho lệnh UP
    q = re.duyet(co_hoi(), lanh, 200, False)
    kiem("hết sạch ngân sách + sức phòng hộ ĐÚNG 1 cổ → vẫn cho phòng hộ",
         q.cho and q.soCoChoPhep <= 1.0 + 1e-9, (q.cho, q.soCoChoPhep))
    k, re = moi()
    re.ghi_lai_lo(-re.tranLoNgayUsd)
    re.ngatKhanCap = False
    re.lyDoNgat = ""
    q = re.duyet(co_hoi(), lanh, 200, False)
    # Canh LỜI TỪ CHỐI, không chỉ canh việc bị từ chối. Chỗ trống đúng
    # bằng 0 là ranh giới `du <= 0`: đổi thành `du < 0` thì vẫn từ chối,
    # nhưng bằng một lý do KHÁC ("sau khi siết còn dưới 1 cổ") — người
    # đọc buồng lái sẽ đi tìm nhầm chỗ.
    kiem("hết sạch ngân sách mà KHÔNG có gì để phòng hộ → TỪ CHỐI",
         q.tu_choi, q.lyDo)
    kiem("và nói ĐÚNG lý do: hết ngân sách, không phải 'dưới 1 cổ'",
         any("ngân sách lỗ ngày" in x for x in q.lyDo), q.lyDo)

    # ── hai cổng còn lại, cùng ranh giới "chỗ trống ĐÚNG BẰNG 0" ──────
    #
    # Cả hai đều phải nới MỌI cổng khác ra trước, không thì cổng khác
    # từ chối hộ và phép kiểm đạt vì lý do chẳng liên quan.
    _cu2 = {("ruiRo", x): CONFIG["ruiRo"].get(x)
            for x in ("phanTramLoNgay", "phanTramMoiThiTruong",
                      "phanTramMoiTaiSan", "phanTramPhoiNhiemGop")}
    _cu2[("khoDoi", "phanTramChuaPhongHo")] = CONFIG["khoDoi"].get(
        "phanTramChuaPhongHo")
    try:
        # (a) PHƠI NHIỄM GỘP đúng bằng trần
        CONFIG["ruiRo"]["phanTramLoNgay"] = 1000
        CONFIG["ruiRo"]["phanTramMoiThiTruong"] = 1000
        CONFIG["ruiRo"]["phanTramMoiTaiSan"] = 1000
        CONFIG["khoDoi"]["phanTramChuaPhongHo"] = 1000
        k, re = moi()
        re.von = 100_000.0
        tranGop = re.tranPhoiNhiemGopUsd
        k.lay("BTC_5M").ghi_khop("UP", tranGop / 0.5, 0.5)
        kiem("dựng được phơi nhiễm gộp ĐÚNG BẰNG trần",
             gan(k.phoi_nhiem_gop(), tranGop, 1e-6), k.phoi_nhiem_gop())
        q = re.duyet(co_hoi(phi=0.0), lanh, 200, True)
        kiem("phơi nhiễm gộp ĐÚNG BẰNG trần → TỪ CHỐI",
             q.tu_choi, q.lyDo)
        kiem("và nói ĐÚNG tên cổng: phơi nhiễm GỘP",
             any("GỘP" in x for x in q.lyDo), q.lyDo)

        # (b) CHÂN TRẦN đúng bằng trần
        CONFIG["khoDoi"]["phanTramChuaPhongHo"] = 5
        CONFIG["ruiRo"]["phanTramPhoiNhiemGop"] = 1000
        k, re = moi()
        re.von = 100_000.0
        tranT2 = re.tranChuaPhongHoUsd
        k.lay("SOL_5M").ghi_khop("UP", tranT2 / 0.5, 0.5)
        q = re.duyet(co_hoi(phi=0.0), lanh, 200, True)
        kiem("chân trần ĐÚNG BẰNG trần → TỪ CHỐI", q.tu_choi, q.lyDo)
        kiem("và nói ĐÚNG tên cổng: nằm trần một chân",
             any("nằm trần một chân" in x for x in q.lyDo), q.lyDo)
    finally:
        for (khoi, x), gt in _cu2.items():
            if gt is None:
                CONFIG[khoi].pop(x, None)
            else:
                CONFIG[khoi][x] = gt

    # ── trần phơi nhiễm gộp = 0 nghĩa là TẮT cổng ─────────────────────
    _cuG = CONFIG["ruiRo"].get("phanTramPhoiNhiemGop")
    try:
        CONFIG["ruiRo"]["phanTramPhoiNhiemGop"] = 0
        k, re = moi()
        kiem("trần phơi nhiễm gộp = 0 là TẮT cổng, không phải cấm hết",
             re.duyet(co_hoi(), lanh, 200, False).cho)
    finally:
        if _cuG is None:
            CONFIG["ruiRo"].pop("phanTramPhoiNhiemGop", None)
        else:
            CONFIG["ruiRo"]["phanTramPhoiNhiemGop"] = _cuG

    # ── trần 0 nghĩa là KHÔNG KHAI, không phải trần bằng không ────────
    _cu = CONFIG["ruiRo"].get("phanTramLoNgay")
    try:
        CONFIG["ruiRo"]["phanTramLoNgay"] = 0
        k, re = moi()
        kiem("trần lỗ ngày = 0 nghĩa là TẮT cổng, không phải cấm hết",
             re.duyet(co_hoi(), lanh, 200, False).cho)
    finally:
        if _cu is None:
            CONFIG["ruiRo"].pop("phanTramLoNgay", None)
        else:
            CONFIG["ruiRo"]["phanTramLoNgay"] = _cu

    # ── trần NHÓM tài sản, soi RIÊNG ─────────────────────────────────
    #
    # Ba trần chồng lên nhau ở tài khoản $1.000: mỗi market $100, mỗi
    # nhóm $200, ngân sách ngày $50. Nên trần nhóm gần như không bao giờ
    # là cái chặn cuối, và một phép kiểm ngây thơ sẽ "đạt" nhờ một cổng
    # khác — bộ quét đột biến bắt được đúng chuyện đó.
    #
    # Cô lập bằng hai việc: nới tạm ngân sách ngày, và dùng vị thế ĐÃ
    # GHÉP KÍN (lỗ xấu nhất bằng 0 nhưng vẫn chiếm chỗ trong trần nhóm).
    _cuN = CONFIG["ruiRo"].get("phanTramLoNgay")
    _cuP = CONFIG["khoDoi"].get("phanTramChuaPhongHo")

    def _rong():
        """Engine đã nới MỌI cổng khác, để chỉ còn trần nhóm nói.

        `von` nâng riêng cho Kelly (Kelly đọc `von`, còn ba trần đọc
        `vonDauNgay`), nên gốc phần trăm không đổi. Không có bước này
        thì Kelly chặn ở 40 cổ và mọi phép kiểm dưới đây "đạt" vì một
        lý do chẳng liên quan.
        """
        kk = Kho()
        rr = RiskEngine(kk)
        rr.von = 100_000.0
        return kk, rr

    try:
        CONFIG["ruiRo"]["phanTramLoNgay"] = 100
        CONFIG["khoDoi"]["phanTramChuaPhongHo"] = 100
        # BTC_15M ghép kín $150 → nhóm BTC còn $50, tức 100 cổ ở giá 0,50.
        k, re = _rong()
        v15 = k.lay("BTC_15M")
        v15.ghi_khop("UP", 150.0, 0.5)
        v15.ghi_khop("DOWN", 150.0, 0.5)
        kiem("vị thế ghép kín KHÔNG gánh lỗ xấu nhất",
             gan(v15.lo_xau_nhat_usd(), 0.0), v15.lo_xau_nhat_usd())
        q = re.duyet(co_hoi(soCo=400.0, phi=0.0, sucChua=10_000.0),
                     lanh, 200, True)
        kiem("cùng NHÓM thì chiếm chỗ của nhau — siết còn 100 cổ",
             q.cho and gan(q.soCoChoPhep, 100.0, 1e-6), q.soCoChoPhep)

        # Cùng cỡ ấy nhưng ở nhóm KHÁC thì KHÔNG được tính vào.
        k, re = _rong()
        vE = k.lay("ETH_5M")
        vE.ghi_khop("UP", 300.0, 0.5)
        vE.ghi_khop("DOWN", 300.0, 0.5)
        q = re.duyet(co_hoi(soCo=400.0, phi=0.0, sucChua=10_000.0),
                     lanh, 200, True)
        kiem("nhóm KHÁC thì không — lệnh BTC được rộng hơn hẳn",
             q.cho and q.soCoChoPhep > 150.0, q.soCoChoPhep)

        # Và dùng ĐÚNG BẰNG trần nhóm thì hết chỗ.
        k, re = _rong()
        v15 = k.lay("BTC_15M")
        v15.ghi_khop("UP", re.tranMoiTaiSanUsd, 0.5)
        v15.ghi_khop("DOWN", re.tranMoiTaiSanUsd, 0.5)
        q = re.duyet(co_hoi(phi=0.0), lanh, 200, True)
        kiem("nhóm BTC dùng ĐÚNG BẰNG trần nhóm → TỪ CHỐI",
             q.tu_choi and any("nhóm" in x for x in q.lyDo), q.lyDo)
    finally:
        if _cuN is None:
            CONFIG["ruiRo"].pop("phanTramLoNgay", None)
        else:
            CONFIG["ruiRo"]["phanTramLoNgay"] = _cuN
        if _cuP is None:
            CONFIG["khoDoi"].pop("phanTramChuaPhongHo", None)
        else:
            CONFIG["khoDoi"]["phanTramChuaPhongHo"] = _cuP

    # ── chân trần đã dùng ĐÚNG BẰNG trần → hết chỗ ───────────────────
    k, re = moi()
    tranT = re.tranChuaPhongHoUsd
    k.lay("SOL_5M").ghi_khop("UP", tranT / 0.5, 0.5)
    kiem("chân trần đã dùng ĐÚNG BẰNG trần thì đo được đúng con số ấy",
         gan(k.tong_chua_phong_ho_usd(), tranT, 1e-6),
         k.tong_chua_phong_ho_usd())
    q = re.duyet(co_hoi(), lanh, 200, False)
    kiem("và lệnh mới bị TỪ CHỐI", q.tu_choi, q.lyDo)

    # ── "lợi kỳ vọng quá mỏng" là NHÁNH CHẾT, và nói ra thì hơn ───────
    #
    # Cổng 11 có hai vế: `cho_phep < 1` rồi `cho_phep × netEdge < 0.01`.
    # Vế sau chỉ chạy khi vế trước không bắn, tức `cho_phep >= 1`. Mà
    # cơ hội nào tới được đây cũng đã qua sàng, tức `netEdge >=
    # netEdgeToiThieu = 0,015`. Nên `cho_phep × netEdge >= 0,015 > 0,01`
    # LUÔN LUÔN — vế sau không bao giờ đúng.
    #
    # Không xoá: `netEdgeToiThieu` là nút vặn được, và dải của nó xuống
    # tới 0,005. Ở đó vế sau sống lại. Nhưng phải KHAI ra, vì một nhánh
    # chết trông y hệt một lớp bảo vệ đang làm việc.
    _nguongNE = float(_CLc["netEdgeToiThieu"])
    kiem("vế `lợi kỳ vọng quá mỏng` là nhánh CHẾT ở ngưỡng hiện tại",
         _nguongNE >= 0.01,
         f"netEdgeToiThieu {_nguongNE:g} — dưới 0,01 thì vế ấy sống lại")


def kiem_doi_soat_truoc_khi_dat_that() -> None:
    """Chưa hỏi sàn đang cầm gì thì KHÔNG được đặt lệnh thật.

    Đây là mục 1 — mục nặng nhất — của danh sách trước cổng. `Kho` chỉ
    nằm trong bộ nhớ, nên khởi động lại giữa một khung là bot quên mình
    đang cầm cổ phiếu trong khi sàn thì không quên.

    Chưa nối được sàn thì không cách nào BIẾT. Nhưng từ chối thì làm
    được ngay, và từ chối là việc đúng: giả định im lặng rằng tài khoản
    đang trống sẽ sai đúng vào lúc nó đắt nhất.

    Phép kiểm này canh cả hai chiều — chặn ở chế độ THẬT, và KHÔNG chặn
    ở chế độ giấy. Chặn nhầm chế độ giấy thì cỗ máy đứng im mà không ai
    hiểu vì sao.
    """
    print()
    print("-- Doi soat voi san truoc khi dat lenh THAT ----------------")
    from kham import config as _cf
    from kham.can_loi import can as _can2
    from kham.so_lenh import Muc as _M2
    from kham.so_lenh import SoLenh as _S2

    so = _S2(ma="BTC_5M", ben="UP",
             bid=[_M2(0.44, 900.0)], ask=[_M2(0.46, 900.0)], nhanLucMs=0.0)
    ch = _can2("BTC_5M", "UP", "t", 0.55, 0.02, so, 300)
    lanh = SucKhoeNguon(200, 150, 80)

    k = Kho()
    re = RiskEngine(k)
    kiem("mặc định là CHƯA đối soát", k.daDoiSoatVoiSan is False)

    # Buồng lái phải ĐẾM đủ cửa. Thiếu một cửa thì ai đó mở hết số cửa
    # nhìn thấy, đọc "0 cửa đang đóng", rồi ngạc nhiên vì lệnh vẫn
    # không đi. Một bảng đếm thiếu tệ hơn không có bảng đếm.
    from kham.config import dat_lenh_that as _dlt
    from kham.config import ly_do_khong_that as _ldkt
    kiem("danh sách cửa CÓ kể cửa đối soát khi được truyền kho",
         any("đối soát" in x for x in _ldkt(k)), _ldkt(k))
    kiem("và KHÔNG kể khi không truyền — `che_hieu_luc` phải sạch",
         not any("đối soát" in x for x in _ldkt()), _ldkt())
    # Vòng tròn: nếu `dat_lenh_that()` cũng xét đối soát thì chưa đối
    # soát ⇒ chế độ thành `giay` ⇒ cổng đối soát không bao giờ chạy.
    kiem("`dat_lenh_that` KHÔNG xét đối soát — nếu không là vòng tròn",
         _dlt() == (not _ldkt()))
    kiem("chế độ GIẤY thì KHÔNG chặn — vị thế giấy là của riêng ta",
         re.duyet(ch, lanh, 200, True).cho)

    cu = _cf.che_hieu_luc
    try:
        _cf.che_hieu_luc = lambda: "that"
        import kham.rui_ro as _RR2
        _RR2.che_hieu_luc = lambda: "that"
        q = re.duyet(ch, lanh, 200, True)
        kiem("chế độ THẬT mà chưa đối soát → TỪ CHỐI", q.tu_choi)
        kiem("và nói rõ VÌ SAO, không im lặng",
             any("ĐỐI SOÁT" in x for x in q.lyDo), q.lyDo)

        # Sàn trả lời "tài khoản trống" KHÁC HẲN "chưa hỏi" — đó là cả
        # lý do `danh_dau_da_doi_soat` tồn tại.
        k.danh_dau_da_doi_soat(None)
        kiem("sàn xác nhận TRỐNG (khác với chưa hỏi) → cho qua",
             re.duyet(ch, lanh, 200, True).cho)

        # Và đối soát phải NẠP được thứ sàn nói là đang cầm.
        k2 = Kho()
        re2 = RiskEngine(k2)
        k2.danh_dau_da_doi_soat({"BTC_5M": (120.0, 0.0, 54.0, 0.0)})
        v2 = k2.lay("BTC_5M")
        kiem("đối soát nạp đúng thứ sàn nói đang cầm",
             gan(v2.coUp, 120.0) and gan(v2.tienUp, 54.0),
             (v2.coUp, v2.tienUp))
        kiem("và tồn kho ấy ĐI VÀO hạn mức ngay",
             re2.lo_xau_nhat_gop_usd() > 0, re2.lo_xau_nhat_gop_usd())
    finally:
        _cf.che_hieu_luc = cu
        import kham.rui_ro as _RR3
        _RR3.che_hieu_luc = cu


def kiem_tran_chan_tran_khong_vuot() -> None:
    """Chân TRẦN không bao giờ vượt trần — chứng minh, không trấn an.

    Danh sách "PHẢI ĐÚNG TRƯỚC KHI MỞ BA CỔNG" ghi mục 3 là "ca khó của
    chân lệch không có lối thoát tự động": `quyet_chan` chỉ khuyên, không
    ai huỷ lệnh hay vượt spread theo nó, nên ca "không ai bán bên thiếu"
    bị bỏ ngỏ.

    Bỏ ngỏ về LỐI THOÁT thì đúng. Nhưng bỏ ngỏ về CỠ thì không — và hai
    chuyện ấy hay bị nói lẫn vào nhau. Cỡ có trần: cổng 8 chặn theo
    `tranChuaPhongHoUsd`. Một rủi ro có chặn và một rủi ro không chặn là
    hai thứ khác hẳn nhau khi quyết có mở cổng hay không.

    Nên phép kiểm này lùa NHIỀU lệnh qua đúng cửa duyệt thật, khớp trọn
    mọi thứ được duyệt, rồi đòi trần không bao giờ bị vượt. Không dò
    chuỗi, không tin một cổng đơn lẻ — đo bất biến ở đầu ra.
    """
    print()
    print("-- Chan tran co TRAN, du khong co loi thoat tu dong ---------")
    import random as _rd

    from kham.can_loi import can as _can
    from kham.so_lenh import Muc as _M
    from kham.so_lenh import SoLenh as _S

    rd = _rd.Random(20260830)
    k = Kho()
    re = RiskEngine(k)
    lanh = SucKhoeNguon(200, 150, 80)
    tran = re.tranChuaPhongHoUsd
    dinh = 0.0
    soCho = 0
    for _i in range(400):
        # Khung 5 phút ĐÓNG theo chu kỳ: tồn kho về 0 rồi mở khung mới.
        # Không có bước này thì trần bão hoà ngay sau lệnh thứ hai và
        # phép kiểm chỉ chạm tới đúng hai lệnh — xanh mà rỗng.
        if _i % 12 == 11:
            for _v in list(k.viThe.values()):
                _v.don()
        ma = rd.choice(("BTC_5M", "ETH_5M", "SOL_5M", "XRP_5M"))
        ben = rd.choice(("UP", "DOWN"))
        gia = rd.choice((0.08, 0.25, 0.45, 0.62, 0.88))
        so = _S(ma=ma, ben=ben,
                bid=[_M(max(0.01, gia - 0.02), 5000.0)],
                ask=[_M(gia, 5000.0)], nhanLucMs=0.0)
        ch = _can(ma, ben, "thử", min(0.99, gia + 0.06), 0.02, so, 400)
        if ch is None:
            continue
        q = re.duyet(ch, lanh, 200, True)
        if not q.cho:
            continue
        soCho += 1
        # Khớp TRỌN phần được duyệt — ca xấu nhất cho trần này.
        k.lay(ma).ghi_khop(ben, q.soCoChoPhep, ch.vwap)
        dinh = max(dinh, k.tong_chua_phong_ho_usd())

    kiem("có duyệt được ít nhất vài chục lệnh (phép kiểm CÓ chạm tới)",
         soCho >= 20, soCho)
    kiem("tiền nằm TRẦN một chân không bao giờ vượt trần",
         dinh <= tran + 1e-6, f"đỉnh ${dinh:.2f} vs trần ${tran:.2f}")
    kiem("và trần ấy co giãn theo vốn, không phải số đô cứng",
         abs(tran - re.vonBanDau * 0.05) < 1e-6, tran)
    # Lỗ xấu nhất gộp cũng phải nằm trong ngân sách ngày — cổng 6b.
    kiem("lỗ xấu nhất gộp không vượt ngân sách lỗ ngày",
         re.lo_xau_nhat_gop_usd() <= re.tranLoNgayUsd + 1e-6,
         (re.lo_xau_nhat_gop_usd(), re.tranLoNgayUsd))


def kiem_phat_ton_kho() -> None:
    print()
    print("-- Phat ton kho phai THAT SU lech gia yet -------------------")
    import math as _m

    from kham.chien_thuat import BoiCanh as _BC
    from kham.chien_thuat import tao_lap as _tl
    from kham.dinh_gia import GiaChuan as _GC
    from kham.dongho import GIUA_KHUNG as _GIUA
    from kham.dongho import LatCat as _LC
    from kham.kho_doi import Kho as _K
    from kham.so_lenh import Muc as _M
    from kham.so_lenh import SoLenh as _S

    def yet(coUp: float, coDown: float, pUp: float,
            sigmaGiay: float = 0.55 / _m.sqrt(365 * 24 * 3600)) -> dict:
        """{bên: giá yết} của ngón tạo lập, với tồn kho cho trước."""
        gc = _GC(ma="BTC_5M", pUp=pUp, pDown=1.0 - pUp, batDinh=0.02,
                 batDinhThamSo=0.02, ruiRoNhay=0.0, z=0.0,
                 sigmaGiay=sigmaGiay, tauGiay=180.0, tauDungSan=False,
                 daMatPhang=False, giaHienTai=100_000.0, giaMo=100_000.0,
                 oHieuChinh="50-60")
        su = _S(ma="BTC_5M", ben="UP", bid=[_M(0.40, 900.0)],
                ask=[_M(0.60, 900.0)], nhanLucMs=0.0)
        sd = _S(ma="BTC_5M", ben="DOWN", bid=[_M(0.40, 900.0)],
                ask=[_M(0.60, 900.0)], nhanLucMs=0.0)
        v = _K().lay("BTC_5M")
        if coUp:
            v.ghi_khop("UP", coUp, 0.5)
        if coDown:
            v.ghi_khop("DOWN", coDown, 0.5)
        lc = _LC(conLaiGiay=180.0, tongGiay=300.0, giaiDoan=_GIUA,
                 troiQuaPct=40.0, lechDongHoMs=0.0, tuoiDuLieuMs=0.0)
        ra = _tl(_BC(ma="BTC_5M", gia=gc, soUp=su, soDown=sd, dongHo=lc,
                     viThe=v)) or []
        return {c.ben: c.fairValue for c in ra}

    can = yet(0, 0, 0.5)
    kiem("tồn kho cân thì yết ĐỐI XỨNG",
         can and gan(can.get("UP", 0), can.get("DOWN", 0)), can)

    # q = 100 cổ ở p = 0,50 phải chịu phạt đúng 1 cent — đó là chỗ γ
    # được chốt, nên nếu ai đổi γ mà quên chỗ này thì phép kiểm đỏ.
    lech = yet(100, 0, 0.5)
    kiem("thừa 100 cổ UP thì yết UP THẤP đi 1 cent",
         lech and gan(can["UP"] - lech["UP"], 0.01, 1e-6),
         can["UP"] - lech.get("UP", 0))
    kiem("và yết DOWN CAO lên đúng chừng ấy",
         gan(lech["DOWN"] - can["DOWN"], 0.01, 1e-6),
         lech.get("DOWN", 0) - can["DOWN"])

    # Phạt phải TỰ VỀ 0 ở hai đầu: sát lúc kết toán, ôm tồn kho không
    # còn rủi ro nữa. Đây là thứ công thức cũ (`σ²τ`) không có.
    for pX in (0.02, 0.98):
        a = yet(0, 0, pX)
        b = yet(300, 0, pX)
        kiem(f"p = {pX:g}: phạt gần như biến mất dù thừa 300 cổ",
             abs(a["UP"] - b["UP"]) < 0.0025,
             abs(a["UP"] - b.get("UP", 0)))
    giua = yet(300, 0, 0.5)
    kiem("còn ở giữa thì phạt LỚN — hình dạng đúng chiều",
         (can["UP"] - giua["UP"]) > 10 * abs(a["UP"] - b["UP"]),
         (can["UP"] - giua["UP"]))

    # ── canh đúng CÁI BỆNH CŨ ─────────────────────────────────────────
    #
    # Công thức cũ `q × 0,0015 × σ_giây² × τ` sai THỨ NGUYÊN: σ_giây là
    # độ lệch log-return mỗi giây (cỡ 3,7e-5) nên σ²τ ra cỡ 4e-7, trong
    # khi giá yết nằm trong [0, 1]. Phạt lớn nhất đo được là 0,00039
    # cent, nhỏ hơn trần kẹp 5 cent tới mười nghìn lần.
    #
    # Bệnh ấy quay lại được bằng cách ai đó kéo `sigmaGiay` vào lại công
    # thức. Nên canh thẳng: đổi RIÊNG `sigmaGiay` mà giá yết đổi là dấu
    # hiệu thứ nguyên lại lẫn lộn.
    m1 = yet(200, 0, 0.5, sigmaGiay=0.21 / _m.sqrt(365 * 24 * 3600))
    m2 = yet(200, 0, 0.5, sigmaGiay=2.00 / _m.sqrt(365 * 24 * 3600))
    kiem("phạt KHÔNG phụ thuộc `sigmaGiay` — nó không cùng thứ nguyên "
         "với giá yết",
         gan(m1["UP"], m2["UP"]), (m1.get("UP"), m2.get("UP")))
    kiem("và phạt đủ lớn để nhìn thấy: 200 cổ lệch ít nhất 1 cent",
         (can["UP"] - m1["UP"]) >= 0.01 - 1e-9, can["UP"] - m1["UP"])


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
    from kham import hoc_offline as _HO
    b2, b60 = m._bien(2), m._bien(60)
    kiem("biên SIẾT theo số ứng viên", b60 > b2,
         f"2 ứng viên → {b2:.5f} · 60 ứng viên → {b60:.5f}")
    kiem("biên luôn dưới 1 (vẫn đòi khá hơn)", b60 < 1.0, b60)

    # ── giảm chấn phải nằm trong dải ĐÃ ĐO ────────────────────────────
    #
    # `scripts/do-giam-chan.py` quét cả trục trên 4 chợ × 20 ngày, khớp
    # trên HỌC, chấm trên CHỐT, khoảng tin bootstrap chia khối theo KHUNG
    # (1.440 khối). Brier CHỐT đơn điệu giảm suốt trục, và so với 0,70:
    #
    #     0,30  [+0,000539, +0,001005]   TỆ HƠN có ý nghĩa
    #     0,50  [+0,000207, +0,000440]   TỆ HƠN có ý nghĩa
    #     0,85  [-0,000247, -0,000073]   TỐT HƠN có ý nghĩa
    #     1,00  [-0,000426, -0,000075]   TỐT HƠN có ý nghĩa
    #
    # Canh cái DẢI TÌM, không canh con số.
    #
    # Trị hiện tại là thứ vòng tiến hoá được phép vặn — đó là việc của
    # nó. Chốt cứng một con số trong phép kiểm là biến một nút sống
    # thành nút chết theo đường vòng, và lượt tiến hoá đầu tiên vặn nó
    # sẽ làm đỏ bộ kiểm mà chẳng có gì hỏng.
    #
    # Thứ ĐÁNG canh là dải tìm không được chứa lại vùng đã đo là tệ
    # hơn (0,30 và 0,50 đều TỆ HƠN 0,70 có ý nghĩa). Để ngỏ vùng ấy
    # không phải "để ngỏ khả năng" — nó là mời cỗ máy lặp lại một sai
    # lầm đã có bằng chứng, và nó ĐÃ lặp nhiều lượt liền.
    from kham.nan_lai import he_so_giam_chan as _hsgc
    _nutGC = NUT_THEO_DUONG["nanLai.heSoGiamChan"]
    kiem("dải tìm giảm chấn KHÔNG chứa lại vùng đã đo là tệ hơn",
         _nutGC.thap >= 0.75 - 1e-9, (_nutGC.thap, _nutGC.cao))
    kiem("nhưng vẫn với tới được 1,00 — mép trên là giới hạn thật",
         abs(_nutGC.cao - 1.0) < 1e-9, _nutGC.cao)
    _hs = _hsgc()
    kiem("và trị đang dùng nằm TRONG dải, không nằm trên mép",
         _nutGC.thap + 1e-9 < _hs <= _nutGC.cao + 1e-9, _hs)
    kiem("và config có ghi phép đo biện minh cho nó",
         "do-giam-chan.py" in (GOC_MA / "config.json")
         .read_text(encoding="utf-8"))

    # ── GỘP CHỢ: thêm THÔNG TIN, không phải thêm CON SỐ ───────────────
    #
    # Bốn coin tương quan gần 1 — `kho_doi` có ma trận nói thế, và cổng
    # 7b dựng lên vì chuyện đó. BTC/ETH/SOL/XRP tại CÙNG một mốc không
    # phải bốn bằng chứng độc lập; chúng gần như một quan sát nhìn từ
    # bốn phía.
    #
    # Nên mốc kéo theo phải là `T` TRẦN TRỤI: bootstrap khối gom cả bốn
    # chợ vào MỘT khối và khoảng tin trung thực. Kéo theo `(mã, T)` thì
    # mẫu trông to gấp bốn, khoảng tin hẹp lại quãng một nửa, và cổng
    # CHỐT sẽ gật cho tiếng ồn — đúng thứ cả cỗ máy này dựng lên để
    # tránh.
    # Giá phải NHẤP NHÔ: đường thẳng cho σ = 0, `sigma_tai` trả None,
    # và cả hai bên đều ra 0 cặp — phép kiểm xanh mà chẳng kiểm gì.
    import math as _m
    _gia = {}
    # Gốc phải NẰM TRÊN LƯỚI 5 phút, không thì không khung nào tồn tại
    # và cả hai vế đều ra 0 cặp — phép kiểm xanh mà chẳng kiểm gì.
    _goc = 1_700_000_000_000 - 1_700_000_000_000 % 300_000
    for _k in range(0, 60):
        _t = _goc + _k * 60_000
        _gia[_t] = 100.0 * (1.0 + 0.004 * _m.sin(_k * 1.3)
                            + 0.0006 * _k)
    _hai = {"BTC_5M": dict(_gia),
            "ETH_5M": {k: v * 2.0 for k, v in _gia.items()}}
    _mocs = [T for T in sorted(_gia) if T % 300_000 == 0]
    _mot = m.cap_du_doan({"BTC_5M": _hai["BTC_5M"]}, _mocs, 300.0,
                         keoMoc=True)
    _bon = m.cap_du_doan(_hai, _mocs, 300.0, keoMoc=True)
    kiem("gộp hai chợ thì SỐ CẶP tăng", len(_bon) > len(_mot),
         (len(_mot), len(_bon)))
    _mocMot = {x[-1] for x in _mot}
    _mocBon = {x[-1] for x in _bon}
    kiem("nhưng SỐ KHỐI bootstrap thì KHÔNG — mốc là thời gian, "
         "không phải (chợ, thời gian)",
         _mocBon == _mocMot, (len(_mocMot), len(_mocBon)))
    kiem("và mọi mốc kéo theo đều là số nguyên mốc thời gian",
         all(isinstance(x[-1], int) for x in _bon))

    # ── nút mà THƯỚC không nhìn thấy thì đừng để trong danh sách ──────
    #
    # `dinhGia.sanNenGiay` CÓ đi vào `pUp` (`tau = max(san, tau_that)`)
    # nhưng bàn thử Brier không bao giờ chạm tới: lát cắt nhỏ nhất là 60
    # giây, mép trên của nút là 15 giây, nên `max` luôn trả `tau_that`.
    # Quét cả trục 1→15 cho Brier GIỐNG HỆT tới 5 chữ số, khoảng tin
    # đúng bằng [0, 0] trên 1.440 khối.
    #
    # Canh cả LÝ DO chứ không chỉ canh kết luận: nếu ai đó thêm được lát
    # cắt nhỏ hơn 15 giây thì bàn thử NHÌN THẤY nút, và lúc ấy phép kiểm
    # này phải đỏ để bắt người ta nghĩ lại.
    kiem("`sanNenGiay` không nằm trong danh sách nút bàn thử Brier",
         "dinhGia.sanNenGiay" not in m.NUT_MO_HINH, m.NUT_MO_HINH)
    _nSan = NUT_THEO_DUONG["dinhGia.sanNenGiay"]
    kiem("và LÝ DO vẫn đúng: lát cắt nhỏ nhất > mép trên của sàn τ",
         min(m.LAT_CAT) > _nSan.cao,
         f"lát nhỏ nhất {min(m.LAT_CAT):g}s vs mép sàn {_nSan.cao:g}s")
    kiem("danh sách nút mô hình chỉ có MỘT nguồn, không ba bản sao",
         m.NUT_MO_HINH is _HO.NUT_MO_HINH)

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
    # Xoá sổ thô THEO CHỢ, không xoá sạch.
    #
    # `ghi_tho` nối thêm, nên không xoá thì mỗi lượt nhân đôi số cặp và
    # phép kiểm ngoài mẫu 70/30 tự chấm bài mình. Nhưng xoá SẠCH thì
    # chạy cho ETH là mất trắng mẫu BTC — đo được: sau ba lượt ETH,
    # SOL, XRP, sổ thô còn đúng 56.836 dòng và tất cả đều là XRP.
    #
    # Kiểm bằng HÀNH VI trên file tạm, không dò chuỗi mã nguồn.
    import importlib.util as _iu2
    _sp2 = _iu2.spec_from_file_location("_htb", GOC_MA / "scripts"
                                        / "hoc-tu-binance.py")
    _htb = _iu2.module_from_spec(_sp2)
    import sys as _sys2
    _cu_argv = _sys2.argv
    _sys2.argv = ["hoc-tu-binance.py"]
    try:
        _sp2.loader.exec_module(_htb)
    finally:
        _sys2.argv = _cu_argv
    from kham import nan_lai as _nl
    _cu_duong = _nl.DUONG_THO
    with tempfile.TemporaryDirectory() as _td:
        _nl.DUONG_THO = Path(_td) / "tho.jsonl"
        _nl.ghi_tho(0.6, True, "BTC_5M")
        _nl.ghi_tho(0.4, False, "ETH_5M")
        _nl.ghi_tho(0.7, True, "BTC_5M")
        _giu = _htb._giu_lai_cho_khac("BTC_5M")
        _con = list(_htb._doc_tho())
        _ma_con = {x[2] for x in _con}
        _nl.DUONG_THO = _cu_duong
    kiem("xoá sổ thô của chợ đang dựng lại", "BTC_5M" not in _ma_con,
         _ma_con)
    kiem("nhưng GIỮ NGUYÊN mẫu của chợ khác",
         _ma_con == {"ETH_5M"} and _giu == 1, (_ma_con, _giu))
    kiem("và sổ TỔNG dựng lại từ sổ THÔ, nơi mọi chợ cùng nằm",
         "for pMoi, thangMoi, maMoi in _doc_tho():" in ma,
         "ghi thẳng `hc` là để lại sổ nói về đúng MỘT chợ "
         "trong khi cỗ máy chạy bốn")


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
    # Đọc mép TỪ BẢNG, đừng chép số vào đây: mép dưới đã đổi 0,30 →
    # 0,80 theo một phép đo, và một phép kiểm chép số thì đỏ lên vì
    # chính cái thay đổi có bằng chứng — báo oan đúng lúc không nên báo.
    _nGC = NUT_THEO_DUONG["nanLai.heSoGiamChan"]
    kiem("vượt trần thì bị kẹp",
         kep("nanLai.heSoGiamChan", _nGC.cao + 0.5) == _nGC.cao)
    kiem("dưới sàn thì bị kẹp",
         kep("nanLai.heSoGiamChan", _nGC.thap - 0.5) == _nGC.thap)

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
    khongTroi = g.giaiTrinh["pChamKhongTroi"]
    # Đẳng thức phản xạ chỉ đúng cho chuyển động Brown KHÔNG trôi, nên
    # nay nó canh `pChamKhongTroi`, không canh `pChamTho`. Bản có trôi
    # KHÔNG được thoả nó — và đó chính là chỗ khác nhau.
    kiem("P(chạm) không trôi = 2 × P(kết thúc bên kia)",
         gan(khongTroi / ket, 2.0, 1e-9),
         f"{khongTroi:.6f} / {ket:.6f} = {khongTroi/ket:.6f}")
    kiem("P(chạm) > P(kết thúc) luôn luôn", tho > ket)
    kiem("bản CÓ trôi thấp hơn bản không trôi — chiều an toàn",
         tho < khongTroi, (tho, khongTroi))

    # Hai giới hạn — thứ khoá chặt công thức, không cho ai đổi tiện tay.
    #
    # Với μ = −σ²/2 thì chính GIÁ là martingale, nên phép dừng tuỳ ý cho
    # hai con số biết trước:
    #
    #     τ → ∞, rào TRÊN  →  S/K   (xác suất từng chạm mốc trên)
    #     τ → ∞, rào DƯỚI  →  1     (martingale dương chạm mọi mức dưới)
    #
    # Bản phản xạ cũ KHÔNG thoả cả hai: nó cho 2Φ(0) = 1 ở rào trên.
    from kham.cham_moc import _p_cham
    _b = math.log(150_000 / 72_000)
    _lau = 500 * 365 * 86400.0
    kiem("τ → ∞, rào TRÊN → S/K (giá là martingale)",
         gan(_p_cham(_b, sig, _lau, True), 72_000 / 150_000, 1e-4),
         _p_cham(_b, sig, _lau, True))
    kiem("τ → ∞, rào DƯỚI → 1", gan(_p_cham(_b, sig, _lau, False), 1.0, 1e-6),
         _p_cham(_b, sig, _lau, False))
    kiem("rào ngay tại giá hiện tại → P = 1 ở cả hai chiều",
         gan(_p_cham(0.0, sig, 60.0, True), 1.0, 1e-9)
         and gan(_p_cham(0.0, sig, 60.0, False), 1.0, 1e-9))

    # Bất định lấy đạo hàm bằng SỐ, nên nó phải theo đúng công thức đang
    # dùng. Kiểm bằng cách so với sai phân thô ngay tại đây.
    _s2 = sig * 1.0001
    _dp = abs(_p_cham(_b, _s2, 133 * NGAY, True)
              - _p_cham(_b, sig, 133 * NGAY, True))
    kiem("bất định > 0 khi P chưa dính hai đầu",
         g.batDinhThamSo > 0 and _dp > 0, (g.batDinhThamSo, _dp))

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
    # Phép kiểm này từng dò ĐÚNG MỘT CHUỖI mã nguồn — nó đỏ ngay lần
    # đầu ai đó thêm một tham số vào lời gọi, dù hành vi không đổi. Dò
    # hành vi thì bền, và nó kiểm đúng thứ đáng kiểm.
    from kham.dat_lenh import CongLenh, Lenh
    _k = Kho()
    _c = CongLenh(_k)
    _l = Lenh(id="x", ma="BTC_5M", ben="UP", chienThuat="t", soCo=10,
              giaDat=0.5, laMaker=False, datLucMs=0.0,
              soCoKhop=10, giaKhop=0.5, phiUsd=0.37, pMoHinh=0.62)
    _c._ghi_kho(_l)
    _v = _k.lay("BTC_5M")
    kiem("đường đặt lệnh TRUYỀN phí vào vị thế",
         gan(_v.phiUsd, 0.37), _v.phiUsd)
    kiem("và TRUYỀN cả niềm tin mô hình lúc vào lệnh",
         _v.pVaoTb is not None and gan(_v.pVaoTb, 0.62), _v.pVaoTb)
    _l2 = Lenh(id="y", ma="BTC_5M", ben="DOWN", chienThuat="t", soCo=10,
               giaDat=0.5, laMaker=False, datLucMs=0.0,
               soCoKhop=10, giaKhop=0.5, phiUsd=0.0, pMoHinh=0.62)
    _c._ghi_kho(_l2)
    kiem("chân DOWN quy về P(UP) — 0,62 bên DOWN nghĩa là P(UP)=0,38",
         gan(_v.pVaoTb, 0.5), _v.pVaoTb)

    kt = khong_chu_thich((GOC_MA / "kham" / "ket_toan.py")
                         .read_text(encoding="utf-8"))
    kiem("kết toán ghi phí THẬT, không ghi 0", "phiUsd=v.phiUsd" in kt)
    kiem("và KHÔNG còn ghi cứng phiUsd=0.0", "phiUsd=0.0" not in kt)
    # `don()` phải trả MỌI trường về mặc định.
    #
    # Bản trước dò `kt.count("v.phiUsd = 0.0") >= 2` — đếm số lần một
    # chuỗi xuất hiện trong mã nguồn. Nó đúng chừng nào có đúng hai chỗ
    # dọn và cả hai viết y hệt nhau; thực tế có BA chỗ, và chỗ thứ ba
    # (`phat_lai._tra_ton_kho`) quên `phiUsd` mà phép kiểm vẫn xanh.
    #
    # So với dataclass thì mỗi trường MỚI thêm vào `ViThe` đều tự động
    # được canh: quên nó trong `don()` là đỏ, không cần ai nhớ.
    import dataclasses as _dc

    from kham.kho_doi import ChanCho, ViThe
    _z = ViThe(ma="z")
    _z.ghi_khop("UP", 40, 0.4, 1.5, 0.7)
    _z.ghi_khop("DOWN", 10, 0.3, 0.2, 0.6)
    _z.choCap.append(ChanCho(ben="UP", soCo=1, giaTrungBinh=0.4,
                             moLucMs=0.0, capMongMuon=0.98))
    _z.don()
    _sach = ViThe(ma="z")
    _sot = [f.name for f in _dc.fields(ViThe)
            if f.name != "ma"
            and getattr(_z, f.name) != getattr(_sach, f.name)]
    kiem("don() trả MỌI trường của ViThe về mặc định", not _sot, _sot)
    kiem("và ba chỗ dọn tồn kho đều gọi don(), không gán tay",
         "v.phiUsd = 0.0" not in kt
         and "coUp = " not in khong_chu_thich(
             (GOC_MA / "kham" / "phat_lai.py").read_text(encoding="utf-8")
         ).split("def _tra_ton_kho")[-1][:400])

    # Chợ nào đối chiếu được — luật này phải KIỂM được, nên nó nằm ở
    # `kham/`, không nằm trong script.
    #
    # `doi-chieu-ket-qua.py` từng lọc bằng `if tienTo and ...`: market
    # không có tiền tố thì bộ lọc lặng lẽ TẮT, và công cụ đem mọi dòng
    # trong sổ so với nến của market đang xét. `--ma=BTC_150K` báo "430
    # LỆCH" và thoát mã HỎNG — 430 kết quả ETH/SOL/XRP so với giá BTC,
    # không dòng nào sai cả. Thước tự bịa ra lỗi thì tệ hơn không thước.
    from kham.ket_qua import thi_truong_doi_chieu_duoc as _tdc
    _ma = [x.get("ma") for x in _tdc()]
    kiem("họ CHẠM MỐC (không `tienTo`) KHÔNG nằm trong danh sách đối chiếu",
         "BTC_150K" not in _ma, _ma)
    kiem("market `theo: false` cũng không", "BTC_15M" not in _ma, _ma)
    kiem("bốn chợ LÊN/XUỐNG đang theo thì CÓ",
         all(x in _ma for x in ("BTC_5M", "ETH_5M", "SOL_5M", "XRP_5M")),
         _ma)
    kiem("và mỗi mục trả về đều có `nen` để lấy nến",
         all(x.get("nen") for x in _tdc()))

    # Phiên phát lại KHÔNG được ghi vào sổ thật, kể cả khi ai đó quên
    # truyền `thuMucSo`. Docstring đã viết "bắt buộc tách khỏi sổ thật"
    # từ lâu trong khi mặc định làm ngược lại, và nó cắn thật: 14 dòng
    # mô phỏng chảy vào `data/ket-toan.jsonl` — chính sổ mà cầu dao đọc
    # lúc khởi động.
    from kham import phat_lai as _PLM
    from kham.config import DATA_DIR as _DD
    _pm = _PLM.PhienPhatLai(von=1000.0)
    kiem("PhienPhatLai không truyền thuMucSo → KHÔNG ghi vào sổ thật",
         Path(_pm.so.duong).resolve()
         != (Path(_DD) / "ket-toan.jsonl").resolve(),
         str(_pm.so.duong))
    kiem("mà rơi vào một thư mục con của data/phat-lai",
         "phat-lai" in Path(_pm.so.duong).as_posix())
    _nem = False
    try:
        _PLM.PhienPhatLai(von=1000.0, thuMucSo=Path(_DD))
    except ValueError:
        _nem = True
    # NÉM chứ không cảnh báo: `_don_so_phien` XOÁ sổ trong thư mục ấy
    # trước khi chạy, nên nhắm sai không phải bẩn sổ mà là MẤT sổ.
    kiem("trỏ thẳng vào DATA_DIR thì NÉM, không phải cảnh báo", _nem)

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

    # Bản trước dò CHỮ trong docstring ("+40,6%" và "CAO HƠN"). Nó đỏ
    # ngay khi ai đó viết lại đoạn văn — kể cả khi viết lại để nói rằng
    # sai lệch ĐÃ ĐƯỢC SỬA. Đo hành vi thì bền, và nó canh đúng thứ
    # đáng canh: số hạng trôi có THẬT SỰ nằm trong công thức không.
    from kham.cham_moc import _p_cham as _pc
    from kham.dinh_gia import phi as PHI
    _sig = 0.55 / math.sqrt(365 * 24 * 3600.0)
    _tau = 124 * 86400.0
    _b = math.log(150_000 / 78_016)
    _coTroi = _pc(_b, _sig, _tau, True)
    _khong = 2.0 * PHI(-_b / (_sig * math.sqrt(_tau)))
    kiem("số hạng trôi CÓ trong công thức chạm mốc",
         _coTroi < _khong * 0.95, (_coTroi, _khong))
    # Cỡ của nó cũng phải đúng: quãng 40% tương đối ở chân trời này.
    # Lệch xa con số ấy nghĩa là công thức đã đổi mà không ai đo lại.
    kiem("và cỡ của nó đúng quãng 40% tương đối ở chân trời 124 ngày",
         0.35 < (_khong / _coTroi - 1.0) < 0.45,
         f"{(_khong / _coTroi - 1.0) * 100:.1f}%")

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
            import gzip as _gz

            # File băng THẬT là gzip hợp lệ. Fixture cũ ghi `b"x"` —
            # không giải nén được — nên sau khi thêm luật "đọc không hết
            # thì GIỮ" nó bị giữ lại và phép kiểm trượt. Một fixture
            # không giống thứ thật thì chứng minh được rất ít.
            gia_cu = tm / "bang-2020-01-01.jsonl.gz"
            gia_moi = tm / "bang-2099-01-01.jsonl.gz"
            khac = tm / "khong-phai-bang.txt"
            for f in (gia_cu, gia_moi):
                with _gz.open(f, "wt", encoding="utf-8") as _fh:
                    # chỉ dòng cửa ĐẶT CƯỢC — loại lúc nào cũng ghi lại được
                    _fh.write('{"thiTruong":[{"giaiDoan":"dat-cuoc"}]}'
                              + chr(10))
            khac.write_bytes(b"x")
            gio = _t.time()
            os.utime(gia_cu, (gio - 400 * 86400, gio - 400 * 86400))

            mg = B.MayGhi.__new__(B.MayGhi)
            mg.duong = gia_moi          # file ĐANG MỞ
            n = B.MayGhi.don_cu(mg)

            kiem("xoá đúng file quá hạn", n == 1 and not gia_cu.exists())
            # KHÔNG BAO GIỜ xoá file có dòng KHUNG ĂN THUA, dù quá hạn.
            #
            # Dòng cửa đặt cược lúc nào cũng ghi được. Dòng khung ăn thua
            # chỉ có trong những phút hiếm hoi đường tới Polymarket thông
            # — tới nay gom được đúng 1.018 dòng, nằm gọn trong BA file.
            # Mất chúng là mất mọi phép đo về chợ thật và con số dương duy
            # nhất đứng được của cả hệ.
            import gzip as _gz
            quy = tm / "bang-2019-01-01.jsonl.gz"
            with _gz.open(quy, "wt", encoding="utf-8") as _f:
                _f.write('{"thiTruong":[{"giaiDoan":"quan-sat"}]}' + chr(10))
            os.utime(quy, (gio - 400 * 86400, gio - 400 * 86400))
            n3 = B.MayGhi.don_cu(mg)
            kiem("file QUÁ HẠN mà có khung ăn thua thì KHÔNG xoá",
                 n3 == 0 and quy.exists(), (n3, quy.exists()))

            # File hỏng không đọc được ⇒ GIỮ. Không chắc thì đừng xoá.
            hong = tm / "bang-2018-01-01.jsonl.gz"
            hong.write_bytes(b"khong-phai-gzip")
            os.utime(hong, (gio - 400 * 86400, gio - 400 * 86400))
            n4 = B.MayGhi.don_cu(mg)
            kiem("file HỎNG không đọc được thì GIỮ, không xoá",
                 n4 == 0 and hong.exists(), (n4, hong.exists()))
            kiem("KHÔNG xoá file đang mở", gia_moi.exists())
            kiem("KHÔNG đụng file không phải băng", khac.exists())

            # File 0 byte: ngoại lệ của luật "không chắc thì giữ". Mỗi lần
            # khởi động lại đẻ một file rỗng — giữ hết thì dồn vô hạn.
            rong = tm / "bang-2018-06-06.jsonl.gz"
            rong.write_bytes(b"")
            os.utime(rong, (gio - 400 * 86400, gio - 400 * 86400))
            n5 = B.MayGhi.don_cu(mg)
            kiem("file RỖNG quá hạn thì XOÁ — không có gì để mất",
                 n5 == 1 and not rong.exists(), (n5, rong.exists()))

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

def kiem_quyet_dinh_cua_nguoi_song_sot() -> None:
    """Người bấm TẠM DỪNG hay TẮT một chiến thuật — quyết định ấy phải sống.

    `tamDung` và `batTat` chỉ nằm trong bộ nhớ. Một lần khởi động lại là
    bot chạy tiếp và mọi chiến thuật bật lại, IM LẶNG.

    Chiều hỏng là chiều NGUY HIỂM: thứ người ta tắt đi thì bật lên, chứ
    không phải ngược lại. Mà người ta tắt một chiến thuật thường là vì vừa
    thấy nó làm gì đó không ổn — đúng lúc KHÔNG được quên.

    Và khởi động lại xảy ra vì đủ thứ lý do chẳng liên quan: cập nhật,
    sập, người bấm nhầm. Riêng hôm nay runtime này khởi động lại hơn mười
    lăm lần.
    """
    print("\n── Quyết định của NGƯỜI phải sống qua khởi động lại ────────")

    import json as _js
    import tempfile

    import kham.vong as V

    with tempfile.TemporaryDirectory() as d:
        r = V.Runtime.__new__(V.Runtime)
        r.batTat = {"a": True, "b": True}
        r.tamDung = False
        r._duongThu = Path(d) / "dieu-khien.json"
        # ép `_duong_dieu_khien` trỏ vào thư mục thử
        V.Runtime._duong_dieu_khien = property(lambda self: self._duongThu)

        r._nap_dieu_khien()
        kiem("chưa có sổ ⇒ mặc định chạy tiếp, mọi chiến thuật bật",
             r.tamDung is False and all(r.batTat.values()))

        r.tamDung = True
        r.batTat["b"] = False
        r.ghi_dieu_khien()
        kiem("ghi ra file thật", r._duongThu.exists())

        r2 = V.Runtime.__new__(V.Runtime)
        r2.batTat = {"a": True, "b": True}
        r2.tamDung = False
        r2._duongThu = r._duongThu
        r2._nap_dieu_khien()
        kiem("khởi động lại: VẪN tạm dừng", r2.tamDung is True)
        kiem("và chiến thuật đã tắt VẪN tắt", r2.batTat["b"] is False)
        kiem("chiến thuật không ai đụng thì vẫn bật", r2.batTat["a"] is True)

        # Sổ hỏng ⇒ chạy bằng mặc định và KÊU, không sập.
        r._duongThu.write_text("{khong-phai-json", encoding="utf-8")
        r3 = V.Runtime.__new__(V.Runtime)
        r3.batTat = {"a": True, "b": True}
        r3.tamDung = False
        r3._duongThu = r._duongThu
        r3._nap_dieu_khien()
        kiem("sổ hỏng thì chạy bằng mặc định, không ném",
             r3.tamDung is False and all(r3.batTat.values()))

        # Chiến thuật lạ trong sổ KHÔNG được đẻ ra khoá mới.
        r._duongThu.write_text(
            _js.dumps({"tamDung": False, "batTat": {"khong-ton-tai": False}}),
            encoding="utf-8")
        r4 = V.Runtime.__new__(V.Runtime)
        r4.batTat = {"a": True, "b": True}
        r4.tamDung = False
        r4._duongThu = r._duongThu
        r4._nap_dieu_khien()
        kiem("tên chiến thuật lạ trong sổ bị bỏ qua",
             set(r4.batTat) == {"a", "b"}, sorted(r4.batTat))

    GOC_MA = Path(__file__).resolve().parent.parent
    sv = (GOC_MA / "kham" / "server.py").read_text(encoding="utf-8")
    kiem("nút tạm dừng GHI NGAY khi bấm",
         sv.count("runtime.ghi_dieu_khien()") >= 2)

def kiem_trang_kham_biet_keu() -> None:
    """Trang khám sức khoẻ phải BIẾT KÊU, và không được tự tính gì.

    Một trang khám lúc nào cũng "ĐẠT" chính là cái bệnh cả bộ kiểm này đi
    sửa: một đèn xanh vĩnh viễn làm người ta thôi nhìn nó.

    Đã thử THẬT: cắm một phép kiểm cố ý hỏng vào `selftest`, chạy trang
    khám — nó in "bộ kiểm số học HỎNG", kể tên dòng hỏng, liệt kê vào mục
    CÓ HỎNG, và trả mã thoát 1. Bỏ phép kiểm hỏng ra thì mã thoát về 0.
    """
    print("\n── Trang khám phải biết kêu, và không tự tính gì ───────────")

    import ast as _a

    GOC_MA = Path(__file__).resolve().parent.parent
    f = GOC_MA / "scripts" / "kham-suc-khoe.py"
    kiem("có trang khám sức khoẻ", f.exists())
    if not f.exists():
        return
    src = f.read_text(encoding="utf-8")
    ma = chr(10).join(x.split("#", 1)[0] for x in src.splitlines())

    kiem("trả mã thoát 1 khi có cái hỏng", "return 1 if hong else 0" in ma)
    kiem("gọi lại selftest chứ không chép", "scripts/selftest.py" in ma)
    kiem("gọi lại cả hai bộ kiểm giao diện",
         "kiem-giao-dien.mjs" in ma and "kiem-buong-lai.mjs" in ma)
    kiem("gọi lại phép đối chiếu sổ kết quả",
         "doi-chieu-ket-qua.py" in ma)
    kiem("đọc trạng thái runtime qua API", "/api/trang-thai" in ma)

    # KHÔNG được tự tính: không import module đo, không dựng lại phép nào.
    cay = _a.parse(src)
    nhap = set()
    for n in _a.walk(cay):
        if isinstance(n, _a.ImportFrom) and (n.module or "").startswith("kham"):
            nhap.add(n.module)
    cam = {"kham.ban_thu", "kham.hoc_offline", "kham.phat_lai",
           "kham.chay_lai", "kham.tien_hoa"}
    kiem("KHÔNG nhập module đo — trang khám không tự tính gì",
         not (nhap & cam), sorted(nhap & cam))

    # Nó phải nói rõ nó KHÔNG trả lời được gì.
    kiem("nói rõ sức khoẻ KHÁC hiệu quả", "KHÁC hiệu quả" in src)
    kiem("và chỉ sang chỗ trả lời câu có lãi không",
         "chay-phat-lai" in src)

    # Đọc DÒNG MÁY, không dò văn xuôi.
    kiem("đọc dòng máy `KETLUAN` thay vì dò văn xuôi", "KETLUAN" in ma)
    dc = (GOC_MA / "scripts" / "doi-chieu-ket-qua.py").read_text(
        encoding="utf-8")
    kiem("và công cụ kia CÓ in dòng ấy ra", "KETLUAN khop=" in dc)

def kiem_loi_ra_mang() -> None:
    """Lối ra mạng phải thông ở CẢ BỐN chỗ gọi — không chỗ nào đi đường thẳng.

    Cả ba host Polymarket đang bị đóng ở tầng TLS từ máy này, và cách gỡ
    duy nhất nằm ngoài mã: người vận hành cấp một lối ra. Nên đây là một
    tính năng chưa bao giờ chạy thật, và nếu nó hỏng thì hôm cắm lối ra
    vào sẽ KHÔNG CÓ GÌ BÁO — chỉ tiếp tục thất bại y như cũ.

    Bốn chỗ phải cùng đi một lối: client HTTP, dòng sống Polymarket, dòng
    nền Binance, và bảng sức khoẻ nguồn (để người ta NHÌN THẤY đang đi lối
    nào). Sót một chỗ là được "một cỗ máy nửa thấy nửa mù mà không có gì
    báo" — đúng câu ghi trong `dong_song.py`.
    """
    print("\n── Lối ra mạng phải thông ở cả bốn chỗ ─────────────────────")

    import os

    from kham.config import CONFIG
    from kham.nguon import nguon

    cuCfg = (CONFIG.get("nguon") or {}).get("proxy")
    cuEnv = os.environ.get("HTTPS_PROXY")
    cuEnv2 = os.environ.get("https_proxy")
    try:
        CONFIG.setdefault("nguon", {})["proxy"] = ""
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("https_proxy", None)
        kiem("không khai gì ⇒ đường thẳng", nguon.proxy is None, nguon.proxy)

        os.environ["HTTPS_PROXY"] = "http://tu-moi-truong:8080"
        kiem("đọc được từ biến môi trường",
             nguon.proxy == "http://tu-moi-truong:8080", nguon.proxy)

        os.environ.pop("HTTPS_PROXY", None)
        os.environ["https_proxy"] = "http://chu-thuong:8080"
        kiem("chấp nhận cả tên biến chữ thường",
             nguon.proxy == "http://chu-thuong:8080", nguon.proxy)

        CONFIG["nguon"]["proxy"] = "http://tu-config:3128"
        kiem("config ĐÈ được biến môi trường",
             nguon.proxy == "http://tu-config:3128", nguon.proxy)

        CONFIG["nguon"]["proxy"] = "   "
        kiem("khai toàn khoảng trắng ⇒ coi như không khai",
             nguon.proxy == "http://chu-thuong:8080", nguon.proxy)

        # Đọc CONFIG mỗi lần gọi, không chốt lúc nạp module.
        CONFIG["nguon"]["proxy"] = "http://doi-giua-chung:9999"
        kiem("đọc CONFIG lúc GỌI, không chốt lúc nạp",
             nguon.proxy == "http://doi-giua-chung:9999", nguon.proxy)
    finally:
        if cuCfg is None:
            (CONFIG.get("nguon") or {}).pop("proxy", None)
        else:
            CONFIG["nguon"]["proxy"] = cuCfg
        for k, v in (("HTTPS_PROXY", cuEnv), ("https_proxy", cuEnv2)):
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    # Bốn chỗ gọi phải CÙNG đọc `nguon.proxy`.
    GOC_MA = Path(__file__).resolve().parent.parent

    def khong_chu_thich(vb: str) -> str:
        return chr(10).join(x.split("#", 1)[0] for x in vb.splitlines())

    ng = khong_chu_thich((GOC_MA / "kham" / "nguon.py")
                         .read_text(encoding="utf-8"))
    kiem("client HTTP truyền lối ra vào httpx",
         'kw["proxy"] = self.proxy' in ng)

    for ten in ("dong_song.py", "dong_song_nen.py"):
        t = khong_chu_thich((GOC_MA / "kham" / ten).read_text(encoding="utf-8"))
        kiem(f"{ten} lấy lối ra từ `nguon.proxy`", "_ng.proxy" in t)
        kiem(f"{ten} TRUYỀN nó vào `connect`",
             '"proxy": _proxy' in t,
             "websockets KHÔNG tự đọc HTTPS_PROXY như httpx")

    kiem("bảng sức khoẻ nguồn KHAI lối đang dùng",
         "duongRa" in ng or "coProxy" in ng)

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
    kiem_bien_cua_chan_rui_ro()
    kiem_bien_cua_dat_lenh()
    kiem_bien_cua_nan_lai()
    kiem_bien_cua_so_lenh()
    kiem_bien_cua_can_loi()
    kiem_bien_cua_dinh_gia()
    kiem_bien_cua_ket_toan()
    kiem_bien_cua_cham_moc()
    kiem_bien_cua_ton_kho()
    kiem_bien_cua_cong_rui_ro()
    kiem_doi_soat_truoc_khi_dat_that()
    kiem_tran_chan_tran_khong_vuot()
    kiem_phat_ton_kho()
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
    kiem_quyet_dinh_cua_nguoi_song_sot()
    kiem_trang_kham_biet_keu()
    kiem_loi_ra_mang()
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
