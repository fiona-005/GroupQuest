import streamlit as st
from datetime import date, timedelta

st.title("🍓Questify🍓")

def page1():
    st.markdown("Account erstellen")

    
    st.markdown("🍓Questify🍓")

    st.title("🔆Profil anlegen🔆")

    with st.form("Kontakt"):
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

    
st.title("Quest erstellen")
 
with st.form("quest_form"):
    quest_name = st.text_input("Name der Quest")
 
    col1, col2 = st.columns(2)
    with col1:
        start_datum = st.date_input("Startdatum", value=date.today())
    with col2:
        end_datum = st.date_input("Enddatum", value=date.today() + timedelta(days=7))
 
    beschreibung = st.text_area("Beschreibung", height=200)
 
    submitted = st.form_submit_button("Quest starten")
 
if submitted:
    errors = []
    if not quest_name.strip():
        errors.append("Bitte einen Namen der Quest eingeben.")
    if end_datum < start_datum:
        errors.append("Das Enddatum muss nach dem Startdatum liegen.")
    if not beschreibung.strip():
        errors.append("Bitte eine Beschreibung eingeben.")
 
    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success(f"Quest '{quest_name}' wurde gestartet!")




# Widgets shared by all the pages
if st.sidebar.button("Account erstellen"):
    page1() 
    
if st.sidebar.button("Quest erstellen"):
    page2(
    )

