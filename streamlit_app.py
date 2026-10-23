import urllib.parse
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Set Streamlit Page Layout
st.set_page_config(
    page_title="Utopia Web Browser",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Utopia Dark Theme Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton > button {
        width: 100%;
        border-radius: 6px;
    }
    .url-bar {
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = [
        {"name": "DuckDuckGo", "url": "https://html.duckduckgo.com"},
        {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
        {"name": "GitHub", "url": "https://github.com"}
    ]
if "current_url" not in st.session_state:
    st.session_state.current_url = "https://html.duckduckgo.com"

def parse_input(user_input: str) -> str:
    """Converts search terms into a DuckDuckGo query or formats valid URLs."""
    user_input = user_input.strip()
    if not user_input:
        return "https://html.duckduckgo.com"
    if user_input.startswith(("http://", "https://")):
        return user_input
    if "." in user_input and " " not in user_input:
        return f"https://{user_input}"
    
    # Web search fallback
    encoded_query = urllib.parse.quote(user_input)
    return f"https://html.duckduckgo.com/html/?q={encoded_query}"

def fetch_proxied_html(url: str) -> str:
    """Fetches HTML server-side and injects a base URL tag to preserve relative assets."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Inject <base> tag so CSS/JS relative links resolve accurately
        if soup.head:
            base_tag = soup.new_tag("base", href=url)
            soup.head.insert(0, base_tag)
            
        return str(soup)
    except Exception as e:
        return f"""
        <div style="color: #ff4b4b; padding: 20px; font-family: sans-serif; background-color: #1e1e1e; border-radius: 8px;">
            <h3>⚠️ Network / Refusal Error</h3>
            <p>Could not fetch <code>{url}</code> via proxy mode.</p>
            <p><b>Details:</b> {str(e)}</p>
            <p><i>Try switching the Render Mode to "Direct Iframe" in the navigation bar.</i></p>
        </div>
        """

# Sidebar Options & Bookmarks
st.sidebar.title("🌐 Utopia Control Panel")

# Speed Dial / Bookmarks Section
st.sidebar.subheader("⭐ Bookmarks")
for bm in st.session_state.bookmarks:
    if st.sidebar.button(f"📌 {bm['name']}", key=f"bm_{bm['url']}"):
        st.session_state.current_url = bm["url"]
        st.rerun()

# Bookmark Management
with st.sidebar.expander("➕ Add Current Page to Bookmarks"):
    bm_name = st.text_input("Bookmark Label", value="")
    if st.button("Save Bookmark") and bm_name:
        st.session_state.bookmarks.append({"name": bm_name, "url": st.session_state.current_url})
        st.sidebar.success("Bookmark added!")

# History Section
st.sidebar.subheader("📜 Browsing History")
if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.rerun()

for idx, hist_url in enumerate(reversed(st.session_state.history[-10:])):
    if st.sidebar.button(f"🔗 {hist_url[:30]}...", key=f"hist_{idx}"):
        st.session_state.current_url = hist_url
        st.rerun()

# Main Browser Bar
st.title("Utopia Web Browser")

col1, col2, col3 = st.columns([6, 2, 2])

with col1:
    input_text = st.text_input(
        "Enter URL or Search Query", 
        value=st.session_state.current_url,
        placeholder="https://example.com or search python...",
        label_visibility="collapsed"
    )

with col2:
    if st.button("🚀 Navigate", use_container_width=True):
        new_url = parse_input(input_text)
        st.session_state.current_url = new_url
        if new_url not in st.session_state.history:
            st.session_state.history.append(new_url)
        st.rerun()

with col3:
    render_mode = st.selectbox(
        "Render Mode", 
        ["Proxied HTML", "Direct Iframe"], 
        label_visibility="collapsed"
    )

st.divider()

# Rendering View
active_url = st.session_state.current_url

if render_mode == "Direct Iframe":
    st.caption(f"Rendering `{active_url}` via direct embedded frame:")
    st.components.v1.iframe(src=active_url, height=750, scrolling=True)
else:
    st.caption(f"Rendering `{active_url}` via server-side proxy fetch:")
    html_content = fetch_proxied_html(active_url)
    st.components.v1.html(html_content, height=750, scrolling=True)
