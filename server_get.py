# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/introduce', methods=['GET'])
def introduce():
    # 요청에서 name과 age를 가져옴
    name = request.args.get('name')
    age = request.args.get('age')
    
    # 간단한 자기소개 생성
    introduction = f"안녕하세요! 저는 {age}살 {name}입니다."
    
    # JSON 응답 반환
    return jsonify({
        "name": name,
        "age": age,
        "introduction": introduction
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
