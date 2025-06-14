import gradio as gr
import pandas as pd
import requests
import json
import random
from datetime import datetime
import webbrowser
import pyperclip  # For clipboard access
import socket
import time
from typing import List, Tuple, Dict, Any, Optional

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

def chat_with_technobot(message, history, message_history):
    """Xử lý chat với TECHNOBOT"""
    if not message.strip():
        return history, "", message_history
    
    try:
        # API endpoint
        api_url = "http://54.87.106.218/api/text2action"
        
        # Chuẩn bị payload - chỉ gửi message_history nếu có
        payload = {"text": message}
        
        if message_history:
            # Format message history cho API
            formatted_history = []
            for msg_pair in message_history:
                if isinstance(msg_pair, list) and len(msg_pair) == 2:
                    user_msg, bot_msg = msg_pair
                    formatted_history.append(f"User: {user_msg}")
                    formatted_history.append(f"Assistant: {bot_msg}")
            
            if formatted_history:
                payload["message_history"] = formatted_history
        
        # Debug logging
        print(f"🔍 DEBUG: API URL = {api_url}")
        print(f"🔍 DEBUG: Payload = {payload}")
        
        # Headers giống như curl
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        print(f"🔍 DEBUG: Headers = {headers}")
        
        # Gọi API
        print("🔍 DEBUG: Đang gọi API...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        
        print(f"🔍 DEBUG: Response status = {response.status_code}")
        print(f"🔍 DEBUG: Response headers = {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🔍 DEBUG: Response JSON = {result}")
        else:
            print(f"🔍 DEBUG: Response text = {response.text}")
            # API error - use mock response
            result = get_mock_response(message, bool(message_history))
            print(f"🔍 DEBUG: Using mock response = {result}")
        
    except Exception as e:
        # Connection error - use mock response
        print(f"🔍 DEBUG: Exception occurred = {type(e).__name__}: {str(e)}")
        print(f"🔍 DEBUG: Using mock response due to exception")
        result = get_mock_response(message, bool(message_history))
    
    # Process result
    action = result.get("action", "ask")
    print(f"🔍 DEBUG: Action = {action}")
    
    if action == "ask":
        payload_data = result.get("payload", {})
        response_text = payload_data.get("answer", "Xin lỗi, tôi không hiểu câu hỏi của bạn.")
        print(f"🔍 DEBUG: Response text = {response_text[:100]}...")
        new_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": response_text}]
        message_history.append([message, response_text])
        return new_history, "", message_history, gr.update(value=""), gr.update(visible=False)
    
    elif action == "transfer_money":
        global pending_transfer
        payload_data = result.get("payload", {})
        pending_transfer = payload_data
        
        response_text = "🔄 Đang chuẩn bị thông tin chuyển tiền... (Demo mode)"
        new_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": response_text}]
        message_history.append([message, response_text])
        
        # Tạo HTML cho transfer info
        amount = payload_data.get("amount", 0)
        recipient_account = payload_data.get("recipient_account", "N/A")
        bank_name = payload_data.get("bank_name", "N/A")
        recipient_name = payload_data.get("recipient_name", "N/A")
        memo = payload_data.get("memo", "N/A")
        
        info_html = f"""
        <div style="background: #2d2d2d; padding: 20px; border-radius: 12px; border: 1px solid #404040; margin: 10px 0;">
            <h3 style="color: #E30613; text-align: center; margin-bottom: 20px;">Có phải bạn muốn chuyển tiền với nội dung dưới đây: (Demo Mode)</h3>
            
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
                <p style="color: #ffcccc; font-size: 14px;">⚠️ Đây là demo mode - API thực tế không khả dụng</p>
            </div>
        </div>
        """
        
        return new_history, "", message_history, gr.update(value=info_html), gr.update(visible=True)
    
    else:
        error_msg = "Xin lỗi, có lỗi xảy ra trong quá trình xử lý."
        new_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}]
        message_history.append([message, error_msg])
        return new_history, "", message_history, gr.update(value=""), gr.update(visible=False)

def product_button_click(product_name):
    """Xử lý khi click vào nút sản phẩm"""
    if not product_name:
        return [], "", []
    
    # Tạo tin nhắn ban đầu
    initial_message = f"Tôi quan tâm đến sản phẩm {product_name}"
    
    # Gọi API để lấy thông tin sản phẩm
    try:
        result = chat_with_technobot(initial_message, [], [])
        if len(result) >= 3:
            new_history, _, new_msg_history = result[:3]
            return new_history, "", new_msg_history
        else:
            # Fallback nếu API không hoạt động
            response = f"Cảm ơn bạn đã quan tâm đến sản phẩm {product_name}! Đây là một sản phẩm tuyệt vời của Techcombank."
            chat_history = [
                {"role": "user", "content": initial_message},
                {"role": "assistant", "content": response}
            ]
            message_history = [[initial_message, response]]
            return chat_history, "", message_history
    except:
        # Fallback nếu có lỗi
        response = f"Cảm ơn bạn đã quan tâm đến sản phẩm {product_name}! Đây là một sản phẩm tuyệt vời của Techcombank."
        chat_history = [
            {"role": "user", "content": initial_message},
            {"role": "assistant", "content": response}
        ]
        message_history = [[initial_message, response]]
        return chat_history, "", message_history

def handle_paste_to_pay():
    """Xử lý nút Paste to Pay - lấy clipboard và gọi API extract"""
    try:
        # Lấy dữ liệu từ clipboard
        clipboard_text = pyperclip.paste()
        
        if not clipboard_text or clipboard_text.strip() == "":
            return "⚠️ Clipboard trống. Vui lòng copy thông tin chuyển tiền trước khi sử dụng Paste to Pay.", "", False, False, None
        
        # Gọi API extract
        api_url = "http://54.81.13.123/extract"
        payload = {"text": clipboard_text}
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Case 1: Thành công - có raw_output
            if result.get("raw_output") is not None:
                raw_output = result["raw_output"]
                
                # Tạo transfer data
                transfer_data = {
                    "bank_name": raw_output.get("bank_name", ""),
                    "bank_acc_number": raw_output.get("bank_acc_number", ""),
                    "amount": raw_output.get("amount", 0),
                    "content": raw_output.get("content", "")
                }
                
                # Format số tiền - xử lý cả string và int
                amount = transfer_data['amount']
                if isinstance(amount, str):
                    try:
                        amount = int(amount)
                    except ValueError:
                        amount = 0
                amount_formatted = f"{amount:,}".replace(",", ".")
                
                # Tạo thông tin hiển thị - PHẢI LÀ STRING
                transfer_info = f"""💳 **XÁC NHẬN CHUYỂN TIỀN**

🏦 **Ngân hàng:** {transfer_data['bank_name']}
📱 **Số tài khoản:** {transfer_data['bank_acc_number']}
💰 **Số tiền:** {amount_formatted} VNĐ
📝 **Nội dung:** {transfer_data['content']}"""
                
                global pending_transfer
                pending_transfer = transfer_data
                
                return (
                    f"📋 Đã phân tích thông tin từ clipboard:\n🏦 {transfer_data['bank_name']}\n📱 {transfer_data['bank_acc_number']}\n💰 {amount_formatted} VNĐ\n📝 {transfer_data['content']}", 
                    transfer_info,
                    True,
                    True,
                    transfer_data
                )
            
            # Case 2: Không thành công - raw_output = null
            else:
                return "⚠️ TECHNOBOT chưa nhận được thông tin chuyển tiền hợp lệ.", "", False, False, None
        
        else:
            return f"❌ Lỗi API: {response.status_code}", "", False, False, None
            
    except Exception as e:
        return f"❌ Lỗi xử lý: {str(e)}", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), None

def get_mock_response(message, has_history=False):
    """Tạo mock response khi API không khả dụng"""
    message_lower = message.lower().strip()
    
    # Detect transfer patterns
    transfer_keywords = ['ck', 'chuyển', 'transfer', 'chuyển khoản', 'chuyển tiền']
    bank_keywords = ['vcb', 'vietcombank', 'techcombank', 'bidv', 'acb', 'mb']
    
    has_transfer_keyword = any(keyword in message_lower for keyword in transfer_keywords)
    has_bank_keyword = any(keyword in message_lower for keyword in bank_keywords)
    has_numbers = any(char.isdigit() for char in message)
    
    if has_transfer_keyword and (has_bank_keyword or has_numbers):
        # Mock transfer response
        return {
            "action": "transfer_money",
            "payload": {
                "amount": 50000,
                "recipient_account": "1234567890",
                "bank_name": "Vietcombank",
                "recipient_name": "Người nhận demo",
                "memo": "Demo transfer"
            }
        }
    else:
        # Mock chat response
        if has_history:
            answer = f"Tôi hiểu bạn đang nói về '{message}'. Đây là phản hồi demo với context từ cuộc trò chuyện trước đó."
        else:
            answer = f"Xin chào! Bạn vừa nói '{message}'. Đây là phản hồi demo từ TECHNOBOT. API thực tế hiện không khả dụng."
        
        return {
            "action": "ask",
            "payload": {
                "question": f"Bạn có thể nói rõ hơn về '{message}' không?",
                "answer": answer
            }
        }

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

/* Paste to Pay button */
.paste-btn {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
    color: white !important;
    border: none !important;
    padding: 12px 20px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin-top: 20px !important;
}

.paste-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
}

/* Paste result styling */
.paste-result {
    background: #2d2d2d !important;
    border: 1px solid #28a745 !important;
    border-radius: 8px !important;
    color: white !important;
    margin: 10px 0 !important;
}

.paste-result textarea {
    background: #2d2d2d !important;
    color: white !important;
    border: none !important;
}
"""

# Create Gradio interface
with gr.Blocks(css=css, title="TECHNOBOT - Hệ thống Phân tích Tín dụng Thông minh") as app:
    # State variables
    message_history_state = gr.State([])
    
    # Header with Paste to Pay button
    with gr.Row():
        with gr.Column(scale=4):
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
        with gr.Column(scale=1):
            paste_to_pay_btn = gr.Button(
                "📋 Paste to Pay",
                variant="primary",
                size="lg",
                elem_classes=["paste-btn"]
            )
    
    # Paste to Pay result display
    paste_result = gr.Textbox(
        label="📋 Kết quả Paste to Pay",
        visible=False,
        interactive=False,
        elem_classes=["paste-result"]
    )
    
    # Transfer confirmation for Paste to Pay
    paste_transfer_info = gr.Markdown(visible=False, elem_classes=["transfer-info"])
    
    with gr.Row(visible=False) as paste_transfer_buttons:
        paste_confirm_btn = gr.Button("✅ Xác nhận chuyển tiền", variant="primary", elem_classes=["confirm-btn"])
        paste_cancel_btn = gr.Button("❌ Hủy giao dịch", variant="secondary", elem_classes=["cancel-btn"])
    
    # Hidden state for paste transfer data
    paste_transfer_state = gr.State(None)
    
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
        result = chat_with_technobot(message, chat_history, message_history)
        
        if len(result) == 5:  # Transfer money case
            new_history, empty_msg, new_msg_history, transfer_info_update, modal_update = result
            return new_history, empty_msg, new_msg_history, transfer_info_update, modal_update
        else:  # Regular chat case
            new_history, empty_msg, new_msg_history = result[:3]
            return new_history, empty_msg, new_msg_history, gr.update(value=""), gr.update(visible=False)
    
    # Connect chat input
    chat_input.submit(
        fn=send_message,
        inputs=[chat_input, chatbot, message_history_state],
        outputs=[chatbot, chat_input, message_history_state, transfer_info, transfer_modal]
    )
    
    send_btn.click(
        fn=send_message,
        inputs=[chat_input, chatbot, message_history_state],
        outputs=[chatbot, chat_input, message_history_state, transfer_info, transfer_modal]
    )
    
    # Transfer confirmation handlers - cần cập nhật transfer_data state
    def handle_chat_confirm():
        global pending_transfer
        if pending_transfer:
            amount = pending_transfer.get('amount', 0)
            recipient_account = pending_transfer.get('recipient_account', 'N/A')
            bank_name = pending_transfer.get('bank_name', 'N/A')
            recipient_name = pending_transfer.get('recipient_name', 'N/A')
            memo = pending_transfer.get('memo', 'N/A')
            
            success_msg = f"""🏦 **TECHCOMBANK - XÁC NHẬN CHUYỂN TIỀN**

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
            
            pending_transfer = None
            return gr.update(visible=False), "", [{"role": "assistant", "content": success_msg}]
        return gr.update(visible=False), "", []
    
    def handle_chat_cancel():
        global pending_transfer
        pending_transfer = None
        cancel_msg = "❌ **Giao dịch đã được hủy thành công!**\n\nQuý khách có thể thực hiện giao dịch mới bất kỳ lúc nào."
        return gr.update(visible=False), "", [{"role": "assistant", "content": cancel_msg}]
    
    confirm_btn.click(
        fn=handle_chat_confirm,
        outputs=[transfer_modal, transfer_info, chatbot]
    )
    
    cancel_btn.click(
        fn=handle_chat_cancel,
        outputs=[transfer_modal, transfer_info, chatbot]
    )

    # Paste to Pay event handler
    def handle_paste_click():
        result_text, transfer_info, info_visible, buttons_visible, transfer_data = handle_paste_to_pay()
        return (
            gr.update(value=result_text, visible=True), 
            gr.update(value=transfer_info, visible=info_visible),
            gr.update(visible=buttons_visible),
            transfer_data
        )
    
    paste_to_pay_btn.click(
        fn=handle_paste_click,
        outputs=[paste_result, paste_transfer_info, paste_transfer_buttons, paste_transfer_state]
    )

    # Paste transfer confirmation handlers
    def handle_paste_confirm(transfer_data):
        if transfer_data:
            amount = transfer_data.get('amount', 0)
            if isinstance(amount, str):
                try:
                    amount = int(amount)
                except ValueError:
                    amount = 0
            amount_formatted = f"{amount:,}".replace(",", ".")
            
            success_msg = f"✅ **CHUYỂN TIỀN THÀNH CÔNG!**\n\n🏦 Ngân hàng: {transfer_data['bank_name']}\n📱 Số TK: {transfer_data['bank_acc_number']}\n💰 Số tiền: {amount_formatted} VNĐ\n📝 Nội dung: {transfer_data['content']}\n\n🎉 Giao dịch đã được thực hiện thành công!"
            return (
                gr.update(value=success_msg, visible=True),
                gr.update(visible=False),
                gr.update(visible=False)
            )
        return gr.update(), gr.update(), gr.update()
    
    def handle_paste_cancel():
        return (
            gr.update(value="❌ Đã hủy giao dịch chuyển tiền.", visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    
    paste_confirm_btn.click(
        fn=handle_paste_confirm,
        inputs=[paste_transfer_state],
        outputs=[paste_result, paste_transfer_info, paste_transfer_buttons]
    )
    
    paste_cancel_btn.click(
        fn=handle_paste_cancel,
        outputs=[paste_result, paste_transfer_info, paste_transfer_buttons]
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