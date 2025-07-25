from rest_framework import serializers
from .models import AnalysisRequest, AnalysisResult, Symbol, MarketData
from django.conf import settings

class AnalysisRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRequest
        fields = ['id', 'symbol', 'method', 'timeframe', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_symbol(self, value):
        if not value.endswith('USDT'):
            raise serializers.ValidationError("Only USDT pairs are supported")
        return value.upper()
    
    def validate_method(self, value):
        if value not in settings.SUPPORTED_METHODS:
            raise serializers.ValidationError(f"Method must be one of: {', '.join(settings.SUPPORTED_METHODS)}")
        return value
    
    def validate_timeframe(self, value):
        if value not in settings.SUPPORTED_TIMEFRAMES:
            raise serializers.ValidationError(f"Timeframe must be one of: {', '.join(settings.SUPPORTED_TIMEFRAMES)}")
        return value

class AnalysisResultSerializer(serializers.ModelSerializer):
    request = AnalysisRequestSerializer(read_only=True)
    
    class Meta:
        model = AnalysisResult
        fields = ['id', 'request', 'raw_analysis', 'parsed_data', 'market_data', 
                 'current_price', 'analysis_timestamp']
        read_only_fields = ['id', 'analysis_timestamp']

class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ['id', 'symbol', 'base_asset', 'quote_asset', 'is_active', 'last_updated']
        read_only_fields = ['id', 'last_updated']

class MarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketData
        fields = ['id', 'symbol', 'timeframe', 'ohlcv_data', 'volume_profile', 
                 'order_book', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class GenerateAnalysisSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20)
    method = serializers.ChoiceField(choices=settings.SUPPORTED_METHODS)
    timeframe = serializers.ChoiceField(choices=settings.SUPPORTED_TIMEFRAMES)
    language = serializers.ChoiceField(choices=['ru', 'en', 'uz'], default='ru')
    
    def validate_symbol(self, value):
        return value.upper()

class SymbolListSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=False, default=50, min_value=1, max_value=100)