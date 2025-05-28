from django.db import models

class Stock(models.Model):
    """
    주식에서 크롤링 할 수 있는 변수들.
    "주식 이름"
    "현재가"
    "전일"
    "시가" "저가" "고가" 
    "거래량" "대금"
    "시총" "외인소진율"
    "52주 최고" "52주 최저"
    "PER" "EPS" "추정PER" "추정EPS"
    "PBR" "BPS"
    "배당수익률" "배당금"
    """
    name = models.CharField(max_length=50)
    current_price = models.CharField(max_length=20) # 현재가
    trading_money_volume = models.CharField(max_length=20) # 거래대금
    trading_value = models.CharField(max_length=20) # 거래량
    market_cap = models.CharField(max_length=20, default=0) # 시가총액
    week52_high = models.CharField(max_length=20) # 52주 최고
    week52_low = models.CharField(max_length=20) # 52주 최저
    