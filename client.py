import os

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import streamlit as st
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")

def stream_data(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content": "你是一个有用的助手，协助用户解答问题。"}
]

if "messages" not in st.session_state:
    st.session_state.messages = messages

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)

st.title("AI Assistant")
st.logo("resource/rebot.png", size="large")

# --- 渲染历史消息 ---
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue  # system message 不显示
    with st.chat_message(msg["role"]):
        if "content" in msg:
            st.write(msg["content"])

prompt = st.chat_input("请输入你想要聊天的内容")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    stream = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=st.session_state.messages,
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )

    with st.chat_message("assistant"):
        full_response = st.write_stream(stream_data(stream))

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
    })
