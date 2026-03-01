import 'package:client_app/features/orchestration/presentation/providers/reflection_form_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class GuidedReflectionForm extends ConsumerWidget {
  const GuidedReflectionForm({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stateAsync = ref.watch(reflectionFormControllerProvider);
    final state = stateAsync.value ?? const ReflectionFormState();

    if (state.inputMode != ReflectionInputMode.guided) {
      if (state.inputMode == ReflectionInputMode.text) {
        return _buildFreeTextForm(context, ref, state.freeText);
      }
      return const SizedBox.shrink(); // File upload handled elsewhere
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildSection(
          context,
          ref,
          title: l10n.q1GoalTitle,
          hint: l10n.q1GoalHint,
          value: state.q1Goal,
          icon: Icons.flag,
          onChanged: (val) => ref.read(reflectionFormControllerProvider.notifier).setQ1Goal(val),
        ),
        const SizedBox(height: 16),
        _buildSection(
          context,
          ref,
          title: l10n.q2FalsificationTitle,
          hint: l10n.q2FalsificationHint,
          value: state.q2Falsification,
          icon: Icons.bug_report,
          onChanged: (val) => ref.read(reflectionFormControllerProvider.notifier).setQ2Falsification(val),
        ),
        const SizedBox(height: 16),
        _buildSection(
          context,
          ref,
          title: l10n.q3SynthesisTitle,
          hint: l10n.q3SynthesisHint,
          value: state.q3Synthesis,
          icon: Icons.create,
          onChanged: (val) => ref.read(reflectionFormControllerProvider.notifier).setQ3Synthesis(val),
        ),
        const SizedBox(height: 16),
        _buildSection(
          context,
          ref,
          title: l10n.q4ArgumentationTitle,
          hint: l10n.q4ArgumentationHint,
          value: state.q4Argumentation,
          icon: Icons.gavel,
          onChanged: (val) => ref.read(reflectionFormControllerProvider.notifier).setQ4Argumentation(val),
        ),
      ],
    );
  }

  Widget _buildFreeTextForm(BuildContext context, WidgetRef ref, String initialValue) {
    final l10n = AppLocalizations.of(context)!;
    return TextFormField(
      initialValue: initialValue,
      minLines: 5,
      maxLines: 15,
      decoration: InputDecoration(
        labelText: l10n.pasteTextLabel,
        alignLabelWithHint: true,
        border: const OutlineInputBorder(),
      ),
      onChanged: (val) => ref.read(reflectionFormControllerProvider.notifier).setFreeText(val),
      validator: (value) {
        if (value == null || value.trim().length < 100) {
          return l10n.minCharsRequired;
        }
        return null;
      },
    );
  }

  Widget _buildSection(
    BuildContext context,
    WidgetRef ref, {
    required String title,
    required String hint,
    required String value,
    required IconData icon,
    required Function(String) onChanged,
  }) {
    final colorScheme = Theme.of(context).colorScheme;
    final length = value.trim().length;
    final isWarning = length > 0 && length < 100;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: colorScheme.primary),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          hint,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: value,
          minLines: 3,
          maxLines: 8,
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            alignLabelWithHint: true,
          ),
          onChanged: onChanged,
          validator: (val) {
            final len = val?.trim().length ?? 0;
            if (len == 0) {
              return AppLocalizations.of(context)!.fieldRequired;
            }
            if (len < 100) {
              return AppLocalizations.of(context)!.charsRemainingLength(len);
            }
            return null;
          },
        ),
        if (isWarning)
          Padding(
            padding: const EdgeInsets.only(top: 4.0),
            child: Text(
              AppLocalizations.of(context)!.expandArgumentationHint(length),
              style: TextStyle(color: colorScheme.error, fontSize: 12),
            ),
          )
      ],
    );
  }
}
