import datetime
import json
import os
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="Support tickets", page_icon="🎫")

# Top right area with Admin button
col1, col2 = st.columns([0.92, 0.08])

with col1:
    st.title("🎫 상담 신청")

with col2:
    # Admin button
    if st.button("🔒", help="Admin Login", key="admin_btn"):
        st.session_state.show_admin_modal = not st.session_state.get("show_admin_modal", False)

# Initialize session state
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_admin_modal" not in st.session_state:
    st.session_state.show_admin_modal = False

st.write(
    """
    여러분의 이야기를 소중히 듣고 함께 생각해 드립니다.\n
    작은 걱정부터 말하기 어려운 이야기까지, 말하지 못해 쌓인 고민이 있다면 이곳에 남겨 주세요.\n
    여러분의 이야기에 귀 기울이겠습니다. 부담 없이 편하게 상담을 신청해 주세요.
    """
)

# File path for storing tickets
TICKETS_FILE = "tickets.json"
ADMIN_PASSWORD = "qlalfqjsghahfmrpTwl"  # Change this to your desired password

# Load or initialize tickets from file
def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    return {"counter": 0, "tickets": []}

def save_tickets(data):
    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Admin modal
if st.session_state.show_admin_modal:
    if st.session_state.is_admin:
        st.sidebar.success("✅ You are logged in as Admin")
        if st.sidebar.button("Logout"):
            st.session_state.is_admin = False
            st.session_state.show_admin_modal = False
            st.rerun()
    else:
        st.sidebar.header("🔒 Admin Login")
        password = st.sidebar.text_input("Enter admin password:", type="password", key="password_input")
        col_a, col_b = st.sidebar.columns(2)
        with col_a:
            if st.button("Login", key="login_btn"):
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.session_state.show_admin_modal = False
                    st.success("✅ Admin logged in!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        with col_b:
            if st.button("Cancel", key="cancel_btn"):
                st.session_state.show_admin_modal = False
                st.rerun()

# Show a section to add a new ticket.
st.header("상담 신청하기")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("상담하고 싶은 내용을 입력해 주세요.")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted and issue:
    # Create a new ticket
    tickets_data = load_tickets()
    tickets_data["counter"] += 1
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    new_ticket = {
        "ID": f"TICKET-{tickets_data['counter']}",
        "Issue": issue,
        "Status": "Open",
        "Priority": priority,
        "Date Submitted": today,
    }
    
    # Add to tickets list and save to file
    tickets_data["tickets"].append(new_ticket)
    save_tickets(tickets_data)
    
    # Show a little success message only (no details shown)
    st.success("✅ Ticket submitted!")

# Show section to view and edit existing tickets (only for admin)
if st.session_state.is_admin:
    st.divider()
    st.header("📋 Manage Tickets (Admin Only)")
    
    tickets_data = load_tickets()
    tickets = tickets_data["tickets"]
    
    if tickets:
        st.info("You can edit tickets below. Changes are saved automatically.", icon="✍️")
        
        # Create editable dataframe
        edited_tickets = st.data_editor(
            tickets,
            use_container_width=True,
            hide_index=True,
            key="tickets_editor",
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Ticket status",
                    options=["Open", "In Progress", "Closed"],
                    required=True,
                ),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    help="Priority",
                    options=["High", "Medium", "Low"],
                    required=True,
                ),
                "ID": st.column_config.TextColumn(disabled=True),
                "Date Submitted": st.column_config.TextColumn(disabled=True),
            },
        )
        
        # Save edited tickets
        if st.button("Save Changes"):
            tickets_data["tickets"] = edited_tickets
            save_tickets(tickets_data)
            st.success("✅ Changes saved!")
    else:
        st.info("No tickets submitted yet.")
