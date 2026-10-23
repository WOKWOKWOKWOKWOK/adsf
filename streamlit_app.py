import streamlit as st

st.set_page_config(
    page_title="App Hub & Resource Portal",
    page_icon="🚀",
    layout="wide"
)

# Sidebar Navigation for Internal App Pages
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard Home", "Web Resource Hub", "Tools & Utilities"])

if page == "Dashboard Home":
    st.title("🚀 Welcome to Your App Hub")
    st.write("Select a tool or resource from the navigation menu on the left.")

elif page == "Web Resource Hub":
    st.title("🌐 Approved Web Resources")
    st.write("Click any resource below to open it safely in a new browser tab:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Search & Reference")
        st.link_button("DuckDuckGo", "https://duckduckgo.com", use_container_width=True)
        st.link_button("Wikipedia", "https://www.wikipedia.org", use_container_width=True)

    with col2:
        st.subheader("Development")
        st.link_button("GitHub", "https://github.com", use_container_width=True)
        st.link_button("Streamlit Docs", "https://docs.streamlit.io", use_container_width=True)

    with col3:
        st.subheader("Learning")
        st.link_button("Khan Academy", "https://www.khanacademy.org", use_container_width=True)
        st.link_button("Python Docs", "https://docs.python.org/3/", use_container_width=True)

elif page == "Tools & Utilities":
    st.title("🛠️ Internal Tools")
    st.write("You can add custom Python tools, calculators, or data viewers here.")
    
    # Example internal tool
    text_input = st.text_area("Quick Note / Text Scratchpad")
    if text_input:
        st.info(f"Word count: {len(text_input.split())}")
