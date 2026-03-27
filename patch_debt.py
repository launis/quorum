import re

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove inspector_pane
    content = content.replace("import 'package:client_app/features/studio/views/widgets/inspector_pane.dart';", "")
    
    # 2. Remove _selectedNodeId
    content = re.sub(r'String\?\s+_selectedNodeId;\s*', '', content)
    
    # 3. Fix initialValue in Dropdown
    old_dropdown_val = "value: blueprints.any((bp) => bp['slug'] == stepDef['task_blueprint'])"
    new_dropdown_val = "initialValue: blueprints.any((bp) => bp['slug'] == stepDef['task_blueprint'])"
    content = content.replace(old_dropdown_val, new_dropdown_val)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Cleaned up debt!")

if __name__ == "__main__":
    main()
