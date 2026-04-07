import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Reusable widget to display collected XAI Output Extensions
/// Enforces Fail-Fast UI degradation rules for missing data without crashing.
class XAIExtensionsBox extends ConsumerWidget {
  final Map<String, List<dynamic>> groupedExtensions;

  const XAIExtensionsBox({super.key, required this.groupedExtensions});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (groupedExtensions.isEmpty) {
      return const SizedBox.shrink();
    }

    // Filter out completely empty extension groups
    final activeExtensions = Map<String, List<dynamic>>.fromEntries(
      groupedExtensions.entries.where((e) {
        if (e.value.isEmpty) {
          ref
              .read(loggerServiceProvider)
              .error(
                'XAIExtensionsBox',
                'Extension group "${e.key}" was requested but AI produced no data. Supressing empty header.',
                null,
              );
          return false;
        }
        return true;
      }),
    );

    if (activeExtensions.isEmpty) {
      return const SizedBox.shrink();
    }

    final l10n = AppLocalizations.of(context)!;
    final isFi = Localizations.localeOf(context).languageCode == 'fi';

    String translateKey(String key) {
      switch (key) {
        case 'citation':
          return l10n
              .reportQuoteTitle('Viitteet')
              .replaceAll(': Viitteet', '')
              .replaceAll(': "Viitteet"', '');
        case 'justification':
          return isFi ? 'Perustelut' : 'Justification';
        case 'falsification':
          return l10n.reportFalsificationTitle;
        case 'theory_link':
          return l10n.reportTheoryLinkTitle;
        case 'risk_flag':
          return l10n.reportRiskFlagTitle;
        case 'coaching':
          return l10n.reportCoachingTitle;
        case 'missing_context':
          return l10n.reportMissingContextTitle;
        case 'remediation_steps':
          return l10n.reportRemediationStepsTitle;
        case 'emotional_sentiment':
          return l10n.reportEmotionalSentimentTitle;
        case 'confidence':
          return l10n.xaiConfidence;
        default:
          return key.toUpperCase();
      }
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: activeExtensions.entries.map((entry) {
          final extKey = entry.key;
          final extItems = entry.value;

          final theme = Theme.of(context);
          final colorScheme = theme.colorScheme;

          return Card(
            elevation: 4,
            margin: const EdgeInsets.only(bottom: 16.0),
            color: colorScheme.secondaryContainer,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: colorScheme.primary, width: 1.5),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.extension,
                        color: colorScheme.tertiary,
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        translateKey(extKey).toUpperCase(),
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.primary,
                        ),
                      ),
                    ],
                  ),
                  Divider(
                    height: 24,
                    color: colorScheme.primary.withAlpha(100),
                  ),
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: extItems.length,
                    separatorBuilder: (context, index) => const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Divider(),
                    ),
                    itemBuilder: (context, index) {
                      final val = extItems[index];

                      if (val is Map) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: val.entries.map((vEntry) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 4.0),
                              child: Text(
                                '- ${vEntry.key}: ${vEntry.value}',
                                style: const TextStyle(fontSize: 14),
                              ),
                            );
                          }).toList(),
                        );
                      }

                      return Text(
                        val.toString(),
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.black87,
                          height: 1.4,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
