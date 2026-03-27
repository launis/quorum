import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

/// **Profile Editor View**
///
/// Admin UI for defining strictly-typed Output Profiles for a specific Workflow.
/// Follows De-Generator Protocol by operating strictly on Map<String, dynamic>.
class ProfileEditorView extends HookConsumerWidget {
  final String workflowSlug;

  const ProfileEditorView({super.key, required this.workflowSlug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(workflowFormProvider(workflowSlug));

    return formState.when(
      loading:
          () => Scaffold(
            appBar: AppBar(title: Text(l10n.editProfilesTitle(workflowSlug))),
            body: const Center(child: CircularProgressIndicator()),
          ),
      error:
          (e, st) => Scaffold(
            appBar: AppBar(title: Text(l10n.editProfilesTitle(workflowSlug))),
            body: ErrorView(
              error: e,
              stackTrace: st,
              compact: false,
              onRetry: () => ref.invalidate(workflowFormProvider(workflowSlug)),
            ),
          ),
      data: (payload) {
        return _buildScaffold(context, ref, l10n, formState, payload);
      },
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
  ) {
    // Profiles Dictionary
    final rawProfiles = payload['output_profiles'];
    final profiles = Map<String, dynamic>.from(SafeCast.safeMap(rawProfiles));

    // Inject initial default if entirely missing
    useMemoized(() {
      if (profiles.isEmpty) {
        profiles['default'] = {
          'name': {'fi': 'Oletusraportti', 'en': 'Default Report'},
          'layouts': [
            {
              'preset_view': '1d_metrics',
              'show_text': true,
              'target_blocks': <String>[],
            },
          ],
        };
        payload['output_profiles'] = profiles;
        ref.read(workflowFormProvider(workflowSlug).notifier).forceRebuild();
      }
    });

    Future<void> saveWorkflow() async {
      try {
        final String idToSave = SafeCast.safeString(payload['id']);
        if (idToSave.isEmpty) throw Exception("Workflow ID is missing");

        payload['output_profiles'] = profiles;

        await ref
            .read(workflowFormProvider(workflowSlug).notifier)
            .submit(payload);

        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.studioSaveButton),
              backgroundColor: Colors.green,
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.saveFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    void addProfileDialog() {
      String newId = '';
      showDialog(
        context: context,
        builder:
            (ctx) => AlertDialog(
              title: Text(l10n.newProfileIdTitle),
              content: TextField(
                decoration: InputDecoration(labelText: l10n.profileIdHint),
                onChanged: (val) => newId = val.trim(),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: Text(l10n.cancelButton),
                ),
                FilledButton(
                  onPressed: () {
                    if (newId.isEmpty || profiles.containsKey(newId)) return;

                    profiles[newId] = {
                      'name': {'fi': 'Uusi profiili', 'en': 'New Profile'},
                      'layouts': [],
                    };
                    payload['output_profiles'] = profiles;
                    ref
                        .read(workflowFormProvider(workflowSlug).notifier)
                        .forceRebuild();

                    Navigator.pop(ctx);
                  },
                  child: const Text('Add'),
                ),
              ],
            ),
      );
    }

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.editProfilesTitle(workflowSlug)),
          actions: [
            if (formState.isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: Center(
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              )
            else
              TextButton.icon(
                onPressed: saveWorkflow,
                icon: const Icon(Icons.save),
                label: Text(l10n.studioSaveButton),
              ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.outputProfilesDictionary,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                FilledButton.icon(
                  onPressed: addProfileDialog,
                  icon: const Icon(Icons.add),
                  label: Text(l10n.addVariantBtn),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...profiles.entries.map(
              (entry) => _buildProfileCard(
                context,
                ref,
                l10n,
                payload,
                profiles,
                entry.key,
                SafeCast.safeMap(entry.value),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
    Map<String, dynamic> profilesMap,
    String profileId,
    Map<String, dynamic> profileDef,
  ) {
    final layouts = SafeCast.safeList(profileDef['layouts']);

    void addLayout() {
      layouts.add({
        'preset_view': '1d_metrics',
        'show_text': true,
        'target_blocks': <String>[],
      });
      profileDef['layouts'] = layouts;
      profilesMap[profileId] = profileDef;
      payload['output_profiles'] = profilesMap;
      ref.read(workflowFormProvider(workflowSlug).notifier).forceRebuild();
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 24.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.variantIdLabel(profileId),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: Colors.blueGrey,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () {
                    profilesMap.remove(profileId);
                    payload['output_profiles'] = profilesMap;
                    ref
                        .read(workflowFormProvider(workflowSlug).notifier)
                        .forceRebuild();
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            I18nTextField(
              label: l10n.profileDisplayNameLabel,
              initialData: SafeCast.safeMap(profileDef['name']),
              onChanged: (val) {
                profileDef['name'] = val;
                profilesMap[profileId] = profileDef;
                payload['output_profiles'] = profilesMap;
                ref
                    .read(workflowFormProvider(workflowSlug).notifier)
                    .forceRebuild();
              },
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.reportLayoutSequenceLabel,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: addLayout,
                  icon: const Icon(Icons.add_box),
                  label: Text(l10n.addLayoutBlockBtn),
                ),
              ],
            ),
            const Divider(),
            if (layouts.isEmpty)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(l10n.noLayoutBlocksDefined),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: layouts.length,
                itemBuilder: (context, index) {
                  final layout = SafeCast.safeMap(layouts[index]);
                  return _buildLayoutEditor(
                    context,
                    ref,
                    l10n,
                    payload,
                    profilesMap,
                    profileId,
                    profileDef,
                    layouts,
                    index,
                    layout,
                  );
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildLayoutEditor(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
    Map<String, dynamic> profilesMap,
    String profileId,
    Map<String, dynamic> profileDef,
    List<dynamic> parentLayoutsList,
    int index,
    Map<String, dynamic> layout,
  ) {
    final blocksList =
        SafeCast.safeList(
          layout['target_blocks'],
        ).map((e) => e.toString()).toList();

    String currentPreset = SafeCast.safeString(
      layout['preset_view'],
      '1d_metrics',
    );
    if (![
      '1d_metrics',
      '2d_compare',
      '3d_complex',
      'text_only',
      'default',
    ].contains(currentPreset)) {
      currentPreset = '1d_metrics';
    }
    final bool showText = layout['show_text'] as bool? ?? true;

    void rebuild() {
      parentLayoutsList[index] = layout;
      profileDef['layouts'] = parentLayoutsList;
      profilesMap[profileId] = profileDef;
      payload['output_profiles'] = profilesMap;
      ref.read(workflowFormProvider(workflowSlug).notifier).forceRebuild();
    }

    void updateCoords(String val, int idx) {
      while (blocksList.length <= idx) blocksList.add('');
      blocksList[idx] = val;
      layout['target_blocks'] = blocksList;
      rebuild();
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 12,
                child: Text(
                  '${index + 1}',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: currentPreset,
                  decoration: InputDecoration(
                    labelText: l10n.presetViewLabel,
                    isDense: true,
                  ),
                  items: [
                    DropdownMenuItem(
                      value: '1d_metrics',
                      child: Text(l10n.preset1dTable),
                    ),
                    DropdownMenuItem(
                      value: '2d_compare',
                      child: Text(l10n.preset2dCompare),
                    ),
                    DropdownMenuItem(
                      value: '3d_complex',
                      child: Text(l10n.preset3dComplex),
                    ),
                    DropdownMenuItem(
                      value: 'text_only',
                      child: Text(l10n.presetTextOnly),
                    ),
                    DropdownMenuItem(
                      value: 'default',
                      child: Text(l10n.presetDefaultView),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      layout['preset_view'] = val;
                      rebuild();
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Row(
                children: [
                  Text(l10n.showTextLabel),
                  Switch(
                    value: showText,
                    onChanged: (val) {
                      layout['show_text'] = val;
                      rebuild();
                    },
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.orange),
                onPressed: () {
                  parentLayoutsList.removeAt(index);
                  profileDef['layouts'] = parentLayoutsList;
                  profilesMap[profileId] = profileDef;
                  payload['output_profiles'] = profilesMap;
                  ref
                      .read(workflowFormProvider(workflowSlug).notifier)
                      .forceRebuild();
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: l10n.sectionTitleLabel,
            initialData: SafeCast.safeMap(layout['title']),
            onChanged: (val) {
              layout['title'] = val;
              rebuild();
            },
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: l10n.sectionDescLabel,
            initialData: SafeCast.safeMap(layout['description']),
            onChanged: (val) {
              layout['description'] = val;
              rebuild();
            },
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  initialValue: blocksList.isNotEmpty ? blocksList[0] : '',
                  decoration: InputDecoration(
                    labelText: l10n.xAxisLabel,
                    isDense: true,
                  ),
                  onChanged: (val) => updateCoords(val.trim(), 0),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  initialValue: blocksList.length > 1 ? blocksList[1] : '',
                  decoration: InputDecoration(
                    labelText: l10n.yAxisLabel,
                    isDense: true,
                  ),
                  onChanged: (val) => updateCoords(val.trim(), 1),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  initialValue: blocksList.length > 2 ? blocksList[2] : '',
                  decoration: InputDecoration(
                    labelText: l10n.zAxisLabel,
                    isDense: true,
                  ),
                  onChanged: (val) => updateCoords(val.trim(), 2),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
