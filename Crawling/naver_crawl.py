from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from time import sleep
import urllib.parse
import pandas as pd
from tqdm import tqdm
import os


def random_sleep(min_seconds=2, max_seconds=3):
    sleep_time = random.uniform(min_seconds, max_seconds)
    sleep(sleep_time)


def save_data(new_data, path):
    new_df = pd.DataFrame(new_data)
    
    if os.path.exists(path):
        existing_df = pd.read_csv(path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(path, index=False, escapechar="\\")
    else:
        new_df.to_csv(path, index=False)


def get_storename_address_from_CSV(idx):
    food_name = food_list.loc[idx, "사업장명"]

    food_full_address = food_list.loc[idx, '도로명전체주소']
    if pd.isna(food_full_address) :
        food_full_address = food_list.loc[idx, '소재지전체주소']

    food_address = " ".join(food_full_address.split(",")[0].split()[1:])

    return food_name, food_address, food_full_address


def setup_webdriver():
    # 웹 드라이버 설정
    options = webdriver.ChromeOptions()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("window-size=1200,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 서버용 
    options.add_argument("--headless")  # Headless 모드로 실행
    options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (리소스 제한 문제 방지)
    options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화


    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })

    url = "https://map.naver.com/p?c=15.00,0,0,0,dh"
    driver.get(url)
    
    return driver


def enter_query_load_page(driver, search_query):
    # URL 접근 및 iframe 전환
    search_box = driver.find_element(By.CSS_SELECTOR, "div.input_box>input.input_search")
    search_box.send_keys(Keys.CONTROL, 'a')  # 모든 텍스트 선택
    search_box.send_keys(Keys.DELETE)       # 선택된 텍스트 삭제
    search_box.clear()
    search_box.clear()
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.ENTER)
    random_sleep()

    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "entryIframe"))
        )
        driver.switch_to.frame(iframe)
        return True
    except Exception as e:
        return False


def check_no_results(driver):
    # 검색 결과 없는 경우 확인
    try:
        no_result_message = driver.find_element(By.CLASS_NAME, "FYVSc").text
        if "조건에 맞는 업체가 없습니다." in no_result_message:
            return True
    except Exception:
        pass  # 검색 결과가 있는 경우
    return False


def scrape_info(driver):
    # 가게 정보를 크롤링
    # 각 가게마다 가지고 있는 여부가 달라 모든 경우에 대해 try, ecept 처리리
    store_name, category, rating, address, business_hours = None, None, None, None, None  

    try:
        store_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "GHAhO"))
        ).text
    except:
        pass
    
    # 카테고리 가져오기
    try:
        category = driver.find_element(By.CLASS_NAME, "lnJFt").text
    except:
        pass
    
    # 별점 가져오기기
    try:
        # 별점이 포함된 부모 div를 먼저 찾기
        rating_parent = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='dAsGb']"))
        )
        # 부모 div 내에서 점수만 추출
        rating_element = rating_parent.find_element(By.XPATH, ".//span[@class='PXMot LXIwF']")
        rating = rating_element.text.strip().split()[1]
    except:
        pass
    
    # 도로명 주소 가져오기기
    try:
        address_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='LDgIH']"))
        )
        address = address_element.text.strip()
    except:
        pass
    
    # 영업 시간
    try:
        driver.find_element(By.XPATH, '//div[@class="y6tNq"]//span').click()
        random_sleep()
        parent_element = driver.find_element(By.XPATH, '//a[@class="gKP9i RMgN0"]')
        child_elements = parent_element.find_elements(By.XPATH, './*[@class="w9QyJ" or @class="w9QyJ undefined"]')
        
        business_hours = ""
        for child in child_elements:
            span_elements = child.find_elements(By.XPATH, './/span[@class="A_cdD"]')
            for span in span_elements:
                business_hours += (" " + span.text)
    except:
        pass

    return store_name, category, rating, address, business_hours


def scrape_reviews(driver):
    reviews = []
    # 리뷰 버튼 클릭
    try:
        review_tab = driver.find_element(By.XPATH, '//span[@class="veBoZ" and text()="리뷰"]')
        review_tab.click()
        random_sleep()   
    except:
        pass      
    # 더보기 누르기(리뷰가 적은 곳은 '더보기' 버튼이 없어서 예외 처리 해야함)
    try:
        more_tab = driver.find_element(By.XPATH, '//span[@class="TeItc" and text()="더보기"]')
        more_tab.click()
        random_sleep()
    except:
        pass
    try:
        more_tab.click()
        random_sleep()
    except:
        pass
    
    try:
        # 모든 리뷰를 포함한 <div> 요소들 찾기
        review_elements = driver.find_elements(By.CLASS_NAME, "pui__vn15t2")
        for element in review_elements:
            review_text = element.find_element(By.TAG_NAME, "a").text
            reviews.append(review_text)
    except :
        pass

    return reviews



if __name__ == "__main__":
    food_list = pd.read_excel('restaurant list data')

    # save path
    FOOD_INFO_PATH = "food_info.csv"
    REVIEW_PATH = "review.csv"

    # for meta information
    index_list = []
    store_name_list = []
    category_list = []
    rating_list = []
    address_list = []
    business_hours_list = []

    # for review data
    review_index_list = []
    review_list = []

    driver = setup_webdriver()
    # 메인 루프
    for i in tqdm(range(2701, 2790)):
        store_name, query_address, _ = get_storename_address_from_CSV(i)

        search_query = store_name + " " + query_address
        enter_query_load_page(driver, search_query)

        index_list.append(i+1)
        if check_no_results(driver):
            # 검색 결과 없는 경우 None으로 저장하고 다음 루프로
            store_name_list.append(None)
            category_list.append(None)
            rating_list.append(None)
            address_list.append(None)
            business_hours_list.append(None)
            
        else:
            # 검색 결과 있는 경우 정보 스크래핑
            store_name, category, rating, address, business_hours = scrape_info(driver)
            reviews = scrape_reviews(driver)

            store_name_list.append(store_name)
            category_list.append(category)
            rating_list.append(rating)
            address_list.append(address)
            business_hours_list.append(business_hours)

            review_index_list.extend([i+1] * len(reviews))
            review_list.extend(reviews)

        driver.switch_to.default_content()

        if i % 10 == 0:
            new_info_data = {
                'id' : index_list,
                'domain' : ['naver'] * len(index_list),
                'store_name' : store_name_list,
                'category' : category_list,
                'rating' : rating_list,
                'address' : address_list,
                'business_hours' : business_hours_list
            }
            save_data(new_info_data, FOOD_INFO_PATH)
            new_review_data = {
                'id' : review_index_list,
                'review' : review_list
            }
            save_data(new_review_data, REVIEW_PATH)

            index_list = []
            store_name_list = []
            category_list = []
            rating_list = []
            address_list = []
            business_hours_list = []

            review_index_list = []
            review_list = []
            print(f"{i}번째까지 저장되었습니다.")

    driver.quit()
