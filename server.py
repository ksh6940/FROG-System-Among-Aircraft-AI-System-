from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
import os
import mapping  # 별도 모듈에 folium 지도 관리

app = Flask(__name__, template_folder='web')

# 메인 페이지
@app.route('/')
def index():
    return render_template('main.html', titles='항공네비')

# web 폴더 내 정적 파일 서빙 (map.html 포함)
@app.route('/web/<path:filename>')
def web_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'web'), filename)

# source 폴더 내 정적 파일 서빙 (sidebar.png 등)
@app.route('/source/<path:filename>')
def source_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'web', 'source'), filename)

# 최신 map.html 직접 반환 (명시적 라우트)
@app.route('/map.html')
def map_html():
    map_path = os.path.join(app.root_path, 'data', 'content', 'map.html')
    return send_from_directory(os.path.dirname(map_path), os.path.basename(map_path))

# 위치 데이터 받기 API
@app.route('/api/location', methods=['POST'])
def receive_location():
    data = request.get_json(force=True)
    place_name = data.get('place_name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    print(f"받은 장소명: {place_name}, 위도: {latitude}, 경도: {longitude}")

    mapping.add_marker_and_save((latitude, longitude), popup_text=place_name, tooltip_text=place_name)

    # 새 지도 파일이 생성되었음을 클라이언트에 알림
    return jsonify({
        'success': True,
        'message': '지도 업데이트 완료',
        'reloadMap': True  # 클라이언트가 iframe 새로고침 할 신호
    })


if __name__ == '__main__':
    app.run(debug=True)
