import os
import re

lib_dir = "c:/src/quorum/client_app/lib"

error_view_import = "import 'package:client_app/core/ui/error_view.dart';"
debug_print_template = "debugPrint('🔴 UI GRACEFUL DEGRADATION: [{component}] fallback.');\n  "

def process_dart_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    filename = os.path.basename(filepath).replace(".dart", "")
    
    # 1. Replace Text('Error...') combinations with ErrorView inside error: (e, s) blocks
    # Looking for: error: (err, st) => Center(child: Text('Error: $err')),
    # Looking for: error: (err, _) => Text('Error loading strategies: $err', ...)
    
    # Strategy: Find error: (err, st) => [some Text/Center] and replace.
    # We will do some manual exact replacements first because regex can mess up flutter brackets.
    replacements = [
        ("error: (err, st) => Center(child: Text('Error: $err')),", "error: (err, st) => ErrorView(error: err, compact: true),"),
        ("child: Text('Error: $error', style: const TextStyle(color: Colors.red)),", "child: ErrorView(error: error, compact: true),"),
        ("error: (err, st) => Center(child: Text('Error loading editor: $err')),", "error: (err, st) => ErrorView(error: err),"),
        ("error: (err, _) => Text('Error loading strategies: $err', style: TextStyle(color: Theme.of(context).colorScheme.error)),", "error: (err, _) => ErrorView(error: err, compact: true),"),
        ("error: (e, _) => Text('Error loading schema: $e'),", "error: (e, _) => ErrorView(error: e, compact: true),"),
        ("return Center(child: Text('Error: ${stepsState.error}'));", "return ErrorView(error: stepsState.error!);"),
        ("error: (err, stack) => Text('Error loading components', style: TextStyle(color: Theme.of(context).colorScheme.error)),", "error: (err, stack) => ErrorView(error: err, compact: true),"),
        ("child: Text('Error: No \"items\" definition in array schema.'),", "child: const ErrorView(error: 'No items definition in array', compact: true),"),
        ("? Center(child: Text('Error: ${componentsState.error}'))", "? ErrorView(error: componentsState.error!)"),
        ("error: (e, s) => Text('Error loading limits: $e'),", "error: (e, s) => ErrorView(error: e, compact: true),"),
        ("child: SelectableText('Error: $e'),", "child: ErrorView(error: e),"),
        ("child: Text('Error: $err', style: const TextStyle(color: Colors.red)),", "child: ErrorView(error: err, compact: true),"),
        ("error: (err, st) => Center(child: SelectableText('Error: $err')),", "error: (err, st) => ErrorView(error: err, compact: true),")
    ]

    for old_str, new_str in replacements:
        if old_str in content:
            content = content.replace(old_str, new_str)
            modified = True

    # 2. Find SizedBox.shrink() that are fallbacks and inject debugPrint IF not already there
    # For one-liners like `if (foo == null) return const SizedBox.shrink();`
    # replace with `if (foo == null) { debugPrint('🔴 UI GRACEFUL DEGRADATION: [filename] fallback'); return const SizedBox.shrink(); }`
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if "SizedBox.shrink()" in line and "return" in line and "debugPrint" not in line:
            # Check if it's a one line if statement
            if "if (" in line and ") return " in line:
                # E.g. `    if (workflow == null) return const SizedBox.shrink();`
                match = re.search(r'^(\s*)if \((.*?)\) return const SizedBox.shrink\(\);', line)
                if match:
                    indent = match.group(1)
                    cond = match.group(2)
                    new_line = f"{indent}if ({cond}) {{ debugPrint('🔴 UI GRACEFUL DEGRADATION: [{filename}] Fallback for {cond}'); return const SizedBox.shrink(); }}"
                    new_lines.append(new_line)
                    modified = True
                    continue
                match2 = re.search(r'^(\s*)if \((.*?)\) return SizedBox.shrink\(\);', line)
                if match2:
                    indent = match2.group(1)
                    cond = match2.group(2)
                    new_line = f"{indent}if ({cond}) {{ debugPrint('🔴 UI GRACEFUL DEGRADATION: [{filename}] Fallback for {cond}'); return const SizedBox.shrink(); }}"
                    new_lines.append(new_line)
                    modified = True
                    continue
            
            # Check for error blocks: `error: (err, _) => const SizedBox.shrink(),`
            if "error:" in line and "=>" in line:
                match = re.search(r'^(\s*)error:\s*\((.*?)\)\s*=>\s*const SizedBox.shrink\(\),', line)
                if match:
                    indent = match.group(1)
                    vars = match.group(2)
                    new_line = f"{indent}error: ({vars}) {{ debugPrint('🔴 UI GRACEFUL DEGRADATION: [{filename}] Error: ${vars.split(',')[0].strip()}'); return const SizedBox.shrink(); }},"
                    new_lines.append(new_line)
                    modified = True
                    continue
            
        new_lines.append(line)
        
    content = '\n'.join(new_lines)
            
    # Add import if ErrorView was added
    if "ErrorView(" in content and "error_view.dart" not in content:
        # insert after first import
        content_lines = content.split('\n')
        for i, line in enumerate(content_lines):
            if line.startswith('import '):
                content_lines.insert(i + 1, error_view_import)
                break
        content = '\n'.join(content_lines)
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modified {filepath}")

for root, _, files in os.walk(lib_dir):
    for file in files:
        if file.endswith('.dart'):
            process_dart_file(os.path.join(root, file))

print("DONE")
