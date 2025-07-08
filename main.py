from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os 

# 크롬드라이버 실행
driver = webdriver.Chrome() 
driver.get('https://www.airportal.go.kr/airplane/airspace01.do')
print("웹페이지 로딩 완료")

# 데이터 리스트 초기화
data_list = []
data_list_child1 = []
data_list_child2 = []
data_list_child3 = []
data_list_child4 = []

# selenium 조작
def select_parent_tag():
    full_html = driver.find_element(By.ID, 'wrap')
    body_html = full_html.find_element(By.ID, 'body')
    main_content = body_html.find_element(By.TAG_NAME, 'main')
    div_container_parent = driver.find_element(By.CSS_SELECTOR, 'div.bx_1440.pb_160')
    div_container = div_container_parent.find_element(By.CSS_SELECTOR, 'div.leisure_content.pb_0')
    right_div = div_container.find_element(By.CSS_SELECTOR, 'div.right')
    return right_div

# 각 카테고리별로 데이터 수집
right_div = select_parent_tag()

'''초경량비행장치 비행공역'''
table_container_1 = right_div.find_element(By.CSS_SELECTOR, 'table.table_list.space')
for num in range(1, 33):
    tr = table_container_1.find_element(By.CSS_SELECTOR, f'tr.p{num}')
    td = tr.find_elements(By.TAG_NAME, 'td')
    name = td[1].text
    pos = td[2].text
    height = td[3].text

    airspace_data = {
        'name': name,
        'pos': pos,
        'height': height
    }

    data_list_child1.append(airspace_data)

# 드라이버 종료
driver.quit()
print("드라이버 종료")
driver = webdriver.Chrome() 
driver.get('https://www.airportal.go.kr/airplane/airspace02.do')
print("웹페이지 로딩 완료")

'''비행금지구역'''
right_div = select_parent_tag()
table_container_2 = right_div.find_element(By.CSS_SELECTOR, 'table.table_list.space.inhib.milit_mb')
tbody = table_container_2.find_element(By.TAG_NAME, 'tbody')

tr_list = []
for i in range(len(tbody.find_elements(By.TAG_NAME, 'tr'))):
    tr = tbody.find_element(By.CSS_SELECTOR, f'tr:nth-child({i + 1})')
    td_elements = tr.find_elements(By.TAG_NAME, 'td')
    processed_td = [td.text for td in td_elements]
    print(processed_td) 
    tr_list.append(processed_td)

for i in range(len(tr_list)-1):
    row_data = tr_list[i+1]
    airspace_data = {
        'name': row_data[1],
        'pos': row_data[2],
        'height': row_data[3]
    }
    data_list_child2.append(airspace_data)

# 드라이버 종료
driver.quit()
print("드라이버 종료")
driver = webdriver.Chrome() 
driver.get('https://www.airportal.go.kr/airplane/airspace03.do')
print("웹페이지 로딩 완료")


'''비행제한구역/군훈련공역'''
right_div = select_parent_tag()
print(right_div.text)







''' 데이터 출력 '''
data_child1 = {
    'category': '초경량비행장치 비행공역',
    'data': data_list_child1
}

data_child2 = {
    'category': '비행금지구역',
    'data': data_list_child2
}

# 데이터프레임으로 변환
df = pd.DataFrame(data_child1)
df2 = pd.DataFrame(data_child2)

# merge df
df = pd.concat([df, df2], ignore_index=True)

# 데이터프레임을 CSV로 저장 
df.to_csv('airspace_data.csv', index=False, encoding='utf-8-sig')
