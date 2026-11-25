## How to build

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create `.streamlit/secrets.toml` with your Groq API credentials:

```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
GROQ_MODEL = "openai/gpt-oss-120b"
```

## Run

```bash
streamlit run app.py
```