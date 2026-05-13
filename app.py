import streamlit as st
from datetime import date, timedelta
import base64
import random

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
            "quest_name": "30 Tage Morgenroutine",
            "schwierigkeit": "Mittel",
            "quest_progress": 40,
            "is_friend": True,
            "same_challenge": True,
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
            "quest_name": "30 Tage Morgenroutine",
            "schwierigkeit": "Mittel",
            "quest_progress": 40,
            "is_friend": True,
            "same_challenge": True,
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
            "quest_name": "30 Tage Morgenroutine",
            "schwierigkeit": "Mittel",
            "quest_progress": 37,
            "is_friend": False,
            "same_challenge": True,
        },
        {
            "id": 4,
            "author": "Felix R.",
            "initials": "FR",
            "day": 7,
            "time": "vor 1 Tag",
            "text": "Woche 1 geschafft! 🏋️ Jeden Tag ins Gym ist krasser als ich dachte, aber ich bin dabei.",
            "img": None,
            "likes": 12,
            "liked": False,
            "comments": [
                {"author": "Lena M.", "text": "Respekt! Weiter so 💪"},
            ],
            "quest_name": "30 Tage Gym",
            "schwierigkeit": "Schwer",
            "quest_progress": 23,
            "is_friend": True,
            "same_challenge": False,
        },
        {
            "id": 5,
            "author": "Sophie W.",
            "initials": "SW",
            "day": 5,
            "time": "vor 2 Tagen",
            "text": "Heute 10 km gelaufen! Mein bisher weitester Lauf. Die Challenge motiviert mich wirklich.",
            "img": None,
            "likes": 6,
            "liked": False,
            "img": "run.jpeg",
            "comments": [],
            "quest_name": "30 Tage Laufen",
            "schwierigkeit": "Schwer",
            "quest_progress": 17,
            "is_friend": False,
            "same_challenge": True,
        },
    ]

if "for_you_posts" not in st.session_state:
    # Separate copies for For-You page
    st.session_state.for_you_posts = [
        {**p} for p in st.session_state.posts
    ]

if "active_quest" not in st.session_state:
    st.session_state.active_quest = None

if "quests" not in st.session_state:
    st.session_state.quests = []

if "page" not in st.session_state:
    st.session_state.page = "feed"

if "comment_inputs" not in st.session_state:
    st.session_state.comment_inputs = {}

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "fy_filter" not in st.session_state:
    st.session_state.fy_filter = "Alle"

# ── NEU: Täglicher Check-in Status ───────────────────────────────────────────
# Speichert das Datum des letzten Check-ins pro Quest, um Doppelklicks zu verhindern
if "daily_checkin" not in st.session_state:
    st.session_state.daily_checkin = {}  # quest_name -> date string

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def img_to_base64(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.read()
    b64 = base64.b64encode(bytes_data).decode()
    mime = uploaded_file.type
    return f"data:{mime};base64,{b64}"

def like_post(post_id, source="posts"):
    lst = st.session_state.for_you_posts if source == "for_you" else st.session_state.posts
    for p in lst:
        if p["id"] == post_id:
            if p["liked"]:
                p["likes"] -= 1
                p["liked"] = False
            else:
                p["likes"] += 1
                p["liked"] = True
            break

def add_comment(post_id, text, source="posts"):
    lst = st.session_state.for_you_posts if source == "for_you" else st.session_state.posts
    for p in lst:
        if p["id"] == post_id:
            p["comments"].append({"author": "Du", "text": text})
            break

def is_checked_in_today(quest_name: str) -> bool:
    """Gibt True zurück, wenn die Quest heute schon abgehakt wurde."""
    today_str = date.today().isoformat()
    return st.session_state.daily_checkin.get(quest_name) == today_str

def do_daily_checkin(quest_name: str, schwierigkeit: str):
    """Führt den täglichen Check-in durch und vergibt XP."""
    today_str = date.today().isoformat()
    st.session_state.daily_checkin[quest_name] = today_str
    xp_amount = XP_PER_DAY.get(schwierigkeit, 5)
    award_xp(xp_amount, reason=f"Tages-Check-in: {quest_name}")

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
    quest = st.session_state.active_quest
    if quest:
        days_done = (date.today() - quest["start"]).days + 1
        days_done = max(0, min(days_done, quest["days_total"]))
        progress = days_done / quest["days_total"] if quest["days_total"] > 0 else 0

        quest_name = quest["name"]
        schwierigkeit = quest.get("schwierigkeit", "Einfach")
        checked_today = is_checked_in_today(quest_name)

        # ── Quest-Banner mit Check-in Button ────────────────────────────────
        col_banner, col_check = st.columns([0.82, 0.18])

        with col_banner:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg,#1a1a2e,#16213e);
                            border-radius:12px;padding:1.2rem;color:white;">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                      <div style="font-size:16px;font-weight:500">⚔️ {quest_name}</div>
                      <div style="font-size:12px;opacity:.7;margin-top:4px">
                        Tag {days_done} von {quest['days_total']} · {schwierigkeit}
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

        with col_check:
            if checked_today:
                # Bereits abgehakt – grüner Zustand
                st.markdown(
                    """
                    <div style="display:flex;flex-direction:column;align-items:center;
                                justify-content:center;height:100%;padding-top:4px">
                      <div style="width:52px;height:52px;border-radius:50%;
                                  background:#1a3a2a;border:2px solid #2ecc71;
                                  display:flex;align-items:center;justify-content:center;
                                  font-size:24px;margin:0 auto">✅</div>
                      <div style="font-size:10px;color:#2ecc71;text-align:center;
                                  margin-top:5px;font-weight:500">Erledigt!</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # Noch nicht abgehakt – klickbarer Button
                st.markdown("<div style='padding-top:4px'>", unsafe_allow_html=True)
                if st.button(
                    "✔",
                    key="daily_checkin_btn",
                    help=f"Tag {days_done} als erledigt markieren (+{XP_PER_DAY.get(schwierigkeit, 5)} XP)",
                    use_container_width=True,
                ):
                    do_daily_checkin(quest_name, schwierigkeit)
                    st.rerun()
                st.markdown(
                    "<div style='font-size:10px;color:gray;text-align:center;margin-top:2px'>Heute abhaken</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

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
                "id": len(st.session_state.posts) + 100,
                "author": "Du",
                "initials": "DU",
                "day": int(tag_num),
                "time": "gerade eben",
                "text": post_text,
                "img": img_data,
                "likes": 0,
                "liked": False,
                "comments": [],
                "quest_name": st.session_state.active_quest["name"] if st.session_state.active_quest else "–",
                "schwierigkeit": st.session_state.active_quest.get("schwierigkeit", "Einfach") if st.session_state.active_quest else "Einfach",
                "quest_progress": 0,
                "is_friend": False,
                "same_challenge": True,
            }
            st.session_state.posts.insert(0, new_post)
            st.session_state.for_you_posts.insert(0, {**new_post})

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
                    like_post(pid, "posts")
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
                        add_comment(pid, new_comment.strip(), "posts")
                        st.rerun()


def page_for_you():
    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#E23D5B,#c0294a);
                    border-radius:14px;padding:1.4rem 1.6rem;color:white;margin-bottom:1.5rem">
          <div style="font-size:22px;font-weight:700;letter-spacing:-0.3px">✨ For You</div>
          <div style="font-size:13px;opacity:0.85;margin-top:4px">
            Fortschritt deiner Freunde &amp; gleiche Challenges
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Freunde-Fortschritt oben ─────────────────────────────────────────────
    st.markdown("### 👥 Freunde – Tages-Fortschritt")

    friends_data = [
        {"name": "Lena M.", "initials": "LM", "quest": "30 Tage Morgenroutine", "day": 12, "total": 30, "schwierigkeit": "Mittel", "streak": 12},
        {"name": "Marco K.", "initials": "MK", "quest": "30 Tage Morgenroutine", "day": 12, "total": 30, "schwierigkeit": "Mittel", "streak": 12},
        {"name": "Felix R.", "initials": "FR", "quest": "30 Tage Gym", "day": 7, "total": 30, "schwierigkeit": "Schwer", "streak": 7},
    ]

    cols = st.columns(len(friends_data))
    for i, f in enumerate(friends_data):
        prog = int(f["day"] / f["total"] * 100)
        badge_style = BADGE_STYLES.get(f["schwierigkeit"], "background:#f0f0f0;color:#555")
        with cols[i]:
            st.markdown(
                f"""
                <div style="background:#fff;border:1px solid #f0f0f0;border-radius:12px;
                            padding:14px 12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
                  <div style="width:44px;height:44px;border-radius:50%;background:#FBEAF0;
                              color:#E23D5B;display:flex;align-items:center;justify-content:center;
                              font-size:15px;font-weight:600;margin:0 auto 8px">{f['initials']}</div>
                  <div style="font-size:13px;font-weight:600;margin-bottom:2px">{f['name']}</div>
                  <div style="font-size:11px;color:gray;margin-bottom:6px;line-height:1.3">{f['quest']}</div>
                  <div style="font-size:10px;padding:2px 7px;border-radius:99px;{badge_style};
                              display:inline-block;margin-bottom:8px">{f['schwierigkeit']}</div>
                  <div style="height:5px;background:#f0f0f0;border-radius:3px;overflow:hidden;margin-bottom:4px">
                    <div style="height:100%;width:{prog}%;background:#E23D5B;border-radius:3px"></div>
                  </div>
                  <div style="font-size:11px;color:#666">Tag {f['day']}/{f['total']}</div>
                  <div style="font-size:12px;margin-top:4px">🔥 {f['streak']} Tage</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter-Tabs ──────────────────────────────────────────────────────────
    st.markdown("### 📋 Beiträge")

    col_f1, col_f2, col_f3 = st.columns(3)
    filters = ["Alle", "👥 Freunde", "🏆 Gleiche Challenge"]
    for col, label in zip([col_f1, col_f2, col_f3], filters):
        is_active = st.session_state.fy_filter == label
        style = (
            "background:#E23D5B;color:white;border:none;border-radius:20px;"
            "padding:6px 14px;font-size:13px;font-weight:500;cursor:pointer;width:100%"
            if is_active else
            "background:#f5f5f5;color:#555;border:none;border-radius:20px;"
            "padding:6px 14px;font-size:13px;cursor:pointer;width:100%"
        )
        with col:
            if st.button(label, key=f"filter_{label}", use_container_width=True):
                st.session_state.fy_filter = label
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Posts filtern ────────────────────────────────────────────────────────
    active_filter = st.session_state.fy_filter
    posts = st.session_state.for_you_posts

    if active_filter == "👥 Freunde":
        posts = [p for p in posts if p.get("is_friend")]
    elif active_filter == "🏆 Gleiche Challenge":
        posts = [p for p in posts if p.get("same_challenge")]

    if not posts:
        st.info("Keine Beiträge für diesen Filter.")
        return

    # ── Post-Karten ──────────────────────────────────────────────────────────
    for post in posts:
        pid = post["id"]
        schwierigkeit = post.get("schwierigkeit", "Einfach")
        badge_style = BADGE_STYLES.get(schwierigkeit, "background:#f0f0f0;color:#555")
        quest_name = post.get("quest_name", "–")
        quest_progress = post.get("quest_progress", 0)
        is_friend = post.get("is_friend", False)
        same_challenge = post.get("same_challenge", False)

        # Badges vorbereiten
        tag_badges = ""
        if is_friend:
            tag_badges += "<span style='font-size:10px;background:#EEF6FF;color:#2563EB;border-radius:99px;padding:2px 7px;margin-right:4px'>👥 Freund</span>"
        if same_challenge:
            tag_badges += "<span style='font-size:10px;background:#FFF0F3;color:#E23D5B;border-radius:99px;padding:2px 7px'>🏆 Gleiche Challenge</span>"

        with st.container(border=True):
            # Header
            col_av, col_info = st.columns([0.1, 0.9])
            with col_av:
                st.markdown(
                    f"<div style='width:42px;height:42px;border-radius:50%;background:#FBEAF0;"
                    f"color:#E23D5B;display:flex;align-items:center;justify-content:center;"
                    f"font-size:13px;font-weight:600;margin-top:2px'>{post['initials']}</div>",
                    unsafe_allow_html=True,
                )
            with col_info:
                st.markdown(
                    f"<div style='margin-bottom:2px'>"
                    f"<strong style='font-size:14px'>{post['author']}</strong>"
                    f" &nbsp;<span style='font-size:12px;color:gray'>{post['time']}</span></div>"
                    f"<div>{tag_badges}</div>",
                    unsafe_allow_html=True,
                )

            # Quest-Kontext-Banner
            st.markdown(
                f"""
                <div style="background:#fafafa;border-left:3px solid #E23D5B;border-radius:0 6px 6px 0;
                            padding:6px 10px;margin:8px 0;display:flex;justify-content:space-between;
                            align-items:center">
                  <div>
                    <span style="font-size:11px;color:gray">Quest: </span>
                    <span style="font-size:12px;font-weight:500;color:#333">{quest_name}</span>
                    &nbsp;
                    <span style="font-size:10px;padding:2px 6px;border-radius:99px;{badge_style}">{schwierigkeit}</span>
                  </div>
                  <div style="font-size:11px;color:gray">Tag {post['day']} &nbsp;·&nbsp;
                    <span style="color:#E23D5B;font-weight:500">{quest_progress}%</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Fortschrittsbalken
            st.markdown(
                f"""
                <div style="height:4px;background:#f0f0f0;border-radius:2px;
                            overflow:hidden;margin-bottom:10px">
                  <div style="height:100%;width:{quest_progress}%;background:#E23D5B;border-radius:2px"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if post["img"]:
                st.image(post["img"], use_container_width=True)

            st.markdown(f"<div style='font-size:14px;line-height:1.5;margin-bottom:8px'>{post['text']}</div>", unsafe_allow_html=True)

            # Like & Kommentar
            col_like, col_comment, _ = st.columns([0.22, 0.28, 0.5])
            with col_like:
                heart = "❤️" if post["liked"] else "🤍"
                if st.button(f"{heart} {post['likes']}", key=f"fy_like_{pid}"):
                    like_post(pid, "for_you")
                    st.rerun()
            with col_comment:
                n_comments = len(post["comments"])
                show_key = f"fy_show_comments_{pid}"
                if show_key not in st.session_state:
                    st.session_state[show_key] = False
                if st.button(f"💬 {n_comments}", key=f"fy_toggle_comments_{pid}"):
                    st.session_state[show_key] = not st.session_state[show_key]
                    st.rerun()

            # Kommentare
            if st.session_state.get(f"fy_show_comments_{pid}", False):
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

                with st.form(f"fy_comment_form_{pid}", clear_on_submit=True):
                    new_comment = st.text_input(
                        "Kommentar schreiben...",
                        key=f"fy_cinput_{pid}",
                        label_visibility="collapsed",
                        placeholder="Schreib etwas Motivierendes... 💬",
                    )
                    c_submitted = st.form_submit_button("Senden")
                    if c_submitted and new_comment.strip():
                        add_comment(pid, new_comment.strip(), "for_you")
                        st.rerun()


def page_level():
    st.markdown("## 🏆 Mein Level")

    info = get_level_info(st.session_state.xp)
    pct  = int(info["progress"] * 100)

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

    col1, col2, col3 = st.columns(3)
    quests = st.session_state.get("quests", [])
    streak = st.session_state.get("streak", 0)

    # Flammen-Anzeige basierend auf Streak
    if streak == 0:
        flame_display = "—"
        flame_label   = "Kein Streak"
        flame_color   = "#aaa"
    elif streak < 3:
        flame_display = "🔥" * streak
        flame_label   = f"{streak} Tag{'e' if streak > 1 else ''}"
        flame_color   = "#E07B39"
    elif streak < 7:
        flame_display = "🔥" * min(streak, 5)
        flame_label   = f"{streak} Tage 🏃"
        flame_color   = "#E05A1A"
    elif streak < 14:
        flame_display = "🔥🔥🔥🔥🔥"
        flame_label   = f"{streak} Tage 💪"
        flame_color   = "#C93E00"
    else:
        flame_display = "🔥🔥🔥🔥🔥"
        flame_label   = f"{streak} Tage 👑"
        flame_color   = "#A52D00"

    col1.metric("Gesamt-XP", st.session_state.xp)
    col2.metric("Quests",    len(quests))

    with col3:
        st.markdown(
            f"""
            <div style="background:#fff;border:0.5px solid #e0e0e0;border-radius:8px;
                        padding:10px 14px;text-align:center">
              <div style="font-size:10px;color:gray;text-transform:uppercase;
                          letter-spacing:.5px;margin-bottom:4px">Streak</div>
              <div style="font-size:20px;line-height:1.2">{flame_display}</div>
              <div style="font-size:13px;font-weight:600;color:{flame_color};
                          margin-top:3px">{flame_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

def explore_quest():
    st.markdown("## 🌍 Explore Quests")

    EXPLORE_QUESTS = [
        {
            "id": "eq1",
            "name": "30 Tage Morgenroutine",
            "schwierigkeit": "Mittel",
            "ort": "für zu Hause",
            "days_total": 30,
            "beschreibung": "Stehe jeden Tag zur gleichen Zeit auf und starte mit einer festen Morgenroutine in den Tag – ob Meditation, Sport oder Journaling.",
            "teilnehmer": 1243,
            "emoji": "🌅",
        },
        {
            "id": "eq2",
            "name": "30 Tage Gym",
            "schwierigkeit": "Schwer",
            "ort": "im Fitnessstudio",
            "days_total": 30,
            "beschreibung": "Gehe 30 Tage in Folge ins Fitnessstudio. Kein Tag wird ausgelassen – Konsequenz ist der Schlüssel zum Erfolg.",
            "teilnehmer": 876,
            "emoji": "🏋️",
        },
        {
            "id": "eq3",
            "name": "7 Tage Digital Detox",
            "schwierigkeit": "Sehr Schwer",
            "ort": "für zu Hause",
            "days_total": 7,
            "beschreibung": "Verzichte eine Woche lang auf Social Media und nicht notwendige Bildschirmzeit. Entdecke, was du mit der gewonnenen Zeit anfängst.",
            "teilnehmer": 512,
            "emoji": "📵",
        },
        {
            "id": "eq4",
            "name": "14 Tage täglich lesen",
            "schwierigkeit": "Einfach",
            "ort": "für zu Hause",
            "days_total": 14,
            "beschreibung": "Lies jeden Tag mindestens 20 Minuten in einem Buch deiner Wahl. Bildung und Entspannung in einem.",
            "teilnehmer": 2041,
            "emoji": "📖",
        },
        {
            "id": "eq5",
            "name": "21 Tage Laufen",
            "schwierigkeit": "Mittel",
            "ort": "im Freien",
            "days_total": 21,
            "beschreibung": "Laufe 21 Tage lang mindestens 20 Minuten am Stück. Egal ob Regen oder Sonnenschein – du ziehst es durch!",
            "teilnehmer": 694,
            "emoji": "🏃",
        },
        {
            "id": "eq6",
            "name": "30 Tage gesund ernähren",
            "schwierigkeit": "Schwer",
            "ort": "für zu Hause",
            "days_total": 30,
            "beschreibung": "Koche jeden Tag selbst und verzichte auf Fast Food, Zucker und verarbeitete Lebensmittel. Dein Körper wird es dir danken.",
            "teilnehmer": 1105,
            "emoji": "🥗",
        },
    ]

    # Session-State für den aktuellen Karten-Index und gesehene Quests
    if "explore_index" not in st.session_state:
        st.session_state.explore_index = 0
    if "explore_accepted" not in st.session_state:
        st.session_state.explore_accepted = []
    if "explore_rejected" not in st.session_state:
        st.session_state.explore_rejected = []

    idx = st.session_state.explore_index
    seen = st.session_state.explore_accepted + st.session_state.explore_rejected
    remaining = [q for q in EXPLORE_QUESTS if q["id"] not in seen]

    if not remaining:
        st.markdown(
            """
            <div style="text-align:center;padding:3rem 1rem">
              <div style="font-size:48px;margin-bottom:1rem">🎉</div>
              <div style="font-size:20px;font-weight:600;margin-bottom:0.5rem">Alle Quests gesehen!</div>
              <div style="font-size:14px;color:gray;margin-bottom:1.5rem">
                Du hast alle verfügbaren Quests durchgesehen.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.explore_accepted:
            st.markdown("### ✅ Angenommene Quests")
            for qid in st.session_state.explore_accepted:
                match = next((q for q in EXPLORE_QUESTS if q["id"] == qid), None)
                if match:
                    st.success(f"{match['emoji']} **{match['name']}** – {match['schwierigkeit']}")
        if st.button("🔄 Neu starten", type="primary"):
            st.session_state.explore_accepted = []
            st.session_state.explore_rejected = []
            st.rerun()
        return

    quest = remaining[0]
    schwierigkeit = quest["schwierigkeit"]
    badge_style = BADGE_STYLES.get(schwierigkeit, "background:#f0f0f0;color:#555")
    ort_icon = LOCATION_ICONS.get(quest["ort"], "📍")
    xp_day = XP_PER_DAY.get(schwierigkeit, 5)
    xp_bonus = XP_COMPLETION_BONUS.get(schwierigkeit, 20)
    total_xp = quest["days_total"] * xp_day + xp_bonus

    # Fortschritts-Zähler
    total_seen = len(seen)
    total_quests = len(EXPLORE_QUESTS)
    st.markdown(
        f"<div style='text-align:center;font-size:12px;color:gray;margin-bottom:0.5rem'>"
        f"Quest {total_seen + 1} von {total_quests}</div>",
        unsafe_allow_html=True,
    )

    # ── Quest-Karte ──────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #f0f0f0;border-radius:20px;
                    padding:2rem 1.6rem;box-shadow:0 8px 32px rgba(0,0,0,0.10);
                    max-width:480px;margin:0 auto 1.5rem">

          <!-- Emoji & Titel -->
          <div style="text-align:center;margin-bottom:1.2rem">
            <div style="font-size:56px;margin-bottom:0.5rem">{quest['emoji']}</div>
            <div style="font-size:21px;font-weight:700;letter-spacing:-0.3px;margin-bottom:0.4rem">
              {quest['name']}
            </div>
            <span style="font-size:12px;padding:3px 10px;border-radius:99px;{badge_style}">
              {schwierigkeit}
            </span>
          </div>

          <!-- Beschreibung -->
          <div style="font-size:14px;color:#444;line-height:1.65;
                      background:#fafafa;border-radius:10px;padding:12px 14px;
                      margin-bottom:1.2rem">
            {quest['beschreibung']}
          </div>

          <!-- Stats-Reihe -->
          <div style="display:flex;justify-content:space-around;text-align:center;
                      margin-bottom:1.2rem">
            <div>
              <div style="font-size:18px;font-weight:600;color:#E23D5B">{quest['days_total']}</div>
              <div style="font-size:11px;color:gray">Tage</div>
            </div>
            <div style="width:1px;background:#f0f0f0"></div>
            <div>
              <div style="font-size:18px;font-weight:600;color:#E23D5B">+{total_xp}</div>
              <div style="font-size:11px;color:gray">Max XP</div>
            </div>
            <div style="width:1px;background:#f0f0f0"></div>
            <div>
              <div style="font-size:18px;font-weight:600;color:#E23D5B">{quest['teilnehmer']:,}</div>
              <div style="font-size:11px;color:gray">Teilnehmer</div>
            </div>
          </div>

          <!-- Ort & XP-Details -->
          <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center">
            <span style="font-size:12px;background:#f5f5f5;border-radius:99px;
                         padding:4px 12px;color:#555">
              {ort_icon} {quest['ort']}
            </span>
            <span style="font-size:12px;background:#FFF0F3;border-radius:99px;
                         padding:4px 12px;color:#E23D5B">
              +{xp_day} XP/Tag
            </span>
            <span style="font-size:12px;background:#EAF3DE;border-radius:99px;
                         padding:4px 12px;color:#3B6D11">
              +{xp_bonus} XP Bonus
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Annehmen / Ablehnen Buttons ──────────────────────────────────────────
    col_reject, col_spacer, col_accept = st.columns([0.38, 0.24, 0.38])

    with col_reject:
        if st.button("❌ Ablehnen", use_container_width=True, key="explore_reject"):
            st.session_state.explore_rejected.append(quest["id"])
            st.rerun()

    with col_accept:
        if st.button("✅ Annehmen", use_container_width=True, key="explore_accept", type="primary"):
            st.session_state.explore_accepted.append(quest["id"])
            # Quest direkt als aktive Quest übernehmen
            new_quest = {
                "name": quest["name"],
                "start": date.today(),
                "end": date.today() + timedelta(days=quest["days_total"]),
                "ort": quest["ort"],
                "schwierigkeit": quest["schwierigkeit"],
                "beschreibung": quest["beschreibung"],
                "days_total": quest["days_total"],
            }
            st.session_state.quests.append(new_quest)
            st.session_state.active_quest = new_quest
            st.success(f"Quest **{quest['name']}** wurde angenommen und ist jetzt aktiv! 🎉")
            st.rerun()

    # ── Swipe-Tipp ───────────────────────────────────────────────────────────
    st.markdown(
        "<div style='text-align:center;font-size:11px;color:#bbb;margin-top:0.5rem'>"
        "❌ Ablehnen &nbsp;·&nbsp; ✅ Annehmen</div>",
        unsafe_allow_html=True,
    )

    # ── Bereits angenommen (kompakt) ─────────────────────────────────────────
    if st.session_state.explore_accepted:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"✅ Angenommene Quests ({len(st.session_state.explore_accepted)})"):
            for qid in st.session_state.explore_accepted:
                match = next((q for q in EXPLORE_QUESTS if q["id"] == qid), None)
                if match:
                    st.markdown(
                        f"{match['emoji']} **{match['name']}** &nbsp;"
                        f"<span style='font-size:11px;color:gray'>{match['schwierigkeit']} · "
                        f"{match['days_total']} Tage</span>",
                        unsafe_allow_html=True,
                    )

# ── Sidebar Navigation ───────────────────────────────────────────────────────

st.sidebar.title("🍓 Questify")
st.sidebar.divider()

if st.sidebar.button("🏠 Feed", use_container_width=True):
    st.session_state.page = "feed"

if st.sidebar.button("✨ For You", use_container_width=True):
    st.session_state.page = "for_you"

if st.sidebar.button("⚔️ Quest erstellen", use_container_width=True):
    st.session_state.page = "quest"

if st.sidebar.button("🏆 Mein Level", use_container_width=True):
    st.session_state.page = "level"

if st.sidebar.button("👤 Account erstellen", use_container_width=True):
    st.session_state.page = "account"

if st.sidebar.button("🌍 Exploring Quests", use_container_width=True):
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

# ── Router ───────────────────────────────────────────────────────────────────

st.title("🍓 Questify")

if st.session_state.page == "feed":
    page_feed()
elif st.session_state.page == "for_you":
    page_for_you()
elif st.session_state.page == "quest":
    page_quest_erstellen()
elif st.session_state.page == "level":
    page_level()
elif st.session_state.page == "account":
    page_account()
elif st.session_state.page == "explore":
    explore_quest()