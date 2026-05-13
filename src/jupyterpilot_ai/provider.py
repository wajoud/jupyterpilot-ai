import json
import os
import requests

class LLMProvider:
    """Provider-agnostic LLM Engine for JupyterPilot."""
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        # Priority: 1. Specified path, 2. User-specific config, 3. Global config
        user_config = os.path.expanduser("~/.jupyterpilot/config.json")
        global_config = "/etc/jupyterpilot/config.json"
        
        path = self.config_path
        if not path:
            if os.path.exists(user_config):
                path = user_config
            elif os.path.exists(global_config):
                path = global_config
        
        if path and os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.config = json.load(f)
                    return
            except Exception as e:
                print(f"# Warning: Failed to load config from {path}: {e}")

        # Default fallback settings
        self.config = {
            "mode": "local",
            "local": {"url": "http://localhost:11434/api/generate", "model": "qwen2.5-coder:7b"},
            "cloud": {"model": "gpt-4o", "provider": "openai"},
            "custom_link_ai": {
                "url": "",
                "model": "",
                "api_key": ""
            }
        }

    def generate(self, prompt, context="", system_prompt=None, raw=False):
        if system_prompt is None:
            system_prompt = "You are JupyterPilot, a high-performance coding assistant. Return ONLY executable Python code. No markdown, no explanations."
        full_prompt = f"{system_prompt}\n\nContext from previous cells:\n{context}\n\nTask: {prompt}"
        
        if self.config.get("mode") == "local":
            text = self._generate_local(full_prompt)
        elif self.config.get("mode") == "custom_link_ai":
            text = self._generate_custom_link_ai(full_prompt)
        else:
            text = self._generate_cloud(full_prompt)
            
        if raw:
            return text
        return self._clean_code(text)

    def _generate_local(self, prompt):
        local_cfg = self.config.get("local", {})
        url = local_cfg.get("url", "http://localhost:11434/api/generate")
        model = local_cfg.get("model", "qwen2.5-coder:7b")
        try:
            response = requests.post(
                url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=15
            )
            text = response.json().get("response", "").strip()
            return text
        except Exception as e:
            return f"# Local Inference Error: {e}"

    def _generate_cloud(self, prompt):
        try:
            import litellm
            cloud_cfg = self.config.get("cloud", {})
            model = cloud_cfg.get("model", "gpt-4o")
            
            if "api_key" in cloud_cfg:
                provider = cloud_cfg.get("provider", "openai").upper()
                os.environ[f"{provider}_API_KEY"] = cloud_cfg["api_key"]
            
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            return text
        except Exception as e:
            return f"# Cloud Inference Error: {e}"

    def _generate_custom_link_ai(self, prompt):
        cfg = self.config.get("custom_link_ai", {})
        url = cfg.get("url", "")
        model = cfg.get("model", "")
        api_key = cfg.get("api_key", "")
        
        if not url:
            return "# Error: custom_link_ai url not configured in config.json"
            
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                
            response = requests.post(
                url,
                headers=headers,
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                timeout=30
            )
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return text
        except Exception as e:
            return f"# Custom Link AI Inference Error: {e}"

    def _clean_code(self, text):
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                if part.strip().startswith(("python", "py")):
                    return "\n".join(part.strip().splitlines()[1:]).strip()
                if len(part.strip()) > 5:
                    return part.strip()
        return text.strip()
