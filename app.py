import streamlit as st
from datetime import date, timedelta
import base64
from io import BytesIO

st.set_page_config(page_title="Questify", page_icon="🍓", layout="centered")

# ── Session State initialisieren ─────────────────────────────────────────────
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "id": 1,
            "author": "Lena M.",
            "initials": "LM",
            "day": 12,
            "time": "vor 2 Std.",
            "text": "Heute wieder um 6 Uhr raus! 20 Minuten meditiert und dann ein kurzer Spaziergang. Fühle mich super energiegeladen! 💪",
            "img": None,
            "likes": 5,
            "liked": False,
            "comments": [
                {"author": "Marco K.", "text": "Stark! Ich schaffe morgens kaum die Augen aufzumachen 😅"},
                {"author": "Jana T.", "text": "Die ersten 5 Minuten sind immer die schwersten!"},
            ],
        },
        {
            "id": 2,
            "author": "Marco K.",
            "initials": "MK",
            "day": 12,
            "time": "vor 4 Std.",
            "text": "Tag 12 gecheckt ✅ Heute war es besonders schwer, aber ich hab's durchgezogen. Kalte Dusche direkt nach dem Aufwachen hilft enorm.",
            "img": None,
            "likes": 8,
            "liked": False,
            "comments": [
                {"author": "Lena M.", "text": "Kalte Dusche ist auf jeden Fall ein Gamechanger! 🥶"},
            ],
        },
        {
            "id": 3,
            "author": "Jana T.",
            "initials": "JT",
            "day": 11,
            "time": "gestern",
            "text": "Morgenroutine komplett abgehakt! Yoga + Tagebuch schreiben. Diese Quest verändert wirklich meinen Alltag.",
            "img": None,
            "likes": 3,
            "liked": False,
            "comments": [],
        },
    ]

if "active_quest" not in st.session_state:
    st.session_state.active_quest = None

if "quests" not in st.session_state:
    st.session_state.quests = []

if "page" not in st.session_state:
    st.session_state.page = "feed"

if "comment_inputs" not in st.session_state:
    st.session_state.comment_inputs = {}

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────
def img_to_base64(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.read()
    b64 = base64.b64encode(bytes_data).decode()
    mime = uploaded_file.type
    return f"data:{mime};base64,{b64}"


def like_post(post_id):
    for p in st.session_state.posts:
        if p["id"] == post_id:
            if p["liked"]:
                p["likes"] -= 1
                p["liked"] = False
            else:
                p["likes"] += 1
                p["liked"] = True
            break


def add_comment(post_id, text):
    for p in st.session_state.posts:
        if p["id"] == post_id:
            p["comments"].append({"author": "Du", "text": text})
            break


# ── Seiten ───────────────────────────────────────────────────────────────────
def page_account():
    st.markdown("## 🔆 Profil anlegen")
    with st.form("Kontakt"):
        col1, col2 = st.columns(2)
        with col1:
            vorname = st.text_input("Vorname")
        with col2:
            nachname = st.text_input("Nachname")

        email = st.text_input("E-Mail")
        nachricht = st.text_area("Nachricht")
        zustimmung = st.checkbox("Ich stimme den AGB zu")
        submitted = st.form_submit_button("Absenden", type="primary")

    if submitted:
        if not zustimmung:
            st.error("Bitte AGB akzeptieren!")
        elif not email:
            st.error("E-Mail fehlt!")
        else:
            st.success(f"Danke, {vorname}! Dein Profil wurde erstellt.")


def page_quest_erstellen():
    st.markdown("## ⚔️ Quest erstellen")
    with st.form("quest_form"):
        quest_name = st.text_input("Name der Quest")

        col1, col2 = st.columns(2)
        with col1:
            start_datum = st.date_input("Startdatum", value=date.today())
        with col2:
            end_datum = st.date_input("Enddatum", value=date.today() + timedelta(days=7))

        col3, col4 = st.columns(2)
        with col3:
            ort = st.selectbox(
                "Ort",
                ["für zu Hause", "im Freien", "im Fitnessstudio", "Schule/Uni/Arbeit", "sonstiges"],
                index=None,
                placeholder="Ort wählen...",
            )
        with col4:
            schwierigkeit = st.selectbox(
                "Schwierigkeitslevel",
                ["Einfach", "Mittel", "Schwer", "Sehr Schwer"],
                index=None,
                placeholder="Schwierigkeit wählen...",
            )

        beschreibung = st.text_area("Beschreibung", height=200)
        submitted = st.form_submit_button("Quest starten 🚀", type="primary")

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
            days_total = (end_datum - start_datum).days
            new_quest = {
                "name": quest_name,
                "start": start_datum,
                "end": end_datum,
                "ort": ort,
                "schwierigkeit": schwierigkeit,
                "beschreibung": beschreibung,
                "days_total": days_total,
            }
            st.session_state.quests.append(new_quest)
            st.session_state.active_quest = new_quest
            st.success(f"Quest '{quest_name}' wurde gestartet! 🎉")
            st.info("Gehe zum Feed, um deinen Fortschritt zu teilen.")


def page_feed():
    # Aktive Quest anzeigen
    quest = st.session_state.active_quest
    if quest:
        days_done = (date.today() - quest["start"]).days + 1
        days_done = max(0, min(days_done, quest["days_total"]))
        progress = days_done / quest["days_total"] if quest["days_total"] > 0 else 0

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg,#1a1a2e,#16213e);
                        border-radius:12px;padding:1.2rem;color:white;margin-bottom:1.5rem;">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-size:16px;font-weight:500">⚔️ {quest['name']}</div>
                  <div style="font-size:12px;opacity:.7;margin-top:4px">
                    Tag {days_done} von {quest['days_total']} · {quest.get('schwierigkeit','–')}
                  </div>
                </div>
                <div style="background:#E23D5B;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:500">
                  Aktiv
                </div>
              </div>
              <div style="height:4px;background:rgba(255,255,255,.2);border-radius:2px;margin-top:12px">
                <div style="height:100%;width:{int(progress*100)}%;background:#E23D5B;border-radius:2px"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Du hast noch keine aktive Quest. Erstelle eine über die Sidebar!")

    # ── Fortschritt teilen ───────────────────────────────────────────────────
    st.markdown("### 📤 Fortschritt teilen")
    with st.form("post_form", clear_on_submit=True):
        post_text = st.text_area(
            "Was hast du heute geschafft?",
            placeholder="Beschreibe deinen Fortschritt...",
            height=100,
        )
        uploaded_img = st.file_uploader("Foto hinzufügen (optional)", type=["jpg", "jpeg", "png"])
        tag_num = st.number_input("Tag #", min_value=1, max_value=365, value=1, step=1)
        post_submitted = st.form_submit_button("📨 Posten", type="primary")

    if post_submitted:
        if not post_text.strip():
            st.error("Bitte einen Text eingeben.")
        else:
            img_data = img_to_base64(uploaded_img) if uploaded_img else None
            new_post = {
                "id": len(st.session_state.posts) + 1,
                "author": "Du",
                "initials": "DU",
                "day": int(tag_num),
                "time": "gerade eben",
                "text": post_text,
                "img": img_data,
                "likes": 0,
                "liked": False,
                "comments": [],
            }
            st.session_state.posts.insert(0, new_post)
            st.success("Dein Fortschritt wurde geteilt! 🎉")
            st.rerun()

    st.divider()
    st.markdown("### 🗂️ Feed")

    # ── Posts anzeigen ───────────────────────────────────────────────────────
    for post in st.session_state.posts:
        pid = post["id"]
        with st.container(border=True):
            # Header
            col_av, col_info, col_day = st.columns([0.08, 0.72, 0.2])
            with col_av:
                st.markdown(
                    f"<div style='width:36px;height:36px;border-radius:50%;background:#FBEAF0;"
                    f"color:#E23D5B;display:flex;align-items:center;justify-content:center;"
                    f"font-size:12px;font-weight:500'>{post['initials']}</div>",
                    unsafe_allow_html=True,
                )
            with col_info:
                st.markdown(
                    f"**{post['author']}** &nbsp; <span style='font-size:12px;color:gray'>{post['time']}</span>",
                    unsafe_allow_html=True,
                )
            with col_day:
                st.markdown(
                    f"<span style='font-size:11px;background:#f0f0f0;border-radius:20px;"
                    f"padding:2px 8px;color:#555'>Tag {post['day']}</span>",
                    unsafe_allow_html=True,
                )

            # Bild
            if post["img"]:
                st.image(post["img"], use_container_width=True)

            # Text
            st.markdown(post["text"])

            # Like & Kommentar Buttons
            col_like, col_comment, _ = st.columns([0.2, 0.25, 0.55])
            with col_like:
                heart = "❤️" if post["liked"] else "🤍"
                if st.button(f"{heart} {post['likes']}", key=f"like_{pid}"):
                    like_post(pid)
                    st.rerun()
            with col_comment:
                n_comments = len(post["comments"])
                show_key = f"show_comments_{pid}"
                if show_key not in st.session_state:
                    st.session_state[show_key] = False
                label = f"💬 {n_comments}"
                if st.button(label, key=f"toggle_comments_{pid}"):
                    st.session_state[show_key] = not st.session_state[show_key]
                    st.rerun()

            # Kommentare
            if st.session_state.get(f"show_comments_{pid}", False):
                if post["comments"]:
                    for c in post["comments"]:
                        st.markdown(
                            f"<div style='background:#f8f8f8;border-radius:8px;padding:8px 12px;"
                            f"margin:4px 0;font-size:13px'>"
                            f"<strong>{c['author']}</strong>: {c['text']}</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("Noch keine Kommentare.")

                with st.form(f"comment_form_{pid}", clear_on_submit=True):
                    new_comment = st.text_input("Kommentar schreiben...", key=f"cinput_{pid}", label_visibility="collapsed")
                    c_submitted = st.form_submit_button("Senden")
                    if c_submitted and new_comment.strip():
                        add_comment(pid, new_comment.strip())
                        st.rerun()


# ── Sidebar Navigation ───────────────────────────────────────────────────────
st.sidebar.title("🍓 Questify")
st.sidebar.divider()

if st.sidebar.button("🏠 Feed", use_container_width=True):
    st.session_state.page = "feed"

if st.sidebar.button("⚔️ Quest erstellen", use_container_width=True):
    st.session_state.page = "quest"

if st.sidebar.button("👤 Account erstellen", use_container_width=True):
    st.session_state.page = "account"

if st.session_state.active_quest:
    st.sidebar.divider()
    st.sidebar.markdown(f"**Aktive Quest:**  \n{st.session_state.active_quest['name']}")

# ── Router ───────────────────────────────────────────────────────────────────
st.title("🍓 Questify")

if st.session_state.page == "feed":
    page_feed()
elif st.session_state.page == "quest":
    page_quest_erstellen()
elif st.session_state.page == "account":
    page_account()