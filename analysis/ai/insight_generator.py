import re
from typing import Dict, List, Optional
from datetime import datetime

class InsightGenerator:
    def __init__(self):
        self.price_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2,8})?)'
        
        self.elliott_templates = {
            'ru': [
                "После завершения волны {prev_wave} {symbol} показывает классический старт {current_wave} волны. При сохранении импульса и пробое ${key_level} вероятно продолжение тренда {direction}. На {timeframe} стоит ждать либо вход от отката, либо пробой с ретестом. Волна {current_wave} — обычно самая сильная, при этом рыночные объёмы уже подтверждают интерес.",
                "Структура волн указывает на завершение коррекции в области ${support_level}. При пробое выше ${resistance_level} откроется путь к цели ${target_level} в рамках волны {current_wave}. Фибо-уровни поддерживают сценарий роста.",
                "Формируется классическая коррективная структура волны {current_wave}. Ключевой уровень поддержки ${support_level}, при его удержании возможен отскок к ${target_level}. Пробой ниже может привести к тестированию ${deeper_support}.",
                "Волновой анализ показывает потенциал для импульсного движения. Текущая позиция в волне {current_wave} даёт возможность входа в направлении основного тренда. Целевая зона ${target_level}-${target_level_2}."
            ],
            'en': [
                "After completing wave {prev_wave}, {symbol} shows a classic start of wave {current_wave}. With momentum continuation and break above ${key_level}, trend continuation {direction} is likely. On {timeframe}, expect either pullback entry or breakout with retest. Wave {current_wave} is usually the strongest, with market volumes already confirming interest.",
                "Wave structure indicates correction completion around ${support_level}. A break above ${resistance_level} opens path to target ${target_level} within wave {current_wave}. Fibonacci levels support the bullish scenario.",
                "Classic corrective structure of wave {current_wave} is forming. Key support level ${support_level}, holding it may lead to bounce to ${target_level}. Break below could lead to testing ${deeper_support}.",
                "Wave analysis shows potential for impulsive movement. Current position in wave {current_wave} provides entry opportunity in main trend direction. Target zone ${target_level}-${target_level_2}."
            ],
            'uz': [
                "{prev_wave} to'lqin tugagandan so'ng, {symbol} {current_wave} to'lqinning klassik boshlanishini ko'rsatmoqda. Impuls saqlanib, ${key_level} dan yuqoriga chiqib ketsa, {direction} trend davom etishi mumkin. {timeframe} da orqaga tortish yoki sinish bilan qayta test kutish kerak. {current_wave} to'lqin odatda eng kuchli bo'lib, bozor hajmlari allaqachon qiziqishni tasdiqlaydi.",
                "To'lqin tuzilishi ${support_level} atrofida tuzatish tugaganini ko'rsatadi. ${resistance_level} dan yuqoriga chiqish {current_wave} to'lqin doirasida ${target_level} maqsadga yo'l ochadi. Fibonacci darajalari ko'tarilish stsenariyni qo'llab-quvvatlaydi.",
                "{current_wave} to'lqinning klassik tuzatuvchi tuzilishi shakllanmoqda. Asosiy qo'llab-quvvatlash darajasi ${support_level}, uni ushlab turish ${target_level} ga sakrashga olib kelishi mumkin. Pastga sinish ${deeper_support} ni sinashga olib kelishi mumkin.",
                "To'lqin tahlili impulsiv harakat potentsialini ko'rsatadi. {current_wave} to'lqindagi joriy pozitsiya asosiy trend yo'nalishida kirish imkoniyatini beradi. Maqsad zonasi ${target_level}-${target_level_2}."
            ]
        }
        
        self.volume_templates = {
            'ru': [
                "Рынок демонстрирует признаки {market_condition} после недавнего {recent_move}. Поддержка в области VAL удержалась, и цена стремится вернуться к POC. Если цена закрепится выше ${poc_level}, это может открыть путь к следующему уровню сопротивления около ${resistance_level}.",
                "Объёмный профиль показывает накопление в зоне ${accumulation_zone}. POC на уровне ${poc_level} выступает магнитом для цены. При пробое VAH ${vah_level} возможно продолжение роста к ${next_resistance}.",
                "Высокие объёмы в области ${high_volume_area} подтверждают интерес участников. Цена тестирует ключевую зону ${key_zone}, удержание которой откроет дорогу к ${target_zone}. Объёмы поддерживают {bias_direction} сценарий.",
                "Volume Profile указывает на дисбаланс в области ${imbalance_zone}. При возврате цены в эту зону возможна реакция. Текущая структура поддерживает движение к ${target_level} при объёмном подтверждении."
            ],
            'en': [
                "Market shows signs of {market_condition} after recent {recent_move}. Support in VAL area held, and price aims to return to POC. If price consolidates above ${poc_level}, it may open path to next resistance level around ${resistance_level}.",
                "Volume Profile shows accumulation in ${accumulation_zone} zone. POC at ${poc_level} acts as price magnet. Breaking VAH ${vah_level} may continue rally to ${next_resistance}.",
                "High volumes in ${high_volume_area} area confirm participant interest. Price tests key zone ${key_zone}, holding it will open path to ${target_zone}. Volumes support {bias_direction} scenario.",
                "Volume Profile indicates imbalance in ${imbalance_zone} area. Price return to this zone may trigger reaction. Current structure supports move to ${target_level} with volume confirmation."
            ],
            'uz': [
                "Bozor yaqinda bo'lgan {recent_move} dan keyin {market_condition} belgilarini ko'rsatmoqda. VAL hududidagi qo'llab-quvvatlash saqlanib qoldi va narx POC ga qaytishga intilmoqda. Agar narx ${poc_level} dan yuqorida mustahkam bo'lsa, bu ${resistance_level} atrofidagi keyingi qarshilik darajasiga yo'l ochishi mumkin.",
                "Volume Profile ${accumulation_zone} zonasida to'planishni ko'rsatadi. ${poc_level} darajasidagi POC narx uchun magnit vazifasini bajaradi. VAH ${vah_level} ni sindirish ${next_resistance} ga qadar ko'tarilishni davom ettirishi mumkin.",
                "${high_volume_area} hududidagi yuqori hajmlar ishtirokchilar qiziqishini tasdiqlaydi. Narx ${key_zone} asosiy zonasini sinaydi, uni ushlab turish ${target_zone} ga yo'l ochadi. Hajmlar {bias_direction} stsenariyni qo'llab-quvvatlaydi.",
                "Volume Profile ${imbalance_zone} hududida nomutanosiblikni ko'rsatadi. Narxning bu zonaga qaytishi reaktsiyani keltirib chiqarishi mumkin. Joriy tuzilish hajm tasdiqlash bilan ${target_level} ga harakatni qo'llab-quvvatlaydi."
            ]
        }
        
        self.smc_templates = {
            'ru': [
                "Рынок демонстрирует признаки возможного разворота после захвата ликвидности в области ${liquidity_zone}. Если цена закрепится выше ${confirmation_level}, это может подтвердить {bias} сценарий с целью ${target_level}. Однако пробой ниже ${invalidation_level} может привести к дальнейшему {opposite_direction}.",
                "Order Block в зоне ${ob_level} показывает {ob_type} интерес институционалов. При подходе к этому уровню возможна реакция. FVG ${fvg_start}-${fvg_end} остаётся незакрытым и может выступать целью.",
                "Smart Money активность указывает на {market_bias} настрой. Break of Structure подтверждён выше ${bos_level}, что открывает путь к ликвидности в области ${liquidity_target}. Ключевой уровень защиты ${stop_level}.",
                "Образовался Quality Order Block на ${ob_level}, совпадающий с уровнем ликвидности. При тестировании этой зоны ожидается {expected_reaction}. Цель движения ${target_level}, стоп ниже ${stop_level}."
            ],
            'en': [
                "Market shows signs of possible reversal after liquidity sweep in ${liquidity_zone} area. If price consolidates above ${confirmation_level}, it may confirm {bias} scenario targeting ${target_level}. However, break below ${invalidation_level} may lead to further {opposite_direction}.",
                "Order Block in ${ob_level} zone shows {ob_type} institutional interest. Reaction possible when approaching this level. FVG ${fvg_start}-${fvg_end} remains unfilled and may act as target.",
                "Smart Money activity indicates {market_bias} bias. Break of Structure confirmed above ${bos_level}, opening path to liquidity in ${liquidity_target} area. Key protection level ${stop_level}.",
                "Quality Order Block formed at ${ob_level}, coinciding with liquidity level. Testing this zone expects {expected_reaction}. Movement target ${target_level}, stop below ${stop_level}."
            ],
            'uz': [
                "Bozor ${liquidity_zone} hududida likvidlik ushlangandan keyin mumkin bo'lgan burilish belgilarini ko'rsatmoqda. Agar narx ${confirmation_level} dan yuqorida mustahkam bo'lsa, bu ${target_level} ni maqsad qilgan {bias} stsenariyni tasdiqlashi mumkin. Biroq, ${invalidation_level} dan pastga sinish keyingi {opposite_direction} ga olib kelishi mumkin.",
                "${ob_level} zonasidagi Order Block {ob_type} institutsional qiziqishni ko'rsatadi. Bu darajaga yaqinlashganda reaktsiya mumkin. FVG ${fvg_start}-${fvg_end} to'ldirilmagan va maqsad vazifasini bajarishi mumkin.",
                "Smart Money faolligi {market_bias} moyillikni ko'rsatadi. Break of Structure ${bos_level} dan yuqorida tasdiqlandi, bu ${liquidity_target} hududidagi likvidlikka yo'l ochadi. Asosiy himoya darajasi ${stop_level}.",
                "${ob_level} da sifatli Order Block shakllandi, likvidlik darajasi bilan mos tushadi. Ushbu zonani sinash {expected_reaction} ni kutadi. Harakat maqsadi ${target_level}, stop ${stop_level} dan past."
            ]
        }

        self.direction_translations = {
            'ru': {'bullish': 'вверх', 'bearish': 'вниз', 'neutral': 'в сторону'},
            'en': {'bullish': 'up', 'bearish': 'down', 'neutral': 'sideways'},
            'uz': {'bullish': 'yuqoriga', 'bearish': 'pastga', 'neutral': 'yon tomonga'}
        }

        self.bias_translations = {
            'ru': {'bullish': 'бычий', 'bearish': 'медвежий', 'neutral': 'нейтральный'},
            'en': {'bullish': 'bullish', 'bearish': 'bearish', 'neutral': 'neutral'},
            'uz': {'bullish': 'ko\'tariluvchi', 'bearish': 'tushuvchi', 'neutral': 'neytral'}
        }

        self.condition_translations = {
            'ru': {'accumulation': 'восстановления', 'distribution': 'ослабления', 'consolidation': 'консолидации', 'trending': 'трендового движения'},
            'en': {'accumulation': 'recovery', 'distribution': 'weakening', 'consolidation': 'consolidation', 'trending': 'trending movement'},
            'uz': {'accumulation': 'tiklanish', 'distribution': 'zaiflashuv', 'consolidation': 'konsolidatsiya', 'trending': 'trend harakati'}
        }

        self.move_translations = {
            'ru': {'decline': 'снижения', 'rise': 'роста'},
            'en': {'decline': 'decline', 'rise': 'rise'},
            'uz': {'decline': 'pasayish', 'rise': 'o\'sish'}
        }

    def generate_insight(self, method: str, analysis_data: Dict, market_data: Dict, language: str = 'ru') -> str:
        symbol = market_data.get('symbol', 'BTC').replace('USDT', '')
        current_price = market_data.get('current_price', 0)
        timeframe = analysis_data.get('timeframe', '4H')
        
        if method == 'elliott_wave':
            return self._generate_elliott_insight(analysis_data, symbol, current_price, timeframe, language)
        elif method == 'volume_cluster':
            return self._generate_volume_insight(analysis_data, symbol, current_price, timeframe, language)
        elif method == 'smart_money':
            return self._generate_smc_insight(analysis_data, symbol, current_price, timeframe, language)
        else:
            return self._generate_generic_insight(analysis_data, symbol, current_price, language)

    def _generate_elliott_insight(self, data: Dict, symbol: str, current_price: float, timeframe: str, language: str) -> str:
        current_wave = data.get('current_wave', 3)
        wave_structure = data.get('wave_structure', {})
        targets = data.get('targets', [])
        fibonacci_levels = data.get('fibonacci_levels', {})
        
        direction = self._determine_trend_direction(data)
        key_levels = self._extract_key_levels(data, current_price)
        
        templates = self.elliott_templates.get(language, self.elliott_templates['ru'])
        template_idx = (current_wave - 1) % len(templates)
        template = templates[template_idx]
        
        direction_text = self.direction_translations.get(language, self.direction_translations['ru']).get(direction, direction)
        
        insight = template.format(
            symbol=symbol,
            current_wave=current_wave,
            prev_wave=current_wave - 1 if current_wave > 1 else 5,
            direction=direction_text,
            timeframe=timeframe,
            key_level=self._format_price(key_levels.get('resistance', current_price * 1.02)),
            support_level=self._format_price(key_levels.get('support', current_price * 0.98)),
            resistance_level=self._format_price(key_levels.get('resistance', current_price * 1.02)),
            target_level=self._format_price(targets[0] if targets else current_price * 1.03),
            target_level_2=self._format_price(targets[1] if len(targets) > 1 else current_price * 1.05),
            deeper_support=self._format_price(key_levels.get('support', current_price * 0.95))
        )
        
        return self._clean_insight(insight)

    def _generate_volume_insight(self, data: Dict, symbol: str, current_price: float, timeframe: str, language: str) -> str:
        volume_profile = data.get('volume_profile', {})
        poc = volume_profile.get('poc', current_price)
        vah = volume_profile.get('vah', current_price * 1.01)
        val = volume_profile.get('val', current_price * 0.99)
        
        market_structure = data.get('market_structure', {})
        key_levels = data.get('key_levels', {})
        
        market_condition = self._determine_market_condition(data)
        market_condition_text = self.condition_translations.get(language, self.condition_translations['ru']).get(market_condition, market_condition)
        
        recent_move = "decline" if current_price < poc else "rise"
        recent_move_text = self.move_translations.get(language, self.move_translations['ru']).get(recent_move, recent_move)
        
        bias_direction = "bullish" if current_price > poc else "bearish"
        bias_direction_text = self.bias_translations.get(language, self.bias_translations['ru']).get(bias_direction, bias_direction)
        
        templates = self.volume_templates.get(language, self.volume_templates['ru'])
        template_idx = 0 if abs(current_price - val) < abs(current_price - vah) else 1
        template = templates[template_idx]
        
        insight = template.format(
            symbol=symbol,
            market_condition=market_condition_text,
            recent_move=recent_move_text,
            poc_level=self._format_price(poc),
            vah_level=self._format_price(vah),
            val_level=self._format_price(val),
            resistance_level=self._format_price(vah * 1.005),
            accumulation_zone=f"{self._format_price(val)}-{self._format_price(poc)}",
            next_resistance=self._format_price(vah * 1.01),
            high_volume_area=self._format_price(poc),
            key_zone=self._format_price(poc),
            target_zone=self._format_price(vah),
            bias_direction=bias_direction_text,
            imbalance_zone=f"{self._format_price(val)}-{self._format_price(vah)}",
            target_level=self._format_price(vah if current_price < poc else vah * 1.01)
        )
        
        return self._clean_insight(insight)

    def _generate_smc_insight(self, data: Dict, symbol: str, current_price: float, timeframe: str, language: str) -> str:
        order_blocks = data.get('order_blocks', [])
        fair_value_gaps = data.get('fair_value_gaps', [])
        liquidity_zones = data.get('liquidity_zones', [])
        market_bias = data.get('market_bias', {})
        
        nearest_ob = self._find_nearest_order_block(order_blocks, current_price)
        nearest_fvg = self._find_nearest_fvg(fair_value_gaps, current_price)
        nearest_liquidity = self._find_nearest_liquidity(liquidity_zones, current_price)
        
        bias = market_bias.get('current_bias', 'neutral')
        bias_text = self.bias_translations.get(language, self.bias_translations['ru']).get(bias, bias)
        
        opposite_direction_map = {
            'ru': {'bullish': 'снижению', 'bearish': 'росту'},
            'en': {'bullish': 'decline', 'bearish': 'rise'},
            'uz': {'bullish': 'pasayishga', 'bearish': 'o\'sishga'}
        }
        opposite_direction = opposite_direction_map.get(language, opposite_direction_map['ru']).get(bias, 'movement')
        
        ob_type_map = {
            'ru': {'bullish': 'бычий', 'bearish': 'медвежий'},
            'en': {'bullish': 'bullish', 'bearish': 'bearish'},
            'uz': {'bullish': 'ko\'tariluvchi', 'bearish': 'tushuvchi'}
        }
        ob_type = ob_type_map.get(language, ob_type_map['ru']).get(nearest_ob.get('type') if nearest_ob else 'bullish', 'bullish')
        
        reaction_map = {
            'ru': {'bullish': 'отскок', 'bearish': 'продажи'},
            'en': {'bullish': 'bounce', 'bearish': 'selling'},
            'uz': {'bullish': 'sakrash', 'bearish': 'sotish'}
        }
        expected_reaction = reaction_map.get(language, reaction_map['ru']).get(bias, 'reaction')
        
        templates = self.smc_templates.get(language, self.smc_templates['ru'])
        template_idx = 0
        if nearest_ob:
            template_idx = 1
        elif len(order_blocks) > 0:
            template_idx = 3
        
        template = templates[template_idx]
        
        confirmation_level = current_price * 1.001 if bias == "bullish" else current_price * 0.999
        target_level = current_price * 1.015 if bias == "bullish" else current_price * 0.985
        invalidation_level = current_price * 0.99 if bias == "bullish" else current_price * 1.01
        
        insight = template.format(
            symbol=symbol,
            liquidity_zone=f"{self._format_price(current_price * 0.995)}-{self._format_price(current_price * 1.005)}",
            confirmation_level=self._format_price(confirmation_level),
            bias=bias_text,
            target_level=self._format_price(target_level),
            invalidation_level=self._format_price(invalidation_level),
            opposite_direction=opposite_direction,
            ob_level=self._format_price(nearest_ob.get('level', current_price) if nearest_ob else current_price),
            ob_type=ob_type,
            fvg_start=self._format_price(nearest_fvg.get('start_price', current_price) if nearest_fvg else current_price),
            fvg_end=self._format_price(nearest_fvg.get('end_price', current_price * 1.01) if nearest_fvg else current_price * 1.01),
            market_bias=bias_text,
            bos_level=self._format_price(current_price * 1.005),
            liquidity_target=self._format_price(target_level),
            stop_level=self._format_price(invalidation_level),
            expected_reaction=expected_reaction
        )
        
        return self._clean_insight(insight)
    

    def _generate_generic_insight(self, data: Dict, symbol: str, current_price: float, language: str) -> str:
       targets = data.get('targets', [])
    
       if targets:
           target = targets[0]
           if language == 'en':
               direction = "growth" if target > current_price else "decline"
               return f"{symbol} analysis indicates potential {direction} to ${self._format_price(target)} level. Key zone for monitoring."
           elif language == 'uz':
               direction = "o'sish" if target > current_price else "pasayish"
               return f"{symbol} tahlili ${self._format_price(target)} darajasiga potentsial {direction} ni ko'rsatadi. Monitoring uchun asosiy zona."
           else:
               direction = "рост" if target > current_price else "снижение"
               return f"Анализ {symbol} указывает на потенциальное {direction} к уровню ${self._format_price(target)}. Ключевая зона для мониторинга."
    
       if language == 'en':
           return f"{symbol} market is in uncertainty state. Recommended to wait for confirming signals before position entry."
       elif language == 'uz':
           return f"{symbol} bozori noaniqlik holatida. Pozitsiyaga kirishdan oldin tasdiqlash signallarini kutish tavsiya etiladi."
       else:
           return f"Рынок {symbol} находится в состоянии неопределённости. Рекомендуется дождаться подтверждающих сигналов для входа в позицию."
   

    def _determine_trend_direction(self, data: Dict) -> str:
        current_wave = data.get('current_wave', 1)
        wave_structure = data.get('wave_structure', {})
        
        if current_wave in [1, 3, 5]:
            return "bullish"
        elif current_wave in [2, 4]:
            return "bearish"
        else:
            return "neutral"

    def _determine_market_condition(self, data: Dict) -> str:
        market_structure = data.get('market_structure', {})
        structure = market_structure.get('structure', 'consolidation')
        return structure

    def _extract_key_levels(self, data: Dict, current_price: float) -> Dict:
        targets = data.get('targets', [])
        fibonacci_levels = data.get('fibonacci_levels', {})
        
        resistance = current_price * 1.02
        support = current_price * 0.98
        
        for target in targets:
            if target > current_price:
                resistance = target
                break
        
        for target in reversed(targets):
            if target < current_price:
                support = target
                break
        
        return {
            'resistance': resistance,
            'support': support
        }

    def _find_nearest_order_block(self, order_blocks: List[Dict], current_price: float) -> Optional[Dict]:
        if not order_blocks:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for ob in order_blocks:
            level = ob.get('level', ob.get('price', 0))
            distance = abs(level - current_price)
            if distance < min_distance:
                min_distance = distance
                nearest = ob
        
        return nearest

    def _find_nearest_fvg(self, fvgs: List[Dict], current_price: float) -> Optional[Dict]:
        if not fvgs:
            return None
        
        for fvg in fvgs:
            start = fvg.get('start_price', fvg.get('start', 0))
            end = fvg.get('end_price', fvg.get('end', 0))
            
            if start <= current_price <= end:
                return fvg
        
        return fvgs[0] if fvgs else None

    def _find_nearest_liquidity(self, liquidity_zones: List[Dict], current_price: float) -> Optional[Dict]:
        if not liquidity_zones:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for zone in liquidity_zones:
            level = zone.get('level', zone.get('start_price', 0))
            distance = abs(level - current_price)
            if distance < min_distance:
                min_distance = distance
                nearest = zone
        
        return nearest

    def _format_price(self, price: float) -> str:
        if price >= 1000:
            return f"{price:,.0f}"
        elif price >= 1:
            return f"{price:.2f}"
        else:
            return f"{price:.4f}"

    def _clean_insight(self, insight: str) -> str:
        insight = ' '.join(insight.split())
        insight = re.sub(r'[.]{2,}', '.', insight)
        insight = re.sub(r'[,]{2,}', ',', insight)
        
        if len(insight) > 300:
            insight = insight[:297] + "..."
        
        return insight
    def extract_insight_from_raw_analysis(self, raw_analysis: str, method: str, current_price: float, language: str = 'ru') -> str:
      lines = raw_analysis.split('\n')
      key_info = {}
      
      for line in lines:
          line = line.strip()
          prices = re.findall(self.price_pattern, line)
          
          entry_keywords = {'ru': ['вход', 'entry'], 'en': ['entry'], 'uz': ['kirish']}
          target_keywords = {'ru': ['цель', 'target'], 'en': ['target'], 'uz': ['maqsad']}
          stop_keywords = {'ru': ['стоп', 'stop'], 'en': ['stop'], 'uz': ['stop']}
          
          if any(keyword in line.lower() for keyword in entry_keywords.get(language, entry_keywords['ru'])) and prices:
              key_info['entry'] = float(prices[0].replace(',', ''))
          elif any(keyword in line.lower() for keyword in target_keywords.get(language, target_keywords['ru'])) and prices:
              key_info['target'] = float(prices[0].replace(',', ''))
          elif any(keyword in line.lower() for keyword in stop_keywords.get(language, stop_keywords['ru'])) and prices:
              key_info['stop'] = float(prices[0].replace(',', ''))
      
      if key_info.get('target') and key_info.get('entry'):
          target = key_info['target']
          entry = key_info['entry']
          
          if language == 'en':
              direction = "growth" if target > current_price else "decline"
              return f"Analysis shows potential for {direction} to ${self._format_price(target)}. Entry zone around ${self._format_price(entry)}. Key levels confirm the scenario."
          elif language == 'uz':
              direction = "o'sish" if target > current_price else "pasayish"
              return f"Tahlil ${self._format_price(target)} ga {direction} potentsialini ko'rsatadi. Kirish zonasi ${self._format_price(entry)} atrofida. Asosiy darajalar stsenariyni tasdiqlaydi."
          else:
              direction = "рост" if target > current_price else "снижение"
              return f"Анализ показывает потенциал для {direction} к ${self._format_price(target)}. Зона входа около ${self._format_price(entry)}. Ключевые уровни подтверждают сценарий."
      
      return self._generate_generic_insight(key_info, "BTC", current_price, language)