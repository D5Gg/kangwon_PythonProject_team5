import requests
import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

def get_kospi_basic_info():
    """네이버 KOSPI 기본 정보를 가져옵니다."""
    url = "https://m.stock.naver.com/api/index/KOSPI/basic"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"KOSPI 기본 정보 가져오기 오류: {e}")
        return None

def get_kospi_realtime_data():
    """네이버 KOSPI 실시간 데이터를 가져옵니다."""
    url = "https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"KOSPI 실시간 데이터 가져오기 오류: {e}")
        return None
