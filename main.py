import streamlit as st

from asistant import AIAssistant
from config import (
    DEFAULT_AI_ASISTANT_NICKNAME,
    DEFAULT_AI_ASISTANT_ROLE,
    LAYOUT,
    MENU_ITEMS,
    PAGE_ICON,
    PAGE_LOGO,
    PAGE_TITLE,
    SIDEBAR_STATE,
)
from models import Role


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

def render_siderbar(assistant: AIAssistant):
    with st.sidebar:
        st.button("新建回话", width="stretch", on_click=assistant.new_session)

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
        session_list = assistant.get_history_session_names()
        for file_name in session_list:
            label = file_name.replace(".json", "")
            is_active = st.session_state.get("session_date") == label
            col1, col2 = st.sidebar.columns([4, 1])
            col1.button(
                label,
                key=f"session_{file_name}",
                on_click=assistant.load_session,
                args=(file_name,),
                type="primary" if is_active else "secondary",
                width="stretch",
            )
            col2.button(
                "🗑",
                key=f"delete_{file_name}",
                on_click=assistant.delete_session,
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

def render_diglog_history(assistant: AIAssistant):
    for msg in assistant.get_messages():
        if msg["role"] == Role.SYSTEM:
            continue
        with st.chat_message(msg["role"]):
            if "content" in msg:
                st.write(msg["content"])


if "assistant" not in st.session_state:
    st.session_state.assistant = AIAssistant()

assistant = st.session_state.assistant
assistant.init_session()

render_web_info()
render_diglog_history(assistant)
render_siderbar(assistant)
assistant.run()
