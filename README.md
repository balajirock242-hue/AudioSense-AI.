# 🎛️ AudioSense AI
## IBM Granite Powered Audio Signal Processing Assistant Agent

> **Problem Statement 32** — AI Assistant for Electronics and Telecommunication Engineering:  
> Troubleshoot audio preamplifiers, filters, amplifiers and audio circuits.

---

## Features

| Feature | Description |
|---|---|
| 🔊 **Noise Troubleshooter** | Diagnose 50/60 Hz hum, ground loops, power-supply ripple, shielding issues |
| 🔧 **Filter Assistant** | Calculate RC cutoff frequency (fc = 1/2πRC) for LP/HP/BP/Notch filters |
| ⚡ **Amplifier Troubleshooter** | Systematic diagnosis for no output, low gain, distortion, clipping, oscillation, overheating, DC offset |
| 💡 **Circuit Advisor** | AI-powered Q&A on op-amps, grounding, shielding, feedback, and distortion |
| ⚡ **Quick Diagnosis** | Describe your problem in plain language — AI classifies and answers |

---

## Project Structure

```
AudioSense-AI/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Streamlit application entry point
│   ├── config.py                # Environment variable management
│   ├── granite_service.py       # IBM Granite / watsonx.ai integration
│   ├── filter_calculator.py     # RC cutoff calculator + query classifier
│   ├── noise_troubleshooter.py  # Noise diagnosis data and formatter
│   ├── amplifier_troubleshooter.py  # Amplifier symptom diagnosis
│   └── circuit_advisor.py       # AI circuit Q&A wrapper
├── knowledge_base/
│   └── audio_engineering.md     # Local reference knowledge base
├── tests/
│   ├── __init__.py
│   ├── test_filter_calculator.py  # RC calculator tests
│   └── test_query_classifier.py   # Query classification tests
├── .env.example                 # Credential template (copy to .env)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Quick Start

### 1. Clone / open the project

```bash
cd AudioSense-AI
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure IBM Granite (optional)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_GRANITE_MODEL=ibm/granite-4-h-small
IBM_ENDPOINT=https://us-south.ml.cloud.ibm.com
```

Also install the IBM watsonx.ai SDK:
```bash
pip install ibm-watsonx-ai
```

> Without credentials, the app runs in clearly-labelled **Demo Mode**.  
> Demo Mode responses are **never** claimed to be from IBM Granite.

### 5. Load environment variables

```bash
# Windows PowerShell
Get-Content .env | ForEach-Object { if ($_ -match "^([^#][^=]*)=(.*)$") { [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim()) } }

# macOS/Linux
export $(cat .env | grep -v '#' | xargs)
```

### 6. Run the application

```bash
streamlit run app/main.py
```

The app will open at **http://localhost:8501**

### 7. Run tests

```bash
pytest tests/ -v
```

---

## IBM Granite Integration

AudioSense AI uses the [IBM watsonx.ai](https://www.ibm.com/watsonx) platform to serve IBM Granite large language models.

**Important:**
- Credentials are loaded **exclusively from environment variables**. They are **never hard-coded**.
- Without valid credentials, the app runs in **Demo Mode** — a clearly labelled fallback using the built-in knowledge base.
- The UI always shows whether responses come from IBM Granite (🟢) or Demo Mode (🟡).
- No demo response will ever claim to be from IBM Granite.

---

## Filter Assistant — RC Cutoff Formula

```
fc = 1 / (2 × π × R × C)
```

Example: **10 kΩ + 15.9 nF ≈ 1 kHz**

Supported units:
- Resistance: **Ω**, **kΩ**, **MΩ**
- Capacitance: **pF**, **nF**, **µF**

---

## Engineering Disclaimer

> ⚠️ **All results are educational guidance only.**  
> Circuit conditions, component ratings, supply voltages, and thermal limits  
> **must be verified from manufacturer datasheets** before making any hardware changes.  
> This tool does not replace professional circuit design review.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python 3.9+ |
| AI Backend | IBM Granite (via ibm-watsonx-ai SDK) |
| Testing | pytest |

---

## License

MIT License — see [LICENSE](LICENSE)
