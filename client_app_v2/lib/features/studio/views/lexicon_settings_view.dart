import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/controllers/lexicon_controller.dart';
import 'package:client_app/features/studio/models/performative_lexicon.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

class LexiconSettingsView extends HookConsumerWidget {
  const LexiconSettingsView({super.key});

  Future<void> _addPhrases(
    WidgetRef ref,
    SystemConfigPerformativeLexicons config,
    String lang,
    List<String> newPhrases,
  ) async {
    if (newPhrases.isEmpty) return;

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

    if (added == 0) return;

    final updatedConfigPayload = currentConfig.copyWith(words: updatedWords);
    final updatedLexiconConfigs = Map<String, LexiconConfigPayload>.from(
      lexiconConfigs,
    );
    updatedLexiconConfigs[lang] = updatedConfigPayload;

    final newConfig = config.copyWith(lexiconConfigs: updatedLexiconConfigs);
    await ref.read(lexiconControllerProvider.notifier).saveLexicons(newConfig);
  }

  Future<void> _discoverPhrases(
    BuildContext context,
    WidgetRef ref,
    String lang,
    SystemConfigPerformativeLexicons config,
  ) async {
    try {
      final phrases = await ref
          .read(lexiconControllerProvider.notifier)
          .discoverPhrases(lang);

      if (context.mounted && phrases.isNotEmpty) {
        await _addPhrases(ref, config, lang, phrases);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Discovered and added ${phrases.length} new phrases.',
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
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
  ) async {
    try {
      final phrases = await ref
          .read(lexiconControllerProvider.notifier)
          .translatePhrases(lang);

      if (context.mounted && phrases.isNotEmpty) {
        await _addPhrases(ref, config, lang, phrases);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Translated and added ${phrases.length} missing phrases.',
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
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

    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, st) => ErrorView(
        error: e,
        onRetry: () =>
            ref.read(lexiconControllerProvider.notifier).fetchLexicons(),
      ),
      data: (config) {
        final lexiconConfigs = config.lexiconConfigs;
        final currentConfig =
            lexiconConfigs[selectedLang] ??
            LexiconConfigPayload(
              languageCode: selectedLang,
              languageName: selectedLang.toUpperCase(),
            );

        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Performative Lexicons (Slop Words)',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Row(
                    children: [
                      DropdownButton<String>(
                        value: selectedLang,
                        items: const [
                          DropdownMenuItem(
                            value: 'en',
                            child: Text('English (en)'),
                          ),
                          DropdownMenuItem(
                            value: 'fi',
                            child: Text('Finnish (fi)'),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) selectedLangState.value = val;
                        },
                      ),
                      const SizedBox(width: 16),
                      FilledButton.icon(
                        onPressed: () => _discoverPhrases(
                          context,
                          ref,
                          selectedLang,
                          config,
                        ),
                        icon: const Icon(Icons.search),
                        label: const Text('Discover New'),
                      ),
                      const SizedBox(width: 8),
                      if (selectedLang != 'en')
                        FilledButton.icon(
                          onPressed: () => _translatePhrases(
                            context,
                            ref,
                            selectedLang,
                            config,
                          ),
                          icon: const Icon(Icons.translate),
                          label: const Text('Translate Missing'),
                        ),
                      const SizedBox(width: 8),
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
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: textController,
                      decoration: const InputDecoration(
                        labelText: 'Add a new slop word / phrase',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                      onSubmitted: (value) async {
                        if (value.trim().isNotEmpty) {
                          await _addPhrases(ref, config, selectedLang, [value]);
                          textController.clear();
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: () async {
                      if (textController.text.trim().isNotEmpty) {
                        await _addPhrases(ref, config, selectedLang, [
                          textController.text,
                        ]);
                        textController.clear();
                      }
                    },
                    child: const Text('Add'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(
                child: Card(
                  child: ListView.builder(
                    itemCount: currentConfig.words.length,
                    itemBuilder: (context, index) {
                      final word = currentConfig.words[index];
                      return ListTile(
                        leading: const Icon(Icons.abc),
                        title: Text(word),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete),
                          onPressed: () {
                            // Local mutation pattern
                            final updatedWords = List<String>.from(
                              currentConfig.words,
                            )..removeAt(index);
                            final updatedConfigPayload = currentConfig.copyWith(
                              words: updatedWords,
                            );
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
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
