from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re



file_path = '일반음식점.xlsx' #검색할 종로구의 업체명 리스트 불러 오기
df = pd.read_excel(file_path)

#중간부터 시작 코드 : 수집 중간에 멈추면 이 코드로 다시 실행
# start_index = df[df['번호'] == 6595].index[0]
# selected_columns = df.loc[start_index:, ['번호', '사업장명', '도로명전체주소']]

selected_columns = df[['번호','사업장명', '도로명전체주소']]

for index, row in selected_columns.iterrows(): # 업체를 하나씩 검색 시작


    url = 'https://map.kakao.com/' # 카카오맵 주소
    driver = webdriver.Chrome() #크롬 드라이버 경로
    driver.get(url) # 크롬으로 URL 접속
    searchloc = f"{row['사업장명']}"  #검색키워드
    num = row['번호'] # 가져온 리스트에서
    target_adds = f"{row['도로명전체주소']}" #검색한 결과의 장소가 맞는지 확인을 위한 정답 값
    start_index = target_adds.find('종로구') # 비교시 "종로구 ~길 ~," 이부분만 사용
    last_index =  target_adds.find(',')
    if start_index != -1:
        target_adds = target_adds[start_index : last_index].strip() # 검색결과와 비교에 사용될 주소 부분
    
    
    
    
    search_area = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]') #검색하는 부분 설정
    search_area.send_keys(searchloc) #검색어 입력
    search_area.send_keys(Keys.ENTER) #검색 버튼 클릭. 엔터
    time.sleep(2) # 2초 쉬기

    driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER) #장소 탭으로 이동 (카카오맵 특징)


    def detail_store_info(num, domain, name, keword, degree, addr) : 
        time.sleep(1)
        temp2 = []
        temp = []
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        operation_info = []
        open_time_list = soup.select('.displayPeriodList')
        more_button = driver.find_elements(By.CSS_SELECTOR, 'a.link_more')
        for period in open_time_list:
            t = period.select_one('.tit_operation').text.strip()  # 제목 가져오기 (예: "영업시간", "공휴일")
            items = period.select('.list_operation > li')  # 리스트 아이템 가져오기
            for item in items:
                time_info = item.text.strip()  # 각 리스트 아이템의 텍스트 가져오기
                operation_info.append(f"{t}: {time_info} ")  # 제목과 함께 저장
        operation_info_str = " ".join(operation_info)
        operation_info_str = re.sub(r'\s+', ' ', operation_info_str)
        start_index = operation_info_str.find('더보기')
        if start_index != -1:
            operation_info_str = operation_info_str[start_index + len('더보기'):].strip()
        temp.append([num, domain, name, addr, keword, degree, operation_info_str])
        while True:
                # 현재 리뷰 리스트 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                review_lists = soup.select('.list_evaluation > li')

                div_element = soup.find('div', class_='evaluation_review')
                element = div_element.find('a', class_='link_more link_unfold')
                # 리뷰 개수 확인
                if len(review_lists) >= 30 or element :
                    break


                element = div_element.find('a', class_='link_more')
                if element:
                    try:
                        # 더보기 버튼 클릭
                        more_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.evaluation_review > a.link_more'))
                        )

                        more_button.click()
                        
                        time.sleep(1)  # 버튼 클릭 후 대기
                    except Exception as e:
                        print(f"[WARNING] 더보기 버튼 클릭 중 오류 발생: {e}")
                        break
                else : break
        for review in review_lists:
            comment = review.select_one('.txt_comment > span').text.strip()         
            #print(f"[INFO] {name} | {keword} | {degree} | {addr} | {operation_info_filtered_str} | {comment} ")
            temp2.append([num, domain, name ,comment])
        #store_data.append(temp) #폐기
        
        return (temp, temp2)
            

    def getInfoCrawler(num) :

        time.sleep(1) #각 페이지 마다 잠시 휴식
        store_data_info = []
        store_data_review = []
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser') #정보 id 찾기 준비
        stores = soup.select('.placelist > .PlaceItem') #리스트로 가게들 전체 가져오기
        #store = soup.select_one('placelist > .PlaceItem ') #최상단의 가게 가져오기

        for idx, store in enumerate(stores) :
            
            if target_adds in store.select_one('.info_item > .addr').text.splitlines()[1] :
                try :             
                    domain = "kakao"                                                        #도메인
                    name = store.select_one('.head_item > .tit_name > .link_name').text #상호명
                    keword = store.select_one('.head_item > .subcategory').text         #키워드
                    degree = store.select_one('.rating > .score > .num').text           #가게평점
                    addr = store.select_one('.info_item > .addr').text.splitlines()[1]  #주소
                    
                    detail_btn = driver.find_element(By.XPATH, f'//*[@id="info.search.place.list"]/li[{idx + 1}]/div[5]/div[4]/a[1]') #"상세페이지" 추적
                    detail_btn.send_keys(Keys.ENTER)
                    driver.switch_to.window(driver.window_handles[-1])  # 크롬 새 탭으로 전환
                    
                    
                    numOfReview = store.select_one('.rating > .score > .numberofscore').text
                    numOfReview = int(numOfReview[:-1])
                    
                    if numOfReview != 0 :
                        store_data_info, store_data_review = detail_store_info(num, domain, name, keword, degree, addr)

                except Exception as e:
                    print(f"[ERROR] Failed to process store: {e}")
                    driver.switch_to.window(driver.window_handles[0])  # 복구

        if len(store_data_info) != 0 and len(store_data_review) != 0 : 
            file_name = 'kakao_place_info_list.csv'
            if not os.path.exists(file_name):
                with open(file_name, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['번호', '도메인', '상호명', '주소', '키워드', '가게평점', '영업시간'])
                    for store in store_data_info:  # store_data의 각 항목을 한 줄씩 저장
                        writer.writerow(store)
            else:
                with open(file_name, 'a', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    for store in store_data_info: 
                        writer.writerow(store)
            
            file_name2 = 'kakao_reivew_lists.csv'
            if not os.path.exists(file_name2):
                with open(file_name2, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['번호', '도메인', '상호명', '리뷰'])
                    for store in store_data_review:  # store_data의 각 항목을 한 줄씩 저장
                        writer.writerow(store)
            else:
                with open(file_name2, 'a', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    for store in store_data_review: 
                        writer.writerow(store)
        #print(f"[INFO] {name} | {keword} | {degree} | {addr} ")
        



    getInfoCrawler(num) #첫 페이지 크롤링
    print("**크롤링 완료**")
    driver.quit()
