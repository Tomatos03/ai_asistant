import streamlit as st
from openai import OpenAI

from config import API_KEY, BASE_URL, ENABLE_STREAMING, MODEL, REASONING_EFFORT
from models import Role
from session import Session


class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def run(self, session: Session):
        prompt = st.chat_input("请输入你想要聊天的内容")
        self.handle_prompt(prompt, session)

    def handle_prompt(self, prompt, session: Session):
        if not prompt:
            return

        with st.chat_message(Role.USER):
            st.write(prompt)

        st.session_state.messages.append({"role": Role.USER, "content": prompt})

        stream = self.client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            stream=ENABLE_STREAMING,
            reasoning_effort=REASONING_EFFORT,
            extra_body={"thinking": {"type": "enabled"}},
        )

        with st.chat_message(Role.ASSISTANT):
            full_response = st.write_stream(self.stream_data(stream))

        st.session_state.messages.append(
            {
                "role": Role.ASSISTANT,
                "content": full_response,
            }
        )

        session.save()
        st.rerun()

    @staticmethod
    def stream_data(stream):
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
