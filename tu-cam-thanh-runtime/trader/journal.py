"""JOURNAL + MEMORY — bốn loại trí nhớ, và phép truy hồi đưa chúng trở lại brain.

    EPISODIC   từng giao dịch, nguyên trạng                (trades.jsonl)
    SEMANTIC   bài học đã hậu kiểm                         (lessons.jsonl)
    PROCEDURAL chiến lược / kỹ năng                        (skills/, config.json)
    PERFORMANCE chiến lược nào hiệu quả trong regime nào    (tính từ trades.jsonl)

Trí nhớ chỉ có giá trị nếu được TRUY HỒI ĐÚNG LÚC. `recall()` dưới đây lọc theo
regime hiện tại trước, rồi mới tới bài học chung — nhét cả nghìn bài học vào mỗi
prompt thì vừa đắt vừa loãng, và bài học đúng chìm nghỉm giữa bài học lạc đề.
"""
from __future__ import annotations

from collections import defaultdict

from . import store


def _stats(trades: list[dict]) -> dict:
    closed = [t for t in trades if t.get("status") == "CLOSED" and t.get("pnl") is not None]
    if not closed:
        return {"count": 0, "wins": 0, "winRate": None, "expectancyR": None,
                "totalPnl": 0.0, "avgWinR": None, "avgLossR": None, "maxLossR": None}
    wins = [t for t in closed if t["pnl"] > 0]
    losses = [t for t in closed if t["pnl"] <= 0]
    rs = [t.get("rMultiple") or 0 for t in closed]
    win_rs = [t.get("rMultiple") or 0 for t in wins]
    loss_rs = [t.get("rMultiple") or 0 for t in losses]
    return {
        "count": len(closed),
        "wins": len(wins),
        "winRate": round(len(wins) / len(closed) * 100, 1),
        "expectancyR": round(sum(rs) / len(rs), 3),
        "totalPnl": round(sum(t["pnl"] for t in closed), 2),
        "avgWinR": round(sum(win_rs) / len(win_rs), 2) if win_rs else None,
        "avgLossR": round(sum(loss_rs) / len(loss_rs), 2) if loss_rs else None,
        "maxLossR": round(min(rs), 2) if rs else None,
    }


def performance() -> dict:
    """PERFORMANCE MEMORY — cắt theo regime và theo chiến lược."""
    trades = store.read_all(store.TRADES)
    by_regime: dict[str, list] = defaultdict(list)
    by_strategy: dict[str, list] = defaultdict(list)
    for t in trades:
        by_regime[t.get("regimeAtEntry") or "UNKNOWN"].append(t)
        by_strategy[t.get("strategy") or "UNKNOWN"].append(t)
    return {
        "overall": _stats(trades),
        "byRegime": {k: _stats(v) for k, v in sorted(by_regime.items())},
        "byStrategy": {k: _stats(v) for k, v in sorted(by_strategy.items())},
    }


def _chon(lessons: list[dict], regime_key: str, regime_primary: str, limit: int) -> list[dict]:
    same_key = [l for l in lessons if l.get("regimeKey") == regime_key]
    same_regime = [l for l in lessons if l.get("regime") == regime_primary and l not in same_key]
    # Bài học nói "phải đổi chiến lược" luôn được ưu tiên — đó là loại bài học
    # đắt nhất, mua bằng một chuỗi lệnh sai chứ không phải một lệnh xui.
    flagged = [l for l in lessons
               if l.get("change_strategy") and l not in same_key and l not in same_regime]
    return (same_key[-limit:] + same_regime[-3:] + flagged[-3:])[-limit - 6:]


def _gon(l: dict) -> dict:
    return {
        "at": l.get("at"), "regime": l.get("regime"), "side": l.get("side"),
        "rMultiple": l.get("rMultiple"), "classification": l.get("classification"),
        "lesson": l.get("lesson"), "changeStrategy": l.get("change_strategy"),
    }


def recall(regime_key: str, regime_primary: str, limit: int = 6) -> dict:
    """Gói trí nhớ đưa vào prompt: bài học hợp regime trước, bài học chung sau.

    Trả về HAI kho tách bạch, không gộp:

        lessonsForThisRegime      từ lệnh THẬT
        lessonsFromReplay         đúc từ chạy lại lịch sử

    Tách vì độ tin cậy khác nhau, và vì bộ não cần biết mình đang đọc loại nào.
    Lệnh chạy lại khớp đúng giá đặt, không nhảy giá qua stop, không khớp một
    phần — chúng nói đúng về CẤU TRÚC ("chế độ này lỗ đều") và nói sai về ĐỘ LỚN.
    Gộp chung thì con số 300 bài học trông như bằng chứng mạnh trong khi phần lớn
    chỉ là một lần bấm nút.
    """
    that = store.read_all(store.LESSONS)
    chay_lai = store.read_all(store.LESSONS_CHAY_LAI)
    perf = performance()
    return {
        "note": "Bài học là quan sát trong quá khứ, không phải quy tắc. Nói rõ nếu bạn bỏ qua một bài học và vì sao.",
        "lessonsForThisRegime": [_gon(l) for l in _chon(that, regime_key, regime_primary, limit)],
        "replayNote": (
            "Những bài học dưới đây đúc từ CHẠY LẠI LỊCH SỬ, không phải lệnh thật. "
            "Trong mô phỏng, lệnh khớp đúng giá đặt và không có nhảy giá qua stop, "
            "nên hãy tin phần CẤU TRÚC (chế độ nào ăn, chế độ nào lỗ, mẫu lặp lại) "
            "và đừng tin phần ĐỘ LỚN (số R cụ thể sẽ xấu hơn ngoài thực tế)."
        ),
        "lessonsFromReplay": [_gon(l) for l in _chon(chay_lai, regime_key, regime_primary, limit)],
        "performanceOverall": perf["overall"],
        "performanceThisRegime": perf["byRegime"].get(regime_primary, {"count": 0}),
        "totalLessonsStored": len(that),
        "totalReplayLessons": len(chay_lai),
    }


def recent_trades(n: int = 25) -> list[dict]:
    return store.read_all(store.TRADES)[-n:][::-1]


def recent_lessons(n: int = 25) -> list[dict]:
    return store.read_all(store.LESSONS)[-n:][::-1]


def recent_theses(n: int = 25) -> list[dict]:
    return store.read_all(store.THESES)[-n:][::-1]
