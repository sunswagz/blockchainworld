"""Điểm khởi động Khâm Thiên Giám.

    python run.py                    chế độ trong config.json (mặc định: giay)
    python run.py --che=quan-sat     chỉ đo, không có vị thế nào
    python run.py --port=5286        đổi cổng
    python run.py --vong=5           đổi nhịp vòng lặp

Buồng lái chỉ sống ở localhost. Xem README.md trước khi đổi `che`.
"""
from __future__ import annotations

import uvicorn

from kham.config import CONFIG, che_hieu_luc, ly_do_khong_that, nao_cham_bat


def main() -> None:
    port = CONFIG["port"]
    che = che_hieu_luc()
    khai = CONFIG.get("che")

    print("=" * 78)
    print("  KHÂM THIÊN GIÁM — đài chiêm nghiệm thị trường tiên đoán")
    print(f"  {len([t for t in CONFIG['thiTruong'] if t.get('theo')])} market theo dõi"
          f" · vòng {CONFIG['loopSeconds']}s"
          f" · não chậm: {'CÓ khoá' if nao_cham_bat() else 'không khoá (vẫn chạy đủ)'}")
    print()

    if che != khai:
        print(f"  chế độ khai `{khai}` nhưng HIỆU LỰC là `{che}` — chưa mở đủ cửa:")
        for c in ly_do_khong_that():
            print(f"     · {c}")
    else:
        print(f"  chế độ: {che.upper()}")

    print()
    if che == "quan-sat":
        print("  CHỈ ĐO. Không mở vị thế nào, kể cả trên sổ giấy.")
    elif che == "giay":
        print("  SỔ GIẤY. Khớp trên sổ lệnh THẬT, phí THẬT, nhưng TIỀN GIẢ.")
        print("  Không đường code nào chạm tới ví ở chế độ này.")
    else:
        print("  ██ TIỀN THẬT ██  trần mỗi lệnh "
              f"${CONFIG['datLenh']['tranMoiLenhUsd']}"
              f" · trần lỗ ngày ${CONFIG['ruiRo']['tranLoNgayUsd']}"
              f" · kill switch sụt vốn {CONFIG['ruiRo']['tranSutVonPct']}%")

    print()
    print(f"  vốn sổ sách ${CONFIG['ruiRo']['vonBanDau']}"
          f" · trần/market ${CONFIG['ruiRo']['vonToiDaMoiThiTruongUsd']}"
          f" · trần nằm trần một chân ${CONFIG['khoDoi']['capChuaKhopToiDaUsd']}")
    print(f"  net edge tối thiểu {CONFIG['canLoi']['netEdgeToiThieu']}"
          f" · biên an toàn {CONFIG['canLoi']['bienAnToan']}")
    print()
    print(f"  buồng lái →  http://localhost:{port}")
    print()
    print("  NET EDGE mới là alpha. Signal, latency, accuracy thì không.")
    print("=" * 78)

    uvicorn.run("kham.server:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
