"""Vòng lặp điều phối — cỗ máy tuần hoàn của M0.

    THẾ GIỚI → MARKET DATA → FEATURES → MARKET STATE/REGIME
             → CLAUDE BRAIN (+ MEMORY + SKILLS) → TRADE THESIS
             → RISK ENGINE → chấp nhận/từ chối → EXECUTION
             → RESULT → JOURNAL → POST-MORTEM → LESSON → MEMORY ↺

Điểm cần nhớ khi đọc: brain KHÔNG được gọi mỗi vòng lặp. Vòng lặp chạy mỗi ~20
giây để theo dõi vị thế và cập nhật dashboard, nhưng brain chỉ được đánh thức khi
có nến mới đóng / regime đổi / người dùng bấm tay, và luôn phải qua cửa hạn mức
chi phí. Gọi model mỗi vòng lặp là cách hết tiền nhanh nhất mà không thu được gì —
giữa hai nến 1H thì trạng thái thị trường gần như không đổi.
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import time as _time
import traceback

import httpx

from .brain import get_brain, mock_thesis
from .broker import PaperBroker
from .broker_testnet import TestnetBroker
from .bus import bus
from .config import CONFIG
from .data import get_market_data, data_source
from .features import build_market_state
from . import chung_cat, nghi_thuc
from .journal import recall
from .regime import classify
from .risk import RiskEngine
from . import snapshot


# Lò chưng cất chạy lại mỗi 20 phút — nguồn của nó (sổ, kho chạy lại, hồ sơ
# trader, champion) thay đổi theo giờ chứ không theo vòng.
CHUNG_CAT_MOI_GIAY = 1200


class Runtime:
    def __init__(self) -> None:
        self.cfg = CONFIG
        self.primary = CONFIG["timeframes"]["primary"]
        self.context = CONFIG["timeframes"]["context"]
        # Chọn sàn theo config. Cả hai cùng giao diện nên phần dưới không cần biết.
        #
        # Rơi về paper khi testnet không nối được là CÓ CHỦ Ý và phải ồn ào: một
        # runtime âm thầm chuyển sang tiền giả trong khi người dùng tưởng đang
        # chạy testnet là kiểu hỏng tệ nhất — mọi con số vẫn đẹp, chỉ là chúng
        # không tương ứng với lệnh nào có thật.
        self.mode = CONFIG.get("mode", "paper")
        if self.mode == "testnet":
            self.broker = TestnetBroker(CONFIG["risk"], CONFIG["symbol"])
            if not self.broker.ready:
                bus.log("system", "roi-ve-paper",
                        f"KHÔNG nối được testnet ({self.broker.last_error}) — chạy sàn giấy. "
                        f"Số liệu dưới đây là tiền giả nội bộ, KHÔNG phải lệnh trên sàn.")
                self.broker = PaperBroker(CONFIG["risk"])
                self.mode = "paper"
        else:
            self.broker = PaperBroker(CONFIG["risk"])

        self.risk = RiskEngine(CONFIG["risk"], spot_only=(self.mode == "testnet"))
        self.brain = None

        self.state: dict | None = None
        self.last_market: dict | None = None
        self.regime: dict | None = None
        self.last_thesis: dict | None = None
        self.last_decision: dict | None = None

        self.paused = False
        self.force_analyze = False
        self.last_thesis_at: _dt.datetime | None = None
        self.last_candle_seen: int | None = None
        self.last_regime_key: str | None = None
        self.ticks = 0
        self.started_at = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        # Lò chưng cất: chạy ở vòng đầu rồi định kỳ. Không chạy mỗi vòng — nó đọc
        # cả bốn kho và gộp lại, tốn hơn một lượt tick rất nhiều, mà số liệu nguồn
        # thì hàng giờ mới đổi một lần.
        self.chung_cat_luc: float | None = None
        self.chung_cat_kq: dict | None = None

    # ── Điều khiển từ dashboard ───────────────────────────────────────────
    def control(self, action: str) -> dict:
        if action == "pause":
            self.paused = True
            bus.log("system", "tam-dung", "vòng lặp tạm dừng — vị thế đang mở vẫn được theo dõi")
        elif action == "resume":
            self.paused = False
            bus.log("system", "chay-lai", "vòng lặp chạy lại")
        elif action == "analyze":
            self.force_analyze = True
            bus.log("system", "phan-tich-tay", "yêu cầu brain phân tích ngay ở vòng kế tiếp")
        elif action == "kill":
            self.risk.halted_reason = "kill switch bấm tay"
            bus.log("system", "kill-switch", "KILL SWITCH — không mở lệnh mới cho tới khi khởi động lại")
        elif action == "unkill":
            self.risk.halted_reason = None
            bus.log("system", "kill-switch-off", "gỡ kill switch")
        elif action == "reset":
            self.broker.reset()
            self.risk.halted_reason = None
        else:
            return {"ok": False, "error": f"hành động không rõ: {action}"}
        return {"ok": True, "action": action}

    # ── Quyết định CÓ gọi brain hay không ─────────────────────────────────
    def _should_call_brain(self, market: dict) -> tuple[bool, str]:
        if self.paused:
            return False, "đang tạm dừng"
        if self.force_analyze:
            return True, "người dùng bấm phân tích"

        blockers = self.risk.circuit_breakers(self.broker.snapshot(market["price"]))
        if blockers:
            return False, blockers[0]

        now = _dt.datetime.now(_dt.timezone.utc)
        if self.last_thesis_at:
            waited = (now - self.last_thesis_at).total_seconds()
            if waited < self.cfg["brain"]["minSecondsBetweenTheses"]:
                return False, f"mới phân tích {int(waited)}s trước"

        new_candle = market["lastClosedCandleTime"] != self.last_candle_seen
        regime_changed = self.regime and self.regime["key"] != self.last_regime_key

        if self.cfg["brain"]["requireNewCandle"] and not new_candle and not regime_changed:
            return False, f"chưa có nến {self.primary} mới đóng"
        if self.regime and self.regime["quality"] == "LOW" and not regime_changed:
            return False, f"regime chất lượng thấp ({self.regime['primary']}) — không đáng gọi"
        return True, "nến mới đóng" if new_candle else "regime đổi"

    # ── Một vòng ──────────────────────────────────────────────────────────
    def _chung_cat_neu_den_han(self) -> None:
        """Đúc lại phát hiện ở vòng đầu, rồi mỗi `CHUNG_CAT_MOI_GIAY` một lần.

        Đặt ngay TRƯỚC `recall()` chứ không đặt cuối vòng: nếu chưng sau khi đã
        truy hồi thì lượt này vẫn đọc phát hiện của lượt trước, và ngay sau một
        phiên huấn luyện vừa xong thì đó đúng là lượt mình cần số mới nhất.

        Nuốt lỗi có chủ ý: lò hỏng thì bộ máy mất phần trí nhớ gộp, nhưng vòng
        giao dịch vẫn phải chạy. Nuốt mà KHÔNG ghi lại thì mới là sai — nên lỗi
        được ghi vào `chung_cat_kq` để nó hiện trên bảng thay vì biến mất.
        """
        gio = _time.time()
        if self.chung_cat_luc is not None and gio - self.chung_cat_luc < CHUNG_CAT_MOI_GIAY:
            return
        self.chung_cat_luc = gio
        try:
            kq = chung_cat.chung_cat()
            self.chung_cat_kq = kq
            bus.emit("hoc", "chung-cat",
                     f"{kq['soPhatHien']} phát hiện · bỏ {kq['soDaBo']} vì chưa đủ mẫu · "
                     + " · ".join(f"{k} {v}" for k, v in sorted(kq["theoNguon"].items())),
                     chungCat=kq)
        except Exception as e:
            self.chung_cat_kq = {"loi": f"{type(e).__name__}: {e}", "soPhatHien": 0}
            bus.log("hoc", "chung-cat-loi", f"{type(e).__name__}: {e}")

    # ── QUÉT NHIỀU CHỢ ────────────────────────────────────────────────────

    def _cho_quet(self) -> list[str]:
        """Danh sách chợ được quét. Mặc định đúng một chợ — hành vi cũ y nguyên.

        Đây là trục cuối cùng còn bằng 1. Bảng đo đã mở ra 48 chợ, 4 lát thời
        gian và hàng chục biến thể tham số; riêng bot chạy thật vẫn nhìn đúng
        một coin, nên nó vào ~1,4 lệnh/ngày và mọi giả thuyết đo trên lệnh thật
        cần hàng tuần mới chốt được.
        """
        ds = self.cfg.get("symbols") or [self.cfg["symbol"]]
        # Chợ nào sàn KHÔNG nhận thì loại ngay, không để tới lúc đặt lệnh.
        #
        # `TestnetBroker` từng khoá cứng một symbol ở 11 chỗ và bản trước chặn
        # thẳng nhiều chợ ở chế độ testnet. Giờ nó nhận symbol từ chính luận
        # điểm, cộng vốn qua mọi tài sản, huỷ lệnh ở mọi chợ, và kiểm cả danh
        # sách chợ lúc nối — nên chặn không còn cần. Cái vẫn cần là loại đúng
        # những chợ sàn không có cặp.
        hong = set(getattr(self.broker, "cho_loi", None) or [])
        if hong:
            ds = [x for x in ds if not any(h.startswith(x) for h in hong)]
        # Chợ chính LUÔN đứng đầu: nó là chợ mà bảng, ảnh chụp và `/api/state`
        # nói về khi không nói rõ chợ nào.
        return [self.cfg["symbol"]] + [x for x in ds if x != self.cfg["symbol"]]

    async def _nap_cho(self, client, ds: list[str]) -> dict[str, dict]:
        """Nạp dữ liệu thị trường cho từng chợ. Chợ nào hỏng thì BỎ, không dừng.

        Một chợ lỗi mạng không được làm chết cả vòng: 14 chợ còn lại vẫn quyết
        định được, và vị thế đang mở ở 14 chợ đó vẫn phải được chấm.
        """
        ra: dict[str, dict] = {}
        for sym in ds:
            try:
                ra[sym] = await get_market_data(client, sym)
            except Exception as e:  # noqa: BLE001
                bus.log("data", "cho-loi", f"{sym}: {type(e).__name__}: {e}")
        return ra

    def _chon_cho(self, cho: dict[str, dict]) -> tuple[str, dict, dict] | None:
        """Chấm mọi chợ bằng LUẬT THUẦN rồi chọn một. Trả (chợ, state, regime).

        Luật thuần chứ không phải bộ não: trần `brain.cli` là 8 lượt/ngày, còn
        đây là 15 chợ mỗi vòng. Chấm bằng luật thì miễn phí và chạy tại máy;
        bộ não chỉ suy luận cho ỨNG VIÊN được chọn, tức đúng chỗ nó đáng tiền.

        Bỏ qua chợ ĐANG có vị thế: mở thêm lệnh thứ hai trên cùng một coin là
        nhân đôi rủi ro của đúng một cược, không phải thêm một cược mới.
        """
        dang_giu = {t.get("symbol") for t in self.broker.state["positions"]}
        ung_vien = []
        for sym, m in cho.items():
            if sym in dang_giu:
                continue
            try:
                st = build_market_state(m)
                rg = classify(st, self.primary, self.context)
                ld = mock_thesis(st, rg, self.primary)
            except Exception as e:  # noqa: BLE001
                bus.log("data", "cham-cho-loi", f"{sym}: {type(e).__name__}: {e}")
                continue
            if ld.get("action") in (None, "NO_TRADE"):
                continue
            # Chất lượng chế độ đứng TRƯỚC độ tin cậy của luật: một tín hiệu
            # rất tự tin trong một chế độ đọc không rõ vẫn là đoán mò.
            diem = ({"HIGH": 2, "MEDIUM": 1}.get(rg.get("quality"), 0),
                    ld.get("confidence") or 0.0)
            ung_vien.append((diem, sym, st, rg))
        if not ung_vien:
            return None
        ung_vien.sort(key=lambda x: x[0], reverse=True)
        _, sym, st, rg = ung_vien[0]
        if len(ung_vien) > 1:
            bus.emit("brain", "chon-cho",
                     f"{len(ung_vien)} chợ có tín hiệu · chọn {sym} "
                     f"({rg['quality']}, tin cậy {ung_vien[0][0][1]:.2f})")
        return sym, st, rg
    async def tick(self, client: httpx.AsyncClient) -> None:
        self.ticks += 1

        # Nạp chợ CHÍNH, cộng thêm mọi chợ ĐANG có vị thế — cái sau bắt buộc,
        # vì không có giá của chính nó thì `mark` không chấm được vị thế đó, và
        # nó sẽ treo qua stop mà không ai đóng.
        _giu = {t.get("symbol") for t in self.broker.state["positions"]}
        _can = [self.cfg["symbol"]] + sorted(_giu - {self.cfg["symbol"]})
        _cho = await self._nap_cho(client, _can)
        market = _cho.get(self.cfg["symbol"]) or await get_market_data(client)
        # Giữ lại nến thô cho /api/candles. Feature là số ĐÃ ĐO; biểu đồ cần
        # chính cái nến để vẽ, không dựng lại được từ feature.
        self.last_market = market
        self.state = build_market_state(market)
        bus.emit("features", "tinh-xong",
                 f"{len(self.state['timeframes'])} khung · RSI {self.state['timeframes'][self.primary].get('rsi14')} · "
                 f"ADX {self.state['timeframes'][self.primary].get('adx')} · ATR% {self.state['timeframes'][self.primary].get('atrPct')}")

        prev_key = self.regime["key"] if self.regime else None
        self.regime = classify(self.state, self.primary, self.context)
        if self.regime["key"] != prev_key:
            bus.log("regime", "doi-regime",
                    f"{prev_key or '—'} → {self.regime['key']} ({self.regime['quality']}) · " + "; ".join(self.regime["reasons"][:2]),
                    regime=self.regime)
        else:
            bus.emit("regime", "giu-nguyen", f"{self.regime['primary']} · chất lượng {self.regime['quality']}", regime=self.regime)

        # Vị thế đang mở được kiểm TRƯỚC khi nghĩ tới lệnh mới. Thoát lệnh không
        # bao giờ được xếp sau việc vào lệnh.
        # Chấm bằng TỪ ĐIỂN {chợ: giá}, không bằng một số. Một số áp lên mọi vị
        # thế nghĩa là vị thế ETH bị chấm bằng giá BTC.
        closed = self.broker.mark({k: v["price"] for k, v in _cho.items()})
        for t in closed:
            bus.emit("journal", "ghi-so", f"đã ghi giao dịch {t['id']} vào nhật ký", trade=t)
            try:
                lesson = await self.brain.postmortem(t, self.regime)
                bus.emit("memory", "luu-tri-nho", f"bài học lưu cho regime {t.get('regimeAtEntry')}", lesson=lesson)
            except Exception as e:  # noqa: BLE001 — hậu kiểm hỏng không được làm chết vòng lặp
                bus.log("memory", "hau-kiem-loi", f"{type(e).__name__}: {e}")

        ok, why = self._should_call_brain(market)
        if not ok:
            bus.emit("brain", "bo-qua", f"không gọi brain: {why}")
            return

        self.force_analyze = False
        self.last_thesis_at = _dt.datetime.now(_dt.timezone.utc)
        self.last_candle_seen = market["lastClosedCandleTime"]
        self.last_regime_key = self.regime["key"]

        account = self.broker.snapshot(market["price"])
        self._chung_cat_neu_den_han()
        # Nghi thức tự lo hạn 6 tiếng và tự chạy ở tiến trình riêng; gọi mỗi
        # vòng là an toàn và rẻ. Không đặt trong `_chung_cat_neu_den_han` vì hai
        # nhịp khác nhau — 20 phút để ĐỌC lại kho, 6 tiếng để SINH RA số mới.
        nghi_thuc.khoi_dong()
        memory = recall(self.regime["key"], self.regime["primary"])
        bus.emit("memory", "truy-hoi",
                 f"{len(memory['lessonsForThisRegime'])} bài học liên quan · "
                 f"lịch sử regime này: {memory['performanceThisRegime'].get('count', 0)} lệnh")

        # QUÉT các chợ khác và chọn ứng viên tốt nhất. Chỉ làm ở đây — sau khi
        # `_should_call_brain` đã cho qua — nên chi phí mạng mỗi vòng không đổi:
        # quét 15 chợ chỉ xảy ra khi thật sự sắp ra quyết định, tức mỗi nến.
        _ds = self._cho_quet()
        if len(_ds) > 1:
            _cho.update(await self._nap_cho(
                client, [x for x in _ds if x not in _cho]))
            _chon = self._chon_cho(_cho)
            if _chon:
                _sym, _st, _rg = _chon
                if _sym != self.cfg["symbol"]:
                    # Đổi chợ đang xét. `self.state`/`self.regime` là thứ mọi
                    # bước sau đọc, kể cả `/api/state` — nên đổi ở đây là đổi
                    # đúng một chỗ, không phải rải điều kiện khắp nơi.
                    market = _cho[_sym]
                    self.last_market, self.state, self.regime = market, _st, _rg

        bus.emit("brain", "dang-nghi", f"gọi brain ({why}) · chợ {market['symbol']}…")
        thesis = await self.brain.thesis(self.state, self.regime, memory, account, self.primary)

        # — CẦU DAO CHẾ ĐỘ: chỗ vòng tuần hoàn khép lại —
        #
        # Phòng huấn luyện đo ra "chế độ này lỗ đều qua ngần này lệnh"; lò chưng
        # cất biến nó thành phát hiện; ở đây phát hiện đó ĐỔI HÀNH VI. Thiếu bước
        # này thì cả dây chuyền dừng ở chỗ "biết" mà không tới được "làm".
        #
        # Giữ nguyên luận điểm gốc trong sổ chứ không xoá: cần đọc được về sau
        # rằng bộ não đã muốn gì và vì sao nó bị chặn. Xoá đi thì cầu dao trở nên
        # vô hình, và không ai đánh giá được nó chặn đúng hay chặn oan.
        ngat = chung_cat.cau_dao(self.regime["key"], self.regime["primary"])
        if ngat and thesis.get("action") not in (None, "NO_TRADE"):
            bus.log("brain", "cau-dao-che-do",
                    f"chặn {thesis['action']} — {ngat['cau'][:150]}", phatHien=ngat)
            thesis = {
                **thesis,
                "action": "NO_TRADE",
                "suggested_risk_pct": 0.0,
                "reason_codes": list(thesis.get("reason_codes") or []) + ["CHE_DO_DA_DO_LA_LO"],
                "reasoning": (f"[cầu dao] {thesis.get('reasoning') or ''} "
                              f"— BỊ CHẶN: {ngat['cau']}").strip(),
                "biChanBoiPhatHien": ngat["ma"],
                "luanDiemGoc": {"action": thesis.get("action"),
                                "confidence": thesis.get("confidence"),
                                "invalidation": thesis.get("invalidation"),
                                "targets": thesis.get("targets")},
            }
        self.last_thesis = thesis

        atr = self.state["timeframes"][self.primary]["_raw"]["atr"]
        decision = self.risk.evaluate(thesis, self.state, account, atr)
        self.last_decision = decision

        if decision["approved"]:
            bus.log("risk", "chap-nhan",
                    f"cho qua · RR {decision['rr']:.2f} · risk ${decision['position']['riskAmount']} "
                    f"({decision['position']['riskPct']}%) · {decision['note']}",
                    decision=decision)
            self.broker.open(decision["position"], thesis, self.regime)
        elif thesis["action"] == "NO_TRADE":
            bus.emit("risk", "khong-vao-lenh", "brain chọn NO_TRADE — đây là một quyết định, không phải bỏ lỡ",
                     decision=decision)
        else:
            bus.log("risk", "tu-choi",
                    f"CHẶN {thesis['action']}: " + " | ".join(decision["rejections"]),
                    decision=decision)

    async def run(self) -> None:
        self.brain = await get_brain()
        # Soát lệch sổ TRƯỚC vòng đầu tiên: runtime có thể đã chết giữa lệnh
        # MARKET và lệnh OCO ở lần chạy trước, để lại một vị thế không ai canh.
        if hasattr(self.broker, "doi_soat"):
            self.broker.doi_soat()
        bus.log("system", "khoi-dong",
                f"{self.cfg['symbol']} · {self.primary}+{self.context} · vòng {self.cfg['loopSeconds']}s · "
                f"vốn ${self.cfg['risk']['startingEquity']:,} · brain {self.brain.mode}")
        async with httpx.AsyncClient(headers={"accept": "application/json"}) as client:
            while True:
                try:
                    await self.tick(client)
                except Exception as e:  # noqa: BLE001 — một vòng hỏng không được giết runtime
                    bus.log("system", "loi-vong-lap", f"{type(e).__name__}: {e}")
                    traceback.print_exc()

                # Ghi lát cắt cho cung tĩnh sau MỌI vòng, kể cả vòng hỏng và vòng
                # thoát sớm. Đặt ở đây chứ không trong tick() vì tick() có nhiều
                # nhánh `return` — đặt trong đó là chắc chắn sót một nhánh, và
                # nhánh bị sót thì trang tĩnh đứng im mà không có gì báo.
                try:
                    snapshot.write(self)
                except Exception as e:  # noqa: BLE001
                    bus.log("system", "snapshot-loi", f"{type(e).__name__}: {e}")

                await asyncio.sleep(self.cfg["loopSeconds"])

    # ── Ảnh chụp cho dashboard ────────────────────────────────────────────
    def snapshot(self) -> dict:
        price = self.state["price"] if self.state else None
        acct = self.broker.snapshot(price)
        return {
            "startedAt": self.started_at,
            "ticks": self.ticks,
            "paused": self.paused,
            "mode": self.mode,
            "venue": getattr(self.broker, "kind", "paper"),
            "spotOnly": self.risk.spot_only,
            "symbol": self.cfg["symbol"],
            "timeframes": {"primary": self.primary, "context": self.context},
            "price": price,
            "dataSource": data_source(),
            "marketState": self.state,
            "regime": self.regime,
            "thesis": self.last_thesis,
            "decision": self.last_decision,
            "chuoiDungNgoai": self._chuoi_dung_ngoai(),
            "account": acct,
            "risk": {
                "halted": self.risk.halted_reason,
                "breakers": self.risk.circuit_breakers(acct),
                "limits": self.cfg["risk"],
            },
            "brain": self.brain.status() if self.brain else {"mode": "chưa khởi động"},
            "nextThesisIn": self._next_in(),
        }

    # Bao nhiêu lượt NO_TRADE liên tiếp thì gọi là ĐỨNG IM chứ không phải thận
    # trọng. Cùng ngưỡng với `scripts/ban-giao.py` — hai chỗ nói cùng một chuyện.
    DUNG_IM_LIEN_TIEP = 12

    def _chuoi_dung_ngoai(self) -> int:
        """Số luận điểm NO_TRADE liên tiếp gần nhất.

        Buồng lái nói "Bộ não chủ động đứng ngoài — đây là một quyết định" ở lượt
        thứ nhất, và nói y hệt câu đó ở lượt thứ 18. Câu ấy đúng cho một lượt và
        sai cho mười tám: đứng ngoài liên tục vì bằng chứng ÂM về chính chế độ
        đang chạy là một thế bí tự khoá — không vào lệnh thì không có dữ liệu mới,
        nên bằng chứng âm đứng nguyên.

        Đọc từ SỔ chứ không đếm trong bộ nhớ: runtime dựng lại thì bộ đếm trong
        bộ nhớ về 0, và chuỗi 18 lượt biến mất đúng lúc cần nhìn thấy nó nhất.
        """
        try:
            from . import store

            ds = store.read_all(store.THESES)
        except Exception:  # noqa: BLE001
            return 0
        n = 0
        for t in reversed(ds):
            if t.get("action") != "NO_TRADE":
                break
            n += 1
        return n
    def _next_in(self) -> int | None:
        if not self.last_thesis_at:
            return 0
        elapsed = (_dt.datetime.now(_dt.timezone.utc) - self.last_thesis_at).total_seconds()
        return max(0, int(self.cfg["brain"]["minSecondsBetweenTheses"] - elapsed))


runtime = Runtime()
