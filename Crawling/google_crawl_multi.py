import time
import re
import pandas as pd
import numpy as np
from loguru import logger
from playwright.sync_api import sync_playwright
import emoji
import time, datetime
from multiprocessing import Pool
from itertools import cycle
from typing import List, Dict
import random
from fake_useragent import UserAgent

base_url = "http://maps.google.com"
max_reviews = 30

def save_to_csv_realtime(data: List[Dict], filename: str, columns: List[str]):
    """
    실시간으로 데이터를 CSV 파일에 저장.
    기존 파일에 데이터를 추가(append)하는 방식.
    """
    df = pd.DataFrame(data, columns=columns)
    # 파일이 없는 경우 헤더 포함, 파일이 있는 경우 헤더 제외
    if not pd.io.common.file_exists(filename):
        df.to_csv(filename, index=False, encoding="utf-8", mode="w")
    else:
        df.to_csv(filename, index=False, encoding="utf-8", mode="a", header=False)

def back_button_click(page):
    # 끝나고 다시 입력상태로 되돌림
    back_button = page.locator("button.yAuNSb.vF7Cdb")
    back_button.click()
    time.sleep(2)

def clean_text(text):
    text = emoji.replace_emoji(text, replace="")
    text = re.sub(r's+', " ", text).strip()
    return text

def save_reviews_to_csv(reviews, filename="google_reviews_lists.csv"):
    df = pd.DataFrame(reviews)
    df.to_csv(filename, index=False, encoding="utf-8")
    logger.info(f"Reviews Saved to {filename}")

def get_user_agents():
    ua = UserAgent()
    user_agents = set()
    num_agents = 6
    while len(user_agents) < num_agents:
        browser = random.choice(["chrome", "firefox", "edge"])
        user_agent = getattr(ua, browser)

        # Windows 또는 Mac 운영 체제 필터링
        if "Windows" in user_agent or "Macintosh" in user_agent:
            user_agents.add(user_agent)

    return list(user_agents)

def get_reviews(page, name, number, process_id):
    # click Review button
    try:
        review_section = page.get_by_role('tab', name="리뷰")
        review_section.click()
        page.wait_for_timeout(3000)
    except Exception as e:
        logger.debug(f"{process_id} process | Review가 없음")
        return None

    try:
        for _ in range(5):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(2000)

        review_elements = page.locator("div[class*='jJc9Ad']")
        logger.info(f"{process_id} process | {review_elements.count()}개의 리뷰를 탐색")
        reviews = []
        i = 0
        for element in review_elements.all()[:max_reviews]:
            reviewer = element.locator("div[class*='d4r55']").inner_text()
            rating = element.locator("span[aria-label]").get_attribute("aria-label")
            
            if element.locator("span[class*='wiI7pd']").count() > 0:
                review_text = element.locator("span[class*='wiI7pd']").inner_text()
            else:
                # logger.info(f"리뷰 텍스트 없음: Reviewer = {reviewer}")
                continue

            more_button = element.locator("button.w8nwRe.kyuRq").nth(0) # 가게 사장 응답도 자세히보기가 있음;; nth(0)으로 예외처리
            if more_button.count() > 0 and more_button.is_visible():
                try:
                    more_button.click()
                    # logger.info(f"더보기 버튼 클릭 성공: Reviewer = {reviewer}")
                    page.wait_for_timeout(2000)  # 클릭 후 잠시 대기
                except Exception as e:
                    logger.warning(f"더보기 버튼 클릭 실패: {e}")
            else:
                # logger.info(f"더보기 버튼 없음: Reviewer = {reviewer}")
                pass


            reviews.append({
                "Number": number,
                "Name": name,
                "Reviewer": clean_text(reviewer),
                "Rating": rating,
                "Review": clean_text(review_text)
            })
    except Exception as e:
        logger.error(f"Error During Scraping on Reviews : {e}")

    return reviews
    
def NoneChecker(number, name, query):
    if name is None:
        with open("none_data_test.txt", "a", encoding="utf-8") as f:  # 'a' 모드로 실시간 추가 저장
            f.write(f"{number},{query}\n")

def get_text_or_none(locator):
    """Locator에서 텍스트를 안전하게 가져옵니다."""
    return locator.inner_text() if locator.count() > 0 else None
    
def get_place_info(page, flag, number, process_id):
    try:
        if not flag:
            infos_elements = page.locator("div.m6QErb.WNBkOb.XiKgde")
        else:
            infos_elements = page.locator("div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
        
        # 가게 이름
        name = get_text_or_none(infos_elements.locator('h1.DUwDvf.lfPIob'))

        # 주소
        address = get_text_or_none(infos_elements.locator('div.Io6YTe.fontBodyMedium.kR99db.fdkmkc').nth(0))

        # 키워드
        # keyword_page_element = infos_elements.locator('div.skqShb.fontBodyMedium')
        keyword = get_text_or_none(infos_elements.locator("button.DkEaL"))

        # 가격 정보
        prices_per_one_element = infos_elements.locator('div.MNVeJb.eXOdV.eF9eN.PnPrlf div').nth(0)
        prices_per_one = get_text_or_none(prices_per_one_element)

        # 평점
        rating_p_element = infos_elements.locator("div.F7nice span.ceNzKf")
        rating = rating_p_element.get_attribute("aria-label") if rating_p_element.count() > 0 else None

    except Exception as e:
        logger.error(f"Error During Scraping on Informations: {e}")
        return None

    # 수집한 정보를 반환
    infos = {
        "Number": number,
        "Name": name,
        "Address": address,
        "Keyword": keyword,
        "Price_per_one": prices_per_one,
        "Rating": rating
    }
    return infos
# TODO: Multiprocessing 코드 작성
def process_place_chunk(process_id, chunk, user_agent, place_info_file, review_file):
    playwright = sync_playwright().start()
    logger.info(f"Using User-Agent: {user_agent}")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(user_agent=user_agent, java_script_enabled=True)
    page = context.new_page()
    page.goto(base_url, wait_until="load")

    place_info_list = []
    review_list = []
    
    for _, row in chunk.iterrows():
        number, place, address = row
        search_query = " ".join([place, address])
        logger.info(f"{process_id} process | Query : {search_query}")

        input_box = page.locator("input[id='searchboxinput']")
        input_box.fill(search_query)
        input_box.press("Enter")

        page.wait_for_timeout(3000)
        time.sleep(2)

        try: 
            xpath_search_result_element = '//div[@role="feed"]'
            page.wait_for_selector(xpath_search_result_element, timeout=3000)
            results_container = page.query_selector(xpath_search_result_element)

            if results_container:
                logger.info(f"{process_id} process | 검색 결과가 여러개인 경우")
                results_container.scroll_into_view_if_needed()
                page.wait_for_selector("a.hfpxzc", timeout=2000)
                first_block = page.locator("a.hfpxzc").nth(0) # 가장 첫번째 선택
                first_block.click()
                
                page.wait_for_load_state("networkidle")
                page.wait_for_selector("h1.DUwDvf.lfPIob", timeout=10000)
                

                # 맨 위 가게정보 데이터 가져오기
                infos = get_place_info(page, flag=True, number=number, process_id=process_id)
                name = infos["Name"]
                logger.info(f"{process_id} process | 실제 검색된 이름 : {name}")
                NoneChecker(number, name, search_query)
                time.sleep(2)
                reviews = get_reviews(page, name, number=number, process_id=process_id)

                # if reviews: # 있든~ 없든~ 일단 extend 하고봐~
                #     review_list.extend(reviews)
                # place_info_list.append(infos) # 장소도 일단.. 저장하고봐....

                if reviews:
                    # 실시간 저장: 리뷰 정보
                    save_to_csv_realtime(reviews, review_file, ["Number", "Name", "Reviewer", "Rating", "Review"])
                
                if infos:
                    # 실시간 저장: 장소 정보
                    save_to_csv_realtime([infos], place_info_file, ["Number", "Name", "Address", "Keyword", "Price_per_one", "Rating"])

            else: #검색된 결과가 엄써용
                logger.info(f"{process_id} process | 검색 결과 container 존재하지 않습니다.")
                back_button_click(page)
                continue


        except Exception as e:
            logger.error(f"Process {process_id} | 바로 검색된 케이스")
            
            # 로딩되기 기다리기
            page.wait_for_load_state("networkidle")
            try:
                page.wait_for_selector("h1.DUwDvf.lfPIob", timeout=10000)
            except Exception as e:
                logger.debug(f"Process {process_id} | 검색 결과 자체가 없음")
                continue
            infos = get_place_info(page, flag=False, number=number, process_id=process_id)
            name = infos["Name"]
            
            logger.info(f"{process_id} process | 실제 검색된 이름 : {name}")
            NoneChecker(number, name, search_query)

            reviews = get_reviews(page, name, number, process_id=process_id)
            # if reviews:
            #     review_list.extend(reviews)
            
            if reviews:
                # 실시간 저장: 리뷰 정보
                save_to_csv_realtime(reviews, review_file, ["Number", "Name", "Reviewer", "Rating", "Review"])
            
            if infos:
                # 실시간 저장: 장소 정보
                save_to_csv_realtime([infos], place_info_file, ["Number", "Name", "Address", "Keyword", "Price_per_one", "Rating"])

            place_info_list.append(infos)

        logger.info(f"{process_id} process | Place info, Review append Complete")
    try:
        browser.close()
        playwright.stop()
    except Exception as e:
        logger.debug(f"{process_id} Process ALL COMPLETE")

    return place_info_list, review_list

if __name__ == "__main__":
    place_list = pd.read_csv("place_list.csv", encoding="utf-8")
    place_list = place_list.iloc[0:66]

    num_processes = 6
    chunk_size = len(place_list) // num_processes
    chunks = [place_list.iloc[i:i + chunk_size] for i in range(0, len(place_list), chunk_size)]

    place_info_file = "place_info_test.csv"
    review_file = "reviews_all_test.csv"

    if len(chunks) > num_processes:
        chunks[-2] = pd.concat([chunks[-2], chunks[-1]])
        chunks = chunks[:-1]


    start = time.time()
    agent = get_user_agents()
    with Pool(processes=num_processes) as pool:
        pool.starmap(
            process_place_chunk, 
            [(i, chunk, agent[i], place_info_file, review_file) for i, chunk in enumerate(chunks)]
        )
    end = time.time()
    duration = datetime.timedelta(seconds=end-start)
    logger.info(f"총 걸린시간 : {duration}")

        





