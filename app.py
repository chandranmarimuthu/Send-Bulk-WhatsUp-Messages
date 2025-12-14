"""
Streamlit UI for WhatsApp Bulk Message Sender
Uses Selenium to open WhatsApp Web once, then send messages one by one
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from whatsapp_sender import WhatsAppBulkSender

# Page config
st.set_page_config(
    page_title="WhatsApp Bulk Messenger",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💬 WhatsApp Bulk Messenger")
st.markdown("*Send automated messages to multiple WhatsApp contacts from CSV*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    delay = st.slider(
        "Delay between messages (seconds)",
        min_value=2,
        max_value=60,
        value=5,
        help="Time to pause between each message to avoid rate limiting"
    )
    
    st.divider()
    
    st.subheader("📖 How to Use")
    st.markdown("""
    1. **Prepare CSV file** with columns:
       - `phone_number`: Contact phone number
       - `name`: Contact name
       - (Optional) Other columns for personalization
    
    2. **Upload CSV** and compose message
    
    3. **Click "Start Sending"** 
       - Browser opens once
       - Scan QR code if needed
       - Messages send automatically
    
    ⚠️ **Requirements:**
    - Chrome or Brave browser
    - WhatsApp Web access
    - Active internet connection
    """)

# Main tabs
tab1, tab2, tab3 = st.tabs(["📤 Send Messages", "📋 CSV Template", "📊 Reports"])

# ==================== TAB 1: SEND MESSAGES ====================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1️⃣ Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=["csv"],
            key="csv_upload"
        )
    
    with col2:
        if st.button("📥 Download Template", width='stretch'):
            template_df = pd.DataFrame({
                'phone_number': ['+9190000002212'],
                'name': ['Chandran Marimuthu']
            })
            st.download_button(
                label="Download template.csv",
                data=template_df.to_csv(index=False),
                file_name="template.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # Load and display CSV
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            st.success(f"✅ Loaded {len(df)} contacts")
            
            # Display contacts preview
            with st.expander("📋 View Contacts", expanded=True):
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Message composition
            st.subheader("2️⃣ Compose Message")
            
            message_template = st.text_area(
                "Write your message",
                value="Hi {name}! 👋\n\nThis is an automated message. How can I help you?",
                height=150,
                help="Use {name} to personalize with contact name. Use column names in curly braces for other fields."
            )
            
            # Preview message
            if df is not None and len(df) > 0:
                first_contact = df.iloc[0]
                preview_msg = message_template.format(**first_contact.to_dict())
                with st.expander("👁️ Preview Message"):
                    st.info(preview_msg)
            
            # Send settings
            st.subheader("3️⃣ Send Settings")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                delay = st.number_input(
                    "Delay between messages (seconds)",
                    min_value=2,
                    max_value=60,
                    value=5,
                    help="Wait time between sending each message"
                )
            
            with col2:
                start_row = st.number_input(
                    "Start from row",
                    min_value=1,
                    max_value=len(df),
                    value=1,
                    help="Send from specific row (useful for resuming)"
                )
            
            with col3:
                end_row = st.number_input(
                    "End at row",
                    min_value=start_row,
                    max_value=len(df),
                    value=len(df),
                    help="Send up to specific row"
                )
            
            # Send button
            st.divider()
            
            if st.button("🚀 Start Sending Messages", use_container_width=True, type="primary"):
                
                # Save CSV to temp file
                temp_csv = "temp_contacts.csv"
                df.to_csv(temp_csv, index=False, encoding='utf-8')
                
                # Initialize sender
                sender = WhatsAppBulkSender(temp_csv, wait_time=delay)
                
                if sender.load_contacts():
                    # Filter contacts by row range
                    contacts_to_send = sender.contacts[start_row-1:end_row]
                    
                    st.warning("⏳ WhatsApp Web will open... Scan QR code when it appears")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    errors_found = []
                    
                    with st.spinner(f"Sending {len(contacts_to_send)} messages..."):
                        try:
                            # Use send_bulk_messages which opens browser once
                            sender.contacts = contacts_to_send
                            result = sender.send_bulk_messages(message_template, delay)
                            
                            # Show results
                            st.divider()
                            st.success(f"✅ Completed! Sent {result['sent']}/{result['total']} messages")
                            
                            # Show metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("✅ Sent", result['sent'])
                            with col2:
                                st.metric("❌ Failed", result['failed'])
                            with col3:
                                st.metric("📊 Success Rate", f"{result['success_rate']:.1f}%")
                            
                            # Show failed messages if any
                            if result['failed'] > 0:
                                st.error("**Failed Messages:**")
                                report = sender.get_report()
                                for fail in report['failed']:
                                    st.write(f"• {fail['name']}: {fail['error']}")
                        
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    # Cleanup
                    if os.path.exists(temp_csv):
                        os.remove(temp_csv)
            
            else:
                st.info("📱 Click button above to start sending messages")
        
        except Exception as e:
            st.error(f"Error processing CSV: {str(e)}")
    
    else:
        st.info("👆 Upload a CSV file to start")

# ==================== TAB 2: CSV TEMPLATE ====================
with tab2:
    st.subheader("📋 CSV Format Guide")
    
    st.markdown("""
    ### Required Columns
    - **phone_number**: Phone number with country code (e.g., +919876543210 or 919876543210)
    - **name**: Contact name for personalization
    
    ### Optional Columns
    Add any columns you want to use in your message template with `{column_name}` syntax.
    """)
    
    st.subheader("Example CSV")
    example_data = {
        'phone_number': ['+919876543210'],
        'name': ['Chandran Marimuthu']
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True, hide_index=True)
    
    st.subheader("Example Message Template")
    st.code("""Hi {name}! 👋""")
    
    st.subheader("Download Template")
    csv_data = example_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Example CSV",
        data=csv_data,
        file_name="whatsapp_contacts_example.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==================== TAB 3: REPORTS ====================
with tab3:
    st.subheader("📊 Sending Reports")
    
    st.info("Reports will appear here after you send messages")
    
    st.markdown("""
    ### What gets tracked:
    - ✅ Successfully sent messages
    - ❌ Failed messages with error details
    - ⏱️ Timestamp of each send
    - 📞 Contact information
    
    ### Save Reports
    After sending, you can:
    1. View detailed logs
    2. Export sent/failed lists as CSV
    3. Retry failed contacts
    """)
