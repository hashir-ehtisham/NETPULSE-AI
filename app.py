import gradio as gr
from huggingface_hub import InferenceClient
import pandas as pd

# Direct link to the image
image_url = "https://drive.google.com/uc?export=view&id=1OX1tj6gTNo8CkV9IDbNKgZ7WHvpNmgFo"


# Define the system message
system_message = """
You are a Fault Prediction Chatbot that analyzes network and system performance data to identify potential issues before they escalate. Based on the provided data, respond in the following format and must include the following headings:
# **Future Performance Prediction**
# **Risk Analysis and Potential Issues**
# **Preventive Actions and Recommendations**
"""

# CSS to hide footer, customize button, and center image
css = """
footer {display:none !important}
.output-markdown{display:none !important}
.gr-button-primary {
    z-index: 14;
    height: 43px;
    width: 130px;
    left: 0px;
    top: 0px;
    padding: 0px;
    cursor: pointer !important; 
    background: none rgb(17, 20, 45) !important;
    border: none !important;
    text-align: center !important;
    font-family: Poppins !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: rgb(255, 255, 255) !important;
    line-height: 1 !important;
    border-radius: 12px !important;
    transition: box-shadow 200ms ease 0s, background 200ms ease 0s !important;
    box-shadow: none !important;
}
.gr-button-primary:hover {
    z-index: 14;
    height: 43px;
    width: 130px;
    left: 0px;
    top: 0px;
    padding: 0px;
    cursor: pointer !important;
    background: none rgb(66, 133, 244) !important;
    border: none !important;
    text-align: center !important;
    font-family: Poppins !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: rgb(255, 255, 255) !important;
    line-height: 1 !important;
    border-radius: 12px !important;
    transition: box-shadow 200ms ease 0s, background 200ms ease 0s !important;
    box-shadow: rgb(0 0 0 / 23%) 0px 1px 7px 0px !important;
}
.hover\:bg-orange-50:hover {
    --tw-bg-opacity: 1 !important;
    background-color: rgb(229,225,255) !important;
}
.to-orange-200 {
    --tw-gradient-to: rgb(37 56 133 / 37%) !important;
}
.from-orange-400 {
    --tw-gradient-from: rgb(17, 20, 45) !important;
    --tw-gradient-to: rgb(255 150 51 / 0);
    --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to) !important;
}
.group-hover\:from-orange-500 {
    --tw-gradient-from:rgb(17, 20, 45) !important; 
    --tw-gradient-to: rgb(37 56 133 / 37%);
    --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to) !important;
}
.group:hover .group-hover\:text-orange-500 {
    --tw-text-opacity: 1 !important;
    color:rgb(37 56 133 / var(--tw-text-opacity)) !important;
}
#image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: auto; /* Adjust the height as needed */
    margin-top: 20px; /* Adjust the margin as needed */
}
#compass-image {
    max-width: 800px; /* Adjust the width as needed */
    max-height: 600px; /* Adjust the height as needed */
    object-fit: contain; /* Maintains aspect ratio */
}
"""

# Initialize the InferenceClient for chatbot
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")

# Global variable to store chat history for the current session
current_chat_history = []

# Define the function for chatbot response
def respond(
    message,
    history,
    system_message,
    max_tokens,
    temperature,
    top_p,
):
    global current_chat_history
    
    messages = [{"role": "system", "content": system_message}]

    for val in history:
        if val[0]:
            messages.append({"role": "user", "content": val[0]})
        if val[1]:
            messages.append({"role": "assistant", "content": val[1]})
            current_chat_history.append(f"Assistant: {val[1]}")
    
    messages.append({"role": "user", "content": message})
    current_chat_history.append(f"User: {message}")
    
    response = ""

    for message in client.chat_completion(
        messages,
        max_tokens=max_tokens,
        stream=True,
        temperature=temperature,
        top_p=top_p,
    ):
        token = message.choices[0].delta.content
        response += token
        yield response

    # Append the assistant's final response to the history
    current_chat_history.append(f"Assistant: {response}")

def download_chat_history():
    # Join the current chat history into a single string
    history_str = "\n".join(current_chat_history)
    # Save the chat history to a text file
    with open("chat_history.txt", "w") as f:
        f.write(history_str)
    return "chat_history.txt"

def clear_chat_history():
    # Reset the current chat history
    global current_chat_history
    current_chat_history.clear()  # Clear the chat history
    return "Chat history cleared."
        
def send_message(message, history, system_message, max_tokens, temperature, top_p):
    if message:
        history.append((message, ""))
        response = respond(
            message=message,
            history=history,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        response_text = ""
        for r in response:
            response_text = r
        # Apply HTML formatting to headings
        formatted_response_text = response_text.replace(
            "Future Performance Prediction:", "<h2><strong>Future Performance Prediction</strong></h2>"
        ).replace(
            "Risk Analysis and Potential Issues:", "<h2><strong>Risk Analysis and Potential Issues</strong></h2>"
        ).replace(
            "Preventive Actions and Recommendations:", "<h2><strong>Preventive Actions and Recommendations</strong></h2>"
        )
        history[-1] = (message, formatted_response_text)
    return history, gr.update(value="")

# Excel reading function
def read_excel(file):
    df = pd.read_excel(file.name)
    return df.to_string()

# Create the Gradio interface
with gr.Blocks(css=css) as demo:
    # Introduction Tab
    with gr.Tab("NetPulse AI"):
        with gr.Row(elem_id="image-container"):
            gr.Image(image_url, elem_id="compass-image")
        
        gr.Markdown("# **NetPulse AI**")
        gr.Markdown("### **Developed by Team HELIX AI**")
        gr.Markdown("""
        **This project monitors network health using a Raspberry Pi, collecting data on CPU usage, temperature, signal strength, and packet loss. The data is logged in Excel, identifying abnormal conditions. Users upload the data to a Hugging Face chatbot for predictive analysis and optimization recommendations.**
        
        **Features:**
        - **Future Performance Prediction:** Identifies upcoming failure risks based on past data trends.
        - **Risk Analysis and Potential Issues:** Detects high-risk periods (e.g., peak CPU load at specific hours). Identifies network bottlenecks, low signal strength, or overheating components.
        - **Preventive Actions and Recommendations:** Suggests cooling measures if temperature spikes are detected. Recommends bandwidth optimization if packet loss is increasing. Alerts users about critical failures and suggests preventive maintenance.
        **Libraries Used:**
        - **Gradio:** For creating the user interface.
        - **Pandas:** For reading and analyzing Excel files.
        - **Hugging API and LLM:** Zephyr-7b-beta For utilizing state-of-the-art language models.
        
        **How It Works:**
        - **Detailed Analysis**
        1. Upload your data in form of excel file.
        2. Paste it in the Detailed Analysis Tab.
        3. Get detailed recommendations!
         - **General Chat for Network Optimization**
        1. Talk to AI for more suggestions and queries regarding Network Issues.
        """)
    
    # Detailed Analysis Tab
    with gr.Tab("Detailed Analysis"):
        gr.Markdown("# Detailed Analysis")
        gr.Markdown("Analyze network performance trends, predict potential issues, and receive tailored recommendations for optimization based on the uploaded data.</div>")
        
        system_message_career = gr.Textbox(value=system_message, visible=False)
        chatbot_career = gr.Chatbot()
        msg_career = gr.Textbox(label="Enter the Excel Copied Data here")
        
        with gr.Row():
            clear_career = gr.Button("New Chat")
            download_button = gr.Button("Download Chat History")
            submit_career = gr.Button("Submit")

        with gr.Row():
            download_output = gr.File(label="Download")
            download_button.click(download_chat_history, outputs=download_output)

        with gr.Row():
            clear_button = gr.Button("Clear Chat History")
            status_output = gr.Textbox(label="Status", interactive=False)  # Add a Textbox for status output
            clear_button.click(clear_chat_history, outputs=status_output)  # Use the status Textbox for output
        
        with gr.Accordion("Additional Inputs", open=False):
            max_tokens_career = gr.Slider(minimum=1, maximum=2048, value=1024, step=1, label="Max new tokens")
            temperature_career = gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature")
            top_p_career = gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)")

        def respond_wrapper_career(message, chat_history, system_message_val, max_tokens_val, temperature_val, top_p_val):
            chat_history, _ = send_message(
                message=message,
                history=chat_history,
                system_message=system_message_val,
                max_tokens=max_tokens_val,
                temperature=temperature_val,
                top_p=top_p_val,
            )
            return gr.update(value=chat_history), gr.update(value="")

        submit_career.click(
            respond_wrapper_career,
            inputs=[msg_career, chatbot_career, system_message_career, max_tokens_career, temperature_career, top_p_career],
            outputs=[chatbot_career, msg_career],
        )
        
        clear_career.click(lambda: None, None, chatbot_career, queue=False)

    # File Upload Tab
    with gr.Tab("Upload Data"):
        gr.Markdown("# Upload Data")
        file_input = gr.File(label="Upload Excel file")
        excel_output = gr.Textbox(label="Excel Content")
        file_input.change(read_excel, inputs=file_input, outputs=excel_output)
    
    # Simple Chatbot Tab (new tab integration)
    with gr.Tab("General Chat for Network Optimization"):
        gr.Markdown("# General Chat for Network Optimization")
        gr.Markdown("""
        A chatbot that provides predictive maintenance insights, cost optimization suggestions, and energy efficiency recommendations.
        """)

        system_message_simple = gr.Textbox(value="You are an AI powered chatbot named as NetPulse-AI built by team HelixAI that provides predictive maintenance insights, cost optimization suggestions, and energy efficiency recommendations for networks.", visible=False)
        chatbot_simple = gr.Chatbot()
        msg_simple = gr.Textbox(label="Type a message")
        
        with gr.Row():
            clear_simple = gr.Button("Clear")
            submit_simple = gr.Button("Submit")
        
        with gr.Accordion("Additional Inputs", open=False):
            max_tokens_simple = gr.Slider(minimum=1, maximum=2048, value=1024, step=1, label="Max new tokens")
            temperature_simple = gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature")
            top_p_simple = gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)")
        
        def respond_wrapper_simple(message, chat_history, system_message_val, max_tokens_val, temperature_val, top_p_val):
            chat_history, _ = send_message(
                message=message,
                history=chat_history,
                system_message=system_message_val,
                max_tokens=max_tokens_val,
                temperature=temperature_val,
                top_p=top_p_val,
            )
            return chat_history

        submit_simple.click(
            respond_wrapper_simple,
            inputs=[
                msg_simple,
                chatbot_simple,
                system_message_simple,
                max_tokens_simple,
                temperature_simple,
                top_p_simple,
            ],
            outputs=[chatbot_simple],
        )

        clear_simple.click(lambda: None, None, chatbot_simple)

# Launch the Gradio app
demo.launch()
