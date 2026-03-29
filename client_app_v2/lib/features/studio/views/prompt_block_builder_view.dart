import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/views/widgets/row_editor_modal.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/models/prompt_block_category.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';

/// **Universal Matrix Builder**
///
/// CRUD interface for editing evaluation matrices adhering strictly to the
/// De-Generator policy (`Map<String, dynamic>`).
/// Now compliant with the Gold Standard Riverpod Form UI pattern.
class PromptBlockBuilderView extends HookConsumerWidget {
  final String? id;
  final String? slug;
  final Map<String, dynamic>? initialData;

  const PromptBlockBuilderView({
    super.key,
    this.id,
    this.slug,
    this.initialData,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final blockId = (id == null || id!.isEmpty) ? 'new' : id!;
    final formState = ref.watch(promptBlockFormProvider(blockId));

    return formState.when(
      loading:
          () => Scaffold(
            appBar: AppBar(title: Text(l10n.promptBlockEditTitle)),
            body: const Center(child: CircularProgressIndicator()),
          ),
      error:
          (e, st) => Scaffold(
            appBar: AppBar(title: Text(l10n.promptBlockEditTitle)),
            body: ErrorView(
              error: e,
              stackTrace: st,
              compact: false,
              onRetry: () => ref.invalidate(promptBlockFormProvider(blockId)),
            ),
          ),
      data: (payload) {
        return _buildScaffold(context, ref, l10n, formState, payload, blockId);
      },
    );
  }

  void _addListItem(
    WidgetRef ref,
    Map<String, dynamic> payload,
    String blockId,
    String key,
    Map<String, dynamic> initialValue,
  ) {
    final list = SafeCast.safeList(payload[key]);
    list.add(initialValue);
    payload[key] = list;
    ref.read(promptBlockFormProvider(blockId).notifier).forceRebuild();
  }

  void _removeListItem(
    WidgetRef ref,
    Map<String, dynamic> payload,
    String blockId,
    String key,
    int index,
  ) {
    final list = SafeCast.safeList(payload[key]);
    list.removeAt(index);
    payload[key] = list;
    ref.read(promptBlockFormProvider(blockId).notifier).forceRebuild();
  }

  void _deletePromptBlock(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    String id,
    MutationState<void> deleteMut,
  ) {
    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(l10n.stepDeleteConfirmTitle),
            content: Text(l10n.stepDeleteConfirmMessage(id)),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text(l10n.cancel),
              ),
              TextButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  deleteMut.mutate(
                    () => ref
                        .read(promptBlocksControllerProvider.notifier)
                        .deletePromptBlock(id),
                  );
                },
                child: Text(
                  l10n.delete,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            ],
          ),
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
    String blockId,
  ) {
    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (context.mounted) {
          final rendered = data['rendered_prompt']?.toString();
          if (rendered == null) {
            throw AppException.validation(l10n.simulatorCorruptionError);
          }
          showDialog(
            context: context,
            builder:
                (ctx) => AlertDialog(
                  title: Text(l10n.simulatorOutputTitle),
                  content: SizedBox(
                    width: double.maxFinite,
                    child: SingleChildScrollView(
                      child: Text(
                        rendered,
                        style: const TextStyle(fontFamily: 'monospace'),
                      ),
                    ),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx),
                      child: Text(l10n.closeModalBtn),
                    ),
                  ],
                ),
          );
        }
      },
      onError: (e) {
        if (context.mounted) {
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to validate prompt block: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.simulatorFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    final deleteMutation = useMutation<void>(
      onSuccess: (_) {
        if (context.mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.studioSaveSuccess)));
          context.pop();
        }
      },
      onError: (e) {
        if (context.mounted) {
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete prompt block: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    Future<void> savePromptBlock() async {
      final labelMap = SafeCast.safeMap(payload['label']);
      final transMap = SafeCast.safeMap(labelMap['translations']);
      final enLabel = SafeCast.safeString(transMap['en']);

      if (enLabel.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.promptBlockMandatoryEnglishError)),
        );
        return;
      }

      if (payload['theory_grounding'] == null) {
        payload.remove('theory_grounding');
      }

      final currentId =
          payload['id']?.toString() != null &&
                  payload['id'].toString().isNotEmpty
              ? payload['id'].toString()
              : 'blk_${DateTime.now().millisecondsSinceEpoch}';

      payload['id'] = currentId;

      try {
        await ref
            .read(promptBlockFormProvider(blockId).notifier)
            .submit(payload);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.promptBlockSavedSuccess),
              backgroundColor: const Color(0xFF2E7D32),
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

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: 'Back to Studio',
            onPressed: () => context.go('/admin'),
          ),
          title: Text(l10n.promptBlockEditTitle),
          actions: [
            if (payload['id']?.toString().isNotEmpty == true)
              IconButton(
                onPressed:
                    () => _deletePromptBlock(
                      context,
                      ref,
                      l10n,
                      payload['id'].toString(),
                      deleteMutation,
                    ),
                icon: Icon(
                  Icons.delete,
                  color: Theme.of(context).colorScheme.error,
                ),
                tooltip: l10n.delete,
              ),
            IconButton(
              onPressed:
                  validateMutation.isLoading
                      ? null
                      : () {
                        validateMutation.mutate(() async {
                          final simulatePayload = {
                            'block': payload,
                            'mock_inputs':
                                <
                                  String,
                                  dynamic
                                >{}, // Provide empty mock inputs for now
                          };
                          return await ref
                              .read(promptBlocksControllerProvider.notifier)
                              .simulatePromptBlock(simulatePayload);
                        });
                      },
              icon:
                  validateMutation.isLoading
                      ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : Icon(
                        Icons.bug_report,
                        color: Theme.of(context).colorScheme.primary,
                      ),
              tooltip: 'Simulate Prompt',
            ),
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
                onPressed: savePromptBlock,
                icon: const Icon(Icons.save),
                label: Text(l10n.studioSaveButton),
              ),
            const SizedBox(width: 16),
          ],
        ),
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Matrix Metadata
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.promptBlockConfigTitle,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 16),
                        if (payload['id']?.toString().isNotEmpty == true) ...[
                          Text(
                            l10n.opaqueIdLabel(payload['id'].toString()),
                            style: TextStyle(
                              color:
                                  Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                              fontFamily: 'monospace',
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 24),
                        ],
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // --- ROOT CONFIGURATION (NO MORE CRITERIA ARRAY) ---
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          l10n.promptBlockPropertiesTitle,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Categories
                        DropdownButtonFormField<PromptBlockCategory>(
                          decoration: InputDecoration(
                            labelText: l10n.categoryLabel,
                          ),
                          initialValue: PromptBlockCategory.fromId(
                            payload['category_id'] as String? ?? 'system_rule',
                          ),
                          items:
                              PromptBlockCategory.values.map((category) {
                                return DropdownMenuItem(
                                  value: category,
                                  child: Text(category.displayName(context)),
                                );
                              }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              payload['category_id'] = val.id;
                              ref
                                  .read(
                                    promptBlockFormProvider(blockId).notifier,
                                  )
                                  .forceRebuild();
                            }
                          },
                        ),
                        const SizedBox(height: 16),

                        // Label (I18N)
                        I18nTextField(
                          label: l10n.blockLabelName,
                          initialData: SafeCast.safeMap(payload['label']),
                          onChanged: (val) {
                            payload['label'] = val;
                            ref
                                .read(promptBlockFormProvider(blockId).notifier)
                                .forceRebuild();
                          },
                        ),
                        const SizedBox(height: 16),

                        // Description (I18N) - Short UI Hint
                        I18nTextField(
                          label: l10n.shortDescriptionHint,
                          initialData: SafeCast.safeMap(payload['description']),
                          onChanged: (val) {
                            payload['description'] = val;
                            ref
                                .read(promptBlockFormProvider(blockId).notifier)
                                .forceRebuild();
                          },
                        ),
                        const SizedBox(height: 16),

                        // AI Description - Core LLM Prompt (English Only)
                        TextFormField(
                          initialValue: payload['ai_description']?.toString(),
                          decoration: InputDecoration(
                            labelText: l10n.systemPromptMandatory,
                            border: const OutlineInputBorder(),
                          ),
                          maxLines: 8,
                          onChanged: (val) {
                            payload['ai_description'] = val;
                            // Opting to not constantly rebuild on text changes to avoid losing focus,
                            // mutation occurs implicitly in payload reference.
                          },
                        ),
                        Padding(
                          padding: const EdgeInsets.only(top: 8.0),
                          child: Text(
                            l10n.adminAiDescriptionHint,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        Padding(
                          padding: EdgeInsets.only(top: 4.0),
                          child: Text(
                            l10n.adminPromptBestPracticesHint,
                            style: TextStyle(
                              color:
                                  Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                              fontSize: 13,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),

                        // XAI & Constraints Container
                        Container(
                          padding: const EdgeInsets.all(12),
                          color:
                              Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHighest,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text(
                                l10n.dataTypeExecutionConstraints,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Wrap(
                                spacing: 16,
                                runSpacing: 8,
                                crossAxisAlignment: WrapCrossAlignment.center,
                                children: [
                                  DropdownButton<String>(
                                    value:
                                        [
                                              'int',
                                              'float',
                                              'number',
                                              'string',
                                              'instruction',
                                              'bool',
                                            ].contains(payload['type'])
                                            ? payload['type'] as String
                                            : 'instruction',
                                    items: [
                                      DropdownMenuItem(
                                        value: 'instruction',
                                        child: Text(l10n.typeInstruction),
                                      ),
                                      DropdownMenuItem(
                                        value: 'string',
                                        child: Text(l10n.typeString),
                                      ),
                                      DropdownMenuItem(
                                        value: 'number',
                                        child: Text(l10n.typeNumber),
                                      ),
                                      DropdownMenuItem(
                                        value: 'int',
                                        child: Text(l10n.typeInteger),
                                      ),
                                      DropdownMenuItem(
                                        value: 'float',
                                        child: Text(l10n.typeFloat),
                                      ),
                                      DropdownMenuItem(
                                        value: 'bool',
                                        child: Text(l10n.typeBoolean),
                                      ),
                                    ],
                                    onChanged: (val) {
                                      payload['type'] = val;
                                      ref
                                          .read(
                                            promptBlockFormProvider(
                                              blockId,
                                            ).notifier,
                                          )
                                          .forceRebuild();
                                    },
                                  ),
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Checkbox(
                                        value:
                                            payload['allow_decimals'] == true,
                                        onChanged: (val) {
                                          payload['allow_decimals'] = val;
                                          ref
                                              .read(
                                                promptBlockFormProvider(
                                                  blockId,
                                                ).notifier,
                                              )
                                              .forceRebuild();
                                        },
                                      ),
                                      Text(l10n.allowDecimals),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                l10n.xaiOutputExtensionsTitle,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children:
                                    {
                                      "justification": l10n.xaiJustification,
                                      "coaching": l10n.xaiCoachingTip,
                                      "falsification": l10n.xaiDevilsAdvocate,
                                      "missing_context": l10n.xaiMissingContext,
                                      "risk_flag": l10n.xaiRiskFlag,
                                      "remediation_steps": l10n.xaiRemediation,
                                      "emotional_sentiment": l10n.xaiSentiment,
                                      "theory_link": l10n.xaiTheoryLink,
                                      "confidence": l10n.xaiConfidence,
                                      "citation": l10n.xaiSourceCitation,
                                    }.entries.map((entry) {
                                      final extList =
                                          SafeCast.safeList(
                                            payload['output_extensions'],
                                          ).map((e) => e.toString()).toList();
                                      final isSelected = extList.contains(
                                        entry.key,
                                      );
                                      return FilterChip(
                                        label: Text(entry.value),
                                        selected: isSelected,
                                        onSelected: (bool selected) {
                                          if (selected) {
                                            extList.add(entry.key);
                                          } else {
                                            extList.remove(entry.key);
                                          }
                                          payload['output_extensions'] =
                                              extList;
                                          payload.remove(
                                            'require_justification',
                                          );
                                          ref
                                              .read(
                                                promptBlockFormProvider(
                                                  blockId,
                                                ).notifier,
                                              )
                                              .forceRebuild();
                                        },
                                        selectedColor:
                                            Theme.of(
                                              context,
                                            ).colorScheme.primaryContainer,
                                        checkmarkColor:
                                            Theme.of(
                                              context,
                                            ).colorScheme.onPrimaryContainer,
                                      );
                                    }).toList(),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),
                        // Theory Grounding Wrapper
                        Container(
                          padding: const EdgeInsets.all(12),
                          color:
                              Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHigh,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    l10n.theoryGroundingTitle,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Switch(
                                    value: payload['theory_grounding'] != null,
                                    onChanged: (val) {
                                      if (val) {
                                        payload['theory_grounding'] = {
                                          'source_url': '',
                                          'citation_reference': '',
                                        };
                                      } else {
                                        payload['theory_grounding'] = null;
                                        payload.remove('theory_grounding');
                                      }
                                      ref
                                          .read(
                                            promptBlockFormProvider(
                                              blockId,
                                            ).notifier,
                                          )
                                          .forceRebuild();
                                    },
                                  ),
                                ],
                              ),
                              if (payload['theory_grounding'] != null) ...[
                                const SizedBox(height: 8),
                                // Source URL
                                TextFormField(
                                  initialValue:
                                      SafeCast.safeMap(
                                        payload['theory_grounding'],
                                      )['source_url']?.toString(),
                                  decoration: InputDecoration(
                                    labelText: l10n.sourceUrlLabel,
                                    border: const UnderlineInputBorder(),
                                  ),
                                  onChanged: (val) {
                                    final grounding = SafeCast.safeMap(
                                      payload['theory_grounding'],
                                    );
                                    grounding['source_url'] = val;
                                  },
                                ),
                                const SizedBox(height: 8),
                                TextFormField(
                                  initialValue:
                                      SafeCast.safeMap(
                                        payload['theory_grounding'],
                                      )['citation_reference']?.toString(),
                                  decoration: InputDecoration(
                                    labelText: l10n.citationReferenceLabel,
                                    border: const UnderlineInputBorder(),
                                  ),
                                  onChanged: (val) {
                                    final grounding = SafeCast.safeMap(
                                      payload['theory_grounding'],
                                    );
                                    grounding['citation_reference'] = val;
                                  },
                                ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                if (payload['type'] != 'instruction') ...[
                  const SizedBox(height: 16),
                  _buildI18nListCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    blockId,
                    'rows',
                    l10n.gridRowsOptional,
                  ),
                  const SizedBox(height: 16),
                  _buildI18nListCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    blockId,
                    'columns',
                    l10n.gridColumnsOptional,
                  ),
                  const SizedBox(height: 16),
                  _buildScalesCard(context, ref, l10n, payload, blockId),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildI18nListCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
    String blockId,
    String key,
    String title,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    Switch(
                      value: payload[key] != null,
                      onChanged: (val) {
                        if (val) {
                          payload[key] = [];
                        } else {
                          payload[key] = null;
                          payload.remove(key);
                        }
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild();
                      },
                    ),
                    if (payload[key] != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final bool isRow = key == 'rows';
                          final initialMap =
                              isRow
                                  ? {
                                    'label': {
                                      'default_locale': 'en',
                                      'translations': <String, dynamic>{
                                        'en': '',
                                      },
                                    },
                                    'ai_description': 'CRITICAL MANDATE: ',
                                  }
                                  : {
                                    'default_locale': 'en',
                                    'translations': <String, dynamic>{'en': ''},
                                  };

                          final result = await showDialog<Map<String, dynamic>>(
                            context: context,
                            builder:
                                (ctx) => RowEditorModal(
                                  initialRow: initialMap,
                                  title: 'Add $title',
                                  isMatrixRow: isRow,
                                ),
                          );
                          if (result != null) {
                            _addListItem(ref, payload, blockId, key, result);
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Add'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (payload[key] != null) ...[
              const SizedBox(height: 16),
              ...SafeCast.safeList(payload[key]).asMap().entries.map((entry) {
                final index = entry.key;
                final item = SafeCast.safeMap(entry.value);
                final bool isRow = key == 'rows';
                final displayItem =
                    isRow ? SafeCast.safeMap(item['label']) : item;

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      displayItem['translations']?[displayItem['default_locale']] ??
                          displayItem['default_locale'] ??
                          'No text',
                    ),
                    subtitle: Text('Item ${index + 1}'),
                    trailing: IconButton(
                      icon: Icon(
                        Icons.delete,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      onPressed:
                          () => _removeListItem(
                            ref,
                            payload,
                            blockId,
                            key,
                            index,
                          ),
                    ),
                    onTap: () async {
                      final result = await showDialog<Map<String, dynamic>>(
                        context: context,
                        builder:
                            (ctx) => RowEditorModal(
                              initialRow: item,
                              title: 'Edit $title Item',
                              isMatrixRow: isRow,
                            ),
                      );
                      if (result != null) {
                        final list = SafeCast.safeList(payload[key]);
                        list[index] = result;
                        payload[key] = list;
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild();
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScalesCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
    String blockId,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.barsScalesTitle,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    Switch(
                      value: payload['scales'] != null,
                      onChanged: (val) {
                        if (val) {
                          payload['scales'] = [];
                        } else {
                          payload['scales'] = null;
                          payload.remove('scales');
                        }
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild();
                      },
                    ),
                    if (payload['scales'] != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final result = await showDialog<Map<String, dynamic>>(
                            context: context,
                            builder:
                                (ctx) => ScaleEditorModal(
                                  initialScale: {
                                    'score': 1,
                                    'name': {
                                      'default_locale': 'en',
                                      'translations': <String, dynamic>{
                                        'en': '',
                                      },
                                    },
                                    'claims': [
                                      {
                                        'default_locale': 'en',
                                        'translations': <String, dynamic>{
                                          'en': '',
                                        },
                                      },
                                    ],
                                  },
                                ),
                          );
                          if (result != null) {
                            _addListItem(
                              ref,
                              payload,
                              blockId,
                              'scales',
                              result,
                            );
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: Text(l10n.addGradeBtn),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (payload['scales'] != null) ...[
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue: payload['scale_min']?.toString() ?? '4',
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                      decoration: InputDecoration(
                        labelText: l10n.scaleMinLabel,
                        border: const OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final parsed = num.tryParse(val);
                        if (parsed != null) {
                          payload['scale_min'] = parsed;
                          // Don't force build for pure typing to avoid blur
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      initialValue: payload['scale_max']?.toString() ?? '10',
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                      decoration: InputDecoration(
                        labelText: l10n.scaleMaxLabel,
                        border: const OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final parsed = num.tryParse(val);
                        if (parsed != null) {
                          payload['scale_max'] = parsed;
                        }
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...SafeCast.safeList(payload['scales']).asMap().entries.map((
                scaleEntry,
              ) {
                final sIndex = scaleEntry.key;
                final scale = SafeCast.safeMap(scaleEntry.value);
                final claimsLength = SafeCast.safeList(scale['claims']).length;
                final gradeName =
                    SafeCast.safeMap(
                      scale['name'],
                    )['translations']?[SafeCast.safeMap(
                      scale['name'],
                    )['default_locale']] ??
                    SafeCast.safeMap(scale['name'])['default_locale'] ??
                    '';

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      l10n.gradeScoreLabel(
                        scale['score'].toString(),
                        gradeName.isNotEmpty ? "- $gradeName" : "",
                      ),
                    ),
                    subtitle: Text(
                      l10n.claimsCountLabel(claimsLength.toString()),
                    ),
                    trailing: IconButton(
                      icon: Icon(
                        Icons.delete,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      onPressed:
                          () => _removeListItem(
                            ref,
                            payload,
                            blockId,
                            'scales',
                            sIndex,
                          ),
                    ),
                    onTap: () async {
                      final result = await showDialog<Map<String, dynamic>>(
                        context: context,
                        builder: (ctx) => ScaleEditorModal(initialScale: scale),
                      );
                      if (result != null) {
                        final list = SafeCast.safeList(payload['scales']);
                        list[sIndex] = result;
                        payload['scales'] = list;
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild();
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
