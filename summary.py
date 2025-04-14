# app.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from resume import get_ai_response, get_prompt, count_tokens, get_model
load_dotenv()
import time

app = Flask(__name__)

@app.route('/introduce', methods=['GET'])
def introduce():
    # 시작 시간 기록
    start_time = time.time()

    # 요청에서 name과 age를 가져옴
    user_question = request.args.get('resume')
    prompt = get_prompt(user_question)
    
    ai_response = get_ai_response(prompt)
    
    # 끝 시간 기록 및 실행 시간 계산
    end_time = time.time()
    execution_time = end_time - start_time

    # 토큰 계산
    question_tokens = count_tokens(prompt)
    answer_tokens = count_tokens(ai_response)

    # JSON 응답 반환
    return jsonify({
        "result": ai_response,
        "question_tokens": question_tokens,
        "answer_tokens": answer_tokens,
        "model": get_model(),
        "execution_time": f"{execution_time:.4f} seconds"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
