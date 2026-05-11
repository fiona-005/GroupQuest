import streamlit as st

# Page config (muss sehr früh aufgerufen werden)
st.set_page_config(
	page_title="Streamlit Demo",
	page_icon="🧪",
	layout="centered",
	initial_sidebar_state="expanded",
)

# Title
st.title("Streamlit Demo App")

# Text
st.write("Diese App zeigt ein paar grundlegende Streamlit-Widgets.")
st.text("st.text() ist für einfachen, unformatierten Text.")

# Text input
name = st.text_input("Wie heißt du?", value="")

# Slider
wert = st.slider("Wähle einen Wert", min_value=0, max_value=100, value=50, step=1)

# Button
if st.button("Ausgeben"):
	if name.strip():
		st.success(f"Hallo {name}! Dein Slider-Wert ist {wert}.")
	else:
		st.warning(f"Bitte gib einen Namen ein. Slider-Wert ist {wert}.")

# Optional: Live-Ausgabe ohne Button
st.caption("Live-Status")
st.write({"name": name, "wert": wert})