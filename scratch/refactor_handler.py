import re
import sys

def main():
    path = "backend_v2/llm/handler.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the fetch_all_available_models method
    match = re.search(r'(    def fetch_all_available_models.*?        # --- MOCK ---)', content, re.DOTALL)
    if not match:
        print("Could not find start of fetch_all_available_models")
        return
    
    mock_start = content.find('        # --- MOCK ---')
    google_start = content.find('        # --- GOOGLE (Vertex AI) ---')
    openai_start = content.find('        # --- OPENAI ---')
    anthropic_start = content.find('        # --- ANTHROPIC (Direct API) ---')
    return_start = content.find('        return models', anthropic_start)

    mock_block = content[mock_start:google_start]
    google_block = content[google_start:openai_start]
    openai_block = content[openai_start:anthropic_start]
    anthropic_block = content[anthropic_start:return_start]

    # Create helper methods
    helpers = f"""
    def _fetch_mock_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
{mock_block.replace('        # --- MOCK ---\n', '')}
    def _fetch_google_models(self, providers: list[str], target_location: str, settings: Any, models: dict[str, list[str] | str]) -> None:
{google_block.replace('        # --- GOOGLE (Vertex AI) ---\n', '')}
    def _fetch_openai_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
{openai_block.replace('        # --- OPENAI ---\n', '')}
    def _fetch_anthropic_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
{anthropic_block.replace('        # --- ANTHROPIC (Direct API) ---\n', '')}"""

    # We need to fix the return in mock logic, as it returned models directly.
    # We will modify the new fetch_all_available_models logic to handle this.
    
    helpers = helpers.replace('return models  # Should matching mock logic, but simplifying', 'return')
    helpers = helpers.replace('return models\n', 'return\n')
    
    new_method = """        # Delegate to helpers
        if settings.use_mock_llm or "mock" in providers:
            self._fetch_mock_models(providers, settings, models)
            if settings.use_mock_llm and "mock" not in providers:
                return models
            if len(providers) == 1 and "mock" in providers:
                return models

        if "google" in providers:
            self._fetch_google_models(providers, target_location, settings, models)

        if "openai" in providers:
            self._fetch_openai_models(providers, settings, models)

        if "anthropic" in providers:
            self._fetch_anthropic_models(providers, settings, models)

"""

    new_content = content[:mock_start] + new_method + content[return_start:]
    
    # insert helpers right after __init__
    init_end = new_content.find('    def fetch_all_available_models')
    new_content = new_content[:init_end] + helpers.strip() + "\n\n" + new_content[init_end:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("Refactor complete!")

if __name__ == "__main__":
    main()
