import streamlit as st

st.title("🍓Questify🍓")

def page1():
    st.markdown("Account erstellen")

def page2():
    st.markdown("Quest erstellen")

# Widgets shared by all the pages
if st.sidebar.button("Account erstellen"):
    page1()
if st.sidebar.button("Quest erstellen"):
    page2()