"""HIỆU NĂNG — đo bằng đường NAV, không bằng một APR nhân thẳng.

## Vì sao không lấy một con số phần trăm nhân lên

Vốn thật đi thế này:

    100 × 1,12 × 1,31 × 0,92 × 1,22 × 1,05

chứ không phải `100 × 1,5^5`. Một năm âm ở giữa không chỉ làm chậm — nó ăn
vào cái nền mà mọi năm sau nhân lên từ đó. Lấy một APR đẹp nhân thẳng là
giấu đúng phần ấy.

Nên bộ máy đo:

    CAGR              lợi suất gộp thật sự, không phải trung bình cộng
    SỤT VỐN TỐI ĐA    đáy sâu nhất tính từ đỉnh trước đó
    THỜI GIAN DƯỚI ĐÁY  bao lâu chưa về lại đỉnh cũ

Con số thứ hai và thứ ba là thứ quyết định người ta có giữ nổi hệ thống qua
một đợt xấu hay không, và không APR nào nói được chúng.

## NẠP VỐN không phải LỢI NHUẬN — và đây là chỗ dễ nói dối nhất

Chủ bỏ thêm 990.000 USD vào một cỗ máy đang có 10.000 thì NAV nhảy từ
10.000 lên 1.000.000. Một phép đo lấy `NAV cuối / NAV đầu` sẽ đọc cú
nhảy ấy thành **lợi nhuận gấp một trăm lần**, và nó sẽ khoe con số ấy
với đầy đủ chữ số thập phân.

Nên đường NAV phải mang theo DÒNG VỐN tại từng điểm, và lợi suất tính
theo kiểu **có trọng số thời gian**: cắt đường ở mỗi lần nạp/rút, tính
lợi suất từng đoạn trên vốn ĐANG CÓ trước dòng vốn ấy, rồi nhân chuỗi.

    đoạn i:  r_i = (NAV_cuối − dòng vốn) / NAV_đầu − 1
    cả kỳ:   (1+r_1)(1+r_2)…(1+r_k) − 1

Cách này trả lời đúng câu người ta muốn hỏi — *"tay lái này giỏi cỡ
nào"* — chứ không phải *"chủ đã bỏ vào bao nhiêu"*. Hai câu ấy khác
nhau, và chỉ câu đầu là thành tích của cỗ máy.

Sụt vốn cũng phải cắt theo dòng vốn: một cú nạp làm NAV vọt lên tạo ra
một "đỉnh" giả, và mọi ngày sau đó đọc thành đang-dưới-đỉnh.

## Chưa đủ mẫu thì NÓI CHƯA ĐỦ MẪU

Với vài giờ dữ liệu, CAGR ngoại suy ra một con số vô nghĩa và trông rất
thuyết phục — quy 0,3% của nửa ngày thành hàng nghìn phần trăm một năm.
Nên dưới `TOI_THIEU_GIO`, mọi trường tỉ suất trả `None`, và `duDeKetLuan`
là `False`. `None` chứ không phải 0: "chưa đo được" khác hẳn "bằng không".
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

#: Dưới ngần này giờ thì không quy đổi ra năm. Bảy ngày.
TOI_THIEU_GIO = 168.0

NAM_GIO = 365.0 * 24.0


@dataclass
class DuongNav:
    """Đường NAV theo thời gian, KÈM dòng vốn ngoài tại từng điểm.

    Mỗi điểm là `(lucMs, nav, dongVonUsd)`. `dongVonUsd` là tiền CHỦ bỏ
    thêm vào (dương) hay rút ra (âm) NGAY TRƯỚC điểm ấy — không phải lãi
    lỗ. Thiếu nó thì một cú nạp vốn đọc thành lợi nhuận.

    Điểm hai phần tử của bản lưu cũ vẫn nạp được: dòng vốn coi như 0, vì
    trước 29/08 chưa có đường nạp vốn nào nên đúng là không có dòng nào.
    """
    tran: int = 20_000
    diem: list = field(default_factory=list)     # [(lucMs, nav, dongVon)]

    def ghi(self, navUsd: float, lucMs: float | None = None,
            dongVonUsd: float = 0.0) -> None:
        import time
        t = lucMs if lucMs is not None else time.time() * 1000.0
        self.diem.append((float(t), float(navUsd), float(dongVonUsd)))
        if len(self.diem) > self.tran:
            # Bỏ điểm CŨ NHẤT, không bỏ ngẫu nhiên: đỉnh và đáy gần đây là
            # thứ quyết định sụt vốn, và chúng nằm ở cuối.
            self.diem = self.diem[-self.tran:]

    def do(self, vonBanDauUsd: float) -> dict:
        return do_hieu_nang(self.diem, vonBanDauUsd)


def _ba(d) -> tuple[float, float, float]:
    """Một điểm về dạng ba phần tử. Điểm cũ hai phần tử → dòng vốn 0."""
    if len(d) >= 3:
        return float(d[0]), float(d[1]), float(d[2])
    return float(d[0]), float(d[1]), 0.0


def do_hieu_nang(diem: list, vonBanDauUsd: float) -> dict:
    """`[(lucMs, nav)]` → CAGR, sụt vốn tối đa, thời gian dưới đáy."""
    if not diem:
        return {"duDeKetLuan": False, "vi": "chưa có điểm NAV nào",
                "soDiem": 0}

    ds = sorted((_ba(x) for x in diem), key=lambda x: x[0])
    t0, n0, _ = ds[0]
    t1, n1, _ = ds[-1]
    gio = (t1 - t0) / 3_600_000.0
    tongDongVon = sum(x[2] for x in ds)

    # ── sụt vốn: đáy sâu nhất tính từ ĐỈNH TRƯỚC ĐÓ ─────────────────────
    dinh = ds[0][1]
    sut_max = 0.0
    sut_luc = None
    dinh_luc = ds[0][0]
    duoi_day_lau = 0.0
    dang_duoi_tu = None
    for t, n, dv in ds:
        if dv:
            # Nạp/rút vốn dịch cả cái thang. Không dịch đỉnh theo thì một cú
            # nạp tạo ra một "đỉnh" giả, và mọi ngày sau đó đọc thành
            # đang-dưới-đỉnh trong khi cỗ máy không mất gì cả.
            dinh += dv
        if n >= dinh:
            dinh, dinh_luc = n, t
            if dang_duoi_tu is not None:
                duoi_day_lau = max(duoi_day_lau, (t - dang_duoi_tu) / 3_600_000.0)
                dang_duoi_tu = None
        else:
            if dang_duoi_tu is None:
                dang_duoi_tu = t
            s = (dinh - n) / dinh if dinh > 0 else 0.0
            if s > sut_max:
                sut_max, sut_luc = s, t
    if dang_duoi_tu is not None:
        duoi_day_lau = max(duoi_day_lau, (ds[-1][0] - dang_duoi_tu) / 3_600_000.0)

    # Lợi suất CÓ TRỌNG SỐ THỜI GIAN: cắt ở mỗi dòng vốn, tính từng đoạn
    # trên vốn ĐANG CÓ, rồi nhân chuỗi. Không thế thì một cú nạp 990.000
    # vào một cỗ máy 10.000 đọc thành lợi nhuận gấp trăm lần.
    tich = 1.0
    truoc = ds[0][1]
    doDuocChuoi = True
    for t, nav, dv in ds[1:]:
        if truoc <= 0:
            doDuocChuoi = False
            break
        tich *= (nav - dv) / truoc
        truoc = nav
    ra = {
        "soDiem": len(ds), "soGio": gio,
        "navDau": n0, "navCuoi": n1, "vonBanDauUsd": float(vonBanDauUsd),
        "dongVonNgoaiUsd": tongDongVon,
        # `laiLoPhanTram` là lợi suất CỦA TAY LÁI — đã trừ mọi đồng chủ bỏ
        # thêm vào. `None` khi có một đoạn NAV không dương, vì lúc ấy phép
        # nhân chuỗi không nói được gì.
        "laiLoPhanTram": ((tich - 1.0) * 100.0) if doDuocChuoi else None,
        "laiLoGomNapVonPhanTram": ((n1 / float(vonBanDauUsd) - 1.0) * 100.0
                                   if vonBanDauUsd else None),
        "sutVonToiDaPhanTram": sut_max * 100.0,
        "sutVonLuc": _iso(sut_luc) if sut_luc else None,
        "gioDuoiDayLauNhat": duoi_day_lau,
        "dangDuoiDay": ds[-1][1] < dinh - 1e-9,
    }

    # ── CAGR: chỉ khi đủ mẫu ────────────────────────────────────────────
    if gio < TOI_THIEU_GIO:
        ra.update({
            "duDeKetLuan": False, "cagrPhanTram": None,
            "vi": f"mới {gio:.1f} giờ dữ liệu, cần ≥ {TOI_THIEU_GIO:.0f} — "
                  f"quy một con số nửa ngày ra năm cho một tỉ suất vô nghĩa "
                  f"mà trông rất thuyết phục"})
        return ra

    if n0 <= 0 or n1 <= 0:
        ra.update({"duDeKetLuan": False, "cagrPhanTram": None,
                   "vi": "NAV không dương, không tính gộp được"})
        return ra

    nam = gio / NAM_GIO
    if not doDuocChuoi:
        ra.update({"duDeKetLuan": False, "cagrPhanTram": None,
                   "vi": "có đoạn NAV không dương — phép nhân chuỗi không "
                         "nói được gì"})
        return ra
    # CAGR gộp từ TÍCH CHUỖI, không từ `n1/n0`: `n1/n0` gồm cả tiền chủ bỏ
    # thêm vào, và đó không phải thành tích của cỗ máy.
    ra.update({"duDeKetLuan": True,
               "cagrPhanTram": (tich ** (1.0 / nam) - 1.0) * 100.0,
               "vi": ""})
    return ra


def _iso(ms: float) -> str:
    return _dt.datetime.fromtimestamp(
        ms / 1000.0, _dt.timezone.utc).isoformat(timespec="seconds")


def doi_chieu_giay_that(so_cai) -> dict:
    """Giấy nói một đằng, thật nói một nẻo? — thước nghiệm thu của $100.

    Bản đồ đặt đúng câu hỏi: nếu sổ giấy ra +18% mà tiền thật ra +2% thì mô
    phỏng đang nói dối, và biết được điều ấy đáng giá hơn cả hai con số.

    Ở bản này **chưa có lệnh thật nào** — `thuc_thi.moPhong` là True cứng.
    Nên hàm này trả về "chưa đối chiếu được", và đó là câu trả lời ĐÚNG, chứ
    không phải một con số 0 giả vờ là kết quả.

    Nó tồn tại để chỗ ấy có sẵn khi lớp ký lệnh tới, và để không ai dựng một
    bảng đối chiếu bịa trong lúc chờ.
    """
    try:
        theo = so_cai.tom_tat().get("theoLoai") or {}
    except Exception:                                     # noqa: BLE001
        theo = {}
    so_but = sum(int((v or {}).get("so") or 0) for v in theo.values())
    return {
        "doiChieuDuoc": False,
        "soButToanGiay": so_but,
        "soButToanThat": 0,
        "vi": "chưa có lệnh thật nào — `thuc_thi.moPhong` là True CỨNG và "
              "không cấu hình nào tắt được. Đối chiếu giấy ↔ thật chỉ có "
              "nghĩa khi cả hai vế cùng tồn tại.",
        "khiNaoDoDuoc": "khi lớp ký lệnh tồn tại và đã có đủ lệnh thật để "
                        "so — trước đó, mọi con số 'sai lệch' đều là bịa.",
    }
