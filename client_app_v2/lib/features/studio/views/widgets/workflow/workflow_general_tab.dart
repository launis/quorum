import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import '../../../../../utils/safe_cast.dart';
import '../i18n_text_field.dart';

/// **WorkflowGeneralTab**
///
/// Componentized UI widget representing Tab 1 of the Workflow Builder.
/// Handles high-level metadata and the default output profile routing.
class WorkflowGeneralTab extends ConsumerWidget {
  final Map<String, dynamic> workflow;
  final TextEditingController idController;
  final TextEditingController slugController;
  final VoidCallback onChanged;

  const WorkflowGeneralTab({
    super.key,
    required this.workflow,
    required this.idController,
    required this.slugController,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final descriptionMap = SafeCast.safeMap(workflow['description']);
    final descTranslations = SafeCast.safeMap(descriptionMap['translations']);

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: idController,
                    decoration: const InputDecoration(
                      labelText: 'Opaque Workflow ID (System Generated)',
                      prefixIcon: Icon(Icons.fingerprint),
                    ),
                    readOnly: true, // Opaque Stripe ID mandate
                    style: const TextStyle(color: Colors.grey),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: slugController,
                    decoration: const InputDecoration(
                      labelText: 'Semantic Routing Slug (e.g. audit-master)',
                      prefixIcon: Icon(Icons.link),
                    ),
                    onChanged: (val) {
                      workflow['slug'] = val;
                      onChanged();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      'Workflow Identity',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    I18nTextField(
                      label: 'Workflow Name',
                      initialData: SafeCast.safeMap(workflow['name']),
                      onChanged: (val) {
                        workflow['name'] = val;
                        onChanged();
                      },
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: TextEditingController(
                        text: SafeCast.safeString(descTranslations['en']),
                      ),
                      maxLines: 2,
                      decoration: const InputDecoration(
                        labelText: 'Description (EN)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        descTranslations['en'] = val;
                        descriptionMap['translations'] = descTranslations;
                        workflow['description'] = descriptionMap;
                        onChanged();
                      },
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: TextEditingController(
                        text: SafeCast.safeString(descTranslations['fi']),
                      ),
                      maxLines: 2,
                      decoration: const InputDecoration(
                        labelText: 'Kuvaus (FI)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        descTranslations['fi'] = val;
                        descriptionMap['translations'] = descTranslations;
                        workflow['description'] = descriptionMap;
                        onChanged();
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Global Execution Settings',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Builder(
                      builder: (context) {
                        final configsAsync = ref.watch(
                          modelRegistryControllerProvider,
                        );
                        if (configsAsync.isLoading) {
                          return const Center(
                            child: CircularProgressIndicator(),
                          );
                        }
                        if (configsAsync.hasError) {
                          return Text('Error: ${configsAsync.error}');
                        }

                        final configs = configsAsync.value ?? [];
                        final registryConfig = configs.firstWhere(
                          (c) => c['type'] == 'model_registry',
                          orElse: () => <String, dynamic>{},
                        );

                        final modelsObj = SafeCast.safeMap(
                          registryConfig['models'],
                        );
                        final modelKeys = modelsObj.keys.toList();

                        if (modelKeys.isEmpty) {
                          return const Text(
                            'Warning: No models found.',
                            style: TextStyle(color: Colors.red),
                          );
                        }

                        final currentStrategy = SafeCast.safeString(
                          workflow['model_strategy'],
                        );
                        final safeValue =
                            modelKeys.contains(currentStrategy)
                                ? currentStrategy
                                : null;

                        return DropdownButtonFormField<String>(
                          key: ValueKey(modelKeys.length),
                          initialValue: safeValue,
                          decoration: const InputDecoration(
                            labelText:
                                'Model Strategy (Cost/Cognition Profile)',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          items:
                              modelKeys.map((key) {
                                final modelData = SafeCast.safeMap(
                                  modelsObj[key],
                                );
                                final label =
                                    modelData['model_name'] != null
                                        ? '${key.toUpperCase()} (${modelData['model_name']})'
                                        : key.toUpperCase();
                                return DropdownMenuItem(
                                  value: key,
                                  child: Text(label),
                                );
                              }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              workflow['model_strategy'] = val;
                              onChanged();
                            }
                          },
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                    Builder(
                      builder: (context) {
                        final outputProfiles = SafeCast.safeMap(
                          workflow['output_profiles'],
                        );
                        final profileKeys = outputProfiles.keys.toList();
                        if (profileKeys.isEmpty) profileKeys.add('default');

                        final currentDefault = SafeCast.safeString(
                          workflow['default_profile_id'],
                          'default',
                        );
                        final safeDefault =
                            profileKeys.contains(currentDefault)
                                ? currentDefault
                                : profileKeys.first;

                        return DropdownButtonFormField<String>(
                          key: ValueKey(profileKeys.join(':')),
                          initialValue: safeDefault,
                          decoration: const InputDecoration(
                            labelText: 'Default Fallback Profile',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          items:
                              profileKeys.map((key) {
                                final profileData = SafeCast.safeMap(
                                  outputProfiles[key],
                                );
                                final profNameMap = SafeCast.safeMap(
                                  profileData['name'],
                                );
                                final title =
                                    profNameMap['fi'] ??
                                    profNameMap['en'] ??
                                    key;
                                return DropdownMenuItem(
                                  value: key,
                                  child: Text('$title ($key)'),
                                );
                              }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              workflow['default_profile_id'] = val;
                              onChanged();
                            }
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
