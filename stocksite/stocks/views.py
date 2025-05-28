from django.http import HttpResponse, HttpRequest
from stocks.models import Stock
from stocks.crawling import crawl_stock_top10


def index(request: HttpRequest) -> HttpResponse:
    top10_stocks = crawl_stock_top10()
    result = "<h1>주식 사이트</h1><p>현재 거래량 상위 10개 주식:</p><ul>"
    for stock in top10_stocks:
        if not stock.get("시총"):
            stock["시총"] = "정보 없음"
        if not stock.get("52주 최고"):
            stock["52주 최고"] = "정보 없음"
        if not stock.get("52주 최저"):
            stock["52주 최저"] = "정보 없음"
        Stock.objects.create(
            name=stock["주식 이름"],
            current_price=stock["현재가"],
            trading_money_volume=stock["대금"],
            trading_value=stock["거래량"],
            market_cap=stock["시총"],
            week52_high=stock["52주 최고"],
            week52_low=stock["52주 최저"]
        )
        result += f"<li>{stock['주식 이름']} - 현재가: {stock['현재가']}, 거래량: {stock['거래량']}, 시가총액: {stock['시총']}</li>"
    result += "</ul>"
    result += "<p>주식 정보는 데이터베이스에 저장되었습니다.</p>"
    return HttpResponse(result)

def mainPage(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>메인 페이지</h1><p>여기는 주식 사이트의 메인 페이지입니다.</p>")
                        
    
