import gradio as gr
import pandas as pd
import requests
import json
import random
from datetime import datetime
import webbrowser

# Load customer data
try:
    customer_data = pd.read_csv('output/customer_recommendations_output.csv')
    metadata = pd.read_csv('data/metadata_user.csv')
except:
    print("Warning: Could not load customer data files")
    customer_data = pd.DataFrame()
    metadata = pd.DataFrame()

# Global variable to store pending transfer
pending_transfer = None

def clean_product_name(product_name):
    """Remove tier information from product name"""
    if not product_name or pd.isna(product_name):
        return ""
    # Remove everything after " tier "
    if " tier " in product_name:
        return product_name.split(" tier ")[0]
    return product_name

def get_customer_options():
    """Get list of customers for dropdown"""
    if customer_data.empty:
        return []
    options = []
    for _, row in customer_data.iterrows():
        user_id = row['user_id'][:8] + "..."
        info = f"ID: {user_id} | {row['age']} tuổi | {row['occupation']} | {row['marital_status']}"
        options.append((info, row['user_id']))
    return options

def get_customer_profile(user_id):
    """Get customer profile information"""
    if customer_data.empty:
        return "Không có dữ liệu khách hàng", "", "", ""
    
    customer = customer_data[customer_data['user_id'] == user_id]
    if customer.empty:
        return "Không tìm thấy khách hàng", "", "", ""
    
    row = customer.iloc[0]
    
    # Customer profile HTML
    profile_html = f"""
    <div style="font-family: 'Nunito', sans-serif; background: #2d2d2d; padding: 15px; border-radius: 8px; border: 1px solid #404040; color: #ffffff;">
        <h3 style="color: #E30613; margin-bottom: 15px;">👤 Thông tin Khách hàng</h3>
        
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>🆔 User ID:</strong> {row['user_id']}</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>🎂 Tuổi:</strong> {row['age']} tuổi</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>💼 Nghề nghiệp:</strong> {row['occupation']}</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>💑 Tình trạng hôn nhân:</strong> {row['marital_status']}</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>✅ Trạng thái recommend:</strong> {"Thành công" if row['recommendation_success'] else "Không thành công"}</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>📊 Số sản phẩm đã sử dụng:</strong> {row['adopted_products_count']}</div>
        <div style="margin-bottom: 10px; color: #ffffff;"><strong>⏰ Thời gian cập nhật:</strong> {row['timestamp']}</div>
        
        <h4 style="color: #E30613; margin-top: 15px; margin-bottom: 10px;">🎯 Sản phẩm được đề xuất:</h4>
        <div style="margin-bottom: 5px; color: #ffffff;">1. {clean_product_name(row['recommended_product_name_1'])}</div>
        <div style="margin-bottom: 5px; color: #ffffff;">2. {clean_product_name(row['recommended_product_name_2'])}</div>
        <div style="margin-bottom: 5px; color: #ffffff;">3. {clean_product_name(row['recommended_product_name_3'])}</div>
    </div>
    """
    
    # Get product buttons
    product1 = clean_product_name(row['recommended_product_name_1'])
    product2 = clean_product_name(row['recommended_product_name_2'])
    product3 = clean_product_name(row['recommended_product_name_3'])
    
    return profile_html, product1, product2, product3

def call_text2action_api(text, message_history=None):
    """Call the text2action API"""
    try:
        # Try the correct API URL
        urls = [
            "http://54.87.106.218/api/text2action",
            "https://54.87.106.218/api/text2action"
        ]
        
        for url in urls:
            try:
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                
                data = {"text": text}
                if message_history:
                    data["message_history"] = message_history
                    
                response = requests.post(url, headers=headers, json=data, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    continue  # Try next URL
            except:
                continue  # Try next URL
        
        # If all URLs failed
        return {
            "action": "ask",
            "payload": {
                "answer": "Xin lỗi, không thể kết nối đến server API. Đây có thể là demo offline - bạn có thể thử các tính năng khác của TECHNOBOT!"
            }
        }
    except Exception as e:
        return {
            "action": "ask",
            "payload": {
                "answer": f"Xin lỗi, có lỗi xảy ra: {str(e)}. Đây có thể là demo offline - bạn có thể thử các tính năng khác của TECHNOBOT!"
            }
        }

def handle_chat_message(message, chat_history, message_history_state):
    """Handle chat message and return response"""
    global pending_transfer
    
    if not message.strip():
        return chat_history, "", message_history_state
    
    # Add user message to chat (using messages format)
    chat_history.append({"role": "user", "content": message})
    
    # Check if user is confirming a pending transfer
    if message.upper().strip() in ["XÁC NHẬN", "XAC NHAN", "CONFIRM"]:
        if 'pending_transfer' in globals() and pending_transfer:
            # Process the transfer confirmation
            amount = pending_transfer.get('amount', 0)
            recipient_account = pending_transfer.get('recipient_account', 'N/A')
            bank_name = pending_transfer.get('bank_name', 'N/A')
            recipient_name = pending_transfer.get('recipient_name', 'N/A')
            memo = pending_transfer.get('memo', 'N/A')
            
            bot_response = f"""🏦 **TECHCOMBANK - XÁC NHẬN CHUYỂN TIỀN**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Số tiền:** {amount:,} VND
🏦 **Ngân hàng nhận:** {bank_name}
📱 **Số tài khoản:** {recipient_account}
👤 **Người nhận:** {recipient_name}
📝 **Nội dung:** {memo}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **GIAO DỊCH ĐÃ ĐƯỢC THỰC HIỆN THÀNH CÔNG!**

🔢 **Mã giao dịch:** TCB{amount}{recipient_account[-4:]}
⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cảm ơn Quý khách đã sử dụng dịch vụ Techcombank! 🙏"""
            
            # Clear pending transfer
            pending_transfer = None
            
            # Add bot response and return
            chat_history.append({"role": "assistant", "content": bot_response})
            new_message_history = message_history_state.copy() if message_history_state else []
            new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
            return chat_history, "", new_message_history, False, None
        else:
            bot_response = "❌ Không có giao dịch nào đang chờ xác nhận. Vui lòng thực hiện lại yêu cầu chuyển tiền."
            chat_history.append({"role": "assistant", "content": bot_response})
            new_message_history = message_history_state.copy() if message_history_state else []
            new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
            return chat_history, "", new_message_history, False, None
    
    elif message.upper().strip() in ["HỦY", "HUY", "CANCEL"]:
        if 'pending_transfer' in globals() and pending_transfer:
            pending_transfer = None
            bot_response = "❌ **Giao dịch đã được hủy thành công!**\n\nQuý khách có thể thực hiện giao dịch mới bất kỳ lúc nào."
            chat_history.append({"role": "assistant", "content": bot_response})
            new_message_history = message_history_state.copy() if message_history_state else []
            new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
            return chat_history, "", new_message_history, False, None
        else:
            bot_response = "❌ Không có giao dịch nào đang chờ xác nhận để hủy."
            chat_history.append({"role": "assistant", "content": bot_response})
            new_message_history = message_history_state.copy() if message_history_state else []
            new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
            return chat_history, "", new_message_history, False, None
    
    # Call API for regular messages
    api_response = call_text2action_api(message, message_history_state)
    
    # Handle response based on action
    if api_response.get("action") == "transfer_money":
        # Handle transfer money action - Trigger popup modal
        payload = api_response.get("payload", {})
        
        # Store transfer data globally for confirmation
        pending_transfer = payload
        
        # Return a simple message and trigger popup via return values
        bot_response = "🔄 Đang chuẩn bị thông tin chuyển tiền..."
        
        # Add bot response to chat and return with popup trigger
        chat_history.append({"role": "assistant", "content": bot_response})
        new_message_history = message_history_state.copy() if message_history_state else []
        new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
        
        # Return with popup trigger (True for popup, payload for data)
        return chat_history, "", new_message_history, True, payload
             
    else:
        # Handle regular chat response
        bot_response = api_response.get("payload", {}).get("answer", "Xin lỗi, tôi không hiểu câu hỏi của bạn.")
    
    # Add bot response to chat (using messages format)
    chat_history.append({"role": "assistant", "content": bot_response})
    
    # Update message history for next API call
    new_message_history = message_history_state.copy() if message_history_state else []
    new_message_history.extend([f"User: {message}", f"Assistant: {bot_response}"])
    
    # Return without popup trigger
    return chat_history, "", new_message_history, False, None

def product_button_click(product_name):
    """Handle product button click"""
    if not product_name:
        return [], "", []
    
    initial_message = f"Tôi quan tâm đến sản phẩm {product_name}"
    
    # Call API for initial product inquiry
    api_response = call_text2action_api(initial_message)
    bot_response = api_response.get("payload", {}).get("answer", f"Cảm ơn bạn đã quan tâm đến sản phẩm {product_name}!")
    
    # Return initial chat with product inquiry (using messages format)
    chat_history = [
        {"role": "user", "content": initial_message},
        {"role": "assistant", "content": bot_response}
    ]
    message_history = [f"User: {initial_message}", f"Assistant: {bot_response}"]
    
    return chat_history, "", message_history

# CSS styling
css = """
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap');

/* Global styles - Dark theme */
body, .gradio-container {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
}

* {
    font-family: 'Nunito', sans-serif !important;
    color: #ffffff !important;
}

/* Override Gradio's white backgrounds */
.block, .form, .panel {
    background-color: #2d2d2d !important;
    border: 1px solid #404040 !important;
}

/* Header styling */
.techno-header {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    border: 2px solid #E30613;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-text {
    font-size: 32px;
    font-weight: 700;
    margin: 0;
}

.tech-text {
    color: #E30613;
}

.nobot-text {
    color: #000000;
}

/* Introduction section */
.intro-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    border-left: 4px solid #E30613;
}

.intro-title {
    color: #E30613;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 15px;
}

.intro-text {
    color: #495057;
    line-height: 1.6;
    margin-bottom: 10px;
}

/* Profile section */
.profile-section {
    background: #2d2d2d !important;
    border: 1px solid #404040 !important;
    border-radius: 12px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    color: #ffffff !important;
}

/* Product buttons */
.product-btn {
    background: linear-gradient(135deg, #E30613 0%, #c50510 100%);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 5px;
}

.product-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(227, 6, 19, 0.3);
}

/* Chat interface */
.chat-container {
    background: #2d2d2d !important;
    border: 1px solid #404040 !important;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    color: #ffffff !important;
}

/* Dark theme elements */
.dark-bg {
    background: #1a1a1a;
    color: white;
}

/* Custom gradio styling */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
}
"""

# Create Gradio interface
with gr.Blocks(css=css, title="TECHNOBOT - Hệ thống Phân tích Tín dụng Thông minh") as app:
    # State variables
    message_history_state = gr.State([])
    
    # Header
    gr.HTML("""
    <div class="techno-header">
        <div class="logo-container">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="background: #E30613; padding: 10px; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: white; font-size: 24px; font-weight: bold;">🤖</span>
                </div>
                <h1 class="logo-text" style="margin: 0; font-size: 32px; font-weight: bold;">
                    <span class="tech-text" style="color: #E30613;">TECH</span><span class="nobot-text" style="color: #ffffff;">NOBOT</span>
                </h1>
            </div>
        </div>
    </div>
    """)
    
    # Introduction section
    gr.HTML("""
    <div class="intro-section" style="background: #2d2d2d; padding: 20px; border-radius: 12px; border: 1px solid #404040; margin-bottom: 20px;">
        <h2 class="intro-title" style="color: #E30613; margin-bottom: 15px;">🤖 TECHNOBOT - Hệ thống Phân tích Tín dụng Thông minh</h2>
        <p class="intro-text" style="color: #ffffff; font-size: 16px; margin-bottom: 15px;">
            🎯 <strong>Hệ thống AI phân tích tín dụng với giải thích minh bạch</strong>
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
            <div style="color: #ffffff; padding: 10px; background: #1a1a1a; border-radius: 8px;">🔍 <strong>Phân tích SHAP:</strong> Giải thích chi tiết các yếu tố ảnh hưởng đến quyết định</div>
            <div style="color: #ffffff; padding: 10px; background: #1a1a1a; border-radius: 8px;">🤖 <strong>AI Chatbot:</strong> Tư vấn thông minh với Gemini AI và ChatGPT</div>
            <div style="color: #ffffff; padding: 10px; background: #1a1a1a; border-radius: 8px;">📊 <strong>Giao diện trực quan:</strong> Dễ sử dụng cho cả chuyên gia và khách hàng</div>
            <div style="color: #ffffff; padding: 10px; background: #1a1a1a; border-radius: 8px;">🔒 <strong>Minh bạch:</strong> Mỗi quyết định đều được giải thích rõ ràng</div>
        </div>
    </div>
    """)
    
    # Main content
    with gr.Row():
        # Left column - Profile selection and display
        with gr.Column(scale=1):
            gr.HTML("<h3 style='color: #E30613; margin-bottom: 15px;'>👤 Chọn Hồ sơ Khách hàng</h3>")
            
            customer_dropdown = gr.Dropdown(
                choices=get_customer_options(),
                label="Chọn khách hàng từ danh sách",
                value=None,
                interactive=True
            )
            
            gr.HTML("<h3 style='color: #E30613; margin-top: 20px; margin-bottom: 10px;'>📋 Hồ sơ Khách hàng</h3>")
            customer_profile = gr.HTML(
                value="<div class='profile-section'>Vui lòng chọn khách hàng từ danh sách trên</div>",
                elem_classes=["profile-section"]
            )
        
        # Right column - Chat interface
        with gr.Column(scale=2):
            gr.HTML("<h3 style='color: #E30613; margin-bottom: 15px;'>💬 Chat cùng TECHNOBOT</h3>")
            
            # Product recommendation buttons
            with gr.Row():
                product_btn1 = gr.Button("", variant="primary", visible=False, elem_classes=["product-btn"])
                product_btn2 = gr.Button("", variant="primary", visible=False, elem_classes=["product-btn"])  
                product_btn3 = gr.Button("", variant="primary", visible=False, elem_classes=["product-btn"])
            
            # Chat interface
            with gr.Row():
                chatbot = gr.Chatbot(
                    height=400,
                    placeholder="Chọn khách hàng và bắt đầu chat với TECHNOBOT...",
                    elem_classes=["chat-container"],
                    type="messages"
                )
            
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Nhập tin nhắn của bạn...",
                    show_label=False,
                    scale=4
                )
                send_btn = gr.Button("Gửi", variant="primary", scale=1)
    
    # Transfer Confirmation Modal (Hidden by default)
    with gr.Row(visible=False) as transfer_modal:
        with gr.Column():
            gr.HTML("<h2 style='color: #E30613; text-align: center;'>🏦 XÁC NHẬN CHUYỂN TIỀN</h2>")
            
            transfer_info = gr.HTML("")
            
            with gr.Row():
                confirm_btn = gr.Button("✅ Xác nhận chuyển tiền", variant="primary", size="lg")
                cancel_btn = gr.Button("❌ Hủy giao dịch", variant="secondary", size="lg")
    
    # Hidden states for popup
    popup_trigger = gr.State(False)
    transfer_data = gr.State(None)
    
    # Transfer popup functions
    def show_transfer_popup(payload):
        """Show transfer confirmation popup"""
        if not payload:
            return gr.update(visible=False), ""
        
        amount = payload.get('amount', 0)
        recipient_account = payload.get('recipient_account', 'N/A')
        bank_name = payload.get('bank_name', 'N/A')
        recipient_name = payload.get('recipient_name', 'N/A')
        memo = payload.get('memo', 'N/A')
        
        info_html = f"""
        <div style="background: #2d2d2d; padding: 20px; border-radius: 12px; border: 1px solid #404040; margin: 10px 0;">
            <h3 style="color: #E30613; text-align: center; margin-bottom: 20px;">Có phải bạn muốn chuyển tiền với nội dung dưới đây:</h3>
            
            <div style="background: #1a1a1a; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">💰 Số tiền:</span>
                    <strong style="color: #ffffff; font-size: 18px;">{amount:,} VND</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">🏦 Ngân hàng nhận:</span>
                    <span style="color: #ffffff;">{bank_name}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">📱 Số tài khoản:</span>
                    <span style="color: #ffffff; font-family: monospace;">{recipient_account}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">👤 Người nhận:</span>
                    <span style="color: #ffffff;">{recipient_name}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">📝 Nội dung:</span>
                    <span style="color: #ffffff;">{memo}</span>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <p style="color: #ffcccc; font-size: 14px;">⚠️ Vui lòng kiểm tra kỹ thông tin trước khi xác nhận!</p>
            </div>
        </div>
        """
        
        return gr.update(visible=True), info_html
    
    def confirm_transfer(transfer_data_state):
        """Confirm transfer and show success message"""
        global pending_transfer
        
        if not transfer_data_state:
            return gr.update(visible=False), "", []
        
        amount = transfer_data_state.get('amount', 0)
        recipient_account = transfer_data_state.get('recipient_account', 'N/A')
        bank_name = transfer_data_state.get('bank_name', 'N/A')
        recipient_name = transfer_data_state.get('recipient_name', 'N/A')
        memo = transfer_data_state.get('memo', 'N/A')
        
        success_message = f"""🏦 **TECHCOMBANK - XÁC NHẬN CHUYỂN TIỀN**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Số tiền:** {amount:,} VND
🏦 **Ngân hàng nhận:** {bank_name}
📱 **Số tài khoản:** {recipient_account}
👤 **Người nhận:** {recipient_name}
📝 **Nội dung:** {memo}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **GIAO DỊCH ĐÃ ĐƯỢC THỰC HIỆN THÀNH CÔNG!**

🔢 **Mã giao dịch:** TCB{amount}{recipient_account[-4:]}
⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cảm ơn Quý khách đã sử dụng dịch vụ Techcombank! 🙏"""
        
        # Clear pending transfer
        pending_transfer = None
        
        # Return: hide modal, empty transfer info, add success message to chat
        return gr.update(visible=False), "", [{"role": "assistant", "content": success_message}]
    
    def cancel_transfer():
        """Cancel transfer and hide popup"""
        global pending_transfer
        pending_transfer = None
        
        cancel_message = "❌ **Giao dịch đã được hủy thành công!**\n\nQuý khách có thể thực hiện giao dịch mới bất kỳ lúc nào."
        
        return gr.update(visible=False), "", [{"role": "assistant", "content": cancel_message}]

    # Event handlers
    def update_profile_and_buttons(customer_id):
        if not customer_id:
            return (
                "<div class='profile-section'>Vui lòng chọn khách hàng từ danh sách trên</div>",
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                "", "", ""
            )
        
        profile_html, product1, product2, product3 = get_customer_profile(customer_id)
        
        # Update button visibility and text
        btn1_update = gr.update(value=product1, visible=bool(product1))
        btn2_update = gr.update(value=product2, visible=bool(product2))
        btn3_update = gr.update(value=product3, visible=bool(product3))
        
        return profile_html, btn1_update, btn2_update, btn3_update, product1, product2, product3
    
    # Store product names in hidden state
    product1_state = gr.State("")
    product2_state = gr.State("")
    product3_state = gr.State("")
    
    customer_dropdown.change(
        update_profile_and_buttons,
        inputs=[customer_dropdown],
        outputs=[customer_profile, product_btn1, product_btn2, product_btn3, 
                product1_state, product2_state, product3_state]
    )
    
    # Product button clicks
    product_btn1.click(
        lambda p1: product_button_click(p1),
        inputs=[product1_state],
        outputs=[chatbot, chat_input, message_history_state]
    )
    
    product_btn2.click(
        lambda p2: product_button_click(p2),
        inputs=[product2_state],
        outputs=[chatbot, chat_input, message_history_state]
    )
    
    product_btn3.click(
        lambda p3: product_button_click(p3),
        inputs=[product3_state],
        outputs=[chatbot, chat_input, message_history_state]
    )
    
    # Chat functionality with popup handling
    def send_message(message, chat_history, message_history):
        result = handle_chat_message(message, chat_history, message_history)
        
        if len(result) == 5:  # Transfer money case
            chat_hist, input_clear, msg_hist, show_popup, payload = result
            if show_popup and payload:
                # Show popup and store transfer data
                modal_visible, transfer_html = show_transfer_popup(payload)
                return chat_hist, input_clear, msg_hist, modal_visible, transfer_html, payload
            else:
                return chat_hist, input_clear, msg_hist, gr.update(visible=False), "", None
        else:  # Regular case
            chat_hist, input_clear, msg_hist = result
            return chat_hist, input_clear, msg_hist, gr.update(visible=False), "", None
    
    send_btn.click(
        send_message,
        inputs=[chat_input, chatbot, message_history_state],
        outputs=[chatbot, chat_input, message_history_state, transfer_modal, transfer_info, transfer_data]
    )
    
    chat_input.submit(
        send_message,
        inputs=[chat_input, chatbot, message_history_state],
        outputs=[chatbot, chat_input, message_history_state, transfer_modal, transfer_info, transfer_data]
    )
    
    # Transfer popup event handlers
    def handle_confirm(data, chat_hist):
        modal_update, info_update, new_messages = confirm_transfer(data)
        updated_chat = chat_hist + new_messages
        return modal_update, info_update, updated_chat
    
    def handle_cancel(chat_hist):
        modal_update, info_update, new_messages = cancel_transfer()
        updated_chat = chat_hist + new_messages
        return modal_update, info_update, updated_chat
    
    confirm_btn.click(
        handle_confirm,
        inputs=[transfer_data, chatbot],
        outputs=[transfer_modal, transfer_info, chatbot]
    )
    
    cancel_btn.click(
        handle_cancel,
        inputs=[chatbot],
        outputs=[transfer_modal, transfer_info, chatbot]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        inbrowser=True
    ) 