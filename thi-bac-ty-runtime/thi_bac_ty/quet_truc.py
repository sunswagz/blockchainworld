"""QUÉT TRỤC NÚT — một núm đổi thì cả danh mục đổi ra sao, trên CẢ trục.

`chay_lai_he.doi_chieu()` so ĐÚNG HAI giá trị. Hai điểm không nói được
hình dạng, và cái bẫy ấy đã cắn một lần rồi: quán quân của một lượt quét
hai điểm có thể là nhiễu, và chiều đúng có khi NGƯỢC HẲN.

File này quét cả trục, và nó mã hoá bốn bài học đã trả giá:

## 1. Điểm hiện tại phải NẰM TRÊN lưới

Lưới không chứa giá trị đang dùng thì mọi so sánh đều so với một điểm
chưa từng đo. Và mép trên phải CHẠM TỚI ĐƯỢC — một lưới dừng trước biên
của `NUT_TRUNG_UONG` khiến người đọc tưởng đã quét hết.

## 2. Đo TỔNG, không chỉ đo bình quân

`netMoiGioBinhQuanBps` là bình quân THEO VỐN. Rót ít vào đúng một cơ hội
tốt cho bình quân rất đẹp — nên chấm bằng bình quân là thưởng cho việc
không làm gì. Cột quyết định là `tongUsdMoiGio` = vốn rót × bình quân.

Đo làn thật 05/09/2026, trục `phanBo.toiDaSoViThe` trên 2.000 tờ trình:
bình quân TỤT đều 0,8475 → 0,7481 khi nới 30 → 300, trong khi vốn rót
TĂNG 651k → 762k. Tổng thì **đứng yên ở 57,014 USD/giờ suốt cả trục** —
không một chữ số nào đổi. Nhìn riêng cột nào cũng ra một kết luận sai.

## 3. Đo lại trên cửa sổ GẤP ĐÔI

Một trục đơn điệu trên một cửa sổ vẫn có thể là ảo. Hai cửa sổ cho hai
kết luận khác nhau thì cả hai đều chưa dùng được — `bat_dong()` nói ra
điều đó thay vì gộp bừa.

## 4. Núm KHÔNG RÀNG BUỘC phải được gọi tên

`ruiRoTong.tranMotCoHoi` quét từ 0,05 tới 0,60 — mười hai lần thay đổi —
mà không một con số nào nhúc nhích. Vì trần ấy là `0,15 × NAV` =
150.000 USD trong khi vị thế lớn nhất chỉ 25.000, tức cao gấp SÁU lần
chỗ nó đáng chặn. Nó không hỏng, nó chỉ không ràng buộc.

Chuyện ấy đáng biết vì `chan_doan_he` có hai triệu chứng khai đúng núm
này. Chỉ người vận hành sang một cái nút không thể đổi được gì là cùng
một lỗi với việc chỉ họ sang cái nút họ không hề chạm vào.
"""
from __future__ import annotations

import copy

#: Hai con số cách nhau ít hơn ngần này (tương đối) thì coi là BẰNG NHAU.
#: Số thực có đuôi, và một trục "đổi" ở chữ số thứ mười hai là một trục
#: không đổi.
SAI_SO_TUONG_DOI = 1e-9


def _gan(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    m = max(abs(float(a)), abs(float(b)), 1.0)
    return abs(float(a) - float(b)) / m <= SAI_SO_TUONG_DOI


def doc_nut(thamSo: dict, duong: str):
    """Giá trị đang dùng của một núm, theo đường `a.b`."""
    o = thamSo
    for k in str(duong).split("."):
        if not isinstance(o, dict):
            return None
        o = o.get(k)
    return o


def quet_truc(toTrinh: list, thamSo: dict, vonBanDauUsd: float,
              nut: str, luoi: list, mot_luot, dat_nut) -> dict:
    """Chạy `mot_luot` cho từng giá trị trên lưới.

    `mot_luot` và `dat_nut` truyền vào chứ không import ở đây: file này là
    LUẬT ĐỌC, và luật đọc phải kiểm được mà không cần dựng cả một Trung
    Ương. Phép kiểm truyền vào hai hàm giả.
    """
    hienTai = doc_nut(thamSo, nut)
    diem = []
    for g in luoi:
        ts = dat_nut(copy.deepcopy(thamSo), nut, g)
        kq = mot_luot(toTrinh, ts, vonBanDauUsd, nhan=str(g))
        d = kq.tom_tat() if hasattr(kq, "tom_tat") else dict(kq)
        net = d.get("netMoiGioBinhQuanBps")
        von = float(d.get("tongCapUsd") or 0.0)
        d["tongUsdMoiGio"] = (von * float(net) / 10_000.0
                              if net is not None else None)
        d["giaTri"] = g
        diem.append(d)
    return {
        "nut": nut, "luoi": list(luoi), "hienTai": hienTai,
        # Lưới không chứa điểm đang dùng thì mọi so sánh đều so với một
        # điểm chưa từng đo.
        "hienTaiTrenLuoi": hienTai in luoi,
        "diem": diem,
        "batDong": bat_dong(diem),
        "totNhat": tot_nhat(diem, hienTai),
    }


def bat_dong(diem: list) -> bool:
    """Cả trục KHÔNG đổi gì — núm không ràng buộc trong chế độ hiện tại.

    Trả `True` thì đừng đề xuất vặn nó: không phải vì nó hỏng, mà vì nó
    không chạm tới chỗ nào.
    """
    if len(diem) < 2:
        return False
    d0 = diem[0]
    return all(_gan(x.get("tongUsdMoiGio"), d0.get("tongUsdMoiGio"))
               and _gan(x.get("tongCapUsd"), d0.get("tongCapUsd"))
               for x in diem[1:])


def dam_hon(x: dict, moc: dict) -> bool:
    """`x` TẬP TRUNG hơn `moc` — cùng luật, cùng dải với `chay_lai_he`.

    Chép luật ra hai chỗ là hai chỗ sẽ lệch, nên chỗ này gọi thẳng
    `chay_lai_he.dam_hon_hai_ben` chứ không viết lại phép so.
    """
    from thi_bac_ty.chay_lai_he import dam_hon_hai_ben
    return dam_hon_hai_ben(
        moc.get("tiTrongCang"), moc.get("tiTrongTy"),
        x.get("tiTrongCang"), x.get("tiTrongTy"))


def tot_nhat(diem: list, hienTai=None) -> dict | None:
    """Điểm có TỔNG cao nhất mà KHÔNG tập trung hơn chỗ đang đứng.

    KHÔNG tuyên bố người thắng nếu trục bất động — cùng luật với
    `chay_lai_he.doi_chieu()`: một cỗ máy tự chấm điểm mình phải bị cấm
    cái thang điểm nó leo được bằng cách tự tháo phanh.

    Và chấm bằng TỔNG một mình cũng là một lối tháo phanh. Đo làn thật
    05/09/2026 trên `ruiRoTong.tranMotCang`:

        0.35 (đang dùng)   311,19 USD/giờ   tỉ trọng ty 47,4%
        0.45               312,41 USD/giờ   tỉ trọng ty 57,1%   ← thắng
                                              theo TỔNG

    Hơn **0,39%** thu, đổi lấy **gần mười điểm** tập trung. Chính cỗ máy
    này gọi thế là `b-tot-hon-NHUNG-dam-hon`, và `cong_duyet` LOẠI nó
    (`KET_LUAN_QUA = ("b-tot-hon",)`). Nên bảng quét trục trước lượt này
    đội vương miện cho đúng thứ cổng duyệt sẽ từ chối — hai cái thước
    trong cùng một cỗ máy nói hai câu khác nhau.

    `hienTai` là điểm ĐANG ĐỨNG. Không có nó — hoặc giá trị đang dùng
    không nằm trên lưới — thì không có mốc so, nên KHÔNG loại ai: bịa ra
    một cái mốc còn tệ hơn không có mốc (xem `truc-nut-lech-luoi`). Chỗ
    ấy khai bằng `thieuMoc`.
    """
    co = [x for x in diem if x.get("tongUsdMoiGio") is not None]
    if not co or bat_dong(diem):
        return None
    dan = sorted(co, key=lambda x: -x["tongUsdMoiGio"])
    moc = None
    if hienTai is not None:
        for x in diem:
            if _gan_gia_tri(x.get("giaTri"), hienTai):
                moc = x
                break
    if moc is None:
        ra = dict(dan[0])
        ra["thieuMoc"] = True
        return ra
    loai = []
    for x in dan:
        if x is moc or not dam_hon(x, moc):
            ra = dict(x)
            ra["thieuMoc"] = False
            if loai:
                ra["quanQuanBiLoai"] = loai
            return ra
        loai.append({"giaTri": x.get("giaTri"),
                     "tongUsdMoiGio": x.get("tongUsdMoiGio"),
                     "tiTrongTy": x.get("tiTrongTy"),
                     "tiTrongCang": x.get("tiTrongCang")})
    return None


def _gan_gia_tri(a, b) -> bool:
    if a is None or b is None:
        return a is b
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return a == b


def doi_chieu_hai_cua_so(a: dict, b: dict) -> dict:
    """Hai cửa sổ có nói cùng một câu không.

    `dongY=False` nghĩa là CẢ HAI chưa dùng được, không phải cái nào đúng.
    """
    ta, tb = a.get("totNhat"), b.get("totNhat")
    if a.get("batDong") and b.get("batDong"):
        return {"dongY": True, "batDong": True, "giaTri": None,
                "vi": "cả hai cửa sổ đều nói núm này KHÔNG ràng buộc"}
    if ta is None or tb is None:
        return {"dongY": False, "batDong": False, "giaTri": None,
                "vi": "một cửa sổ nói núm bất động, cửa kia thì không — "
                      "chưa dùng được"}
    if ta["giaTri"] != tb["giaTri"]:
        return {"dongY": False, "batDong": False, "giaTri": None,
                "vi": f"cửa sổ nhỏ chọn {ta['giaTri']}, cửa sổ gấp đôi "
                      f"chọn {tb['giaTri']} — hai câu khác nhau thì cả hai "
                      f"chưa dùng được"}
    return {"dongY": True, "batDong": False, "giaTri": ta["giaTri"],
            "vi": "hai cửa sổ cùng chọn một giá trị"}
