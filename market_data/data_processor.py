from typing import List, Dict, Any
import numpy as np
from datetime import datetime

def parse_klines_to_ohlc(klines_data: List[List]) -> List[Dict[str, Any]]:
    ohlc_data = []
    for kline in klines_data:
        ohlc_data.append({
            "timestamp": int(kline[0]),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5])
        })
    return ohlc_data

def calculate_volume_profile(klines_data: List[Dict], order_book_data: Dict = None) -> Dict:
    if not klines_data:
        return {}
    
    prices = []
    volumes = []
    
    for candle in klines_data:
        high = candle['high']
        low = candle['low']
        volume = candle['volume']
        
        price_range = np.linspace(low, high, 10)
        volume_per_level = volume / 10
        
        prices.extend(price_range)
        volumes.extend([volume_per_level] * 10)
    
    if not prices:
        return {}
    
    price_levels = np.linspace(min(prices), max(prices), 50)
    volume_by_price = {}
    
    for i, price_level in enumerate(price_levels):
        volume_at_level = 0
        for j, price in enumerate(prices):
            if abs(price - price_level) <= (max(prices) - min(prices)) / 50:
                volume_at_level += volumes[j]
        volume_by_price[float(price_level)] = volume_at_level
    
    sorted_volumes = sorted(volume_by_price.items(), key=lambda x: x[1], reverse=True)
    
    total_volume = sum(volume_by_price.values())
    cumulative_volume = 0
    value_area_volume = total_volume * 0.68
    
    poc = sorted_volumes[0][0] if sorted_volumes else 0
    
    vah = poc
    val = poc
    
    for price, volume in sorted_volumes:
        cumulative_volume += volume
        if price > poc:
            vah = max(vah, price)
        if price < poc:
            val = min(val, price)
        if cumulative_volume >= value_area_volume:
            break
    
    return {
        "poc": poc,
        "vah": vah,
        "val": val,
        "volume_by_price": volume_by_price
    }

def calculate_support_resistance(ohlc_data: List[Dict]) -> Dict:
    if len(ohlc_data) < 20:
        return {"support_levels": [], "resistance_levels": []}
    
    highs = [candle['high'] for candle in ohlc_data]
    lows = [candle['low'] for candle in ohlc_data]
    
    support_levels = []
    resistance_levels = []
    
    for i in range(2, len(lows) - 2):
        if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
            lows[i] < lows[i+1] and lows[i] < lows[i+2]):
            support_levels.append(lows[i])
    
    for i in range(2, len(highs) - 2):
        if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
            highs[i] > highs[i+1] and highs[i] > highs[i+2]):
            resistance_levels.append(highs[i])
    
    return {
        "support_levels": sorted(list(set(support_levels)), reverse=True)[:5],
        "resistance_levels": sorted(list(set(resistance_levels)))[:5]
    }