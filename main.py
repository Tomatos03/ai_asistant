import streamlit as st

from asistant import AIAssistant
from renderer import Renderer
from session import Session

if "session" not in st.session_state:
    st.session_state.session = Session()

if "assistant" not in st.session_state:
    st.session_state.assistant = AIAssistant()

session = st.session_state.session
assistant = st.session_state.assistant
session.setup()

renderer = Renderer(session)
renderer.render_page()
assistant.run(session)
