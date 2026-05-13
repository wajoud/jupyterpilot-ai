# 🧠 JupyterPilot AI

**JupyterPilot AI** (`jupyterpilot-ai`) is a lightweight, provider-agnostic AI coding partner for IPython and Jupyter. It brings natural language code generation (`%do`) and automated error healing (`%fix`) to your notebook.

---

## 🚀 Features
- **%do <prompt>**: Transform instructions into Python code instantly.
- **%fix**: Post-mortem self-healing for your last error.
- **%review**: Analyze the previous cell and get optimization suggestions or code reviews.
- **Context Awareness**: Remembers your last 3 cells for accurate variable usage.
- **Data Observer (New)**: Automatically detects Pandas DataFrames, SQL engines, and MongoDB databases to provide schema context to the AI.
  - *Smart MongoDB Introspection*: Aggregates schema keys from the 20 most recent documents and extracts collection indexes, helping the AI write highly optimized queries.
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
    },
    "custom_link_ai": {
        "url": "",
        "model": "",
        "api_key": ""
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

- **Custom Link AI Mode (`"mode": "custom_link_ai"`)**:
  - Connect to your custom AI API endpoint directly.
  - Set your custom `url`, `model`, and `api_key`.

---

## 🛠️ Usage

### Basic Commands
- `%do plot a sine wave`
- `%fix` (after an error)
- `%review` (to review the last run cell)

### Advanced Data Observer Example
If you have `jupyterpilot-ai[data]` installed, simply connecting to your database in a cell is enough for the AI to understand your schema.

```python
# Cell 1: Connect to your database (Pandas, SQL, or Mongo)
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["Testing"]
```

```python
# Cell 2: Ask the AI to write a query without explaining your collections or fields!
%do find the most recently active admin user
```
*Behind the scenes, JupyterPilot automatically extracts the collection names, schema keys, and indices from `db` and injects them into the AI's context so it generates perfect code.*

---

## 📬 Contact
**Wajoud Noorani** - [Wajoudnoorani59@gmail.com](mailto:wajoudnoorani59@gmail.com)

---

## 📄 License
MIT
