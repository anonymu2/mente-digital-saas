import ccxt
import os

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True
})

def get_profit(email):
    # TODO: conectar a tu lógica real de trading
    # Por ahora simulamos profit por usuario
    return 123.45
