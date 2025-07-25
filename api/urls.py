from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('analysis/generate/', views.generate_analysis, name='generate_analysis'),
    path('analysis/', views.AnalysisRequestListView.as_view(), name='analysis_list'),
    path('analysis/<int:pk>/', views.AnalysisRequestDetailView.as_view(), name='analysis_detail'),
    path('analysis/result/<int:pk>/', views.AnalysisResultDetailView.as_view(), name='analysis_result'),
    path('symbols/', views.get_symbols, name='symbols'),
    path('market-data/<str:symbol>/', views.get_market_data, name='market_data'),
]