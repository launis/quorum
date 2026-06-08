import export_to_pdf

md = export_to_pdf.read_markdown_file('koko_arkkitehtuuri.md')
d = export_to_pdf.extract_mermaid_diagrams(md)
m1 = export_to_pdf.replace_mermaid_with_placeholders(md, d)
print("placeholder in m1:", "MERMAID_PLACEHOLDER_mermaid_diagram_1" in m1)

h1 = export_to_pdf.markdown_to_html(m1)
print("placeholder in h1:", "MERMAID_PLACEHOLDER_mermaid_diagram_1" in h1)
# print a snippet of where the placeholder is in h1
idx = h1.find("MERMAID_PLACEHOLDER_mermaid_diagram_1")
if idx != -1:
    print("h1 snippet:", repr(h1[max(0, idx-20):idx+50]))

h2 = export_to_pdf.inject_mermaid_html(h1, d)
print("placeholder in h2:", "MERMAID_PLACEHOLDER_mermaid_diagram_1" in h2)
print("class='mermaid' in h2:", "class=\"mermaid\"" in h2)
