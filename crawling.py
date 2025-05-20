from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

stock_name = "삼성전자"

def crawl_stock_info(stock_name:str) -> None:
    driver = webdriver.Chrome()
    driver.get("https://m.stock.naver.com/")

    # 검색 버튼 클릭
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "HeaderButton-module_article__KwTay"))
    )
    element.click()

    # 검색창에 접근하여 stock_name 입력
    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "SearchBar_input__t2ws8"))
    )
    search_input.clear()
    search_input.send_keys(stock_name)
    sleep(1)  
    search_input.send_keys(u'\ue007')  # 엔터키 입력
    sleep(1)
    
    # 검색 결과 없음 처리 (타이틀 기반 추가)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    if soup.find(class_="newError_title__ohzpq"):
        print("검색 결과가 없습니다. (타이틀 오류)")
        driver.quit()
        return

    # 주식 코드 추출 (SearchList_information__E8LJ_ 안의 SearchList_code__59hG9)
    info_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "SearchList_information__E8LJ_"))
    )
    stock_code_elem = info_elem.find_element(By.CLASS_NAME, "SearchList_code__59hG9")
    stock_code = stock_code_elem.text.strip()

    # 해당 주식 상세 페이지로 이동
    stock_url = f"https://m.stock.naver.com/domestic/stock/{stock_code}/total"
    driver.get(stock_url)

    sleep(2)  # 페이지 로딩 대기

    # BeautifulSoup으로 정보 크롤링
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    sleep(1)

    # 디버깅용: HTML 일부 출력
    print("==== HTML 일부 미리보기 ====")
    print(soup.prettify()[:1000])
    print("===========================")

    sleep(1)
    # 현재가
    price_elem = soup.find(class_="GraphMain_price__GT8dV")
    if price_elem:
        current_price = price_elem.text.strip()
        print(f"현재가: {current_price}")
    else:
        print("현재가를 찾을 수 없습니다.")

    # 변수 정보와 값
    keys = soup.find_all(class_="StockInfo_key__naiA4")
    values = soup.find_all(class_="StockInfo_value__WAuXk")

    if keys and values and len(keys) == len(values):
        print("[주식 정보]")
        for k, v in zip(keys, values):
            print(f"{k.text.strip()}: {v.text.strip()}")
    else:
        print("변수 정보 또는 값을 찾을 수 없습니다.")

    sleep(3)  # 잠시 대기

    driver.quit()
    return

if __name__ == "__main__":
    # 주식 이름을 입력받아 크롤링
    stock_name = input("주식 이름을 입력하세요: ")
    crawl_stock_info(stock_name)