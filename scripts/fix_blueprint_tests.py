import re

def fix_blueprint_tests():
    with open("backend_v2/tests/unit/services/test_blueprint.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Add import
    import_stmt = "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n"
    if "MatrixDomainParser" not in content:
        content = content.replace("from backend_v2.services.blueprint import BlueprintTransformer", 
                                  import_stmt + "        from backend_v2.services.blueprint import BlueprintTransformer")

    # Replace transformer._parse_matrix_trace_results with MatrixDomainParser.parse_matrices
    content = content.replace("transformer._parse_matrix_trace_results(", "MatrixDomainParser.parse_matrices(")

    with open("backend_v2/tests/unit/services/test_blueprint.py", "w", encoding="utf-8") as f:
        f.write(content)

fix_blueprint_tests()
print("Fixed test_blueprint.py")
