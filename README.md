# AI File & Project Organizer

An intelligent Python automation script powered by Google Gemini AI that scans project directories, analyzes code snippets, and automatically groups loose files into structured project folders and categories.

---

## ✨ Features

* AI-Powered Code Analysis: Inspects file headers and code snippets to understand context and dependencies.
* Smart Project Grouping: Automatically identifies related files (e.g., main.py, config.py, database.db) and groups them into dedicated project directories.
* Fallback & Retry Mechanism: Automatically handles server rate limits (HTTP 503) and seamlessly falls back across multiple Gemini models (gemini-2.5-flash / gemini-1.5-flash).
* Structured Output: Enforces strict JSON responses using google-genai system configs.
* Safe Operations: Excludes system, environment, and configuration files (.git, .env, cache files) from being moved or overwritten.

---

## 🛠️ Requirements & Installation

1. Python 3.9+ installed on your system.
2. Install the required dependencies:

pip install google-genai

3. Set up your Gemini API Key in your environment variables:

Linux / macOS:
export GEMINI_API_KEY="your_api_key_here"

Windows (CMD):
set GEMINI_API_KEY="your_api_key_here"

Windows (PowerShell):
$env:GEMINI_API_KEY="your_api_key_here"

---

## 🚀 Usage

Place ai_sort.py inside the directory you wish to organize and run:

python ai_sort.py

### How It Works:
1. Manifest Building: Scans the current workspace and collects lightweight code snippets (up to 5 lines / 200 characters) from readable text files.
2. AI Categorization: Sends the workspace map to Gemini AI to generate an optimal folder structure plan.
3. Execution: Moves files safely into target category folders based on the AI plan.

---

## 📂 Categories Target
The AI organizes projects into the following directories:
* 1.Python/needs improvement — Python projects & scripts.
* 2.html/needs improvement — Web templates, HTML, CSS, JS scripts.
* 3.another — Miscellaneous files and assets.

---

## 🛡️ License
Distributed under the MIT License.
