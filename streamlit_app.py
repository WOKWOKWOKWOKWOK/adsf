import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(
    page_title="Utopia Web Browser",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark UI Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton > button { width: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# State initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = [
        {"name": "DuckDuckGo HTML", "url": "https://html.duckduckgo.com/html/"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Main_Page"},
        {"name": "Hacker News", "url": "https://news.ycombinator.com"}
    ]
if "current_url" not in st.session_state:
    st.session_state.current_url = "https://html.duckduckgo.com/html/"

def parse_input(user_input: str) -> str:
    user_input = user_input.strip()
    if not user_input:
        return "https://html.duckduckgo.com/html/"
    if user_input.startswith(("http://", "https://")):
        return user_input
    if "." in user_input and " " not in user_input:
        return f"https://{user_input}"
    
    encoded_query = urllib.parse.quote(user_input)
    return f"https://html.duckduckgo.com/html/?q={encoded_query}"

def fetch_and_clean_html(target_url: str) -> str:
    """Fetches web content, injects base URL, and strips frame restrictions."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove meta tags that enforce iframe restrictions
        for meta in soup.find_all("meta"):
            if meta.get("http-equiv", "").lower() in ["x-frame-options", "content-security-policy"]:
                meta.decompose()
        
        # Inject <base> tag so relative styles, images, and links resolve correctly
        base_tag = soup.new_tag("base", href=target_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            head_tag = soup.new_tag("head")
            head_tag.insert(0, base_tag)
            if soup.html:
                soup.html.insert(0, head_tag)

        return str(soup)

    except Exception as err:
        return f"""
        <div style="color: #ff6b6b; padding: 25px; background: #1a1c23; border-radius: 8px; font-family: sans-serif;">
            <h2>⚠️ Website Blocked or Unreachable</h2>
            <p><b>URL:</b> <code>{target_url}</code></p>
            <p><b>Reason:</b> {str(err)}</p>
            <p>Some major platforms (e.g., Google, YouTube) use bot detection or strict security policies that reject simple proxy scripts.</p>
        </div>
        """

# Sidebar Navigation
st.sidebar.title("🌐 Utopia Control")

st.sidebar.subheader("⭐ Bookmarks")
for bm in st.session_state.bookmarks:
    if st.sidebar.button(f"📌 {bm['name']}", key=f"bm_{bm['url']}"):
        st.session_state.current_url = bm["url"]
        st.rerun()

st.sidebar.subheader("📜 History")
for idx, item in enumerate(reversed(st.session_state.history[-5:])):
    if st.sidebar.button(f"🔗 {item[:25]}...", key=f"h_{idx}"):
        st.session_state.current_url = item
        st.rerun()

# Top Address Bar
st.title("Utopia Browser")
c1, c2, c3 = st.columns([6, 2, 2])

with c1:
    url_input = st.text_input("URL", value=st.session_state.current_url, label_visibility="collapsed")

with c2:
    if st.button("Go", use_container_width=True):
        final_url = parse_input(url_input)
        st.session_state.current_url = final_url
        if final_url not in st.session_state.history:
            st.session_state.history.append(final_url)
        st.rerun()

with c3:
    mode = st.selectbox("Mode", ["Proxied HTML", "Direct Iframe"], label_visibility="collapsed")

st.divider()

# Rendering engine selection
active_url = st.session_state.current_url

if mode == "Proxied HTML":
    html_data = fetch_and_clean_html(active_url)
    st.components.v1.html(html_data, height=800, scrolling=True)
else:
    st.components.v1.iframe(src=active_url, height=800, scrolling=True)
