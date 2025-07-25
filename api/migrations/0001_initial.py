# Generated by Django 5.2 on 2025-07-21 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20, unique=True)),
                ('base_asset', models.CharField(max_length=10)),
                ('quote_asset', models.CharField(max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
        migrations.CreateModel(
            name='AnalysisRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20)),
                ('method', models.CharField(choices=[('elliott_wave', 'Elliott Wave'), ('volume_cluster', 'Volume Cluster'), ('smart_money', 'Smart Money Concept')], max_length=20)),
                ('timeframe', models.CharField(choices=[('1h', '1 Hour'), ('4h', '4 Hours'), ('1d', '1 Day')], max_length=5)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AnalysisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_analysis', models.TextField()),
                ('parsed_data', models.JSONField(default=dict)),
                ('market_data', models.JSONField(default=dict)),
                ('current_price', models.DecimalField(decimal_places=8, max_digits=20)),
                ('analysis_timestamp', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='api.analysisrequest')),
            ],
        ),
        migrations.CreateModel(
            name='MarketData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20)),
                ('timeframe', models.CharField(max_length=5)),
                ('ohlcv_data', models.JSONField()),
                ('volume_profile', models.JSONField(default=dict)),
                ('order_book', models.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'unique_together': {('symbol', 'timeframe', 'timestamp')},
            },
        ),
    ]
