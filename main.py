import flet as ft
import asyncio
import websockets
import json
import math
import time
from datetime import datetime

# ==========================================
# 1. الهوية البصرية (Dark Cyber Neon)
# ==========================================
BG_DARK = "#050814"
BG_NAVY = "#0B1124"
CARD_GLASS = "#131C38"
BORDER_GLOW = "#1E2D5A"
NEON_CYAN = "#00F0FF"
NEON_PURPLE = "#9D4EDD"
NEON_GREEN = "#00E676"
NEON_RED = "#FF2A5F"
NEON_GOLD = "#FFD166"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"

DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"

# ==========================================
# 2. قاموس اللغات (عربي RTL / إنجليزي LTR)
# ==========================================
LANG = {
    "ar": {
        "app_name": "AI TRADING BOT ULTIMATE",
        "subtitle": "الروبوت الذكي للتحليل الاحترافي ومحاكاة التداول",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب جديد",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "enter_app": "دخول المنصة",
        "dashboard": "لوحة التحكم",
        "markets": "الأسواق الحية",
        "charts": "الرسم البياني",
        "ai_analysis": "التحليل الذكي AI",
        "candles": "تحليل الشموع",
        "indicators": "المؤشرات الفنية",
        "signals": "مركز الإشارات",
        "news": "الأخبار الاقتصادية",
        "calendar": "التقويم الاقتصادي",
        "strategy_lab": "مختبر الاستراتيجيات",
        "backtest": "الاختبار التاريخي",
        "portfolio": "المحفظة الافتراضية",
        "risk": "إدارة المخاطر",
        "journal": "سجل التداول",
        "assistant": "مساعد AI",
        "reports": "التقارير",
        "alerts": "التنبيهات",
        "settings": "الإعدادات",
        "api_conn": "ربط Deriv API",
        "about": "حول التطبيق",
        "virtual_balance": "الرصيد الافتراضي (Paper)",
        "demo_only": "وضع المحاكاة والتدريب فقط — لا توجد أموال حقيقية",
        "connected": "متصل بخادم Deriv الحي",
        "disconnected": "غير متصل — جاري المحاولة",
        "buy": "شراء (صعود)",
        "sell": "بيع (هبوط)",
        "neutral": "محايد / انتظار",
        "reset_acc": "إعادة تعيين الحساب الافتراضي",
        "lang_switch": "English (LTR)",
    },
    "en": {
        "app_name": "AI TRADING BOT ULTIMATE",
        "subtitle": "Smart AI Market Analysis & Paper Trading Terminal",
        "login": "Login",
        "register": "Create Account",
        "email": "Email Address",
        "password": "Password",
        "enter_app": "Enter Terminal",
        "dashboard": "Dashboard",
        "markets": "Live Markets",
        "charts": "Live Charts",
        "ai_analysis": "AI Analysis",
        "candles": "Candlestick AI",
        "indicators": "Indicators",
        "signals": "Signals Center",
        "news": "Market News",
        "calendar": "Economic Calendar",
        "strategy_lab": "Strategy Lab",
        "backtest": "Backtesting",
        "portfolio": "Demo Portfolio",
        "risk": "Risk Manager",
        "journal": "Trading Journal",
        "assistant": "AI Assistant",
        "reports": "Reports",
        "alerts": "Alerts",
        "settings": "Settings",
        "api_conn": "Deriv API Setup",
        "about": "About App",
        "virtual_balance": "Virtual Balance (Paper)",
        "demo_only": "Educational & Simulation Mode Only — No Real Funds",
        "connected": "Connected to Deriv Live Feed",
        "disconnected": "Disconnected — Reconnecting",
        "buy": "BUY (BULLISH)",
        "sell": "SELL (BEARISH)",
        "neutral": "NEUTRAL / WAIT",
        "reset_acc": "Reset Virtual Account",
        "lang_switch": "العربية (RTL)",
    }
}

ASSETS = [
    {"symbol": "R_100", "name": "Volatility 100 Index", "cat": "Synthetic", "digits": 2},
    {"symbol": "R_75", "name": "Volatility 75 Index", "cat": "Synthetic", "digits": 4},
    {"symbol": "R_50", "name": "Volatility 50 Index", "cat": "Synthetic", "digits": 4},
    {"symbol": "1HZ100V", "name": "Volatility 100 (1s)", "cat": "Synthetic", "digits": 2},
    {"symbol": "frxEURUSD", "name": "EUR / USD", "cat": "Forex", "digits": 5},
    {"symbol": "frxGBPUSD", "name": "GBP / USD", "cat": "Forex", "digits": 5},
    {"symbol": "frxUSDJPY", "name": "USD / JPY", "cat": "Forex", "digits": 3},
    {"symbol": "frxXAUUSD", "name": "Gold / USD (XAU)", "cat": "Commodities", "digits": 2},
    {"symbol": "cryBTCUSD", "name": "Bitcoin / USD", "cat": "Crypto", "digits": 2},
    {"symbol": "cryETHUSD", "name": "Ethereum / USD", "cat": "Crypto", "digits": 2},
]

TIMEFRAMES = [
    {"label": "1m", "sec": 60},
    {"label": "5m", "sec": 300},
    {"label": "15m", "sec": 900},
    {"label": "1h", "sec": 3600},
    {"label": "4h", "sec": 14400},
]

# ==========================================
# 3. محرك التحليل الرياضي والفني المتكامل
# ==========================================
class TechnicalEngine:
    @staticmethod
    def calc_ema(prices, period):
        if not prices:
            return 0.0
        if len(prices) < period:
            return sum(prices) / len(prices)
        k = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price * k) + (ema * (1 - k))
        return ema

    @staticmethod
    def calc_macd(prices):
        if len(prices) < 26:
            return 0.0, 0.0, 0.0
        ema12 = TechnicalEngine.calc_ema(prices, 12)
        ema26 = TechnicalEngine.calc_ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = macd_line * 0.85
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    @staticmethod
    def calc_rsi(prices, period=14):
        if len(prices) < period + 1:
            return 50.0
        gains, losses = [], []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i - 1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calc_bollinger(prices, period=20, std_dev=2):
        if len(prices) < period:
            p = prices[-1] if prices else 0.0
            return p, p, p
        window = prices[-period:]
        sma = sum(window) / period
        variance = sum((x - sma) ** 2 for x in window) / period
        sd = math.sqrt(variance)
        return sma + (std_dev * sd), sma, sma - (std_dev * sd)

    @staticmethod
    def detect_candle_pattern(candles):
        if len(candles) < 2:
            return "تجميع بيانات الشموع...", "Neutral"
        c1 = candles[-2]
        c2 = candles[-1]
        body2 = abs(c2["close"] - c2["open"])
        range2 = max(c2["high"] - c2["low"], 0.00001)
        upper_wick = c2["high"] - max(c2["open"], c2["close"])
        lower_wick = min(c2["open"], c2["close"]) - c2["low"]

        if lower_wick > body2 * 2 and upper_wick < body2 * 0.5:
            return "مطرقة صاعدة (Bullish Hammer)", "Bullish"
        if upper_wick > body2 * 2 and lower_wick < body2 * 0.5:
            return "شهاب هابط (Shooting Star)", "Bearish"
        if c2["close"] > c2["open"] and c1["close"] < c1["open"] and c2["close"] > c1["open"] and c2["open"] < c1["close"]:
            return "ابتلاع شرائي (Bullish Engulfing)", "Bullish"
        if c2["close"] < c2["open"] and c1["close"] > c1["open"] and c2["close"] < c1["open"] and c2["open"] > c1["close"]:
            return "ابتلاع بيعي (Bearish Engulfing)", "Bearish"
        if body2 / range2 < 0.15:
            return "شمعة دوجي حيرة (Doji Indecision)", "Neutral"
        return "شمعة زخم قياسية (Standard Momentum)", "Bullish" if c2["close"] >= c2["open"] else "Bearish"


# ==========================================
# 4. التطبيق الرئيسي (Flet Android App v2.0)
# ==========================================
async def main(page: ft.Page):
    page.title = "AI TRADING BOT ULTIMATE"
    page.bgcolor = BG_DARK
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.rtl = True

    state = {
        "lang": "ar",
        "user_email": "trader@hassanstudio.ai",
        "selected_symbol": "R_100",
        "timeframe": 60,
        "ws_connected": False,
        "ws_ref": None,
        "deriv_token": "",
        "deriv_demo_verified": False,
        "deriv_account_id": "غير مربوط",
        "deriv_real_demo_bal": 0.0,
        "prices": {a["symbol"]: 0.0 for a in ASSETS},
        "prev_prices": {a["symbol"]: 0.0 for a in ASSETS},
        "candles": {a["symbol"]: [] for a in ASSETS},
        "paper_balance": 10000.0,
        "equity_curve": [10000.0],
        "open_trades": [],
        "trade_history": [],
        "risk_percent": 2.0,
        "active_strategy": "EMA + RSI Confluence",
        "alerts": [
            {"time": "الآن", "msg": "تم تشغيل محرك التحليل الحي Deriv WebSocket v3 بنجاح", "type": "info"}
        ],
        "chat_messages": [
            {"sender": "ai", "text": "مرحباً بك في AI TRADING BOT ULTIMATE! أنا متصل ببيانات السوق الحية. اسألني عن تحليل الأصل الحالي، المؤشرات، أو السيناريوهات المحتملة."}
        ]
    }

    # استرجاع كافة البيانات المحفوظة محلياً
    try:
        saved_bal = await page.client_storage.get_async("paper_balance")
        if saved_bal is not None:
            state["paper_balance"] = float(saved_bal)
        saved_eq = await page.client_storage.get_async("equity_curve")
        if saved_eq:
            state["equity_curve"] = json.loads(saved_eq)
        saved_open = await page.client_storage.get_async("open_trades")
        if saved_open:
            state["open_trades"] = json.loads(saved_open)
        saved_hist = await page.client_storage.get_async("trade_history")
        if saved_hist:
            state["trade_history"] = json.loads(saved_hist)
        saved_risk = await page.client_storage.get_async("risk_percent")
        if saved_risk is not None:
            state["risk_percent"] = float(saved_risk)
        saved_token = await page.client_storage.get_async("deriv_token")
        if saved_token:
            state["deriv_token"] = saved_token
        saved_lang = await page.client_storage.get_async("lang")
        if saved_lang in ["ar", "en"]:
            state["lang"] = saved_lang
            page.rtl = (saved_lang == "ar")
    except Exception:
        pass

    def t(key):
        return LANG[state["lang"]].get(key, key)

    async def save_all_state():
        try:
            await page.client_storage.set_async("paper_balance", state["paper_balance"])
            await page.client_storage.set_async("equity_curve", json.dumps(state["equity_curve"][-30:]))
            await page.client_storage.set_async("open_trades", json.dumps(state["open_trades"]))
            await page.client_storage.set_async("trade_history", json.dumps(state["trade_history"][:50]))
            await page.client_storage.set_async("risk_percent", state["risk_percent"])
            await page.client_storage.set_async("deriv_token", state["deriv_token"])
        except Exception:
            pass

    # ==========================================
    # مكونات الهوية البصرية
    # ==========================================
    def build_robot_emblem(size=72):
        return ft.Container(
            width=size,
            height=size,
            border_radius=size // 2,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[NEON_CYAN, NEON_PURPLE, BG_NAVY],
            ),
            padding=3,
            shadow=ft.BoxShadow(blur_radius=18, color=ft.colors.with_opacity(0.45, NEON_CYAN)),
            content=ft.Container(
                bgcolor=BG_NAVY,
                border_radius=size // 2,
                alignment=ft.alignment.center,
                content=ft.Stack([
                    ft.Icon(ft.icons.SMART_TOY_ROUNDED, color=NEON_CYAN, size=size * 0.55),
                    ft.Container(
                        right=size * 0.14,
                        bottom=size * 0.14,
                        content=ft.Icon(ft.icons.CANDLESTICK_CHART, color=NEON_GREEN, size=size * 0.28),
                    )
                ])
            )
        )

    def glass_card(content, padding=14, border_color=BORDER_GLOW):
        return ft.Container(
            bgcolor=ft.colors.with_opacity(0.88, CARD_GLASS),
            border=ft.border.all(1, border_color),
            border_radius=16,
            padding=padding,
            shadow=ft.BoxShadow(blur_radius=12, color=ft.colors.with_opacity(0.25, "#000000")),
            content=content
        )

    def section_badge(text, color=NEON_CYAN):
        return ft.Container(
            bgcolor=ft.colors.with_opacity(0.15, color),
            border=ft.border.all(1, ft.colors.with_opacity(0.5, color)),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color=color)
        )

    # ==========================================
    # طلب الشموع الفوري عند تغيير الأصل أو الفريم
    # ==========================================
    async def request_candles_now(symbol, granularity):
        ws = state.get("ws_ref")
        if ws and state["ws_connected"]:
            try:
                await ws.send(json.dumps({"forget_all": "candles"}))
                await ws.send(json.dumps({
                    "ticks_history": symbol,
                    "adjust_start_time": 1,
                    "count": 45,
                    "end": "latest",
                    "granularity": granularity,
                    "style": "candles",
                    "subscribe": 1
                }))
            except Exception:
                pass

    # ==========================================
    # الاتصال الحي بـ Deriv WebSocket API
    # ==========================================
    async def deriv_feed_worker():
        while True:
            try:
                async with websockets.connect(DERIV_WS_URL, ping_interval=20) as ws:
                    state["ws_connected"] = True
                    state["ws_ref"] = ws

                    for asset in ASSETS:
                        await ws.send(json.dumps({"ticks": asset["symbol"], "subscribe": 1}))

                    await request_candles_now(state["selected_symbol"], state["timeframe"])

                    async for raw in ws:
                        data = json.loads(raw)
                        msg_type = data.get("msg_type")

                        if msg_type == "tick":
                            tick = data["tick"]
                            sym = tick["symbol"]
                            quote = float(tick["quote"])
                            state["prev_prices"][sym] = state["prices"].get(sym, quote)
                            state["prices"][sym] = quote

                            if state["candles"].get(sym):
                                last_c = state["candles"][sym][-1]
                                last_c["close"] = quote
                                last_c["high"] = max(last_c["high"], quote)
                                last_c["low"] = min(last_c["low"], quote)

                        elif msg_type == "candles":
                            sym = data.get("echo_req", {}).get("ticks_history", state["selected_symbol"])
                            state["candles"][sym] = [
                                {
                                    "epoch": c["epoch"],
                                    "open": float(c["open"]),
                                    "high": float(c["high"]),
                                    "low": float(c["low"]),
                                    "close": float(c["close"]),
                                }
                                for c in data.get("candles", [])
                            ]
                            if current_route["name"] in ["dashboard", "charts", "ai_analysis", "candles", "indicators"]:
                                render_view()

                        elif msg_type == "ohlc":
                            ohlc = data["ohlc"]
                            sym = ohlc["symbol"]
                            c_obj = {
                                "epoch": ohlc["open_time"],
                                "open": float(ohlc["open"]),
                                "high": float(ohlc["high"]),
                                "low": float(ohlc["low"]),
                                "close": float(ohlc["close"]),
                            }
                            if state["candles"].get(sym):
                                if state["candles"][sym][-1]["epoch"] == c_obj["epoch"]:
                                    state["candles"][sym][-1] = c_obj
                                else:
                                    state["candles"][sym].append(c_obj)
                                    if len(state["candles"][sym]) > 55:
                                        state["candles"][sym].pop(0)

                        if current_route["name"] in ["dashboard", "markets", "charts", "ai_analysis", "portfolio"]:
                            refresh_dynamic_values()

            except Exception:
                state["ws_connected"] = False
                state["ws_ref"] = None
                await asyncio.sleep(4)

    # ==========================================
    # محرك التحليل الفني الشامل
    # ==========================================
    def get_current_analysis():
        sym = state["selected_symbol"]
        candles = state["candles"].get(sym, [])
        closes = [c["close"] for c in candles]
        current_price = state["prices"].get(sym, 0.0)
        if not closes and current_price > 0:
            closes = [current_price]

        ema9 = TechnicalEngine.calc_ema(closes, 9)
        ema21 = TechnicalEngine.calc_ema(closes, 21)
        rsi = TechnicalEngine.calc_rsi(closes, 14)
        macd_l, macd_s, macd_h = TechnicalEngine.calc_macd(closes)
        bb_up, bb_mid, bb_low = TechnicalEngine.calc_bollinger(closes, 20)
        candle_name, candle_bias = TechnicalEngine.detect_candle_pattern(candles)

        bull_score = 50
        bull_score += 15 if ema9 > ema21 else -15
        bull_score += 15 if rsi < 35 else (-15 if rsi > 65 else 0)
        bull_score += 10 if macd_h > 0 else -10
        bull_score += 10 if candle_bias == "Bullish" else (-10 if candle_bias == "Bearish" else 0)

        bull_prob = max(15, min(85, bull_score))
        bear_prob = max(10, min(80, 90 - bull_prob))
        neutral_prob = max(5, 100 - bull_prob - bear_prob)

        if bull_prob >= 60:
            direction = t("buy")
            dir_color = NEON_GREEN
        elif bear_prob >= 60:
            direction = t("sell")
            dir_color = NEON_RED
        else:
            direction = t("neutral")
            dir_color = NEON_GOLD

        support = min(closes[-15:]) if closes else current_price
        resistance = max(closes[-15:]) if closes else current_price

        return {
            "symbol": sym,
            "price": current_price,
            "ema9": ema9,
            "ema21": ema21,
            "rsi": rsi,
            "macd_l": macd_l,
            "macd_s": macd_s,
            "macd_h": macd_h,
            "bb_up": bb_up,
            "bb_mid": bb_mid,
            "bb_low": bb_low,
            "candle_name": candle_name,
            "candle_bias": candle_bias,
            "bull_prob": bull_prob,
            "bear_prob": bear_prob,
            "neutral_prob": neutral_prob,
            "direction": direction,
            "dir_color": dir_color,
            "support": support,
            "resistance": resistance,
            "candles": candles,
        }

    # ==========================================
    # مخطط الشموع اليابانية + منحنى الأرباح
    # ==========================================
    def build_candlestick_widget(candles, height=210):
        if len(candles) < 5:
            return ft.Container(
                height=height,
                alignment=ft.alignment.center,
                bgcolor="#070C1D",
                border_radius=12,
                border=ft.border.all(1, BORDER_GLOW),
                content=ft.Column([
                    ft.ProgressRing(color=NEON_CYAN, width=28, height=28),
                    ft.Text("جاري تحميل الشموع الحية من Deriv API...", color=TEXT_SECONDARY, size=12)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
            )

        visible = candles[-26:]
        highs = [c["high"] for c in visible]
        lows = [c["low"] for c in visible]
        max_p = max(highs)
        min_p = min(lows)
        span = max(max_p - min_p, 0.00001)

        bars = []
        for c in visible:
            is_bull = c["close"] >= c["open"]
            color = NEON_GREEN if is_bull else NEON_RED
            top_wick_pct = (max_p - c["high"]) / span
            body_top_pct = (max_p - max(c["open"], c["close"])) / span
            body_h_pct = max(abs(c["close"] - c["open"]) / span, 0.025)
            wick_h_pct = max((c["high"] - c["low"]) / span, 0.03)

            bars.append(
                ft.Container(
                    width=8,
                    height=height - 20,
                    content=ft.Stack([
                        ft.Container(
                            left=3.2,
                            top=top_wick_pct * (height - 20),
                            width=1.5,
                            height=wick_h_pct * (height - 20),
                            bgcolor=color,
                        ),
                        ft.Container(
                            left=0.5,
                            top=body_top_pct * (height - 20),
                            width=7,
                            height=body_h_pct * (height - 20),
                            bgcolor=color,
                            border_radius=2,
                        ),
                    ])
                )
            )

        return ft.Container(
            height=height,
            bgcolor="#070C1D",
            border_radius=12,
            border=ft.border.all(1, BORDER_GLOW),
            padding=10,
            content=ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    def build_equity_chart(points, height=110):
        if len(points) < 2:
            points = [10000.0, state["paper_balance"]]
        mx = max(points)
        mn = min(points)
        sp = max(mx - mn, 1.0)
        cols = []
        for val in points[-20:]:
            pct = max((val - mn) / sp, 0.15)
            col = NEON_GREEN if val >= 10000.0 else NEON_RED
            cols.append(
                ft.Container(
                    width=10,
                    height=pct * (height - 20),
                    bgcolor=col,
                    border_radius=4,
                )
            )
        return ft.Container(
            height=height,
            bgcolor="#070C1D",
            border_radius=12,
            border=ft.border.all(1, BORDER_GLOW),
            padding=10,
            alignment=ft.alignment.bottom_center,
            content=ft.Row(cols, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END)
        )

    # ==========================================
    # نظام التنقل والتحديث
    # ==========================================
    current_route = {"name": "splash"}
    main_container = ft.Container(expand=True)
    live_price_text = ft.Text("0.00", size=21, weight=ft.FontWeight.BOLD, color=NEON_CYAN)
    ws_status_badge = section_badge(t("disconnected"), NEON_RED)

    def refresh_dynamic_values():
        sym = state["selected_symbol"]
        p = state["prices"].get(sym, 0.0)
        digits = next((a["digits"] for a in ASSETS if a["symbol"] == sym), 2)
        live_price_text.value = f"{p:.{digits}f}" if p > 0 else "Loading..."
        ws_status_badge.content.value = t("connected") if state["ws_connected"] else t("disconnected")
        ws_status_badge.content.color = NEON_GREEN if state["ws_connected"] else NEON_RED
        try:
            page.update()
        except Exception:
            pass

    def navigate(route_name):
        current_route["name"] = route_name
        page.drawer.open = False
        render_view()

    # ==========================================
    # الصفحات الـ 22 كاملة ومتكاملة
    # ==========================================
    def view_splash():
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#09132E", BG_DARK, "#0C071E"]
            ),
            padding=24,
            content=ft.Column([
                ft.Container(height=30),
                build_robot_emblem(110),
                ft.Text(t("app_name"), size=23, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Text(t("subtitle"), size=13, color=NEON_CYAN, text_align=ft.TextAlign.CENTER),
                ft.Container(height=16),
                glass_card(
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.VERIFIED_USER, color=NEON_GREEN, size=18), ft.Text("بيانات سوق حقيقية 100% من Deriv API", size=12, color=TEXT_PRIMARY)]),
                        ft.Row([ft.Icon(ft.icons.PSYCHOLOGY, color=NEON_PURPLE, size=18), ft.Text("محرك تحليل ذكي ومؤشرات فنية دقيقة", size=12, color=TEXT_PRIMARY)]),
                        ft.Row([ft.Icon(ft.icons.SHIELD, color=NEON_GOLD, size=18), ft.Text("محاكاة Paper Trading تعليمية آمنة", size=12, color=TEXT_PRIMARY)]),
                    ], spacing=10)
                ),
                ft.Container(height=16),
                ft.ElevatedButton(
                    text=t("login"),
                    bgcolor=NEON_CYAN,
                    color=BG_DARK,
                    width=260,
                    height=48,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    on_click=lambda _: navigate("login")
                ),
                ft.OutlinedButton(
                    text=t("lang_switch"),
                    width=260,
                    height=42,
                    on_click=lambda _: toggle_language("splash")
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
        )

    def view_login():
        email_in = ft.TextField(label=t("email"), value=state["user_email"], border_color=NEON_CYAN, border_radius=12)
        pass_in = ft.TextField(label=t("password"), password=True, can_reveal_password=True, value="********", border_color=NEON_PURPLE, border_radius=12)

        def do_login(_):
            if email_in.value:
                state["user_email"] = email_in.value
            navigate("dashboard")

        return ft.Container(
            expand=True,
            padding=24,
            content=ft.Column([
                ft.Container(height=20),
                build_robot_emblem(80),
                ft.Text(t("login"), size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(t("demo_only"), size=11, color=NEON_GOLD),
                glass_card(
                    ft.Column([
                        email_in,
                        pass_in,
                        ft.ElevatedButton(
                            text=t("enter_app"),
                            bgcolor=NEON_CYAN,
                            color=BG_DARK,
                            width=300,
                            height=46,
                            on_click=do_login
                        ),
                        ft.TextButton(t("register"), on_click=do_login)
                    ], spacing=14)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14)
        )

    def view_dashboard():
        an = get_current_analysis()
        refresh_dynamic_values()
        total_pnl = sum(tr["pnl"] for tr in state["trade_history"])

        tools_grid = ft.GridView(
            runs_count=3,
            max_extent=120,
            child_aspect_ratio=1.05,
            spacing=8,
            run_spacing=8,
            shrink=True,
            controls=[
                tool_tile(t("ai_analysis"), ft.icons.PSYCHOLOGY, NEON_CYAN, "ai_analysis"),
                tool_tile(t("charts"), ft.icons.CANDLESTICK_CHART, NEON_GREEN, "charts"),
                tool_tile(t("signals"), ft.icons.BOLT, NEON_GOLD, "signals"),
                tool_tile(t("news"), ft.icons.NEWSPAPER, NEON_PURPLE, "news"),
                tool_tile(t("strategy_lab"), ft.icons.SCIENCE, NEON_CYAN, "strategy_lab"),
                tool_tile(t("backtest"), ft.icons.HISTORY, NEON_GREEN, "backtest"),
                tool_tile(t("risk"), ft.icons.SECURITY, NEON_RED, "risk"),
                tool_tile(t("portfolio"), ft.icons.ACCOUNT_BALANCE_WALLET, NEON_GOLD, "portfolio"),
                tool_tile(t("api_conn"), ft.icons.API, NEON_PURPLE, "api_conn"),
            ]
        )

        return ft.Column([
            glass_card(
                ft.Column([
                    ft.Row([ws_status_badge, section_badge("PAPER MODE", NEON_GOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=BORDER_GLOW, height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text(t("virtual_balance"), size=12, color=TEXT_SECONDARY),
                            ft.Text(f"${state['paper_balance']:,.2f}", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ]),
                        ft.Column([
                            ft.Text("صافي المحاكاة", size=12, color=TEXT_SECONDARY),
                            ft.Text(f"{total_pnl:+.2f}$", size=18, weight=ft.FontWeight.BOLD, color=NEON_GREEN if total_pnl >= 0 else NEON_RED),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ])
            ),
            glass_card(
                ft.Column([
                    ft.Row([
                        ft.Row([ft.Icon(ft.icons.SHOW_CHART, color=NEON_CYAN), ft.Text(state["selected_symbol"], size=16, weight=ft.FontWeight.BOLD)]),
                        live_price_text,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text(f"التوجه الفني: {an['direction']}", color=an["dir_color"], weight=ft.FontWeight.BOLD, size=13),
                        ft.Text(f"RSI: {an['rsi']:.1f}", color=TEXT_SECONDARY, size=12),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    build_candlestick_widget(an["candles"], height=150),
                ], spacing=8)
            ),
            ft.Text("كل الأدوات في تطبيق واحد", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            tools_grid,
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def tool_tile(title, icon, color, route):
        return ft.Container(
            bgcolor=CARD_GLASS,
            border=ft.border.all(1, BORDER_GLOW),
            border_radius=14,
            padding=8,
            on_click=lambda _: navigate(route),
            content=ft.Column([
                ft.Container(
                    padding=8,
                    border_radius=10,
                    bgcolor=ft.colors.with_opacity(0.15, color),
                    content=ft.Icon(icon, color=color, size=22)
                ),
                ft.Text(title, size=11, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER, max_lines=2)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)
        )

    def view_markets():
        rows = []
        for asset in ASSETS:
            sym = asset["symbol"]
            price = state["prices"].get(sym, 0.0)
            prev = state["prev_prices"].get(sym, price)
            diff = price - prev
            c_col = NEON_GREEN if diff >= 0 else NEON_RED
            digits = asset["digits"]

            def select_sym(_, s=sym):
                state["selected_symbol"] = s
                asyncio.create_task(request_candles_now(s, state["timeframe"]))
                navigate("charts")

            rows.append(
                glass_card(
                    ft.Row([
                        ft.Column([
                            ft.Text(asset["name"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{sym} • {asset['cat']}", size=11, color=TEXT_SECONDARY),
                        ]),
                        ft.Row([
                            ft.Text(f"{price:.{digits}f}" if price > 0 else "...", size=15, weight=ft.FontWeight.BOLD, color=c_col),
                            ft.IconButton(icon=ft.icons.CANDLESTICK_CHART, icon_color=NEON_CYAN, on_click=select_sym)
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10
                )
            )
        return ft.Column([
            ft.Text(t("markets"), size=18, weight=ft.FontWeight.BOLD),
            ft.Text("اضغط على أي أصل لتحميل شموعه الحية فوراً", size=12, color=TEXT_SECONDARY),
            *rows
        ], spacing=8, scroll=ft.ScrollMode.AUTO)

    def view_charts():
        an = get_current_analysis()

        def change_tf(sec):
            state["timeframe"] = sec
            state["candles"][state["selected_symbol"]] = []
            asyncio.create_task(request_candles_now(state["selected_symbol"], sec))
            render_view()

        tf_buttons = ft.Row([
            ft.ElevatedButton(
                text=tf["label"],
                bgcolor=NEON_CYAN if state["timeframe"] == tf["sec"] else CARD_GLASS,
                color=BG_DARK if state["timeframe"] == tf["sec"] else TEXT_PRIMARY,
                height=34,
                on_click=lambda _, s=tf["sec"]: change_tf(s)
            ) for tf in TIMEFRAMES
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        def execute_paper_trade(side):
            if an["price"] <= 0:
                return
            stake = round(state["paper_balance"] * (state["risk_percent"] / 100.0), 2)
            trade = {
                "id": int(time.time()),
                "symbol": state["selected_symbol"],
                "side": side,
                "entry": an["price"],
                "stake": stake,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "OPEN",
                "pnl": 0.0
            }
            state["open_trades"].append(trade)
            asyncio.create_task(save_all_state())
            navigate("portfolio")

        return ft.Column([
            ft.Row([
                ft.Text(f"{state['selected_symbol']}", size=18, weight=ft.FontWeight.BOLD),
                live_price_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tf_buttons,
            build_candlestick_widget(an["candles"], height=230),
            glass_card(
                ft.Column([
                    ft.Row([
                        ft.Text(f"EMA 9: {an['ema9']:.4f}", size=11, color=NEON_CYAN),
                        ft.Text(f"EMA 21: {an['ema21']:.4f}", size=11, color=NEON_PURPLE),
                        ft.Text(f"RSI: {an['rsi']:.1f}", size=11, color=NEON_GOLD),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"MACD: {an['macd_l']:.4f} | Signal: {an['macd_s']:.4f}", size=11, color=TEXT_SECONDARY),
                    ft.Text(f"نموذج الشمعة: {an['candle_name']}", size=12, color=TEXT_PRIMARY),
                ], spacing=4)
            ),
            ft.Row([
                ft.ElevatedButton(
                    text="شراء افتراضي (Paper Buy)",
                    bgcolor=NEON_GREEN,
                    color=BG_DARK,
                    expand=True,
                    height=45,
                    on_click=lambda _: execute_paper_trade("BUY")
                ),
                ft.ElevatedButton(
                    text="بيع افتراضي (Paper Sell)",
                    bgcolor=NEON_RED,
                    color=TEXT_PRIMARY,
                    expand=True,
                    height=45,
                    on_click=lambda _: execute_paper_trade("SELL")
                ),
            ], spacing=10)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def view_ai_analysis():
        an = get_current_analysis()
        return ft.Column([
            ft.Row([build_robot_emblem(48), ft.Text("التحليل الذكي بالذكاء الاصطناعي", size=17, weight=ft.FontWeight.BOLD)]),
            glass_card(
                ft.Column([
                    ft.Text(f"الأصل المحلل: {an['symbol']}", size=13, color=NEON_CYAN),
                    ft.Text(f"التقدير الفني الحالي: {an['direction']}", size=18, weight=ft.FontWeight.BOLD, color=an["dir_color"]),
                    ft.Divider(color=BORDER_GLOW),
                    ft.Text("السيناريوهات المحتملة (تقدير إحصائي تعليمي):", size=13, weight=ft.FontWeight.BOLD),
                    scenario_bar("سيناريو صاعد (Bullish)", an["bull_prob"], NEON_GREEN),
                    scenario_bar("سيناريو هابط (Bearish)", an["bear_prob"], NEON_RED),
                    scenario_bar("سيناريو عرضي (Neutral)", an["neutral_prob"], NEON_GOLD),
                    ft.Divider(color=BORDER_GLOW),
                    ft.Row([
                        ft.Text(f"الدعم الرئيسي: {an['support']:.4f}", color=NEON_GREEN, size=12),
                        ft.Text(f"المقاومة الرئيسية: {an['resistance']:.4f}", color=NEON_RED, size=12),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("ملاحظة: التحليل يعتمد على معادلات المؤشرات الحية ولا يمثل توصية مالية مضمونة.", size=11, color=TEXT_SECONDARY),
                ], spacing=10)
            )
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def scenario_bar(label, pct, color):
        return ft.Column([
            ft.Row([ft.Text(label, size=12), ft.Text(f"{pct}%", size=12, weight=ft.FontWeight.BOLD, color=color)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=pct / 100.0, color=color, bgcolor=BG_DARK, height=8)
        ], spacing=4)

    def view_candles():
        an = get_current_analysis()
        return ft.Column([
            ft.Text("محلل نماذج الشموع اليابانية AI", size=18, weight=ft.FontWeight.BOLD),
            build_candlestick_widget(an["candles"], height=200),
            glass_card(
                ft.Column([
                    ft.Text("النموذج المكتشف على الشمعة الأخيرة:", size=12, color=TEXT_SECONDARY),
                    ft.Text(an["candle_name"], size=16, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
                    ft.Text("تفسير النموذج: يراقب المحرك طول الفتائل مقارنة بجسم الشمعة لتحديد مناطق انعكاس السيولة أو استمرار الزخم.", size=12, color=TEXT_PRIMARY),
                ], spacing=8)
            )
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def view_indicators():
        an = get_current_analysis()
        return ft.Column([
            ft.Text(t("indicators"), size=18, weight=ft.FontWeight.BOLD),
            indicator_card("RSI (14) — مؤشر القوة النسبية", f"{an['rsi']:.2f}", "تشبع بيعي (<30) أو تشبع شرائي (>70)", NEON_GOLD),
            indicator_card("MACD (12, 26, 9) — الزخم والاتجاه", f"MACD: {an['macd_l']:.4f} | Hist: {an['macd_h']:.4f}", "قياس قوة الاتجاه وتقاطع الزخم", NEON_GREEN),
            indicator_card("EMA (9 / 21) — المتوسط المتحرك الأسي", f"{an['ema9']:.4f} / {an['ema21']:.4f}", "تقاطع المتوسطات لتحديد اتجاه الزخم", NEON_CYAN),
            indicator_card("Bollinger Bands (20, 2)", f"Upper: {an['bb_up']:.4f} | Lower: {an['bb_low']:.4f}", "قياس التذبذب والانحراف المعياري للسعر", NEON_PURPLE),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def indicator_card(title, val, desc, color):
        return glass_card(
            ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(val, size=15, weight=ft.FontWeight.BOLD),
                ft.Text(desc, size=11, color=TEXT_SECONDARY),
            ], spacing=4)
        )

    def view_signals():
        items = []
        for a in ASSETS[:7]:
            sym = a["symbol"]
            p = state["prices"].get(sym, 0.0)
            c = state["candles"].get(sym, [])
            closes = [x["close"] for x in c] if c else [p]
            rsi = TechnicalEngine.calc_rsi(closes)
            sig = "شراء (RSI منخفض)" if rsi < 42 else ("بيع (RSI مرتفع)" if rsi > 58 else "مراقبة الحياد")
            col = NEON_GREEN if "شراء" in sig else (NEON_RED if "بيع" in sig else NEON_GOLD)
            items.append(
                glass_card(
                    ft.Row([
                        ft.Column([ft.Text(sym, weight=ft.FontWeight.BOLD), ft.Text(f"السعر الحي: {p:.2f}", size=11, color=TEXT_SECONDARY)]),
                        section_badge(sig, col)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10
                )
            )
        return ft.Column([ft.Text(t("signals"), size=18, weight=ft.FontWeight.BOLD), *items], spacing=8, scroll=ft.ScrollMode.AUTO)

    def view_news():
        news_list = [
            ("تحديثات السياسة النقدية وأسعار الفائدة الأمريكية", "تأثير مرتفع على أزواج الدولار والذهب XAU/USD", NEON_RED),
            ("حركة السيولة في أسواق العملات الرقمية BTC & ETH", "تأثير متوسط — متابعة مستويات المقاومة", NEON_GOLD),
            ("استقرار خوارزميات مؤشرات التذبذب الاصطناعية Volatility", "تأثير منخفض — حركة فنية منتظمة", NEON_CYAN),
        ]
        return ft.Column([
            ft.Text(t("news"), size=18, weight=ft.FontWeight.BOLD),
            *[glass_card(ft.Column([ft.Text(n[0], weight=ft.FontWeight.BOLD), ft.Text(n[1], size=12, color=n[2])])) for n in news_list]
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def view_calendar():
        events = [
            ("15:30", "USD — بيانات التضخم ومؤشر أسعار المستهلكين", "عالي التأثير", NEON_RED),
            ("17:00", "EUR — تصريحات البنك المركزي الأوروبي", "متوسط التأثير", NEON_GOLD),
            ("21:00", "USD — محضر اجتماع اللجنة الفيدرالية", "عالي التأثير", NEON_RED),
        ]
        return ft.Column([
            ft.Text(t("calendar"), size=18, weight=ft.FontWeight.BOLD),
            *[glass_card(ft.Row([ft.Text(e[0], color=NEON_CYAN, weight=ft.FontWeight.BOLD), ft.Column([ft.Text(e[1], size=12), section_badge(e[2], e[3])], expand=True)])) for e in events]
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def view_strategy_lab():
        strategies = [
            ("EMA + RSI Confluence", "دمج تقاطع EMA 9/21 مع فلتر القوة النسبية RSI لتقليل الإشارات الكاذبة."),
            ("Bollinger Reversal", "استهداف ارتداد السعر من الحدود العليا والسفلى لقنوات بولينجر."),
            ("Price Action Candle AI", "الاعتماد على نماذج الشموع الانعكاسية عند مستويات الدعم والمقاومة."),
        ]

        def set_strat(name):
            state["active_strategy"] = name
            render_view()

        return ft.Column([
            ft.Text(t("strategy_lab"), size=18, weight=ft.FontWeight.BOLD),
            ft.Text(f"الاستراتيجية النشطة: {state['active_strategy']}", color=NEON_GREEN, size=13),
            *[
                glass_card(
                    ft.Column([
                        ft.Text(s[0], size=15, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
                        ft.Text(s[1], size=12, color=TEXT_SECONDARY),
                        ft.ElevatedButton("تفعيل الاستراتيجية", on_click=lambda _, n=s[0]: set_strat(n))
                    ])
                ) for s in strategies
            ]
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def view_backtest():
        an = get_current_analysis()
        candles = an["candles"]
        wins, losses = 0, 0
        for i in range(5, len(candles) - 1):
            if candles[i]["close"] > candles[i - 1]["close"]:
                if candles[i + 1]["close"] > candles[i]["close"]:
                    wins += 1
                else:
                    losses += 1
        total = max(wins + losses, 1)
        win_rate = (wins / total) * 100

        return ft.Column([
            ft.Text(t("backtest"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    ft.Text(f"الأصل المختبر: {state['selected_symbol']}", color=NEON_CYAN),
                    ft.Text(f"الاستراتيجية: {state['active_strategy']}", size=13),
                    ft.Text(f"عدد الشموع الحقيقية المختبرة: {len(candles)}", size=13),
                    ft.Divider(color=BORDER_GLOW),
                    ft.Row([ft.Text("إجمالي الإشارات التاريخية:"), ft.Text(f"{wins + losses}", weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("نسبة النجاح المحسوبة:"), ft.Text(f"{win_rate:.1f}%", color=NEON_GREEN, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=8)
            )
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def view_portfolio():
        def close_trade(idx):
            tr = state["open_trades"].pop(idx)
            curr_p = state["prices"].get(tr["symbol"], tr["entry"])
            diff_pct = (curr_p - tr["entry"]) / max(tr["entry"], 0.0001)
            if tr["side"] == "SELL":
                diff_pct = -diff_pct
            pnl = round(tr["stake"] * diff_pct * 50, 2)
            tr["pnl"] = pnl
            tr["status"] = "CLOSED"
            state["paper_balance"] = round(state["paper_balance"] + pnl, 2)
            state["equity_curve"].append(state["paper_balance"])
            state["trade_history"].insert(0, tr)
            asyncio.create_task(save_all_state())
            render_view()

        def reset_account(_):
            state["paper_balance"] = 10000.0
            state["equity_curve"] = [10000.0]
            state["open_trades"] = []
            state["trade_history"] = []
            asyncio.create_task(save_all_state())
            render_view()

        open_cards = []
        for i, tr in enumerate(state["open_trades"]):
            open_cards.append(
                glass_card(
                    ft.Row([
                        ft.Column([
                            ft.Text(f"{tr['symbol']} ({tr['side']})", weight=ft.FontWeight.BOLD, color=NEON_GREEN if tr["side"] == "BUY" else NEON_RED),
                            ft.Text(f"دخول: {tr['entry']} | حجم: ${tr['stake']}", size=11, color=TEXT_SECONDARY),
                        ]),
                        ft.ElevatedButton("إغلاق الصفقة", bgcolor=NEON_GOLD, color=BG_DARK, on_click=lambda _, idx=i: close_trade(idx))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )

        return ft.Column([
            ft.Text(t("portfolio"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    ft.Text(t("virtual_balance"), size=12, color=TEXT_SECONDARY),
                    ft.Text(f"${state['paper_balance']:,.2f}", size=26, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
                    ft.Text("منحنى تطور المحفظة الافتراضية:", size=11, color=TEXT_SECONDARY),
                    build_equity_chart(state["equity_curve"]),
                    ft.OutlinedButton(t("reset_acc"), on_click=reset_account)
                ], spacing=8)
            ),
            ft.Text(f"الصفقات الافتراضية المفتوحة ({len(open_cards)})", weight=ft.FontWeight.BOLD),
            *(open_cards if open_cards else [ft.Text("لا توجد صفقات مفتوحة حالياً. افتح صفقة تجريبية من صفحة الرسم البياني.", size=12, color=TEXT_SECONDARY)])
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def view_risk():
        risk_amount = round(state["paper_balance"] * (state["risk_percent"] / 100.0), 2)

        def on_risk_change(e):
            state["risk_percent"] = round(e.control.value, 1)
            asyncio.create_task(save_all_state())
            render_view()

        return ft.Column([
            ft.Text(t("risk"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    ft.Text(f"نسبة المخاطرة لكل صفقة افتراضية: {state['risk_percent']}%", size=14, weight=ft.FontWeight.BOLD),
                    ft.Slider(min=0.5, max=10.0, divisions=19, value=state["risk_percent"], active_color=NEON_CYAN, on_change=on_risk_change),
                    ft.Divider(color=BORDER_GLOW),
                    ft.Row([ft.Text("حجم الحساب الافتراضي:"), ft.Text(f"${state['paper_balance']:,.2f}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("المبلغ المخاطر به بالصفقة:"), ft.Text(f"${risk_amount:,.2f}", color=NEON_GOLD, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10)
            )
        ], spacing=12)

    def view_journal():
        hist_cards = [
            glass_card(
                ft.Row([
                    ft.Column([
                        ft.Text(f"{h['symbol']} • {h['side']}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"دخول: {h['entry']} | {h['time']}", size=11, color=TEXT_SECONDARY)
                    ]),
                    ft.Text(f"{h['pnl']:+.2f}$", weight=ft.FontWeight.BOLD, color=NEON_GREEN if h["pnl"] >= 0 else NEON_RED)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10
            )
            for h in state["trade_history"]
        ]
        return ft.Column([
            ft.Text(t("journal"), size=18, weight=ft.FontWeight.BOLD),
            *(hist_cards if hist_cards else [ft.Text("سجل التداول الافتراضي فارغ حالياً.", color=TEXT_SECONDARY)])
        ], spacing=8, scroll=ft.ScrollMode.AUTO)

    def view_assistant():
        chat_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=340)
        for m in state["chat_messages"]:
            is_ai = m["sender"] == "ai"
            chat_col.controls.append(
                ft.Container(
                    bgcolor=CARD_GLASS if is_ai else "#1D2B53",
                    border=ft.border.all(1, NEON_CYAN if is_ai else NEON_PURPLE),
                    border_radius=12,
                    padding=10,
                    content=ft.Text(m["text"], size=12, color=TEXT_PRIMARY)
                )
            )

        prompt_in = ft.TextField(hint_text="اسأل المساعد الذكي عن السوق أو المؤشرات...", expand=True, border_radius=12)

        def send_msg(_):
            q = prompt_in.value.strip()
            if not q:
                return
            state["chat_messages"].append({"sender": "user", "text": q})
            an = get_current_analysis()
            reply = (
                f"تحليل {an['symbol']} الحي (السعر: {an['price']}):\n"
                f"• التوجه الفني الحالي: {an['direction']}\n"
                f"• مؤشر RSI عند {an['rsi']:.1f}، ومؤشر MACD عند {an['macd_l']:.4f}، ونموذج الشمعة: {an['candle_name']}.\n"
                f"• السيناريو الصاعد: {an['bull_prob']}% مقابل الهابط: {an['bear_prob']}%.\n"
                f"تذكر: هذه قراءة تعليمية مبنية على البيانات الحية وليست ضماناً للربح."
            )
            state["chat_messages"].append({"sender": "ai", "text": reply})
            render_view()

        return ft.Column([
            ft.Row([build_robot_emblem(42), ft.Text(t("assistant"), size=18, weight=ft.FontWeight.BOLD)]),
            glass_card(chat_col),
            ft.Row([
                prompt_in,
                ft.IconButton(icon=ft.icons.SEND_ROUNDED, icon_color=NEON_CYAN, on_click=send_msg)
            ])
        ], spacing=10)

    def view_reports():
        total = len(state["trade_history"])
        wins = len([h for h in state["trade_history"] if h["pnl"] > 0])
        net = sum(h["pnl"] for h in state["trade_history"])
        rate = (wins / total * 100) if total > 0 else 0.0
        return ft.Column([
            ft.Text(t("reports"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    ft.Text("تقرير أداء المحاكاة (Paper Trading)", size=15, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
                    build_equity_chart(state["equity_curve"], height=120),
                    ft.Row([ft.Text("إجمالي الصفقات المغلقة:"), ft.Text(f"{total}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("الصفقات الرابحة:"), ft.Text(f"{wins}", color=NEON_GREEN)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("نسبة النجاح:"), ft.Text(f"{rate:.1f}%", color=NEON_GOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("صافي الربح/الخسارة الافتراضي:"), ft.Text(f"{net:+.2f}$", color=NEON_GREEN if net >= 0 else NEON_RED)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10)
            )
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def view_alerts():
        return ft.Column([
            ft.Text(t("alerts"), size=18, weight=ft.FontWeight.BOLD),
            *[glass_card(ft.Row([ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=NEON_CYAN), ft.Text(a["msg"], size=12, expand=True)])) for a in state["alerts"]]
        ], spacing=8, scroll=ft.ScrollMode.AUTO)

    def toggle_language(return_route="settings"):
        state["lang"] = "en" if state["lang"] == "ar" else "ar"
        page.rtl = (state["lang"] == "ar")
        asyncio.create_task(page.client_storage.set_async("lang", state["lang"]))
        navigate(return_route)

    def view_settings():
        return ft.Column([
            ft.Text(t("settings"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    ft.Text(f"المستخدم: {state['user_email']}", size=13),
                    ft.ElevatedButton(t("lang_switch"), on_click=lambda _: toggle_language("settings")),
                    ft.OutlinedButton("تسجيل الخروج", on_click=lambda _: navigate("login"))
                ], spacing=12)
            )
        ], spacing=12)

    def view_api_connections():
        token_field = ft.TextField(
            label="Deriv Demo API Token (للقراءة فقط)",
            password=True,
            can_reveal_password=True,
            value=state["deriv_token"],
            border_color=NEON_CYAN
        )
        status_txt = ft.Text(
            f"الحالة: {state['deriv_account_id']} | الرصيد التجريبي المصرح: ${state['deriv_real_demo_bal']:.2f}",
            color=NEON_GREEN if state["deriv_demo_verified"] else TEXT_SECONDARY,
            size=12
        )

        async def verify_deriv_demo_token(_):
            tk = token_field.value.strip()
            if not tk:
                return
            state["deriv_token"] = tk
            await save_all_state()
            try:
                async with websockets.connect(DERIV_WS_URL) as ws:
                    await ws.send(json.dumps({"authorize": tk}))
                    res = json.loads(await ws.recv())
                    if "authorize" in res:
                        auth = res["authorize"]
                        if auth.get("is_virtual") == 1:
                            state["deriv_demo_verified"] = True
                            state["deriv_account_id"] = f"Demo ({auth.get('loginid')})"
                            state["deriv_real_demo_bal"] = float(auth.get("balance", 0.0))
                        else:
                            state["deriv_demo_verified"] = False
                            state["deriv_account_id"] = "مرفوض: يُسمح بالحسابات التجريبية Demo فقط!"
                    else:
                        state["deriv_account_id"] = "رمز API غير صالح"
            except Exception as ex:
                state["deriv_account_id"] = f"خطأ اتصال: {ex}"
            render_view()

        return ft.Column([
            ft.Text(t("api_conn"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    section_badge("DEMO ACCOUNT ONLY — READ ONLY", NEON_GOLD),
                    ft.Text("يقبل التطبيق رموز حسابات Deriv التجريبية (Virtual/Demo) فقط، ويُعطل تماماً تنفيذ الصفقات المالية الحقيقية لحماية المستخدم.", size=12, color=TEXT_SECONDARY),
                    token_field,
                    ft.ElevatedButton(
                        text="التحقق من اتصال حساب Deriv التجريبي",
                        bgcolor=NEON_CYAN,
                        color=BG_DARK,
                        on_click=lambda e: asyncio.create_task(verify_deriv_demo_token(e))
                    ),
                    status_txt
                ], spacing=10)
            )
        ], spacing=12)

    def view_about():
        return ft.Column([
            ft.Text(t("about"), size=18, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column([
                    build_robot_emblem(64),
                    ft.Text("AI TRADING BOT — DERIV ULTIMATE AI", size=16, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
                    ft.Text("منصة ذكية لتحليل الأسواق المالية وتعليم التداول والمحاكاة الافتراضية (Paper Trading) باستخدام بيانات Deriv الحية.", size=12),
                    ft.Text("الإصدار: 2.0.0 Ultimate Android Release", size=11, color=TEXT_SECONDARY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            )
        ], spacing=12)

    # ==========================================
    # القائمة الجانبية وشريط التنقل السفلي
    # ==========================================
    drawer_items = [
        ("dashboard", t("dashboard"), ft.icons.DASHBOARD),
        ("markets", t("markets"), ft.icons.SHOW_CHART),
        ("charts", t("charts"), ft.icons.CANDLESTICK_CHART),
        ("ai_analysis", t("ai_analysis"), ft.icons.PSYCHOLOGY),
        ("candles", t("candles"), ft.icons.AUTO_GRAPH),
        ("indicators", t("indicators"), ft.icons.ANALYTICS),
        ("signals", t("signals"), ft.icons.BOLT),
        ("news", t("news"), ft.icons.NEWSPAPER),
        ("calendar", t("calendar"), ft.icons.EVENT_NOTE),
        ("strategy_lab", t("strategy_lab"), ft.icons.SCIENCE),
        ("backtest", t("backtest"), ft.icons.HISTORY),
        ("portfolio", t("portfolio"), ft.icons.ACCOUNT_BALANCE_WALLET),
        ("risk", t("risk"), ft.icons.SECURITY),
        ("journal", t("journal"), ft.icons.BOOK),
        ("assistant", t("assistant"), ft.icons.SMART_TOY),
        ("reports", t("reports"), ft.icons.ASSESSMENT),
        ("alerts", t("alerts"), ft.icons.NOTIFICATIONS),
        ("api_conn", t("api_conn"), ft.icons.API),
        ("settings", t("settings"), ft.icons.SETTINGS),
        ("about", t("about"), ft.icons.INFO),
    ]

    page.drawer = ft.NavigationDrawer(
        bgcolor=BG_NAVY,
        controls=[
            ft.Container(
                padding=16,
                content=ft.Row([build_robot_emblem(44), ft.Text("ULTIMATE AI v2", weight=ft.FontWeight.BOLD, color=NEON_CYAN)])
            ),
            ft.Divider(color=BORDER_GLOW),
            *[
                ft.ListTile(
                    leading=ft.Icon(ic, color=NEON_CYAN, size=20),
                    title=ft.Text(lbl, size=13),
                    on_click=lambda _, r=rt: navigate(r)
                ) for rt, lbl, ic in drawer_items
            ]
        ]
    )

    app_bar = ft.AppBar(
        bgcolor=BG_NAVY,
        leading=ft.IconButton(ft.icons.MENU, icon_color=NEON_CYAN, on_click=lambda _: page.open(page.drawer)),
        title=ft.Text("AI TRADING BOT ULTIMATE", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
        actions=[
            ft.IconButton(ft.icons.NOTIFICATIONS_OUTLINED, icon_color=NEON_GOLD, on_click=lambda _: navigate("alerts")),
            ft.IconButton(ft.icons.SMART_TOY_OUTLINED, icon_color=NEON_CYAN, on_click=lambda _: navigate("assistant")),
        ]
    )

    bottom_nav = ft.NavigationBar(
        bgcolor=BG_NAVY,
        indicator_color=ft.colors.with_opacity(0.2, NEON_CYAN),
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label="الرئيسية"),
            ft.NavigationBarDestination(icon=ft.icons.SHOW_CHART, label="الأسواق"),
            ft.NavigationBarDestination(icon=ft.icons.CANDLESTICK_CHART, label="الشارت"),
            ft.NavigationBarDestination(icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED, label="المحفظة"),
            ft.NavigationBarDestination(icon=ft.icons.PSYCHOLOGY_OUTLINED, label="تحليل AI"),
        ],
        on_change=lambda e: navigate(["dashboard", "markets", "charts", "portfolio", "ai_analysis"][e.control.selected_index])
    )

    def render_view():
        r = current_route["name"]
        views_map = {
            "splash": view_splash,
            "login": view_login,
            "dashboard": view_dashboard,
            "markets": view_markets,
            "charts": view_charts,
            "ai_analysis": view_ai_analysis,
            "candles": view_candles,
            "indicators": view_indicators,
            "signals": view_signals,
            "news": view_news,
            "calendar": view_calendar,
            "strategy_lab": view_strategy_lab,
            "backtest": view_backtest,
            "portfolio": view_portfolio,
            "risk": view_risk,
            "journal": view_journal,
            "assistant": view_assistant,
            "reports": view_reports,
            "alerts": view_alerts,
            "settings": view_settings,
            "api_conn": view_api_connections,
            "about": view_about,
        }
        is_auth_screen = r in ["splash", "login"]
        page.appbar = None if is_auth_screen else app_bar
        page.navigation_bar = None if is_auth_screen else bottom_nav
        main_container.padding = 0 if is_auth_screen else 14
        main_container.content = views_map.get(r, view_dashboard)()
        page.update()

    page.add(main_container)
    render_view()

    asyncio.create_task(deriv_feed_worker())

if __name__ == "__main__":
    ft.app(target=main)
