"""Cờ dòng lệnh: khai MỘT chỗ, và TỪ CHỐI cờ lạ.

Mười script đo đạc từng có mười bộ đọc cờ gần như giống hệt nhau, và cả
mười hỏng theo cùng một kiểu:

    def _tham_so(ten, mac_dinh=None):
        for a in sys.argv[1:]:
            if a.startswith(f"--{ten}="):
                return a.split("=", 1)[1]
        return mac_dinh

Cờ nào không thấy thì trả mặc định, và cờ LẠ thì không ai nói gì. Gõ
`--vốn=10000` (có dấu), `--von 10000` (dấu cách thay vì bằng), hay
`--capital=10000` — cả ba đều chạy ngon lành ở giá trị MẶC ĐỊNH rồi in
ra một báo cáo trông hoàn toàn hợp lệ.

Với một bộ dụng cụ ĐO thì đó là lỗi nặng: phép đo báo cáo một cấu hình
khác cấu hình người ta yêu cầu, và không dấu vết nào để lần. Cùng họ với
mấy lỗi đã ghi ở đây — thước tự khớp trên tập nó chấm, bộ đếm mang tên
việc A mà đếm việc B, nhật ký cũ trình bày như tin mới.

Nên: khai một lần, dùng cho cả ba việc — đọc, kiểm, và in `--help`. Cờ
không khai thì DỪNG HẲN, chứ không cảnh báo rồi chạy tiếp: chạy tiếp là
vẫn cho ra một báo cáo sai, chỉ thêm một dòng chữ ít ai đọc.
"""
from __future__ import annotations

import sys

#: Đánh dấu một cờ BẬT/TẮT (`--quet`), không mang giá trị.
BAT = object()


class ThamSo:
    """Kết quả đọc cờ. `lay` cho cờ có giá trị, `co` cho cờ bật/tắt."""

    def __init__(self, gt: dict, khai: dict) -> None:
        self._gt = gt
        self._khai = khai

    def lay(self, ten: str, macDinh=None):
        """Giá trị chuỗi của cờ `--ten=...`, hoặc `macDinh`."""
        if ten not in self._khai:
            # Hỏi một cờ chưa khai là lỗi của người viết script, không
            # phải của người dùng. Ném ngay, đừng trả None cho nó trôi.
            raise KeyError(f"cờ `{ten}` chưa được khai trong doc(...)")
        v = self._gt.get(ten)
        return macDinh if v is None else v

    def so(self, ten: str, macDinh=None):
        """Như `lay` nhưng đổi ra số. Gõ sai kiểu thì DỪNG, không lặng lẽ
        lùi về mặc định — lùi về là lại đo cấu hình khác cấu hình yêu cầu.
        """
        v = self.lay(ten)
        if v is None:
            return macDinh
        try:
            return float(v)
        except (TypeError, ValueError):
            _chet(f"cờ `--{ten}={v}` không phải một số")

    def co(self, ten: str) -> bool:
        """Cờ bật/tắt có mặt không."""
        if self._khai.get(ten) is not BAT:
            raise KeyError(f"`{ten}` không phải cờ bật/tắt")
        return bool(self._gt.get(ten))


def _chet(loi: str) -> None:
    print(f"  LỖI: {loi}", file=sys.stdout)
    print("  Chạy lại với --help để xem các cờ nhận được.")
    raise SystemExit(2)


def _in_giup(khai: dict, ten: str) -> None:
    print(f"  {ten} — các cờ nhận được:")
    if not khai:
        print("    (không có cờ nào)")
    for k in sorted(khai):
        v = khai[k]
        nhan = f"--{k}" if v is BAT else f"--{k}=..."
        mo = "bật/tắt" if v is BAT else str(v)
        print(f"    {nhan:<28} {mo}")


def doc(khai: dict, argv: list | None = None, ten: str = "") -> ThamSo:
    """Đọc cờ theo bảng khai. Cờ lạ ⇒ dừng với mã 2.

    `khai` là {tên cờ: mô tả} — hoặc `BAT` thay cho mô tả nếu là cờ
    bật/tắt. Tên KHÔNG mang hai dấu gạch đầu.
    """
    av = list(sys.argv[1:] if argv is None else argv)
    ten = ten or (sys.argv[0] if sys.argv else "script")
    if "--help" in av or "-h" in av:
        _in_giup(khai, ten)
        raise SystemExit(0)

    gt: dict = {}
    for a in av:
        if not a.startswith("--"):
            _chet(f"không hiểu `{a}` — mọi cờ đều phải bắt đầu bằng `--`")
        tho = a[2:]
        if "=" in tho:
            k, v = tho.split("=", 1)
        else:
            k, v = tho, True
        if k not in khai:
            gan = [x for x in khai if x.startswith(k[:3])] if len(k) >= 3 else []
            them = f"  Có phải ý bạn là `--{gan[0]}`?" if gan else ""
            print(f"  LỖI: không có cờ `--{k}`.{them}")
            _in_giup(khai, ten)
            raise SystemExit(2)
        if khai[k] is BAT and v is not True:
            _chet(f"`--{k}` là cờ bật/tắt, đừng gán giá trị cho nó")
        if khai[k] is not BAT and v is True:
            _chet(f"`--{k}` cần một giá trị: `--{k}=...`")
        gt[k] = v
    return ThamSo(gt, khai)
