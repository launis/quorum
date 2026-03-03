import 'package:client_app/features/orchestration/presentation/providers/reflection_form_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ReflectionModeSelector extends ConsumerWidget {
  const ReflectionModeSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stateAsync = ref.watch(reflectionFormControllerProvider);
    final state = stateAsync.value ?? const ReflectionFormState();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            l10n.addReflectionIntent,
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 16.0),
          child: Text(
            l10n.reflectionDescription,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Row(
          children: [
            Expanded(
              child: _buildCard(
                context,
                ref,
                mode: ReflectionInputMode.guided,
                currentMode: state.inputMode,
                icon: Icons.lightbulb_outline,
                label: l10n.guidedReflectionRecommended,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildCard(
                context,
                ref,
                mode: ReflectionInputMode.text,
                currentMode: state.inputMode,
                icon: Icons.notes,
                label: '📝 ${l10n.pasteText}',
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildCard(
                context,
                ref,
                mode: ReflectionInputMode.file,
                currentMode: state.inputMode,
                icon: Icons.attach_file,
                label: '📎 ${l10n.uploadFile}',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCard(
    BuildContext context,
    WidgetRef ref, {
    required ReflectionInputMode mode,
    required ReflectionInputMode currentMode,
    required IconData icon,
    required String label,
  }) {
    final isSelected = mode == currentMode;
    final colorScheme = Theme.of(context).colorScheme;

    return InkWell(
      onTap: () {
        ref.read(reflectionFormControllerProvider.notifier).setMode(mode);
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          border: Border.all(
            color:
                isSelected ? colorScheme.primary : colorScheme.outlineVariant,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(8),
          color:
              isSelected
                  ? colorScheme.primaryContainer.withAlpha(50)
                  : colorScheme.surface,
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color:
                  isSelected
                      ? colorScheme.primary
                      : colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? colorScheme.primary : colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
