import re
import sys

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Add imports if needed
    imports_to_add = """import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
"""
    if "mcp_gateways_controller.dart" not in content:
        content = content.replace("import 'package:client_app/features/studio/views/widgets/dag_canvas_view.dart';",
                                  "import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';")

    # 2. Add mcpGatewaysAsync watch inside build()
    # It starts around: final stepsAsync = ref.watch(stepsControllerProvider);
    if "final mcpGatewaysAsync" not in content:
        content = content.replace(
            "final stepsAsync = ref.watch(stepsControllerProvider);",
            "final stepsAsync = ref.watch(stepsControllerProvider);\n    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);\n    final mcpGateways = mcpGatewaysAsync.value ?? [];"
        )
    
    # 3. Update _addStep()
    content = content.replace(
        "        'input_mappings': <String, dynamic>{'inputs': '\\$inputs'},\n      });",
        "        'input_mappings': <String, dynamic>{'inputs': '\\$inputs'},\n        'allowed_mcp_tools': <String>[],\n      });"
    )

    # 4. Replace DAG Container entirely with the Step ListView
    # From: // DAG Steps Canvas (V2 V3 Architecture)
    # To:   const SizedBox(height: 16), BEFORE Expected Inputs? No, DAG is after.
    
    dag_start = content.find("// DAG Steps Canvas")
    if dag_start == -1:
        print("Could not find DAG Steps Canvas marker!")
        return
        
    # Find the end of the Container that wraps DagCanvasView.
    # It ends at children: [\n        Expanded(... DagCanvasView ... InspectorPane ... 
    # We will just regex it out up to the next ], which is the end of the Column children.
    # Wait, it ends just before `],` which belongs to the Column.
    
    # Let's find the closing brackets of the Children array.
    column_end = content.find("            ],\n          ),\n        ),\n      ),\n    );\n  }")
    if column_end == -1:
        print("Could not find end of Column")
        return
        
    replacement_ui = """
              // Restored Legacy V1 Step List UI
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Steps & Dependencies',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addStep,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Step Node'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...SafeCast.safeList(_editableWorkflow['steps']).asMap().entries.map((entry) {
                final allSteps = SafeCast.safeList(_editableWorkflow['steps'])
                    .map((s) => SafeCast.safeMap(s))
                    .toList();
                return _buildStepCard(
                  entry.key,
                  SafeCast.safeMap(entry.value),
                  stepsList, 
                  allSteps,
                  mcpGateways,
                  l10n,
                );
              }),
"""
    
    new_content = content[:dag_start] + replacement_ui + content[column_end:]

    # 5. Add the _buildStepCard method at the end of the class.
    
    step_card_code = """
  Widget _buildStepCard(
    int index,
    Map<String, dynamic> stepDef,
    List<Map<String, dynamic>> blueprints,
    List<Map<String, dynamic>> allSteps,
    List<Map<String, dynamic>> mcpGateways,
    AppLocalizations l10n,
  ) {
    final stepIdController = TextEditingController(
      text: SafeCast.safeString(stepDef['id'], stepDef['step_id']),
    );

    final previousSteps = allSteps
        .map((s) => SafeCast.safeString(s['id'], s['step_id']))
        .where((id) => id.isNotEmpty && id != stepIdController.text)
        .toList();

    final dependsOn = SafeCast.safeList(stepDef['depends_on'])
        .map((e) => e.toString())
        .toList();

    final mappings = SafeCast.safeMap(stepDef['input_mappings'])
        .map((k, v) => MapEntry(k.toString(), v.toString()));
        
    final allowedMcpTools = SafeCast.safeList(stepDef['allowed_mcp_tools'])
        .map((e) => e.toString())
        .toList();

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Step ${index + 1}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () {
                    setState(() {
                      SafeCast.safeList(
                        _editableWorkflow['steps'],
                      ).removeAt(index);
                    });
                  },
                ),
              ],
            ),
            const Divider(),

            Row(
              children: [
                Expanded(
                  child: Focus(
                    onFocusChange: (f) {
                      if (!f) stepDef['id'] = stepIdController.text;
                    },
                    child: TextField(
                      controller: stepIdController,
                      decoration: const InputDecoration(
                        labelText: 'Node ID (e.g. step_1)',
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Task Blueprint (Cognitive Engine)',
                    ),
                    value: blueprints.any((bp) => bp['slug'] == stepDef['task_blueprint'])
                            ? stepDef['task_blueprint'] as String?
                            : null,
                    items: blueprints.map((bp) {
                          final slug = SafeCast.safeString(bp['slug']);
                          final nameMap = SafeCast.safeMap(bp['name']);
                          final enName = SafeCast.safeString(nameMap['en']);
                          final label = enName.isNotEmpty ? enName : slug;
                          return DropdownMenuItem(
                            value: slug,
                            child: Text(label),
                          );
                        }).toList(),
                    onChanged: (val) => setState(() => stepDef['task_blueprint'] = val),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Text(
              'Depends On (Executes AFTER these steps complete)',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            Wrap(
              spacing: 8,
              children: previousSteps.map((prevStepId) {
                    final isSelected = dependsOn.contains(prevStepId);
                    return FilterChip(
                      label: Text(prevStepId),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            dependsOn.add(prevStepId);
                          } else {
                            dependsOn.remove(prevStepId);
                          }
                          stepDef['depends_on'] = dependsOn;
                        });
                      },
                    );
                  }).toList(),
            ),
            if (previousSteps.isEmpty)
              const Text(
                'No previous steps available to depend on.',
                style: TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
              ),

            // Outputs like coaching (MCP Gateway integration)
            const SizedBox(height: 16),
            const Text(
              'Allowed MCP Gateways (e.g. Coaching, External Systems)',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            Wrap(
              spacing: 8,
              children: mcpGateways.map((mcp) {
                    final mcpId = SafeCast.safeString(mcp['id']);
                    final isSelected = allowedMcpTools.contains(mcpId);
                    return FilterChip(
                      label: Text(mcpId),
                      selected: isSelected,
                      selectedColor: Colors.purple.withAlpha(50),
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            allowedMcpTools.add(mcpId);
                          } else {
                            allowedMcpTools.remove(mcpId);
                          }
                          stepDef['allowed_mcp_tools'] = allowedMcpTools;
                        });
                      },
                    );
                  }).toList(),
            ),
            if (mcpGateways.isEmpty)
              const Text(
                'No MCP gateways configured in system.',
                style: TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
              ),

            const SizedBox(height: 16),
            const Text(
              'Input Mappings',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  ...mappings.entries.map((m) {
                    final targetCtrl = TextEditingController(text: m.key);
                    final sourceCtrl = TextEditingController(text: m.value.toString());
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: Focus(
                              onFocusChange: (f) {
                                if (!f && targetCtrl.text.isNotEmpty && sourceCtrl.text.isNotEmpty) {
                                  mappings.remove(m.key);
                                  mappings[targetCtrl.text] = sourceCtrl.text;
                                  stepDef['input_mappings'] = mappings;
                                }
                              },
                              child: TextField(
                                controller: targetCtrl,
                                decoration: const InputDecoration(
                                  labelText: 'Step Internal Variable',
                                  isDense: true,
                                ),
                              ),
                            ),
                          ),
                          const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 8.0),
                            child: Icon(Icons.arrow_back),
                          ),
                          Expanded(
                            child: Focus(
                              onFocusChange: (f) {
                                if (!f && targetCtrl.text.isNotEmpty && sourceCtrl.text.isNotEmpty) {
                                  mappings[targetCtrl.text] = sourceCtrl.text;
                                  stepDef['input_mappings'] = mappings;
                                }
                              },
                              child: TextField(
                                controller: sourceCtrl,
                                decoration: const InputDecoration(
                                  labelText: 'Source Value (e.g. \\$inputs.x)',
                                  isDense: true,
                                ),
                              ),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.remove_circle, color: Colors.red),
                            onPressed: () {
                              setState(() {
                                mappings.remove(m.key);
                                stepDef['input_mappings'] = mappings;
                              });
                            },
                          ),
                        ],
                      ),
                    );
                  }),
                  TextButton.icon(
                    onPressed: () {
                      setState(() {
                        mappings['new_input_key_${mappings.length}'] = '\\$inputs.';
                        stepDef['input_mappings'] = mappings;
                      });
                    },
                    icon: const Icon(Icons.add_link),
                    label: const Text('Add Mapping'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
"""

    pos = new_content.rfind("}")
    if pos != -1:
        new_content = new_content[:pos] + step_card_code + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("Patched workflow_builder_view.dart successfully!")

if __name__ == "__main__":
    main()
