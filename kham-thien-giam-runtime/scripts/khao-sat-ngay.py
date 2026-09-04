"""KHẢO SÁT NGÀY — cho mô hình ngôn ngữ phán, GHI TRƯỚC, chấm SAU.

    python scripts/khao-sat-ngay.py --kho          # chọn mẫu, KHÔNG gọi model
    python scripts/khao-sat-ngay.py                # phán và ghi vào sổ
    python scripts/khao-sat-ngay.py --cham         # chấm những phán đã ngã ngũ
    python scripts/khao-sat-ngay.py --tu-tep=data/gamma-mau.json

## Đây KHÔNG phải "hôm nay nên chơi lĩnh vực nào"

Câu ấy nghe hay và sai theo một kiểu đắt: quét vài trăm market rồi chọn
cái trông ngon nhất là một lượt rút thăm vài trăm lần. Cùng cỗ máy đã
buộc cổng tiến hoá phải siết biên theo `log(số ứng viên)`, phóng to
mười lần, và không có gì bắt lại được.

Script này làm chuyện NGƯỢC LẠI: nó chọn mẫu TRƯỚC khi biết mô hình
nghĩ gì, chọn bằng một hạt giống suy từ NGÀY chứ không từ chất lượng
market, rồi bắt mô hình phán trên đúng mẫu ấy — kể cả những cái mô hình
chẳng có gì để nói. Một cái sổ chỉ ghi những lần mình thấy tự tin thì
không chấm được.

## Ba luật của cái sổ, và vì sao từng luật có mặt

1. **Ghi trước, chấm sau.** `so_phan_doan.them()` từ chối bản ghi kèm
   sẵn `ketQua`. Không có dấu thời gian thì mọi thành tích đều là kể
   chuyện sau khi biết đáp án.

2. **Mốc so là GIÁ CHỢ, không phải tỉ lệ nền.** Đánh bại tỉ lệ nền là
   chuyện dễ. Cổng `du_de_dat_cuoc` chỉ mở theo cái thứ hai. Nên mọi
   phán đoán phải mang theo giá chợ LÚC PHÁN — thiếu nó thì bản ghi ấy
   vô dụng vĩnh viễn, không cứu lại được.

3. **Chưa đủ thành tích thì trọng số bằng 0, không phải "nhỏ".** Cùng
   tinh thần `HieuChinh.du_de_dung_kelly`.

## Vì sao chỉ lấy market ở khoảng giá GIỮA

Chợ yết 0,99 thì mô hình gật theo cũng được điểm Brier rất đẹp mà không
nói thêm gì. Đúng chỗ đo được đóng góp thật là chỗ chợ CHƯA CHẮC. Bên
họ nhiệt độ đã thấy y hệt: |z| lớn cho kỹ năng +84%, còn ô duy nhất có
tiền là ô |z| < 0,25 với +1,9%.

## Vì sao KHÔNG cho mô hình biết giá chợ

Cho biết thì nó neo vào đó, và điểm kỹ năng so với chợ đo được sẽ tiến
về 0 vì một lý do chẳng liên quan gì tới việc nó giỏi hay dở.

## Chấm bằng gì

Bằng chính KẾT QUẢ NGÃ NGŨ của market. Với một câu hỏi "market này sẽ
ngã về YES chứ?", sự thật nền đúng là phán quyết của chính chợ ấy —
không cần dựng nguồn riêng cho từng họ.

## Chưa chạy online được

Cần `gamma-api.polymarket.com`, đúng tên máy đang bị chặn theo SNI (xem
`//proxyChanDoan` trong config.json). Dùng `--tu-tep` để chạy và kiểm
ngay bây giờ; có `nguon.proxy` rồi thì bỏ cờ ấy đi là xong.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "tu-tep": "đọc market từ file JSON thay vì gọi mạng",
    "kho": (tham_so.BAT, "chỉ chọn mẫu và in ra, KHÔNG gọi mô hình, "
                         "KHÔNG ghi sổ"),
    "cham": (tham_so.BAT, "chấm những phán đoán đã tới hạn, không phán thêm"),
    "so-phan": "số market đem phán trong một lượt",
    "nguon": "tên nguồn phán đoán ghi vào sổ",
}, ten='khao-sat-ngay.py')

from kham.config import CONFIG  # noqa: E402
from kham.nguon import nguon  # noqa: E402
from kham.so_phan_doan import (TOI_THIEU_NGA_NGU, PhanDoan,  # noqa: E402
                              SoPhanDoan)

TU_TEP = CO.lay("tu-tep", "")
KHO = CO.co("kho")
CHAM = CO.co("cham")
SO_PHAN = int(CO.lay("so-phan", "12"))
NGUON = CO.lay("nguon", "claude")

#: Chỉ phán ở khoảng giá GIỮA. Ngoài khoảng này chợ đã chắc, và điểm
#: đẹp kiếm được ở đó không nói lên điều gì về đóng góp thật.
GIA_THAP, GIA_CAO = 0.10, 0.90

#: Chỉ phán market ngã ngũ trong khoảng này. Quá gần thì mô hình chỉ
#: đọc lại giá; quá xa thì sổ mấy năm mới đủ dày để chấm.
NGAY_TOI_THIEU, NGAY_TOI_DA = 1.0, 45.0

#: Những HỌ có nguồn sự thật nền dày (xem `sang-ho-market.py`). Cái sổ
#: này chấm bằng phán quyết của chính chợ nên về nguyên tắc họ nào cũng
#: chấm được — nhưng một họ ngã ngũ mỗi năm một lần thì phải mấy chục
#: năm mới đủ 60 bản ghi, và trong lúc ấy không ai biết gì cả.
HO_DUOC_PHAN = ("crypto", "co-phieu", "thoi-tiet", "the-thao", "esport",
                "kinh-te")

from kham.ho_market import ho_cua  # noqa: E402,F401


def gia_cho(m: dict) -> float | None:
    """Giá YES lúc này. None khi không đọc nổi — bỏ market ấy.

    Không đoán bừa 0,5: một bản ghi thiếu giá chợ thật thì cột duy nhất
    đáng giá của cái sổ này là số bịa.
    """
    for k in ("lastTradePrice", "bestBid", "outcomePrice"):
        v = m.get(k)
        if isinstance(v, (int, float)) and 0.0 < float(v) < 1.0:
            return float(v)
    d = m.get("outcomePrices")
    if isinstance(d, str):
        try:
            d = json.loads(d)
        except json.JSONDecodeError:
            d = None
    if isinstance(d, list) and d:
        try:
            v = float(d[0])
        except (TypeError, ValueError):
            return None
        if 0.0 < v < 1.0:
            return v
    return None


def han_ms(m: dict) -> float | None:
    s = str(m.get("endDate") or "")[:10]
    if len(s) != 10:
        return None
    try:
        d = dt.date.fromisoformat(s)
    except ValueError:
        return None
    return dt.datetime(d.year, d.month, d.day,
                       tzinfo=dt.timezone.utc).timestamp() * 1000.0


def _bay_gio_iso() -> str:
    """Mốc `end_date_min` cho Gamma: bây giờ, theo ISO UTC."""
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tai_json(url: str, tham: dict, lanThu: int = 14):
    """GET qua CLIENT BỀN của runtime, thử lại khi nối hỏng. None = chịu.

    ## Vì sao không gọi `curl` mỗi lượt, và vì sao chuyện này từng bị
    ## chẩn đoán SAI thành "bị chặn"

    Từ máy này, MỞ một kết nối tới `*.polymarket.com` hỏng rất thường:
    đo 05/09/2026 bằng `httpx.get` (mỗi lượt một kết nối mới) được
    **3/12**, `curl` được **0/4**. Nhìn con số ấy rất giống một bộ lọc
    theo tên miền, và nó ĐÃ được ghi vào config lẫn sổ tay là "chặn theo
    SNI, đổi DNS hay IP đều vô ích, chỉ proxy mới xong".

    Sai. Đo lại bằng MỘT `httpx.Client` giữ nguyên qua cả loạt:
    **13/15**. Runtime đạt 672/679 vì nó vẫn luôn làm vậy. Hỏng nằm ở
    khâu THIẾT LẬP kết nối; kết nối đã dựng thì chạy bình thường.

    Bài học đắt hơn con số: một tỉ lệ hỏng cao đo bằng công cụ SAI trông
    y hệt một bức tường, và cái kết luận ấy bảo mọi phiên sau bỏ cuộc.

    Nên ở đây dùng đúng `nguon.client()` của runtime — cùng client, cùng
    proxy khai trong config, cùng User-Agent — và thử lại vài lần.
    """
    import time as _t

    c = nguon.client()
    if c is None:
        return None
    for i in range(lanThu):
        try:
            r = c.get(url, params=tham)
            r.raise_for_status()
            return r.json()
        except Exception:                            # noqa: BLE001
            if i == lanThu - 1:
                return None
            # Tỉ lệ nối được đo là ~25% mỗi lượt MỞ MỚI. Sáu lượt cho
            # 1 − 0,75^6 = 82% — tức cứ năm lần chạy thì một lần chịu
            # thua dù đường vẫn bình thường. Mười bốn lượt cho 98%.
            # Trần 4 giây để cả loạt không quá một phút.
            _t.sleep(min(4.0, 0.5 * (i + 1)))
    return None


def _tai(so: int) -> list | None:
    goc = CONFIG["nguon"]["polymarketGamma"]
    ra: list = []
    buoc = 100          # gamma chặn ở 100 và lặng lẽ cắt xuống
    for lech in range(0, so, buoc):
        d = _tai_json(f"{goc}/markets",
                      {"limit": min(buoc, so - lech), "offset": lech,
                       "closed": "false", "order": "endDate",
                       "ascending": "true",
                       # THIẾU `end_date_min` thì `ascending=true` moi
                       # trúng market ĐÃ QUÁ HẠN mà cờ vẫn `active` —
                       # đã ghi trong sổ tay, và tôi vừa đi qua nó một
                       # lần. Bảng đếm sẽ phồng lên bằng xác market.
                       "end_date_min": _bay_gio_iso()})
        if d is None:
            return ra or None
        if not isinstance(d, list) or not d:
            break
        ra.extend(d)
        if len(d) < buoc:
            break
    return ra or None


def chon_mau(ds: list, ngay: str, so: int, bayMs: float | None = None) -> list:
    """Chọn mẫu bằng HẠT GIỐNG SUY TỪ NGÀY, không từ chất lượng market.

    Đây là chỗ dễ tự lừa nhất trong cả script. Nếu mẫu được chọn theo
    "cái nào trông đáng phán" thì cái sổ chỉ chứa những lần mô hình tự
    tin, và điểm kỹ năng đo được sẽ nói về sự tự tin chứ không về sự
    đúng. Sắp theo băm của `ngày + id` là chọn ngẫu nhiên nhưng LẶP LẠI
    ĐƯỢC: chạy hai lần cùng ngày ra cùng mẫu, nên không ai bấm lại cho
    tới khi ra mẫu vừa ý.
    """
    bay = time.time() * 1000.0 if bayMs is None else float(bayMs)
    ung = []
    for m in ds:
        if not isinstance(m, dict) or m.get("closed") or m.get("resolved"):
            continue
        p = gia_cho(m)
        han = han_ms(m)
        if p is None or han is None:
            continue
        if not (GIA_THAP <= p <= GIA_CAO):
            continue
        conNgay = (han - bay) / 86_400_000.0
        if not (NGAY_TOI_THIEU <= conNgay <= NGAY_TOI_DA):
            continue
        ho = ho_cua(str(m.get("slug") or ""), str(m.get("question") or ""))
        if ho not in HO_DUOC_PHAN:
            continue
        ung.append((m, p, han, ho))
    ung.sort(key=lambda x: hashlib.sha256(
        (ngay + "|" + str(x[0].get("id") or x[0].get("slug") or "")
         ).encode("utf-8")).hexdigest())
    return ung[:so]


LOI_DAN = """Bạn đang được CHẤM ĐIỂM, không được nghe hay.

Câu hỏi: {cauHoi}
Ngã ngũ: {han}

Trả về ĐÚNG một dòng JSON, không giải thích gì ngoài JSON:
{{"p": <xác suất câu hỏi ngã về YES, số thực giữa 0.01 và 0.99>, "lyLe": "<tối đa 200 ký tự>"}}

Ba điều bị chấm nặng:
- Nói 0.5 khi không biết là hợp lệ và thường là câu trả lời đúng nhất.
- Điểm tính SO VỚI GIÁ CHỢ. Giá chợ cố ý không cho bạn biết: một con số
  đã neo thì bạn chỉ lặp lại nó.
- Tự tin mà sai bị phạt nặng hơn thận trọng mà đúng (điểm Brier)."""


def doc_phan(t: str) -> tuple[float, str] | None:
    """Bóc JSON khỏi câu trả lời. None khi không đọc nổi.

    KHÔNG rơi về 0,5 khi hỏng: một bản ghi 0,5 sinh ra từ sự cố trông y
    hệt một bản ghi 0,5 do mô hình thật sự không biết, và nó sẽ lặng lẽ
    kéo điểm kỹ năng về 0 mà không ai truy được vì sao.
    """
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        d = json.loads(t[i:j + 1])
        p = float(d["p"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if not (0.0 < p < 1.0):
        return None
    return p, str(d.get("lyLe") or "")[:200]


def hoi_model(cauHoi: str, han: str) -> tuple[float, str] | None:
    loi = LOI_DAN.format(cauHoi=cauHoi, han=han)
    try:
        r = subprocess.run(["claude", "-p", loi],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    return doc_phan((r.stdout or "").strip())


def ket_qua(m: dict) -> bool | None:
    """YES hay NO. None khi chợ đóng mà chưa công bố — chưa chấm vội.

    Ngưỡng 0,99/0,01 chứ không phải 0,5: một market đóng vì hết hạn mà
    chưa trọng tài xong vẫn còn giá lửng, và chấm theo giá lửng ấy là
    bịa ra một sự thật nền.
    """
    d = m.get("outcomePrices")
    if isinstance(d, str):
        try:
            d = json.loads(d)
        except json.JSONDecodeError:
            d = None
    if isinstance(d, list) and d:
        try:
            v = float(d[0])
        except (TypeError, ValueError):
            return None
        if v >= 0.99:
            return True
        if v <= 0.01:
            return False
    return None


def cham_lai(so: SoPhanDoan, ds: list) -> int:
    """Ngã ngũ những phán đoán tới hạn, bằng phán quyết của chính chợ."""
    theoId = {}
    for m in ds:
        if isinstance(m, dict):
            theoId[str(m.get("id") or m.get("slug") or "")] = m
    n = 0
    for pd in list(so.ds):
        if pd.ketQua is not None:
            continue
        m = theoId.get(pd.market)
        if m is None or not (m.get("closed") or m.get("resolved")):
            continue
        kq = ket_qua(m)
        if kq is None:
            continue
        so.nga_ngu(pd.id, kq)
        n += 1
    return n


def _doc_ds() -> list | None:
    if TU_TEP:
        try:
            return json.loads(Path(TU_TEP).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  không đọc được {TU_TEP}: {e}")
            return None
    return _tai(2000)


def in_bang_diem(so: SoPhanDoan, nguon: str = "") -> None:
    nguon = nguon or NGUON
    d = so.cham(nguon)
    co, ly = so.du_de_dat_cuoc(nguon)
    print()
    print("  ── SỔ ĐIỂM ──────────────────────────────────────────────")
    print(f"    tổng phán đoán   {len(so.ds)}")
    print(f"    đã ngã ngũ       {d.get('soNgaNgu', 0)}"
          f" / {TOI_THIEU_NGA_NGU} cần có")
    if d.get("brier") is not None:
        print(f"    Brier mô hình    {d['brier']:.4f}")
    if d.get("brierNen") is not None:
        print(f"    Brier tỉ lệ nền  {d['brierNen']:.4f}")
    if d.get("brierCho") is not None:
        print(f"    Brier GIÁ CHỢ    {d['brierCho']:.4f}")
    if d.get("kyNangSoCho") is not None:
        print(f"    kỹ năng so CHỢ   {d['kyNangSoCho'] * 100:+.1f}%")
    t = d.get("tin95SoCho")
    if t:
        print(f"    khoảng tin 95%   [{t[0] * 100:+.1f}%, {t[1] * 100:+.1f}%]"
              f"  ({t[2]} khối tuần)")
    print()
    print(f"    CỔNG TIỀN: {'MỞ' if co else 'ĐÓNG'} — {ly}")
    print("=" * 78)


def main() -> int:
    ngay = dt.datetime.now(dt.timezone.utc).date().isoformat()
    so = SoPhanDoan()

    print()
    print("=" * 78)
    print(f"  KHẢO SÁT NGÀY {ngay} — ghi trước, chấm sau")
    print("=" * 78)

    ds = _doc_ds()
    if ds is None:
        print()
        print("  KHÔNG TỚI ĐƯỢC `gamma-api.polymarket.com` sau 6 lượt thử.")
        print("  Đường này CHẬP CHỜN chứ không bị chặn — thử lại sau, hoặc")
        print("  chạy offline bằng --tu-tep=<file JSON>.")
        print()
        return 3
    print(f"  {len(ds):,} market đọc được")

    if CHAM:
        n = cham_lai(so, ds)
        print(f"  ngã ngũ thêm {n} phán đoán")
        in_bang_diem(so)
        return 0

    mau = chon_mau(ds, ngay, SO_PHAN)
    print(f"  mẫu hôm nay: {len(mau)} market"
          f" (giá trong [{GIA_THAP}, {GIA_CAO}],"
          f" ngã ngũ trong {NGAY_TOI_DA:.0f} ngày)")
    if not mau:
        print("  không có market nào qua bộ lọc.")
        in_bang_diem(so)
        return 0

    print()
    for m, p, han, ho in mau:
        ten = str(m.get("question") or m.get("slug") or "?")[:56]
        print(f"    {ho:<10} chợ {p:5.2f}   {ten}")

    if KHO:
        print()
        print("  --kho: dừng ở đây, KHÔNG gọi mô hình, KHÔNG ghi sổ.")
        in_bang_diem(so)
        return 0

    print()
    daGhi = hong = 0
    for m, p, han, ho in mau:
        cauHoi = str(m.get("question") or m.get("slug") or "?")
        hanTen = dt.datetime.fromtimestamp(
            han / 1000.0, dt.timezone.utc).date().isoformat()
        kq = hoi_model(cauHoi, hanTen)
        if kq is None:
            hong += 1
            print(f"    ✗ không phán được: {cauHoi[:50]}")
            continue
        pm, lyLe = kq
        maMarket = str(m.get("id") or m.get("slug") or "")
        # `id` suy từ (nguồn, NGÀY, market) chứ không từ đồng hồ: chạy
        # lại cùng ngày thì `them` thấy trùng và trả False, nên không
        # ai vô tình ghi hai lần một phán đoán rồi làm dày sổ bằng bản
        # sao của chính nó.
        if not so.them(PhanDoan(
                id=f"{NGUON}-{ngay}-{maMarket}", nguon=NGUON, ho=ho,
                market=maMarket, cauHoi=cauHoi, p=pm,
                lucMs=time.time() * 1000.0, hanMs=han,
                giaCho=p, lyLe=lyLe)):
            print(f"    · đã có trong sổ hôm nay: {cauHoi[:44]}")
            continue
        daGhi += 1
        print(f"    ✓ {pm:5.2f} (chợ {p:5.2f})  {cauHoi[:46]}")

    print()
    print(f"  ghi {daGhi} phán đoán, {hong} lượt hỏng")
    in_bang_diem(so)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
