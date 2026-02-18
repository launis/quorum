
import json
import statistics

DB_PATH = r"c:\src\quorum\data\db.json"
OUT_PATH = r"c:\src\quorum\knowledge_snapshot.txt"

def analyze_knowledge_base():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        kb = data.get("knowledge_base", {})
        if not kb:
            print("No knowledge base found.")
            return

        items = list(kb.values()) if isinstance(kb, dict) else kb
        
        # Categorize
        concepts = [i for i in items if i.get("type") == "concept"]
        claims = [i for i in items if i.get("type") == "claim"]
        references = [i for i in items if i.get("type") == "reference"]
        
        with open(OUT_PATH, "w", encoding="utf-8") as out:
            out.write(f"--- KNOWLEDGE BASE SNAPSHOT ---\n")
            out.write(f"Total Items: {len(items)}\n")
            out.write(f"Concepts: {len(concepts)}\n")
            out.write(f"Claims: {len(claims)}\n")
            out.write(f"References: {len(references)}\n\n")
            
            # Helper to print stats
            def print_stats(label, subset):
                if not subset:
                    out.write(f"\n--- {label} (0) ---\n")
                    return
                
                lengths = [len(i.get("definition", "")) for i in subset]
                avg_len = statistics.mean(lengths) if lengths else 0
                max_len = max(lengths) if lengths else 0
                
                out.write(f"\n--- {label} ({len(subset)}) ---\n")
                out.write(f"Avg Definition Length: {avg_len:.0f} chars\n")
                out.write(f"Max Definition Length: {max_len} chars\n")
                
                # Samples
                out.write("Samples:\n")
                for i, item in enumerate(subset[:3]): # Take first 3
                    term = item.get("term", "N/A")
                    defn = item.get("definition", "N/A")
                    meta = item.get("metadata", {})
                    out.write(f"  [{i+1}] Term: {term}\n")
                    out.write(f"      Definition: {defn[:200].replace(chr(10), ' ')}...\n")
                    out.write(f"      Metadata: {json.dumps(meta, ensure_ascii=False)}\n")
            
            print_stats("CONCEPTS", concepts)
            print_stats("CLAIMS", claims)
            print_stats("REFERENCES", references)
            
        print(f"Snapshot written to {OUT_PATH}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_knowledge_base()
