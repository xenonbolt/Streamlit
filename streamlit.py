import streamlit as st
import time
import random
import hashlib
from datetime import datetime

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Portal",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── User Database (in-memory) ───────────────────────────────────────────────
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

DEFAULT_USERS = {
    "admin@nexus.io": {
        "name": "Alex Admin",
        "password_hash": hash_pw("admin123"),
        "group": "admins",
        "joined": "2024-01-10",
    },
    "staff@nexus.io": {
        "name": "Sam Internal",
        "password_hash": hash_pw("staff123"),
        "group": "internal",
        "joined": "2024-03-22",
    },
    "user@nexus.io": {
        "name": "Casey Customer",
        "password_hash": hash_pw("user123"),
        "group": "customers",
        "joined": "2025-01-05",
    },
}

GROUPS = {
    "admins":    {"label": "Admin",         "icon": "🛡️",  "color": "#e74c3c", "grad_a": "#c0392b", "grad_b": "#8e1a0e"},
    "internal":  {"label": "Internal User", "icon": "🏢",  "color": "#3498db", "grad_a": "#1a6b9a", "grad_b": "#0d3b5e"},
    "customers": {"label": "Customer",      "icon": "🌟",  "color": "#2ecc71", "grad_a": "#1e7e5e", "grad_b": "#0a3d2b"},
}

# ─── Initialize Session State ────────────────────────────────────────────────
if "users_db" not in st.session_state:
    st.session_state.users_db = DEFAULT_USERS.copy()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "auth_error" not in st.session_state:
    st.session_state.auth_error = ""
if "auth_success" not in st.session_state:
    st.session_state.auth_success = ""

# ─── Dummy Backend Functions ──────────────────────────────────────────────────
def dummy_fetch_admin(q):
    time.sleep(0.7)
    return random.choice([
        f"[ADMIN API] All 12 services operational. Query '{q}' processed successfully.",
        f"[ADMIN API] 3 audit log entries matched '{q}'. Zero anomalies flagged.",
        f"[ADMIN API] User access tokens refreshed. Permissions matrix updated.",
        f"[ADMIN API] System uptime 99.4% over 30 days. Dashboard metrics refreshed.",
        f"[ADMIN API] Config change staged. Pending approval from the security team.",
    ])

def dummy_fetch_internal(q):
    time.sleep(0.5)
    return random.choice([
        f"[INTERNAL API] 5 KB articles matched '{q}'. Displaying top result.",
        f"[INTERNAL API] Ticket TKT-{random.randint(1000,9999)} created and assigned.",
        f"[INTERNAL API] Policy doc retrieved from SharePoint. Updated 2024-11-15.",
        f"[INTERNAL API] HR lookup done. Onboarding has 3 pending items remaining.",
        f"[INTERNAL API] Sprint board synced: 4 open tasks, 1 blocked item.",
    ])

def dummy_fetch_customer(q):
    time.sleep(0.4)
    return random.choice([
        f"[CUSTOMER API] Order #ORD-{random.randint(10000,99999)} found. Delivery: Tomorrow.",
        f"[CUSTOMER API] Account active. Last login: {datetime.now().strftime('%b %d, %Y')}.",
        f"[CUSTOMER API] Support ticket submitted. Response within 24 hours.",
        f"[CUSTOMER API] Loyalty balance: {random.randint(500,5000)} pts. Redeem anytime!",
        f"[CUSTOMER API] FAQ match found for '{q}'. Connect to a live agent?",
    ])

FETCH_FN = {"admins": dummy_fetch_admin, "internal": dummy_fetch_internal, "customers": dummy_fetch_customer}

QUICK_ACTIONS = {
    "admins":    ["View Audit Logs", "User Permissions", "System Health", "Config Settings"],
    "internal":  ["Open Ticket", "Search KB", "HR Portal", "Team Board"],
    "customers": ["Track Order", "My Account", "Support", "My Rewards"],
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_user():
    return st.session_state.users_db.get(st.session_state.current_user)

def get_group():
    u = get_user()
    return u["group"] if u else "customers"

def login(email, password):
    db = st.session_state.users_db
    if email not in db:
        return False, "No account found with that email."
    if db[email]["password_hash"] != hash_pw(password):
        return False, "Incorrect password."
    return True, ""

def signup(name, email, password):
    db = st.session_state.users_db
    if not name.strip():
        return False, "Please enter your name."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if email in db:
        return False, "An account with this email already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    db[email] = {
        "name": name.strip(),
        "password_hash": hash_pw(password),
        "group": "customers",
        "joined": datetime.now().strftime("%Y-%m-%d"),
    }
    return True, ""

# ─── CSS Factory ──────────────────────────────────────────────────────────────
def inject_css(group="customers"):
    g = GROUPS[group]
    c = g["color"]; ga = g["grad_a"]; gb = g["grad_b"]
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background: #070b0e !important;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d1117 0%, #080c10 100%) !important;
        border-right: 1px solid {c}28 !important;
    }}
    [data-testid="stSidebar"] * {{ color: #cbd5e1 !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    .auth-page-bg {{
        background: radial-gradient(ellipse at 20% 50%, {ga}25 0%, transparent 55%),
                    radial-gradient(ellipse at 80% 15%, {gb}18 0%, transparent 50%),
                    radial-gradient(ellipse at 55% 85%, {ga}12 0%, transparent 45%);
    }}

    .auth-logo {{
        text-align: center; margin-bottom: 26px;
    }}
    .auth-logo-mark {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 58px; height: 58px; border-radius: 18px;
        background: linear-gradient(135deg, {ga}, {gb});
        font-size: 1.7rem; margin-bottom: 12px;
        box-shadow: 0 10px 30px {ga}50;
    }}
    .auth-logo-title {{
        font-size: 1.55rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px;
    }}
    .auth-logo-sub {{
        font-size: 0.75rem; color: #475569; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 2px; margin-top: 3px;
    }}

    .tab-row {{
        display: flex; gap: 4px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 11px; padding: 4px; margin-bottom: 24px;
    }}
    .tab-item {{
        flex: 1; text-align: center; padding: 9px;
        border-radius: 8px; font-size: 0.85rem; font-weight: 500;
        color: #475569;
    }}
    .tab-item.active {{
        background: linear-gradient(135deg, {ga}dd, {gb}cc);
        color: #fff; font-weight: 700;
        box-shadow: 0 4px 14px {ga}40;
    }}

    .cred-box {{
        background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px; padding: 14px 16px; margin-top: 4px;
    }}
    .cred-title {{
        font-size: 0.68rem; color: #334155; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px;
    }}
    .cred-row {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 7px 10px; border-radius: 8px; margin-bottom: 4px;
        background: rgba(255,255,255,0.025);
    }}
    .cred-row:last-child {{ margin-bottom: 0; }}
    .cred-info {{ font-size: 0.78rem; color: #64748b; font-family: 'DM Mono', monospace; }}
    .cred-val {{ color: {c}; }}
    .cred-badge {{
        font-size: 0.65rem; padding: 2px 8px; border-radius: 20px;
        background: {ga}33; border: 1px solid {ga}55; color: {c};
        font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .signup-note {{
        font-size: 0.74rem; color: #475569; margin-top: -4px; margin-bottom: 14px;
        font-family: 'DM Mono', monospace;
        background: rgba(46,204,113,0.06); border: 1px solid rgba(46,204,113,0.15);
        border-radius: 8px; padding: 8px 12px;
    }}

    .app-banner {{
        background: linear-gradient(120deg, {ga}2e 0%, {gb}1a 55%, transparent 100%);
        border: 1px solid {c}2e; border-radius: 18px;
        padding: 22px 28px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 20px;
    }}
    .app-banner-left {{ display: flex; align-items: center; gap: 16px; }}
    .app-banner-icon {{
        width: 50px; height: 50px; border-radius: 14px;
        background: linear-gradient(135deg, {ga}, {gb});
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; box-shadow: 0 8px 22px {ga}44;
    }}
    .app-banner-title {{
        font-size: 1.45rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.4px;
    }}
    .app-banner-sub {{
        font-size: 0.74rem; color: #475569; font-family: 'DM Mono', monospace; margin-top: 2px;
    }}
    .app-banner-badge {{
        padding: 6px 16px; border-radius: 20px;
        background: linear-gradient(135deg, {ga}40, {gb}28);
        border: 1px solid {c}44; color: {c};
        font-size: 0.7rem; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600;
    }}

    .qa-label {{
        font-size: 0.68rem; color: #334155; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;
    }}

    .chat-area {{ display: flex; flex-direction: column; gap: 16px; padding: 6px 2px 80px; min-height: 280px; }}
    .msg-row {{ display: flex; align-items: flex-end; gap: 9px; }}
    .msg-row.user {{ flex-direction: row-reverse; }}
    .msg-av {{
        width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 12px;
    }}
    .msg-av.bot {{ background: linear-gradient(135deg, {ga}55, {gb}44); border: 1px solid {c}33; }}
    .msg-av.user {{ background: linear-gradient(135deg, {ga}44, {gb}33); border: 1px solid {c}33; }}
    .msg-bubble {{
        max-width: 70%; padding: 11px 16px; border-radius: 16px;
        font-size: 0.875rem; line-height: 1.6;
    }}
    .msg-bubble.bot {{
        background: linear-gradient(135deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08); border-bottom-left-radius: 4px; color: #cbd5e1;
    }}
    .msg-bubble.user {{
        background: linear-gradient(135deg, {ga}48, {gb}38);
        border: 1px solid {c}40; border-bottom-right-radius: 4px; color: #f1f5f9;
    }}
    .msg-meta {{ font-size: 0.63rem; color: #2d3748; font-family: 'DM Mono', monospace; margin-top: 4px; }}
    .msg-row.user .msg-meta {{ text-align: right; }}
    .api-tag {{ font-size: 0.66rem; color: {c}77; font-family: 'DM Mono', monospace; margin-bottom: 3px; }}

    .empty-state {{
        text-align: center; padding: 80px 20px;
    }}
    .empty-state-icon {{ font-size: 2.8rem; margin-bottom: 14px; opacity: 0.4; }}
    .empty-state-text {{ font-size: 0.95rem; color: #334155; font-weight: 500; }}
    .empty-state-sub {{ font-size: 0.75rem; color: #1e293b; font-family: 'DM Mono', monospace; margin-top: 6px; }}

    .stTextInput > div > div > input {{
        background: #0f1923 !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 10px !important; color: #e2e8f0 !important;
        font-family: 'Outfit', sans-serif !important; font-size: 0.88rem !important;
        padding: 11px 15px !important;
        caret-color: {c} !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {c}77 !important;
        box-shadow: 0 0 0 3px {ga}1a !important;
        color: #f1f5f9 !important;
        background: #0f1923 !important;
    }}
    .stTextInput > div > div > input:active {{
        color: #f1f5f9 !important;
        background: #0f1923 !important;
    }}
    .stTextInput > label {{ color: #475569 !important; font-size: 0.78rem !important; margin-bottom: 4px !important; }}
    .stTextInput > div > div > input::placeholder {{ color: #3d5166 !important; }}

    .stButton > button {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        color: #64748b !important; border-radius: 9px !important;
        font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important;
        transition: all 0.18s ease !important;
    }}
    .stButton > button:hover {{
        background: {ga}28 !important; border-color: {c}44 !important; color: {c} !important;
    }}
    .primary-btn > button {{
        background: linear-gradient(135deg, {ga}, {gb}) !important;
        border: none !important; color: #fff !important; font-weight: 700 !important;
        border-radius: 11px !important; font-size: 0.92rem !important;
        font-family: 'Outfit', sans-serif !important;
        box-shadow: 0 6px 22px {ga}44 !important; padding: 12px !important;
        letter-spacing: 0.2px !important;
    }}
    .primary-btn > button:hover {{ filter: brightness(1.12) !important; }}
    .send-btn > button {{
        background: linear-gradient(135deg, {ga}, {gb}) !important;
        border: none !important; color: #fff !important; font-weight: 700 !important;
        border-radius: 10px !important; box-shadow: 0 4px 14px {ga}44 !important;
    }}
    .logout-btn > button {{
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.2) !important; color: #f87171 !important;
        border-radius: 9px !important; font-size: 0.78rem !important;
    }}
    .logout-btn > button:hover {{
        background: rgba(239,68,68,0.18) !important; border-color: #f87171 !important;
        color: #fca5a5 !important;
    }}

    .user-card {{
        background: linear-gradient(135deg, {ga}1e, {gb}12);
        border: 1px solid {c}28; border-radius: 12px; padding: 14px 16px;
    }}
    .user-card-name {{ font-size: 0.9rem; font-weight: 700; color: #f1f5f9; }}
    .user-card-email {{ font-size: 0.7rem; color: #475569; font-family: 'DM Mono', monospace; margin-top: 2px; }}
    .user-card-group {{
        display: inline-block; margin-top: 8px; padding: 3px 10px;
        border-radius: 20px; font-size: 0.68rem; font-family: 'DM Mono', monospace;
        background: linear-gradient(135deg, {ga}33, {gb}22);
        border: 1px solid {c}44; color: {c};
        text-transform: uppercase; letter-spacing: 1px;
    }}

    .user-list-item {{
        padding: 8px 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px; font-size: 0.74rem;
    }}

    hr {{ border-color: rgba(255,255,255,0.05) !important; }}
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-thumb {{ background: {c}28; border-radius: 2px; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth_page():
    inject_css("customers")
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    is_login = st.session_state.auth_view == "login"

    _, col, _ = st.columns([1, 1.05, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div class="auth-logo">
            <div class="auth-logo-mark">⬡</div>
            <div class="auth-logo-title">Nexus Portal</div>
            <div class="auth-logo-sub">Secure Access Platform</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tab switcher — real Streamlit buttons, styled as pills ───────────
        st.markdown(f"""
        <style>
        div[data-testid="stHorizontalBlock"]:has(> div > div > div[data-testid="stButton"] > button[kind="secondary"]) {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 5px;
            gap: 4px !important;
        }}
        div[data-testid="column"]:has(button[key="tab_login"]) button,
        div[data-testid="column"]:has(button[key="tab_signup"]) button {{
            border-radius: 10px !important;
            padding: 10px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            height: 42px !important;
        }}
        {"div[data-testid='column']:has(button[key='tab_login']) button" if is_login else "div[data-testid='column']:has(button[key='tab_signup']) button"} {{
            background: linear-gradient(135deg, #1e7e5e, #0a3d2b) !important;
            color: #fff !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 4px 16px rgba(30,126,94,0.4), inset 0 1px 0 rgba(255,255,255,0.12) !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("Sign In", use_container_width=True, key="tab_login"):
                st.session_state.auth_view = "login"
                st.session_state.auth_error = ""
                st.rerun()
        with tc2:
            if st.button("Create Account", use_container_width=True, key="tab_signup"):
                st.session_state.auth_view = "signup"
                st.session_state.auth_error = ""
                st.rerun()

        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
        if st.session_state.auth_success:
            st.success(st.session_state.auth_success)

        # ── LOGIN ──────────────────────────────────────────────────────────
        if is_login:
            email    = st.text_input("Email Address", placeholder="you@example.com", key="li_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Sign In  →", use_container_width=True, key="do_login"):
                ok, err = login(email.strip().lower(), password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email.strip().lower()
                    st.session_state.auth_error = ""
                    st.session_state.auth_success = ""
                    uid = email.strip().lower()
                    if uid not in st.session_state.chats:
                        st.session_state.chats[uid] = []
                    st.rerun()
                else:
                    st.session_state.auth_error = err
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── SIGNUP ─────────────────────────────────────────────────────────
        else:
            name     = st.text_input("Full Name", placeholder="Jane Smith", key="su_name")
            email    = st.text_input("Email Address", placeholder="you@example.com", key="su_email")
            password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="su_pw")
            st.markdown("""
            <div class="signup-note">
                ✦ New accounts are added to the <b style="color:#2ecc71">Customers</b> group by default.
                Contact an admin to change your role.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, key="do_signup"):
                ok, err = signup(name, email.strip().lower(), password)
                if ok:
                    st.session_state.auth_success = f"✓ Account created! Sign in as {email.strip().lower()}"
                    st.session_state.auth_error = ""
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.session_state.auth_error = err
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# APP PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_app():
    user  = get_user()
    group = user["group"]
    g     = GROUPS[group]
    inject_css(group)

    uid = st.session_state.current_user
    if uid not in st.session_state.chats:
        st.session_state.chats[uid] = []
    chat = st.session_state.chats[uid]

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:8px 0 18px;">
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.3px;">⬡ Nexus</div>
            <div style="font-size:0.65rem;color:#1e293b;font-family:'DM Mono',monospace;letter-spacing:2px;text-transform:uppercase;">Portal v1.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="user-card">
            <div class="user-card-name">{user['name']}</div>
            <div class="user-card-email">{uid}</div>
            <div class="user-card-group">{g['icon']} {g['label']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:0.68rem;color:#334155;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">
            Account
        </div>
        <div style="font-size:0.78rem;color:#475569;line-height:2;">
            <span style="color:#2d3748;">Joined</span> &nbsp;<b style="color:#64748b;">{user['joined']}</b><br>
            <span style="color:#2d3748;">Group</span> &nbsp;&nbsp;<b style="color:{g['color']};">{g['label']}</b><br>
            <span style="color:#2d3748;">Msgs</span> &nbsp;&nbsp;&nbsp;<b style="color:#64748b;">{len(chat)//2}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🗑️  Clear Chat", use_container_width=True, key="clear"):
            st.session_state.chats[uid] = []
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("← Sign Out", use_container_width=True, key="logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.auth_error = ""
            st.session_state.auth_success = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Admin sees all users
        if group == "admins":
            st.markdown("---")
            st.markdown("""
            <div style="font-size:0.68rem;color:#334155;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">
                👥 All Users
            </div>
            """, unsafe_allow_html=True)
            for em, u in st.session_state.users_db.items():
                ug = GROUPS[u["group"]]
                st.markdown(f"""
                <div class="user-list-item">
                    <span style="color:#94a3b8;">{ug['icon']} {u['name']}</span>
                    <span style="float:right;font-size:0.65rem;color:{ug['color']};font-family:'DM Mono',monospace;">{ug['label'].upper()}</span><br>
                    <span style="color:#2d3748;font-family:'DM Mono',monospace;font-size:0.66rem;">{em}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── Banner ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="app-banner">
        <div class="app-banner-left">
            <div class="app-banner-icon">{g['icon']}</div>
            <div>
                <div class="app-banner-title">{g['label']} Console</div>
                <div class="app-banner-sub">Welcome back, {user['name'].split()[0]} · {datetime.now().strftime('%A, %b %d %Y')}</div>
            </div>
        </div>
        <div class="app-banner-badge">{g['label'].upper()} · ACTIVE SESSION</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.markdown('<div class="qa-label">Quick Actions</div>', unsafe_allow_html=True)
    actions = QUICK_ACTIONS[group]
    qa_cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with qa_cols[i]:
            if st.button(action, key=f"qa_{action}", use_container_width=True):
                ts = datetime.now().strftime("%H:%M")
                chat.append({"role": "user", "content": action, "time": ts})
                with st.spinner("Fetching from backend..."):
                    reply = FETCH_FN[group](action)
                chat.append({"role": "bot", "content": reply, "time": datetime.now().strftime("%H:%M")})
                st.rerun()

    st.markdown("---")

    # ── Chat ─────────────────────────────────────────────────────────────────
    if not chat:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">{g['icon']}</div>
            <div class="empty-state-text">Start a conversation</div>
            <div class="empty-state-sub">Use quick actions above or type below</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-area">', unsafe_allow_html=True)
        for msg in chat:
            role    = msg["role"]
            content = msg["content"]
            ts      = msg.get("time", "")
            if role == "user":
                st.markdown(f"""
                <div class="msg-row user">
                    <div>
                        <div class="msg-meta">{ts}</div>
                        <div class="msg-bubble user">{content}</div>
                    </div>
                    <div class="msg-av user">👤</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-row bot">
                    <div class="msg-av bot">{g['icon']}</div>
                    <div>
                        <div class="api-tag">◈ backend · {group}</div>
                        <div class="msg-bubble bot">{content}</div>
                        <div class="msg-meta">{ts}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    ic, bc = st.columns([5, 1])
    placeholders = {
        "admins":    "Query logs, manage users, configure system...",
        "internal":  "Ask about policies, tickets, team resources...",
        "customers": "Track orders, get support, check your account...",
    }
    with ic:
        user_input = st.text_input("msg", placeholder=placeholders[group],
                                   label_visibility="collapsed", key="chat_input")
    with bc:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send = st.button("Send ➤", use_container_width=True, key="send_msg")
        st.markdown('</div>', unsafe_allow_html=True)

    if send and user_input.strip():
        ts = datetime.now().strftime("%H:%M")
        chat.append({"role": "user", "content": user_input.strip(), "time": ts})
        with st.spinner("Calling backend API..."):
            reply = FETCH_FN[group](user_input.strip())
        chat.append({"role": "bot", "content": reply, "time": datetime.now().strftime("%H:%M")})
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in and st.session_state.current_user:
    show_app()
else:
    show_auth_page()