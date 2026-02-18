
import json

DB_PATH = r"c:\src\quorum\data\db.json"
QUERIES = ["tekoäly", "strategia", "mittaaminen", "Bloomin taksonomia"]
MAX_CONTEXT = 15000 
OUT_PATH = r"c:\src\quorum\retrieval_simulation.txt"

def simulate_retrieval():
    try:
        with open(OUT_PATH, "w", encoding="utf-8") as out:
            def log(msg):
                out.write(msg + "\n")
                print(msg) 

            log("--- RETRIEVAL SIMULATION ---")
            
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            kb = data.get("knowledge_base", {})
            if not kb:
                log("No knowledge base found.")
                return

            items = list(kb.values()) if isinstance(kb, dict) else kb
            
            for q in QUERIES:
                log(f"\nQUERY: '{q}'")
                matches = []
                lower_q = q.lower()
                
                for item in items:
                    term = item.get("term", "").lower()
                    defn = item.get("definition", "").lower()
                    if lower_q in term or lower_q in defn:
                        matches.append(item)
                
                limited_matches = matches[:20]
                total_chars = sum(len(m.get("definition", "")) + len(m.get("term", "")) for m in limited_matches)
                
                log(f"  Matches Found: {len(matches)}")
                log(f"  Matches Returned (Top 20): {len(limited_matches)}")
                log(f"  Context Usage: {total_chars} chars (~{total_chars//4} tokens)")
                
                if total_chars > MAX_CONTEXT:
                    log("  WARNING: Exceeds safe context limit!")
                else:
                    log("  STATUS: OK")

                log("  Top 3 Results:")
                for i, m in enumerate(limited_matches[:3]):
                    term = m.get("term", "?")
                    defn = m.get("definition", "")[:100].replace("\n", " ") + "..."
                    type_ = m.get("type", "?")
                    log(f"    [{i+1}] {type_}: {term} | {defn}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simulate_retrieval()
