# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/post', methods=['POST'])
def handle_post():
    # JSON 데이터를 받음
    data = request.get_json()
    print(f"Received data: {data}")
    
    # 응답 반환
    return jsonify({
        "message": "데이터를 성공적으로 받았습니다!",
        "received_data": data
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
