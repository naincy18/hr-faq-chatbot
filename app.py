import streamlit as st
from retrieval import PolicyRetriever
from confidence import build_response

st.set_page_config(page_title="HR Policy FAQ Chatbot", page_icon="💬")


@st.cache_resource
def load_retriever():
    return PolicyRetriever()


retriever = load_retriever()

# --- Role selection (sidebar) ---
st.sidebar.title("👤 User Role")
role = st.sidebar.selectbox(
    "Select your role:",
    options=["Employee", "HR Staff", "HR Admin"],
)
st.session_state.role = role  # store current role for use elsewhere in the app

st.sidebar.markdown("---")
st.sidebar.caption(
    "Role determines what you can see:\n"
    "- **Employee**: chat only\n"
    "- **HR Staff**: chat + confidence scores\n"
    "- **HR Admin**: chat + confidence scores + logs access"
)

# --- Admin-only panel placeholder (wired to real logs in Task 7) ---
if role == "HR Admin":
    with st.sidebar.expander("🔐 Admin Panel"):
        st.write("Interaction logs will appear here once logging is implemented (Task 7).")

st.title("💬 HR Policy FAQ Chatbot")
st.caption(f"Ask me about leave, attendance, payroll, benefits, and other HR policies. (Logged in as: **{role}**)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("Type your HR question here...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Checking HR policies..."):
            results = retriever.retrieve(user_question, top_k=1)
            top_result = results[0]
            response = build_response(top_result, user_question)

        if response["handoff"]:
            reply_text = response["answer_text"]
        else:
            reply_text = response["answer_text"]
            reply_text += f"\n\n**Source:** {response['source_reference']} → `{response['policy_id']}`"
            reply_text += f"\n**Form:** {response['related_form']}"

        # Role-based extra info: only HR Staff and HR Admin see the raw confidence score
        if role in ("HR Staff", "HR Admin"):
            reply_text += (
                f"\n\n---\n*[Staff view] Confidence: {response['confidence_level']} "
                f"(score: {response['score']:.3f})*"
            )

        st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})