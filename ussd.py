import streamlit as st
import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="*617# USSD Simulator – ENGAGE",
    page_icon="📱",
    layout="centered",
)

# ── Custom CSS – dark phone aesthetic ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Nunito:wght@400;700;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0d0d;
    color: #e8e8e8;
    font-family: 'Nunito', sans-serif;
}

[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"]  { display: none; }
footer { visibility: hidden; }

/* Title */
h1 { color: #00e676 !important; font-family: 'Nunito', sans-serif; font-weight:900; }

/* Phone shell */
.phone-shell {
    background: #1a1a2e;
    border: 3px solid #00e676;
    border-radius: 28px;
    padding: 28px 24px 32px 24px;
    max-width: 370px;
    margin: 0 auto 24px auto;
    box-shadow: 0 0 40px #00e67640, 0 0 0 6px #0f0f0f;
    font-family: 'Share Tech Mono', monospace;
}

/* Screen header bar */
.screen-header {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #aaa;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #333;
}

/* USSD text box */
.ussd-box {
    background: #111;
    border: 1px solid #00e67650;
    border-radius: 10px;
    padding: 18px 16px;
    font-size: 15px;
    line-height: 1.7;
    color: #e0ffe0;
    min-height: 120px;
    white-space: pre-wrap;
    letter-spacing: 0.3px;
}

/* Airtime badge */
.airtime-badge {
    background: #ff1744;
    color: #fff;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 10px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
}

/* Keypad */
.keypad-hint {
    color: #888;
    font-size: 12px;
    margin-top: 12px;
    text-align: center;
    font-family: 'Nunito', sans-serif;
}

/* Status log */
.log-box {
    background: #111;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 12px;
    color: #888;
    font-family: 'Share Tech Mono', monospace;
    margin-top: 8px;
    max-height: 160px;
    overflow-y: auto;
}
.log-entry { margin-bottom: 4px; }
.log-entry.success { color: #00e676; }
.log-entry.info    { color: #40c4ff; }
.log-entry.warn    { color: #ffab40; }

/* Streamlit button override */
div.stButton > button {
    width: 100%;
    background: #00e676;
    color: #000;
    font-weight: 800;
    font-family: 'Nunito', sans-serif;
    border-radius: 12px;
    border: none;
    padding: 10px 0;
    font-size: 16px;
    letter-spacing: 0.5px;
    transition: background 0.2s;
}
div.stButton > button:hover {
    background: #69f0ae;
    color: #000;
}
div.stButton > button:active {
    background: #00c853;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "screen": "idle",        # idle | home | tier | done | declined
        "tier": None,
        "log": [],
        "airtime_used": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── USSD Logic helpers ────────────────────────────────────────────────────────
TIERS = {
    "1": ("Tier 1", "High School"),
    "2": ("Tier 2", "Diploma"),
    "3": ("Tier 3", "Degree"),
}

def add_log(msg, level="info"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append({"ts": ts, "msg": msg, "level": level})

def dial():
    """User dials *617#"""
    st.session_state.screen = "home"
    st.session_state.airtime_used += 1.0   # KES 1 charged on dial
    add_log("Session started – *617# dialled", "info")
    add_log("KES 1.00 deducted from airtime balance", "warn")

def choose_home(option: str):
    if option == "1":
        st.session_state.screen = "tier"
        add_log("User selected YES – proceeding to tier selection", "info")
    else:
        st.session_state.screen = "declined"
        add_log("User selected NO – session ended", "warn")

def choose_tier(option: str):
    if option in TIERS:
        st.session_state.tier = TIERS[option]
        st.session_state.screen = "done"
        add_log(f"User selected {TIERS[option][0]} ({TIERS[option][1]}) – registration submitted", "success")
    else:
        add_log("Invalid option entered", "warn")

def reset():
    for k in ["screen", "tier", "log", "airtime_used"]:
        del st.session_state[k]
    init_state()
    add_log("Simulator reset", "info")


# ── Screen content ────────────────────────────────────────────────────────────
def get_ussd_text():
    s = st.session_state.screen
    if s == "idle":
        return "Dial *617# to start\nENGAGE Project Registration"
    if s == "home":
        return ("ENGAGE Project\n"
                "─────────────────\n"
                "Do you want to proceed to apply\n"
                "for ENGAGE Project Training\n"
                "Cohort 3?\n\n"
                "1. Yes\n"
                "2. No")
    if s == "tier":
        return ("ENGAGE Cohort 3\n"
                "─────────────────\n"
                "Select your training tier:\n\n"
                "1. Tier 1 – High School\n"
                "2. Tier 2 – Diploma\n"
                "3. Tier 3 – Degree")
    if s == "done":
        t = st.session_state.tier
        return (f"✅ Registration Received!\n"
                f"─────────────────\n"
                f"Tier: {t[0]} ({t[1]})\n\n"
                f"You will receive a confirmation\n"
                f"SMS shortly. Thank you!\n\n"
                f"[END]")
    if s == "declined":
        return ("Thank you for dialling.\n"
                "Session ended.\n\n"
                "[END]")
    return ""


# ── Render UI ─────────────────────────────────────────────────────────────────
st.markdown("## 📱 USSD Simulator — `*617#`")
st.markdown("**ENGAGE Project Training Cohort 3** · _KES 1 per session_")
st.markdown("---")

now = datetime.datetime.now().strftime("%H:%M")
airtime = f"KES {st.session_state.airtime_used:.2f} used"

# Phone shell
ussd_text = get_ussd_text()
screen_html = f"""
<div class="phone-shell">
  <div class="screen-header">
    <span>Safaricom</span>
    <span>{now}</span>
    <span>▌▌▌</span>
  </div>
  <div class="ussd-box">{ussd_text}</div>
  {"<div class='airtime-badge'>💸 " + airtime + " (KES 1/session)</div>" if st.session_state.airtime_used > 0 else ""}
  <div class="keypad-hint">Use the buttons below to respond</div>
</div>
"""
st.markdown(screen_html, unsafe_allow_html=True)

# ── Action buttons per screen ─────────────────────────────────────────────────
s = st.session_state.screen

if s == "idle":
    if st.button("📲 Dial  *617#"):
        dial()
        st.rerun()

elif s == "home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("1 – Yes ✅"):
            choose_home("1")
            st.rerun()
    with col2:
        if st.button("2 – No ❌"):
            choose_home("2")
            st.rerun()

elif s == "tier":
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("1 – High School"):
            choose_tier("1")
            st.rerun()
    with c2:
        if st.button("2 – Diploma"):
            choose_tier("2")
            st.rerun()
    with c3:
        if st.button("3 – Degree"):
            choose_tier("3")
            st.rerun()

elif s in ("done", "declined"):
    if st.button("🔄 New Session (Dial Again)"):
        reset()
        st.rerun()

# ── Session log ───────────────────────────────────────────────────────────────
st.markdown("### 🖥️ Session Log")
if st.session_state.log:
    log_html = "<div class='log-box'>"
    for e in reversed(st.session_state.log):
        log_html += f"<div class='log-entry {e['level']}'>[{e['ts']}] {e['msg']}</div>"
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)
else:
    st.markdown("<div class='log-box'>No events yet. Dial *617# to begin.</div>", unsafe_allow_html=True)

# ── Reset btn ─────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🗑️ Reset Simulator"):
    reset()
    st.rerun()

st.markdown(
    "<div style='text-align:center;color:#444;font-size:11px;margin-top:24px;'>"
    "ENGAGE Project · USSD *617# Simulator · Built with Python & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
