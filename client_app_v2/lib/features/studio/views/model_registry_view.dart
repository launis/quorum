import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';

/// Admin Studio View for managing the Model Registry (SystemConfig).
/// Uses raw `Map<String, dynamic>` to adhere to V2 De-Generator principles.
class ModelRegistryView extends ConsumerStatefulWidget {
  const ModelRegistryView({super.key});

  @override
  ConsumerState<ModelRegistryView> createState() => _ModelRegistryViewState();
}

class _ModelRegistryViewState extends ConsumerState<ModelRegistryView> {
  final _formKey = GlobalKey<FormState>();

  /// Working copy of the data. Initialized in build when state data arrives.
  Map<String, dynamic>? _editableState;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final state = ref.watch(modelRegistryControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.modelRegistryTitle),
        actions: [
          if (state.hasValue && !state.isLoading)
            FilledButton.icon(
              icon: const Icon(Icons.save),
              label: Text(l10n.studioSaveButton),
              onPressed: _saveRegistry,
            ),
          const SizedBox(width: 16),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (data) {
          // Initialize working copy if not already done. Map.from enables deep-ish copy.
          _editableState ??= _deepCopy(data);

          return Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                _buildSystemAttributes(l10n, _editableState!),
                const SizedBox(height: 24),
                _buildModelsSection(l10n, _editableState!),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSystemAttributes(
    AppLocalizations l10n,
    Map<String, dynamic> data,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.systemMetaTitle,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: data['id']?.toString(),
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true,
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data['type']?.toString(),
              decoration: InputDecoration(labelText: l10n.configTypeLabel),
              readOnly: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModelsSection(AppLocalizations l10n, Map<String, dynamic> data) {
    final models = data['models'] as Map<String, dynamic>? ?? {};

    // Group by provider for UI display
    final Map<String, Map<String, dynamic>> providerGroups = {};
    for (final entry in models.entries) {
      final modelId = entry.key;
      final attrs = entry.value;
      if (attrs is Map<String, dynamic>) {
        final provider = attrs['provider'] as String? ?? 'unknown';
        providerGroups.putIfAbsent(provider, () => {})[modelId] = attrs;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          l10n.providerSettings,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        if (models.isEmpty) Text(l10n.noModelsDefined),
        ...providerGroups.entries.map((providerEntry) {
          final providerName = providerEntry.key;
          final providerModels = providerEntry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 16.0),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text('${l10n.providerLabel}: $providerName'),
              children:
                  providerModels.entries.map((modelEntry) {
                    final modelId = modelEntry.key;
                    final fields = modelEntry.value as Map<String, dynamic>;

                    return Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${l10n.strategyLabel}: $modelId',
                            style: Theme.of(
                              context,
                            ).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildStringField(
                            fields,
                            'model_name',
                            l10n.modelNameLabel,
                          ),
                          _buildDoubleField(
                            fields,
                            'temperature',
                            l10n.temperatureLabel,
                          ),
                          _buildIntField(
                            fields,
                            'max_tokens',
                            l10n.maxTokensLabel,
                          ),
                          _buildStringField(
                            fields,
                            'parsing_mode',
                            l10n.parsingModeLabel,
                          ),
                          _buildDoubleField(fields, 'top_p', l10n.topPLabel),
                          _buildIntField(
                            fields,
                            'tpm_limit',
                            l10n.tpmLimitLabel,
                          ),
                          _buildIntField(
                            fields,
                            'rpm_limit',
                            l10n.rpmLimitLabel,
                          ),
                          _buildBoolField(
                            fields,
                            'supports_grounding',
                            l10n.supportsGroundingLabel,
                          ),
                          _buildBoolField(
                            fields,
                            'is_active',
                            l10n.isActiveLabel,
                          ),
                          const Divider(height: 32),
                        ],
                      ),
                    );
                  }).toList(),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStringField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '',
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onSaved: (val) => map[key] = val,
      ),
    );
  }

  Widget _buildDoubleField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '0.0',
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null; // Optional
          if (double.tryParse(val) == null) return 'Must be a number';
          return null;
        },
        onSaved: (val) {
          if (val != null && val.isNotEmpty) {
            map[key] = double.tryParse(val);
          }
        },
      ),
    );
  }

  Widget _buildIntField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '0',
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null;
          if (int.tryParse(val) == null) return 'Must be an integer';
          return null;
        },
        onSaved: (val) {
          if (val != null && val.isNotEmpty) {
            map[key] = int.tryParse(val);
          }
        },
      ),
    );
  }

  Widget _buildBoolField(Map<String, dynamic> map, String key, String label) {
    // Value could be null initially.
    final currentValue = map[key] as bool? ?? false;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: SwitchListTile(
        title: Text(label),
        value: currentValue,
        onChanged: (val) {
          setState(() {
            map[key] = val;
          });
        },
      ),
    );
  }

  Map<String, dynamic> _deepCopy(Map<String, dynamic> source) {
    // Simple deep copy for JSON-like Maps used in V2 De-Generator
    final copy = <String, dynamic>{};
    for (final entry in source.entries) {
      if (entry.value is Map<String, dynamic>) {
        copy[entry.key] = _deepCopy(entry.value as Map<String, dynamic>);
      } else {
        copy[entry.key] = entry.value;
      }
    }
    return copy;
  }

  Future<void> _saveRegistry() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();

      try {
        await ref
            .read(modelRegistryControllerProvider.notifier)
            .saveConfig(_editableState!);

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Model Registry saved successfully.')),
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Save failed: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }
}
