"""SO HAI LÀN — làn chính (spot, chỉ LONG) cạnh làn demo (paper, hai chiều).

    python scripts/so-hai-lan.py

VÌ SAO CẦN MỘT LỆNH RIÊNG

Toàn bộ lợi thế đo được của hệ này nằm ở nửa SHORT: MOCK_KEO_LUI_V1 trên 33 chợ
1d chưa từng dùng cho SHORT +0,303R/226 lệnh và LONG −0,306R/44 lệnh. Làn chính
chạy sàn spot testnet nên `risk.py` chặn SHORT — nó chạy đúng nửa lỗ. Làn demo
(cổng 5282, chế độ `paper`, sổ `data-hai-chieu/`) chạy được cả hai chiều.

Phép đo ấy sẽ kéo hàng THÁNG: nhịp lệnh đo được là ~0,015 lệnh/chợ/ngày, nên 30
lệnh SHORT trên 15 chợ mất khoảng 5 tháng. Một phép đo dài như thế mà phải gõ
sáu lệnh mới đọc được thì sẽ không ai đọc, và giả thuyết
«keo-lui-short-tien-tuong» sẽ chết già trong sổ.

CÁI SỐ NÀY KHÔNG NÓI ĐƯỢC

Hai làn KHÔNG so được trực tiếp: khác sàn (thật/giấy), khác bộ luật, khác hướng.
Đặt cạnh nhau là để thấy NHỊP và HƯỚNG, không phải để tuyên bố làn nào hơn. Cột
duy nhất so được là kỳ vọng R của cùng một hướng trên cùng một khoảng thời gian,
và cả hai làn đều chưa đủ lệnh cho việc đó.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

NL = chr(10)
# Mỗi làn khai luôn TÊN FILE tài khoản của nó. Hai sàn ghi hai file khác nhau
# (`broker_testnet.ACCOUNT_FILE` vs `store.ACCOUNT`), và đoán bằng "file nào có
# trước" thì làn demo sẽ đọc trúng file của sàn giấy trong sổ của làn CHÍNH —
# bản đầu của script này đọc vốn 10.093 trong khi buồng lái báo 9.720.
LAN = (("làn CHÍNH  (spot testnet · chỉ LONG)", GOC / "data",
        "account_testnet.json", 5182),
       ("làn DEMO   (paper · hai chiều)", GOC / "data-hai-chieu",
        "account.json", 5282))


def _von(cong: int, tk: dict) -> tuple[str, str]:
    """Vốn của làn, và NÓ ĐẾN TỪ ĐÂU.

    Sổ trên đĩa KHÔNG đủ để nói vốn: sàn testnet lưu tiền quote + danh sách vị
    thế và không lưu `equity` nào cả, còn sàn giấy lưu `equity` CHƯA CHẤM GIÁ —
    tức thiếu lãi/lỗ của vị thế đang mở. Buồng lái thì chấm giá mỗi vòng.

    Nên hỏi buồng lái trước, và khi nó không trả lời thì NÓI RÕ con số đang
    thiếu gì, chứ không in một số trần trụi trông như đã đủ.
    """
    try:
        import urllib.request

        with urllib.request.urlopen(f"http://localhost:{cong}/api/state",
                                    timeout=4) as r:
            import json as _j

            a = _j.loads(r.read().decode("utf-8")).get("account") or {}
        v = a.get("equityMarked", a.get("equity"))
        if isinstance(v, (int, float)):
            return f"{v:,.2f}", f"buồng lái :{cong}"
    except Exception:  # noqa: BLE001 — làn không chạy thì rơi về sổ
        pass
    v = tk.get("equity")
    if isinstance(v, (int, float)):
        return f"{v:,.2f}", "sổ trên đĩa · CHƯA chấm giá vị thế đang mở"
    return "—", f"làn không chạy ở :{cong} và sổ không lưu vốn"


def _doc(thu_muc: Path, ten_tk: str) -> dict | None:
    """Đọc sổ của MỘT làn. Nạp lại module vì DATA_DIR chốt lúc import."""
    os.environ["TCT_DATA_DIR"] = str(thu_muc)
    for ten in [k for k in list(sys.modules) if k.startswith("trader")]:
        del sys.modules[ten]
    from trader import chien_luoc, store          # noqa: PLC0415
    from trader.journal import performance        # noqa: PLC0415

    if not thu_muc.exists():
        return None
    ds = store.read_all(store.TRADES)
    tk = store.read_json(ten_tk, None) or {}
    return {"hieuNang": performance(), "soLenh": len(ds),
            # Vị thế đang mở nằm ở FILE TÀI KHOẢN, không phải ở sổ lệnh: sổ chỉ
            # nhận bản ghi khi lệnh đã đóng. Đếm bằng sổ thì luôn ra 0.
            "dangMo": len(tk.get("positions") or []),
            "boLuat": (chien_luoc.doc().get("champion") or {}).get("ma"),
            "huongHieuLuc": _huong_hieu_luc(chien_luoc.doc()),
            "banGhiChampion": _lech_bang_chung(chien_luoc.doc(),
                                              _khung_cua_lan(thu_muc)),
            "huong": {h: sum(1 for t in ds if t.get("side") == h)
                      for h in ("LONG", "SHORT")},
            "taiKhoan": tk}


def _khung_cua_lan(thu_muc: Path) -> str | None:
    """Khung mà LÀN NÀY chạy, đọc từ file cấu hình của chính nó.

    Không dùng `CONFIG` toàn cục: tiến trình này đọc cả hai làn, mà mỗi làn có
    một file cấu hình riêng — lấy CONFIG toàn cục là gán khung của làn này cho
    làn kia, đúng loại lỗi mà hàm dưới sinh ra để bắt.
    """
    ten = ("config-hai-chieu.json" if thu_muc.name == "data-hai-chieu"
           else "config.json")
    f = thu_muc.parent / ten
    if not f.exists():
        return None
    try:
        return (json.loads(f.read_text(encoding="utf-8"))
                .get("timeframes", {}).get("primary"))
    except (OSError, ValueError):
        return None


def _lech_bang_chung(d: dict, khung_chay: str | None) -> str | None:
    """Bản ghi champion có đo trên ĐÚNG cấu hình mà làn này đang chạy không?

    `chien_luoc` ghi `cho`/`khung` bằng `setdefault` từ CONFIG LÚC GHI. Nếu bản
    ghi được tạo bởi một tiến trình chạy cấu hình khác — hoặc làn đổi khung sau
    khi tôn champion — thì con số nằm đó mãi mãi mà không ai biết nó nói về thứ
    khác. Làn demo KHÔNG chạy nghi thức nên `ketQua` của nó không bao giờ được
    đo lại; đây là ca đúng như vậy.

    Ca thật 05/09/2026: làn demo chạy `1d` trên 90 chợ, mà champion của nó ghi
    `cho="BTCUSDT:4h"`, `khung="4h"` — tức bằng chứng của làn CHÍNH, một chợ.
    Bản ghi nói −0,314R; chạy lại đúng bộ luật ấy trên 1d qua 35 và 39 chợ lạ
    cho +0,139R và +0,205R. Không con số nào sai, chúng nói về hai thứ khác
    nhau — và suýt dẫn tới một kết luận ngược.

    Trả về câu cảnh báo, hoặc None nếu khớp. KHÔNG chặn gì: đây là tầng hiển
    thị, việc của nó là làm chỗ lệch NHÌN THẤY ĐƯỢC chứ không phải quyết định
    thay người đọc.
    """
    kq = ((d.get("champion") or {}).get("ketQua")) or {}
    if not kq:
        return None
    khung_ghi = kq.get("khung")
    cho_ghi = kq.get("cho")
    if khung_ghi and khung_chay and khung_ghi != khung_chay:
        return (f"bản ghi đo khung {khung_ghi} (chợ {cho_ghi}) nhưng làn này "
                f"chạy khung {khung_chay} — con số dưới đây KHÔNG nói về làn này")
    if cho_ghi and ":" in str(cho_ghi) and str(cho_ghi).count(",") == 0:
        return (f"bản ghi đo trên MỘT chợ ({cho_ghi}) — đừng đọc nó như kết quả "
                f"của cả làn")
    return None


def _huong_hieu_luc(d: dict) -> str | None:
    """Hướng mà champion THẬT SỰ được phép đánh, đọc từ `tham.cheDoVao`.

    Nhãn của làn trong `LAN` nói về SÀN cho phép gì; nó không đổi khi ai đó khoá
    hướng ở tầng bộ luật. Ngày 05/09/2026 làn demo bị đặt `cheDoVao:
    ["TREND_DOWN"]` (bỏ nửa LONG vì nó âm −0,157 và −0,170 trên hai tập chợ lạ)
    mà nhãn vẫn ghi "hai chiều" — bảng nói một đằng, hệ chạy một nẻo, đúng họ
    lỗi mà `_lech_bang_chung` ở trên dựng ra để bắt.
    """
    ch = (d.get("champion") or {}).get("tham") or {}
    che = ch.get("cheDoVao")
    if not che:
        return None
    ten = {"TREND_UP": "LONG", "TREND_DOWN": "SHORT"}
    co = [ten.get(x, x) for x in che]
    if len(co) == 1:
        return f"bộ luật KHOÁ hướng: chỉ {co[0]} (cheDoVao={che})"
    return f"bộ luật cho phép: {', '.join(co)}"


def _pheu(thu_muc: Path) -> str | None:
    """Bao nhiêu luận điểm thành lệnh, bao nhiêu bị tầng rủi ro chặn.

    VÌ SAO IN RA: bản chạy lại khớp đúng giá mà luận điểm đọc, nên nó KHÔNG BAO
    GIỜ gặp cửa `GIA_DA_CHAY` (`maxTroiGiaAtr`). Nó tính vào thống kê những lệnh
    mà bản thật từ chối. Đo 05/09/2026 bằng biến thay thế
    `|close(i+1) − close(i)| / ATR(i)`: **~30% lệnh trong bản chạy lại bị cửa
    này chặn ở bản thật** — 33,1% và 30,2% trên hai tập chợ độc lập. Và 30% là
    SÀN, vì biến thay thế ấy đánh giá thấp độ trôi thật (bot có thể hành động
    nhiều giờ sau khi nến đóng; ca TUSDT 03/09 trôi +46% trong ngày).

    Hệ quả: **đừng suy nhịp lệnh thật từ số lệnh trong bản chạy lại.** Nhịp chạy
    lại dự đoán 1,15 lệnh/ngày cho làn demo, nhịp thật đo được 0,36.

    Còn CHƯA xác lập, đừng đọc rộng hơn: nhóm bị chặn có kỳ vọng khác nhóm qua
    được hay không. Hai tập bất đồng hẳn (−0,0021R và +0,1859R), nên chỗ lệch
    này mới chỉ chắc về SỐ LƯỢNG, chưa chắc về GIÁ TRỊ.

    Đọc từ nhật ký chứ không từ sổ: sổ chỉ ghi lệnh ĐÃ VÀO, nên tự nó không bao
    giờ kể được phần bị chặn.
    """
    f = thu_muc / "nhat-ky" / "runtime.log"
    if not f.exists():
        return None
    try:
        dong = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    mo = sum(1 for d in dong if "mo-vi-the" in d)
    tu_choi = [d for d in dong if "tu-choi" in d]
    if not mo and not tu_choi:
        return None
    ly_do: dict[str, int] = {}
    for d in tu_choi:
        for ma in ("GIA_DA_CHAY", "SL_SAI_PHÍA", "SL_QUÁ_RỘNG", "SL_QUÁ_HẸP",
                   "SPOT_KHONG_SHORT", "RR_THẤP", "CONFIDENCE_THẤP"):
            if ma in d:
                ly_do[ma] = ly_do.get(ma, 0) + 1
                break
    dau = ""
    if ly_do:
        ten, so = max(ly_do.items(), key=lambda x: x[1])
        dau = f" · đầu bảng {ten} ×{so}"
    return f"mở {mo} · tầng rủi ro CHẶN {len(tu_choi)}{dau}"


def _nhip(thu_muc: Path, ten_tk: str) -> str:
    """Nhịp lệnh THẬT của làn, và bao lâu nữa đủ 30 lệnh SHORT.

    Ước lượng ban đầu — ~6 tuần trên 46 chợ — suy từ nhịp luật nổ trong bản chạy
    lại (0,015 lệnh/chợ/ngày). Một ước lượng suy từ chạy lại có thể sai vài lần:
    bản chạy lại không có `maxOpenPositions`, không bỏ lỡ tín hiệu vì hết chỗ,
    và không có vòng lặp 60 giây bỏ sót nến.

    Nên in nhịp ĐO ĐƯỢC cạnh nó. Nếu hai con số lệch nhau nhiều thì cái sai là
    ước lượng, và ghi chú trong bản khai giả thuyết phải được đọc lại — chứ
    không phải im lặng chờ thêm ba tháng.
    """
    import datetime as _dt

    os.environ["TCT_DATA_DIR"] = str(thu_muc)
    for ten in [k for k in list(sys.modules) if k.startswith("trader")]:
        del sys.modules[ten]
    from trader import store                       # noqa: PLC0415

    tk = store.read_json(ten_tk, None) or {}
    ds = [t for t in store.read_all(store.TRADES) if t.get("closedAt")]
    # `createdAt` chỉ có sau khi sàn ghi tài khoản lần đầu, mà sàn giấy chỉ ghi
    # khi có gì đó ĐỔI. Làn vừa bật thì chưa có file nào — và "chưa rõ tuổi sổ"
    # đọc như một lỗi trong khi đó là trạng thái đúng và bình thường.
    tao = tk.get("createdAt") or min(
        (t.get("openedAt") for t in ds if t.get("openedAt")), default=None)
    if not tao:
        return "chưa có lệnh nào — nhịp tính được sau lệnh đầu tiên"
    try:
        t0 = _dt.datetime.fromisoformat(str(tao))
        if t0.tzinfo is None:
            t0 = t0.replace(tzinfo=_dt.timezone.utc)
        ngay = (_dt.datetime.now(_dt.timezone.utc) - t0).total_seconds() / 86400
    except (ValueError, TypeError):
        return f"mốc mở sổ không đọc được ({tao!r})"
    if ngay < 0.5:
        return f"sổ mới {ngay * 24:.1f} giờ — chưa đủ để nói nhịp"
    n_s = sum(1 for t in ds if t.get("side") == "SHORT")
    nhip = len(ds) / ngay
    if not n_s:
        return (f"{len(ds)} lệnh trong {ngay:.1f} ngày = {nhip:.2f} lệnh/ngày · "
                f"chưa lệnh SHORT nào")
    con = max(0, 30 - n_s) / (n_s / ngay)
    return (f"{len(ds)} lệnh trong {ngay:.1f} ngày = {nhip:.2f} lệnh/ngày · "
            f"SHORT {n_s / ngay:.2f}/ngày ⇒ còn ~{con:.0f} ngày cho đủ 30")


def _huong_r(thu_muc: Path, huong: str) -> tuple[float | None, int]:
    """Kỳ vọng R của MỘT hướng, chỉ lệnh đóng tự nhiên."""
    os.environ["TCT_DATA_DIR"] = str(thu_muc)
    for ten in [k for k in list(sys.modules) if k.startswith("trader")]:
        del sys.modules[ten]
    from trader import store                       # noqa: PLC0415
    from trader.journal import LY_DO_TU_NHIEN      # noqa: PLC0415

    # Trường là `rMultiple`. Bản đầu đọc `t["R"]` — không có key ấy trong sổ, nên
    # danh sách luôn rỗng và mọi hướng đều in "—". Không lỗi, chỉ là một bảng
    # trống nhìn y hệt "chưa có lệnh nào".
    r = [t["rMultiple"] for t in store.read_all(store.TRADES)
         if t.get("closedAt") and t.get("rMultiple") is not None
         and (t.get("exitReason") or "STOP_LOSS") in LY_DO_TU_NHIEN
         and t.get("side") == huong]
    return (sum(r) / len(r) if r else None), len(r)


def main() -> int:
    print(NL + "  HAI LÀN" + NL + "  " + "─" * 62)
    for nhan, tm, ten_tk, cong in LAN:
        d = _doc(tm, ten_tk)
        if d is None:
            print(f"{NL}  {nhan}{NL}    chưa có sổ ({tm.name}/)")
            continue
        o = d["hieuNang"]["overall"]
        tk = d["taiKhoan"]
        von, tu_dau = _von(cong, tk)
        kv = o.get("expectancyR")
        print(f"{NL}  {nhan}")
        print(f"    bộ luật     {d['boLuat']}")
        if d.get("banGhiChampion"):
            print(f"    ⚠ {d['banGhiChampion']}")
        print(f"    vốn         {von:>12}    · đang mở {d['dangMo']}")
        print(f"                ({tu_dau})")
        print(f"    lệnh        {d['soLenh']} (LONG {d['huong']['LONG']} · "
              f"SHORT {d['huong']['SHORT']})")
        print(f"    đóng tự nhiên {o.get('count', 0)} lệnh · kỳ vọng "
              + (f"{kv:+.4f}R" if kv is not None else "— (chưa đủ)"))
        for h in ("LONG", "SHORT"):
            r, n = _huong_r(tm, h)
            print(f"      {h:<6} {n:>4} lệnh · "
                  + (f"{r:+.4f}R" if r is not None else "—"))
        print(f"    nhịp        {_nhip(tm, ten_tk)}")
        if d.get("huongHieuLuc"):
            print(f"    ⚠ {d['huongHieuLuc']}")
        _ph = _pheu(tm)
        if _ph:
            print(f"    phễu        {_ph}")

    print(NL + "  " + "─" * 62)
    print("  Hai làn KHÔNG so trực tiếp được: khác sàn, khác bộ luật, khác")
    print("  hướng. Cột đáng đọc là NHỊP lệnh và kỳ vọng của TỪNG hướng.")
    print("  Giả thuyết đang chờ: keo-lui-short-tien-tuong — cần 30 lệnh SHORT.")
    print("  Ước lượng lúc khai (~6 tuần) suy từ nhịp trong bản CHẠY LẠI. Nhịp")
    print("  THẬT của làn chính đo được 3,04 lệnh/ngày, tức nhanh hơn ước lượng")
    print("  ấy hơn mười lần — bản chạy lại không bỏ lỡ tín hiệu vì hết chỗ và")
    print("  không có vòng lặp 60 giây. Đọc dòng «nhịp» ở trên, đừng đọc ước")
    print("  lượng cũ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
