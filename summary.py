# app.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from resume import get_ai_response

load_dotenv()

app = Flask(__name__)

@app.route('/introduce', methods=['GET'])
def introduce():
    # 요청에서 name과 age를 가져옴
    user_question = request.args.get('resume')
    ai_response = get_ai_response(user_question)
    
    # JSON 응답 반환
    return jsonify({
        "result": ai_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
