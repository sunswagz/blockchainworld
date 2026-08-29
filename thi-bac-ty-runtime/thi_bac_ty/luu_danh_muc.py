"""GIỮ DANH MỤC QUA LẦN KHỞI ĐỘNG LẠI — và cùng với nó, đường NAV.

## Chuyện đo được, không phải suy đoán

Sổ cái ngày 29/08 nói ty xoay lãi cho vay **lỗ 3,28 USD**. Tách khoản ra
thì nó **lãi 0,15**, và 3,43 kia là phí VÀO LỆNH trả qua **51 lần vào
lệnh** — cho bảy vị thế.

Bảy vị thế mà 51 lần vào, vì mỗi lần `python run.py` khởi động lại là
một lần vào lệnh mới: `DanhMuc` dựng trong RAM nên nó quên sạch, rồi
vòng sau mở lại từ đầu và trả phí lần nữa. Mười lăm lần deploy trong một
buổi chiều là mười lăm lần vào lệnh.

Hai hậu quả, và cái thứ hai nặng hơn hẳn:

**1. Lãi lỗ bị bẩn.** Chi phí VẬN HÀNH đội lốt chi phí chiến lược.
`lai_lo_tach_khoan()` đã tách được hai thứ ấy, nhưng tách một khoản
không đáng có vẫn không bằng đừng sinh ra nó.

**2. Đường NAV không bao giờ dài quá một lần chạy.** `hieuNang` đòi ≥168
giờ dữ liệu mới dám kết luận; máy khởi động lại vài lần một ngày thì con
số ấy vĩnh viễn ở mức vài phút. Sụt vốn, thời gian dưới đáy, CAGR —
bốn thứ đứng trên đường NAV — đều không bao giờ đo được. Và vòng tiến
hoá tham số, thứ ăn chính những con số ấy, không bao giờ có gì để học.

Một cỗ máy dựng ra để chạy nhiều tháng mà trí nhớ chỉ dài bằng một lần
chạy thì nó không phải cỗ máy nhiều tháng.

## Giữ cái gì, và vì sao KHÔNG giữ cái gì

    tienMatUsd            tiền mặt còn lại
    laiLoDaThucHienUsd    lãi lỗ đã ghi
    viThe                 các chân đang mở
    soViThe               sổ vị thế của Trung Ương (mở lúc nào, cộng dồn gì)
    duongNav              các điểm NAV theo thời gian

**KHÔNG giữ `ngoai`** — vốn ở cỗ máy khác đọc lại được mỗi vòng, và giữ
một bản cũ là đúng thứ `von-ngoai-mu` sinh ra để chặn: một con số cũ
trông y hệt một con số mới.

**KHÔNG giữ `vonBanDauUsd`** — nó là cấu hình, đọc từ `config.json`. Giữ
bản cũ thì đổi vốn ảo trong config sẽ không có tác dụng, và im lặng.

## Khoảng máy TẮT phải được KHAI, không được lấp

Vị thế sống qua restart, nhưng lúc máy tắt thì không ai cộng lãi cho nó.
Nạp lại rồi cộng bù cả khoảng ấy là **bịa ra một phép đo chưa từng
chạy** — ta không biết rate trong lúc mình đang tắt.

Nên mốc kế toán đặt lại thành **BÂY GIỜ**, khoảng trống bị bỏ, và
`giayTatMay` ghi lại đúng nó mất bao lâu. Đường NAV cũng có một quãng
đứt tương ứng, và `hieu_nang` đọc được nó vì các điểm mang dấu thời gian
thật chứ không phải số thứ tự.

## Ghi ATOMIC, vì một file hỏng là mất cả danh mục

Ghi thẳng vào file đích mà tiến trình chết giữa chừng thì lần sau nạp
phải một JSON cụt — và lúc ấy máy mất sạch vị thế trong khi sổ đăng ký
vẫn ghi chúng đang mở, tức là quay về đúng chỗ lệch mà
`doi_soat_vi_the.py` sinh ra để bắt. Nên ghi ra file tạm rồi `replace()`,
thao tác đổi tên là nguyên tử trên cả Windows lẫn POSIX.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

#: Bản ghi. Đổi cấu trúc thì tăng số, và bản cũ bị BỎ chứ không đoán —
#: nạp một cấu trúc mình không hiểu là cách chắc chắn để dựng lại sai.
BAN = 1


def luu(duong, danh_muc, soViThe: dict, duongNav, soVonGio=None,
        napThemUsd: float = 0.0) -> int:
    """Ghi danh mục ra đĩa. Trả về số byte đã ghi.

    Ghi qua file tạm rồi đổi tên: chết giữa chừng thì file đích vẫn là
    bản cũ còn đọc được, thay vì một JSON cụt.
    """
    d = {
        "ban": BAN,
        "lucGiay": time.time(),
        "tienMatUsd": float(danh_muc.tienMatUsd),
        "laiLoDaThucHienUsd": float(danh_muc.laiLoDaThucHienUsd),
        "viThe": {k: [c.tom_tat() for c in v]
                  for k, v in danh_muc.viThe.items()},
        "soViThe": [{
            "ma": s.ma, "chienLuoc": s.chienLuoc, "toTrinh": s.toTrinh,
            "vonUsd": s.vonUsd, "moLucGiay": s.moLucGiay,
            "keToanLucGiay": s.keToanLucGiay,
            "thuCongDonUsd": s.thuCongDonUsd,
            "phiCongDonUsd": s.phiCongDonUsd,
            "soVongKeToan": s.soVongKeToan,
            "soVongKhongDoDuoc": s.soVongKhongDoDuoc,
            "coKeToan": s.coKeToan,
        } for s in soViThe.values()],
        # Ba phần tử: thời điểm, NAV, DÒNG VỐN ngoài. Thiếu phần tử thứ ba
        # thì một cú nạp vốn đọc thành lợi nhuận — xem `hieu_nang.py`.
        "duongNav": [[float(x[0]), float(x[1]),
                      float(x[2]) if len(x) >= 3 else 0.0]
                     for x in getattr(duongNav, "diem", [])],
        # Vốn CHỦ bỏ thêm, cộng dồn. KHÁC `vonBanDauUsd`: cái kia là cấu
        # hình và phải đổi được, cái này là chuỗi sự kiện đã xảy ra và không
        # được mất — mất nó thì lần khởi động sau vốn gốc tụt về mức cũ
        # trong khi tiền mặt vẫn còn, và sụt vốn đọc ra một con số bịa.
        "napThemUsd": float(napThemUsd),
        # Trường THÊM, không đổi cấu trúc cũ — nên KHÔNG tăng `BAN`. Bản đọc
        # cũ bỏ qua khoá lạ; bản đọc mới gặp bản lưu thiếu khoá này thì cộng
        # lại từ 0 và KHAI ra là mới bắt đầu. Tăng `BAN` ở đây sẽ vứt cả danh
        # mục đang mở chỉ để thêm một thước đo — cái giá ấy không tương xứng,
        # và luật `BAN` sinh ra cho thay đổi KHÔNG ĐỌC NỔI, không phải cho
        # mọi thay đổi.
        "soVonGio": ({"vonGioUsd": float(soVonGio.vonGioUsd),
                      "thuRongUsd": float(soVonGio.thuRongUsd),
                      "tuGiay": float(soVonGio.tuGiay),
                      "denGiay": float(soVonGio.denGiay)}
                     if soVonGio is not None else None),
    }
    p = Path(duong)
    p.parent.mkdir(parents=True, exist_ok=True)
    tam = p.with_suffix(p.suffix + ".dang-ghi")
    noi = json.dumps(d, ensure_ascii=False)
    tam.write_text(noi, encoding="utf-8")
    os.replace(tam, p)
    return len(noi)


def nap(duong, danh_muc, duongNav) -> dict:
    """Nạp danh mục từ đĩa. Trả về tóm tắt để nhật ký và buồng lái nói ra.

    KHÔNG ném: file hỏng, thiếu, hay sai bản đều trả về một tóm tắt khai
    lý do rồi để máy chạy tiếp với danh mục rỗng. Chết ở đây là chết lúc
    khởi động, và một cỗ máy không lên được vì file trạng thái hỏng thì
    tệ hơn một cỗ máy lên với trí nhớ trống.
    """
    from .danh_muc import ViThe
    from .ke_toan import SoViThe

    p = Path(duong)
    if not p.is_file():
        return {"co": False, "vi": "chưa có bản lưu nào — máy chạy lần đầu "
                                   "hoặc bản lưu đã bị xoá"}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"co": True, "nap": False,
                "loi": f"{type(e).__name__}: {e}",
                "vi": "bản lưu ĐỌC KHÔNG ĐƯỢC — máy chạy với danh mục rỗng, "
                      "và `doi_soat_vi_the` sẽ thấy sổ đăng ký lệch"}
    if int(d.get("ban") or 0) != BAN:
        return {"co": True, "nap": False, "banFile": d.get("ban"),
                "vi": f"bản lưu là bản {d.get('ban')}, mã hiểu bản {BAN} — "
                      f"BỎ chứ không đoán cấu trúc"}

    now = time.time()
    tat = max(0.0, now - float(d.get("lucGiay") or now))

    danh_muc.tienMatUsd = float(d.get("tienMatUsd") or 0.0)
    danh_muc.laiLoDaThucHienUsd = float(d.get("laiLoDaThucHienUsd") or 0.0)
    danh_muc.viThe = {
        k: [ViThe(maToTrinh=c["maToTrinh"], chienLuoc=c["chienLuoc"],
                  ben=c["ben"], cang=c["cang"], taiSan=c["taiSan"],
                  vonUsd=float(c["vonUsd"]), chuoi=c.get("chuoi"),
                  loai=c.get("loai") or "perp", moLuc=c.get("moLuc") or "")
            for c in v]
        for k, v in (d.get("viThe") or {}).items()}

    soViThe: dict = {}
    for s in (d.get("soViThe") or []):
        # Mốc kế toán đặt lại thành BÂY GIỜ: khoảng máy tắt KHÔNG được
        # cộng bù. Ta không biết rate trong lúc mình đang tắt, và cộng bù
        # là bịa ra một phép đo chưa từng chạy.
        soViThe[s["ma"]] = SoViThe(
            ma=s["ma"], chienLuoc=s["chienLuoc"], toTrinh=s["toTrinh"],
            vonUsd=float(s["vonUsd"]), moLucGiay=float(s["moLucGiay"]),
            keToanLucGiay=now,
            thuCongDonUsd=float(s.get("thuCongDonUsd") or 0.0),
            phiCongDonUsd=float(s.get("phiCongDonUsd") or 0.0),
            soVongKeToan=int(s.get("soVongKeToan") or 0),
            soVongKhongDoDuoc=int(s.get("soVongKhongDoDuoc") or 0),
            coKeToan=s.get("coKeToan"))

    duongNav.diem = [(float(x[0]), float(x[1]),
                      float(x[2]) if len(x) >= 3 else 0.0)
                     for x in (d.get("duongNav") or [])]

    # Vốn-giờ: thiếu khoá thì KHÔNG cộng bù, y như mốc kế toán. Ta không
    # biết vốn nằm bao lâu trong lúc máy tắt, và đoán ra một mẫu số là bịa
    # ra một tỉ suất.
    from .ke_toan import SoVonGio
    vg = d.get("soVonGio") or None
    soVonGio = SoVonGio(
        vonGioUsd=float((vg or {}).get("vonGioUsd") or 0.0),
        thuRongUsd=float((vg or {}).get("thuRongUsd") or 0.0),
        tuGiay=float((vg or {}).get("tuGiay") or now),
        denGiay=now)

    return {
        "co": True, "nap": True,
        "soViThe": len(soViThe), "soDiemNav": len(duongNav.diem),
        "_soVonGio": soVonGio, "coSoVonGio": vg is not None,
        "_napThemUsd": float(d.get("napThemUsd") or 0.0),
        "tienMatUsd": danh_muc.tienMatUsd,
        "laiLoDaThucHienUsd": danh_muc.laiLoDaThucHienUsd,
        "giayTatMay": tat,
        "_soViThe": soViThe,
        "vi": (f"nạp lại {len(soViThe)} vị thế và {len(duongNav.diem)} điểm "
               f"NAV. Máy tắt {tat / 60:.1f} phút — khoảng ấy KHÔNG được "
               f"cộng lãi cho vị thế nào, vì không ai đo được rate trong "
               f"lúc máy không chạy."),
    }
