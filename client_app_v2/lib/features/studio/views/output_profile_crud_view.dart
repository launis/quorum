import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';

import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/profile/synthesis_editor_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/models/enums.dart';

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
    final enableThreePaneLayout = useState(true);

    // Data Dependencies
    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);
    final formState = ref.watch(outputProfileFormProvider(id));

    return formState.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l10n.editOutputProfileTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
        appBar: AppBar(title: Text(l10n.editOutputProfileTitle)),
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
          idController.text = payload.id;
          slugController.text = payload.slug;
          workflowIdController.text = payload.workflowId;
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
          enableThreePaneLayout,
        );
      },
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<OutputProfile> formState,
    OutputProfile payload,
    TextEditingController idController,
    TextEditingController slugController,
    TextEditingController workflowIdController,
    AsyncValue<List<dynamic>> promptBlocksState,
    AsyncValue<List<dynamic>> workflowsState,
    AsyncValue<List<dynamic>> stepsState,
    ValueNotifier<bool> enableThreePaneLayout,
  ) {
    var layouts = List<OutputLayoutBlock>.from(payload.layouts);

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    Future<void> saveProfile() async {
      if (!formKey.currentState!.validate()) return;

      try {
        final String idToSave = idController.text.trim();
        if (idToSave.isEmpty) {
          throw Exception(l10n.studioViewsProfileIdRequired);
        }

        final newPayload = payload.copyWith(
          id: idToSave,
          slug: slugController.text.trim().isNotEmpty
              ? slugController.text.trim()
              : idToSave,
          workflowId: workflowIdController.text.trim(),
          layouts: layouts,
        );

        final notifier = ref.read(outputProfileFormProvider(id).notifier);
        await notifier.submit(newPayload);

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
      final String idToDelete = payload.id;
      if (idToDelete.isEmpty) return;

      final currentLocale = Localizations.localeOf(context).languageCode;
      final nameToDisplay =
          payload.name.translations[currentLocale] ??
          payload.name.translations['en'] ??
          idToDelete;

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

    final String selectedWorkflowId = workflowIdController.text;
    Set<String> allowedBlockIds = {};

    if (selectedWorkflowId.isNotEmpty &&
        workflowsState.hasValue &&
        stepsState.hasValue) {
      final workflows = workflowsState.value!.cast<Workflow>();
      final steps = stepsState.value!.cast<NodeStrategy>();

      final Workflow? workflow = workflows
          .where((w) => w.id == selectedWorkflowId)
          .firstOrNull;

      if (workflow != null) {
        final taskBlueprintIds = workflow.steps
            .map((s) => s.taskBlueprint)
            .toSet();

        for (final step in steps) {
          final stepId = step.id;
          if (taskBlueprintIds.contains(stepId)) {
            allowedBlockIds.addAll(step.promptBlocks);
          }
        }
      }
    }

    Widget buildIdentityPane() {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: idController,
                decoration: InputDecoration(
                  labelText: l10n.profileIdLabel,
                  border: const OutlineInputBorder(),
                ),
                readOnly: true,
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
                data: (rawWorkflows) {
                  final workflows = rawWorkflows.cast<Workflow>();
                  String? currentValue = workflowIdController.text.isNotEmpty
                      ? workflowIdController.text
                      : null;

                  final bool hasValidValue =
                      currentValue != null &&
                      (workflows.any((w) => w.id == currentValue) ||
                          currentValue == '');

                  return DropdownButtonFormField<String>(
                    initialValue: hasValidValue ? currentValue : null,
                    isExpanded: true,
                    decoration: InputDecoration(
                      labelText: l10n.workflowIdBindingLabel,
                      border: const OutlineInputBorder(),
                    ),
                    hint: Text(l10n.selectWorkflowHint),
                    items: [
                      DropdownMenuItem(
                        value: '',
                        child: Text(
                          l10n.noneDefaultLabel,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      ...workflows.map((flow) {
                        final flowId = flow.id;
                        final localeCode = Localizations.localeOf(
                          context,
                        ).languageCode;
                        final displayName = flow.name.get(localeCode);

                        return DropdownMenuItem(
                          value: flowId,
                          child: Text(
                            '$displayName ($flowId)',
                            overflow: TextOverflow.ellipsis,
                          ),
                        );
                      }),
                    ],
                    onChanged: (val) {
                      if (val != null) {
                        workflowIdController.text = val;
                        updatePayload(payload.copyWith(workflowId: val));
                      }
                    },
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) =>
                    Text(l10n.studioViewsErrorLoadingWorkflows(e.toString())),
              ),
              const SizedBox(height: 16),
              I18nTextField(
                label: l10n.profileDisplayNameLabel,
                initialData: payload.name,
                onChanged: (val) {
                  updatePayload(payload.copyWith(name: val));
                },
              ),
              const SizedBox(height: 16),
              I18nTextField(
                label: l10n.profileDescriptionLabel,
                initialData: payload.description,
                onChanged: (val) {
                  final isEmpty =
                      val.translations.isEmpty ||
                      val.translations.values.every((v) => v.trim().isEmpty);
                  updatePayload(
                    payload.copyWith(description: isEmpty ? null : val),
                  );
                },
              ),
              const SizedBox(height: 16),
              I18nTextField(
                label: 'Selite (Rich Text Preface)',
                initialData: payload.customPreface,
                onChanged: (val) {
                  final isEmpty =
                      val.translations.isEmpty ||
                      val.translations.values.every((v) => v.trim().isEmpty);
                  updatePayload(
                    payload.copyWith(customPreface: isEmpty ? null : val),
                  );
                },
              ),
              const SizedBox(height: 16),
              InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.profileDisplayScaleLabel,
                  isDense: true,
                  border: const OutlineInputBorder(),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: payload.displayScale,
                    isDense: true,
                    isExpanded: true,
                    items: [
                      DropdownMenuItem(
                        value: 'original',
                        child: Text(
                          l10n.scaleOriginal,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      DropdownMenuItem(
                        value: 'custom',
                        child: Text(
                          l10n.scaleCustom,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      DropdownMenuItem(
                        value: 'normalized_100',
                        child: Text(
                          l10n.scaleNormalized100,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                    onChanged: (val) {
                      if (val != null) {
                        updatePayload(payload.copyWith(displayScale: val));
                      }
                    },
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Arviointimoottori ja Ankaruustaso',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 8),
              InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.strictnessSelectorTitle,
                  isDense: true,
                  border: const OutlineInputBorder(),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<int?>(
                    value: payload.strictnessLevel,
                    isDense: true,
                    isExpanded: true,
                    items: [
                      DropdownMenuItem<int?>(
                        value: null,
                        child: Text(
                          l10n.noneDefaultLabel,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      ...StrictnessLevel.values.map((lvl) {
                        return DropdownMenuItem<int?>(
                          value: lvl.value,
                          child: Text(switch (lvl) {
                            StrictnessLevel.fullFlexibility =>
                              l10n.strictnessFullFlex,
                            StrictnessLevel.lenient => l10n.strictnessLenient,
                            StrictnessLevel.balanced => l10n.strictnessBalanced,
                            StrictnessLevel.strict => l10n.strictnessStrict,
                            StrictnessLevel.absolute => l10n.strictnessAbsolute,
                          }, overflow: TextOverflow.ellipsis),
                        );
                      }),
                    ],
                    onChanged: (val) {
                      updatePayload(payload.copyWith(strictnessLevel: val));
                    },
                  ),
                ),
              ),
              const SizedBox(height: 16),
              InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.analysisLevelLabel,
                  isDense: true,
                  border: const OutlineInputBorder(),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<ScoringStrategy?>(
                    value: payload.scoringStrategy,
                    isDense: true,
                    isExpanded: true,
                    items: [
                      DropdownMenuItem<ScoringStrategy?>(
                        value: null,
                        child: Text(
                          l10n.noneDefaultLabel,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      ...ScoringStrategy.values.map((strategy) {
                        return DropdownMenuItem<ScoringStrategy?>(
                          value: strategy,
                          child: Text(switch (strategy) {
                            ScoringStrategy.waterfall =>
                              l10n.strategyKoearvostelu,
                            ScoringStrategy.dampening =>
                              l10n.strategySyvaarvostelu,
                            ScoringStrategy.average =>
                              l10n.strategyLineaarinenKeskiarvo,
                            ScoringStrategy.weightedAverage =>
                              l10n.strategyPainotettuKeskiarvo,
                          }, overflow: TextOverflow.ellipsis),
                        );
                      }),
                    ],
                    onChanged: (val) {
                      updatePayload(payload.copyWith(scoringStrategy: val));
                    },
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Kannen metatiedot (Identity Metadata)',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 8),
              ...[
                'date',
                'organization',
                'user',
                'scoring_engine',
                'strictness',
                'cost',
                'tokens',
              ].map((meta) {
                final String title = switch (meta) {
                  'date' => 'Päivämäärä (date)',
                  'organization' => 'Organisaatio (organization)',
                  'user' => 'Käyttäjä (user)',
                  'scoring_engine' => 'Arviointimoottori (scoring_engine)',
                  'strictness' => 'Ankaruustaso (strictness)',
                  'cost' => 'Hinta-arvio (cost)',
                  'tokens' => 'Kognitiivinen työ (tokens)',
                  _ => meta,
                };
                return CheckboxListTile(
                  title: Text(title),
                  value: payload.visibleMetadata.contains(meta),
                  onChanged: (val) {
                    final masterOrder = [
                      'date',
                      'organization',
                      'user',
                      'scoring_engine',
                      'strictness',
                      'cost',
                      'tokens',
                    ];
                    final list = List<String>.from(payload.visibleMetadata);
                    if (val == true) {
                      if (!list.contains(meta)) list.add(meta);
                    } else {
                      list.remove(meta);
                    }
                    // Sort by master order to enforce UI and PDF parity
                    list.sort((a, b) {
                      final indexA = masterOrder.indexOf(a);
                      final indexB = masterOrder.indexOf(b);
                      if (indexA == -1 || indexB == -1) return 0;
                      return indexA.compareTo(indexB);
                    });
                    updatePayload(payload.copyWith(visibleMetadata: list));
                  },
                  controlAffinity: ListTileControlAffinity.leading,
                );
              }),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: payload.maxExtensionItems?.toString() ?? '3',
                decoration: const InputDecoration(
                  labelText: 'Max Extension Items',
                  border: OutlineInputBorder(),
                  helperText:
                      'Maximum number of items to show per XAI extension. 999 for unlimited.',
                ),
                keyboardType: TextInputType.number,
                onChanged: (val) {
                  final parsed = int.tryParse(val);
                  if (parsed != null && parsed >= 1) {
                    updatePayload(payload.copyWith(maxExtensionItems: parsed));
                  }
                },
                validator: (val) {
                  if (val == null || val.isEmpty) return null;
                  final parsed = int.tryParse(val);
                  if (parsed == null || parsed < 1)
                    return 'Given value must be an integer >= 1';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              InputDecorator(
                decoration: const InputDecoration(
                  labelText: 'Visible XAI Extensions',
                  isDense: true,
                  border: OutlineInputBorder(),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: XaiExtensionType.values.map((ext) {
                    return CheckboxListTile(
                      title: Text(ext.name),
                      value: payload.visibleExtensions.contains(ext),
                      onChanged: (val) {
                        final updatedList = List<XaiExtensionType>.from(
                          payload.visibleExtensions,
                        );
                        if (val == true) {
                          updatedList.add(ext);
                        } else {
                          updatedList.remove(ext);
                        }
                        updatePayload(
                          payload.copyWith(visibleExtensions: updatedList),
                        );
                      },
                      controlAffinity: ListTileControlAffinity.leading,
                      dense: true,
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ),
      );
    }

    Widget buildSynthesisPane() {
      return SynthesisEditorCard(
        synthesis: payload.synthesis,
        onChanged: (val) {
          updatePayload(payload.copyWith(synthesis: val));
        },
      );
    }

    Widget buildLayoutPane() {
      if (selectedWorkflowId.isEmpty) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Center(
              child: Text(
                l10n.workflowSelectWarning,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        );
      }
      return LayoutEditorCard(
        layouts: layouts,
        onChanged: (val) {
          updatePayload(payload.copyWith(layouts: val));
        },
        allowedBlockIds: allowedBlockIds,
        promptBlocksState: promptBlocksState,
      );
    }

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.editOutputProfileTitle),
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
              IconButton(
                icon: Icon(
                  enableThreePaneLayout.value
                      ? Icons.table_rows
                      : Icons.view_column,
                ),
                onPressed: () =>
                    enableThreePaneLayout.value = !enableThreePaneLayout.value,
                tooltip: "Toggle Layout",
              ),
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
          child: LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 1100;
              final useThreePane = enableThreePaneLayout.value && isWide;

              if (useThreePane) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 1,
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16.0),
                        child: buildIdentityPane(),
                      ),
                    ),
                    const VerticalDivider(width: 1),
                    Expanded(
                      flex: 1,
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16.0),
                        child: buildSynthesisPane(),
                      ),
                    ),
                    const VerticalDivider(width: 1),
                    Expanded(
                      flex: 1,
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(16.0),
                        child: buildLayoutPane(),
                      ),
                    ),
                  ],
                );
              } else {
                return ListView(
                  padding: const EdgeInsets.all(16.0),
                  children: [
                    buildIdentityPane(),
                    const SizedBox(height: 24),
                    buildSynthesisPane(),
                    const SizedBox(height: 24),
                    buildLayoutPane(),
                  ],
                );
              }
            },
          ),
        ),
      ),
    );
  }
}
