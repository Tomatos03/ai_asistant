import json
from datetime import datetime

import streamlit as st
from openai import OpenAI
from pandas.compat import os

from config import (
    API_KEY,
    BASE_URL,
    DEFAULT_AI_ASISTANT_NICKNAME,
    DEFAULT_AI_ASISTANT_ROLE,
    ENABLE_STREAMING,
    LAYOUT,
    MENU_ITEMS,
    MODEL,
    PAGE_ICON,
    PAGE_LOGO,
    PAGE_TITLE,
    REASONING_EFFORT,
    SIDEBAR_STATE,
)
from models import Role
from prompts import system_prompt


def stream_data(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

def new_session():
    if not os.path.exists(".dialog_history"):
        os.mkdir(".dialog_history")

    if "session_data" not in st.session_state:
        st.session_state.session_data = {
            "messages": st.session_state.messages,
            "session_date": st.session_state.session_date,
            "nickname": st.session_state.nickname,
            "role": st.session_state.role,
        }

    if len(st.session_state.messages) > 1:
        with open(f".dialog_history/{st.session_state.session_date}.json", "w") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
            reset_session()

def reset_session():
    st.session_state.session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages = [
        {
            "role": Role.SYSTEM,
            "content": system_prompt(
                nickname=st.session_state.nickname, role=st.session_state.role
            ),
        },
    ]
    st.session_state.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.session_data = None

def get_history_session_name():
    file_name_list = []
    file_list = os.listdir(".dialog_history")
    for file_name in file_list:
        if file_name.endswith(".json"):
            file_name_list.append(file_name)
    return file_name_list

def load_session(file_name: str):
    file_path = f".dialog_history/{file_name}"
    with open(file_path, "r") as f:
        st.session_state.messages = json.load(f)
    st.session_state.session_date = file_name.replace(".json", "")

def delete_session(file_name: str):
    file_path = f".dialog_history/{file_name}"
    os.remove(file_path)
    if st.session_state.get("session_date") == file_name.replace(".json", ""):
        reset_session()

def render_siderbar():
    with st.sidebar:
        st.button("新建回话", width="stretch", on_click=new_session)

        st.sidebar.markdown("""
            <style>
            div[data-testid="stSidebar"] button[kind="secondary"] {
                text-align: left;
                border-radius: 6px;
                margin-bottom: 4px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("### 历史会话")
        session_list = get_history_session_name()
        for file_name in session_list:
            label = file_name.replace(".json", "")
            is_active = st.session_state.get("session_date") == label
            col1, col2 = st.sidebar.columns([4, 1])
            col1.button(
                label,
                key=f"session_{file_name}",
                on_click=load_session,
                args=(file_name,),
                type="primary" if is_active else "secondary",
                width="stretch",
            )
            col2.button(
                "🗑",
                key=f"delete_{file_name}",
                on_click=delete_session,
                args=(file_name,),
                width="stretch",
            )

        st.subheader("系统设置")
        st.session_state.nickname = st.text_input(
            "昵称", placeholder="请输入 AI 助手的昵称", value=DEFAULT_AI_ASISTANT_NICKNAME
        )
        st.session_state.role = st.text_input(
            "角色", placeholder="请输入 AI 助手的角色", value=DEFAULT_AI_ASISTANT_ROLE
        )

def load_history_dialog():
    if "messages" not in st.session_state:
        history = get_history_session_name()
        if history:
            latest = sorted(history, reverse=True)[0]
            load_session(latest)
        else:
            st.session_state.messages = []
            st.session_state.session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def render_diglog_history():
    load_history_dialog()
    # --- 渲染历史消息 ---
    for msg in st.session_state.messages:
        if msg["role"] == Role.SYSTEM:
            continue  # system message 不显示
        with st.chat_message(msg["role"]):
            if "content" in msg:
                st.write(msg["content"])

def handle_user_input(prompt):
    if not prompt:
        return

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

    st.session_state.messages.append(
        {
            "role": Role.ASSISTANT,
            "content": full_response,
        }
    )

def render_web_info():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE,
        menu_items=MENU_ITEMS,
    )
    st.title("AI Assistant")
    st.logo(PAGE_LOGO, size="large")


render_web_info()
render_diglog_history()
render_siderbar()
prompt = st.chat_input("请输入你想要聊天的内容")
handle_user_input(prompt)
