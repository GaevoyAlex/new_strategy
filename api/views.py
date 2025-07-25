from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import logging

from .models import AnalysisRequest, AnalysisResult, Symbol
from .serializers import (
    AnalysisRequestSerializer, AnalysisResultSerializer, 
    SymbolSerializer, GenerateAnalysisSerializer, SymbolListSerializer
)
from market_data.client import BinanceClient
from market_data.data_processor import parse_klines_to_ohlc, calculate_volume_profile
from analysis.methods.elliott_wave import ElliottWaveAnalyzer
from analysis.methods.volume_cluster import VolumeClusterAnalyzer
from analysis.methods.smart_money import SmartMoneyAnalyzer
from analysis.ai.claude_client import ClaudeClient

logger = logging.getLogger('trading_analysis')

class AnalysisRequestListView(generics.ListCreateAPIView):
    queryset = AnalysisRequest.objects.all()
    serializer_class = AnalysisRequestSerializer

class AnalysisRequestDetailView(generics.RetrieveAPIView):
    queryset = AnalysisRequest.objects.all()
    serializer_class = AnalysisRequestSerializer

class AnalysisResultDetailView(generics.RetrieveAPIView):
    queryset = AnalysisResult.objects.all()
    serializer_class = AnalysisResultSerializer

@api_view(['POST'])
def generate_analysis(request):
    serializer = GenerateAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    symbol = serializer.validated_data['symbol']
    method = serializer.validated_data['method']
    timeframe = serializer.validated_data['timeframe']
    language = serializer.validated_data.get('language', 'ru')
    
    logger.info(f"Analysis request: {symbol} | {method} | {timeframe}")
    
    try:
        analysis_request = AnalysisRequest.objects.create(
            symbol=symbol,
            method=method,
            timeframe=timeframe,
            status='processing'
        )
        
        binance_client = BinanceClient()
        
        klines_data = binance_client.get_klines(symbol, timeframe, settings.DEFAULT_KLINES_LIMIT)
        ohlc_data = parse_klines_to_ohlc(klines_data)
        
        if not ohlc_data:
            analysis_request.status = 'failed'
            analysis_request.save()
            return Response(
                {'error': 'No market data available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_price = ohlc_data[-1]['close']
        
        try:
            order_book_data = binance_client.get_order_book(symbol, 1000)
        except Exception:
            order_book_data = {}
        
        market_data = {
            'symbol': symbol,
            'current_price': current_price,
            'ohlc_data': ohlc_data,
            'order_book': order_book_data
        }
        
        if method == 'elliott_wave':
            analyzer = ElliottWaveAnalyzer()
            analysis_data = analyzer.analyze(ohlc_data, timeframe)
            market_data['analysis_data'] = {
                'wave_structure': analysis_data.get('wave_structure', {}),
                'fibonacci_levels': analysis_data.get('fibonacci_levels', {}),
                'current_wave': analysis_data.get('current_wave', 1),
                'forecast': analysis_data.get('forecast', {})
            }
        
        elif method == 'volume_cluster':
            analyzer = VolumeClusterAnalyzer()
            analysis_data = analyzer.analyze(ohlc_data, order_book_data, timeframe)
            market_data['analysis_data'] = {
                'volume_profile': analysis_data.get('volume_profile', {}),
                'key_levels': analysis_data.get('key_levels', {}),
                'market_position': analysis_data.get('market_position', {}),
                'trading_signals': analysis_data.get('trading_signals', {})
            }
        
        elif method == 'smart_money':
            analyzer = SmartMoneyAnalyzer()
            analysis_data = analyzer.analyze(ohlc_data, timeframe)
            market_data['analysis_data'] = {
                'order_blocks': analysis_data.get('order_blocks', []),
                'fair_value_gaps': analysis_data.get('fair_value_gaps', []),
                'structure_breaks': analysis_data.get('structure_breaks', []),
                'liquidity_zones': analysis_data.get('liquidity_zones', []),
                'smc_signals': analysis_data.get('smc_signals', {})
            }
        
        claude_client = ClaudeClient()
        claude_response = claude_client.generate_analysis(method, market_data, timeframe, language)
        
        analysis_result = AnalysisResult.objects.create(
            request=analysis_request,
            raw_analysis=claude_response.get('raw_analysis', ''),
            parsed_data=claude_response,
            market_data=market_data,
            current_price=current_price
        )
        
        analysis_request.status = 'completed'
        analysis_request.save()
        
        return Response({
            'analysis_id': analysis_request.id,
            'result_id': analysis_result.id,
            'status': 'completed',
            'raw_analysis': claude_response.get('raw_analysis', ''),
            'analysis_data': market_data.get('analysis_data', {}),
            'current_price': current_price,
            'timestamp': analysis_result.analysis_timestamp
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Analysis generation failed: {str(e)}")
        if 'analysis_request' in locals():
            analysis_request.status = 'failed'
            analysis_request.save()
        
        return Response(
            {'error': f'Analysis generation failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_symbols(request):
    serializer = SymbolListSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    search = serializer.validated_data.get('search', '')
    limit = serializer.validated_data.get('limit', 50)
    
    try:
        binance_client = BinanceClient()
        all_symbols = binance_client.get_symbols()
        
        if search:
            filtered_symbols = [s for s in all_symbols if search.upper() in s]
        else:
            filtered_symbols = all_symbols
        
        return Response({
            'symbols': filtered_symbols[:limit],
            'total': len(filtered_symbols)
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch symbols: {str(e)}")
        return Response(
            {'error': 'Failed to fetch symbols'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_market_data(request, symbol):
    timeframe = request.query_params.get('timeframe', '4h')
    
    if timeframe not in settings.SUPPORTED_TIMEFRAMES:
        return Response(
            {'error': f'Timeframe must be one of: {", ".join(settings.SUPPORTED_TIMEFRAMES)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        binance_client = BinanceClient()
        
        klines_data = binance_client.get_klines(symbol.upper(), timeframe, 100)
        ohlc_data = parse_klines_to_ohlc(klines_data)
        
        volume_profile = calculate_volume_profile(ohlc_data)
        
        ticker_data = binance_client.get_24hr_ticker(symbol.upper())
        
        return Response({
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'current_price': float(ticker_data.get('lastPrice', 0)),
            'price_change_24h': float(ticker_data.get('priceChange', 0)),
            'price_change_percent_24h': float(ticker_data.get('priceChangePercent', 0)),
            'volume_24h': float(ticker_data.get('volume', 0)),
            'ohlc_data': ohlc_data[-50:],
            'volume_profile': volume_profile
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch market data for {symbol}: {str(e)}")
        return Response(
            {'error': 'Failed to fetch market data'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )