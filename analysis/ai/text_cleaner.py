import re
from typing import Dict, Any

class TextCleaner:
    def __init__(self):
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"   
            "\U0001F300-\U0001F5FF"   
            "\U0001F680-\U0001F6FF"   
            "\U0001F1E0-\U0001F1FF"  
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        self.markdown_patterns = {
            r'\*\*(.*?)\*\*': r'\1',   
            r'\*(.*?)\*': r'\1',       
            r'#{1,6}\s*': '',          
            r'`(.*?)`': r'\1',        
            r'\[(.*?)\]\(.*?\)': r'\1',  
        }

    def clean_text(self, text: str) -> str:
        cleaned = text
        
        cleaned = self.emoji_pattern.sub('', cleaned)
        
        for pattern, replacement in self.markdown_patterns.items():
            cleaned = re.sub(pattern, replacement, cleaned)
        
        cleaned = re.sub(r'[-=]{3,}', '', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('*') and line != '---':
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def structure_elliott_analysis(self, raw_text: str) -> Dict[str, Any]:
        cleaned_text = self.clean_text(raw_text)
        
        structured = {
            "method": "Elliott Wave Analysis",
            "summary": self.extract_summary(cleaned_text),
            "wave_structure": self.extract_wave_structure_text(cleaned_text),
            "current_position": self.extract_current_position(cleaned_text),
            "trading_scenarios": self.extract_trading_scenarios(cleaned_text),
            "key_levels": self.extract_key_levels_text(cleaned_text),
            "risk_management": self.extract_risk_management(cleaned_text),
            "clean_text": cleaned_text
        }
        
        return structured

    def structure_volume_analysis(self, raw_text: str) -> Dict[str, Any]:
        cleaned_text = self.clean_text(raw_text)
        
        structured = {
            "method": "Volume Cluster Analysis",
            "summary": self.extract_summary(cleaned_text),
            "volume_profile": self.extract_volume_profile_text(cleaned_text),
            "key_levels": self.extract_key_levels_text(cleaned_text),
            "market_structure": self.extract_market_structure_text(cleaned_text),
            "trading_signals": self.extract_trading_signals_text(cleaned_text),
            "clean_text": cleaned_text
        }
        
        return structured

    def structure_smc_analysis(self, raw_text: str) -> Dict[str, Any]:
        cleaned_text = self.clean_text(raw_text)
        
        structured = {
            "method": "Smart Money Concept Analysis",
            "summary": self.extract_summary(cleaned_text),
            "order_blocks": self.extract_order_blocks_text(cleaned_text),
            "fair_value_gaps": self.extract_fvg_text(cleaned_text),
            "liquidity_zones": self.extract_liquidity_text(cleaned_text),
            "market_bias": self.extract_market_bias_text(cleaned_text),
            "trading_plan": self.extract_trading_plan(cleaned_text),
            "clean_text": cleaned_text
        }
        
        return structured

    def extract_summary(self, text: str) -> str:
        lines = text.split('\n')
        summary_lines = []
        
        for i, line in enumerate(lines[:10]):
            if ('текущая цена' in line.lower() or 'current price' in line.lower() or 
                'анализ' in line.lower() or 'analysis' in line.lower()):
                summary_lines.append(line)
        
        return ' '.join(summary_lines) if summary_lines else "Анализ выполнен"

    def extract_wave_structure_text(self, text: str) -> str:
        sections = []
        lines = text.split('\n')
        
        in_wave_section = False
        for line in lines:
            if ('волновая структура' in line.lower() or 
                'wave structure' in line.lower() or
                'волна' in line.lower()):
                in_wave_section = True
                sections.append(line)
            elif in_wave_section and line.strip():
                if ('сценарий' in line.lower() or 'scenario' in line.lower() or
                    'ключевые уровни' in line.lower() or 'key levels' in line.lower()):
                    break
                sections.append(line)
        
        return '\n'.join(sections) if sections else "Волновая структура не определена"

    def extract_current_position(self, text: str) -> str:
        lines = text.split('\n')
        position_lines = []
        
        for line in lines:
            if ('текущее положение' in line.lower() or 'current position' in line.lower() or
                'статус' in line.lower() or 'status' in line.lower()):
                position_lines.append(line)
                
        return '\n'.join(position_lines) if position_lines else "Позиция не определена"

    def extract_trading_scenarios(self, text: str) -> str:
        sections = []
        lines = text.split('\n')
        
        in_scenario_section = False
        for line in lines:
            if ('сценарий' in line.lower() or 'scenario' in line.lower() or
                'торговый план' in line.lower() or 'trading plan' in line.lower()):
                in_scenario_section = True
                sections.append(line)
            elif in_scenario_section and line.strip():
                if ('ключевые уровни' in line.lower() or 'key levels' in line.lower() or
                    'риск' in line.lower() or 'risk' in line.lower()):
                    break
                sections.append(line)
        
        return '\n'.join(sections) if sections else "Торговые сценарии не определены"

    def extract_key_levels_text(self, text: str) -> str:
        sections = []
        lines = text.split('\n')
        
        in_levels_section = False
        for line in lines:
            if ('ключевые уровни' in line.lower() or 'key levels' in line.lower() or
                'поддержка' in line.lower() or 'support' in line.lower() or
                'сопротивление' in line.lower() or 'resistance' in line.lower()):
                in_levels_section = True
                sections.append(line)
            elif in_levels_section and line.strip():
                if ('риск' in line.lower() or 'risk' in line.lower() or
                    'рекомендации' in line.lower() or 'recommendations' in line.lower()):
                    break
                sections.append(line)
        
        return '\n'.join(sections) if sections else "Ключевые уровни не определены"

    def extract_risk_management(self, text: str) -> str:
        sections = []
        lines = text.split('\n')
        
        in_risk_section = False
        for line in lines:
            if ('риск' in line.lower() or 'risk' in line.lower() or
                'менеджмент' in line.lower() or 'management' in line.lower() or
                'рекомендации' in line.lower() or 'recommendations' in line.lower()):
                in_risk_section = True
                sections.append(line)
            elif in_risk_section and line.strip():
                sections.append(line)
        
        return '\n'.join(sections) if sections else "Рекомендации по риск-менеджменту отсутствуют"

    def extract_volume_profile_text(self, text: str) -> str:
        lines = text.split('\n')
        volume_lines = []
        
        for line in lines:
            if ('poc' in line.lower() or 'vah' in line.lower() or 'val' in line.lower() or
                'volume profile' in line.lower() or 'объем' in line.lower()):
                volume_lines.append(line)
        
        return '\n'.join(volume_lines) if volume_lines else "Volume Profile не определен"

    def extract_market_structure_text(self, text: str) -> str:
        lines = text.split('\n')
        structure_lines = []
        
        for line in lines:
            if ('структура рынка' in line.lower() or 'market structure' in line.lower() or
                'аккумуляция' in line.lower() or 'accumulation' in line.lower() or
                'дистрибуция' in line.lower() or 'distribution' in line.lower()):
                structure_lines.append(line)
        
        return '\n'.join(structure_lines) if structure_lines else "Структура рынка не определена"

    def extract_trading_signals_text(self, text: str) -> str:
        lines = text.split('\n')
        signals_lines = []
        
        for line in lines:
            if ('сигнал' in line.lower() or 'signal' in line.lower() or
                'вход' in line.lower() or 'entry' in line.lower() or
                'покупка' in line.lower() or 'buy' in line.lower()):
                signals_lines.append(line)
        
        return '\n'.join(signals_lines) if signals_lines else "Торговые сигналы не определены"

    def extract_order_blocks_text(self, text: str) -> str:
        lines = text.split('\n')
        ob_lines = []
        
        for line in lines:
            if ('order block' in line.lower() or 'ордер блок' in line.lower() or
                'ob' in line.lower()):
                ob_lines.append(line)
        
        return '\n'.join(ob_lines) if ob_lines else "Order Blocks не найдены"

    def extract_fvg_text(self, text: str) -> str:
        lines = text.split('\n')
        fvg_lines = []
        
        for line in lines:
            if ('fair value gap' in line.lower() or 'fvg' in line.lower() or
                'гэп' in line.lower() or 'gap' in line.lower()):
                fvg_lines.append(line)
        
        return '\n'.join(fvg_lines) if fvg_lines else "Fair Value Gaps не найдены"

    def extract_liquidity_text(self, text: str) -> str:
        lines = text.split('\n')
        liq_lines = []
        
        for line in lines:
            if ('liquidity' in line.lower() or 'ликвидность' in line.lower() or
                'зона ликвидности' in line.lower()):
                liq_lines.append(line)
        
        return '\n'.join(liq_lines) if liq_lines else "Зоны ликвидности не определены"

    def extract_market_bias_text(self, text: str) -> str:
        lines = text.split('\n')
        bias_lines = []
        
        for line in lines:
            if ('bias' in line.lower() or 'настрой' in line.lower() or
                'направление' in line.lower() or 'direction' in line.lower() or
                'bullish' in line.lower() or 'bearish' in line.lower() or
                'бычий' in line.lower() or 'медвежий' in line.lower()):
                bias_lines.append(line)
        
        return '\n'.join(bias_lines) if bias_lines else "Направление рынка не определено"

    def extract_trading_plan(self, text: str) -> str:
        lines = text.split('\n')
        plan_lines = []
        
        for line in lines:
            if ('план' in line.lower() or 'plan' in line.lower() or
                'стратегия' in line.lower() or 'strategy' in line.lower() or
                'рекомендации' in line.lower() or 'recommendations' in line.lower()):
                plan_lines.append(line)
        
        return '\n'.join(plan_lines) if plan_lines else "Торговый план не определен"