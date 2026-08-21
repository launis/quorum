import 'package:flutter/material.dart';
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
            l10n.blockLevelExtensionsLabel,
            style: Theme.of(
              context,
            ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.s8),
          switch (availableExtensionsState) {
            AsyncData(value: final availableExtensions) => Wrap(
              spacing: AppSpacing.s8,
              runSpacing: AppSpacing.s4,
              children: [
                for (final ext in XaiExtensionType.values)
                  if (availableExtensions.contains(ext.backendValue) &&
                      ext != XaiExtensionType.varianceValidation &&
                      ext != XaiExtensionType.authenticityEvaluation)
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
