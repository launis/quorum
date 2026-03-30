import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// **Profile Editor View**
///
/// Admin UI for defining strictly-typed Output Profiles for a specific Workflow.
class ProfileEditorView extends HookConsumerWidget {
  final String workflowSlug;

  const ProfileEditorView({super.key, required this.workflowSlug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(workflowFormProvider(workflowSlug));

    return formState.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l10n.editProfilesTitle(workflowSlug))),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
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
    AsyncValue<Workflow> formState,
    Workflow payload,
  ) {
    // Inject initial default if entirely missing
    useMemoized(() {
      if (payload.outputProfiles.isEmpty) {
        Future.microtask(() {
          final newProfiles = Map<String, EmbeddedOutputProfile>.from(
            payload.outputProfiles,
          );
          newProfiles['default'] = const EmbeddedOutputProfile(
            name: I18nText(
              defaultLocale: 'en',
              translations: {'fi': 'Oletusraportti', 'en': 'Default Report'},
            ),
            layouts: [
              OutputLayoutBlock(
                presetView: '1d_metrics',
                title: I18nText(defaultLocale: 'en'),
                showText: true,
                targetBlocks: [],
              ),
            ],
          );
          ref
              .read(workflowFormProvider(workflowSlug).notifier)
              .forceRebuild(payload.copyWith(outputProfiles: newProfiles));
        });
      }
    });

    Future<void> saveWorkflow() async {
      try {
        if (payload.id.isEmpty) throw Exception("Workflow ID is missing");

        await ref
            .read(workflowFormProvider(workflowSlug).notifier)
            .submit(payload);

        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.studioSaveButton),
              backgroundColor: const Color(0xFF2E7D32),
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (!context.mounted) return;
        ref
            .read(loggerServiceProvider)
            .error('Studio', 'Failed to save user profile: $e', e);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.saveFailedError(e.toString())),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }

    void addProfileDialog() {
      String newId = '';
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
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
                if (newId.isEmpty ||
                    payload.outputProfiles.containsKey(newId)) {
                  return;
                }

                final newProfiles = Map<String, EmbeddedOutputProfile>.from(
                  payload.outputProfiles,
                );
                newProfiles[newId] = const EmbeddedOutputProfile(
                  name: I18nText(
                    defaultLocale: 'en',
                    translations: {'fi': 'Uusi profiili', 'en': 'New Profile'},
                  ),
                  layouts: [],
                );

                ref
                    .read(workflowFormProvider(workflowSlug).notifier)
                    .forceRebuild(
                      payload.copyWith(outputProfiles: newProfiles),
                    );

                Navigator.pop(ctx);
              },
              child: Text(l10n.addVariantBtn),
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
            ...payload.outputProfiles.entries.map(
              (entry) => _buildProfileCard(
                context,
                ref,
                l10n,
                payload,
                entry.key,
                entry.value,
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
    Workflow payload,
    String profileId,
    EmbeddedOutputProfile profileDef,
  ) {
    final layouts = List<OutputLayoutBlock>.from(profileDef.layouts);

    void rebuildProfile(EmbeddedOutputProfile updatedProfile) {
      final newProfiles = Map<String, EmbeddedOutputProfile>.from(
        payload.outputProfiles,
      );
      newProfiles[profileId] = updatedProfile;
      ref
          .read(workflowFormProvider(workflowSlug).notifier)
          .forceRebuild(payload.copyWith(outputProfiles: newProfiles));
    }

    void addLayout() {
      layouts.add(
        const OutputLayoutBlock(
          presetView: '1d_metrics',
          title: I18nText(defaultLocale: 'en'),
          showText: true,
          targetBlocks: [],
        ),
      );
      rebuildProfile(profileDef.copyWith(layouts: layouts));
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 24.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Theme.of(context).colorScheme.outline),
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
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
                IconButton(
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: () {
                    final newProfiles = Map<String, EmbeddedOutputProfile>.from(
                      payload.outputProfiles,
                    );
                    newProfiles.remove(profileId);
                    ref
                        .read(workflowFormProvider(workflowSlug).notifier)
                        .forceRebuild(
                          payload.copyWith(outputProfiles: newProfiles),
                        );
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            I18nTextField(
              label: l10n.profileDisplayNameLabel,
              initialData: profileDef.name,
              onChanged: (val) {
                rebuildProfile(profileDef.copyWith(name: val));
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
                  final layout = layouts[index];
                  return _buildLayoutEditor(
                    context,
                    ref,
                    l10n,
                    payload,
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
    Workflow payload,
    String profileId,
    EmbeddedOutputProfile profileDef,
    List<OutputLayoutBlock> parentLayoutsList,
    int index,
    OutputLayoutBlock layout,
  ) {
    final blocksList = List<String>.from(layout.targetBlocks);

    String currentPreset = layout.presetView;
    if (![
      '1d_metrics',
      '2d_compare',
      '3d_complex',
      'text_only',
      'default',
    ].contains(currentPreset)) {
      currentPreset = '1d_metrics';
    }
    final bool showText = layout.showText;

    void rebuildLayout(OutputLayoutBlock updatedLayout) {
      parentLayoutsList[index] = updatedLayout;
      final newProfiles = Map<String, EmbeddedOutputProfile>.from(
        payload.outputProfiles,
      );
      newProfiles[profileId] = profileDef.copyWith(layouts: parentLayoutsList);
      ref
          .read(workflowFormProvider(workflowSlug).notifier)
          .forceRebuild(payload.copyWith(outputProfiles: newProfiles));
    }

    void updateCoords(String val, int idx) {
      while (blocksList.length <= idx) {
        blocksList.add('');
      }
      blocksList[idx] = val;
      rebuildLayout(layout.copyWith(targetBlocks: blocksList));
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
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
                      rebuildLayout(layout.copyWith(presetView: val));
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
                      rebuildLayout(layout.copyWith(showText: val));
                    },
                  ),
                ],
              ),
              IconButton(
                icon: Icon(
                  Icons.delete_outline,
                  color: Theme.of(context).colorScheme.error,
                ),
                onPressed: () {
                  parentLayoutsList.removeAt(index);
                  final newProfiles = Map<String, EmbeddedOutputProfile>.from(
                    payload.outputProfiles,
                  );
                  newProfiles[profileId] = profileDef.copyWith(
                    layouts: parentLayoutsList,
                  );
                  ref
                      .read(workflowFormProvider(workflowSlug).notifier)
                      .forceRebuild(
                        payload.copyWith(outputProfiles: newProfiles),
                      );
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: l10n.sectionTitleLabel,
            initialData: layout.title ?? const I18nText(defaultLocale: 'en'),
            onChanged: (val) {
              rebuildLayout(layout.copyWith(title: val));
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
