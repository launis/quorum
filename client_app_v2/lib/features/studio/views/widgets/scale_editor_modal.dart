import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/contrastive_pair_editor.dart';
import 'package:client_app/features/studio/views/widgets/dynamic_item_list_editor.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/linguistic_shield_banner.dart';
import 'package:client_app/features/studio/views/widgets/prompt_preview_dialog.dart';
import 'package:client_app/features/studio/views/widgets/tag_chip_input.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class _SaveIntent extends Intent {
  const _SaveIntent();
}

class _DismissIntent extends Intent {
  const _DismissIntent();
}

/// Desktop-class pro-tool modal editor for evaluation scale rubrics and TDA assertions.
/// Enforces Adaptive Master Selector navigation, 5-card layout, save debouncing, and PopScope dismissal.
class ScaleEditorModal extends ConsumerStatefulWidget {
  final MatrixScale initialScale;

  const ScaleEditorModal({super.key, required this.initialScale});

  @override
  ConsumerState<ScaleEditorModal> createState() => _ScaleEditorModalState();
}

class _ScaleEditorModalState extends ConsumerState<ScaleEditorModal> {
  final _formKey = GlobalKey<FormState>();
  final _tagChipKey = GlobalKey<TagChipInputState>();
  final _scrollController = ScrollController();

  late MatrixScale _editableScale;
  late final String _initialScaleJson;
  int _selectedClaimIndex = 0;
  bool _isSaving = false;
  bool _isLoadingPreview = false;

  @override
  void initState() {
    super.initState();
    _editableScale = widget.initialScale.copyWith();
    _initialScaleJson = jsonEncode(widget.initialScale.toJson());
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  bool _isModelDirty() {
    return jsonEncode(_editableScale.toJson()) != _initialScaleJson;
  }

  bool _hasPendingInputBuffers() {
    return _tagChipKey.currentState?.hasPendingBuffer ?? false;
  }

  void _handleDismiss() {
    FocusScope.of(context).unfocus();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final isDirty = _isModelDirty() || _hasPendingInputBuffers();
      if (!isDirty) {
        Navigator.of(context).pop(null);
        return;
      }

      final l10n = AppLocalizations.of(context)!;
      showDialog<void>(
        context: context,
        builder: (dialogCtx) => AlertDialog(
          title: Text(l10n.scaleDiscardChangesTitle),
          content: Text(l10n.scaleDiscardChangesMessage),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text(l10n.scaleContinueEditingBtn),
            ),
            FilledButton(
              onPressed: () {
                Navigator.of(dialogCtx).pop();
                Navigator.of(context).pop(null);
              },
              child: Text(l10n.scaleDiscardBtn),
            ),
          ],
        ),
      );
    });
  }

  void _save() {
    if (_isSaving) return;
    _isSaving = true;

    FocusScope.of(context).unfocus();

    // 1. Validate active claim first via Form
    if (!_formKey.currentState!.validate()) {
      _isSaving = false;
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          0,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
      return;
    }

    // 2. Validate all other claims by checking their underlying model state
    final claims = _editableScale.claims;
    for (int i = 0; i < claims.length; i++) {
      final claim = claims[i];
      final primaryLabel = claim.label.get('en').trim();
      if (primaryLabel.isEmpty) {
        _isSaving = false;
        setState(() => _selectedClaimIndex = i);
        return;
      }
      for (final tda in claim.tdaAssertions) {
        if (tda.conceptDescription.trim().length < 10) {
          _isSaving = false;
          setState(() => _selectedClaimIndex = i);
          return;
        }
      }
    }

    // Auto-commit transient tag chip buffer if any before pop
    _formKey.currentState!.save();
    Navigator.of(context).pop(_editableScale);
  }

  Future<void> _previewScalePrompt() async {
    if (_isLoadingPreview) return;
    setState(() => _isLoadingPreview = true);

    try {
      final transientBlock = PromptBlock.matrix(
        id: 'blk_0000000000000000',
        slug: 'sim_preview',
        label: const I18nText(translations: {'en': 'Simulation'}),
        description: const I18nText(translations: {'en': 'Simulation'}),
        scales: [_editableScale],
      );

      final currentLocale = Localizations.localeOf(context).languageCode;

      final res = await ref
          .read(promptBlocksControllerProvider.notifier)
          .simulatePromptBlock(
            transientBlock,
            const <String, dynamic>{},
            targetScaleScore: _editableScale.score,
            targetLocale: currentLocale,
          );

      if (!mounted) return;
      setState(() => _isLoadingPreview = false);

      final promptContext =
          res['prompt_context'] as Map<String, dynamic>? ?? const {};
      final staticMessages = promptContext['static_messages'];
      final dynamicMessages = promptContext['dynamic_messages'];
      final tools = promptContext['tools'];
      final renderedPrompt = res['rendered_prompt'] as String? ?? '';

      await showDialog<void>(
        context: context,
        builder: (dialogCtx) => PromptPreviewDialog(
          staticContent: PromptPreviewFormatter.formatMessagesFromRaw(
            staticMessages,
          ),
          dynamicContent: PromptPreviewFormatter.formatMessagesFromRaw(
            dynamicMessages,
          ),
          schemaContent: PromptPreviewFormatter.formatSchema(
            tools,
            renderedPrompt,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingPreview = false);
      final l10n = AppLocalizations.of(context)!;
      await showDialog<void>(
        context: context,
        builder: (errCtx) => AlertDialog(
          title: Text(l10n.errorUnknown),
          content: Text(e.toString()),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(errCtx).pop(),
              child: Text(l10n.dialogOk),
            ),
          ],
        ),
      );
    }
  }

  void _addClaim() {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.add(
        MatrixClaim(
          label: const I18nText(translations: {'en': 'New Criterion'}),
          tdaAssertions: [
            TDAAssertion.create(
              conceptDescription: 'CRITICAL MANDATE: ',
              inverseEvidence: false,
              aggregationMode: AggregationMode.exists,
            ),
          ],
        ),
      );
      _editableScale = _editableScale.copyWith(claims: claims);
      _selectedClaimIndex = claims.length - 1;
    });
  }

  void _removeClaim(int index) {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.removeAt(index);
      _editableScale = _editableScale.copyWith(claims: claims);
      if (_selectedClaimIndex >= claims.length) {
        _selectedClaimIndex = claims.isEmpty ? 0 : claims.length - 1;
      }
    });
  }

  void _updateActiveTda(TDAAssertion Function(TDAAssertion old) updater) {
    if (_editableScale.claims.isEmpty) return;
    final claims = List<MatrixClaim>.from(_editableScale.claims);
    final claim = claims[_selectedClaimIndex];
    if (claim.tdaAssertions.isEmpty) return;

    final tdas = List<TDAAssertion>.from(claim.tdaAssertions);
    tdas[0] = updater(tdas[0]);
    claims[_selectedClaimIndex] = claim.copyWith(tdaAssertions: tdas);
    setState(() {
      _editableScale = _editableScale.copyWith(claims: claims);
    });
  }

  Widget _buildCard({required String title, required Widget child}) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            AppSpacing.h16,
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildCard1Core(TDAAssertion tda, AppLocalizations l10n) {
    return _buildCard(
      title: l10n.scaleSectionCoreHypothesis,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            key: ValueKey('concept_${tda.tdaId}_$_selectedClaimIndex'),
            initialValue: tda.conceptDescription,
            decoration: InputDecoration(
              labelText: l10n.scaleConceptDescriptionLabel,
              helperText: l10n.scaleConceptDescriptionHelper,
              border: const OutlineInputBorder(),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
            ),
            maxLines: 3,
            validator: (val) {
              final len = val?.trim().length ?? 0;
              if (len < SystemUiConstraints.tdaConceptMinLength.value) {
                return l10n.tdaConceptMinLengthError(
                  SystemUiConstraints.tdaConceptMinLength.value,
                );
              }
              return null;
            },
            onChanged: (val) =>
                _updateActiveTda((t) => t.copyWith(conceptDescription: val)),
          ),
          LinguisticShieldBanner(text: tda.conceptDescription),
          AppSpacing.h12,
          LayoutBuilder(
            builder: (context, constraints) {
              final isNarrow = constraints.maxWidth < 520;
              final anchorField = TextFormField(
                key: ValueKey('anchor_${tda.tdaId}_$_selectedClaimIndex'),
                initialValue: tda.anchorTarget,
                decoration: InputDecoration(
                  labelText: l10n.tdaAnchorTarget,
                  helperText: l10n.tdaAnchorTargetHelper,
                  border: const OutlineInputBorder(),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 8,
                  ),
                ),
                onChanged: (val) => _updateActiveTda(
                  (t) => t.copyWith(
                    anchorTarget: val.trim().isEmpty ? null : val.trim(),
                  ),
                ),
              );

              final scopeDropdown = DropdownButtonFormField<String>(
                key: ValueKey('scope_${tda.tdaId}_$_selectedClaimIndex'),
                isExpanded: true,
                initialValue: tda.boundingBoxScope,
                decoration: InputDecoration(
                  labelText: l10n.tdaBoundingBox,
                  helperText: l10n.tdaBoundingBoxHelper,
                  border: const OutlineInputBorder(),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 8,
                  ),
                ),
                items: [
                  DropdownMenuItem(
                    value: 'sentence',
                    child: Text(l10n.tdaScopeSentence),
                  ),
                  DropdownMenuItem(
                    value: 'paragraph',
                    child: Text(l10n.tdaScopeParagraph),
                  ),
                  DropdownMenuItem(
                    value: 'adjacent_paragraphs',
                    child: Text(l10n.tdaScopeAdjacentParagraphs),
                  ),
                  DropdownMenuItem(
                    value: 'document',
                    child: Text(l10n.tdaScopeDocument),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    _updateActiveTda((t) => t.copyWith(boundingBoxScope: val));
                  }
                },
              );

              if (isNarrow) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [anchorField, AppSpacing.h12, scopeDropdown],
                );
              }

              return Row(
                children: [
                  Expanded(child: anchorField),
                  AppSpacing.w16,
                  Expanded(child: scopeDropdown),
                ],
              );
            },
          ),
          AppSpacing.h12,
          TextFormField(
            key: ValueKey('rule_${tda.tdaId}_$_selectedClaimIndex'),
            initialValue: tda.extractionRule,
            decoration: InputDecoration(
              labelText: l10n.tdaExtractionRule,
              helperText: l10n.tdaExtractionRuleHelper,
              border: const OutlineInputBorder(),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
            ),
            onChanged: (val) => _updateActiveTda(
              (t) => t.copyWith(
                extractionRule: val.trim().isEmpty ? null : val.trim(),
              ),
            ),
          ),
          AppSpacing.h12,
          DropdownButtonFormField<EvaluationTrack>(
            key: ValueKey('track_${tda.tdaId}_$_selectedClaimIndex'),
            isExpanded: true,
            initialValue: tda.evaluationTrack,
            decoration: InputDecoration(
              labelText: l10n.scaleEvaluationTrackLabel,
              helperText: l10n.scaleEvaluationTrackHelper,
              border: const OutlineInputBorder(),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
            ),
            items: EvaluationTrack.values.map((track) {
              return DropdownMenuItem<EvaluationTrack>(
                value: track,
                child: Text(
                  track == EvaluationTrack.extractiveSensor
                      ? l10n.scaleTrackSensor
                      : l10n.scaleTrackJudgement,
                ),
              );
            }).toList(),
            onChanged: (track) {
              if (track != null)
                _updateActiveTda((t) => t.copyWith(evaluationTrack: track));
            },
          ),
          AppSpacing.h8,
          SwitchListTile(
            title: Text(l10n.scaleEnforcePreFlightTitle),
            subtitle: Text(l10n.scaleEnforcePreFlightDesc),
            value: tda.enforcePreFlight,
            onChanged: (val) =>
                _updateActiveTda((t) => t.copyWith(enforcePreFlight: val)),
          ),
          if (tda.evaluationTrack == EvaluationTrack.extractiveSensor) ...[
            AppSpacing.h12,
            TagChipInput(
              key: ValueKey('facts_${tda.tdaId}_$_selectedClaimIndex'),
              initialTags: tda.factsToFind,
              labelText: l10n.scaleFactsToFindLabel,
              helperText: l10n.scaleFactsToFindHelper,
              onChanged: (tags) =>
                  _updateActiveTda((t) => t.copyWith(factsToFind: tags)),
            ),
            AppSpacing.h12,
            TextFormField(
              key: ValueKey('logical_${tda.tdaId}_$_selectedClaimIndex'),
              initialValue: tda.logicalExpression,
              decoration: InputDecoration(
                labelText: l10n.scaleLogicalExpressionLabel,
                helperText: l10n.scaleLogicalExpressionHelper,
                border: const OutlineInputBorder(),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 8,
                ),
              ),
              onChanged: (val) => _updateActiveTda(
                (t) => t.copyWith(
                  logicalExpression: val.trim().isEmpty ? null : val.trim(),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCard2Reasoning(TDAAssertion tda, AppLocalizations l10n) {
    return _buildCard(
      title: l10n.scaleSectionReasoning,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.scaleAcceptanceCriteriaLabel,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          AppSpacing.h8,
          DynamicItemListEditor(
            key: ValueKey('criteria_${tda.tdaId}_$_selectedClaimIndex'),
            items: tda.acceptanceCriteria.map((a) => a.instruction).toList(),
            addButtonLabel: l10n.scaleAddCriterionBtn,
            placeholder: l10n.scaleCriterionPlaceholder,
            onChanged: (items) {
              final parsed = items
                  .map(
                    (i) => AcceptanceCriterion(
                      instruction: i,
                      requiresContextualOverride: false,
                    ),
                  )
                  .toList();
              _updateActiveTda((t) => t.copyWith(acceptanceCriteria: parsed));
            },
          ),
          AppSpacing.h16,
          Text(
            l10n.scaleAntiPatternsLabel,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          AppSpacing.h8,
          DynamicItemListEditor(
            key: ValueKey('antipatterns_${tda.tdaId}_$_selectedClaimIndex'),
            items: tda.antiPatterns.map((a) => a.pattern).toList(),
            addButtonLabel: l10n.scaleAddAntiPatternBtn,
            placeholder: l10n.scaleAntiPatternPlaceholder,
            onChanged: (items) {
              final parsed = items.map((i) => AntiPattern(pattern: i)).toList();
              _updateActiveTda((t) => t.copyWith(antiPatterns: parsed));
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCard3Contrastive(TDAAssertion tda, AppLocalizations l10n) {
    return _buildCard(
      title: l10n.scaleSectionContrastive,
      child: ContrastivePairEditor(
        key: ValueKey('contrastive_${tda.tdaId}_$_selectedClaimIndex'),
        initialValue: tda.contrastiveExample,
        onChanged: (pair) =>
            _updateActiveTda((t) => t.copyWith(contrastiveExample: pair)),
      ),
    );
  }

  Widget _buildCard4Anchors(TDAAssertion tda, AppLocalizations l10n) {
    final theme = Theme.of(context);
    return _buildCard(
      title: l10n.scaleSectionAnchors,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TagChipInput(
            key: _tagChipKey,
            initialTags: tda.syntacticAnchors,
            labelText: l10n.scaleSyntacticAnchorsLabel,
            helperText: l10n.scaleSyntacticAnchorsHelper,
            hintText: l10n.scaleAnchorChipPlaceholder,
            onChanged: (tags) =>
                _updateActiveTda((t) => t.copyWith(syntacticAnchors: tags)),
          ),
          AppSpacing.h8,
          Text(
            l10n.scaleSystemLanguageNotice,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCard5Aggregation(TDAAssertion tda, AppLocalizations l10n) {
    final theme = Theme.of(context);
    return _buildCard(
      title: l10n.scaleSectionAggregation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SwitchListTile(
            title: Text(l10n.scaleInverseLabel),
            subtitle: Text(l10n.scaleInverseTooltip),
            value: tda.inverseEvidence,
            onChanged: (val) {
              _updateActiveTda(
                (t) => t.copyWith(
                  inverseEvidence: val,
                  aggregationMode: val
                      ? AggregationMode.exists
                      : t.aggregationMode,
                ),
              );
            },
          ),
          if (tda.inverseEvidence)
            Container(
              margin: const EdgeInsets.only(top: 8, bottom: 12),
              padding: AppSpacing.p12,
              decoration: BoxDecoration(
                color: theme.colorScheme.errorContainer,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: theme.colorScheme.error.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    color: theme.colorScheme.onErrorContainer,
                    size: 24,
                  ),
                  AppSpacing.w8,
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.scaleInverseEvidenceWarningTitle,
                          style: theme.textTheme.titleSmall?.copyWith(
                            color: theme.colorScheme.onErrorContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        AppSpacing.h4,
                        Text(
                          l10n.scaleInverseEvidenceWarningDesc,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onErrorContainer,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          AppSpacing.h8,
          DropdownButtonFormField<AggregationMode>(
            key: ValueKey('agg_${tda.tdaId}_$_selectedClaimIndex'),
            isExpanded: true,
            initialValue: tda.aggregationMode,
            decoration: InputDecoration(
              labelText: l10n.scaleAggregationModeLabel,
              helperText: l10n.scaleAggregationModeHelper,
              border: const OutlineInputBorder(),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
            ),
            items: AggregationMode.values.map((mode) {
              final isDisabled =
                  tda.inverseEvidence && mode == AggregationMode.allMustComply;
              return DropdownMenuItem<AggregationMode>(
                value: mode,
                enabled: !isDisabled,
                child: Text(
                  mode == AggregationMode.exists
                      ? l10n.scaleAggExists
                      : l10n.scaleAggAllMustComply,
                  style: isDisabled
                      ? TextStyle(color: theme.disabledColor)
                      : null,
                ),
              );
            }).toList(),
            onChanged: (mode) {
              if (mode != null)
                _updateActiveTda((t) => t.copyWith(aggregationMode: mode));
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDetailCanvas(AppLocalizations l10n) {
    if (_editableScale.claims.isEmpty) {
      return Center(
        child: Padding(
          padding: AppSpacing.p24,
          child: OutlinedButton.icon(
            onPressed: _addClaim,
            icon: const Icon(Icons.add),
            label: Text(l10n.matrixAddCriterion),
          ),
        ),
      );
    }

    final claim = _editableScale.claims[_selectedClaimIndex];
    final tda = claim.tdaAssertions.isNotEmpty
        ? claim.tdaAssertions[0]
        : TDAAssertion.create(
            conceptDescription: '',
            inverseEvidence: false,
            aggregationMode: AggregationMode.exists,
          );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        I18nTextField(
          label: l10n.scaleGradeNameLabel,
          initialData: _editableScale.name,
          onChanged: (val) => _editableScale = _editableScale.copyWith(
            name: val.isEmpty ? null : val,
          ),
          leadingInput: SizedBox(
            width: 180,
            child: TextFormField(
              initialValue: _editableScale.score.toString(),
              decoration: InputDecoration(
                labelText: l10n.scaleGradeScoreLabel,
                border: const OutlineInputBorder(),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surface,
              ),
              keyboardType: TextInputType.number,
              onChanged: (val) {
                final parsed = int.tryParse(val);
                if (parsed != null) {
                  _editableScale = _editableScale.copyWith(score: parsed);
                }
              },
            ),
          ),
          bottomInput: TextFormField(
            initialValue: _editableScale.aiLabel,
            decoration: InputDecoration(
              labelText: l10n.scaleGradeAiLabel,
              border: const OutlineInputBorder(),
              filled: true,
              fillColor: Theme.of(context).colorScheme.surface,
            ),
            onChanged: (val) =>
                _editableScale = _editableScale.copyWith(aiLabel: val.trim()),
          ),
        ),
        AppSpacing.h16,
        I18nTextField(
          key: ValueKey('claimlabel_${tda.tdaId}_$_selectedClaimIndex'),
          label: l10n.scaleClaimTranslationLabel,
          initialData: claim.label,
          onChanged: (val) {
            final claims = List<MatrixClaim>.from(_editableScale.claims);
            claims[_selectedClaimIndex] = claim.copyWith(label: val);
            setState(() {
              _editableScale = _editableScale.copyWith(claims: claims);
            });
          },
        ),
        AppSpacing.h16,
        _buildCard1Core(tda, l10n),
        _buildCard2Reasoning(tda, l10n),
        _buildCard3Contrastive(tda, l10n),
        _buildCard4Anchors(tda, l10n),
        _buildCard5Aggregation(tda, l10n),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final claims = _editableScale.claims;

    return Shortcuts(
      shortcuts: <ShortcutActivator, Intent>{
        LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.keyS):
            const _SaveIntent(),
        LogicalKeySet(LogicalKeyboardKey.meta, LogicalKeyboardKey.keyS):
            const _SaveIntent(),
        const SingleActivator(LogicalKeyboardKey.escape):
            const _DismissIntent(),
      },
      child: Actions(
        actions: <Type, Action<Intent>>{
          _SaveIntent: CallbackAction<_SaveIntent>(
            onInvoke: (_) {
              _save();
              return null;
            },
          ),
          _DismissIntent: CallbackAction<_DismissIntent>(
            onInvoke: (_) {
              _handleDismiss();
              return null;
            },
          ),
        },
        child: PopScope(
          canPop: false,
          onPopInvokedWithResult: (didPop, result) {
            if (!didPop) _handleDismiss();
          },
          child: Dialog(
            insetPadding: AppSpacing.p16,
            child: ConstrainedBox(
              constraints: const BoxConstraints(
                minWidth: 480,
                maxWidth: 1400,
                minHeight: 600,
              ),
              child: Scaffold(
                appBar: AppBar(
                  title: Text(l10n.editDimension),
                  leading: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: _handleDismiss,
                  ),
                  actions: [
                    IconButton(
                      icon: _isLoadingPreview
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.code),
                      tooltip: l10n.previewScalePromptTooltip,
                      onPressed: _isLoadingPreview ? null : _previewScalePrompt,
                    ),
                    AppSpacing.w8,
                    FilledButton.icon(
                      onPressed: _save,
                      icon: const Icon(Icons.check),
                      label: Text(l10n.save),
                    ),
                    AppSpacing.w8,
                  ],
                ),
                body: Form(
                  key: _formKey,
                  child: Padding(
                    padding: AppSpacing.p16,
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        final isWide = constraints.maxWidth >= 900;
                        if (isWide) {
                          return Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SizedBox(
                                width: 240,
                                child: Column(
                                  children: [
                                    Expanded(
                                      child: ListView.separated(
                                        itemCount: claims.length,
                                        separatorBuilder: (_, __) =>
                                            AppSpacing.h8,
                                        itemBuilder: (context, idx) {
                                          final isSelected =
                                              _selectedClaimIndex == idx;
                                          return InkWell(
                                            onTap: () => setState(
                                              () => _selectedClaimIndex = idx,
                                            ),
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                            child: Container(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    horizontal: 12,
                                                    vertical: 10,
                                                  ),
                                              decoration: BoxDecoration(
                                                color: isSelected
                                                    ? theme
                                                          .colorScheme
                                                          .primaryContainer
                                                    : theme
                                                          .colorScheme
                                                          .surfaceContainerLow,
                                                borderRadius:
                                                    BorderRadius.circular(12),
                                                border: Border.all(
                                                  color: isSelected
                                                      ? theme
                                                            .colorScheme
                                                            .primary
                                                      : theme
                                                            .colorScheme
                                                            .outlineVariant,
                                                ),
                                              ),
                                              child: Row(
                                                children: [
                                                  Expanded(
                                                    child: Text(
                                                      l10n.scaleClaimIndexTitle(
                                                        idx + 1,
                                                      ),
                                                      style: theme
                                                          .textTheme
                                                          .labelLarge
                                                          ?.copyWith(
                                                            fontWeight:
                                                                isSelected
                                                                ? FontWeight
                                                                      .bold
                                                                : FontWeight
                                                                      .normal,
                                                            color: isSelected
                                                                ? theme
                                                                      .colorScheme
                                                                      .onPrimaryContainer
                                                                : theme
                                                                      .colorScheme
                                                                      .onSurface,
                                                          ),
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                    ),
                                                  ),
                                                  if (claims.length > 1)
                                                    IconButton(
                                                      icon: const Icon(
                                                        Icons.delete,
                                                        size: 18,
                                                      ),
                                                      color: theme
                                                          .colorScheme
                                                          .error,
                                                      tooltip: l10n
                                                          .scaleRemoveClaimTooltip,
                                                      onPressed: () =>
                                                          _removeClaim(idx),
                                                    ),
                                                ],
                                              ),
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                    AppSpacing.h8,
                                    OutlinedButton.icon(
                                      onPressed: _addClaim,
                                      icon: const Icon(Icons.add),
                                      label: Text(l10n.matrixAddCriterion),
                                    ),
                                  ],
                                ),
                              ),
                              AppSpacing.w16,
                              Expanded(
                                child: SingleChildScrollView(
                                  controller: _scrollController,
                                  child: _buildDetailCanvas(l10n),
                                ),
                              ),
                            ],
                          );
                        } else {
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: Row(
                                  children: [
                                    for (
                                      int idx = 0;
                                      idx < claims.length;
                                      idx++
                                    ) ...[
                                      ChoiceChip(
                                        label: Text(
                                          l10n.scaleClaimIndexTitle(idx + 1),
                                        ),
                                        selected: _selectedClaimIndex == idx,
                                        onSelected: (sel) {
                                          if (sel)
                                            setState(
                                              () => _selectedClaimIndex = idx,
                                            );
                                        },
                                      ),
                                      AppSpacing.w8,
                                    ],
                                    ActionChip(
                                      avatar: const Icon(Icons.add, size: 16),
                                      label: Text(l10n.matrixAddCriterion),
                                      onPressed: _addClaim,
                                    ),
                                  ],
                                ),
                              ),
                              AppSpacing.h16,
                              Expanded(
                                child: SingleChildScrollView(
                                  controller: _scrollController,
                                  child: _buildDetailCanvas(l10n),
                                ),
                              ),
                            ],
                          );
                        }
                      },
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
