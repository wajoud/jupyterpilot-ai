# 🧠 JupyterPilot AI

**JupyterPilot AI** (`jupyterpilot-ai`) is a lightweight, provider-agnostic AI coding partner for IPython and Jupyter. It brings natural language code generation (`%do`) and automated error healing (`%fix`) to your notebook.

---

## 🚀 Features
- **%do <prompt>**: Transform instructions into Python code instantly.
- **%fix**: Post-mortem self-healing for your last error.
- **Context Awareness**: Remembers your last 3 cells for accurate variable usage.
- **Data Observer (New)**: Automatically detects Pandas DataFrames, SQL engines, and MongoDB databases to provide schema context to the AI.
- **Hybrid Support**: Switch between local **Ollama** and cloud **GPT-4o/Claude** via LiteLLM.

---

## 📥 Installation

```bash
pip install jupyterpilot-ai
```

### Enable Data Observer (Optional)
To enable automatic schema detection for Pandas, SQL, and MongoDB, install the data extras:
```bash
pip install "jupyterpilot-ai[data]"
```

### Enable the Extension
Add this to any cell in your notebook or your IPython startup script:
```python
%load_ext jupyterpilot_ai
```

---

## ⚙️ Configuration

JupyterPilot AI looks for a configuration file at `~/.jupyterpilot/config.json`. 

### Switching Modes
To switch between local and paid models, simply change the `"mode"` value in your config file:

```json
{
    "mode": "cloud", 
    "local": {
        "url": "http://localhost:11434/api/generate",
        "model": "qwen2.5-coder:7b"
    },
    "cloud": {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": "sk-..."
    }
}
```

- **Local Mode (`"mode": "local"`)**: 
  - Uses **Ollama** by default.
  - Requires Ollama to be running (`ollama run qwen2.5-coder:7b`).
  - You can customize the `url` and `model` in the `local` block.

- **Cloud Mode (`"mode": "cloud"`)**: 
  - Uses **LiteLLM** to connect to paid providers.
  - Supports OpenAI, Anthropic (Claude), Google (Gemini), etc.
  - Specify your `provider`, `model`, and `api_key`.

---

## 🛠️ Usage
- `%do plot a sine wave`
- `%fix` (after an error)

---

## 📬 Contact
**Wajoud Noorani** - [Wajoudnoorani59@gmail.com](mailto:wajoudnoorani59@gmail.com)

---

## 📄 License
MIT
