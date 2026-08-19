import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Section widget for block-level and workflow-level XAI extension toggles.
class ProfileXaiExtensionsSection extends ConsumerWidget {
  final String id;
  const ProfileXaiExtensionsSection({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) return const SizedBox.shrink();

    final availableExtensionsState = ref.watch(
      workflowAvailableExtensionsProvider(payload.workflowId),
    );

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        InputDecorator(
          decoration: InputDecoration(
            labelText: l10n.blockLevelExtensionsLabel,
            isDense: true,
            border: const OutlineInputBorder(),
          ),
          child: switch (availableExtensionsState) {
            AsyncData(value: final availableExtensions) => Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final ext in XaiExtensionType.values)
                  if (availableExtensions.contains(ext.backendValue) &&
                      ext != XaiExtensionType.varianceValidation &&
                      ext != XaiExtensionType.authenticityEvaluation)
                    CheckboxListTile(
                      title: Text(_xaiLabel(ext, l10n)),
                      value: payload.visibleBlockExtensions.contains(ext),
                      onChanged: (val) {
                        final updatedList = List<XaiExtensionType>.from(
                          payload.visibleBlockExtensions,
                        );
                        if (val == true) {
                          updatedList.add(ext);
                        } else {
                          updatedList.remove(ext);
                        }
                        updatePayload(
                          payload.copyWith(visibleBlockExtensions: updatedList),
                        );
                      },
                      controlAffinity: ListTileControlAffinity.leading,
                      dense: true,
                    ),
              ],
            ),
            AsyncLoading() => const Center(child: CircularProgressIndicator()),
            AsyncError(:final error) => Text(error.toString()),
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
                  final title = switch (ext) {
                    XaiExtensionType.varianceValidation =>
                      l10n.xaiVarianceValidationTitle,
                    XaiExtensionType.authenticityEvaluation =>
                      l10n.xaiAuthenticityEvaluationTitle,
                    _ => ext.name,
                  };
                  return CheckboxListTile(
                    title: Text(title),
                    value: payload.visibleWorkflowExtensions.contains(ext),
                    onChanged: (val) {
                      final updatedList = List<XaiExtensionType>.from(
                        payload.visibleWorkflowExtensions,
                      );
                      if (val == true) {
                        updatedList.add(ext);
                      } else {
                        updatedList.remove(ext);
                      }
                      updatePayload(
                        payload.copyWith(
                          visibleWorkflowExtensions: updatedList,
                        ),
                      );
                    },
                    controlAffinity: ListTileControlAffinity.leading,
                    dense: true,
                  );
                }).toList(),
          ),
        ),
      ],
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
