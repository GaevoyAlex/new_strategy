from typing import Dict, List
import numpy as np

class ElliottWaveAnalyzer:
    def __init__(self):
        self.fibonacci_ratios = [0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618, 2.618]

    def analyze(self, ohlc_data: List[Dict], timeframe: str) -> Dict:
        wave_structure = self.identify_wave_structure(ohlc_data)
        fibonacci_levels = self.calculate_fibonacci_levels(wave_structure)
        current_wave = self.identify_current_wave(wave_structure)
        forecast = self.generate_forecast(current_wave, fibonacci_levels)
        
        return {
            "wave_structure": wave_structure,
            "fibonacci_levels": fibonacci_levels,
            "current_wave": current_wave,
            "forecast": forecast
        }

    def identify_wave_structure(self, ohlc_data: List[Dict]) -> Dict:
        if len(ohlc_data) < 20:
            return {}
        
        highs = [candle['high'] for candle in ohlc_data]
        lows = [candle['low'] for candle in ohlc_data]
        closes = [candle['close'] for candle in ohlc_data]
        
        pivots = self.find_pivots(highs, lows)
        waves = self.identify_waves_from_pivots(pivots)
        
        return {
            "waves": waves,
            "pivots": pivots,
            "trend": self.determine_trend(closes)
        }

    def find_pivots(self, highs: List[float], lows: List[float]) -> List[Dict]:
        pivots = []
        window = 5
        
        for i in range(window, len(highs) - window):
            is_high_pivot = all(highs[i] >= highs[i+j] for j in range(-window, window+1) if j != 0)
            is_low_pivot = all(lows[i] <= lows[i+j] for j in range(-window, window+1) if j != 0)
            
            if is_high_pivot:
                pivots.append({"index": i, "price": highs[i], "type": "high"})
            elif is_low_pivot:
                pivots.append({"index": i, "price": lows[i], "type": "low"})
        
        return pivots

    def identify_waves_from_pivots(self, pivots: List[Dict]) -> Dict:
        if len(pivots) < 5:
            return {}
        
        waves = {}
        for i in range(min(5, len(pivots) - 1)):
            wave_num = i + 1
            start_pivot = pivots[i]
            end_pivot = pivots[i + 1] if i + 1 < len(pivots) else pivots[i]
            
            waves[f"wave_{wave_num}"] = {
                "start": start_pivot["price"],
                "end": end_pivot["price"],
                "type": "impulse" if wave_num in [1, 3, 5] else "corrective",
                "direction": "up" if end_pivot["price"] > start_pivot["price"] else "down"
            }
        
        return waves

    def calculate_fibonacci_levels(self, wave_structure: Dict) -> Dict:
        if not wave_structure.get("waves"):
            return {}
        
        waves = wave_structure["waves"]
        if "wave_1" not in waves or "wave_2" not in waves:
            return {}
        
        wave_1_start = waves["wave_1"]["start"]
        wave_1_end = waves["wave_1"]["end"]
        wave_range = abs(wave_1_end - wave_1_start)
        
        fibonacci_levels = {}
        for ratio in self.fibonacci_ratios:
            if wave_1_end > wave_1_start:
                level = wave_1_end + (wave_range * ratio)
            else:
                level = wave_1_end - (wave_range * ratio)
            fibonacci_levels[f"fib_{ratio}"] = round(level, 2)
        
        return fibonacci_levels

    def identify_current_wave(self, wave_structure: Dict) -> int:
        if not wave_structure.get("waves"):
            return 1
        
        wave_count = len(wave_structure["waves"])
        return min(wave_count + 1, 5)

    def generate_forecast(self, current_wave: int, fibonacci_levels: Dict) -> Dict:
        if not fibonacci_levels:
            return {}
        
        forecast = {
            "next_wave": current_wave + 1 if current_wave < 5 else 1,
            "targets": [],
            "support_resistance": []
        }
        
        if current_wave == 3:
            forecast["targets"] = [
                fibonacci_levels.get("fib_1.618", 0),
                fibonacci_levels.get("fib_2.618", 0)
            ]
        elif current_wave == 4:
            forecast["targets"] = [
                fibonacci_levels.get("fib_0.382", 0),
                fibonacci_levels.get("fib_0.618", 0)
            ]
        
        return forecast

    def determine_trend(self, closes: List[float]) -> str:
        if len(closes) < 20:
            return "sideways"
        
        recent_closes = closes[-20:]
        trend_line = np.polyfit(range(len(recent_closes)), recent_closes, 1)
        
        if trend_line[0] > 0:
            return "bullish"
        elif trend_line[0] < 0:
            return "bearish"
        else:
            return "sideways"