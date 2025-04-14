from langchain_openai import ChatOpenAI
from resume_config import answer_examples

def get_ai_response(user_message):
    llm = ChatOpenAI(model='gpt-4o')

    system_prompt = (
        "당신은 채용 전문가입니다. 어떠한 이력서든 한번 보면 그 사람의 이력서를 이해할 수 있습니다."
        "지금부터 이력서의 내용을 전달 받으면, 아래의 형식으로 답변해주세요."
        "이력서 내용이 아니라면, 답변하지 마세요."
        "기본요구사항 : 아르바이트 채용 담당자의 판단을 돕기 위해, 지원자의 정보를 바탕으로 요약문을 생성해야한다."
        "형식 : "
        "1 최대 3문장, 최소 1문장으로 구성해야 한다."
        "2 각 문장은 1문장 단위로 독립되며, 공백 포함 25자 내외로 작성해야 한다. (22자~28자)"
        "3 요약이 불가한 경우에는 다른 문장을 출력하면 안되고 요약불가 판단을 해야한다."
        "내용 : "
        "1 각 문장은 서로 다른 주제를 가져야 한다. (예: 책임감, 적응력, 팀워크, 열정 등)"
        "2 경력에 대한 문장은 반드시 1개 이상 포함해야 한다."
        "3 지원자에 대한 평가는 신중하며 긍정적으로 작성해야 한다."
        "4 부정적인 표현, 비교, 단정적인 평가는 포함하지 않는다. (예: 부족하다, 미흡하다, 추천하지 않는다 등)"
        "어투 : "
        "1. 문장 끝 어미는 모두 '~요' 또는 '~예요' 형태로 마무리한다."
        "2. 해요체를 기준으로 하며, 친절하고, 다정하며, 신뢰감을 주는 말투를 사용한다."
        "3. 지원자의 이름을 지칭하지 않는다."
        "\n\n{context}"
    )

    # Few-shot 예제를 포함한 프롬프트 생성
    examples_prompt = "\n".join(
        f"질문: {example['input']}\n답변: {example['answer']}\n"
        for example in answer_examples
    )

    full_prompt = f"{system_prompt}\n\n예제:\n{examples_prompt}\n\n사용자 질문: {user_message}"

    ai_message = llm.invoke(full_prompt)
    return ai_message.content
