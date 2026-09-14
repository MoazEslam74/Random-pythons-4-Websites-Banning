<p align="center">
  <img src="RP_Websites_Banning.ico" alt="Centered image" width="300">
</p>

# Website Access Control Tool

A robust, Python-based desktop application designed for Windows to manage and restrict access to specific websites. It prevents common bypass methods by modifying the Windows `hosts` file and preemptively disabling DNS over HTTPS (DoH) across major browsers.

## Key Features

* **Complete Blocking:** Automatically parses domains (handling both root and `www` versions) and routes them to localhost (`127.0.0.1`).
* **DoH Prevention:** Modifies the Windows Registry to disable DNS over HTTPS in Google Chrome, Microsoft Edge, Brave, Vivaldi, and Mozilla Firefox, preventing users from bypassing the `hosts` file.
* **Smart Scheduling:** Run restrictions in different modes:
  * **Always Blocked:** Permanent restriction.
  * **Hourly Duration:** Block for a specific number of minutes every hour.
  * **Time Range:** Block between specific hours (e.g., 14:00 to 18:00).
  * **Specific Days:** Enforce blocks only on selected days of the week.
* **Background Execution:** Minimizes to the background with zero console windows, utilizing lightweight recurring checks (every 10 seconds) without freezing the UI.
* **Bilingual Interface:** Built-in toggle between English and Arabic using standard `Tkinter`.
* **DNS Auto-Flush:** Automatically executes `ipconfig /flushdns` when restrictions change to ensure browsers instantly recognize the updated network state.

## Prerequisites & Libraries

This application is built entirely using **Python Standard Libraries**. You do not need to install any external packages via `pip` to run the source code. 

**Required Environment:**
* **OS:** Windows 10 or Windows 11 (Requires Administrator privileges to modify `hosts` and Registry).
* **Python:** Python 3.6 or higher.

**Standard Libraries Used:**
* `tkinter` (GUI framework)
* `winreg` (Windows Registry manipulation)
* `ctypes` (Admin privilege escalation & Console hiding)
* `json` (Saving and loading user settings)
* `os`, `sys`, `urllib.parse`, `datetime`

## Setup & Installation

1. **Clone or Download** the repository to your local Windows machine.
2. Ensure Python is installed and added to your system `PATH`.
3. Run the script directly by double-clicking `main.py` or executing it via command line:
   ```cmd
   python main.py

*Note: The script will automatically trigger a User Account Control (UAC) prompt to request the necessary Administrator privileges.*

## Usage Instructions

* **Adding a Site:** Type the URL (`example.com` or `https://www.exmple.com`) into the text field and click **Add to Blocklist**. Ensure all browsers are closed when prompted to apply registry changes successfully.

* **Removing a Site:** Click Remove next to the site in the list. The tool will automatically clean the `hosts`file, restore DoH settings if the list becomes empty, and flush the DNS cache.

* **Scheduling:** Navigate to the Scheduling tab, select your preferred time constraints, and click **Save Settings**. The tool evaluates the schedule in the background.

* **Background Mode:** Clicking the standard window close button (X) will hide the interface but keep the scheduler running in the background. To completely terminate the process, re-open the app and click **Exit Tool Completely**.