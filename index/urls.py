# team5project/index/urls.py
from django.urls import path
from .views import (
    # index, # 'index' 뷰를 직접 사용하지 않는다면 주석 처리하거나 제거하세요.
    charts, 
    login, password, register, tables,
    # kospi_data_page,  # 이 줄을 제거합니다.
    kospi_basic_api,
    kospi_realtime_api,
    stock_detail,
    search_stock_api,
    search_log_list,
    # industry_chart_page, # 이 줄을 제거합니다.
    StockListView
)

urlpatterns = [
    # 메인 대시보드 페이지: StockListView가 KOSPI 및 산업 차트 데이터를 포함하여 index.html을 렌더링합니다.
    path('', StockListView.as_view(), name='index'),

    # 'charts.html'이라는 별도의 차트 페이지가 여전히 필요하다면 유지합니다.
    path('charts/', charts, name='charts'),

    # 인증 관련 페이지들
    path('login/', login, name='login'),
    path('password/', password, name='password'),
    path('register/', register, name='register'),

    # 테이블 페이지
    path('tables/', tables, name='tables'),

    # API 엔드포인트는 계속 유지됩니다.
    path('api/kospi_basic/', kospi_basic_api, name='kospi_basic_api'),
    path('api/kospi_realtime/', kospi_realtime_api, name='kospi_realtime_api'),

     # 새로운 주식 검색 API 엔드포인트
    path('api/search-stock/', search_stock_api, name='search_stock_api'), # <--- 이 줄을 수정
    path('stock_detail/', stock_detail, name='stock_detail'),
    path('stock.html/', stock_detail, name='stock_detail'),
    path('search_logs.html/', search_log_list, name='search_log_list'),
]