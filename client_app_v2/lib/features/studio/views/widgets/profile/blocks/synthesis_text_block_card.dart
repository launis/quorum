import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

/// Config card for synthesisTextBlock supporting pipeline block selection and on-the-fly synthesis.
class SynthesisTextBlockCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final AsyncValue<List<PromptBlock>> promptBlocksState;
  final Widget? dragHandle;

  const SynthesisTextBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    required this.promptBlocksState,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.synthesisTextBlock,
    );
    final currentSynthesis = payload.synthesis ?? const SynthesisConfigDTO();
    final blocksList = promptBlocksState.value ?? [];

    return BaseBlockCard(
      blockType: TargetBlockType.synthesisTextBlock,
      title: 'Synthesis & Narrative Text',
      subtitle:
          'Executive synthesis narratives, LLM summaries, and section preambles',
      icon: Icons.psychology_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.synthesisTextBlock)) {
            newOrder.add(TargetBlockType.synthesisTextBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.synthesisTextBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Pipeline Synthesis Block Binding',
            style: Theme.of(
              context,
            ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.s4),
          DropdownButtonFormField<String?>(
            initialValue: currentSynthesis.synthesisBlockId,
            isExpanded: true,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: 'Synthesis Prompt Block (Pipeline Way)',
              helperText:
                  'Select an existing prompt block configured in the workflow',
            ),
            items: [
              const DropdownMenuItem<String?>(
                value: null,
                child: Text('None (Use On-the-Fly configuration below)'),
              ),
              ...blocksList.map((block) {
                final locale = Localizations.localeOf(context).languageCode;
                final label =
                    block.label.translations[locale] ??
                    block.label.translations['en'] ??
                    block.slug;
                return DropdownMenuItem<String?>(
                  value: block.id,
                  child: Text(
                    '$label (${block.id})',
                    overflow: TextOverflow.ellipsis,
                  ),
                );
              }),
            ],
            onChanged: (val) {
              updatePayload(
                payload.copyWith(
                  synthesis: currentSynthesis.copyWith(synthesisBlockId: val),
                ),
              );
            },
          ),
          const SizedBox(height: AppSpacing.s16),
          I18nTextField(
            label: 'Tone Instruction (Voice & Audience)',
            initialData: payload.toneInstruction,
            onChanged: (val) {
              updatePayload(
                payload.copyWith(
                  toneInstruction: val.translations.isEmpty ? null : val,
                ),
              );
            },
          ),
          const SizedBox(height: AppSpacing.s12),
          I18nTextField(
            label: 'Section Preamble Text',
            initialData: currentSynthesis.preambleText,
            onChanged: (val) {
              updatePayload(
                payload.copyWith(
                  synthesis: currentSynthesis.copyWith(
                    preambleText: val.translations.isEmpty ? null : val,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
