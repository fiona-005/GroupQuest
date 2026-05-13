import streamlit as st
from datetime import date, timedelta
import base64

st.set_page_config(page_title="Questify", page_icon="🍓", layout="centered")

# ── XP-Konfiguration ─────────────────────────────────────────────────────────

XP_PER_DAY = {
    "Einfach":     5,
    "Mittel":      15,
    "Schwer":      25,
    "Sehr Schwer": 40,
}

XP_COMPLETION_BONUS = {
    "Einfach":     20,
    "Mittel":      50,
    "Schwer":      100,
    "Sehr Schwer": 200,
}

LEVEL_TITLES = {
    1:  "Neuling",
    2:  "Entdecker",
    3:  "Einsteiger",
    4:  "Aufsteiger",
    5:  "Kämpfer",
    6:  "Strebsamer",
    7:  "Abenteurer",
    8:  "Veteran",
    9:  "Champion",
    10: "Meister",
    11: "Großmeister",
    12: "Legende",
}

LOCATION_ICONS = {
    "für zu Hause":      "🏠",
    "im Freien":         "🌳",
    "im Fitnessstudio":  "🏋️",
    "Schule/Uni/Arbeit": "📚",
    "sonstiges":         "📍",
}

BADGE_STYLES = {
    "Einfach":     "background:#EAF3DE;color:#3B6D11",
    "Mittel":      "background:#FAEEDA;color:#854F0B",
    "Schwer":      "background:#FCEBEB;color:#A32D2D",
    "Sehr Schwer": "background:#EEEDFE;color:#3C3489",
}

# ── Level-Hilfsfunktionen ────────────────────────────────────────────────────

def xp_for_level(level: int) -> int:
    return int(100 * (level ** 1.6))

def total_xp_for_level(level: int) -> int:
    return sum(xp_for_level(lvl) for lvl in range(2, level + 1))

def get_level_info(total_xp: int) -> dict:
    level = 1
    while level < 99:
        if total_xp >= total_xp_for_level(level + 1):
            level += 1
        else:
            break
    xp_start    = total_xp_for_level(level)
    xp_end      = total_xp_for_level(level + 1)
    xp_in_level = total_xp - xp_start
    xp_needed   = xp_end - xp_start
    progress    = xp_in_level / xp_needed if xp_needed > 0 else 1.0
    return {
        "level":       level,
        "title":       LEVEL_TITLES.get(level, f"Level {level}"),
        "xp_in_level": xp_in_level,
        "xp_needed":   xp_needed,
        "xp_to_next":  xp_needed - xp_in_level,
        "progress":    progress,
    }

def award_xp(amount: int, reason: str = ""):
    old_info = get_level_info(st.session_state.xp)
    st.session_state.xp += amount
    new_info = get_level_info(st.session_state.xp)
    if new_info["level"] > old_info["level"]:
        st.balloons()
        st.success(
            f"🎉 Level Up! Du bist jetzt **Level {new_info['level']} – {new_info['title']}**!"
        )
    else:
        label = f" ({reason})" if reason else ""
        st.success(f"+{amount} XP{label}")

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "account"

if "comment_inputs" not in st.session_state:
    st.session_state.comment_inputs = {}

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "friends" not in st.session_state:
    st.session_state.friends = []  # Liste von Freunde-Dicts

# ── Demo-Nutzerdatenbank (simuliert andere User) ──────────────────────────────
ALL_USERS = [
    {"name": "Lena M.",  "initials": "LM", "level": 5,  "quest": "Morgenroutine"},
    {"name": "Marco K.", "initials": "MK", "level": 8,  "quest": "30 Tage Fitness"},
    {"name": "Jana T.",  "initials": "JT", "level": 3,  "quest": "Täglich lesen"},
    {"name": "Tom B.",   "initials": "TB", "level": 11, "quest": "Meditation"},
    {"name": "Sara L.",  "initials": "SL", "level": 2,  "quest": "Joggen"},
    {"name": "Felix W.", "initials": "FW", "level": 7,  "quest": "Kalt duschen"},
    {"name": "Mia H.",   "initials": "MH", "level": 4,  "quest": "Tagebuch"},
    {"name": "Leon S.",  "initials": "LS", "level": 9,  "quest": "Vokabeln lernen"},
    {"name": "Anna R.",  "initials": "AR", "level": 6,  "quest": "Yoga"},
    {"name": "Noah P.",  "initials": "NP", "level": 1,  "quest": "Spazieren gehen"},
]

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
        elif not vorname.strip():
            st.error("Bitte einen Vornamen eingeben.")
        else:
            st.session_state.logged_in = True
            st.session_state.user_name = vorname.strip()
            st.session_state.user_initials = (vorname[0] + (nachname[0] if nachname else "")).upper()
            st.session_state.page = "feed"
            st.rerun()


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

            # XP vergeben
            schwierigkeit = (
                st.session_state.active_quest.get("schwierigkeit", "Einfach")
                if st.session_state.active_quest
                else "Einfach"
            )
            award_xp(XP_PER_DAY.get(schwierigkeit, 5), reason="Fortschritt geteilt")
            st.rerun()

    st.divider()
    st.markdown("### 🗂️ Feed")

    for post in st.session_state.posts:
        pid = post["id"]
        with st.container(border=True):
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

            if post["img"]:
                st.image(post["img"], use_container_width=True)

            st.markdown(post["text"])

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
                if st.button(f"💬 {n_comments}", key=f"toggle_comments_{pid}"):
                    st.session_state[show_key] = not st.session_state[show_key]
                    st.rerun()

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
                    new_comment = st.text_input(
                        "Kommentar schreiben...", key=f"cinput_{pid}", label_visibility="collapsed"
                    )
                    c_submitted = st.form_submit_button("Senden")
                    if c_submitted and new_comment.strip():
                        add_comment(pid, new_comment.strip())
                        st.rerun()


def page_level():
    st.markdown("## 🏆 Mein Level")

    info = get_level_info(st.session_state.xp)
    pct  = int(info["progress"] * 100)

    # Haupt-XP-Block
    st.markdown(
        f"""
        <div style="background:#fff;border:0.5px solid #e0e0e0;border-radius:12px;
                    padding:1.2rem;margin-bottom:1rem">
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:1rem">
            <div style="width:56px;height:56px;border-radius:50%;background:#FBEAF0;
                        color:#E23D5B;display:flex;align-items:center;justify-content:center;
                        font-size:24px;font-weight:500;flex-shrink:0">{info['level']}</div>
            <div>
              <div style="font-size:17px;font-weight:500">
                Level {info['level']} – {info['title']}
              </div>
              <div style="font-size:13px;color:gray">{st.session_state.xp} XP gesamt</div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;
                      color:gray;margin-bottom:5px">
            <span>{info['xp_in_level']} / {info['xp_needed']} XP in diesem Level</span>
            <span>{info['xp_to_next']} XP bis Level {info['level'] + 1}</span>
          </div>
          <div style="height:14px;background:#f0f0f0;border-radius:7px;overflow:hidden">
            <div style="height:100%;width:{pct}%;background:#E23D5B;border-radius:7px"></div>
          </div>
          <div style="font-size:11px;color:gray;margin-top:4px;text-align:right">{pct}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Statistiken
    col1, col2, col3 = st.columns(3)
    quests = st.session_state.get("quests", [])
    active = 1 if st.session_state.get("active_quest") else 0
    col1.metric("Gesamt-XP",  st.session_state.xp)
    col2.metric("Quests",     len(quests))
    col3.metric("Aktiv",      active)

    # Aktive Quests
    st.markdown("### 📋 Aktive Quests")
    if not quests:
        st.info("Noch keine Quests erstellt.")
    else:
        for q in quests:
            schwierigkeit = q.get("schwierigkeit") or "Einfach"
            ort           = q.get("ort") or "sonstiges"
            icon          = LOCATION_ICONS.get(ort, "📍")
            xp_day        = XP_PER_DAY.get(schwierigkeit, 5)
            days_total    = max(q.get("days_total", 1), 1)
            days_done     = (date.today() - q["start"]).days + 1
            days_done     = max(0, min(days_done, days_total))
            progress_q    = int(days_done / days_total * 100)
            xp_earned     = days_done * xp_day
            badge_style   = BADGE_STYLES.get(schwierigkeit, "background:#f0f0f0;color:#555")

            st.markdown(
                f"""
                <div style="background:#fff;border:0.5px solid #e0e0e0;border-radius:10px;
                            padding:12px 14px;margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;align-items:center;
                              margin-bottom:6px">
                    <span style="font-size:14px;font-weight:500">{icon} {q['name']}</span>
                    <span style="font-size:11px;padding:2px 8px;border-radius:99px;
                                 {badge_style}">{schwierigkeit}</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div style="flex:1;height:6px;background:#f0f0f0;border-radius:3px;overflow:hidden">
                      <div style="height:100%;width:{progress_q}%;background:#E23D5B;
                                  border-radius:3px"></div>
                    </div>
                    <span style="font-size:12px;color:gray;white-space:nowrap">
                      {days_done} / {days_total} · {ort}
                    </span>
                  </div>
                  <div style="font-size:11px;color:gray;margin-top:5px">
                    +{xp_day} XP/Tag · {xp_earned} XP bisher ·
                    Abschluss-Bonus: +{XP_COMPLETION_BONUS.get(schwierigkeit, 20)} XP
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # XP-Legende
    with st.expander("ℹ️ Wie werden XP berechnet?"):
        st.markdown(
            """
            | Schwierigkeit | XP pro Tag | Abschluss-Bonus |
            |---|---|---|
            | Einfach | +5 | +20 |
            | Mittel | +15 | +50 |
            | Schwer | +25 | +100 |
            | Sehr Schwer | +40 | +200 |

            **Level-Formel:** `XP für Level N = int(100 × N^1.6)`  
            → Level 2: 100 XP · Level 5: 760 XP · Level 10: 2 512 XP · Level 20: 8 103 XP

            XP werden automatisch vergeben, wenn du im Feed einen Fortschritt postest.
            """
        )


def page_freunde():
    st.markdown("## 👥 Meine Freunde")

    # ── Suchleiste ───────────────────────────────────────────────────────────
    st.markdown("### 🔍 Freunde suchen")
    suche = st.text_input(
        "Name eingeben...",
        placeholder="z. B. Lena M.",
        label_visibility="collapsed",
    )

    friend_names = [f["name"] for f in st.session_state.friends]

    if suche.strip():
        treffer = [
            u for u in ALL_USERS
            if suche.lower() in u["name"].lower()
        ]
        if treffer:
            for u in treffer:
                bereits = u["name"] in friend_names
                col_av, col_info, col_btn = st.columns([0.1, 0.65, 0.25])
                with col_av:
                    st.markdown(
                        f"<div style='width:38px;height:38px;border-radius:50%;"
                        f"background:#FBEAF0;color:#E23D5B;display:flex;align-items:center;"
                        f"justify-content:center;font-size:12px;font-weight:500'>"
                        f"{u['initials']}</div>",
                        unsafe_allow_html=True,
                    )
                with col_info:
                    st.markdown(
                        f"**{u['name']}** &nbsp;"
                        f"<span style='font-size:12px;color:gray'>Lv. {u['level']} · {u['quest']}</span>",
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if bereits:
                        st.button("✓ Gefolgt", key=f"search_follow_{u['name']}", disabled=True)
                    else:
                        if st.button("➕ Folgen", key=f"search_follow_{u['name']}", type="primary"):
                            st.session_state.friends.append(u)
                            st.rerun()
        else:
            st.caption("Keine Nutzer gefunden.")

    st.divider()

    # ── Freundesliste ────────────────────────────────────────────────────────
    st.markdown(f"### 👫 Meine Freunde ({len(st.session_state.friends)})")

    if not st.session_state.friends:
        st.info("Du folgst noch niemandem. Suche oben nach Freunden!")
    else:
        for u in st.session_state.friends:
            col_av, col_info, col_btn = st.columns([0.1, 0.65, 0.25])
            with col_av:
                st.markdown(
                    f"<div style='width:38px;height:38px;border-radius:50%;"
                    f"background:#FBEAF0;color:#E23D5B;display:flex;align-items:center;"
                    f"justify-content:center;font-size:12px;font-weight:500'>"
                    f"{u['initials']}</div>",
                    unsafe_allow_html=True,
                )
            with col_info:
                st.markdown(
                    f"**{u['name']}** &nbsp;"
                    f"<span style='font-size:12px;color:gray'>Lv. {u['level']} · {u['quest']}</span>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("Entfernen", key=f"unfollow_{u['name']}"):
                    st.session_state.friends = [
                        f for f in st.session_state.friends if f["name"] != u["name"]
                    ]
                    st.rerun()

def explore_quest():
    st.markdown("## 👥 Explore Quests")

# ── Sidebar Navigation ───────────────────────────────────────────────────────

st.sidebar.title("🍓 Questify")
st.sidebar.divider()

if not st.session_state.logged_in:
    # Vor dem Login: nur Account erstellen anzeigen
    st.sidebar.button("👤 Account erstellen", use_container_width=True, disabled=True)
else:
    # Nach dem Login: alle Seiten
    if st.sidebar.button("🏠 Feed", use_container_width=True):
        st.session_state.page = "feed"

    if st.sidebar.button("⚔️ Quest erstellen", use_container_width=True):
        st.session_state.page = "quest"

    if st.sidebar.button("🏆 Mein Level", use_container_width=True):
        st.session_state.page = "level"

    if st.sidebar.button("👥 Meine Freunde", use_container_width=True):
        st.session_state.page = "freunde"
    
    if st.sidebar.button("⚔️ Exploring Quests", use_container_width=True):
        st.session_state.page = "explore"

    # Kompaktes Level-Widget in der Sidebar
    info = get_level_info(st.session_state.xp)
    pct  = int(info["progress"] * 100)
    st.sidebar.divider()
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
          <div style="width:32px;height:32px;border-radius:50%;background:#FBEAF0;
                      color:#E23D5B;display:flex;align-items:center;justify-content:center;
                      font-size:13px;font-weight:500;flex-shrink:0">{info['level']}</div>
          <div>
            <div style="font-size:13px;font-weight:500">
              Lv. {info['level']} – {info['title']}
            </div>
            <div style="font-size:11px;color:gray">{st.session_state.xp} XP gesamt</div>
          </div>
        </div>
        <div style="height:6px;background:#f0f0f0;border-radius:3px;overflow:hidden">
          <div style="height:100%;width:{pct}%;background:#E23D5B;border-radius:3px"></div>
        </div>
        <div style="font-size:10px;color:gray;margin-top:3px;text-align:right">
          {info['xp_to_next']} XP bis Level {info['level'] + 1}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.active_quest:
        st.sidebar.divider()
        st.sidebar.markdown(f"**Aktive Quest:**  \n{st.session_state.active_quest['name']}")

    # Freunde-Mini-Liste in der Sidebar
    if st.session_state.friends:
        st.sidebar.divider()
        st.sidebar.markdown(
            f"<div style='font-size:12px;font-weight:500;color:gray;margin-bottom:6px'>"
            f"👥 Freunde ({len(st.session_state.friends)})</div>",
            unsafe_allow_html=True,
        )
        for f in st.session_state.friends[:5]:
            st.sidebar.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
                f"<div style='width:26px;height:26px;border-radius:50%;background:#FBEAF0;"
                f"color:#E23D5B;display:flex;align-items:center;justify-content:center;"
                f"font-size:10px;font-weight:500;flex-shrink:0'>{f['initials']}</div>"
                f"<div style='font-size:12px'>{f['name']}"
                f"<span style='color:gray;font-size:11px'> · Lv.{f['level']}</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        if len(st.session_state.friends) > 5:
            st.sidebar.caption(f"+ {len(st.session_state.friends) - 5} weitere")

# ── Router ───────────────────────────────────────────────────────────────────

st.title("🍓 Questify")

if not st.session_state.logged_in:
    page_account()
elif st.session_state.page == "feed":
    page_feed()
elif st.session_state.page == "quest":
    page_quest_erstellen()
elif st.session_state.page == "level":
    page_level()
elif st.session_state.page == "freunde":
    page_freunde()
elif st.session_state.page == "account":
    page_account()
elif st.session_state.page == "explore":
    explore_quest()
