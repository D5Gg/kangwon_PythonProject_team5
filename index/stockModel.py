from django.db import models

class StockModel(models.Model):
    # itemCode는 API에서 각 주식을 식별하는 고유 코드이므로 기본 키로 적합합니다.
    item_code = models.CharField(max_length=20, primary_key=True)
    stock_name = models.CharField(max_length=100, verbose_name="주식 이름", null=True, blank=True)
    close_price = models.CharField(max_length=20, verbose_name="현재가", null=True, blank=True)
    compare_to_previous_close_price = models.CharField(max_length=20, verbose_name="전일비", null=True, blank=True)
    fluctuations_ratio = models.CharField(max_length=20, verbose_name="등락률", null=True, blank=True)
    accumulated_trading_volume = models.CharField(max_length=50, verbose_name="거래량", null=True, blank=True)
    accumulated_trading_value_krw_hangeul = models.CharField(max_length=50, verbose_name="거래대금(억)", null=True, blank=True)

    # 데이터 업데이트 시간 기록
    last_updated = models.DateTimeField(auto_now=True) # 데이터가 저장/업데이트될 때마다 자동 갱신

    class Meta:
        verbose_name = "주식 정보"
        verbose_name_plural = "주식 정보"
        # 기본 정렬 순서를 지정할 수 있습니다 (예: 거래량 내림차순)
        ordering = ['-accumulated_trading_volume']

    def __str__(self):
        return self.stock_name if self.stock_name else self.item_code


# 거래대금 (억) 단위의 한글 표현을 정수로 변환하는 함수
# 저장 시 --> stock.accumulated_trading_value_krw_hangeul = parse_krw_hangeul(원본값)
# 예 : "1,234억원" -> 123400000000
def parse_krw_hangeul(value):
    if value is None:
        return 0
    value = str(value).replace(',', '').replace(' ', '')
    if value.endswith('억원'):
        try:
            num = float(value.replace('억원', ''))
            return int(num * 100000000)
        except ValueError:
            return 0
    try:
        return int(value)
    except ValueError:
        return 0


class SearchLog(models.Model):
    stock_name = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_name} searched at {self.searched_at}"