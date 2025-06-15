# team5project/index/views.py
from django.shortcuts import render, redirect
from .models import Note
from .stockModel import StockModel, SearchLog # index 앱의 StockModel 모델
from django.views.generic import ListView
from django.db import transaction # 트랜잭션 임포트
from .utils import get_kospi_basic_info, get_kospi_realtime_data
from django.http import JsonResponse
import requests
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .utils import get_stock_code_by_name  # 종목 이름 → 코드 변환 함수
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json



# crawling.py에 있는 함수를 임포트합니다.
from .crawling import get_and_display_stocks_data_and_save

# 기존 뷰 함수들...
def index(request):
    # This 'index' view is largely superseded by StockListView for rendering index.html
    # You might want to consider removing it or renaming it if its purpose changes.
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'index/index.html', {'notes': notes})


def charts(request):
    # 모든 주식 데이터 (차트, 표 등에서 사용)
    stocks = StockModel.objects.all().order_by('-accumulated_trading_volume')[:200]

    # 거래량/거래대금 numeric 변환
    def to_int(val):
        try:
            return int(str(val).replace(',', ''))
        except Exception:
            return 0
    from .stockModel import parse_krw_hangeul
    volumes = [to_int(s.accumulated_trading_volume) for s in stocks]
    values = [parse_krw_hangeul(s.accumulated_trading_value_krw_hangeul) for s in stocks]

    def get_bin_distribution(data):
        if not data or max(data) == 0:
            return [0]*5, [0]*5, [0]*5
        x = max(data)
        bin_edges = [x, 4*x//5, 3*x//5, 2*x//5, x//5, 0]
        bin_counts = [0]*5
        for v in data:
            if v > bin_edges[1]:
                bin_counts[0] += 1
            elif v > bin_edges[2]:
                bin_counts[1] += 1
            elif v > bin_edges[3]:
                bin_counts[2] += 1
            elif v > bin_edges[4]:
                bin_counts[3] += 1
            else:
                bin_counts[4] += 1
        total = sum(bin_counts)
        bin_percents = [round((c/total)*100, 2) if total else 0 for c in bin_counts]
        bin_labels = [
            f'>{bin_edges[1]:,}',
            f'{bin_edges[2]+1:,}~{bin_edges[1]:,}',
            f'{bin_edges[3]+1:,}~{bin_edges[2]:,}',
            f'{bin_edges[4]+1:,}~{bin_edges[3]:,}',
            f'≤{bin_edges[4]:,}'
        ]
        return bin_labels, bin_percents, bin_counts

    volume_bin_labels, volume_bin_percents, volume_bin_counts = get_bin_distribution(volumes)
    value_bin_labels, value_bin_percents, value_bin_counts = get_bin_distribution(values)

    # 거래량 1위 종목 추출 (기존 area chart dummy)
    top_stock = stocks.first() if stocks else None
    area_labels = [f"{i+1}" for i in range(10)]
    area_values = []
    area_name = top_stock.stock_name if top_stock else "-"
    if top_stock:
        try:
            price = float(str(top_stock.close_price).replace(',', ''))
        except Exception:
            price = 0
        area_values = [price for _ in range(10)]
    else:
        area_values = [0 for _ in range(10)]
    area_chart_data = {
        "labels": area_labels,
        "values": area_values,
        "name": area_name,
    }

    print("volume_bin_counts:", volume_bin_counts)
    print("value_bin_counts:", value_bin_counts)

    return render(request, "index/charts.html", {
        "stocks": stocks,
        "area_chart_data": area_chart_data,
        "volume_bin_labels_json": json.dumps(volume_bin_labels),
        "volume_bin_counts_json": json.dumps(volume_bin_counts),
        "value_bin_labels_json": json.dumps(value_bin_labels),
        "value_bin_counts_json": json.dumps(value_bin_counts),
    })


def login(request):
    return render(request, 'index/login.html')

def password(request):
    return render(request, 'index/password.html')

def register(request):
    return render(request, 'index/register.html')

def tables(request):
    return render(request, 'index/tables.html')

def stock_detail(request):
    return render(request, 'index/stock_detail.html')

def search_log_list(request):
    logs = SearchLog.objects.all().order_by('-searched_at')
    return render(request, 'index/search_log_list.html', {'logs': logs})  # ← 경로 수정


# 주식 목록을 보여주는 클래스 기반 뷰 (주요 변경 사항)
class StockListView(ListView):
    model = StockModel
    template_name = 'index/index.html'
    context_object_name = 'stocks_page' # 템플릿 변수 이름을 'stocks_page'로 통일

    def dispatch(self, request, *args, **kwargs):
        # 페이지가 로드될 때마다 최신 주식 데이터를 가져와 DB에 저장/업데이트
        get_and_display_stocks_data_and_save()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # API 호출 스크립트와 동일한 정렬을 유지하거나 원하는 정렬로 변경
        return StockModel.objects.all().order_by('-accumulated_trading_volume')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- KOSPI Basic Data for Area Chart ---
        kospi_data = get_kospi_basic_info()
        close_price = 0
        if kospi_data and "closePrice" in kospi_data:
            try:
                close_price = float(kospi_data["closePrice"].replace(",", ""))
            except ValueError:
                close_price = 0

        # Generate dummy data for KOSPI chart labels and values
        now = datetime.now()
        labels = []
        values = []
        for i in range(9, 0, -1):
            past_time = (now - timedelta(seconds=i * 5)).strftime("%H:%M:%S")
            labels.append(past_time)
            values.append(close_price)  # Use the fetched current price as dummy
        labels.append(now.strftime("%H:%M:%S"))
        values.append(close_price)
        
        context['basic_data'] = {
            "labels": labels,
            "values": values
        }

        # --- Industry Data for Bar Chart ---
        industry_url = "https://m.stock.naver.com/api/stocks/industry?page=1&pageSize=20"
        try:
            response = requests.get(industry_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Pass the raw 'groups' data, as chart-bar-demo.js expects it.
            context['industry_data'] = data
        except Exception as e:
            logging.error(f"Error fetching or parsing industry data: {e}")
            context['industry_data'] = {"groups": []} # Ensure 'groups' key is always present
        
        # Existing Note data
        context['notes'] = Note.objects.all().order_by('-created_at')
        
        return context

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

# (기존 get_stock_code 함수는 동일하게 유지)
def get_stock_code(stock_name):
    import re
    from bs4 import BeautifulSoup
    import requests

    print(f"검색어: {stock_name}")

    if stock_name.isdigit() and len(stock_name) == 6:
        return stock_name  # 이미 코드면 바로 반환
        

    search_url = f"https://finance.naver.com/search/search.naver?query={stock_name}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 종목 코드가 들어 있는 링크 찾기
        a_tags = soup.select('a')  # 모든 a 태그를 순회
        for a in a_tags:
            href = a.get('href', '')
            if '/item/main.naver?code=' in href:
                match = re.search(r'code=(\d{6})', href)
                if match:
                    return match.group(1)

    except requests.RequestException as e:
        print(f"종목 코드 가져오기 오류: {e}")

    return None

def get_stock_info(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 주식명
        stock_name_tag = soup.select_one("div.wrap_company h2 a")
        stock_name = stock_name_tag.text.strip() if stock_name_tag else "알 수 없음"

        # 2. 현재가
        current_price_tag = soup.select_one("p.no_today span.blind")
        current_price = current_price_tag.text.strip().replace(",", "") if current_price_tag else "N/A"

        # 3. 전일비 및 등락률
        diff_tags = soup.select("p.no_exday span.blind")
        if len(diff_tags) >= 2:
            previous_day_change = diff_tags[0].text.strip().replace(",", "")
            fluctuation_rate = diff_tags[1].text.strip().replace("%", "").replace("상승", "").replace("하락", "")
        else:
            previous_day_change = fluctuation_rate = "N/A"

        # 4. 전일/고가/저가 (rate_info에서)
        last_price = soup.select_one("table.no_info td.first span.blind")
        high_price = soup.select_one("table.no_info td:nth-of-type(2) span.blind")
        low_price = soup.select_one("table.no_info tr:nth-of-type(2) td:nth-of-type(2) span.blind")

        # 5. 거래량
        trade_volume_tag = soup.select_one("table.no_info td:nth-of-type(3) span.blind")

    

        return {
            "stock_name": stock_name,
            "current_price": current_price,
            "previous_day_change": previous_day_change,
            "fluctuation_rate": fluctuation_rate,
            "last_price": last_price.text.strip().replace(",", "") if last_price else "N/A",
            "high_price": high_price.text.strip().replace(",", "") if high_price else "N/A",
            "low_price": low_price.text.strip().replace(",", "") if low_price else "N/A",
            "trade_volume": trade_volume_tag.text.strip().replace(",", "") if trade_volume_tag else "N/A",
        }

    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {e}")
        return {}

def get_daily_stock_prices(code, pages=10): # 최근 10페이지의 데이터를 가져온다고 가정
    prices = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 일별 시세 테이블 파싱
            table = soup.find('table', class_='type2')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 7: # 날짜, 종가, 전일비, 시가, 고가, 저가, 거래량
                        date = cols[0].text.strip()
                        if date.startswith('2'): # 날짜 형식 확인 (예: 2023.01.01)
                            close_price = cols[1].text.strip().replace(',', '')
                            prices.append({'date': date, 'close_price': int(close_price)})
            else:
                break # 더 이상 테이블이 없으면 종료

        except requests.exceptions.RequestException as e:
            print(f"일별 시세 가져오기 오류 (code: {code}, page: {page}): {e}")
            break
    
    # 날짜 순서대로 정렬 (가장 오래된 날짜가 먼저 오도록)
    prices.sort(key=lambda x: x['date'])
    return prices


def search_stock_api(request):
    stock_name = request.GET.get('stock_name', '').strip()

    if not stock_name:
        return JsonResponse({'error': '주식 이름을 입력해주세요.'}, status=400)

    # 검색 로그 저장
    SearchLog.objects.create(stock_name=stock_name)

    # 6자리 숫자인 경우 그대로 종목 코드로 사용
    if stock_name.isdigit() and len(stock_name) == 6:
        return JsonResponse({'code': stock_name})

    # 한글 종목 이름인 경우 코드 변환 시도
    code = get_stock_code_by_name(stock_name)
    if code:
        return JsonResponse({'code': code})
    else:
        return JsonResponse({'error': '해당 종목을 찾을 수 없습니다.'}, status=404)


def stock_detail(request):
    stock_code = request.GET.get('code')
    stock_info = {}
    daily_prices = []

    if stock_code:
        stock_info = get_stock_info(stock_code)
        daily_prices = get_daily_stock_prices(stock_code)  # 예: 리스트나 DataFrame

    # daily_prices 가 리스트면 DataFrame으로 변환
    if daily_prices and isinstance(daily_prices, list):
        df = pd.DataFrame(daily_prices)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    elif isinstance(daily_prices, pd.DataFrame):
        df = daily_prices.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
    else:
        df = pd.DataFrame()  # 빈 데이터프레임 fallback
    #체크
    print(f"daily_prices: {daily_prices[:5] if daily_prices else 'No data'}") # 처음 5개 항목만 출력
    if not df.empty:
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"First 5 rows of df:\n{df.head()}")
    else:
        print("DataFrame 'df' is empty.")
    #체크
    # 최소한 'close' 컬럼은 있어야 함
    if not df.empty and 'close_price' in df.columns:
        closing_prices = df[['close_price']]
        
        # 정규화
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(closing_prices)

        # create_dataset 함수 정의
        def create_dataset(data, time_step=60):
            X, Y = [], []
            for i in range(len(data) - time_step - 1):
                X.append(data[i:(i + time_step), 0])
                Y.append(data[i + time_step, 0])
            return np.array(X), np.array(Y)

        time_step = 60
        X, y = create_dataset(scaled_data, time_step)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        # LSTM 모델 생성 및 학습 (에포크 적게 설정 권장, 실서비스면 미리 학습한 모델 로드 추천)
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=1, batch_size=1, verbose=0)

        # 예측
        predictions = model.predict(X)
        predictions = scaler.inverse_transform(predictions)

        # 실제 값 (역정규화)
        actual = scaler.inverse_transform(y.reshape(-1, 1))

        # 결과 시각화 이미지를 base64로 변환해서 템플릿에 넘기기
        plt.figure(figsize=(10,5))
        plt.plot(actual, label='Actual Price')
        plt.plot(predictions, label='Predicted Price')
        plt.legend()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

    else:
        image_base64 = None

    context = {
        'stock_info': stock_info,
        'stock_code': stock_code,
        'daily_prices': daily_prices,
        'lstm_plot': image_base64,
    }
    return render(request, 'index/stock_detail.html', context)