from tinydb import TinyDB, Query
import uuid

def seed_acemoglu():
    p = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(p)
    kb = db.table('knowledge_base')
    
    # 1. Acemoglu
    full_cit = "Acemoglu, Daron & Restrepo, Pascual. 2018: The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488–1542. DOI: 10.1257/aer.20160696."
    short_cit = "Acemoglu & Restrepo 2018"
    doi = "https://doi.org/10.1257/aer.20160696"
    
    # Check exist
    existing = kb.search(Query().short_citation == short_cit)
    if existing:
        print("Acemoglu already exists.")
    else:
        kb.insert({
            "id": str(uuid.uuid4()),
            "type": "reference",
            "citation": full_cit,
            "short_citation": short_cit,
            "doi_link": doi,
            "metadata": {"source": "manual_patch"}
        })
        print("Inserted Acemoglu.")

    # 2. Eloundou (From Context)
    # Eloundou ym. 2023 -> "Eloundou, Tyna et al. 2023: GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models."
    # I'll add a generic placeholder if not known, but I can guess from common knowledge or just leave it.
    # User specifically asked for Acemoglu link.
    
if __name__ == "__main__":
    seed_acemoglu()
