# utils/binance_bot.py
import random

def get_profit(user):
    # Aquí va la integración real con Binance
    profit = round(random.uniform(0, 200), 2)  # Simulación
    user["profit"] = profit
    return profit
