import re
import json
from typing import Dict, List, Optional

class ResponseParser:
    def __init__(self):
        self.price_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        self.level_pattern = r'(?:уровень|level|target|цель|поддержка|сопротивление|support|resistance)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        
    def parse_elliott_response(self, claude_response: str) -> Dict:
        extracted_data = {
            "analysis_type": "elliott_wave",
            "wave_structure": self.extract_wave_structure(claude_response),
            "entry_zone": self.extract_entry_zone(claude_response),
            "targets": self.extract_targets(claude_response),
            "stop_loss": self.extract_stop_loss(claude_response),
            "fibonacci_levels": self.extract_fibonacci_levels(claude_response),
            "current_wave": self.extract_current_wave(claude_response),
            "comment": self.extract_comment(claude_response),
            "raw_analysis": claude_response
        }
        return extracted_data

    def parse_volume_response(self, claude_response: str) -> Dict:
        extracted_data = {
            "analysis_type": "volume_cluster",
            "poc": self.extract_poc(claude_response),
            "vah_val": self.extract_vah_val(claude_response),
            "entry_zone": self.extract_entry_zone(claude_response),
            "targets": self.extract_targets(claude_response),
            "stop_loss": self.extract_stop_loss(claude_response),
            "volume_levels": self.extract_volume_levels(claude_response),
            "market_structure": self.extract_market_structure(claude_response),
            "comment": self.extract_comment(claude_response),
            "raw_analysis": claude_response
        }
        return extracted_data

    def parse_smc_response(self, claude_response: str) -> Dict:
        extracted_data = {
            "analysis_type": "smart_money_concept",
            "order_blocks": self.extract_order_blocks(claude_response),
            "fair_value_gaps": self.extract_fvg(claude_response),
            "liquidity_zones": self.extract_liquidity_zones(claude_response),
            "entry_zone": self.extract_entry_zone(claude_response),
            "targets": self.extract_targets(claude_response),
            "stop_loss": self.extract_stop_loss(claude_response),
            "market_bias": self.extract_market_bias(claude_response),
            "comment": self.extract_comment(claude_response),
            "raw_analysis": claude_response
        }
        return extracted_data

    def extract_wave_structure(self, text: str) -> Dict:
        wave_structure = {}
        
        wave_patterns = [
            r'волна\s*(\d+)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'wave\s*(\d+)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(\d+)\s*волна[:\s]*(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in wave_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                wave_num = match[0]
                price = self.clean_price(match[1])
                if price:
                    wave_structure[f"wave_{wave_num}"] = price
        
        return wave_structure

    def extract_entry_zone(self, text: str) -> Optional[float]:
        patterns = [
            r'(?:вход|entry|buy|покупка)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:зона входа|entry zone)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_price(match.group(1))
        return None

    def extract_targets(self, text: str) -> List[float]:
        targets = []
        patterns = [
            r'(?:цель|target|tp)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:цели|targets)[:\s]*([^.]+)',
            r'(?:take profit|тейк профит)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                
                prices = re.findall(self.price_pattern, str(match))
                for price_str in prices:
                    price = self.clean_price(price_str)
                    if price and price not in targets:
                        targets.append(price)
        
        return sorted(targets)[:3]

    def extract_stop_loss(self, text: str) -> Optional[float]:
        patterns = [
            r'(?:стоп|stop|sl|stop loss)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:стоп лосс|stop-loss)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_price(match.group(1))
        return None

    def extract_fibonacci_levels(self, text: str) -> Dict:
        fib_levels = {}
        patterns = [
            r'(\d+(?:\.\d+)?%?)\s*фибо?[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'fib[:\s]*(\d+(?:\.\d+)?%?)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(\d+\.\d+)\s*уровень[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                level = match[0].replace('%', '')
                price = self.clean_price(match[1])
                if price:
                    fib_levels[f"fib_{level}"] = price
        
        return fib_levels

    def extract_current_wave(self, text: str) -> int:
        patterns = [
            r'текущая волна[:\s]*(\d+)',
            r'current wave[:\s]*(\d+)',
            r'находимся в[:\s]*(\d+)[:\s]*волне'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 1

    def extract_poc(self, text: str) -> Optional[float]:
        patterns = [
            r'(?:poc|point of control)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:точка контроля|пок)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_price(match.group(1))
        return None

    def extract_vah_val(self, text: str) -> Dict:
        vah_val = {}
        
        vah_patterns = [
            r'(?:vah|value area high)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:верх зоны стоимости)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        val_patterns = [
            r'(?:val|value area low)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:низ зоны стоимости)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in vah_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vah_val['vah'] = self.clean_price(match.group(1))
                break
        
        for pattern in val_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vah_val['val'] = self.clean_price(match.group(1))
                break
        
        return vah_val

    def extract_order_blocks(self, text: str) -> List[Dict]:
        order_blocks = []
        patterns = [
            r'(?:bullish|бычий)\s*(?:order block|ордер блок)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:bearish|медвежий)\s*(?:order block|ордер блок)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                price = self.clean_price(match)
                if price:
                    ob_type = "bullish" if "bullish" in pattern or "бычий" in pattern else "bearish"
                    order_blocks.append({
                        "level": price,
                        "type": ob_type
                    })
        
        return order_blocks

    def extract_fvg(self, text: str) -> List[Dict]:
        fvgs = []
        patterns = [
            r'(?:fvg|fair value gap|гэп)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)[:\s]*-[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                start_price = self.clean_price(match[0])
                end_price = self.clean_price(match[1])
                if start_price and end_price:
                    fvgs.append({
                        "start": min(start_price, end_price),
                        "end": max(start_price, end_price),
                        "status": "unfilled"
                    })
        
        return fvgs

    def extract_liquidity_zones(self, text: str) -> List[Dict]:
        zones = []
        patterns = [
            r'(?:liquidity|ликвидность)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:зона ликвидности)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                price = self.clean_price(match)
                if price:
                    zones.append({
                        "level": price,
                        "type": "liquidity"
                    })
        
        return zones

    def extract_market_structure(self, text: str) -> str:
        patterns = [
            r'(?:accumulation|аккумуляция)',
            r'(?:distribution|дистрибуция)',
            r'(?:consolidation|консолидация)',
            r'(?:trending|тренд)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return pattern.split('|')[0]
        
        return "undefined"

    def extract_market_bias(self, text: str) -> str:
        bullish_patterns = [
            r'(?:bullish|бычий|рост|вверх|покупка)',
            r'(?:long|лонг)'
        ]
        
        bearish_patterns = [
            r'(?:bearish|медвежий|падение|вниз|продажа)',
            r'(?:short|шорт)'
        ]
        
        for pattern in bullish_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "bullish"
        
        for pattern in bearish_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "bearish"
        
        return "neutral"

    def extract_volume_levels(self, text: str) -> List[float]:
        levels = []
        patterns = [
            r'(?:high volume|высокий объем)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)',
            r'(?:объемный уровень)[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                price = self.clean_price(match)
                if price and price not in levels:
                    levels.append(price)
        
        return sorted(levels)

    def extract_comment(self, text: str) -> str:
        lines = text.split('\n')
        comment_lines = []
        
        for line in lines:
            line = line.strip()
            if (not re.search(self.price_pattern, line) and 
                len(line) > 20 and 
                not line.startswith('•') and
                not line.startswith('-')):
                comment_lines.append(line)
        
        return ' '.join(comment_lines[:3])

    def clean_price(self, price_str: str) -> Optional[float]:
        if not price_str:
            return None
        
        try:
            cleaned = price_str.replace(',', '').replace('$', '').strip()
            price = float(cleaned)
            
            if 1 <= price <= 1000000:
                return price
        except (ValueError, TypeError):
            pass
        
        return None