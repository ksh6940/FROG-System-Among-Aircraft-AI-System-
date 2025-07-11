import pandas as pd
import folium
import re
import os
import math

# 작업 경로 및 저장 경로 설정
content_dir = os.path.join(os.getcwd(), 'data', 'content')
os.makedirs(content_dir, exist_ok=True)
map_path = os.path.join(os.getcwd(), 'web', 'map.html')  # 웹 폴더 내에 저장

# 공역 타입별 색상 정의
type_color = {
    '초경량비행장치 비행공역': 'green',
    '비행금지구역': 'red',
    '비행 제한 구역': 'orange',
    'ALERT 구역': 'purple',
    '비행 위험 구역': 'blue',
    '군작전 공역': 'gray',
}

def dms_to_decimal(dms):
    match = re.match(r'(\d{2,3})(\d{2})(\d{2})([NSWE])', dms)
    if not match:
        return None
    deg, minute, sec, direction = match.groups()
    decimal = int(deg) + int(minute)/60 + int(sec)/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_polygon_pos(pos_str):
    coord_pattern = r'(\d{6}[NS])\s*(\d{7}[EW])'
    matches = re.findall(coord_pattern, pos_str.replace('-', ''))
    coords = [[dms_to_decimal(lat), dms_to_decimal(lon)] for lat, lon in matches]
    return [c for c in coords if None not in c]

# CSV 불러오기
df = pd.read_csv(os.path.join(content_dir, 'airspace_data.csv'))
df_polygons = df[~df['pos'].str.contains('반경', na=False)].copy()

# 최초 기본 중심 좌표
default_location = [36.447675, 127.123221]
default_zoom = 12

# 기본 지도 생성 (폴리곤 그리기)
def create_base_map(location=default_location, zoom_start=default_zoom):
    m = folium.Map(location=location, zoom_start=zoom_start)
    for _, row in df_polygons.iterrows():
        coords = parse_polygon_pos(row['pos'])
        if len(coords) >= 3:
            t = row['type']
            tooltip_html = f"<b>{t}</b><br>{row['name']}<br><span style='color:#888'>{row['height']}</span>"
            folium.Polygon(
                locations=coords,
                color=type_color.get(t, 'blue'),
                fill=True,
                fill_opacity=0.25,
                weight=3,
                dash_array='5, 5',
                popup=folium.Popup(tooltip_html, max_width=300),
                tooltip=tooltip_html
            ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m

def add_marker_and_save(location, popup_text=None, tooltip_text=None, save_path=map_path):
    # create_base_map 함수가 중심 좌표, 줌 레벨로 기본 지도를 생성한다고 가정
    m = create_base_map(location=location, zoom_start=default_zoom)
    
    folium.Marker(
        location=location,
        popup=popup_text,
        tooltip=tooltip_text,
    ).add_to(m)
    
    m.save(save_path)
    print(f"✅ 마커 추가 및 지도 저장 완료: {save_path}")


# 최초 기본 지도 저장
base_map = create_base_map()
base_map.save(map_path)
print(f"✅ 기본 지도 생성 완료: {map_path}")
