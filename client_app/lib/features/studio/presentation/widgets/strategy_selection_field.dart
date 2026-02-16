
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/admin/presentation/providers/model_registry_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class StrategySelectionField extends HookConsumerWidget {
  final String? currentStrategy;
  final ValueChanged<String?> onChanged;

  const StrategySelectionField({
    super.key,
    required this.currentStrategy,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final registryState = ref.watch(modelRegistryControllerProvider);

    return registryState.when(
      loading: () => const LinearProgressIndicator(),
      error: (err, _) => Text('Error loading strategies: $err', style: TextStyle(color: Theme.of(context).colorScheme.error)),
      data: (state) {
        // Collect strategies from providers list
        // We assume 'id' in provider config acts as the strategy name for now, 
        // or we might need a distinct list. Based on backend, strategy maps to a config.
        final strategies = state.providers.map((p) => p.id).toSet().toList()..sort();

        return DropdownButtonFormField<String>(
          value: strategies.contains(currentStrategy) ? currentStrategy : null,
          decoration: InputDecoration(
            labelText: l10n.modelStrategyLabel ?? 'Model Strategy', // Fallback if key missing
            border: const OutlineInputBorder(),
            isDense: true,
            helperText: l10n.modelStrategyHelper ?? 'Select the AI model strategy for this step.',
          ),
          items: [
             const DropdownMenuItem(value: null, child: Text('Default (Inherit)')),
             ...strategies.map((s) {
               return DropdownMenuItem(
                 value: s,
                 child: Text(s),
               );
             }),
          ],
          onChanged: onChanged,
        );
      },
    );
  }
}
