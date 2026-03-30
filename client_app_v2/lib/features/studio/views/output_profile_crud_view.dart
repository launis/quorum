import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Admin Studio View for managing Output Profiles.
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class OutputProfileCrudView extends HookConsumerWidget {
  final String id;
  const OutputProfileCrudView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());

    // UI transient hook state
    final idController = useTextEditingController();
    final slugController = useTextEditingController();
    final workflowIdController = useTextEditingController();

    // Data Dependencies
    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);
    final formState = ref.watch(outputProfileFormProvider(id));

    return formState.when(
      loading: () => Scaffold(
        appBar: AppBar(
          title: Text(
            id == 'new'
                ? l10n.newOutputProfileTitle
                : l10n.editOutputProfileTitle,
          ),
        ),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
        appBar: AppBar(
          title: Text(
            id == 'new'
                ? l10n.newOutputProfileTitle
                : l10n.editOutputProfileTitle,
          ),
        ),
        body: ErrorView(
          error: e,
          stackTrace: st,
          compact: false,
          onRetry: () => ref.invalidate(outputProfileFormProvider(id)),
        ),
      ),
      data: (payload) {
        // Hydrate transient hooks on first build safely
        useMemoized(() {
          idController.text = payload['id']?.toString() ?? '';
          slugController.text = payload['slug']?.toString() ?? '';
          workflowIdController.text = payload['workflow_id']?.toString() ?? '';
        });

        return _buildScaffold(
          context,
          ref,
          l10n,
          formKey,
          formState,
          payload,
          idController,
          slugController,
          workflowIdController,
          promptBlocksState,
          workflowsState,
          stepsState,
        );
      },
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
    TextEditingController idController,
    TextEditingController slugController,
    TextEditingController workflowIdController,
    AsyncValue<List<dynamic>> promptBlocksState,
    AsyncValue<List<dynamic>> workflowsState,
    AsyncValue<List<dynamic>> stepsState,
  ) {
    final layouts = SafeCast.safeList(payload['layouts']);

    Future<void> saveProfile() async {
      if (!formKey.currentState!.validate()) return;

      try {
        final String idToSave = idController.text.trim();
        if (idToSave.isEmpty)
          throw Exception(l10n.studioViewsProfileIdRequired);

        payload['id'] = idToSave;
        payload['slug'] = slugController.text.trim().isNotEmpty
            ? slugController.text.trim()
            : idToSave;
        payload['workflow_id'] = workflowIdController.text.trim();
        payload['layouts'] = layouts;

        final notifier = ref.read(outputProfileFormProvider(id).notifier);
        await notifier.submit(payload);

        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.profileSavedSuccess),
            backgroundColor: const Color(0xFF2E7D32),
          ),
        );
        context.pop(); // GoRouter
      } catch (e) {
        if (!context.mounted) return;
        ref
            .read(loggerServiceProvider)
            .error('Studio', 'Failed to save profile: $e', e);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.saveFailedError(e.toString())),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }

    Future<void> deleteProfile() async {
      final String idToDelete = payload['id']?.toString() ?? '';
      if (idToDelete.isEmpty || id == 'new') return;

      final nameMap = SafeCast.safeMap(payload['name']);
      final translations = SafeCast.safeMap(nameMap['translations']);
      final nameToDisplay = translations['fi']?.toString() ?? translations['en']?.toString() ?? idToDelete;

      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.deleteProfileTitle),
          content: Text(l10n.deleteProfileConfirmation(nameToDisplay)),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(l10n.cancelButton),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: Text(l10n.deleteButton),
            ),
          ],
        ),
      );

      if (confirm == true) {
        try {
          await ref
              .read(outputProfilesControllerProvider.notifier)
              .deleteProfile(idToDelete);
          if (context.mounted) context.pop();
        } catch (e) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete profile: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.deleteFailedError(e.toString()))),
          );
        }
      }
    }

    void addLayout() {
      layouts.add({
        'layout_type': 'box_1d',
        'title': {
          'default_locale': 'en',
          'translations': <String, dynamic>{'en': 'New Layout Block'},
        },
        'show_text': true,
        'components': <String>[],
      });
      ref.read(outputProfileFormProvider(id).notifier).forceRebuild();
    }

    final String selectedWorkflowId = workflowIdController.text;
    Set<String> allowedBlockIds = {};

    if (selectedWorkflowId.isNotEmpty &&
        workflowsState.hasValue &&
        stepsState.hasValue) {
      final workflows = workflowsState.value!;
      final steps = stepsState.value!;

      final workflow = workflows.cast<Map<String, dynamic>?>().firstWhere(
        (w) => w != null && w['id']?.toString() == selectedWorkflowId,
        orElse: () => null,
      );

      if (workflow != null) {
        final stepRules = SafeCast.safeList(workflow['steps']);
        final taskBlueprintIds = stepRules
            .map((s) => SafeCast.safeMap(s)['task_blueprint']?.toString())
            .where((s) => s != null)
            .cast<String>()
            .toSet();

        for (final step in steps) {
          final stepId = step['id']?.toString() ?? '';
          final stepSlug = step['slug']?.toString() ?? stepId;
          if (taskBlueprintIds.contains(stepId) ||
              taskBlueprintIds.contains(stepSlug)) {
            final promptBlocksRaw = SafeCast.safeList(
              step['prompt_blocks'],
            ).map((b) => b.toString());
            allowedBlockIds.addAll(promptBlocksRaw);
          }
        }
      }
    }

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            id == 'new'
                ? l10n.newOutputProfileTitle
                : l10n.editOutputProfileTitle,
          ),
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
            else ...[
              if (id != 'new')
                IconButton(
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: deleteProfile,
                  tooltip: l10n.deleteProfileTitle,
                ),
              TextButton.icon(
                onPressed: saveProfile,
                icon: const Icon(Icons.save),
                label: Text(l10n.studioSaveButton),
              ),
            ],
          ],
        ),
        body: Form(
          key: formKey,
          child: ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      TextFormField(
                        controller: idController,
                        decoration: InputDecoration(
                          labelText: l10n.profileIdLabel,
                          border: const OutlineInputBorder(),
                        ),
                        enabled: id == 'new', // Cannot change ID after creation
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: slugController,
                        decoration: InputDecoration(
                          labelText: l10n.urlSlugLabel,
                          border: const OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      workflowsState.when(
                        data: (workflows) {
                          String? currentValue =
                              workflowIdController.text.isNotEmpty
                              ? workflowIdController.text
                              : null;

                          final bool hasValidValue =
                              currentValue != null &&
                              (workflows.any(
                                    (w) => w['id']?.toString() == currentValue,
                                  ) ||
                                  currentValue == '');

                          return DropdownButtonFormField<String>(
                            initialValue: hasValidValue ? currentValue : null,
                            decoration: InputDecoration(
                              labelText: l10n.workflowIdBindingLabel,
                              border: const OutlineInputBorder(),
                            ),
                            hint: Text(l10n.selectWorkflowHint),
                            items: [
                              DropdownMenuItem(
                                value: '',
                                child: Text(l10n.noneDefaultLabel),
                              ),
                              ...workflows.map((flow) {
                                final flowId = flow['id']?.toString() ?? '';
                                final labelDict = SafeCast.safeMap(
                                  flow['name'],
                                );
                                final translations = SafeCast.safeMap(
                                  labelDict['translations'],
                                );
                                final localeCode = Localizations.localeOf(
                                  context,
                                ).languageCode;
                                final displayName =
                                    translations[localeCode] ??
                                    translations['fi'] ??
                                    translations['en'] ??
                                    flowId;

                                return DropdownMenuItem(
                                  value: flowId,
                                  child: Text('$displayName ($flowId)'),
                                );
                              }),
                            ],
                            onChanged: (val) {
                              if (val != null) {
                                workflowIdController.text = val;
                                payload['workflow_id'] = val;
                                ref
                                    .read(
                                      outputProfileFormProvider(id).notifier,
                                    )
                                    .forceRebuild();
                              }
                            },
                          );
                        },
                        loading: () =>
                            const Center(child: CircularProgressIndicator()),
                        error: (e, _) => Text(
                          l10n.studioViewsErrorLoadingWorkflows(e.toString()),
                        ),
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: l10n.profileDisplayNameLabel,
                        initialData: I18nText.fromJson(
                          SafeCast.safeMap(payload['name']),
                        ),
                        onChanged: (val) {
                          payload['name'] = val.toJson();
                          ref
                              .read(outputProfileFormProvider(id).notifier)
                              .forceRebuild();
                        },
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: l10n.profileDescriptionLabel,
                        initialData: I18nText.fromJson(
                          SafeCast.safeMap(payload['description']),
                        ),
                        onChanged: (val) {
                          payload['description'] = val.toJson();
                          ref
                              .read(outputProfileFormProvider(id).notifier)
                              .forceRebuild();
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              if (selectedWorkflowId.isEmpty)
                Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Center(
                    child: Text(
                      l10n.workflowSelectWarning,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                )
              else ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.layoutBlocksTitle,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                    FilledButton.icon(
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
                        index,
                        layout,
                        layouts,
                        promptBlocksState,
                        allowedBlockIds,
                      );
                    },
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLayoutEditor(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    int index,
    Map<String, dynamic> layout,
    List<dynamic> parentLayoutsList,
    AsyncValue<List<dynamic>> promptBlocksState,
    Set<String> allowedBlockIds,
  ) {
    final blocksList = SafeCast.safeList(
      layout['components'],
    ).map((e) => e.toString()).toList();

    String currentPreset = SafeCast.safeString(
      layout['layout_type'] ?? layout['preset_view'],
      'box_1d',
    );
    if (![
      'box_1d',
      'matrix_2d',
      'radar_3d',
      'text_only',
      'automatic',
    ].contains(currentPreset)) {
      currentPreset = 'box_1d';
    }

    final bool showText = layout['show_text'] as bool? ?? true;

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
                      value: 'box_1d',
                      child: Text(l10n.preset1dTable),
                    ),
                    DropdownMenuItem(
                      value: 'matrix_2d',
                      child: Text(l10n.preset2dGrid),
                    ),
                    DropdownMenuItem(
                      value: 'radar_3d',
                      child: Text(l10n.preset3dRadar),
                    ),
                    DropdownMenuItem(
                      value: 'text_only',
                      child: Text(l10n.presetTextOnly),
                    ),
                    DropdownMenuItem(
                      value: 'automatic',
                      child: Text(l10n.presetAutomatic),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      layout['layout_type'] = val;
                      layout.remove('preset_view');
                      ref
                          .read(outputProfileFormProvider(id).notifier)
                          .forceRebuild();
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
                      ref
                          .read(outputProfileFormProvider(id).notifier)
                          .forceRebuild();
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
                  ref
                      .read(outputProfileFormProvider(id).notifier)
                      .forceRebuild();
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: l10n.layoutBlockTitleLabel,
            initialData: I18nText.fromJson(SafeCast.safeMap(layout['title'])),
            onChanged: (val) {
              layout['title'] = val.toJson();
              ref.read(outputProfileFormProvider(id).notifier).forceRebuild();
            },
          ),
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              l10n.targetComponentsTitle,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),
          const SizedBox(height: 8),
          promptBlocksState.when(
            data: (blocks) {
              final targetBlocks = blocks.cast<Map<String, dynamic>>().where((
                b,
              ) {
                final bId = b['id']?.toString() ?? '';
                final bSlug = b['slug']?.toString() ?? bId;
                final isAllowed =
                    allowedBlockIds.contains(bId) ||
                    allowedBlockIds.contains(bSlug);
                if (!isAllowed) return false;

                final isMatrix = b['category_id']?.toString() == 'matrix';
                final extensions = SafeCast.safeList(b['output_extensions']);
                return isMatrix || extensions.isNotEmpty;
              }).toList();

              final int requiredDropdowns = switch (currentPreset) {
                'box_1d' => 1,
                'matrix_2d' => 2,
                'radar_3d' => 3,
                _ => 1,
              };

              final List<Widget> dropdowns = [];
              for (int i = 0; i < requiredDropdowns; i++) {
                String? selectedValue;
                if (i < blocksList.length) {
                  final val = blocksList[i];
                  if (val == '*' ||
                      targetBlocks.any((b) => b['id'].toString() == val)) {
                    selectedValue = val;
                  }
                }

                final String axisLabel = switch (i) {
                  0 => l10n.componentXAxisLabel,
                  1 => l10n.componentYAxisLabel,
                  2 => l10n.componentZAxisLabel,
                  _ => l10n.componentGenericLabel('${i + 1}'),
                };

                dropdowns.add(
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: DropdownButtonFormField<String>(
                      initialValue: selectedValue,
                      decoration: InputDecoration(
                        labelText: axisLabel,
                        isDense: true,
                        border: const OutlineInputBorder(),
                      ),
                      hint: Text(l10n.selectComponentHint),
                      items: [
                        DropdownMenuItem(
                          value: '*',
                          child: Text(l10n.selectAllComponentsLabel),
                        ),
                        ...targetBlocks.map((block) {
                          final blockId = block['id']?.toString() ?? '';
                          final labelDict = SafeCast.safeMap(block['label']);
                          final translations = SafeCast.safeMap(
                            labelDict['translations'],
                          );
                          final localeCode = Localizations.localeOf(
                            context,
                          ).languageCode;
                          final blockName =
                              translations[localeCode] ??
                              translations['fi'] ??
                              translations['en'] ??
                              blockId;

                          return DropdownMenuItem(
                            value: blockId,
                            child: Text(blockName),
                          );
                        }),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          while (blocksList.length <= i) {
                            blocksList.add('');
                          }
                          blocksList[i] = val;
                          layout['components'] = blocksList
                              .where((b) => b.isNotEmpty)
                              .toList();
                          ref
                              .read(outputProfileFormProvider(id).notifier)
                              .forceRebuild();
                        }
                      },
                    ),
                  ),
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: dropdowns,
              );
            },
            loading: () => const Align(
              alignment: Alignment.centerLeft,
              child: CircularProgressIndicator(),
            ),
            error: (e, _) =>
                Text(l10n.studioViewsErrorLoadingBlocks(e.toString())),
          ),
        ],
      ),
    );
  }
}
