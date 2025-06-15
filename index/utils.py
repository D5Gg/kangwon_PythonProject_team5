import requests
import logging
from django.shortcuts import render
from bs4 import BeautifulSoup
import pandas as pd
import os

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
        
def get_stock_code_by_name(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'stockCodeInfo.xlsx')
    print(f"[DEBUG] stockCodeInfo path: {file_path}")  # 경로 출력

    df = pd.read_excel(file_path, engine='openpyxl')
    df['회사명'] = df['회사명'].astype(str).str.strip()

    row = df[df['회사명'] == name]
    if not row.empty:
        return str(row.iloc[0]['종목코드']).zfill(6)
    return None