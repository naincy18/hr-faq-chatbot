import streamlit as st
import pandas as pd
from retrieval import PolicyRetriever
from confidence import build_response
from logger import init_db, log_interaction, get_all_logs, get_stats, log_escalation, get_urgent_escalations
from auth import verify_admin_login

st.set_page_config(page_title="HR Policy FAQ Chatbot", page_icon="💬", layout="centered")

init_db()

# Contact details for urgent escalation -- replace with your real demo number
URGENT_CONTACT_PHONE = "+91-89798-21876"
URGENT_CONTACT_LABEL = "HR Immediate Helpline"
NON_URGENT_CONTACT_EMAIL = "hr-support@company.com"

# ------------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.app-header {
    background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
    padding: 28px 24px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid #DEE2E6;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    animation: fadeInDown 0.6s ease-out;
}
.app-header h1 {
    color: #1A1A1A;
    font-size: 26px;
    font-weight: 700;
    margin: 0;
}
.app-header p {
    color: #495057;
    font-size: 14px;
    margin-top: 6px;
}

.role-badge {
    display: inline-block;
    background: #1A1A1A;
    color: white;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 10px;
}

.stChatMessage {
    animation: fadeInUp 0.35s ease-out;
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    margin-top: 8px;
    margin-right: 6px;
}
.badge-high { background: #DCFCE7; color: #166534; }
.badge-medium { background: #FEF9C3; color: #854D0E; }
.badge-low { background: #FEE2E2; color: #991B1B; }
.badge-source { background: #E0E7FF; color: #3730A3; }
.badge-form { background: #F3E8FF; color: #6B21A8; }

.handoff-card {
    background: #FEF2F2;
    border-left: 4px solid #EF4444;
    padding: 12px 16px;
    border-radius: 8px;
    animation: shake 0.4s ease-in-out;
}
.urgency-card {
    background: #FFF7ED;
    border-left: 4px solid #F97316;
    padding: 14px 16px;
    border-radius: 8px;
    margin-top: 10px;
    animation: fadeInUp 0.3s ease-out;
}
.escalate-card {
    background: #FEE2E2;
    border-left: 4px solid #DC2626;
    padding: 14px 16px;
    border-radius: 8px;
    animation: shake 0.4s ease-in-out;
}
.calm-card {
    background: #ECFDF5;
    border-left: 4px solid #10B981;
    padding: 14px 16px;
    border-radius: 8px;
}

section[data-testid="stSidebar"] {
    background: #FAFAFF;
}
.call-link {
    color: #B91C1C;
    font-weight: 700;
    text-decoration: underline;
    font-size: 15px;
}
.call-link:hover {
    color: #7F1D1D;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-4px); }
    75% { transform: translateX(4px); }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_retriever():
    return PolicyRetriever()


retriever = load_retriever()

# ------------------------------------------------------------------
# Sidebar: Role selection + Admin login
# ------------------------------------------------------------------
st.sidebar.markdown("### 👤 User Role")
role_choice = st.sidebar.selectbox(
    "Select your role:",
    options=["Employee", "HR Staff", "HR Admin"],
    label_visibility="collapsed",
)

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if role_choice == "HR Admin":
    if not st.session_state.admin_authenticated:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**🔒 HR Admin Login**")
        username = st.sidebar.text_input("Username", key="admin_username")
        password = st.sidebar.text_input("Password", type="password", key="admin_password")

        if st.sidebar.button("Log in", use_container_width=True):
            if verify_admin_login(username, password):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect username or password.")

        role = "Employee"
    else:
        role = "HR Admin"
        st.sidebar.success("Logged in as HR Admin ✅")
        if st.sidebar.button("Log out", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
else:
    st.session_state.admin_authenticated = False
    role = role_choice

st.session_state.role = role

st.sidebar.markdown("---")
st.sidebar.caption(
    "Role determines what you can see:\n"
    "- **Employee**: chat only\n"
    "- **HR Staff**: chat + confidence scores\n"
    "- **HR Admin**: chat + confidence scores + logs access (login required)"
)

# --- Admin Panel ---
if role == "HR Admin":
    with st.sidebar.expander("🔐 Admin Panel", expanded=True):
        stats = get_stats()
        st.metric("Total questions", stats["total"])
        st.metric("Handoff rate", f"{stats['handoff_rate']:.1f}%")

        st.markdown("**Recent logs**")
        logs = get_all_logs()
        if logs:
            logs_df = pd.DataFrame(logs)
            st.dataframe(
                logs_df[["timestamp", "role", "question", "policy_id", "confidence_level", "score", "handoff"]],
                height=250,
            )
        else:
            st.caption("No interactions logged yet.")

        st.markdown("**🚨 Urgent escalations**")
        urgent = get_urgent_escalations()
        if urgent:
            st.dataframe(pd.DataFrame(urgent)[["timestamp", "role", "question"]], height=150)
        else:
            st.caption("No urgent escalations yet.")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state.awaiting_urgency = False
    st.rerun()

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(f"""
<div class="app-header">
    <h1>💬 HR Policy FAQ Chatbot</h1>
    <p>Ask me about leave, attendance, payroll, benefits, and other HR policies.</p>
    <span class="role-badge">Logged in as: {role}</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Session state init
# ------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_urgency" not in st.session_state:
    st.session_state.awaiting_urgency = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# ------------------------------------------------------------------
# Suggested question chips (only shown before the first message)
# ------------------------------------------------------------------
clicked = None
if len(st.session_state.messages) == 0:
    st.markdown("**Try asking:**")
    suggestions = [
        "How many annual leave days do I get?",
        "Can I work from home?",
        "Do I need a medical certificate for sick leave?",
        "What is the notice period for resignation?",
    ]
    cols = st.columns(2)
    for i, sug in enumerate(suggestions):
        if cols[i % 2].button(sug, use_container_width=True, key=f"sug_{i}"):
            clicked = sug

# ------------------------------------------------------------------
# Chat history
# ------------------------------------------------------------------
for message in st.session_state.messages:
    avatar = "🙋" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

# ------------------------------------------------------------------
# Urgency follow-up (shown only right after a handoff)
# ------------------------------------------------------------------
if st.session_state.awaiting_urgency:
    st.markdown("""
    <div class="urgency-card">
    ⏱️ <b>Is this urgent and do you need to speak to someone right now?</b>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        urgent_clicked = st.button("🚨 Yes, it's urgent", use_container_width=True)
    with col2:
        not_urgent_clicked = st.button("🙂 No, I can wait", use_container_width=True)

    if urgent_clicked:
        log_escalation(role, st.session_state.pending_question, is_urgent=True)
        # tel: link format needs no spaces/dashes for best cross-device compatibility
        tel_href = URGENT_CONTACT_PHONE.replace(" ", "").replace("-", "")
        msg = f"""<div class="escalate-card">
📞 <b>Connecting you to a live HR agent now.</b><br>
Please call <a href="tel:{tel_href}" class="call-link">{URGENT_CONTACT_PHONE}</a>
({URGENT_CONTACT_LABEL}) — tap the number to call immediately.
</div>"""
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.awaiting_urgency = False
        st.rerun()

    if not_urgent_clicked:
        log_escalation(role, st.session_state.pending_question, is_urgent=False)
        msg = f"""<div class="calm-card">
👍 No problem. Your question has been logged for HR follow-up.<br>
You can also reach us anytime at <b>{NON_URGENT_CONTACT_EMAIL}</b> or visit the HR office, 10 AM–5 PM on working days.
</div>"""
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.awaiting_urgency = False
        st.rerun()

# ------------------------------------------------------------------
# Input handling (typed or clicked suggestion)
# ------------------------------------------------------------------
user_question = st.chat_input("Type your HR question here...")
if clicked:
    user_question = clicked

if user_question:
    user_question = user_question.strip()

    if len(user_question) < 3:
        st.session_state.messages.append({"role": "user", "content": user_question})
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Could you provide a bit more detail in your question so I can help? 🙂"
        })
        st.rerun()

    else:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(user_question)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔎 Checking HR policies..."):
                results = retriever.retrieve(user_question, top_k=1)
                top_result = results[0]
                response = build_response(top_result, user_question)
                log_interaction(role, user_question, response)

            if response["handoff"]:
                reply_text = f"""<div class="handoff-card">
⚠️ {response['answer_text']}
</div>"""
                st.session_state.awaiting_urgency = True
                st.session_state.pending_question = user_question
            else:
                reply_text = response["answer_text"]
                reply_text += (
                    f"\n\n<span class='badge badge-source'>📄 {response['source_reference']} "
                    f"→ {response['policy_id']}</span>"
                    f"<span class='badge badge-form'>📝 {response['related_form']}</span>"
                )

                if role in ("HR Staff", "HR Admin"):
                    badge_class = f"badge-{response['confidence_level']}"
                    reply_text += (
                        f"<span class='badge {badge_class}'>"
                        f"🎯 {response['confidence_level'].upper()} "
                        f"({response['score']:.2f})</span>"
                    )

            st.markdown(reply_text, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()









