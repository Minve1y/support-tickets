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
    if st.button("❤️", help="관리자 로그인", key="admin_btn"):
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
        st.sidebar.header("❤️ 관리자 로그인")
        password = st.sidebar.text_input("관리자 비밀번호를 입력해 주세요:", type="password", key="password_input")
        col_a, col_b = st.sidebar.columns(2)
        with col_a:
            if st.button("로그인", key="login_btn"):
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.session_state.show_admin_modal = False
                    st.success("✅ Admin logged in!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        with col_b:
            if st.button("취소", key="cancel_btn"):
                st.session_state.show_admin_modal = False
                st.rerun()

# Show a section to add a new ticket.
st.header("상담 신청하기")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("상담하고 싶은 내용을 입력해 주세요.")
    contact_info = st.text_input("연락 가능한 정보를 입력해 주세요. (예: 이메일, 전화번호, 인스타그램 등)")
    submitted = st.form_submit_button("제출")

if submitted and issue:
    # Create a new ticket
    tickets_data = load_tickets()
    tickets_data["counter"] += 1
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    new_ticket = {
        "번호": tickets_data["counter"],
        "상담 신청 내용": issue,
        "연락처": contact_info,
        "신청 날짜": today,
        "상태": "접수",
    }
    
    # Add to tickets list and save to file
    tickets_data["tickets"].append(new_ticket)
    save_tickets(tickets_data)
    
    # Show a little success message only (no details shown)
    st.success("✅ 상담 신청이 완료되었습니다.")

# Show section to view and edit existing tickets (only for admin)
if st.session_state.is_admin:
    st.divider()
    st.header("📋 상담 신청 내역 (관리자용)")
    
    tickets_data = load_tickets()
    tickets = tickets_data["tickets"]
    
    if tickets:
        st.info("상태만 수정할 수 있습니다.", icon="✍️")
        
        # Reorder columns: 번호, 상담 신청 내용, 연락처, 신청 날짜, 상태
        tickets_reordered = []
        for ticket in tickets:
            # Convert old format to new format if needed
            if "번호" not in ticket:
                # Old format conversion
                ticket_num = int(ticket.get("ID", "TICKET-0").split("-")[1])
                reordered = {
                    "번호": ticket_num,
                    "상담 신청 내용": ticket.get("Issue", ""),
                    "연락처": ticket.get("Contact", ""),
                    "신청 날짜": ticket.get("Date Submitted", ""),
                    "상태": "완료" if ticket.get("Status") == "Closed" else ("진행중" if ticket.get("Status") == "In Progress" else "접수"),
                }
            else:
                # New format
                reordered = {
                    "번호": ticket["번호"],
                    "상담 신청 내용": ticket["상담 신청 내용"],
                    "연락처": ticket["연락처"],
                    "신청 날짜": ticket["신청 날짜"],
                    "상태": ticket["상태"],
                }
            tickets_reordered.append(reordered)
        
        # Create editable dataframe with limited editing
        edited_tickets = st.data_editor(
            tickets_reordered,
            use_container_width=True,
            hide_index=True,
            key="tickets_editor",
            column_config={
                "번호": st.column_config.NumberColumn("번호", width="small"),
                "상담 신청 내용": st.column_config.TextColumn("상담 신청 내용", width="large", disabled=True),
                "연락처": st.column_config.TextColumn("연락처", width="medium", disabled=True),
                "신청 날짜": st.column_config.TextColumn("신청 날짜", width="small", disabled=True),
                "상태": st.column_config.SelectboxColumn(
                    "상태",
                    width="small",
                    options=["접수", "진행중", "완료"],
                ),
            },
        )
        
        # Save edited tickets
        if st.button("저장"):
            save_tickets({"counter": tickets_data["counter"], "tickets": edited_tickets})
            st.success("✅ 저장되었습니다!")
            st.rerun()
    else:
        st.info("상담 신청 내역이 없습니다.")
