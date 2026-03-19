import os

path = 'c:/src/quorum/backend_v2/templates/report_template.jinja2'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix table layouts
text = text.replace(
    '<div style="display: table; width: 100%; margin-top: 25px;">',
    '<div style="display: block; width: 100%; margin-top: 25px;">'
)
text = text.replace(
    '<div style="display: table-cell; width: 220px; vertical-align: top; padding-right: 20px;">',
    '<div style="display: block; width: 100%; margin-bottom: 30px; text-align: center;">'
)
# Make the actual graph box stand in the middle
text = text.replace(
    '<div style="width: 200px; height: 200px; background: #fafafa; border: 1px solid #ddd; position: relative;">',
    '<div style="width: 200px; height: 200px; background: #fafafa; border: 1px solid #ddd; position: relative; margin: 0 auto; text-align: left;">'
)
text = text.replace(
    '<div style="width: 200px; height: 200px; background: #fafafa; border: 1px solid #ddd; position: relative; border-left: 2px solid #555; border-bottom: 2px solid #555;">',
    '<div style="width: 200px; height: 200px; background: #fafafa; border: 1px solid #ddd; position: relative; border-left: 2px solid #555; border-bottom: 2px solid #555; margin: 0 auto; text-align: left;">'
)
# Fix the right-side text container
text = text.replace(
    '<div style="display: table-cell; vertical-align: top;">',
    '<div style="display: block; width: 100%;">'
)
# Fix the overlapping Y-axis labels rotation origin
text = text.replace(
    'left: -110px; top: 90px; width: 200px;',
    'left: -130px; top: 90px; width: 240px;'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("PDF Layout template patched successfully.")
