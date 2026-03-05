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

# ─── User Database ────────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

DEFAULT_USERS = {
    "admin@nexus.io":  {"name": "Alex Admin",     "password_hash": hash_pw("admin123"), "group": "admins",    "joined": "2024-01-10"},
    "staff@nexus.io":  {"name": "Sam Internal",   "password_hash": hash_pw("staff123"), "group": "internal",  "joined": "2024-03-22"},
    "user@nexus.io":   {"name": "Casey Customer", "password_hash": hash_pw("user123"),  "group": "customers", "joined": "2025-01-05"},
}

GROUPS = {
    "admins":    {"label": "Admin",         "icon": "🛡️", "color": "#e74c3c", "grad_a": "#c0392b", "grad_b": "#8e1a0e"},
    "internal":  {"label": "Internal User", "icon": "🏢", "color": "#3498db", "grad_a": "#1a6b9a", "grad_b": "#0d3b5e"},
    "customers": {"label": "Customer",      "icon": "🌟", "color": "#2ecc71", "grad_a": "#1e7e5e", "grad_b": "#0a3d2b"},
}

# ─── Theme Palettes ───────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg":           "#070b0e",
        "sidebar_bg":   "#0d1117",
        "surface":      "rgba(255,255,255,0.04)",
        "surface2":     "rgba(255,255,255,0.025)",
        "border":       "rgba(255,255,255,0.08)",
        "border2":      "rgba(255,255,255,0.05)",
        "text_primary": "#f1f5f9",
        "text_sec":     "#94a3b8",
        "text_muted":   "#475569",
        "text_faint":   "#334155",
        "input_bg":     "#0f1923",
        "input_border": "rgba(255,255,255,0.09)",
        "input_text":   "#e2e8f0",
        "placeholder":  "#3d5166",
        "msg_bot_bg":   "linear-gradient(135deg,rgba(255,255,255,0.045),rgba(255,255,255,0.02))",
        "msg_bot_bdr":  "rgba(255,255,255,0.08)",
        "msg_bot_text": "#cbd5e1",
        "msg_meta":     "#2d3748",
        "hr":           "rgba(255,255,255,0.05)",
        "sidebar_text": "#cbd5e1",
        "toggle_icon":  "🌙",
        "toggle_label": "Dark mode",
        "user_list_bg": "rgba(255,255,255,0.025)",
        "user_list_bdr":"rgba(255,255,255,0.05)",
    },
    "light": {
        "bg":           "#f0f4f8",
        "sidebar_bg":   "#ffffff",
        "surface":      "rgba(0,0,0,0.03)",
        "surface2":     "rgba(0,0,0,0.04)",
        "border":       "rgba(0,0,0,0.09)",
        "border2":      "rgba(0,0,0,0.07)",
        "text_primary": "#0f172a",
        "text_sec":     "#334155",
        "text_muted":   "#64748b",
        "text_faint":   "#94a3b8",
        "input_bg":     "#ffffff",
        "input_border": "rgba(0,0,0,0.12)",
        "input_text":   "#0f172a",
        "placeholder":  "#94a3b8",
        "msg_bot_bg":   "linear-gradient(135deg,rgba(255,255,255,0.9),rgba(241,245,249,0.95))",
        "msg_bot_bdr":  "rgba(0,0,0,0.08)",
        "msg_bot_text": "#334155",
        "msg_meta":     "#94a3b8",
        "hr":           "rgba(0,0,0,0.07)",
        "sidebar_text": "#334155",
        "toggle_icon":  "☀️",
        "toggle_label": "Light mode",
        "user_list_bg": "rgba(0,0,0,0.03)",
        "user_list_bdr":"rgba(0,0,0,0.07)",
    },
}

# ─── Session State ────────────────────────────────────────────────────────────
for k, v in {
    "users_db": DEFAULT_USERS.copy(),
    "logged_in": False,
    "current_user": None,
    "auth_view": "login",
    "chats": {},
    "auth_error": "",
    "auth_success": "",
    "theme": "dark",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Dummy Backends ───────────────────────────────────────────────────────────
def dummy_fetch_admin(q):
    time.sleep(0.7)
    return random.choice([
        f"[ADMIN API] All 12 services operational. Query '{q}' processed.",
        f"[ADMIN API] 3 audit log entries matched '{q}'. Zero anomalies.",
        f"[ADMIN API] Access tokens refreshed. Permissions matrix updated.",
        f"[ADMIN API] Uptime 99.4% over 30 days. Dashboard refreshed.",
        f"[ADMIN API] Config change staged. Pending security approval.",
    ])

def dummy_fetch_internal(q):
    time.sleep(0.5)
    return random.choice([
        f"[INTERNAL API] 5 KB articles matched '{q}'.",
        f"[INTERNAL API] Ticket TKT-{random.randint(1000,9999)} created.",
        f"[INTERNAL API] Policy doc retrieved. Updated 2024-11-15.",
        f"[INTERNAL API] HR lookup done. 3 onboarding items pending.",
        f"[INTERNAL API] Sprint board: 4 open, 1 blocked.",
    ])

def dummy_fetch_customer(q):
    time.sleep(0.4)
    return random.choice([
        f"[CUSTOMER API] Order #ORD-{random.randint(10000,99999)}. Delivery: Tomorrow.",
        f"[CUSTOMER API] Account active. Last login: {datetime.now().strftime('%b %d, %Y')}.",
        f"[CUSTOMER API] Support ticket submitted. Response within 24 hrs.",
        f"[CUSTOMER API] Loyalty balance: {random.randint(500,5000)} pts.",
        f"[CUSTOMER API] FAQ match for '{q}'. Connect to live agent?",
    ])

FETCH_FN     = {"admins": dummy_fetch_admin, "internal": dummy_fetch_internal, "customers": dummy_fetch_customer}
QUICK_ACTIONS = {
    "admins":    ["View Audit Logs", "User Permissions", "System Health", "Config Settings"],
    "internal":  ["Open Ticket", "Search KB", "HR Portal", "Team Board"],
    "customers": ["Track Order", "My Account", "Support", "My Rewards"],
}
PLACEHOLDERS = {
    "admins":    "Query logs, manage users, configure system...",
    "internal":  "Ask about policies, tickets, team resources...",
    "customers": "Track orders, get support, check your account...",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_user():  return st.session_state.users_db.get(st.session_state.current_user)
def get_group(): u = get_user(); return u["group"] if u else "customers"
def T():         return THEMES[st.session_state.theme]

def login(email, password):
    db = st.session_state.users_db
    if email not in db: return False, "No account found with that email."
    if db[email]["password_hash"] != hash_pw(password): return False, "Incorrect password."
    return True, ""

def signup(name, email, password):
    db = st.session_state.users_db
    if not name.strip(): return False, "Please enter your name."
    if "@" not in email or "." not in email: return False, "Please enter a valid email address."
    if email in db: return False, "An account with this email already exists."
    if len(password) < 6: return False, "Password must be at least 6 characters."
    db[email] = {"name": name.strip(), "password_hash": hash_pw(password),
                 "group": "customers", "joined": datetime.now().strftime("%Y-%m-%d")}
    return True, ""

# ─── CSS ─────────────────────────────────────────────────────────────────────
def inject_css(group="customers"):
    g  = GROUPS[group]
    c  = g["color"]; ga = g["grad_a"]; gb = g["grad_b"]
    t  = T()
    is_dark = st.session_state.theme == "dark"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
    *, *::before, *::after {{ box-sizing: border-box; }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background: {t['bg']} !important;
        color: {t['text_primary']};
        font-family: 'Outfit', sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background: {t['sidebar_bg']} !important;
        border-right: 1px solid {c}28 !important;
    }}
    [data-testid="stSidebar"] * {{ color: {t['sidebar_text']} !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    /* ── Auth ── */
    .auth-logo {{ text-align: center; margin-bottom: 26px; }}
    .auth-logo-mark {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 58px; height: 58px; border-radius: 18px;
        background: linear-gradient(135deg, {ga}, {gb});
        font-size: 1.7rem; margin-bottom: 12px;
        box-shadow: 0 10px 30px {ga}50;
    }}
    .auth-logo-title {{ font-size: 1.55rem; font-weight: 800; color: {t['text_primary']}; letter-spacing: -0.5px; }}
    .auth-logo-sub   {{ font-size: 0.75rem; color: {t['text_muted']}; font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 2px; margin-top: 3px; }}

    .signup-note {{
        font-size: 0.74rem; color: {t['text_muted']}; margin-top: -4px; margin-bottom: 14px;
        font-family: 'DM Mono', monospace;
        background: rgba(46,204,113,0.06); border: 1px solid rgba(46,204,113,0.18);
        border-radius: 8px; padding: 8px 12px;
    }}

    /* ── Banner ── */
    .app-banner {{
        background: linear-gradient(120deg, {ga}{'2e' if is_dark else '18'} 0%, {gb}{'1a' if is_dark else '0e'} 55%, transparent 100%);
        border: 1px solid {c}{'2e' if is_dark else '33'}; border-radius: 18px;
        padding: 22px 28px; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 20px;
    }}
    .app-banner-left  {{ display: flex; align-items: center; gap: 16px; }}
    .app-banner-icon  {{
        width: 50px; height: 50px; border-radius: 14px;
        background: linear-gradient(135deg, {ga}, {gb});
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; box-shadow: 0 8px 22px {ga}44;
    }}
    .app-banner-title {{ font-size: 1.45rem; font-weight: 800; color: {t['text_primary']}; letter-spacing: -0.4px; }}
    .app-banner-sub   {{ font-size: 0.74rem; color: {t['text_muted']}; font-family: 'DM Mono', monospace; margin-top: 2px; }}
    .app-banner-badge {{
        padding: 6px 16px; border-radius: 20px;
        background: linear-gradient(135deg, {ga}40, {gb}28);
        border: 1px solid {c}44; color: {c};
        font-size: 0.7rem; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600;
    }}

    /* ── Quick actions label ── */
    .qa-label {{ font-size: 0.68rem; color: {t['text_faint']}; font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }}

    /* ── Chat ── */
    .chat-area {{ display: flex; flex-direction: column; gap: 16px; padding: 6px 2px 80px; min-height: 280px; }}
    .msg-row {{ display: flex; align-items: flex-end; gap: 9px; width: 100%; }}
    .msg-row.user {{ flex-direction: row-reverse; }}
    .msg-row > div {{ max-width: 66%; }}
    .msg-av {{
        width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 12px;
    }}
    .msg-av.bot  {{ background: linear-gradient(135deg, {ga}55, {gb}44); border: 1px solid {c}33; }}
    .msg-av.user {{ background: linear-gradient(135deg, {ga}44, {gb}33); border: 1px solid {c}33; }}
    .msg-bubble {{
        width: fit-content;
        max-width: 100%;
        min-width: 0;
        padding: 10px 16px; border-radius: 16px;
        font-size: 0.875rem; line-height: 1.55; word-break: break-word;
        white-space: pre-wrap; display: block;
    }}
    .msg-bubble.bot  {{
        background: {t['msg_bot_bg']}; border: 1px solid {t['msg_bot_bdr']};
        border-bottom-left-radius: 4px; color: {t['msg_bot_text']};
    }}
    .msg-bubble.user {{
        background: linear-gradient(135deg, {ga}48, {gb}38);
        border: 1px solid {c}40; border-bottom-right-radius: 4px; color: #f1f5f9;
        margin-left: auto;
    }}
    .msg-meta {{ font-size: 0.63rem; color: {t['msg_meta']}; font-family: 'DM Mono', monospace; margin-top: 4px; }}
    .msg-row.user .msg-meta {{ text-align: right; }}
    .api-tag {{ font-size: 0.66rem; color: {c}88; font-family: 'DM Mono', monospace; margin-bottom: 3px; }}

    /* ── Clear chat bar ── */
    .chat-header {{
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 12px;
    }}
    .chat-header-label {{
        font-size: 0.68rem; color: {t['text_faint']}; font-family: 'DM Mono', monospace;
        text-transform: uppercase; letter-spacing: 1.5px;
    }}
    .clear-btn {{
        font-size: 0.7rem; color: {t['text_muted']}; font-family: 'DM Mono', monospace;
        cursor: pointer; padding: 3px 10px; border-radius: 6px;
        border: 1px solid {t['border2']}; background: {t['surface2']};
        transition: all 0.15s;
    }}
    .clear-btn:hover {{ color: #ef4444; border-color: #ef444455; background: rgba(239,68,68,0.06); }}

    /* ── Empty state ── */
    .empty-state {{ text-align: center; padding: 80px 20px; }}
    .empty-state-icon {{ font-size: 2.8rem; margin-bottom: 14px; opacity: 0.3; }}
    .empty-state-text {{ font-size: 0.95rem; color: {t['text_muted']}; font-weight: 500; }}
    .empty-state-sub  {{ font-size: 0.75rem; color: {t['text_faint']}; font-family: 'DM Mono', monospace; margin-top: 6px; }}

    /* ── Inputs ── */
    .stTextInput > div > div > input {{
        background: {t['input_bg']} !important;
        border: 1px solid {t['input_border']} !important;
        border-radius: 10px !important; color: {t['input_text']} !important;
        font-family: 'Outfit', sans-serif !important; font-size: 0.88rem !important;
        padding: 11px 15px !important; caret-color: {c} !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {c}88 !important; box-shadow: 0 0 0 3px {ga}22 !important;
        color: {t['input_text']} !important; background: {t['input_bg']} !important;
    }}
    .stTextInput > label {{ color: {t['text_muted']} !important; font-size: 0.78rem !important; margin-bottom: 4px !important; }}
    .stTextInput > div > div > input::placeholder {{ color: {t['placeholder']} !important; }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {t['surface']} !important;
        border: 1px solid {t['border']} !important;
        color: {t['text_muted']} !important; border-radius: 9px !important;
        font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important;
        transition: all 0.18s ease !important;
    }}
    .stButton > button:hover {{
        background: {ga}22 !important; border-color: {c}55 !important; color: {c} !important;
    }}
    .primary-btn > button {{
        background: linear-gradient(135deg, {ga}, {gb}) !important;
        border: none !important; color: #fff !important; font-weight: 700 !important;
        border-radius: 11px !important; font-size: 0.92rem !important;
        font-family: 'Outfit', sans-serif !important;
        box-shadow: 0 6px 22px {ga}44 !important; padding: 12px !important;
    }}
    .primary-btn > button:hover {{ filter: brightness(1.1) !important; }}
    .send-btn > button {{
        background: linear-gradient(135deg, {ga}, {gb}) !important;
        border: none !important; color: #fff !important; font-weight: 700 !important;
        border-radius: 10px !important; box-shadow: 0 4px 14px {ga}44 !important;
    }}
    .logout-btn > button {{
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.2) !important; color: #ef4444 !important;
        border-radius: 9px !important;
    }}
    .logout-btn > button:hover {{
        background: rgba(239,68,68,0.15) !important; border-color: #ef4444 !important;
    }}
    .theme-btn > button {{
        background: {t['surface2']} !important;
        border: 1px solid {t['border2']} !important;
        color: {t['text_sec']} !important; border-radius: 20px !important;
        font-size: 0.78rem !important; padding: 6px 14px !important;
        font-family: 'Outfit', sans-serif !important;
    }}
    .theme-btn > button:hover {{
        background: {ga}18 !important; border-color: {c}44 !important; color: {c} !important;
    }}

    /* ── Sidebar cards ── */
    .user-card {{
        background: linear-gradient(135deg, {ga}{'1e' if is_dark else '12'}, {gb}{'12' if is_dark else '08'});
        border: 1px solid {c}28; border-radius: 12px; padding: 14px 16px;
    }}
    .user-card-name  {{ font-size: 0.9rem; font-weight: 700; color: {t['text_primary']}; }}
    .user-card-email {{ font-size: 0.7rem; color: {t['text_muted']}; font-family: 'DM Mono', monospace; margin-top: 2px; }}
    .user-card-group {{
        display: inline-block; margin-top: 8px; padding: 3px 10px;
        border-radius: 20px; font-size: 0.68rem; font-family: 'DM Mono', monospace;
        background: linear-gradient(135deg, {ga}33, {gb}22);
        border: 1px solid {c}44; color: {c};
        text-transform: uppercase; letter-spacing: 1px;
    }}
    .user-list-item {{
        padding: 8px 10px; margin-bottom: 5px;
        background: {t['user_list_bg']}; border: 1px solid {t['user_list_bdr']};
        border-radius: 8px; font-size: 0.74rem;
    }}

    hr {{ border-color: {t['hr']} !important; }}
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-thumb {{ background: {c}28; border-radius: 2px; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth_page():
    inject_css("customers")
    t       = T()
    is_dark = st.session_state.theme == "dark"
    is_login = st.session_state.auth_view == "login"
    ga = GROUPS["customers"]["grad_a"]
    gb = GROUPS["customers"]["grad_b"]

    st.markdown("""
    <style>
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Theme toggle — top right ─────────────────────────────────────────────
    _, tr_col = st.columns([8, 1])
    with tr_col:
        st.markdown('<div class="theme-btn">', unsafe_allow_html=True)
        if st.button("☀️" if is_dark else "🌙", key="auth_theme", use_container_width=True):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Centered card ────────────────────────────────────────────────────────
    _, col, _ = st.columns([1, 1.05, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo
        st.markdown(f"""
        <div class="auth-logo">
            <div class="auth-logo-mark">⬡</div>
            <div class="auth-logo-title">Nexus Portal</div>
            <div class="auth-logo-sub">Secure Access Platform</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tab switcher ──────────────────────────────────────────────────
        st.markdown(f"""
        <style>
        /* Style the tab button columns - first stHorizontalBlock in auth area */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type {{
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 14px;
            padding: 5px;
            gap: 5px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type button {{
            border-radius: 10px !important;
            border: none !important;
            background: transparent !important;
            color: {t['text_muted']} !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            box-shadow: none !important;
            padding: 10px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"]:nth-child({'1' if is_login else '2'}) button {{
            background: linear-gradient(135deg, {ga}, {gb}) !important;
            color: #fff !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px {ga}44 !important;
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

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.auth_error:   st.error(st.session_state.auth_error)
        if st.session_state.auth_success: st.success(st.session_state.auth_success)

        # ── LOGIN ─────────────────────────────────────────────────────────
        if is_login:
            email    = st.text_input("Email Address", placeholder="you@example.com", key="li_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Sign In  →", use_container_width=True, key="do_login"):
                ok, err = login(email.strip().lower(), password)
                if ok:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = email.strip().lower()
                    st.session_state.auth_error   = ""
                    st.session_state.auth_success = ""
                    uid = email.strip().lower()
                    if uid not in st.session_state.chats:
                        st.session_state.chats[uid] = []
                    st.rerun()
                else:
                    st.session_state.auth_error = err
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── SIGNUP ────────────────────────────────────────────────────────
        else:
            name     = st.text_input("Full Name",     placeholder="Jane Smith",          key="su_name")
            email    = st.text_input("Email Address", placeholder="you@example.com",     key="su_email")
            password = st.text_input("Password",      placeholder="Min. 6 characters",   key="su_pw", type="password")
            st.markdown("""
            <div class="signup-note">
                ✦ New accounts are added to the <b style="color:#2ecc71">Customers</b> group by default.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, key="do_signup"):
                ok, err = signup(name, email.strip().lower(), password)
                if ok:
                    st.session_state.auth_success = f"✓ Account created! Sign in as {email.strip().lower()}"
                    st.session_state.auth_error   = ""
                    st.session_state.auth_view    = "login"
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
    t       = T()
    is_dark = st.session_state.theme == "dark"

    uid = st.session_state.current_user
    if uid not in st.session_state.chats:
        st.session_state.chats[uid] = []
    chat = st.session_state.chats[uid]

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:8px 0 18px;">
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:800;color:{t['text_primary']};letter-spacing:-0.3px;">⬡ Nexus</div>
            <div style="font-size:0.65rem;color:{t['text_faint']};font-family:'DM Mono',monospace;letter-spacing:2px;text-transform:uppercase;">Portal v1.0</div>
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
        <div style="font-size:0.68rem;color:{t['text_faint']};font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">Account</div>
        <div style="font-size:0.78rem;color:{t['text_muted']};line-height:2;">
            <span style="color:{t['text_faint']};">Joined</span> &nbsp;<b style="color:{t['text_sec']};">{user['joined']}</b><br>
            <span style="color:{t['text_faint']};">Group</span> &nbsp;&nbsp;<b style="color:{g['color']};">{g['label']}</b><br>
            <span style="color:{t['text_faint']};">Msgs</span> &nbsp;&nbsp;&nbsp;<b style="color:{t['text_sec']};">{len(chat)//2}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Theme toggle in sidebar
        st.markdown('<div class="theme-btn">', unsafe_allow_html=True)
        if st.button(f"{'☀️ Light mode' if is_dark else '🌙 Dark mode'}", key="app_theme", use_container_width=True):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️  Clear Chat", use_container_width=True, key="clear"):
            st.session_state.chats[uid] = []
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("← Sign Out", use_container_width=True, key="logout"):
            st.session_state.logged_in    = False
            st.session_state.current_user = None
            st.session_state.auth_error   = ""
            st.session_state.auth_success = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Admin sees all users
        if group == "admins":
            st.markdown("---")
            st.markdown(f"""
            <div style="font-size:0.68rem;color:{t['text_faint']};font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">
                👥 All Users
            </div>
            """, unsafe_allow_html=True)
            for em, u in st.session_state.users_db.items():
                ug = GROUPS[u["group"]]
                st.markdown(f"""
                <div class="user-list-item">
                    <span style="color:{t['text_sec']};">{ug['icon']} {u['name']}</span>
                    <span style="float:right;font-size:0.65rem;color:{ug['color']};font-family:'DM Mono',monospace;">{ug['label'].upper()}</span><br>
                    <span style="color:{t['text_faint']};font-family:'DM Mono',monospace;font-size:0.66rem;">{em}</span>
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
        <div class="app-banner-badge">{g['label'].upper()} · ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.markdown('<div class="qa-label">Quick Actions</div>', unsafe_allow_html=True)
    qa_cols = st.columns(len(QUICK_ACTIONS[group]))
    for i, action in enumerate(QUICK_ACTIONS[group]):
        with qa_cols[i]:
            if st.button(action, key=f"qa_{action}", use_container_width=True):
                ts = datetime.now().strftime("%H:%M")
                chat.append({"role": "user", "content": action, "time": ts})
                with st.spinner("Fetching from backend..."):
                    reply = FETCH_FN[group](action)
                chat.append({"role": "bot", "content": reply, "time": datetime.now().strftime("%H:%M")})
                st.rerun()

    st.markdown("---")

    # ── Chat header with clear button ────────────────────────────────────────
    ch1, ch2 = st.columns([6, 1])
    with ch1:
        st.markdown(f'<div class="qa-label" style="margin-top:6px;">Conversation</div>', unsafe_allow_html=True)
    with ch2:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🗑 Clear", key="clear_chat_inline", use_container_width=True):
            st.session_state.chats[uid] = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chat messages ─────────────────────────────────────────────────────────
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
            role, content, ts = msg["role"], msg["content"], msg.get("time", "")
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
    with ic:
        user_input = st.text_input("msg", placeholder=PLACEHOLDERS[group],
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
