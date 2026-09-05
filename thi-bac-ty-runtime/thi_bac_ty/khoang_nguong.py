"""KHOẢNG CÁCH TỚI NGƯỠNG — một phép ĐẾM không nói được cổng đặt đúng hay sai.

Một bảng lý do từ chối nói «net dưới ngưỡng: 2.989» đọc như «sát mà chưa
đủ». Nhưng cùng con số ấy cũng đúng khi khối bị loại nằm xa ngưỡng cả một
bậc độ lớn — và hai chuyện ấy đòi hai cách chữa ngược nhau: một bên vặn
ngưỡng, một bên là ĐỪNG ĐỘNG VÀO, chợ không có gì để lấy.

Ba lần đo trong một ngày, ba lần cùng một câu hỏi và ba script rời để
trả lời:

    amm.fee_farming     8.005 pool trượt TVL — nhưng chỉ 7,9% nằm trong
                        khoảng NỬA ngưỡng; trung vị 108.669 USD so với
                        ngưỡng 1 triệu. Chợ trống, không phải cổng sai.
    options.put_call    748 cơ hội trượt NET — gross ÂM ở cả 748, cao
                        nhất −4,35 bps. Spread ăn hết.
    stablecoin.cross    chênh thô ĐÚNG BẰNG 0,00 bps trên ngưỡng 1,00,
                        và phí 9 bps. Cần một cú depeg mới có việc.

Ba lần là đủ để thôi viết script rời. File này là cái thước ấy, và nó
sống trong ảnh chụp chứ không trong đầu người đọc.

## Nó KHÔNG làm gì

Không khuyên vặn ngưỡng. Không chấm điểm. Nó chỉ nói khối bị loại nằm ở
ĐÂU so với ngưỡng, để câu «vặn ngưỡng có mở được gì không» trả lời được
bằng số.
"""
from __future__ import annotations


def vi_tri(ds) -> dict | None:
    """`n · min · p50 · max` của một chùm số. `None` khi chưa có mẫu.

    Trả `None` chứ không trả 0: một số 0 ở đây đọc thành «đo được, và
    bằng không» — một câu dữ liệu không hề nói.
    """
    d = sorted(x for x in ds if x is not None)
    if not d:
        return None
    n = len(d)
    return {"n": n, "min": round(d[0], 4),
            "p50": round(d[n // 2], 4), "max": round(d[-1], 4)}


def khoang_cach(ds, nguong: float, tren: bool = True) -> dict:
    """Khối bị loại nằm SÁT ngưỡng hay xa hẳn.

    `tren=True` nghĩa là muốn giá trị LỚN HƠN ngưỡng (net, APY, TVL);
    `tren=False` là muốn NHỎ HƠN (phí, tuổi dữ liệu).

    `cach` là khoảng cách từ ứng viên TỐT NHẤT tới ngưỡng — con số duy
    nhất trả lời được «vặn ngưỡng có mở được gì không». Âm nghĩa là đã
    có kẻ vượt ngưỡng.

    `phanTrongNua` là phần khối bị loại nằm trong khoảng NỬA ngưỡng tính
    từ ngưỡng ra. Đây là chỗ `amm` lật ngược trực giác: 8.005 pool trượt
    nghe như «hạ ngưỡng là mở được nhiều», nhưng 92% nằm ngoài cả nửa
    ngưỡng nên hạ xuống một nửa chỉ thêm 632 pool bé nhất.
    """
    d = [float(x) for x in ds if x is not None]
    ra = {"nguong": float(nguong), "tren": bool(tren),
          "phanBo": vi_tri(d), "soDat": 0, "soTruot": 0,
          "cach": None, "phanTrongNua": None}
    if not d:
        return ra
    dat = [x for x in d if (x >= nguong if tren else x <= nguong)]
    truot = [x for x in d
             if not (x >= nguong if tren else x <= nguong)]
    ra["soDat"], ra["soTruot"] = len(dat), len(truot)
    tot = max(d) if tren else min(d)
    ra["cach"] = round((nguong - tot) if tren else (tot - nguong), 4)
    if truot:
        # Nửa ngưỡng đo từ NGƯỠNG ra, không phải từ 0: với ngưỡng 1 triệu
        # thì «trong khoảng nửa ngưỡng» là 500k–1tr, và một pool 50k nằm
        # ngoài. Đo từ 0 sẽ gộp cả những pool xa hẳn vào nhóm «sát».
        nua = abs(float(nguong)) / 2.0
        gan = [x for x in truot
               if (x >= nguong - nua if tren else x <= nguong + nua)]
        ra["phanTrongNua"] = round(len(gan) / len(truot), 4)
    return ra
