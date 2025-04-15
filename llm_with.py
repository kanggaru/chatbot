from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from resume_config import answer_examples

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_retriever():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'tax-index'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
    retriever = database.as_retriever(search_kwargs={'k': 4})
    return retriever

def get_history_retriever():
    llm = get_llm()
    retriever = get_retriever()
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever


def get_llm(model='gpt-4o'):
    llm = ChatOpenAI(model=model)
    return llm


def get_dictionary_chain():
    dictionary = ["사람을 나타내는 표현 -> 지원자"]
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(f"""
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다.
        그런 경우에는 질문만 리턴해주세요
        사전: {dictionary}
        
        질문: {{question}}
    """)

    dictionary_chain = prompt | llm | StrOutputParser()
    
    return dictionary_chain


def get_rag_chain():
    llm = get_llm()
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
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
        "\n\n"
        "{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = get_history_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')
    
    return conversational_rag_chain


def get_ai_response(user_message):
    dictionary_chain = get_dictionary_chain()
    rag_chain = get_rag_chain()
    tax_chain = {"input": dictionary_chain} | rag_chain
    ai_response = tax_chain.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "joeyTest"}
        },
    )

    return ai_response