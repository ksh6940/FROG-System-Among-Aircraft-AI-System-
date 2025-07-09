import pandas as pd
import folium
import re
import os
import math
import numpy as np


# 작업 디렉토리 및 지도 HTML 저장 경로 설정
content_dir = os.path.join(os.getcwd(), 'content')
os.makedirs(content_dir, exist_ok=True)
map_path = os.path.join(content_dir, 'map.html')

# 중심 좌표 기준 folium 지도 생성
base_map = folium.Map(location=[36.447675, 127.123221], zoom_start=12)

# 각 공역 타입별 색상 정의
type_color = {
    '초경량비행장치 비행공역': 'green',
    '비행금지구역': 'red',
    '비행 제한 구역': 'orange',
    'ALERT 구역': 'purple',
    '비행 위험 구역': 'blue',
    '군작전 공역': 'gray',
}

# DMS (도분초 + 방향) 문자열을 10진수 위경도로 변환
def dms_to_decimal(dms):
    match = re.match(r'(\d{2,3})(\d{2})(\d{2})([NSWE])', dms)
    if not match:
        return None
    deg, minute, sec, direction = match.groups()
    decimal = int(deg) + int(minute)/60 + int(sec)/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

# "반경" 기반 pos 필드에서 중심 좌표와 반경(km) 추출
def parse_radius_pos(text):
    coord_match = re.search(r'(\d+[NS])\s*(\d+[EW])', text.replace(' ', ''))
    lat, lon = coord_match.groups() if coord_match else (None, None)
    radius_match = re.search(r'반경\s*([\d.]+)\s*KM', text)
    radius_km = float(radius_match.group(1)) if radius_match else None
    return lat, lon, radius_km

# 다각형 영역 pos 필드에서 좌표 배열로 변환
def parse_polygon_pos(pos_str):
    coord_pattern = r'(\d{6}[NS])\s*(\d{7}[EW])'
    matches = re.findall(coord_pattern, pos_str.replace('-', ''))
    coords = [[dms_to_decimal(lat), dms_to_decimal(lon)] for lat, lon in matches]
    return [c for c in coords if None not in c]

# 중심 좌표(lat, lon)와 반경으로 원형 polygon 좌표 생성
def make_circle_polygon(lat, lon, radius_km, num_points=36):
    points = []
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    d = radius_km / 6371.0  # 지구 반지름(km)
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        lat_point = math.asin(math.sin(lat_rad) * math.cos(d) +
                              math.cos(lat_rad) * math.sin(d) * math.cos(angle))
        lon_point = lon_rad + math.atan2(math.sin(angle) * math.sin(d) * math.cos(lat_rad),
                                         math.cos(d) - math.sin(lat_rad) * math.sin(lat_point))
        points.append([math.degrees(lat_point), math.degrees(lon_point)])
    return points

# CSV 불러오기 및 영역 분류
df = pd.read_csv(os.path.join(content_dir, 'airspace_data.csv'))
df_radius = df[df['pos'].str.contains('반경', na=False)].copy()
df_polygons = df[~df['pos'].str.contains('반경', na=False)].copy()

# 반경 기반 구역 파싱
parsed_radius = []
for _, row in df_radius.iterrows():
    lat, lon, radius_km = parse_radius_pos(row['pos'])
    parsed_radius.append({
        'lat': lat, 'lon': lon, 'radius_km': radius_km,
        'type': row['type'], 'name': row['name'], 'height': row['height']
    })

# 지도에 시각화할 feature group 정의
feature_groups = {t: folium.FeatureGroup(name=t, show=True) for t in type_color.keys()}

# 다각형 구역 시각화
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
        ).add_to(feature_groups[t])

# 원형 구역 시각화
for item in parsed_radius:
    if all([item['lat'], item['lon'], item['radius_km']]):
        lat = dms_to_decimal(item['lat'])
        lon = dms_to_decimal(item['lon'])
        if lat and lon:
            t = item['type']
            tooltip_html = f"<b>{t}</b><br>{item['name']}<br>{item['height']}<br><span style='color:#c00'>반경 {item['radius_km']} km</span>"
            circle_coords = make_circle_polygon(lat, lon, item['radius_km'])
            folium.Polygon(
                locations=circle_coords,
                color=type_color.get(t, 'red'),
                fill=True,
                fill_opacity=0.3,
                weight=3,
                dash_array='5, 5',
                popup=folium.Popup(tooltip_html, max_width=300),
                tooltip=tooltip_html
            ).add_to(feature_groups[t])

# 지도에 feature group 및 레이어 컨트롤 추가
for fg in feature_groups.values():
    base_map.add_child(fg)
folium.LayerControl(collapsed=False).add_to(base_map)

base_map.save(map_path)
print(f"✅ 구역이 지도에 성공적으로 시각화되었습니다.\n👉 파일 경로: {map_path}")
