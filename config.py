import os

from streamlit.commands.page_config import MenuItems

# DeepSeek API
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# Streamlit 页面配置
PAGE_TITLE = "Ex-stream-ly Cool App"
PAGE_ICON = "🧊"
PAGE_LOGO = "resource/rebot.png"
SIDEBAR_STATE = "expanded"
LAYOUT = "wide"
MENU_ITEMS: MenuItems = {
    "Get Help": "https://www.extremelycoolapp.com/help",
    "Report a bug": "https://www.extremelycoolapp.com/bug",
    "About": "# This is a header. This is an *extremely* cool app!",
}
REASONING_EFFORT="high"
ENABLE_STREAMING = True
