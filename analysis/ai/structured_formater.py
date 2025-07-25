import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class StructuredFormatter:
    def __init__(self):
        self.price_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        
    def format_smc_analysis(self, text: str, symbol: str, current_price: float) -> Dict[str, Any]:
        return {
            "analysis_info": {
                "method": "Smart Money Concept",
                "symbol": symbol,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "timeframe": self.extract_timeframe(text)
            },
            "order_blocks": self.extract_order_blocks_structured(text),
            "fair_value_gaps": self.extract_fvg_structured(text),
            "liquidity_zones": self.extract_liquidity_zones_structured(text),
            "market_bias": self.extract_market_bias_structured(text),
            "trading_plan": self.extract_trading_plan_structured(text),
            "key_levels": self.extract_key_levels_structured(text),
            "summary": self.create_summary(text, current_price)
        }
    
    def format_elliott_analysis(self, text: str, symbol: str, current_price: float) -> Dict[str, Any]:
        return {
            "analysis_info": {
                "method": "Elliott Wave Analysis",
                "symbol": symbol,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "timeframe": self.extract_timeframe(text)
            },
            "wave_structure": self.extract_waves_structured(text),
            "current_wave": self.extract_current_wave_info(text),
            "fibonacci_levels": self.extract_fibonacci_structured(text),
            "trading_scenarios": self.extract_scenarios_structured(text),
            "key_levels": self.extract_key_levels_structured(text),
            "risk_management": self.extract_risk_management_structured(text),
            "summary": self.create_summary(text, current_price)
        }
    
    def format_volume_analysis(self, text: str, symbol: str, current_price: float) -> Dict[str, Any]:
        return {
            "analysis_info": {
                "method": "Volume Cluster Analysis",
                "symbol": symbol,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "timeframe": self.extract_timeframe(text)
            },
            "volume_profile": self.extract_volume_profile_structured(text),
            "key_levels": self.extract_key_levels_structured(text),
            "market_structure": self.extract_market_structure_structured(text),
            "trading_signals": self.extract_trading_signals_structured(text),
            "summary": self.create_summary(text, current_price)
        }

    def extract_order_blocks_structured(self, text: str) -> Dict[str, Any]:
        above_price = []
        below_price = []
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'выше цены' in line.lower() or 'above price' in line.lower():
                current_section = 'above'
                continue
            elif 'ниже цены' in line.lower() or 'below price' in line.lower():
                current_section = 'below'
                continue
            
            if current_section and '-' in line and any(c.isdigit() for c in line):
                ob_data = self.parse_order_block_line(line)
                if ob_data:
                    if current_section == 'above':
                        above_price.append(ob_data)
                    else:
                        below_price.append(ob_data)
        
        return {
            "above_price": above_price,
            "below_price": below_price,
            "total_count": len(above_price) + len(below_price),
            "strongest_resistance": self.find_strongest_level(above_price),
            "strongest_support": self.find_strongest_level(below_price)
        }

    def parse_order_block_line(self, line: str) -> Optional[Dict]:
        price_match = re.search(self.price_pattern, line)
        if not price_match:
            return None
        
        price = float(price_match.group(1).replace(',', ''))
        
        strength = "weak"
        if "сильн" in line.lower() or "strong" in line.lower():
            strength = "strong"
        elif "средн" in line.lower() or "medium" in line.lower():
            strength = "medium"
        
        block_type = "bullish"
        if "медвеж" in line.lower() or "bearish" in line.lower():
            block_type = "bearish"
        
        description = line.split('-', 1)[-1].strip() if '-' in line else ""
        
        return {
            "price": price,
            "type": block_type,
            "strength": strength,
            "description": description
        }

    def extract_fvg_structured(self, text: str) -> Dict[str, Any]:
        bullish_fvgs = []
        bearish_fvgs = []
        
        lines = text.split('\n')
        current_type = None
        
        for line in lines:
            line = line.strip()
            if 'бычьи fvg' in line.lower() or 'bullish fvg' in line.lower():
                current_type = 'bullish'
                continue
            elif 'медвежьи fvg' in line.lower() or 'bearish fvg' in line.lower():
                current_type = 'bearish'
                continue
            
            if current_type and '-' in line and any(c.isdigit() for c in line):
                fvg_data = self.parse_fvg_line(line)
                if fvg_data:
                    fvg_data['type'] = current_type
                    if current_type == 'bullish':
                        bullish_fvgs.append(fvg_data)
                    else:
                        bearish_fvgs.append(fvg_data)
        
        return {
            "bullish": bullish_fvgs,
            "bearish": bearish_fvgs,
            "total_count": len(bullish_fvgs) + len(bearish_fvgs),
            "nearest_fvg": self.find_nearest_fvg(bullish_fvgs + bearish_fvgs)
        }

    def parse_fvg_line(self, line: str) -> Optional[Dict]:
        prices = re.findall(self.price_pattern, line)
        if len(prices) < 2:
            return None
        
        start_price = float(prices[0].replace(',', ''))
        end_price = float(prices[1].replace(',', ''))
        
        status = "unfilled"
        if "заполнен" in line.lower() or "filled" in line.lower():
            status = "filled"
        elif "частично" in line.lower() or "partial" in line.lower():
            status = "partially_filled"
        
        size = "small"
        if "крупный" in line.lower() or "large" in line.lower():
            size = "large"
        elif "средний" in line.lower() or "medium" in line.lower():
            size = "medium"
        
        description = line.split('(', 1)[-1].split(')', 1)[0] if '(' in line else ""
        
        return {
            "start_price": min(start_price, end_price),
            "end_price": max(start_price, end_price),
            "size": end_price - start_price,
            "status": status,
            "importance": size,
            "description": description
        }

    def extract_liquidity_zones_structured(self, text: str) -> List[Dict]:
        zones = []
        lines = text.split('\n')
        
        for line in lines:
            if '-' in line and any(c.isdigit() for c in line) and ('зона' in line.lower() or 'zone' in line.lower()):
                zone_data = self.parse_liquidity_zone(line)
                if zone_data:
                    zones.append(zone_data)
        
        return zones

    def parse_liquidity_zone(self, line: str) -> Optional[Dict]:
        prices = re.findall(self.price_pattern, line)
        if not prices:
            return None
        
        if len(prices) >= 2:
            start_price = float(prices[0].replace(',', ''))
            end_price = float(prices[1].replace(',', ''))
        else:
            price = float(prices[0].replace(',', ''))
            start_price = price - 500
            end_price = price + 500
        
        zone_type = "mixed"
        if "бычь" in line.lower() or "bullish" in line.lower():
            zone_type = "bullish"
        elif "медвеж" in line.lower() or "bearish" in line.lower():
            zone_type = "bearish"
        
        importance = "medium"
        if "высокой" in line.lower() or "high" in line.lower():
            importance = "high"
        elif "низкой" in line.lower() or "low" in line.lower():
            importance = "low"
        
        description = line.split('-', 1)[-1].strip() if '-' in line else ""
        
        return {
            "start_price": min(start_price, end_price),
            "end_price": max(start_price, end_price),
            "type": zone_type,
            "importance": importance,
            "description": description
        }

    def extract_market_bias_structured(self, text: str) -> Dict[str, Any]:
        bias_section = ""
        lines = text.split('\n')
        in_bias_section = False
        
        for line in lines:
            if 'направление рынка' in line.lower() or 'market bias' in line.lower():
                in_bias_section = True
                continue
            elif in_bias_section:
                if line.strip() and not line.startswith('5.'):
                    bias_section += line + "\n"
                elif line.startswith('5.'):
                    break
        
        current_bias = "neutral"
        if "бычий" in bias_section.lower() or "bullish" in bias_section.lower():
            current_bias = "bullish"
        elif "медвежий" in bias_section.lower() or "bearish" in bias_section.lower():
            current_bias = "bearish"
        
        strength = "weak"
        if "сильн" in bias_section.lower() or "strong" in bias_section.lower():
            strength = "strong"
        elif "умерен" in bias_section.lower() or "moderate" in bias_section.lower():
            strength = "moderate"
        
        return {
            "current_bias": current_bias,
            "strength": strength,
            "timeframe": "short-term",
            "confidence": self.extract_confidence(bias_section),
            "description": bias_section.strip()
        }

    def extract_trading_plan_structured(self, text: str) -> Dict[str, Any]:
        bullish_scenario = None
        bearish_scenario = None
        
        lines = text.split('\n')
        current_scenario = None
        current_data = {}
        
        for line in lines:
            line = line.strip()
            if 'бычий сценарий' in line.lower() or 'bullish scenario' in line.lower():
                if current_scenario == 'bearish' and current_data:
                    bearish_scenario = current_data.copy()
                current_scenario = 'bullish'
                current_data = {"type": "bullish"}
            elif 'медвежий сценарий' in line.lower() or 'bearish scenario' in line.lower():
                if current_scenario == 'bullish' and current_data:
                    bullish_scenario = current_data.copy()
                current_scenario = 'bearish'
                current_data = {"type": "bearish"}
            elif current_scenario:
                if 'вход' in line.lower() or 'entry' in line.lower():
                    current_data['entry'] = self.extract_price_from_line(line)
                elif 'стоп' in line.lower() or 'stop' in line.lower():
                    current_data['stop_loss'] = self.extract_price_from_line(line)
                elif 'цел' in line.lower() or 'target' in line.lower():
                    targets = self.extract_targets_from_line(line)
                    if targets:
                        current_data['targets'] = targets
        
        if current_scenario == 'bearish' and current_data:
            bearish_scenario = current_data
        elif current_scenario == 'bullish' and current_data:
            bullish_scenario = current_data
        
        return {
            "bullish_scenario": bullish_scenario,
            "bearish_scenario": bearish_scenario,
            "recommended_approach": self.extract_recommended_approach(text)
        }

    def extract_key_levels_structured(self, text: str) -> Dict[str, Any]:
        support_levels = []
        resistance_levels = []
        
        lines = text.split('\n')
        
        for line in lines:
            if 'поддержка' in line.lower() or 'support' in line.lower():
                levels = self.extract_levels_from_line(line)
                support_levels.extend(levels)
            elif 'сопротивление' in line.lower() or 'resistance' in line.lower():
                levels = self.extract_levels_from_line(line)
                resistance_levels.extend(levels)
        
        return {
            "support": sorted(support_levels, reverse=True),
            "resistance": sorted(resistance_levels),
            "key_support": support_levels[0] if support_levels else None,
            "key_resistance": resistance_levels[0] if resistance_levels else None
        }

    def extract_price_from_line(self, line: str) -> Optional[float]:
        prices = re.findall(self.price_pattern, line)
        return float(prices[0].replace(',', '')) if prices else None

    def extract_targets_from_line(self, line: str) -> List[float]:
        prices = re.findall(self.price_pattern, line)
        return [float(p.replace(',', '')) for p in prices]

    def extract_levels_from_line(self, line: str) -> List[float]:
        prices = re.findall(self.price_pattern, line)
        return [float(p.replace(',', '')) for p in prices]

    def find_strongest_level(self, levels: List[Dict]) -> Optional[Dict]:
        if not levels:
            return None
        
        strong_levels = [l for l in levels if l.get('strength') == 'strong']
        if strong_levels:
            return strong_levels[0]
        
        medium_levels = [l for l in levels if l.get('strength') == 'medium']
        if medium_levels:
            return medium_levels[0]
        
        return levels[0] if levels else None

    def find_nearest_fvg(self, fvgs: List[Dict]) -> Optional[Dict]:
        return fvgs[0] if fvgs else None

    def extract_confidence(self, text: str) -> str:
        if 'высокая' in text.lower() or 'high' in text.lower():
            return "high"
        elif 'низкая' in text.lower() or 'low' in text.lower():
            return "low"
        return "medium"

    def extract_recommended_approach(self, text: str) -> str:
        if 'ожидать' in text.lower() or 'wait' in text.lower():
            return "wait_for_confirmation"
        elif 'агрессивн' in text.lower() or 'aggressive' in text.lower():
            return "aggressive"
        return "conservative"

    def extract_timeframe(self, text: str) -> str:
        if '1h' in text or '1H' in text:
            return "1h"
        elif '4h' in text or '4H' in text:
            return "4h"
        elif '1d' in text or '1D' in text:
            return "1d"
        return "4h"

    def create_summary(self, text: str, current_price: float) -> Dict[str, str]:
        return {
            "overall_sentiment": self.extract_overall_sentiment(text),
            "key_insight": self.extract_key_insight(text),
            "recommended_action": self.extract_recommended_action(text),
            "risk_level": self.extract_risk_level(text)
        }

    def extract_overall_sentiment(self, text: str) -> str:
        bullish_words = ['рост', 'покупк', 'bullish', 'buy', 'long']
        bearish_words = ['падение', 'продаж', 'bearish', 'sell', 'short']
        
        bullish_count = sum(1 for word in bullish_words if word in text.lower())
        bearish_count = sum(1 for word in bearish_words if word in text.lower())
        
        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        return "neutral"

    def extract_key_insight(self, text: str) -> str:
        lines = text.split('\n')
        for line in lines:
            if ('ключев' in line.lower() or 'key' in line.lower() or 
                'важно' in line.lower() or 'important' in line.lower()):
                return line.strip()
        return "Анализ завершен"

    def extract_recommended_action(self, text: str) -> str:
        if 'покупка' in text.lower() or 'buy' in text.lower():
            return "buy"
        elif 'продажа' in text.lower() or 'sell' in text.lower():
            return "sell"
        elif 'ожидать' in text.lower() or 'wait' in text.lower():
            return "wait"
        return "monitor"

    def extract_risk_level(self, text: str) -> str:
        if 'высокий риск' in text.lower() or 'high risk' in text.lower():
            return "high"
        elif 'низкий риск' in text.lower() or 'low risk' in text.lower():
            return "low"
        return "medium"

    # Заглушки для других методов
    def extract_waves_structured(self, text: str) -> Dict:
        return {"waves": [], "current_wave": 1}
    
    def extract_current_wave_info(self, text: str) -> Dict:
        return {"wave_number": 1, "wave_type": "impulse"}
    
    def extract_fibonacci_structured(self, text: str) -> Dict:
        return {"levels": {}}
    
    def extract_scenarios_structured(self, text: str) -> Dict:
        return {"primary": {}, "alternative": {}}
    
    def extract_risk_management_structured(self, text: str) -> Dict:
        return {"position_size": "2-3%", "risk_reward": "1:3"}
    
    def extract_volume_profile_structured(self, text: str) -> Dict:
        return {"poc": None, "vah": None, "val": None}
    
    def extract_market_structure_structured(self, text: str) -> Dict:
        return {"structure": "consolidation"}
    
    def extract_trading_signals_structured(self, text: str) -> List:
        return []