"""A/B phép nắn trên BĂNG THẬT — thô so với đã nắn.

    python scripts/thu-nan-lai.py

Phép nắn tới giờ mới chỉ được đo trên chính bảng hiệu chỉnh đã sinh ra
nó: sai số 6,37 → 1,91 điểm. Con số ấy đúng, nhưng nó là **tự chấm bài
mình** — đường nắn khớp từ bảng đó thì tất nhiên khớp với bảng đó.

Phép thử thật là: đem cả hai bộ tham số chạy lại trên băng đã ghi, chấm
bằng kết quả có thật, rồi so lãi lỗ. Đó là câu hỏi khác hẳn — không phải
"mô hình có khớp bảng không" mà "vặn thế này thì kiếm được nhiều hơn
không".

Hai câu đó có thể trả lời ngược nhau, và khi ngược thì câu sau đúng.
"""
from __future__ import annotations

import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402

from kham import tham_so  # noqa: E402

# Không cờ nào — nhưng vẫn phải TỪ CHỐI cờ lạ. Một cờ gõ sai bị
# nuốt im lặng thì phép đo chạy ở cấu hình khác cấu hình người ta
# yêu cầu, rồi in ra một báo cáo trông hoàn toàn hợp lệ.
tham_so.doc({}, ten='thu-nan-lai.py')
from kham.bang import BaoCaoDoc, lan_luot  # noqa: E402
from kham.chay_lai import ThamSo, mot_luot  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import HieuChinh  # noqa: E402
from kham.ket_qua import so_ket_qua  # noqa: E402
from kham.nan_lai import khop  # noqa: E402


def main() -> int:
    print(f"\n  Sổ kết quả: {so_ket_qua.tom_tat()}")
    pn = khop(HieuChinh())
    print(f"  Phép nắn : {pn.tongMau} mẫu · "
          f"sai số {pn.saiTruoc*100:.2f} → {pn.saiSau*100:.2f} điểm "
          f"· dùng được: {pn.dung_duoc}")
    if not pn.dung_duoc:
        print("\n  Chưa nắn được thì không có gì để so.\n")
        return 0

    print("  Nạp băng…")
    bao = BaoCaoDoc()
    khung = list(lan_luot(None, bao))
    print(f"  {len(khung)} khung hình · {bao.soFileHong} file hỏng, "
          f"{bao.soFileCutDuoi} cụt đuôi")

    cl = CONFIG["canLoi"]
    chung = {"netEdgeToiThieu": float(cl["netEdgeToiThieu"]),
             "bienAnToan": float(cl["bienAnToan"])}
    a = ThamSo(ten="thô", **chung)
    b = ThamSo(ten="đã nắn", phepNan=pn, **chung)

    print("\n  Chạy lại…")
    ka, kb = mot_luot(khung, a), mot_luot(khung, b)

    def dong(k):
        tb = (k.tongLaiLo / k.soKhop) if k.soKhop else 0.0
        tl = (k.soThang / k.soKhop) if k.soKhop else 0.0
        return (f"  {k.ten:9} | cơ hội {k.soCoHoi:6} | qua sàng {k.soQuaSang:5} "
                f"| chấm {k.soKhop:5} | thắng {tl:5.1%} "
                f"| lãi lỗ {k.tongLaiLo:+9.2f} | mỗi lệnh {tb:+7.4f}")

    print("\n" + "  " + "─" * 96)
    print(dong(ka))
    print(dong(kb))
    print("  " + "─" * 96)

    if not ka.soKhop and not kb.soKhop:
        print("\n  KHÔNG chấm được khung nào. Lý do hàng đầu:")
        for ly, n in sorted(ka.boQua.items(), key=lambda x: -x[1])[:5]:
            print(f"    {n:7} × {ly}")
        print()
        return 0

    d = kb.tongLaiLo - ka.tongLaiLo
    print(f"\n  Chênh lệch: {d:+.2f} "
          f"({'nắn LỜI hơn' if d > 0 else 'nắn LỖ hơn' if d < 0 else 'ngang nhau'})")
    print("\n  Nhắc: đây vẫn là chạy lại TRONG MẪU — băng này chính là quãng "
          "\n  thời gian đã sinh ra bảng hiệu chỉnh. Nó bác bỏ được (nếu nắn "
          "\n  làm tệ đi thì thấy ngay), nhưng chưa chứng minh được.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
