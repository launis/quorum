import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../../../utils/safe_cast.dart';
import '../../../../../l10n/gen/app_localizations.dart';
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
    final l10n = AppLocalizations.of(context)!;
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
                    decoration: InputDecoration(
                      labelText: l10n.studioWorkflowIdOpaque,
                      prefixIcon: const Icon(Icons.fingerprint),
                    ),
                    readOnly: true, // Opaque Stripe ID mandate
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: slugController,
                    decoration: InputDecoration(
                      labelText: l10n.studioWorkflowSlugSemantic,
                      prefixIcon: const Icon(Icons.link),
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
                    Text(
                      l10n.studioWorkflowIdentity,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    I18nTextField(
                      label: l10n.studioWorkflowNameLabel,
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
                      decoration: InputDecoration(
                        labelText: l10n.studioWorkflowDescEnLabel,
                        border: const OutlineInputBorder(),
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
                      decoration: InputDecoration(
                        labelText: l10n.studioWorkflowDescFiLabel,
                        border: const OutlineInputBorder(),
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
                    Text(
                      l10n.studioWorkflowGlobalSettings,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
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
                          decoration: InputDecoration(
                            labelText: l10n.studioWorkflowDefaultProfile,
                            border: const OutlineInputBorder(),
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
