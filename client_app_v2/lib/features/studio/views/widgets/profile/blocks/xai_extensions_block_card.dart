import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Config card for groupedExtensionsBlock (XAI Output Extensions).
class XaiExtensionsBlockCard extends ConsumerWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const XaiExtensionsBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  // SSOT: Macro/Micro XAI Extension Categorization (frontend-only IA grouping)
  // Macro Synthesis (run-level): riskFlag, emotionalSentiment, theoryLink, confidence, justification
  // Micro Atom (observation-level): citation, coaching, falsification, remediationSteps, sourceId, missingContext, contextualOverride
  // When adding new XaiExtensionType values, explicitly assign to Macro or Micro group here.
  static const List<XaiExtensionType> _macroExtensions = [
    XaiExtensionType.riskFlag,
    XaiExtensionType.emotionalSentiment,
    XaiExtensionType.theoryLink,
    XaiExtensionType.confidence,
    XaiExtensionType.justification,
  ];

  static const List<XaiExtensionType> _microExtensions = [
    XaiExtensionType.citation,
    XaiExtensionType.coaching,
    XaiExtensionType.falsification,
    XaiExtensionType.remediationSteps,
    XaiExtensionType.sourceId,
    XaiExtensionType.missingContext,
    XaiExtensionType.contextualOverride,
  ];

  static List<XaiExtensionType> _filterExtensions(
    List<XaiExtensionType> extensions,
    List<String> availableExtensions,
  ) {
    return extensions
        .where(
          (ext) =>
              availableExtensions.contains(ext.backendValue) &&
              ext != XaiExtensionType.varianceValidation &&
              ext != XaiExtensionType.authenticityEvaluation,
        )
        .toList();
  }

  static Widget _buildExtensionGroup({
    required BuildContext context,
    required String title,
    required String subtitle,
    required List<XaiExtensionType> extensions,
    required OutputProfile payload,
    required void Function(OutputProfile) updatePayload,
    required AppLocalizations l10n,
  }) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.labelLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppSpacing.s4),
        Text(
          subtitle,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: AppSpacing.s8),
        Wrap(
          spacing: AppSpacing.s8,
          runSpacing: AppSpacing.s4,
          children: [
            for (final ext in extensions)
              FilterChip(
                label: Text(_xaiLabel(ext, l10n)),
                selected: payload.visibleBlockExtensions.contains(ext),
                onSelected: (selected) {
                  final updated = List<XaiExtensionType>.from(
                    payload.visibleBlockExtensions,
                  );
                  if (selected) {
                    updated.add(ext);
                  } else {
                    updated.remove(ext);
                  }
                  updatePayload(
                    payload.copyWith(visibleBlockExtensions: updated),
                  );
                },
              ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.groupedExtensionsBlock,
    );

    final availableExtensionsState = ref.watch(
      workflowAvailableExtensionsProvider(payload.workflowId),
    );

    final sliderMin = SystemUiConstraints.maxExtensionItemsSliderMin.value
        .toDouble();
    final sliderMax = SystemUiConstraints.maxExtensionItemsSliderMax.value
        .toDouble();
    final clampedSliderVal = payload.maxExtensionItems
        .clamp(
          SystemUiConstraints.maxExtensionItemsSliderMin.value,
          SystemUiConstraints.maxExtensionItemsSliderMax.value,
        )
        .toDouble();

    return BaseBlockCard(
      blockType: TargetBlockType.groupedExtensionsBlock,
      title: l10n.blockAiExtensionsTitle,
      subtitle: l10n.blockAiExtensionsSubtitle,
      icon: Icons.extension_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.groupedExtensionsBlock)) {
            newOrder.add(TargetBlockType.groupedExtensionsBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.groupedExtensionsBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.xaiHighlightsTitle,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.s12),
          switch (availableExtensionsState) {
            AsyncData(value: final availableExtensions) => Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_filterExtensions(
                  _macroExtensions,
                  availableExtensions,
                ).isNotEmpty) ...[
                  _buildExtensionGroup(
                    context: context,
                    title: l10n.xaiMacroSynthesisSectionTitle,
                    subtitle: l10n.xaiMacroSynthesisSectionSubtitle,
                    extensions: _filterExtensions(
                      _macroExtensions,
                      availableExtensions,
                    ),
                    payload: payload,
                    updatePayload: updatePayload,
                    l10n: l10n,
                  ),
                  const SizedBox(height: AppSpacing.s16),
                ],
                if (_filterExtensions(
                  _microExtensions,
                  availableExtensions,
                ).isNotEmpty)
                  _buildExtensionGroup(
                    context: context,
                    title: l10n.xaiMicroAtomSectionTitle,
                    subtitle: l10n.xaiMicroAtomSectionSubtitle,
                    extensions: _filterExtensions(
                      _microExtensions,
                      availableExtensions,
                    ),
                    payload: payload,
                    updatePayload: updatePayload,
                    l10n: l10n,
                  ),
              ],
            ),
            AsyncLoading() => const Center(
              child: Padding(
                padding: AppSpacing.p8,
                child: CircularProgressIndicator(),
              ),
            ),
            AsyncError(:final error) => Text(error.toString()),
          },
          const SizedBox(height: AppSpacing.s16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.maxExtensionItemsCount(payload.maxExtensionItems),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    Slider(
                      value: clampedSliderVal,
                      min: sliderMin,
                      max: sliderMax,
                      divisions: (sliderMax - sliderMin).toInt(),
                      label: payload.maxExtensionItems.toString(),
                      onChanged: (val) {
                        updatePayload(
                          payload.copyWith(maxExtensionItems: val.toInt()),
                        );
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(width: AppSpacing.s16),
              SizedBox(
                width: 80,
                child: TextFormField(
                  key: ValueKey('max_ext_${payload.maxExtensionItems}'),
                  initialValue: payload.maxExtensionItems.toString(),
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: l10n.maxFieldLabel,
                    border: const OutlineInputBorder(),
                    isDense: true,
                  ),
                  onChanged: (val) {
                    final parsed = int.tryParse(val);
                    if (parsed != null &&
                        parsed >=
                            SystemUiConstraints
                                .maxExtensionItemsSliderMin
                                .value &&
                        parsed <=
                            SystemUiConstraints
                                .maxExtensionItemsAbsoluteMax
                                .value) {
                      updatePayload(
                        payload.copyWith(maxExtensionItems: parsed),
                      );
                    }
                  },
                  validator: (val) {
                    if (val == null || val.isEmpty) return null;
                    final parsed = int.tryParse(val);
                    if (parsed == null ||
                        parsed <
                            SystemUiConstraints
                                .maxExtensionItemsSliderMin
                                .value ||
                        parsed >
                            SystemUiConstraints
                                .maxExtensionItemsAbsoluteMax
                                .value) {
                      return l10n.extensionItemsMustBeIntError;
                    }
                    return null;
                  },
                ),
              ),
            ],
          ),
          AppSpacing.h16,
          TextFormField(
            key: const Key('profile_xai_synthesis_directive_field'),
            initialValue: payload.xaiSynthesisDirective,
            maxLines: 4,
            decoration: InputDecoration(
              labelText: l10n.profileXaiSynthesisDirectiveLabel,
              border: const OutlineInputBorder(),
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  xaiSynthesisDirective: trimmed.isEmpty ? null : trimmed,
                ),
              );
            },
          ),
          AppSpacing.h16,
          TextFormField(
            key: const Key('profile_xai_length_constraint_field'),
            initialValue: payload.xaiLengthConstraint?.toString() ?? '',
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: l10n.profileXaiLengthLabel,
              hintText: l10n.profileXaiLengthHint,
              border: const OutlineInputBorder(),
              isDense: true,
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  xaiLengthConstraint: trimmed.isNotEmpty
                      ? int.tryParse(trimmed)
                      : null,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  static String _xaiLabel(XaiExtensionType ext, AppLocalizations l10n) {
    return switch (ext) {
      XaiExtensionType.citation => l10n.xaiSourceCitation,
      XaiExtensionType.justification => l10n.xaiJustification,
      XaiExtensionType.falsification => l10n.xaiDevilsAdvocate,
      XaiExtensionType.theoryLink => l10n.xaiTheoryLink,
      XaiExtensionType.riskFlag => l10n.xaiRiskFlag,
      XaiExtensionType.coaching => l10n.xaiCoachingTip,
      XaiExtensionType.missingContext => l10n.xaiMissingContext,
      XaiExtensionType.remediationSteps => l10n.xaiRemediation,
      XaiExtensionType.emotionalSentiment => l10n.xaiSentiment,
      XaiExtensionType.confidence => l10n.xaiConfidence,
      XaiExtensionType.sourceId => l10n.xaiSourceId,
      XaiExtensionType.contextualOverride => l10n.xaiContextualOverride,
      XaiExtensionType.varianceValidation => l10n.xaiVarianceValidationTitle,
      XaiExtensionType.authenticityEvaluation =>
        l10n.xaiAuthenticityEvaluationTitle,
    };
  }
}
