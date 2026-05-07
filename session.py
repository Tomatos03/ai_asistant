import json
import os
from datetime import datetime

import streamlit as st

from config import HISTORY_DIR
from models import Role
from prompts import system_prompt


class Session:
    def setup(self):
        if not os.path.exists(HISTORY_DIR):
            os.mkdir(HISTORY_DIR)

        if "messages" not in st.session_state:
            history = self.get_history_names()
            if history:
                self.load(sorted(history, reverse=True)[0])
            else:
                self.reset()

    def reset(self):
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

    def new(self):
        if "session_data" not in st.session_state:
            st.session_state.session_data = {
                "messages": st.session_state.messages,
                "session_date": st.session_state.session_date,
                "nickname": st.session_state.nickname,
                "role": st.session_state.role,
            }

        self.save()
        self.reset()

    def load(self, file_name: str):
        file_path = f"{HISTORY_DIR}/{file_name}"
        with open(file_path, "r") as f:
            st.session_state.messages = json.load(f)
        st.session_state.session_date = file_name.replace(".json", "")

    def delete(self, file_name: str):
        file_path = f"{HISTORY_DIR}/{file_name}"
        os.remove(file_path)
        if st.session_state.get("session_date") == file_name.replace(".json", ""):
            history = self.get_history_names()
            if history:
                self.load(sorted(history, reverse=True)[0])
            else:
                self.reset()

    def save(self):
        if len(st.session_state.messages) > 1:
            with open(f"{HISTORY_DIR}/{st.session_state.session_date}.json", "w") as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

    def get_history_names(self):
        if not os.path.exists(HISTORY_DIR):
            return []
        return [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]

    def get_messages(self):
        return st.session_state.messages
