# NetPulse AI

NetPulse AI is an AI-driven network monitoring and fault prediction system designed to enhance performance and reliability across industries.

## 👥 Our Team

- **Muhammad Hashir Ehtisham** - Team Leader & Pre-Engineering Student
- **Aditi Prabhakar** - Software Engineer
- **Momina Kanwal** - Software Engineer

## 🚀 Features
- **AI-Powered Monitoring** – Detects anomalies and predicts faults.
- **Future Performance Prediction** - Identifies upcoming failure risks based on past data trends.
- **Risk Analysis and Potential Issues** - Detects high-risk periods (e.g., peak CPU load at specific hours). Identifies network bottlenecks, low signal strength, or overheating components.
- **Preventive Actions and Recommendations** - Suggests cooling measures if temperature spikes are detected. Recommends bandwidth optimization if packet loss is increasing. Alerts users about critical failures and suggests
- **Real-Time Data Logging** – VB script logs real-time network data into excel file.
- **User-Friendly Interface** – Interactive UI built using Gradio.

## 📌 Tech Stack
- **SDK:** Gradio
- **Language:** Python
- **Application File:** `app.py`
- **Hardware Requirements:** Raspberry Pi, Sensors

## 📥 Installation & Setup
```bash
# Clone the repository
git clone https://github.com/hashir-ehtisham/NETPULSE-AI.git
cd NETPULSE-AI

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🔧 Requirements to Run VBS Script for Network Health Logging
1️⃣ **Enable Serial Communication**
   - Ensure Raspberry Pi sends data via serial (UART) to a COM port.
   - Identify the correct COM port (e.g., COM3).

2️⃣ **Install & Register MSComm32.ocx** (For Serial Port Communication)
   - Place `MSComm32.ocx` in:
     - `C:\Windows\System32\` (32-bit Windows)
     - `C:\Windows\SysWOW64\` (64-bit Windows)
   - Register via Command Prompt (Admin):
     ```bash
     regsvr32 C:\Windows\SysWOW64\MSComm32.ocx  # for 64-bit
     regsvr32 C:\Windows\System32\MSComm32.ocx  # for 32-bit
     ```
   - Restart your system after registering.

3️⃣ **Microsoft Excel Installed**
   - The script logs data into `network-data.xlsx`.
   - Ensure Microsoft Excel is installed on your PC.

4️⃣ **VBScript Enabled**
   - Run `wscript.exe` to verify VBScript is enabled.
   - Disable antivirus restrictions on `.vbs` scripts if necessary.

5️⃣ **Correct File Path & Permissions**
   - Ensure the script saves data to:
     ```
     D:\Apps by Hashir\Network Health Prediction\network-data.xlsx
     ```
   - Update the directory path if needed before execution.

6️⃣ **Run the Script**
   - Double-click the `.vbs` file to execute.
   - If using CMD, navigate to the script directory and run:
     ```bash
     cscript script.vbs
     ```
   - If no COM port is connected, the script may fail or loop indefinitely.

💡 **Tip:** If MSComm32 is not working, use PowerShell or Python for serial communication. 🚀

## 🤝 Contribution
Contributions are welcome! Submit pull requests or open issues for discussion.
