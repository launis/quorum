import sys

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\workflow\workflow_general_tab.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Imports
    imports = """import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import '../../../../../utils/safe_cast.dart';
import '../i18n_text_field.dart';"""

    content = content.replace(
        "import 'package:flutter/material.dart';\nimport '../../../../../utils/safe_cast.dart';",
        imports
    )

    # Class signature
    content = content.replace(
        "class WorkflowGeneralTab extends StatelessWidget {",
        "class WorkflowGeneralTab extends ConsumerWidget {"
    )
    
    # Build signature
    content = content.replace(
        "Widget build(BuildContext context) {",
        "Widget build(BuildContext context, WidgetRef ref) {"
    )

    # Replace the Model Strategy Hardcoded dropdown with the real Dynamic Registry Logic
    old_model_strategy = """                    DropdownButtonFormField<String>(
                      initialValue: SafeCast.safeString(
                        workflow['model_strategy'],
                        'deep', // default
                      ),
                      decoration: const InputDecoration(
                        labelText: 'LLM Model Strategy',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'deep',
                          child: Text('Deep & Analytical (O1 / Opus)'),
                        ),
                        DropdownMenuItem(
                          value: 'fast',
                          child: Text('Fast & Tactical (Haiku / 4o-mini)'),
                        ),
                        DropdownMenuItem(
                          value: 'strict',
                          child: Text('Strict Execution (Sonnet 3.5)'),
                        ),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          workflow['model_strategy'] = val;
                          onChanged();
                        }
                      },
                    ),"""
    
    new_model_strategy = """                    Builder(
                      builder: (context) {
                        final configsAsync = ref.watch(modelRegistryControllerProvider);
                        if (configsAsync.isLoading) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (configsAsync.hasError) {
                          return Text('Error: ${configsAsync.error}');
                        }

                        final configs = configsAsync.value ?? [];
                        final registryConfig = configs.firstWhere(
                          (c) => c['type'] == 'model_registry',
                          orElse: () => <String, dynamic>{},
                        );

                        final modelsObj = SafeCast.safeMap(registryConfig['models']);
                        final modelKeys = modelsObj.keys.toList();

                        if (modelKeys.isEmpty) {
                          return const Text('Warning: No models found.', style: TextStyle(color: Colors.red));
                        }

                        final currentStrategy = SafeCast.safeString(workflow['model_strategy']);
                        final safeValue = modelKeys.contains(currentStrategy) ? currentStrategy : null;

                        return DropdownButtonFormField<String>(
                          key: ValueKey(modelKeys.length),
                          initialValue: safeValue,
                          decoration: const InputDecoration(
                            labelText: 'Model Strategy (Cost/Cognition Profile)',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: modelKeys.map((key) {
                            final modelData = SafeCast.safeMap(modelsObj[key]);
                            final label = modelData['model_name'] != null
                                ? '${key.toUpperCase()} (${modelData['model_name']})'
                                : key.toUpperCase();
                            return DropdownMenuItem(value: key, child: Text(label));
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              workflow['model_strategy'] = val;
                              onChanged();
                            }
                          },
                        );
                      },
                    ),"""

    content = content.replace(old_model_strategy, new_model_strategy)

    # Also, we forgot to use I18nTextField for Name
    old_name = """                    TextField(
                      controller: TextEditingController(
                        text: SafeCast.safeString(translations['en']),
                      ),
                      decoration: const InputDecoration(
                        labelText: 'Name (EN)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        translations['en'] = val;
                        nameMap['translations'] = translations;
                        workflow['name'] = nameMap;
                        onChanged();
                      },
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: TextEditingController(
                        text: SafeCast.safeString(translations['fi']),
                      ),
                      decoration: const InputDecoration(
                        labelText: 'Nimi (FI)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        translations['fi'] = val;
                        nameMap['translations'] = translations;
                        workflow['name'] = nameMap;
                        onChanged();
                      },
                    ),"""
                    
    new_name = """                    I18nTextField(
                      label: 'Workflow Name',
                      initialData: SafeCast.safeMap(workflow['name']),
                      onChanged: (val) {
                        workflow['name'] = val;
                        onChanged();
                      },
                    ),"""
                    
    content = content.replace(old_name, new_name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Patched General Tab.")

if __name__ == "__main__":
    main()
