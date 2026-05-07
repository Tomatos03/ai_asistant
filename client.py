from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import streamlit as st
from openai import OpenAI

from config import API_KEY, BASE_URL, ENABLE_STREAMING, LAYOUT, MODEL, PAGE_TITLE, PAGE_ICON, PAGE_LOGO, REASONING_EFFORT, SIDEBAR_STATE, MENU_ITEMS
from models import Role
from prompts import system_prompt

def stream_data(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

messages: list[ChatCompletionMessageParam] = [
    {"role": Role.SYSTEM, "content": system_prompt(nickname = "小智", role = "AI 助手")},
]

if "messages" not in st.session_state:
    st.session_state.messages = messages

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
    menu_items=MENU_ITEMS,
)

st.title("AI Assistant")
st.logo(PAGE_LOGO, size="large")

# --- 渲染历史消息 ---
for msg in st.session_state.messages:
    if msg["role"] == Role.SYSTEM:
        continue  # system message 不显示
    with st.chat_message(msg["role"]):
        if "content" in msg:
            st.write(msg["content"])

prompt = st.chat_input("请输入你想要聊天的内容")

if prompt:
    with st.chat_message(Role.USER):
        st.write(prompt)

    st.session_state.messages.append({"role": Role.USER, "content": prompt})

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    stream = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        stream=ENABLE_STREAMING,
        reasoning_effort=REASONING_EFFORT,
        extra_body={"thinking": {"type": "enabled"}},
    )

    with st.chat_message(Role.ASSISTANT):
        full_response = st.write_stream(stream_data(stream))

    st.session_state.messages.append({
        "role": Role.ASSISTANT,
        "content": full_response,
    })
