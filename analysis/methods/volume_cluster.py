from typing import Dict, List
import numpy as np

class VolumeClusterAnalyzer:
    def analyze(self, ohlcv_data: List[Dict], order_book_data: Dict, timeframe: str) -> Dict:
        volume_profile = self.calculate_volume_profile(ohlcv_data)
        key_levels = self.identify_key_levels(volume_profile, order_book_data)
        market_position = self.analyze_market_position(key_levels)
        trading_signals = self.generate_trading_signals(market_position)
        
        return {
            "volume_profile": volume_profile,
            "key_levels": key_levels,
            "market_position": market_position,
            "trading_signals": trading_signals
        }

    def calculate_volume_profile(self, ohlcv_data: List[Dict]) -> Dict:
        if not ohlcv_data:
            return {}
        
        all_prices = []
        all_volumes = []
        
        for candle in ohlcv_data:
            high = candle['high']
            low = candle['low']
            volume = candle['volume']
            
            price_levels = np.linspace(low, high, 10)
            volume_per_level = volume / 10
            
            all_prices.extend(price_levels)
            all_volumes.extend([volume_per_level] * 10)
        
        if not all_prices:
            return {}
        
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_bins = np.linspace(min_price, max_price, 50)
        
        volume_by_price = {}
        
        for i in range(len(price_bins) - 1):
            bin_volume = 0
            bin_center = (price_bins[i] + price_bins[i + 1]) / 2
            
            for j, price in enumerate(all_prices):
                if price_bins[i] <= price < price_bins[i + 1]:
                    bin_volume += all_volumes[j]
            
            volume_by_price[round(bin_center, 2)] = bin_volume
        
        sorted_volumes = sorted(volume_by_price.items(), key=lambda x: x[1], reverse=True)
        
        poc = sorted_volumes[0][0] if sorted_volumes else 0
        
        total_volume = sum(volume_by_price.values())
        value_area_volume = total_volume * 0.68
        cumulative_volume = 0
        
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
            "volume_distribution": volume_by_price
        }

    def identify_key_levels(self, volume_profile: Dict, order_book_data: Dict) -> Dict:
        key_levels = {
            "support_levels": [],
            "resistance_levels": [],
            "high_volume_levels": []
        }
        
        if not volume_profile.get("volume_distribution"):
            return key_levels
        
        volume_dist = volume_profile["volume_distribution"]
        sorted_volumes = sorted(volume_dist.items(), key=lambda x: x[1], reverse=True)
        
        high_volume_levels = [price for price, volume in sorted_volumes[:10]]
        key_levels["high_volume_levels"] = high_volume_levels
        
        poc = volume_profile.get("poc", 0)
        current_price = max(volume_dist.keys()) if volume_dist else 0
        
        support_levels = [price for price in high_volume_levels if price < current_price]
        resistance_levels = [price for price in high_volume_levels if price > current_price]
        
        key_levels["support_levels"] = sorted(support_levels, reverse=True)[:5]
        key_levels["resistance_levels"] = sorted(resistance_levels)[:5]
        
        if order_book_data:
            bid_levels = self.analyze_order_book_levels(order_book_data, "bids")
            ask_levels = self.analyze_order_book_levels(order_book_data, "asks")
            
            key_levels["bid_support"] = bid_levels
            key_levels["ask_resistance"] = ask_levels
        
        return key_levels

    def analyze_order_book_levels(self, order_book_data: Dict, side: str) -> List[float]:
        if side not in order_book_data:
            return []
        
        levels = order_book_data[side][:20]
        significant_levels = []
        
        for price_str, quantity_str in levels:
            price = float(price_str)
            quantity = float(quantity_str)
            
            if quantity > 100:
                significant_levels.append(price)
        
        return significant_levels[:5]

    def analyze_market_position(self, key_levels: Dict) -> Dict:
        support_levels = key_levels.get("support_levels", [])
        resistance_levels = key_levels.get("resistance_levels", [])
        
        if not support_levels and not resistance_levels:
            return {"structure": "undefined"}
        
        nearest_support = max(support_levels) if support_levels else 0
        nearest_resistance = min(resistance_levels) if resistance_levels else float('inf')
        
        if len(support_levels) > len(resistance_levels):
            structure = "accumulation"
        elif len(resistance_levels) > len(support_levels):
            structure = "distribution"
        else:
            structure = "consolidation"
        
        return {
            "structure": structure,
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_strength": len(support_levels),
            "resistance_strength": len(resistance_levels)
        }

    def generate_trading_signals(self, market_position: Dict) -> Dict:
        structure = market_position.get("structure", "undefined")
        
        signals = {
            "direction": "neutral",
            "strength": "weak",
            "entry_zone": None,
            "targets": [],
            "stop_loss": None
        }
        
        if structure == "accumulation":
            signals["direction"] = "bullish"
            signals["strength"] = "strong"
            signals["entry_zone"] = market_position.get("nearest_support")
            
        elif structure == "distribution":
            signals["direction"] = "bearish"
            signals["strength"] = "strong"
            signals["entry_zone"] = market_position.get("nearest_resistance")
            
        elif structure == "consolidation":
            signals["direction"] = "range"
            signals["strength"] = "medium"
        
        return signals