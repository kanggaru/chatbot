import streamlit as st

from dotenv import load_dotenv
from llm_history import get_ai_response

load_dotenv()


st.set_page_config(page_title="소득세 쳇봇", page_icon="📠")
st.title("📠 소득세 쳇봇")
st.caption("소득세에 관련된 모든것을 답해드립니다!")

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            st.markdown(f'<div style="color:blue;">{message["content"]}</div>', unsafe_allow_html=True)


if user_question := st.chat_input(placeholder="소득세에 관련된 궁금한 내용들을 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})
    with st.spinner("답변을 준비중입니다..."):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            st.write_stream(ai_response)
        st.session_state.message_list.append({"role": "ai", "content": ai_response})
