import re

def fix_all_indentations():
    with open("backend_v2/tests/unit/services/test_blueprint.py", "r", encoding="utf-8") as f:
        content = f.read()

    # The issue is that I replaced "from backend_v2.services.blueprint import BlueprintTransformer"
    # with "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n        from backend_v2.services.blueprint import BlueprintTransformer"
    # globally!
    # Let's fix this by finding all lines with "        from backend_v2.services.blueprint import BlueprintTransformer"
    # and re-indenting them based on their surrounding context, OR just replacing them with 4 spaces since they are probably inside functions.
    # Wait, the best way is to revert the global replace.
    # Actually, the file uses 4 spaces for indentation inside functions.
    
    # We can just replace "        from backend_v2.services.blueprint import BlueprintTransformer" 
    # with "    from backend_v2.services.blueprint import BlueprintTransformer" if the context requires 4 spaces.
    
    # Let's just remove the bad lines and let ruff format it, or I can just fix it properly.
    
    # A safer approach: I will replace "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n        from backend_v2.services.blueprint import BlueprintTransformer" 
    # with "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n    from backend_v2.services.blueprint import BlueprintTransformer"
    content = content.replace(
        "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n        from backend_v2.services.blueprint import BlueprintTransformer",
        "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n    from backend_v2.services.blueprint import BlueprintTransformer"
    )

    with open("backend_v2/tests/unit/services/test_blueprint.py", "w", encoding="utf-8") as f:
        f.write(content)

fix_all_indentations()
print("Fixed all indentations")
