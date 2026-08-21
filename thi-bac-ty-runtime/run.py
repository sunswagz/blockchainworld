"""Điểm khởi động Thị Bạc Ty.

    python run.py                    chế độ trong config.json (mặc định: quan-sat)
    python run.py --port=5288        đổi cổng
    python run.py --nhip=15          đổi nhịp quét, giây

Buồng lái chỉ sống ở localhost. Đọc README.md trước khi đổi `che`.
"""
from __future__ import annotations

import sys

import uvicorn

from bac.config import CONFIG, che_hieu_luc, ly_do_khong_that, san_co_khoa


def _co(ten: str):
    for a in sys.argv[1:]:
        if a.startswith(f"--{ten}="):
            return a.split("=", 1)[1]
    return None


def main() -> None:
    if (p := _co("port")):
        CONFIG["port"] = int(p)
    if (n := _co("nhip")):
        CONFIG["nhipGiay"] = float(n)

    port = CONFIG["port"]
    che, khai = che_hieu_luc(), CONFIG.get("che")
    q = CONFIG["quet"]
    cang = [k for k, v in CONFIG["san"].items() if (v or {}).get("bat")]

    print("=" * 78)
    print("  THỊ BẠC TY — ty coi việc buôn bán giữa các cảng")
    print(f"  {len(cang)} cảng ({', '.join(cang)})"
          f" · {len(q['ma'])} mã · nhịp {CONFIG['nhipGiay']:g}s"
          f" · cửa sổ giữ {q['giuGio']:g}h")
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
    else:
        print("  SỔ GIẤY. Cân trên funding và giá THẬT, nhưng không lệnh nào rời máy.")
    print("  Lớp đặt lệnh chưa được viết. Không cấu hình nào mở được nó.")

    khoa = san_co_khoa()
    if any(khoa.values()):
        co = [k for k, v in khoa.items() if v]
        print(f"  (.env có khoá cho: {', '.join(co)} — bản này KHÔNG đọc giá trị của chúng)")

    print()
    print(f"  ngưỡng: gross ≥ {CONFIG['ruiRo']['grossToiThieuBpsNgay']:g} bps/ngày"
          f" · NET ≥ {CONFIG['ruiRo']['netToiThieuBps']:g} bps"
          f" · lệch mark ≤ {CONFIG['ruiRo']['lechMarkToiDaBps']:g} bps"
          f" · tuổi ≤ {CONFIG['ruiRo']['tuoiToiDaGiay']:g}s")
    print()
    print(f"  buồng lái →  http://localhost:{port}")
    print()
    print("  Funding trả theo MỐC, không chảy liên tục. Giữ 4 giờ trên sàn")
    print("  kết toán 8 giờ có thể thu được ĐÚNG BẰNG KHÔNG.")
    print("=" * 78)

    uvicorn.run("bac.server:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
