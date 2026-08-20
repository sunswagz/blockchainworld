"""SOÁT LẠI BÀI HỌC — chạy hậu kiểm lần nữa, lần này với cả sổ trong tay.

    python scripts/soat-lai-bai-hoc.py          xem trước, không ghi
    python scripts/soat-lai-bai-hoc.py --ghi    ghi data/lessons-soat-lai.jsonl

VÌ SAO CẦN

Bài học được đúc NGAY LÚC lệnh đóng. Lúc đó sổ mới có vài lệnh, nên mọi câu hỏi
cần so sánh đều không trả lời được: "lệnh này cược lớn hơn mức thường bao nhiêu"
là câu hỏi vô nghĩa khi chưa tồn tại "mức thường". Kết quả đo được ở đây: tám
lệnh khác nhau ra đúng HAI câu bài học, và hai lệnh thua cược gấp 1,8–1,9× mức
trung bình vẫn được dán nhãn GOOD_TRADE.

Bộ não đọc bài học qua `journal.recall()`. Nếu kho bài học chỉ có hai câu thì dù
hậu kiểm có thông minh tới đâu, cái CHẢY VÀO prompt vẫn là hai câu cũ. Sửa hàm
hậu kiểm mà không soát lại kho là sửa cái vòi trong khi bể vẫn đầy nước cũ.

VÌ SAO KHÔNG GHI ĐÈ `lessons.jsonl`

Đó là bản ghi bộ não ĐÃ nghĩ gì lúc đó — bằng chứng cho chính chỗ hỏng này. Ghi
đè là xoá bằng chứng, và `store.write_all()` chặn thẳng. File soát lại là lớp
phủ: `recall()` ưu tiên nó khi có, xoá file đi là quay về nguyên trạng.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import store  # noqa: E402
from trader.brain import mock_postmortem  # noqa: E402

GHI = "--ghi" in sys.argv


def main() -> int:
    lenh = store.read_all(store.TRADES)
    goc = store.read_all(store.LESSONS)
    if not goc:
        print("Chưa có bài học nào để soát.")
        return 0

    theo_id = {t["id"]: t for t in lenh}
    ra, thieu, doi = [], 0, 0

    for l in goc:
        t = theo_id.get(l.get("tradeId"))
        if t is None:
            thieu += 1
            continue
        # so=lenh → hậu kiểm nhìn CẢ SỔ, không nhìn một lệnh đứng lẻ
        moi = mock_postmortem(t, lenh)
        khac = moi.get("lesson") != l.get("lesson") or \
            moi.get("classification") != l.get("classification")
        doi += bool(khac)
        ra.append({"tradeId": t["id"], "soatLaiLuc": None, **moi})

        dau = "ĐỔI " if khac else "     "
        print(f"{dau}{t['id'][:8]}  {l.get('classification','?'):24} → {moi['classification']}")
        if khac:
            print(f"      cũ : {(l.get('lesson') or '')[:96]}")
            print(f"      mới: {moi['lesson'][:96]}")

    cau_goc = len({(l.get('classification'), l.get('lesson')) for l in goc})
    cau_moi = len({(r['classification'], r['lesson']) for r in ra})
    print()
    print(f"{len(ra)} bài học · {doi} bài đổi kết luận"
          + (f" · {thieu} bài không tìm thấy lệnh gốc (bỏ qua)" if thieu else ""))
    print(f"số câu KHÁC NHAU: {cau_goc} → {cau_moi}")
    doi_chien_luoc = sum(1 for r in ra if r.get("change_strategy"))
    print(f"đòi đổi chiến lược: {sum(1 for l in goc if l.get('change_strategy'))} → {doi_chien_luoc}")

    if not GHI:
        print("\n(xem trước — thêm --ghi để lưu)")
        return 0

    store.write_all(store.LESSONS_SOAT_LAI, ra)
    print(f"\nĐã ghi {len(ra)} bài vào {store.LESSONS_SOAT_LAI}. "
          f"lessons.jsonl KHÔNG bị đụng tới.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
