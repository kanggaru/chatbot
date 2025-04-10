import streamlit as st

from dotenv import load_dotenv
from llm_with import get_ai_response

load_dotenv()


st.set_page_config(page_title="알바몬 쳇봇", page_icon="🐱")
st.title("🐱 알바몬 쳇봇")
st.caption("알바몬에서 테스트중인 쳇봇입니다.")

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])
       


if user_question := st.chat_input(placeholder="이력서의 내용을 입력해주세요."):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})
    with st.spinner("답변을 준비중입니다..."):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
            st.session_state.message_list.append({"role": "ai", "content": ai_message})
