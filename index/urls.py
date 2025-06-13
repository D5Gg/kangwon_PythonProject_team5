# team5project/index/urls.py
from django.urls import path
from .views import (
    index, charts, error_401, error_404, error_500,
    layout_sidenav_light, layout_static,
    login, password, register, tables,
    kospi_data_page,
    kospi_basic_api,
    kospi_realtime_api,
    industry_chart_page,
    StockListView # <--- StockListView를 임포트합니다.
)

urlpatterns = [
    # path('', index, name='index'), # 이 줄은 주석 처리하거나 다른 경로로 옮깁니다.
                                     # 만약 index 뷰의 Note 기능이 필요하다면 별도 경로를 줍니다.
    path('', StockListView.as_view(), name='index'), # 루트 경로를 StockListView에 연결

    path('charts/', charts, name='charts'),

    path('401/', error_401, name='error_401'),
    path('404/', error_404, name='error_404'),
    path('500/', error_500, name='error_500'),

    path('layout-sidenav-light/', layout_sidenav_light, name='layout_sidenav_light'),
    path('layout-static/', layout_static, name='layout_static'),

    path('login/', login, name='login'),
    path('password/', password, name='password'),
    path('register/', register, name='register'),

    path('tables/', tables, name='tables'),
    path('api/kospi_basic/', kospi_basic_api, name='kospi_basic_api'),
    path('api/kospi_realtime/', kospi_realtime_api, name='kospi_realtime_api'),
      path('industry-chart/', industry_chart_page, name='industry_chart'),
]