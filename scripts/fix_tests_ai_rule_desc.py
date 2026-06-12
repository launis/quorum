import glob
import re


def fix_tests():
    files = glob.glob('c:/src/quorum/backend_v2/tests/**/*.py', recursive=True)

    dict_pattern = re.compile(r'"ai_rule_description":\s*("[^"]*")')
    kwarg_pattern = re.compile(r'ai_rule_description=("[^"]*"|f"[^"]*")')

    for path in files:
        with open(path, encoding='utf-8') as f:
            content = f.read()

        if 'ai_rule_description' not in content:
            continue

        # Replace dict string: "ai_rule_description": "rule"
        # with "concept_description": {"default_locale": "en", "translations": {"en": "rule"}}
        content = dict_pattern.sub(r'"concept_description": {"default_locale": "en", "translations": {"en": \1}}', content)

        # Replace kwarg: ai_rule_description="rule"
        # with concept_description=I18nText(default_locale="en", translations={"en": "rule"})
        content = kwarg_pattern.sub(r'concept_description=I18nText(default_locale="en", translations={"en": \1})', content)

        # Add I18nText import if missing and used
        if 'I18nText' in content and 'from backend_v2.models.v2_core import' not in content:
            pass # Usually it's better to just manually fix imports, or let ruff auto-fix if possible, but let's try injecting.

        if 'I18nText' in content and 'I18nText' not in [line for line in content.split('\n') if line.startswith('from ')]:
            # Find the last import
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i

            lines.insert(last_import_idx + 1, "from backend_v2.models.v2_core import I18nText")
            content = '\n'.join(lines)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    fix_tests()
