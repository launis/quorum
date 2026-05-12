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
      return const SizedBox();
    }

    // Filter out completely empty extension groups
    final activeExtensions = Map<String, List<dynamic>>.fromEntries(
      groupedExtensions.entries.where((e) {
        if (e.value.isEmpty) {
          ref
              .read(loggerServiceProvider)
              .info(
                'XAIExtensionsBox',
                'Extension group "${e.key}" was requested but AI produced no data. Supressing empty header.',
              );
          return false;
        }
        return true;
      }),
    );

    if (activeExtensions.isEmpty) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;

    String translateKey(String key) {
      switch (key) {
        case 'citation':
          return l10n.xaiSourceCitation;
        case 'justification':
          return l10n.xaiJustification;
        case 'falsification':
          return l10n.xaiDevilsAdvocate;
        case 'theory_link':
          return l10n.xaiTheoryLink;
        case 'risk_flag':
          return l10n.xaiRiskFlag;
        case 'coaching':
          return l10n.xaiCoachingTip;
        case 'missing_context':
          return l10n.xaiMissingContext;
        case 'remediation_steps':
          return l10n.xaiRemediation;
        case 'emotional_sentiment':
          return l10n.xaiSentiment;
        case 'confidence':
          return l10n.xaiConfidence;
        default:
          return key.toUpperCase();
      }
    }

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 24.0, top: 16.0),
            child: Text(
              l10n.xaiGlobalExtensionsHeader,
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ),
          ...activeExtensions.entries.map((entry) {
            final extKey = entry.key;
            final extItems = entry.value;

            Color cardBgColor = colorScheme.secondaryContainer;
            Color cardBorderColor = colorScheme.secondary;

            switch (extKey) {
              case 'falsification':
              case 'risk_flag':
                cardBgColor = colorScheme.errorContainer;
                cardBorderColor = colorScheme.error;
                break;
              case 'coaching':
              case 'remediation_steps':
                cardBgColor = const Color(0xFFE8F5E9);
                cardBorderColor = const Color(0xFF2E7D32);
                break;
              case 'justification':
              case 'theory_link':
                cardBgColor = colorScheme.primaryContainer;
                cardBorderColor = colorScheme.primary;
                break;
              case 'missing_context':
                cardBgColor = const Color(0xFFFFF3E0);
                cardBorderColor = const Color(0xFFE65100);
                break;
            }

            return Card(
              elevation: 4,
              margin: const EdgeInsets.only(bottom: 16.0),
              color: cardBgColor,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(color: cardBorderColor, width: 1.5),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
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
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8.0),
                      itemBuilder: (context, index) {
                        final val = extItems[index];

                        if (val is Map) {
                          // Support Zero-Math UI or Legacy UI
                          String displayContent = val.toString();
                          if (!val.containsKey('content') &&
                              val.containsKey('axis_name')) {
                            final innerKey = val.keys.firstWhere(
                              (k) => k != 'axis_name' && k != '_score',
                              orElse: () => '',
                            );
                            if (innerKey.toString().isNotEmpty) {
                              displayContent =
                                  '${val['axis_name']}:\n${val[innerKey]}';
                            }
                          }

                          final content =
                              val['content']?.toString() ?? displayContent;
                          final colorTheme =
                              val['color_theme']?.toString() ?? 'info';
                          Color bgColor = theme.colorScheme.primaryContainer;
                          Color fgColor = theme.colorScheme.onPrimaryContainer;

                          switch (colorTheme) {
                            case 'danger':
                              bgColor = theme.colorScheme.errorContainer;
                              fgColor = theme.colorScheme.error;
                              break;
                            case 'warning':
                              bgColor = const Color(0xFFFFF3E0);
                              fgColor = const Color(0xFFE65100);
                              break;
                            case 'success':
                              bgColor = const Color(0xFFE8F5E9);
                              fgColor = const Color(0xFF1B5E20);
                              break;
                            case 'info':
                            default:
                              bgColor = theme.colorScheme.secondaryContainer;
                              fgColor = theme.colorScheme.onSecondaryContainer;
                          }

                          return Container(
                            padding: const EdgeInsets.all(12.0),
                            decoration: BoxDecoration(
                              color: bgColor,
                              borderRadius: BorderRadius.circular(8.0),
                              border: Border(
                                left: BorderSide(color: fgColor, width: 4.0),
                              ),
                            ),
                            child: Text(
                              content,
                              style: TextStyle(
                                fontSize: 14,
                                color: theme.colorScheme.onSurface,
                                height: 1.4,
                              ),
                            ),
                          );
                        }

                        // Fallback for legacy strings
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
          }),
        ],
      ),
    );
  }
}
