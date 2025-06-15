# team5project/index/views.py
from django.shortcuts import render, redirect
from .models import Note # index 앱의 Note 모델
from .stockModel import StockModel # index 앱의 StockModel 모델
from django.views.generic import ListView
from django.db import transaction # 트랜잭션 임포트
from .utils import get_kospi_basic_info, get_kospi_realtime_data
from django.http import JsonResponse
import requests
import logging

# crawling.py에 있는 함수를 임포트합니다.
# index 앱 내에 crawling.py가 있다면 상대 경로 임포트
from .crawling import get_and_display_stocks_data_and_save # 이름 변경 제안

# 기존 뷰 함수들...
def index(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Note.objects.create(content=content)
            return redirect('index')
    notes = Note.objects.all().order_by('-created_at')
    # index.html이 Note와 StockModel 데이터를 동시에 보여줘야 한다면
    # 아래 StockListView의 로직을 여기에 통합해야 합니다.
    # 하지만 현재 StockListView가 index.html을 직접 렌더링하므로,
    # 'notes' 데이터를 여기에 전달하는 것은 이 'index' 뷰가 아니라 StockListView에 통합되어야 할 수 있습니다.
    # 일단은 기존 index 뷰는 Note 관련 기능만 유지합니다.
    return render(request, 'index/index.html', {'notes': notes})


def charts(request):
    # StockListView와 동일하게 거래량 내림차순 200개(혹은 전체)로 통일
    stocks = StockModel.objects.all().order_by('-accumulated_trading_volume')[:200]
    print(stocks)  # 데이터가 실제로 있는지 확인
    return render(request, "index/charts.html", {"stocks": stocks})

def error_401(request):
    return render(request, 'index/401.html')

def error_404(request):
    return render(request, 'index/404.html')

def error_500(request):
    return render(request, 'index/500.html')

def layout_sidenav_light(request):
    return render(request, 'index/layout-sidenav-light.html')

def layout_static(request):
    return render(request, 'index/layout-static.html')

def login(request):
    return render(request, 'index/login.html')

def password(request):
    return render(request, 'index/password.html')

def register(request):
    return render(request, 'index/register.html')

def tables(request):
    return render(request, 'index/tables.html')


# 주식 목록을 보여주는 클래스 기반 뷰 (주요 변경 사항)
class StockListView(ListView):
    model = StockModel
    template_name = 'index/index.html'
    context_object_name = 'stocks_page' # 템플릿 변수 이름을 'stocks_page'로 통일
    # paginate_by = 20  # 이 줄을 제거하여 모든 데이터 표시

    # 이 메소드가 뷰가 렌더링되기 전에 호출됩니다.
    def dispatch(self, request, *args, **kwargs):
        # 페이지가 로드될 때마다 최신 주식 데이터를 가져와 DB에 저장/업데이트
        # get_and_display_stocks_data_and_save는 API 호출 및 DB 저장 로직만 수행하도록 crawling.py에서 수정해야 합니다.
        get_and_display_stocks_data_and_save()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # API 호출 스크립트와 동일한 정렬을 유지하거나 원하는 정렬로 변경
        return StockModel.objects.all().order_by('-accumulated_trading_volume')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 기존 index 뷰의 Note 데이터를 StockListView에 통합 (선택 사항)
        # 만약 index.html에서 Note 데이터도 함께 보여줘야 한다면
        context['notes'] = Note.objects.all().order_by('-created_at')
        return context
    
from django.http import JsonResponse

def kospi_basic_api(request):
    """KOSPI 기본 정보를 JSON으로 반환합니다."""
    try:
        data = get_kospi_basic_info()
        if data:
            return JsonResponse(data, status=200, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse({"error": "No KOSPI basic data available"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Exception occurred: {str(e)}"}, status=500)

def kospi_realtime_api(request):
    """KOSPI 실시간 데이터를 JSON으로 반환합니다."""
    try:
        data = get_kospi_realtime_data()
        if data:
            if 'result' in data:
                return JsonResponse(data['result'], status=200, json_dumps_params={'ensure_ascii': False})
            return JsonResponse(data, status=200, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse({"error": "No KOSPI realtime data available"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Exception occurred: {str(e)}"}, status=500)


# def kospi_data_page(request):
#     raw_data = get_kospi_basic_info()
#     if not raw_data or 'items' not in raw_data:
#         basic_data = {"dates": [], "values": []}
#     else:
#         items = raw_data['items']
#         dates = [item['date'] for item in items]
#         values = [float(item['closePrice'].replace(',', '')) for item in items]
#         basic_data = {
#             "dates": dates,
#             "values": values
#         }
#     return render(request, 'stock_app/kospi_dashboard.html', {'basic_data': basic_data})
from datetime import datetime, timedelta

def kospi_data_page(request):
    kospi_data = get_kospi_basic_info()

    if kospi_data:
        close_price_str = kospi_data.get("closePrice", "0").replace(",", "")
        try:
            close_price = float(close_price_str)
        except ValueError:
            close_price = 0
    else:
        close_price = 0

    # ✅ 현재 시간 기준으로 과거 9개 더미 데이터 생성
    now = datetime.now()
    labels = []
    values = []

    for i in range(9, 0, -1):
        past_time = (now - timedelta(seconds=i * 5)).strftime("%H:%M:%S")
        labels.append(past_time)
        values.append(close_price)  # 더미 값으로 현재 값 재사용

    # ✅ 마지막은 실제 데이터 시간
    labels.append(now.strftime("%H:%M:%S"))
    values.append(close_price)

    basic_data = {
        "labels": labels,
        "values": values
    }

    return render(request, 'index/charts.html', {'basic_data': basic_data})
def industry_chart_page(request):
    import requests
    industry_url = "https://m.stock.naver.com/api/stocks/industry?page=1&pageSize=20"
    try:
        response = requests.get(industry_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # groups 키에 산업별 리스트가 있음
        groups = data.get("groups", [])

        # 각 그룹 이름과 changeRate 추출, changeRate를 float로 변환
        industry_labels = []
        industry_values = []
        for g in groups:
            industry_labels.append(g.get("name", ""))
            try:
                # !!! 이 부분이 중요합니다. API 응답에서 'changeRate'가 없을 수 있습니다.
                # 'changeRate'가 숫자여야 하는데 문자열이거나 없을 경우를 대비해야 합니다.
                change_rate_str = g.get("changeRate", "0")
                industry_values.append(float(change_rate_str))
            except ValueError:
                # 문자열을 float로 변환할 수 없을 때 0.0을 추가
                industry_values.append(0.0)

        industry_data = {
            "labels": industry_labels,
            "values": industry_values, # 이곳이 항상 배열이 되어야 합니다.
        }
    except Exception as e:
        print(f"Error fetching or parsing industry data: {e}")
        industry_data = {"labels": [], "values": []} # 오류 시에도 배열로 초기화

    basic_data = {
        "labels": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
        "values": [2200, 2210, 2190, 2230, 2220],
    }

    stocks_page = []  # 필요하면 실제 데이터 넣기

    print("DEBUG: industry_data generated in Django view:", industry_data) # 이 줄 추가

    return render(request, "index/industry_chart.html", {
        "industry_data": industry_data,
        "basic_data": basic_data,
        "stocks_page": stocks_page,
    })
