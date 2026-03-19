import re

file_path = r'c:\src\quorum\backend_v2\templates\report_template.jinja2'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace 1D gauge 100.0 default
text = text.replace("{% set max1d = comp.scale_max | float | default(100.0, true) %}", "{% set max1d = comp.scale_max | float %}")

# Replace 2D/3D x_scale_max default
text = text.replace("{% set max_x = comp.get('x_scale_max', 6.0) | float | default(6.0, true) %}", "{% set max_x = comp.get('x_scale_max') | float %}")

# Replace 2D/3D y_scale_max default
text = text.replace("{% set max_y = comp.get('y_scale_max', 6.0) | float | default(6.0, true) %}", "{% set max_y = comp.get('y_scale_max') | float %}")

# Replace 3D z_scale_max default
text = text.replace("{% set max_z = comp.z_scale_max | float | default(100.0, true) %}", "{% set max_z = comp.z_scale_max | float %}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully removed all hardcoded Jinja fallbacks.')
