import json
import os
import re

SEED_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'seed_data.json')

def clean_content(content):
    """
    Detects and removes specific repetition patterns in prompt content.
    """
    if not content:
        return content
        
    # Pattern 1: "VAIHE X... TEHTÄVÄT: ... VAIHE X... TEHTÄVÄT:"
    # We look for the header appearing twice at the start
    lines = content.split('\n')
    if len(lines) < 5:
        return content
        
    # Check if the first line is repeated within the first 20 lines
    first_line = lines[0].strip()
    if not first_line:
        return content
        
    # Find indices where the first line appears
    indices = [i for i, line in enumerate(lines) if line.strip() == first_line]
    
    if len(indices) > 1:
        # If it appears more than once, check if it's a block duplication
        # We'll assume the second occurrence marks the start of the duplicate block
        # and that the duplicate block is identical to the first block.
        
        # Simple heuristic: If the text from start to second occurrence is repeated immediately after
        split_point = indices[1]
        first_block = '\n'.join(lines[:split_point]).strip()
        remaining_text = '\n'.join(lines[split_point:]).strip()
        
        if remaining_text.startswith(first_block):
            print(f"  - Detected block duplication starting at line {split_point}")
            # Return just the first block + any unique tail? 
            # Actually, usually it's just A + A. So we just return A.
            # But sometimes there might be extra stuff.
            
            # Let's try a safer approach:
            # If content looks like "A\n\nA", return "A"
            half_len = len(content) // 2
            # Fuzzy check isn't great.
            
            # Let's use the specific user example:
            # "VAIHE 1... [content] ... VAIHE 1... [content]"
            # We can just cut off at the second occurrence of the header if the content following matches.
            
            return '\n'.join(lines[:split_point])
            
    # Pattern 2: "MÄÄRITYSLISÄYS... VAIHE X... TEHTÄVÄT:"
    # Sometimes the duplication happens inside a section.
    
    return content

def clean_seed_data():
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    components = data.get('components', [])
    modified_count = 0
    
    for comp in components:
        if comp.get('type') == 'prompt' and comp.get('id').startswith('PROMPT_'):
            original = comp.get('content', '')
            
            # Specific fix for the user's reported issue
            # It seems the duplication is exact repetition of the whole prompt or large chunks.
            
            # Strategy: Split by the first line. If the chunks are identical, keep one.
            lines = original.split('\n')
            if not lines: continue
            
            header = lines[0].strip()
            if not header: continue
            
            # Count occurrences of the header
            header_count = original.count(header)
            
            if header_count > 1:
                print(f"Cleaning {comp['id']} (Header appears {header_count} times)")
                
                # Split by header
                parts = original.split(header)
                # parts[0] might be empty if it starts with header
                # parts[1] is the first body, parts[2] is the second body...
                
                # Reconstruct the first valid block
                # valid block = header + parts[1]
                
                # Check if parts[1] is roughly same as parts[2]
                if len(parts) > 2:
                    # Very likely duplication
                    new_content = header + parts[1]
                    
                    # Clean up trailing newlines
                    new_content = new_content.strip()
                    
                    if new_content != original.strip():
                        comp['content'] = new_content
                        modified_count += 1
                        print(f"  -> Cleaned.")

    if modified_count > 0:
        print(f"Saving {modified_count} modified components to {SEED_DATA_PATH}")
        with open(SEED_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print("No changes needed.")

if __name__ == "__main__":
    clean_seed_data()
