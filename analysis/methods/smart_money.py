from typing import Dict, List
import numpy as np

class SmartMoneyAnalyzer:
    def analyze(self, ohlc_data: List[Dict], timeframe: str) -> Dict:
        order_blocks = self.identify_order_blocks(ohlc_data)
        fair_value_gaps = self.identify_fair_value_gaps(ohlc_data)
        structure_breaks = self.analyze_structure_breaks(ohlc_data)
        liquidity_zones = self.identify_liquidity_zones(ohlc_data)
        smc_signals = self.generate_smc_signals(order_blocks, fair_value_gaps, structure_breaks, liquidity_zones)
        
        return {
            "order_blocks": order_blocks,
            "fair_value_gaps": fair_value_gaps,
            "structure_breaks": structure_breaks,
            "liquidity_zones": liquidity_zones,
            "smc_signals": smc_signals
        }

    def identify_order_blocks(self, ohlc_data: List[Dict]) -> List[Dict]:
        if len(ohlc_data) < 10:
            return []
        
        order_blocks = []
        
        for i in range(3, len(ohlc_data) - 3):
            current = ohlc_data[i]
            prev_candles = ohlc_data[i-3:i]
            next_candles = ohlc_data[i+1:i+4]
            
            is_bullish_ob = self.is_bullish_order_block(current, prev_candles, next_candles)
            is_bearish_ob = self.is_bearish_order_block(current, prev_candles, next_candles)
            
            if is_bullish_ob:
                order_blocks.append({
                    "level": current['low'],
                    "type": "bullish",
                    "strength": self.calculate_ob_strength(current, next_candles),
                    "index": i
                })
            elif is_bearish_ob:
                order_blocks.append({
                    "level": current['high'],
                    "type": "bearish", 
                    "strength": self.calculate_ob_strength(current, next_candles),
                    "index": i
                })
        
        return order_blocks[-10:]

    def is_bullish_order_block(self, current: Dict, prev_candles: List[Dict], next_candles: List[Dict]) -> bool:
        if not next_candles:
            return False
        
        current_body = abs(current['close'] - current['open'])
        current_range = current['high'] - current['low']
        
        if current_body < current_range * 0.6:
            return False
        
        if current['close'] <= current['open']:
            return False
        
        next_high = max(candle['high'] for candle in next_candles)
        return next_high > current['high']

    def is_bearish_order_block(self, current: Dict, prev_candles: List[Dict], next_candles: List[Dict]) -> bool:
        if not next_candles:
            return False
        
        current_body = abs(current['close'] - current['open'])
        current_range = current['high'] - current['low']
        
        if current_body < current_range * 0.6:
            return False
        
        if current['close'] >= current['open']:
            return False
        
        next_low = min(candle['low'] for candle in next_candles)
        return next_low < current['low']

    def calculate_ob_strength(self, current: Dict, next_candles: List[Dict]) -> str:
        if not next_candles:
            return "weak"
        
        current_volume = current.get('volume', 0)
        avg_volume = sum(candle.get('volume', 0) for candle in next_candles) / len(next_candles)
        
        if current_volume > avg_volume * 1.5:
            return "strong"
        elif current_volume > avg_volume:
            return "medium"
        else:
            return "weak"

    def identify_fair_value_gaps(self, ohlc_data: List[Dict]) -> List[Dict]:
        if len(ohlc_data) < 3:
            return []
        
        fvgs = []
        
        for i in range(1, len(ohlc_data) - 1):
            prev_candle = ohlc_data[i-1]
            current_candle = ohlc_data[i]
            next_candle = ohlc_data[i+1]
            
            bullish_fvg = self.is_bullish_fvg(prev_candle, current_candle, next_candle)
            bearish_fvg = self.is_bearish_fvg(prev_candle, current_candle, next_candle)
            
            if bullish_fvg:
                fvgs.append({
                    "start": prev_candle['high'],
                    "end": next_candle['low'],
                    "type": "bullish",
                    "status": "unfilled",
                    "index": i
                })
            elif bearish_fvg:
                fvgs.append({
                    "start": prev_candle['low'],
                    "end": next_candle['high'],
                    "type": "bearish",
                    "status": "unfilled",
                    "index": i
                })
        
        return fvgs[-10:]

    def is_bullish_fvg(self, prev: Dict, current: Dict, next: Dict) -> bool:
        return prev['high'] < next['low'] and current['close'] > current['open']

    def is_bearish_fvg(self, prev: Dict, current: Dict, next: Dict) -> bool:
        return prev['low'] > next['high'] and current['close'] < current['open']

    def analyze_structure_breaks(self, ohlc_data: List[Dict]) -> List[Dict]:
        if len(ohlc_data) < 20:
            return []
        
        structure_breaks = []
        swing_highs = []
        swing_lows = []
        
        for i in range(5, len(ohlc_data) - 5):
            is_swing_high = all(ohlc_data[i]['high'] >= ohlc_data[j]['high'] for j in range(i-5, i+6) if j != i)
            is_swing_low = all(ohlc_data[i]['low'] <= ohlc_data[j]['low'] for j in range(i-5, i+6) if j != i)
            
            if is_swing_high:
                swing_highs.append({"price": ohlc_data[i]['high'], "index": i})
            if is_swing_low:
                swing_lows.append({"price": ohlc_data[i]['low'], "index": i})
        
        for i in range(len(swing_highs) - 1):
            current_high = swing_highs[i]
            next_high = swing_highs[i + 1]
            
            if next_high["price"] > current_high["price"]:
                structure_breaks.append({
                    "level": current_high["price"],
                    "direction": "bullish",
                    "confirmed": True,
                    "type": "higher_high"
                })
        
        for i in range(len(swing_lows) - 1):
            current_low = swing_lows[i]
            next_low = swing_lows[i + 1]
            
            if next_low["price"] < current_low["price"]:
                structure_breaks.append({
                    "level": current_low["price"],
                    "direction": "bearish",
                    "confirmed": True,
                    "type": "lower_low"
                })
        
        return structure_breaks[-5:]

    def identify_liquidity_zones(self, ohlc_data: List[Dict]) -> List[Dict]:
        if len(ohlc_data) < 10:
            return []
        
        liquidity_zones = []
        
        for i in range(5, len(ohlc_data) - 1):
            current = ohlc_data[i]
            prev_candles = ohlc_data[i-5:i]
            
            prev_highs = [candle['high'] for candle in prev_candles]
            prev_lows = [candle['low'] for candle in prev_candles]
            
            if current['high'] > max(prev_highs):
                liquidity_zones.append({
                    "start": min(prev_highs),
                    "end": max(prev_highs),
                    "type": "swept",
                    "direction": "bullish"
                })
            
            if current['low'] < min(prev_lows):
                liquidity_zones.append({
                    "start": min(prev_lows),
                    "end": max(prev_lows),
                    "type": "swept",
                    "direction": "bearish"
                })
        
        return liquidity_zones[-5:]

    def generate_smc_signals(self, order_blocks: List[Dict], fair_value_gaps: List[Dict], 
                           structure_breaks: List[Dict], liquidity_zones: List[Dict]) -> Dict:
        
        bullish_signals = 0
        bearish_signals = 0
        
        for ob in order_blocks[-3:]:
            if ob['type'] == 'bullish' and ob['strength'] in ['strong', 'medium']:
                bullish_signals += 1
            elif ob['type'] == 'bearish' and ob['strength'] in ['strong', 'medium']:
                bearish_signals += 1
        
        for sb in structure_breaks[-2:]:
            if sb['direction'] == 'bullish' and sb['confirmed']:
                bullish_signals += 1
            elif sb['direction'] == 'bearish' and sb['confirmed']:
                bearish_signals += 1
        
        unfilled_bullish_fvgs = [fvg for fvg in fair_value_gaps if fvg['type'] == 'bullish' and fvg['status'] == 'unfilled']
        unfilled_bearish_fvgs = [fvg for fvg in fair_value_gaps if fvg['type'] == 'bearish' and fvg['status'] == 'unfilled']
        
        if len(unfilled_bullish_fvgs) > len(unfilled_bearish_fvgs):
            bullish_signals += 1
        elif len(unfilled_bearish_fvgs) > len(unfilled_bullish_fvgs):
            bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            market_structure = "bullish_shift"
            signal_strength = "strong" if bullish_signals >= 3 else "medium"
        elif bearish_signals > bullish_signals:
            market_structure = "bearish_shift"
            signal_strength = "strong" if bearish_signals >= 3 else "medium"
        else:
            market_structure = "consolidation"
            signal_strength = "weak"
        
        return {
            "market_structure": market_structure,
            "signal_strength": signal_strength,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "unfilled_fvgs": len(unfilled_bullish_fvgs) + len(unfilled_bearish_fvgs)
        }