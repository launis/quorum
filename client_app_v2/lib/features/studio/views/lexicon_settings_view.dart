import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/controllers/lexicon_controller.dart';
import 'package:client_app/features/studio/models/performative_lexicon.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/logging/logger_service.dart';

class LexiconSettingsView extends HookConsumerWidget {
  const LexiconSettingsView({super.key});

  Future<int> _addPhrases(
    WidgetRef ref,
    SystemConfigPerformativeLexicons config,
    String lang,
    List<String> newPhrases,
  ) async {
    if (newPhrases.isEmpty) return 0;

    final lexiconConfigs = config.lexiconConfigs;
    final currentConfig =
        lexiconConfigs[lang] ??
        LexiconConfigPayload(
          languageCode: lang,
          languageName: lang.toUpperCase(),
        );

    final updatedWords = List<String>.from(currentConfig.words);
    int added = 0;
    for (final phrase in newPhrases) {
      final norm = phrase.trim().toLowerCase();
      if (norm.isNotEmpty && !updatedWords.contains(norm)) {
        updatedWords.add(norm);
        added++;
      }
    }

    updatedWords.sort();

    bool changed = added > 0;
    if (!changed) {
      if (currentConfig.words.length != updatedWords.length) {
        changed = true;
      } else {
        for (int i = 0; i < currentConfig.words.length; i++) {
          if (currentConfig.words[i] != updatedWords[i]) {
            changed = true;
            break;
          }
        }
      }
    }

    if (!changed) return 0;

    final updatedConfigPayload = currentConfig.copyWith(words: updatedWords);
    final updatedLexiconConfigs = Map<String, LexiconConfigPayload>.from(
      lexiconConfigs,
    );
    updatedLexiconConfigs[lang] = updatedConfigPayload;

    final newConfig = config.copyWith(lexiconConfigs: updatedLexiconConfigs);
    await ref.read(lexiconControllerProvider.notifier).saveLexicons(newConfig);
    return added;
  }

  Future<void> _discoverPhrases(
    BuildContext context,
    WidgetRef ref,
    String lang,
    SystemConfigPerformativeLexicons config,
    AppLocalizations l10n,
  ) async {
    try {
      final phrases = await ref
          .read(lexiconControllerProvider.notifier)
          .discoverPhrases(lang);

      if (context.mounted) {
        if (phrases.isNotEmpty) {
          final addedCount = await _addPhrases(ref, config, lang, phrases);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                l10n.lexiconDiscoveredSuccess(addedCount, phrases.length),
              ),
            ),
          );
        } else {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.lexiconDiscoveredEmpty)));
        }
      }
    } catch (e, st) {
      if (context.mounted) {
        ref
            .read(loggerServiceProvider)
            .error('LexiconSettingsView', 'Discover failed', e, st);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  Future<void> _translatePhrases(
    BuildContext context,
    WidgetRef ref,
    String lang,
    SystemConfigPerformativeLexicons config,
    AppLocalizations l10n,
  ) async {
    try {
      final phrases = await ref
          .read(lexiconControllerProvider.notifier)
          .translatePhrases(lang);

      if (context.mounted) {
        if (phrases.isNotEmpty) {
          final addedCount = await _addPhrases(ref, config, lang, phrases);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.lexiconTranslatedSuccess(addedCount))),
          );
        } else {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.lexiconTranslatedEmpty)));
        }
      }
    } catch (e, st) {
      if (context.mounted) {
        ref
            .read(loggerServiceProvider)
            .error('LexiconSettingsView', 'Translate failed', e, st);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(lexiconControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    final selectedLangState = useState<String>('en');
    final selectedLang = selectedLangState.value;

    final textController = useTextEditingController();

    return switch (state) {
      AsyncLoading() => const Center(child: CircularProgressIndicator()),
      AsyncError(:final error) => ErrorView(
        error: error,
        onRetry: () =>
            ref.read(lexiconControllerProvider.notifier).fetchLexicons(),
      ),
      AsyncData(value: final config) => Builder(
        builder: (context) {
          final lexiconConfigs = config.lexiconConfigs;
          final currentConfig =
              lexiconConfigs[selectedLang] ??
              LexiconConfigPayload(
                languageCode: selectedLang,
                languageName: selectedLang.toUpperCase(),
              );

          return Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.lexiconTitle,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Row(
                      children: [
                        DropdownButton<String>(
                          value: selectedLang,
                          items: [
                            DropdownMenuItem(
                              value: 'en',
                              child: Text(l10n.lexiconLangEn),
                            ),
                            DropdownMenuItem(
                              value: 'fi',
                              child: Text(l10n.lexiconLangFi),
                            ),
                          ],
                          onChanged: (val) {
                            if (val != null) selectedLangState.value = val;
                          },
                        ),
                        AppSpacing.w16,
                        FilledButton.icon(
                          onPressed: () => _discoverPhrases(
                            context,
                            ref,
                            selectedLang,
                            config,
                            l10n,
                          ),
                          icon: const Icon(Icons.search),
                          label: Text(l10n.lexiconDiscoverNew),
                        ),
                        AppSpacing.w8,
                        if (selectedLang != 'en')
                          FilledButton.icon(
                            onPressed: () => _translatePhrases(
                              context,
                              ref,
                              selectedLang,
                              config,
                              l10n,
                            ),
                            icon: const Icon(Icons.translate),
                            label: Text(l10n.lexiconTranslateMissing),
                          ),
                        AppSpacing.w8,
                        FilledButton.icon(
                          onPressed: () {
                            ref
                                .read(lexiconControllerProvider.notifier)
                                .saveLexicons(config);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(l10n.studioChangesSaved)),
                            );
                          },
                          icon: const Icon(Icons.save),
                          label: Text(l10n.save),
                        ),
                      ],
                    ),
                  ],
                ),
                AppSpacing.h16,
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: textController,
                        decoration: InputDecoration(
                          labelText: l10n.lexiconAddPlaceholder,
                          border: const OutlineInputBorder(),
                          isDense: true,
                        ),
                        onSubmitted: (value) async {
                          if (value.trim().isNotEmpty) {
                            await _addPhrases(ref, config, selectedLang, [
                              value,
                            ]);
                            textController.clear();
                          }
                        },
                      ),
                    ),
                    AppSpacing.w8,
                    FilledButton(
                      onPressed: () async {
                        if (textController.text.trim().isNotEmpty) {
                          await _addPhrases(ref, config, selectedLang, [
                            textController.text,
                          ]);
                          textController.clear();
                        }
                      },
                      child: Text(l10n.lexiconAddButton),
                    ),
                  ],
                ),
                AppSpacing.h16,
                Expanded(
                  child: Card(
                    child: Builder(
                      builder: (context) {
                        final displayWords = List<String>.from(
                          currentConfig.words,
                        )..sort();
                        return ListView.builder(
                          itemCount: displayWords.length,
                          itemBuilder: (context, index) {
                            final word = displayWords[index];
                            return ListTile(
                              leading: const Icon(Icons.abc),
                              title: Text(word),
                              trailing: IconButton(
                                icon: const Icon(Icons.delete),
                                onPressed: () {
                                  // Local mutation pattern
                                  final updatedWords = List<String>.from(
                                    currentConfig.words,
                                  )..remove(word);
                                  final updatedConfigPayload = currentConfig
                                      .copyWith(words: updatedWords);
                                  final updatedLexiconConfigs =
                                      Map<String, LexiconConfigPayload>.from(
                                        lexiconConfigs,
                                      );
                                  updatedLexiconConfigs[selectedLang] =
                                      updatedConfigPayload;

                                  final newConfig = config.copyWith(
                                    lexiconConfigs: updatedLexiconConfigs,
                                  );
                                  ref
                                      .read(lexiconControllerProvider.notifier)
                                      .saveLexicons(newConfig);
                                },
                              ),
                            );
                          },
                        );
                      },
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    };
  }
}
