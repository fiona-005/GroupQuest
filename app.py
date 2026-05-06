import streamlit as st

st.title("🍓Questify🍓")

def page1():
    st.markdown("Account erstellen")

    
    st.markdown("🍓Questify🍓")

    st.title("🔆Profil anlegen🔆")

    with st.form("kontakt"):
        col1, col2 = st.columns(2)
        with col1:
            vorname = st.text_input("Vorname")
        
        with col2:
            nachname = st.text_input("Nachname")
            
            email   = st.text_input("E-Mail")
            nachricht = st.text_area("Nachricht")
            zustimmung = st.checkbox("Ich stimme den AGB zu")
            
            submitted = st.form_submit_button("Absenden", type="primary")

        


    if submitted:
        if not zustimmung:
            st.error("Bitte AGB akzeptieren!")
        elif not email:
            st.error("E-Mail fehlt!")
        else:
            st.success(f"Danke, {vorname}! Deine Nachricht wurde gesendet.")

def page2():
    st.markdown("Quest erstellen")

# Widgets shared by all the pages
if st.sidebar.button("Account erstellen"):
    page1()
if st.sidebar.button("Quest erstellen"):
    page2(
    )