# team5project/index/crawling.py

import requests
import json
import time
from django.db import transaction
from .stockModel import StockModel # index 앱의 StockModel 임포트

# 함수 이름을 변경하여 역할이 명확해지도록 했습니다.
def get_and_display_stocks_data_and_save(): # request 인자는 더 이상 필요 없습니다.
    """
    네이버 금융 API에서 최신 주식 데이터를 가져와 모델에 저장/업데이트합니다.
    (웹 페이지 렌더링은 이 함수에서 하지 않습니다.)
    """
    stocks_per_page = 20
    base_api_url = "https://m.stock.naver.com/api/stocks/quantTop/all"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://m.stock.naver.com/"
    }

    total_api_pages_to_fetch = 10 # 200개 주식 (20개씩 10페이지)
    fetched_data_from_api = []

    print(f"API에서 최신 주식 데이터 가져오기 시작 (총 {total_api_pages_to_fetch * stocks_per_page}개 목표)...")

    for i in range(1, total_api_pages_to_fetch + 1):
        full_url = f"{base_api_url}?page={i}&pageSize={stocks_per_page}"
        print(f"    -> API 페이지 {i} 요청 중: {full_url}")

        try:
            response = requests.get(full_url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and 'stocks' in data and isinstance(data['stocks'], list):
                fetched_data_from_api.extend(data['stocks'])
            else:
                print(f"    -> API 페이지 {i}에서 데이터 없음 또는 예상치 못한 형식: {data}. API 호출 중단.")
                print(f"    -> API 응답 내용 (원문): {response.text[:500]}...")
                break

        except requests.exceptions.Timeout:
            print(f"    -> API 페이지 {i} 요청 시간 초과.")
            break
        except requests.exceptions.RequestException as e:
            print(f"    -> API 페이지 {i} 요청 중 오류 발생: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"    -> API 페이지 {i} JSON 디코딩 오류: {e}. 응답 텍스트: {response.text[:500]}")
            break

        time.sleep(0.05)

    print(f"\nAPI에서 총 {len(fetched_data_from_api)}개 항목 가져옴. DB 저장/업데이트 시작.")

    with transaction.atomic():
        saved_count = 0
        for stock_item in fetched_data_from_api:
            try:
                StockModel.objects.update_or_create( # StockModel로 변경
                    item_code=stock_item.get("itemCode"),
                    defaults={
                        'stock_name': stock_item.get("stockName"),
                        'close_price': stock_item.get("closePrice"),
                        'compare_to_previous_close_price': stock_item.get("compareToPreviousClosePrice"),
                        'fluctuations_ratio': stock_item.get("fluctuationsRatio"),
                        'accumulated_trading_volume': stock_item.get("accumulatedTradingVolume"),
                        'accumulated_trading_value_krw_hangeul': stock_item.get("accumulatedTradingValueKrwHangeul"),
                    }
                )
                saved_count += 1
            except Exception as e:
                print(f"      주식 {stock_item.get('stockName')} 저장/업데이트 중 오류 발생: {e}")
        print(f"총 {saved_count}개의 주식 데이터를 DB에 저장/업데이트했습니다.")

    # 이 함수에서는 더 이상 렌더링을 하지 않습니다.
    # return render(request, 'index.html', context) 이 부분 삭제



#-----------------------------코스피 크롤링---------------------
def get_kospi_basic_info():
    url = "https://m.stock.naver.com/api/index/KOSPI/basic"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"KOSPI 기본 정보 가져오기 오류: {e}")
        return None

def get_kospi_realtime_data():
    url = "https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"KOSPI 실시간 데이터 가져오기 오류: {e}")
        return None