import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import '../providers/model_registry_controller.dart';
import '../../domain/models/model_registry.dart';

class ProviderConfigForm extends HookConsumerWidget {
  final LLMProviderConfig config;
  final Function(LLMProviderConfig) onSave;
  final bool isSaving;

  const ProviderConfigForm({
    super.key,
    required this.config,
    required this.onSave,
    this.isSaving = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unnecessary_non_null_assertion
    final l10n = AppLocalizations.of(context)!;

    // Controllers
    final providerCtrl = useTextEditingController(text: config.provider);
    final modelNameCtrl = useTextEditingController(text: config.modelName);
    final apiKeyCtrl = useTextEditingController(text: config.apiKey ?? '');
    final baseUrlCtrl = useTextEditingController(text: config.baseUrl ?? '');
    final tempCtrl = useTextEditingController(
      text: config.temperature.toString(),
    );
    final maxTokensCtrl = useTextEditingController(
      text: config.additionalParams['max_tokens']?.toString() ?? '',
    );
    final tpmCtrl = useTextEditingController(text: config.tpmLimit.toString());
    final rpmCtrl = useTextEditingController(text: config.rpmLimit.toString());
    final defMaxCtrl = useTextEditingController(
      text: config.defaultMaxTokens?.toString() ?? '',
    );
    final locationCtrl = useTextEditingController(
      text: config.vertexLocation ?? '',
    );
    final supportsGrounding = useState(config.supportsGrounding);
    final isActive = useState(config.isActive);

    // Watch options specific to provider for capabilities? 
    // For now, simple conditional checks based on string.
    final availableOptions = ref.watch(modelRegistryControllerProvider.select((s) => s.whenData((data) => data.availableOptions)));

    final formKey = useMemoized(() => GlobalKey<FormState>());

    return Form(
      key: formKey,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Provider Dropdown
          availableOptions.when(
            data: (options) {
              final providerList = options.keys.toSet();
              if (config.provider.isNotEmpty) {
                providerList.add(config.provider);
              }
              final sortedProviders = providerList.toList()..sort();

              return DropdownButtonFormField<String>(
                value: sortedProviders.contains(config.provider) ? config.provider : null,
                decoration: InputDecoration(
                  labelText: l10n.providerLabel,
                  border: const OutlineInputBorder(),
                  helperText: l10n.helperSelectProvider,
                ),
                items: sortedProviders.map((p) {
                  return DropdownMenuItem(
                    value: p,
                    child: Text(p),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    providerCtrl.text = value;
                  }
                },
                validator: (value) {
                  if (value == null || value.isEmpty) return l10n.fieldRequired;
                  return null;
                },
              );
            },
            loading: () => const LinearProgressIndicator(),
            error: (_, __) => Text(l10n.failedToLoad('options')),
          ),
          const SizedBox(height: 16),

          // Model Dropdown
          availableOptions.when(
            data: (options) {
              final currentProvider = providerCtrl.text.toLowerCase();
              // Try case-insensitive matching for keys, but options keys should be lower anyway from backend?
              // Models logic:
              // Backend returns dict[str, list[str]].
              // We should look up safely.
              
              // Find key safely
              final matchingKey = options.keys.firstWhere(
                (k) => k.toLowerCase() == currentProvider,
                orElse: () => currentProvider,
              );
              
              final fetchedModels = options[matchingKey] ?? [];
              final modelSet = fetchedModels.toSet();
              
              if (config.modelName.isNotEmpty) {
                modelSet.add(config.modelName);
              }
              final sortedModels = modelSet.toList()..sort();

              // If current provider has no models and we have no current value, this might be empty.
              // But we added config.modelName if not empty.
              
              return DropdownButtonFormField<String>(
                value: sortedModels.contains(config.modelName) ? config.modelName : null,
                decoration: InputDecoration(
                  labelText: l10n.modelNameLabel,
                  border: const OutlineInputBorder(),
                  helperText: l10n.helperSelectModel,
                ),
                items: sortedModels.map((m) {
                  return DropdownMenuItem(
                    value: m,
                    child: Text(m),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    modelNameCtrl.text = value;
                  }
                },
                validator: (value) {
                  if (value == null || value.isEmpty) return l10n.fieldRequired;
                  return null;
                },
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 16),

          TextFormField(
            controller: apiKeyCtrl,
            obscureText: true,
            decoration: InputDecoration(
              labelText: l10n.apiKeyLabel,
              border: const OutlineInputBorder(),
              helperText: l10n.helperApiKeyMasked,
            ),
          ),
          const SizedBox(height: 16),

          TextFormField(
            controller: baseUrlCtrl,
            decoration: InputDecoration(
              labelText: l10n.baseUrlLabel,
              border: const OutlineInputBorder(),
              helperText: l10n.helperOptionalOverride,
            ),
          ),
          const SizedBox(height: 16),

          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: tempCtrl,
                  decoration: InputDecoration(
                    labelText: l10n.temperatureLabel,
                    border: const OutlineInputBorder(),
                  ),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  validator: (value) {
                    if (value == null || value.isEmpty) return null;
                    final n = double.tryParse(value);
                    if (n == null) return l10n.errorMustBeNumber;
                    if (n < 0 || n > 2) return l10n.errorRangeTemperature;
                    return null;
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextFormField(
                  controller: maxTokensCtrl,
                  decoration: InputDecoration(
                    labelText: 'Max Tokens', // This is also hardcoded! Add to l10n? User didn't ask but "Max Tokens" is English.
                    border: const OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    if (value == null || value.isEmpty) return null;
                    if (int.tryParse(value) == null) return l10n.errorMustBeInteger;
                    return null;
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Rate Limits (TPM / RPM)
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: tpmCtrl,
                  decoration: const InputDecoration(
                    labelText: 'TPM Limit', 
                    border: OutlineInputBorder(),
                    helperText: '0 = Unlimited',
                  ),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                     if (value == null || value.isEmpty) return null;
                     if (int.tryParse(value) == null) return l10n.errorMustBeInteger;
                     return null;
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextFormField(
                  controller: rpmCtrl,
                  decoration: const InputDecoration(
                    labelText: 'RPM Limit', 
                    border: OutlineInputBorder(),
                    helperText: '0 = Unlimited',
                  ),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                     if (value == null || value.isEmpty) return null;
                     if (int.tryParse(value) == null) return l10n.errorMustBeInteger;
                     return null;
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Advanced / Provider Specific
          if (providerCtrl.text.toLowerCase().contains('vertex') || providerCtrl.text.toLowerCase().contains('google')) ...[
            TextFormField(
              controller: locationCtrl,
              decoration: const InputDecoration(
                labelText: 'Vertex Location',
                border: OutlineInputBorder(),
                helperText: 'e.g. europe-north1',
              ),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
               title: const Text('Supports Grounding'),
               subtitle: const Text('Enable Google Search integration'),
               value: supportsGrounding.value,
               onChanged: (v) => supportsGrounding.value = v,
            ),
          ],
          
          SwitchListTile(
            title: const Text('Is Active'),
            subtitle: const Text('Disable to prevent usage'),
            value: isActive.value,
            onChanged: (v) => isActive.value = v,
          ),
          
          const SizedBox(height: 24),

          ElevatedButton.icon(
            onPressed:
                isSaving
                    ? null
                    : () {
                      if (formKey.currentState!.validate()) {
                        // Merge max_tokens into additionalParams
                        final newParams = Map<String, dynamic>.from(config.additionalParams);
                        if (maxTokensCtrl.text.isNotEmpty) {
                          newParams['max_tokens'] = int.tryParse(maxTokensCtrl.text);
                        } else {
                          newParams.remove('max_tokens');
                        }

                          
                        final newConfig = config.copyWith(
                          provider: providerCtrl.text,
                          modelName: modelNameCtrl.text,
                          apiKey: apiKeyCtrl.text.isEmpty ? null : apiKeyCtrl.text,
                          baseUrl: baseUrlCtrl.text.isEmpty ? null : baseUrlCtrl.text,
                          temperature: double.tryParse(tempCtrl.text) ?? 0.7,
                          tpmLimit: int.tryParse(tpmCtrl.text) ?? 0,
                          rpmLimit: int.tryParse(rpmCtrl.text) ?? 0,
                          defaultMaxTokens: int.tryParse(defMaxCtrl.text), // Correctly map to field, not params
                          vertexLocation: locationCtrl.text.isEmpty ? null : locationCtrl.text,
                          supportsGrounding: supportsGrounding.value,
                          isActive: isActive.value,
                          additionalParams: newParams,
                        );
                        onSave(newConfig);
                      }
                    },
            icon:
                isSaving
                    ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                    : const Icon(Icons.save),
            label: Text(isSaving ? l10n.studioSaving : l10n.save),
          ),
        ],
      ),
    );
  }
}
