import anthropic
from django.conf import settings
from datetime import datetime
import logging
from .response_parser import ResponseParser
from .text_cleaner import TextCleaner
from .structured_formater import StructuredFormatter
from .insight_generator import InsightGenerator

logger = logging.getLogger('trading_analysis')

ELLIOTT_WAVE_TEMPLATE = {
    'ru': """
Проведи волновой анализ Эллиота для {symbol} на {timeframe}.
Данные: цена {current_price}, волны {wave_structure}, фибо {fibonacci_levels}, прогноз {forecast}.

Создай КРАТКИЙ торговый инсайт в стиле профессионального трейдера, как в примерах:
"После завершения волны 2 BTC показывает классический старт третьей волны. При сохранении импульса и пробое $105,400 вероятно продолжение тренда вверх. На 1H стоит ждать либо вход от отката, либо пробой с ретестом. Волна 3 — обычно самая сильная, при этом рыночные объёмы уже подтверждают интерес."

Требования:
- Максимум 2-3 предложения
- Конкретные уровни цен с $
- Практические советы для входа
- Без эмодзи, без markdown
- НА РУССКОМ языке
- Уникальный текст каждый раз

Пиши как опытный трейдер для трейдеров.
""",
    'en': """
Conduct Elliott Wave analysis for {symbol} on {timeframe}.
Data: price {current_price}, waves {wave_structure}, fibonacci {fibonacci_levels}, forecast {forecast}.

Create BRIEF trading insight in professional trader style, like examples:
"After completing wave 2, BTC shows classic start of third wave. With momentum continuation and break above $105,400, upward trend continuation is likely. On 1H timeframe, wait for either pullback entry or breakout with retest. Wave 3 is usually the strongest, with market volumes already confirming interest."

Requirements:
- Maximum 2-3 sentences
- Specific price levels with $
- Practical entry advice
- No emojis, no markdown
- IN ENGLISH
- Unique text each time

Write as experienced trader for traders.
""",
    'uz': """
{symbol} uchun {timeframe} da Elliott Wave tahlili o'tkazing.
Ma'lumotlar: narx {current_price}, to'lqinlar {wave_structure}, fibonacci {fibonacci_levels}, prognoz {forecast}.

Professional treyderlar uslubida QISQA savdo insight yarating, masalan:
"Ikkinchi to'lqin tugagandan so'ng, BTC uchinchi to'lqinning klassik boshlanishini ko'rsatmoqda. Impuls davom etib, $105,400 dan yuqoriga chiqib ketsa, yuqoriga trend davom etishi mumkin. 1H da orqaga tortish yoki sinish bilan qayta testni kutish kerak. 3-to'lqin odatda eng kuchli bo'lib, bozor hajmlari allaqachon qiziqishni tasdiqlaydi."

Talablar:
- Maksimum 2-3 ta gap
- $ bilan aniq narx darajalari
- Kirish uchun amaliy maslahatlar
- Emojisiz, markdownsiz
- O'ZBEK TILIDA
- Har safar noyob matn

Tajribali treyderlar uchun treyderlar kabi yozing.
"""
}

VOLUME_CLUSTER_TEMPLATE = {
    'ru': """
Проведи объёмный анализ для {symbol} на {timeframe}.
Данные: цена {current_price}, Volume Profile {volume_profile}, уровни {key_levels}, структура {market_position}.

Создай КРАТКИЙ торговый инсайт в стиле профессионального трейдера, как в примерах:
"Рынок демонстрирует признаки восстановления после недавнего снижения. Поддержка в области VAL удержалась, и цена стремится вернуться к POC. Если цена закрепится выше $104,700, это может открыть путь к следующему уровню сопротивления около $105,627."

Требования:
- Максимум 2-3 предложения
- Конкретные уровни POC, VAH, VAL с $
- Практические выводы по объёмам
- Без эмодзи, без markdown
- НА РУССКОМ языке
- Уникальный текст каждый раз

Пиши как опытный трейдер для трейдеров.
""",
    'en': """
Conduct volume analysis for {symbol} on {timeframe}.
Data: price {current_price}, Volume Profile {volume_profile}, levels {key_levels}, structure {market_position}.

Create BRIEF trading insight in professional trader style, like examples:
"Market shows signs of recovery after recent decline. Support in VAL area held, and price aims to return to POC. If price consolidates above $104,700, it may open path to next resistance level around $105,627."

Requirements:
- Maximum 2-3 sentences
- Specific POC, VAH, VAL levels with $
- Practical volume conclusions
- No emojis, no markdown
- IN ENGLISH
- Unique text each time

Write as experienced trader for traders.
""",
    'uz': """
{symbol} uchun {timeframe} da hajm tahlili o'tkazing.
Ma'lumotlar: narx {current_price}, Volume Profile {volume_profile}, darajalar {key_levels}, tuzilish {market_position}.

Professional treyderlar uslubida QISQA savdo insight yarating, masalan:
"Bozor yaqinda pasayishdan keyin tiklanish belgilarini ko'rsatmoqda. VAL hududidagi qo'llab-quvvatlash saqlanib qoldi va narx POC ga qaytishga intilmoqda. Agar narx $104,700 dan yuqorida mustahkam bo'lsa, bu $105,627 atrofidagi keyingi qarshilik darajasiga yo'l ochishi mumkin."

Talablar:
- Maksimum 2-3 ta gap
- $ bilan aniq POC, VAH, VAL darajalari
- Hajmlar bo'yicha amaliy xulosalar
- Emojisiz, markdownsiz
- O'ZBEK TILIDA
- Har safar noyob matn

Tajribali treyderlar uchun treyderlar kabi yozing.
"""
}

SMC_TEMPLATE = {
    'ru': """
Проведи Smart Money анализ для {symbol} на {timeframe}.
Данные: цена {current_price}, Order Blocks {order_blocks}, FVG {fair_value_gaps}, структура {structure_breaks}, ликвидность {liquidity_zones}.

Создай КРАТКИЙ торговый инсайт в стиле профессионального трейдера, как в примерах:
"Рынок демонстрирует признаки возможного разворота после захвата ликвидности в области $104,500–$105,000. Если цена закрепится выше $104,300, это может подтвердить бычий сценарий с целью $105,500. Однако пробой ниже $103,500 может привести к дальнейшему снижению."

Требования:
- Максимум 2-3 предложения
- Конкретные уровни Order Blocks, FVG с $
- Сценарии и ключевые уровни
- Без эмодзи, без markdown
- НА РУССКОМ языке
- Уникальный текст каждый раз

Пиши как опытный трейдер для трейдеров.
""",
    'en': """
Conduct Smart Money analysis for {symbol} on {timeframe}.
Data: price {current_price}, Order Blocks {order_blocks}, FVG {fair_value_gaps}, structure {structure_breaks}, liquidity {liquidity_zones}.

Create BRIEF trading insight in professional trader style, like examples:
"Market shows signs of possible reversal after liquidity sweep in $104,500–$105,000 area. If price consolidates above $104,300, it may confirm bullish scenario targeting $105,500. However, break below $103,500 may lead to further decline."

Requirements:
- Maximum 2-3 sentences
- Specific Order Blocks, FVG levels with $
- Scenarios and key levels
- No emojis, no markdown
- IN ENGLISH
- Unique text each time

Write as experienced trader for traders.
""",
    'uz': """
{symbol} uchun {timeframe} da Smart Money tahlili o'tkazing.
Ma'lumotlar: narx {current_price}, Order Blocks {order_blocks}, FVG {fair_value_gaps}, tuzilish {structure_breaks}, likvidlik {liquidity_zones}.

Professional treyderlar uslubida QISQA savdo insight yarating, masalan:
"Bozor $104,500–$105,000 hududida likvidlik ushlangandan keyin mumkin bo'lgan burilish belgilarini ko'rsatmoqda. Agar narx $104,300 dan yuqorida mustahkam bo'lsa, bu $105,500 ni maqsad qilgan ko'tarilish stsenariyni tasdiqlashi mumkin. Biroq, $103,500 dan pastga sinish keyingi pasayishga olib kelishi mumkin."

Talablar:
- Maksimum 2-3 ta gap
- $ bilan aniq Order Blocks, FVG darajalari
- Stsenariylar va asosiy darajalar
- Emojisiz, markdownsiz
- O'ZBEK TILIDA
- Har safar noyob matn

Tajribali treyderlar uchun treyderlar kabi yozing.
"""
}

class ClaudeClient:
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL
        
        try:
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=30.0
            )
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            raise Exception(f"Claude client initialization failed: {str(e)}")
            
        self.parser = ResponseParser()
        self.cleaner = TextCleaner()
        self.formatter = StructuredFormatter()
        self.insight_generator = InsightGenerator()

    def generate_analysis(self, method: str, market_data: dict, timeframe: str, language: str = 'ru') -> dict:
        try:
            prompt = self.build_prompt(method, market_data, timeframe, language)
            logger.info(f"Generating dynamic insight: {method} | {market_data.get('symbol')}")
            
            # Более безопасный вызов API с обработкой ошибок
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                analysis_text = response.content[0].text
                
            except anthropic.APIConnectionError as e:
                logger.error(f"Claude API connection error: {e}")
                raise Exception("Failed to connect to Claude API")
            except anthropic.RateLimitError as e:
                logger.error(f"Claude API rate limit: {e}")
                raise Exception("Claude API rate limit exceeded")
            except anthropic.APIStatusError as e:
                logger.error(f"Claude API status error: {e}")
                raise Exception(f"Claude API error: {e.status_code}")
            except Exception as e:
                logger.error(f"Unexpected Claude API error: {e}")
                raise Exception(f"Claude API call failed: {str(e)}")
            
            parsed_response = self.parse_response(analysis_text, method, market_data.get('symbol', 'UNKNOWN'), market_data.get('current_price', 0.0))
            
            insight = self._extract_clean_insight(analysis_text)
            
            if not insight or len(insight) < 50:
                insight = self.insight_generator.generate_insight(method, market_data.get('analysis_data', {}), market_data, language)
            
            parsed_response['trading_insight'] = insight
            parsed_response['short_analysis'] = insight
            parsed_response['dynamic_insight'] = True
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            
            fallback_insight = self.insight_generator.generate_insight(
                method, market_data.get('analysis_data', {}), market_data, language
            )
            
            return {
                'raw_analysis': f"Технический анализ {market_data.get('symbol')} выполнен. {fallback_insight}",
                'analysis_type': method,
                'status': 'completed_with_fallback',
                'trading_insight': fallback_insight,
                'short_analysis': fallback_insight,
                'dynamic_insight': False,
                'error': str(e)
            }


    def build_prompt(self, method: str, market_data: dict, timeframe: str, language: str = 'ru') -> str:
        template = self.get_base_template(method, language)
        
        return template.format(
            symbol=market_data.get('symbol'),
            timeframe=timeframe,
            current_price=market_data.get('current_price'),
            **market_data.get('analysis_data', {})
        )

    def get_base_template(self, method: str, language: str = 'ru') -> str:
        templates = {
            'elliott_wave': ELLIOTT_WAVE_TEMPLATE,
            'volume_cluster': VOLUME_CLUSTER_TEMPLATE,
            'smart_money': SMC_TEMPLATE
        }
        
        template_dict = templates.get(method, ELLIOTT_WAVE_TEMPLATE)
        return template_dict.get(language, template_dict.get('ru', ''))

    def parse_response(self, response_text: str, method: str, symbol: str = "UNKNOWN", current_price: float = 0.0) -> dict:
        base_parsed = None
        structured_text = None
        structured_data = None
        
        if method == 'elliott_wave':
            base_parsed = self.parser.parse_elliott_response(response_text)
            structured_text = self.cleaner.structure_elliott_analysis(response_text)
            structured_data = self.formatter.format_elliott_analysis(response_text, symbol, current_price)
        elif method == 'volume_cluster':
            base_parsed = self.parser.parse_volume_response(response_text)
            structured_text = self.cleaner.structure_volume_analysis(response_text)
            structured_data = self.formatter.format_volume_analysis(response_text, symbol, current_price)
        elif method == 'smart_money':
            base_parsed = self.parser.parse_smc_response(response_text)
            structured_text = self.cleaner.structure_smc_analysis(response_text)
            structured_data = self.formatter.format_smc_analysis(response_text, symbol, current_price)
        else:
            base_parsed = {
                "analysis_type": method,
                "raw_analysis": response_text,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            structured_text = {"clean_text": self.cleaner.clean_text(response_text)}
            structured_data = {"analysis_info": {"method": method, "symbol": symbol}}
        
        if base_parsed:
            base_parsed.update({
                "structured_analysis": structured_text,
                "structured_data": structured_data,
                "clean_text": structured_text.get("clean_text", "")
            })
        
        return base_parsed

    def _extract_clean_insight(self, claude_response: str) -> str:
        lines = claude_response.strip().split('\n')
        
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Требования:') and not line.startswith('Requirements:') and not line.startswith('Talablar:'):
                if not line.startswith('-') and not line.startswith('•'):
                    if len(line) > 30:
                        clean_lines.append(line)
        
        insight = ' '.join(clean_lines)
        
        if len(insight) > 350:
            sentences = insight.split('.')
            truncated_sentences = []
            current_length = 0
            
            for sentence in sentences:
                if current_length + len(sentence) + 1 <= 350:
                    truncated_sentences.append(sentence.strip())
                    current_length += len(sentence) + 1
                else:
                    break
            
            insight = '. '.join(truncated_sentences)
            if insight and not insight.endswith('.'):
                insight += '.'
        
        insight = ' '.join(insight.split())
        
        return insight if len(insight) > 50 else ""

    def generate_quick_insight(self, method: str, market_data: dict, language: str = 'ru') -> str:
        try:
            return self.insight_generator.generate_insight(
                method, 
                market_data.get('analysis_data', {}), 
                market_data,
                language
            )
        except Exception as e:
            logger.error(f"Quick insight generation failed: {e}")
            symbol = market_data.get('symbol', 'BTC').replace('USDT', '')
            
            if language == 'en':
                return f"{symbol} analysis completed. Recommended to monitor key levels for direction determination."
            elif language == 'uz':
                return f"{symbol} tahlili tugallandi. Yo'nalishni aniqlash uchun asosiy darajalarni monitoring qilish tavsiya etiladi."
            else:
                return f"Анализ {symbol} завершён. Рекомендуется мониторинг ключевых уровней для определения направления."