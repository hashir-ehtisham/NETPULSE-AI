import gradio as gr
from huggingface_hub import InferenceClient
import pandas as pd

# Direct link to the image
image_url = "https://drive.google.com/uc?export=view&id=1OX1tj6gTNo8CkV9IDbNKgZ7WHvpNmgFo"

# Define the system message
SYSTEM_MESSAGE = """
You are a Fault Prediction Chatbot that analyzes network and system performance data to identify potential issues before they escalate. Based on the provided data, respond in the following format and must include the following headings:
# **Future Performance Prediction**
# **Risk Analysis and Potential Issues**
# **Preventive Actions and Recommendations**
"""

SIMPLE_SYSTEM_MESSAGE = (
    "You are an AI powered chatbot named as NetPulse-AI built by team HelixAI that provides "
    "predictive maintenance insights, cost optimization suggestions, and energy efficiency "
    "recommendations for networks."
)

css = """
footer {display:none !important}
.output-markdown{display:none !important}
.gr-button-primary {
    z-index: 14; height: 43px; width: 130px; left: 0px; top: 0px; padding: 0px;
    cursor: pointer !important;
    background: none rgb(17, 20, 45) !important;
    border: none !important; text-align: center !important;
    font-family: Poppins !important; font-size: 14px !important;
    font-weight: 500 !important; color: rgb(255, 255, 255) !important;
    line-height: 1 !important; border-radius: 12px !important;
    transition: box-shadow 200ms ease 0s, background 200ms ease 0s !important;
    box-shadow: none !important;
}
.gr-button-primary:hover {
    background: none rgb(66, 133, 244) !important;
    box-shadow: rgb(0 0 0 / 23%) 0px 1px 7px 0px !important;
}
#image-container {
    display: flex; justify-content: center;
    align-items: center; height: auto; margin-top: 20px;
}
#compass-image { max-width: 800px; max-height: 600px; object-fit: contain; }
"""

# Global chat-history store for download feature
current_chat_history = []


# ── Core respond generator ────────────────────────────────────────────────────
def respond(message, history, system_msg, max_tokens, temperature, top_p,
            hf_token: gr.OAuthToken):
    global current_chat_history

    if not hf_token:
        yield "⚠️ Please log in with your Hugging Face account using the button in the sidebar before sending messages."
        return

    client = InferenceClient(model="microsoft/phi-4", token=hf_token.token)

    messages = [{"role": "system", "content": system_msg}]
    for user_msg, bot_msg in history:
        if user_msg:
            messages.append({"role": "user",      "content": user_msg})
        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})
            current_chat_history.append(f"Assistant: {bot_msg}")

    messages.append({"role": "user", "content": message})
    current_chat_history.append(f"User: {message}")

    response = ""
    for chunk in client.chat_completion(
        messages, max_tokens=max_tokens, stream=True,
        temperature=temperature, top_p=top_p,
    ):
        token = chunk.choices[0].delta.content or ""
        response += token
        yield response

    current_chat_history.append(f"Assistant: {response}")


# ── Helpers ───────────────────────────────────────────────────────────────────
def format_response(text: str) -> str:
    return (
        text
        .replace("Future Performance Prediction:",
                 "<h2><strong>Future Performance Prediction</strong></h2>")
        .replace("Risk Analysis and Potential Issues:",
                 "<h2><strong>Risk Analysis and Potential Issues</strong></h2>")
        .replace("Preventive Actions and Recommendations:",
                 "<h2><strong>Preventive Actions and Recommendations</strong></h2>")
    )


def send_message(message, history, system_msg, max_tokens, temperature, top_p, hf_token):
    if not message:
        return history, gr.update(value="")
    history.append((message, ""))
    response_text = ""
    for r in respond(message, history[:-1], system_msg, max_tokens, temperature, top_p, hf_token):
        response_text = r
    history[-1] = (message, format_response(response_text))
    return history, gr.update(value="")


def download_chat_history():
    with open("chat_history.txt", "w") as f:
        f.write("\n".join(current_chat_history))
    return "chat_history.txt"


def clear_chat_history_fn():
    global current_chat_history
    current_chat_history.clear()
    return "Chat history cleared."


def read_excel(file):
    df = pd.read_excel(file.name)
    return df.to_string()


# ── UI ────────────────────────────────────────────────────────────────────────
with gr.Blocks(css=css) as demo:

    # Sidebar — login lives here, exactly like EyeAgri
    with gr.Sidebar():
        gr.Markdown("### 🔐 Login")
        gr.LoginButton()
        gr.Markdown(
            "Log in with your Hugging Face account to use NetPulse AI. "
            "Your token is used only to call the inference API."
        )

    # ── Introduction Tab ──────────────────────────────────────────────────────
    with gr.Tab("NetPulse AI"):
        with gr.Row(elem_id="image-container"):
            gr.Image(image_url, elem_id="compass-image")

        gr.Markdown("# **NetPulse AI**")
        gr.Markdown("### **Developed by Team HELIX AI**")
        gr.Markdown("""
**This project monitors network health using a Raspberry Pi, collecting data on CPU usage,
temperature, signal strength, and packet loss. The data is logged in Excel, identifying
abnormal conditions. Users upload the data to the chatbot for predictive analysis and
optimization recommendations.**

**Features:**
- **Future Performance Prediction:** Identifies upcoming failure risks based on past data trends.
- **Risk Analysis and Potential Issues:** Detects high-risk periods and network bottlenecks.
- **Preventive Actions and Recommendations:** Suggests cooling measures, bandwidth optimization, and maintenance alerts.

**How It Works:**
1. Log in with your Hugging Face account (sidebar).
2. Upload your Excel file in the *Upload Data* tab.
3. Paste the data into *Detailed Analysis* for a full report.
4. Use *General Chat* for follow-up questions.
        """)

    # ── Detailed Analysis Tab ─────────────────────────────────────────────────
    with gr.Tab("Detailed Analysis"):
        gr.Markdown("# Detailed Analysis")
        gr.Markdown(
            "Analyze network performance trends, predict potential issues, and receive "
            "tailored recommendations based on the uploaded data."
        )

        chatbot_career = gr.Chatbot()
        msg_career     = gr.Textbox(label="Enter the Excel Copied Data here")

        with gr.Row():
            clear_career    = gr.Button("New Chat")
            download_button = gr.Button("Download Chat History")
            submit_career   = gr.Button("Submit")

        with gr.Row():
            download_output = gr.File(label="Download")
        download_button.click(download_chat_history, outputs=download_output)

        with gr.Row():
            clear_button  = gr.Button("Clear Chat History")
            status_output = gr.Textbox(label="Status", interactive=False)
        clear_button.click(clear_chat_history_fn, outputs=status_output)

        with gr.Accordion("Additional Inputs", open=False):
            max_tokens_career  = gr.Slider(1, 2048, 1024, step=1,     label="Max new tokens")
            temperature_career = gr.Slider(0.1, 4.0, 0.7,  step=0.1,  label="Temperature")
            top_p_career       = gr.Slider(0.1, 1.0, 0.95, step=0.05, label="Top-p (nucleus sampling)")

        system_msg_career = gr.Textbox(value=SYSTEM_MESSAGE, visible=False)

        def respond_wrapper_career(message, chat_history, sys_msg,
                                    max_tok, temp, top_p, hf_token):
            updated, _ = send_message(
                message, chat_history, sys_msg, max_tok, temp, top_p, hf_token
            )
            return gr.update(value=updated), gr.update(value="")

        submit_career.click(
            respond_wrapper_career,
            inputs=[msg_career, chatbot_career, system_msg_career,
                    max_tokens_career, temperature_career, top_p_career],
            outputs=[chatbot_career, msg_career],
        )
        clear_career.click(lambda: None, None, chatbot_career, queue=False)

    # ── Upload Data Tab ───────────────────────────────────────────────────────
    with gr.Tab("Upload Data"):
        gr.Markdown("# Upload Data")
        file_input   = gr.File(label="Upload Excel file")
        excel_output = gr.Textbox(label="Excel Content")
        file_input.change(read_excel, inputs=file_input, outputs=excel_output)

    # ── General Chat Tab ──────────────────────────────────────────────────────
    with gr.Tab("General Chat for Network Optimization"):
        gr.Markdown("# General Chat for Network Optimization")
        gr.Markdown(
            "Ask NetPulse AI for predictive maintenance insights, cost optimization "
            "suggestions, and energy efficiency recommendations."
        )

        chatbot_simple = gr.Chatbot()
        msg_simple     = gr.Textbox(label="Type a message")

        with gr.Row():
            clear_simple  = gr.Button("Clear")
            submit_simple = gr.Button("Submit")

        with gr.Accordion("Additional Inputs", open=False):
            max_tokens_simple  = gr.Slider(1, 2048, 1024, step=1,     label="Max new tokens")
            temperature_simple = gr.Slider(0.1, 4.0, 0.7,  step=0.1,  label="Temperature")
            top_p_simple       = gr.Slider(0.1, 1.0, 0.95, step=0.05, label="Top-p (nucleus sampling)")

        system_msg_simple = gr.Textbox(value=SIMPLE_SYSTEM_MESSAGE, visible=False)

        def respond_wrapper_simple(message, chat_history, sys_msg,
                                    max_tok, temp, top_p, hf_token):
            updated, _ = send_message(
                message, chat_history, sys_msg, max_tok, temp, top_p, hf_token
            )
            return updated

        submit_simple.click(
            respond_wrapper_simple,
            inputs=[msg_simple, chatbot_simple, system_msg_simple,
                    max_tokens_simple, temperature_simple, top_p_simple],
            outputs=[chatbot_simple],
        )
        clear_simple.click(lambda: None, None, chatbot_simple)


demo.launch()
