# 🚨 InSecCam - CCTV Scanner 🔍 📹
InSecCam is a powerful yet lightweight Python tool designed to scan your local network’s default gateway for exposed IP cameras and CCTV devices. It identifies open ports commonly used by cameras, detects vendor fingerprints, and checks for accessible login pages — helping you secure your environment and protect your privacy.

## ✨ Features
🏠 Automatic Gateway Detection: Automatically finds your router’s IP to scan the correct local target.

⚡ Multi-threaded Port Scanning: Rapidly scans common CCTV/IP camera ports with threaded efficiency.

🔍 Vendor & Device Detection: Recognizes popular camera brands like Hikvision, Dahua, Axis, and more via HTTP headers and page content.

🔐 Authentication Page Discovery: Detects camera login pages and notes authentication requirements.

🎨 Color-Coded Console Output: Uses colorama for clear, easy-to-read terminal feedback.

🌐 Comprehensive Endpoint Checks: Probes typical camera URLs such as /admin, /login, /stream, etc.

🤝 Error-Resilient: Handles network errors gracefully without crashes.

## 🚀 How to Use

pip install -r requirements.txt
python insecam.py
Requires Python 3.x, plus requests and colorama.
For improved gateway detection, install netifaces (optional but recommended).

## ❓ Why Use InSecCam?
IP cameras and CCTV devices often have weak security or are unintentionally exposed on networks, posing privacy risks or unauthorized access threats.
InSecCam empowers security pros, network admins, and privacy-conscious users to identify and mitigate these exposures proactively.

## ⚠️ Disclaimer
This tool is intended only for ethical use on networks you own or have permission to audit. Unauthorized scanning or access is illegal and unethical. Use responsibly.

## 🤝 Contributions & Feedback
Contributions, feature requests, and bug reports are welcome! Open an issue or submit a pull request to help improve InSecCam.

## ☕ Support Me
If you like this project, feel free to [buy me a coffee](https://ko-fi.com/G2G114SBVV)!

[![Buy Me a Coffee](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/G2G114SBVV)

## Educational Purposes Only!! Stay safe, stay ethical. ✌️
