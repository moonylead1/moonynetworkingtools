# moony's NetTools

## Overview

**moony's NetTools** is a console-based application built with Python using the `textual` framework. This tool provides real-time network diagnostics, including ping monitoring and internet speed testing. It features dynamic logging, responsive statistics, and an intuitive user interface.

## Version

Current Version: **1.0.0 (dev)**

## Features

- **Ping Monitoring**: Track the responsiveness of any IP or domain.
- **Speed Testing**: Measure your internet speed with ease.
- **Dynamic Logging**: View logs in real-time for better tracking.
- **Responsive Statistics**: Get average ping, packet loss, and other metrics at a glance.
- **Integrated Speed Test Display**: View download and upload speeds along with latency.
- **Custom Dark Mode Toggle**: A more comfortable viewing experience in low-light conditions.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/moonylead1/moonynetworkingtools.git
   cd ping-speed-monitor
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
-  Ensure that the following libraries are included in your requirements.txt:
   ```
   textual pythonping speedtest-cli
3. **Run the application:**
   ```bash
   python main.py
**Interface Overview:**
   - Enter an IP address or domain in the input field and click "Set" to configure your ping target.
   - Use "Start" to begin monitoring pings and "Stop" to end monitoring.
   - Click "Speed Test" to measure your internet speed.
   - Toggle dark mode by pressing the d key.
   ```
   Key Bindings:
      F5: Start ping monitoring
      F6: Stop ping monitoring
      F7: Run speed test
      d: Toggle dark mode
      c: Clear logs
      r: Reset statistics
      Ctrl+C: Quit the application
   ```
**Troubleshooting:**
- Common Issues:
   - If the application fails to run, ensure all dependencies are installed and you're using Python 3.7 or higher.
   - For any errors during speed tests, check your internet connection and ensure no firewall settings are blocking the application.
   
**Contributing:**
- Contributions are welcome! If you find any bugs or would like to add features, please fork the repository and create a pull request.

**Acknowledgments:**
   - textual: For building the console interface.
   - pythonping: For ping functionality.
   - speedtest-cli: For measuring internet speed.
