from django.db import models
from django.contrib.auth.models import User
import json

class AnalysisRequest(models.Model):
    ANALYSIS_METHODS = [
        ('elliott_wave', 'Elliott Wave'),
        ('volume_cluster', 'Volume Cluster'),
        ('smart_money', 'Smart Money Concept'),
    ]
    
    TIMEFRAMES = [
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    symbol = models.CharField(max_length=20)
    method = models.CharField(max_length=20, choices=ANALYSIS_METHODS)
    timeframe = models.CharField(max_length=5, choices=TIMEFRAMES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

class AnalysisResult(models.Model):
    request = models.OneToOneField(AnalysisRequest, on_delete=models.CASCADE, related_name='result')
    raw_analysis = models.TextField()
    parsed_data = models.JSONField(default=dict)
    market_data = models.JSONField(default=dict)
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    analysis_timestamp = models.DateTimeField(auto_now_add=True)
    
    def set_parsed_data(self, data):
        self.parsed_data = data
    
    def get_parsed_data(self):
        return self.parsed_data

class Symbol(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    base_asset = models.CharField(max_length=10)
    quote_asset = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['symbol']
    
    def __str__(self):
        return self.symbol

class MarketData(models.Model):
    symbol = models.CharField(max_length=20)
    timeframe = models.CharField(max_length=5)
    ohlcv_data = models.JSONField()
    volume_profile = models.JSONField(default=dict)
    order_book = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['symbol', 'timeframe', 'timestamp']