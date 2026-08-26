import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// **Profile Editor View**
///
/// Admin UI for defining strictly-typed Output Profiles for a specific Workflow.
class ProfileEditorView extends HookConsumerWidget {
  final String workflowId;

  const ProfileEditorView({super.key, required this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(workflowFormProvider(workflowId));
    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);
    final availableExtensionsState = ref.watch(
      workflowAvailableExtensionsProvider(workflowId),
    );

    return switch (formState) {
      AsyncData(:final value) => _buildScaffold(
        context,
        ref,
        l10n,
        formState,
        value,
        promptBlocksState,
        stepsState,
        availableExtensionsState,
      ),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.editProfilesTitle(workflowId))),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(workflowFormProvider(workflowId)),
        ),
      ),
      _ => Scaffold(
        appBar: AppBar(title: Text(l10n.editProfilesTitle(workflowId))),
        body: const Center(child: CircularProgressIndicator()),
      ),
    };
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    AsyncValue<Workflow> formState,
    Workflow payload,
    AsyncValue<List<dynamic>> promptBlocksState,
    AsyncValue<List<dynamic>> stepsState,
    AsyncValue<List<String>> availableExtensionsState,
  ) {
    Set<String> allowedBlockIds = {};
    if (stepsState.hasValue) {
      final stepsList = stepsState.value!.cast<NodeStrategy>();
      final taskBlueprintIds = payload.steps
          .map((s) => s.taskBlueprint)
          .toSet();
      for (final step in stepsList) {
        if (taskBlueprintIds.contains(step.id)) {
          if (step.roleBlockId != null) allowedBlockIds.add(step.roleBlockId!);
          if (step.extractionProtocolBlockId != null) {
            allowedBlockIds.add(step.extractionProtocolBlockId!);
          }
          allowedBlockIds.addAll(step.criteriaBlockIds);
        }
      }
    }

    // Inject initial default if entirely missing
    useMemoized(() {
      if (payload.outputProfiles.isEmpty) {
        Future.microtask(() {
          final newProfiles = Map<String, OutputProfile>.from(
            payload.outputProfiles,
          );
          newProfiles['default'] = OutputProfile(
            id: 'default',
            workflowId: payload.id,
            name: const I18nText(
              translations: {'fi': 'Oletusraportti', 'en': 'Default Report'},
            ),
            visibleBlockExtensions: const [],
            visibleWorkflowExtensions: const [],
            layouts: const [
              OutputLayoutBlock(
                presetView: PresetView.metrics1d,
                title: I18nText(translations: {'en': 'Metrics 1D'}),
                textDeliveryMode: TextDeliveryMode.full,
                targetBlocks: [],
              ),
            ],
          );
          ref
              .read(workflowFormProvider(workflowId).notifier)
              .forceRebuild(payload.copyWith(outputProfiles: newProfiles));
        });
      }
    });

    Future<void> saveWorkflow() async {
      try {
        if (payload.id.isEmpty) throw Exception("Workflow ID is missing");

        await ref
            .read(workflowFormProvider(workflowId).notifier)
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
      } catch (e, st) {
        if (!context.mounted) return;
        ref
            .read(loggerServiceProvider)
            .error('Studio', 'Failed to save user profile: $e', e, st);
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

                final newProfiles = Map<String, OutputProfile>.from(
                  payload.outputProfiles,
                );
                newProfiles[newId] = OutputProfile(
                  id: newId,
                  workflowId: payload.id,
                  name: const I18nText(
                    translations: {'fi': 'Uusi profiili', 'en': 'New Profile'},
                  ),
                  visibleBlockExtensions: const [],
                  visibleWorkflowExtensions: const [],
                  layouts: const [],
                );

                ref
                    .read(workflowFormProvider(workflowId).notifier)
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
          title: Text(l10n.editProfilesTitle(workflowId)),
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
          padding: AppSpacing.p16,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    l10n.outputProfilesDictionary,
                    style: Theme.of(context).textTheme.headlineSmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                AppSpacing.w8,
                FilledButton.icon(
                  onPressed: addProfileDialog,
                  icon: const Icon(Icons.add),
                  label: Text(l10n.addVariantBtn),
                ),
              ],
            ),
            AppSpacing.h16,
            ...payload.outputProfiles.entries.map(
              (entry) => _buildProfileCard(
                context,
                ref,
                l10n,
                payload,
                entry.key,
                entry.value,
                allowedBlockIds,
                promptBlocksState,
                availableExtensionsState,
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
    OutputProfile profileDef,
    Set<String> allowedBlockIds,
    AsyncValue<List<dynamic>> promptBlocksState,
    AsyncValue<List<String>> availableExtensionsState,
  ) {
    final layouts = List<OutputLayoutBlock>.from(profileDef.layouts);

    void rebuildProfile(OutputProfile updatedProfile) {
      final newProfiles = Map<String, OutputProfile>.from(
        payload.outputProfiles,
      );
      newProfiles[profileId] = updatedProfile;
      ref
          .read(workflowFormProvider(workflowId).notifier)
          .forceRebuild(payload.copyWith(outputProfiles: newProfiles));
    }

    return Card(
      margin: const EdgeInsets.only(bottom: AppSpacing.s24),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Theme.of(context).colorScheme.outline),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: DefaultTabController(
          length: 3,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TabBar(
                tabs: [
                  Tab(text: l10n.profileTabGeneral),
                  Tab(text: l10n.profileTabXai),
                  Tab(text: l10n.profileTabLayouts),
                ],
              ),
              AppSpacing.h16,
              SizedBox(
                height: 600,
                child: TabBarView(
                  children: [
                    // Tab 1: General
                    ListView(
                      padding: const EdgeInsets.all(AppSpacing.s8),
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                l10n.variantIdLabel(profileId),
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            AppSpacing.w8,
                            IconButton(
                              icon: Icon(
                                Icons.delete,
                                color: Theme.of(context).colorScheme.error,
                              ),
                              onPressed: () {
                                final newProfiles =
                                    Map<String, OutputProfile>.from(
                                      payload.outputProfiles,
                                    );
                                newProfiles.remove(profileId);
                                ref
                                    .read(
                                      workflowFormProvider(workflowId).notifier,
                                    )
                                    .forceRebuild(
                                      payload.copyWith(
                                        outputProfiles: newProfiles,
                                      ),
                                    );
                              },
                            ),
                          ],
                        ),
                        AppSpacing.h12,
                        I18nTextField(
                          label: l10n.profileDisplayNameLabel,
                          initialData: profileDef.name,
                          onChanged: (val) {
                            rebuildProfile(profileDef.copyWith(name: val));
                          },
                        ),
                        AppSpacing.h16,
                        InputDecorator(
                          decoration: InputDecoration(
                            labelText: l10n.profileDisplayScaleLabel,
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<DisplayScale>(
                              value: profileDef.displayScale,
                              isDense: true,
                              isExpanded: true,
                              items: [
                                DropdownMenuItem(
                                  value: DisplayScale.original,
                                  child: Text(l10n.scaleOriginal),
                                ),
                                DropdownMenuItem(
                                  value: DisplayScale.custom,
                                  child: Text(l10n.scaleCustom),
                                ),
                                DropdownMenuItem(
                                  value: DisplayScale.normalized100,
                                  child: Text(l10n.scaleNormalized100),
                                ),
                              ],
                              onChanged: (val) {
                                if (val != null) {
                                  rebuildProfile(
                                    profileDef.copyWith(displayScale: val),
                                  );
                                }
                              },
                            ),
                          ),
                        ),
                      ],
                    ),

                    // Tab 2: XAI / Extensions
                    ListView(
                      padding: const EdgeInsets.all(AppSpacing.s8),
                      children: [
                        InputDecorator(
                          decoration: InputDecoration(
                            labelText: l10n.blockLevelExtensionsLabel,
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                          child: switch (availableExtensionsState) {
                            AsyncData(value: final availableExtensions) =>
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: XaiExtensionType.values.map((ext) {
                                  final l10n = AppLocalizations.of(context)!;
                                  String label = ext.name;
                                  switch (ext) {
                                    case XaiExtensionType.citation:
                                      label = l10n.xaiSourceCitation;
                                      break;
                                    case XaiExtensionType.justification:
                                      label = l10n.xaiJustification;
                                      break;
                                    case XaiExtensionType.falsification:
                                      label = l10n.xaiDevilsAdvocate;
                                      break;
                                    case XaiExtensionType.theoryLink:
                                      label = l10n.xaiTheoryLink;
                                      break;
                                    case XaiExtensionType.riskFlag:
                                      label = l10n.xaiRiskFlag;
                                      break;
                                    case XaiExtensionType.coaching:
                                      label = l10n.xaiCoachingTip;
                                      break;
                                    case XaiExtensionType.missingContext:
                                      label = l10n.xaiMissingContext;
                                      break;
                                    case XaiExtensionType.remediationSteps:
                                      label = l10n.xaiRemediation;
                                      break;
                                    case XaiExtensionType.emotionalSentiment:
                                      label = l10n.xaiSentiment;
                                      break;
                                    case XaiExtensionType.confidence:
                                      label = l10n.xaiConfidence;
                                      break;
                                    case XaiExtensionType.sourceId:
                                      label = l10n.xaiSourceId;
                                      break;
                                    case XaiExtensionType.contextualOverride:
                                      label = l10n.xaiContextualOverride;
                                      break;
                                    case XaiExtensionType.varianceValidation:
                                      label = l10n.xaiVarianceValidationTitle;
                                      break;
                                    case XaiExtensionType
                                        .authenticityEvaluation:
                                      label =
                                          l10n.xaiAuthenticityEvaluationTitle;
                                      break;
                                  }

                                  // Dynamic Dropdown Population
                                  if (!availableExtensions.contains(
                                    ext.backendValue,
                                  )) {
                                    return const SizedBox.shrink();
                                  }

                                  final isWorkflowExtension = [
                                    XaiExtensionType.varianceValidation,
                                    XaiExtensionType.authenticityEvaluation,
                                  ].contains(ext);

                                  if (isWorkflowExtension)
                                    return const SizedBox.shrink();

                                  return CheckboxListTile(
                                    title: Text(label),
                                    value: profileDef.visibleBlockExtensions
                                        .contains(ext),
                                    onChanged: (val) {
                                      final updatedList =
                                          List<XaiExtensionType>.from(
                                            profileDef.visibleBlockExtensions,
                                          );
                                      if (val == true) {
                                        updatedList.add(ext);
                                      } else {
                                        updatedList.remove(ext);
                                      }
                                      rebuildProfile(
                                        profileDef.copyWith(
                                          visibleBlockExtensions: updatedList,
                                        ),
                                      );
                                    },
                                    controlAffinity:
                                        ListTileControlAffinity.leading,
                                    dense: true,
                                  );
                                }).toList(),
                              ),
                            AsyncLoading() => const Center(
                              child: CircularProgressIndicator(),
                            ),
                            AsyncError(:final error) => Text(
                              l10n.studioViewsErrorLoadingExtensions(
                                error.toString(),
                              ),
                            ),
                          },
                        ),
                        AppSpacing.h16,
                        InputDecorator(
                          decoration: InputDecoration(
                            labelText: l10n.workflowLevelExtensionsLabel,
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children:
                                [
                                  XaiExtensionType.varianceValidation,
                                  XaiExtensionType.authenticityEvaluation,
                                ].map((ext) {
                                  final l10n = AppLocalizations.of(context)!;
                                  String label = ext.name;
                                  switch (ext) {
                                    case XaiExtensionType.varianceValidation:
                                      label = l10n.xaiVarianceValidationTitle;
                                      break;
                                    case XaiExtensionType
                                        .authenticityEvaluation:
                                      label =
                                          l10n.xaiAuthenticityEvaluationTitle;
                                      break;
                                    case XaiExtensionType.confidence:
                                      label = l10n.xaiConfidence;
                                      break;
                                    default:
                                      break;
                                  }

                                  return CheckboxListTile(
                                    title: Text(label),
                                    value: profileDef.visibleWorkflowExtensions
                                        .contains(ext),
                                    onChanged: (val) {
                                      final updatedList =
                                          List<XaiExtensionType>.from(
                                            profileDef
                                                .visibleWorkflowExtensions,
                                          );
                                      if (val == true) {
                                        updatedList.add(ext);
                                      } else {
                                        updatedList.remove(ext);
                                      }
                                      rebuildProfile(
                                        profileDef.copyWith(
                                          visibleWorkflowExtensions:
                                              updatedList,
                                        ),
                                      );
                                    },
                                    controlAffinity:
                                        ListTileControlAffinity.leading,
                                    dense: true,
                                  );
                                }).toList(),
                          ),
                        ),
                        AppSpacing.h24,
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              AppLocalizations.of(
                                context,
                              )!.profileEditorMaxExtensionItems,
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            AppSpacing.h8,
                            Row(
                              children: [
                                Expanded(
                                  child: Slider(
                                    value: profileDef.maxExtensionItems
                                        .toDouble(),
                                    min: SystemUiConstraints
                                        .maxExtensionItemsSliderMin
                                        .value
                                        .toDouble(),
                                    max: SystemUiConstraints
                                        .maxExtensionItemsSliderMax
                                        .value
                                        .toDouble(),
                                    divisions:
                                        SystemUiConstraints
                                            .maxExtensionItemsSliderMax
                                            .value -
                                        SystemUiConstraints
                                            .maxExtensionItemsSliderMin
                                            .value,
                                    label: profileDef.maxExtensionItems
                                        .toString(),
                                    onChanged: (val) {
                                      rebuildProfile(
                                        profileDef.copyWith(
                                          maxExtensionItems: val.round(),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                                SizedBox(
                                  width: 40,
                                  child: Text(
                                    profileDef.maxExtensionItems.toString(),
                                    textAlign: TextAlign.center,
                                    style: Theme.of(
                                      context,
                                    ).textTheme.titleMedium,
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              AppLocalizations.of(
                                context,
                              )!.profileEditorMaxExtensionItemsDesc,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                                  ),
                            ),
                          ],
                        ),
                      ],
                    ),

                    // Tab 3: Layouts
                    ListView(
                      padding: const EdgeInsets.all(AppSpacing.s8),
                      children: [
                        LayoutEditorCard(
                          layouts: layouts,
                          onChanged: (val) {
                            rebuildProfile(profileDef.copyWith(layouts: val));
                          },
                          allowedBlockIds: allowedBlockIds,
                          promptBlocksState: promptBlocksState,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
