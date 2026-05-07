import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

from config import API_KEY, BASE_URL, ENABLE_STREAMING, HISTORY_DIR, MODEL, REASONING_EFFORT
from models import Role
from prompts import system_prompt


class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def init_session(self):
        if not os.path.exists(HISTORY_DIR):
            os.mkdir(HISTORY_DIR)

        if "messages" not in st.session_state:
            history = self.get_history_session_names()
            if history:
                latest = sorted(history, reverse=True)[0]
                self.load_session(latest)
            else:
                self.reset_session()

    def reset_session(self):
        st.session_state.session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages = [
            {
                "role": Role.SYSTEM,
                "content": system_prompt(
                    nickname=st.session_state.nickname, role=st.session_state.role
                ),
            },
        ]
        st.session_state.session_data = None

    def new_session(self):
        if "session_data" not in st.session_state:
            st.session_state.session_data = {
                "messages": st.session_state.messages,
                "session_date": st.session_state.session_date,
                "nickname": st.session_state.nickname,
                "role": st.session_state.role,
            }

        if len(st.session_state.messages) > 1:
            with open(f"{HISTORY_DIR}/{st.session_state.session_date}.json", "w") as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

        self.reset_session()

    def load_session(self, file_name: str):
        file_path = f"{HISTORY_DIR}/{file_name}"
        with open(file_path, "r") as f:
            st.session_state.messages = json.load(f)
        st.session_state.session_date = file_name.replace(".json", "")

    def delete_session(self, file_name: str):
        file_path = f"{HISTORY_DIR}/{file_name}"
        os.remove(file_path)
        if st.session_state.get("session_date") == file_name.replace(".json", ""):
            history = self.get_history_session_names()
            if history:
                self.load_session(sorted(history, reverse=True)[0])
            else:
                self.reset_session()

    def get_history_session_names(self):
        if not os.path.exists(HISTORY_DIR):
            return []
        return [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]

    def get_messages(self):
        return st.session_state.messages

    def run(self):
        prompt = st.chat_input("请输入你想要聊天的内容")
        self.handle_prompt(prompt)

    def handle_prompt(self, prompt):
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

        with open(f"{HISTORY_DIR}/{st.session_state.session_date}.json", "w") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.rerun()

    @staticmethod
    def stream_data(stream):
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
