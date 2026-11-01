import 'dart:io';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ValidationTimelineWidget extends ConsumerWidget {
  final String title;
  final List<dynamic> events;

  const ValidationTimelineWidget({
    super.key,
    required this.title,
    required this.events,
  });

  static const double _connectorColumnWidth = 60.0;
  static const double _timeColumnWidth = 50.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    try {
      if (title.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: ValidationTimelineWidget title cannot be empty.',
        );
      }

      final parsedEvents = <_ParsedTimelineEvent>[];
      for (var i = 0; i < events.length; i++) {
        final rawEvent = events[i];
        if (rawEvent is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: ValidationTimelineWidget event at index $i must be a Map<String, Object?>.',
          );
        }

        final rawLabel = rawEvent['label']?.toString().trim() ?? '';
        if (rawLabel.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: ValidationTimelineWidget event at index $i is missing a non-empty label.',
          );
        }

        final rawTs = rawEvent['timestamp']?.toString().trim() ?? '';
        final timeDisplay = _extractTimeDisplay(rawTs);
        final isAlert = rawEvent['is_alert'] == true;
        final rawContent = rawEvent['content']?.toString().trim() ?? '';

        parsedEvents.add(
          _ParsedTimelineEvent(
            timeDisplay: timeDisplay,
            label: rawLabel,
            content: rawContent,
            isAlert: isAlert,
          ),
        );
      }

      return Card(
        elevation: AppSpacing.s2,
        child: Semantics(
          excludeSemantics: Platform.isWindows,
          child: ExpansionTile(
            initiallyExpanded: true,
            title: Text(
              title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            children: [
              if (parsedEvents.isEmpty)
                Padding(
                  padding: AppSpacing.p16,
                  child: Text(
                    l10n.sharedNoTimelineData,
                    style: textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ...parsedEvents.asMap().entries.map((entry) {
                final index = entry.key;
                final event = entry.value;
                final isLast = index == parsedEvents.length - 1;

                final transparentConnectorColor = colorScheme.onSurfaceVariant
                    .withValues(alpha: 0.0);

                return IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SizedBox(
                        width: _connectorColumnWidth,
                        child: Column(
                          children: [
                            Container(
                              width: AppSpacing.s2,
                              height: AppSpacing.s16,
                              color: index == 0
                                  ? transparentConnectorColor
                                  : colorScheme.onSurfaceVariant,
                            ),
                            Container(
                              width: AppSpacing.s12,
                              height: AppSpacing.s12,
                              decoration: BoxDecoration(
                                color: event.isAlert
                                    ? colorScheme.error
                                    : colorScheme.primary,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: colorScheme.surface,
                                  width: AppSpacing.s2,
                                ),
                              ),
                            ),
                            Expanded(
                              child: Container(
                                width: AppSpacing.s2,
                                color: isLast
                                    ? transparentConnectorColor
                                    : colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ),
                      SizedBox(
                        width: _timeColumnWidth,
                        child: Padding(
                          padding: const EdgeInsets.only(top: AppSpacing.s12),
                          child: Text(
                            event.timeDisplay,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.labelMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: event.isAlert
                                  ? colorScheme.error
                                  : colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(
                            AppSpacing.s8,
                            AppSpacing.s12,
                            AppSpacing.s16,
                            AppSpacing.s24,
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                event.label,
                                style: textTheme.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: event.isAlert
                                      ? colorScheme.error
                                      : colorScheme.onSurface,
                                ),
                              ),
                              if (event.content.isNotEmpty) ...[
                                AppSpacing.h4,
                                Text(
                                  event.content,
                                  style: textTheme.bodyMedium?.copyWith(
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }),
              AppSpacing.h8,
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ValidationTimelineWidget',
            'VALIDATION_FAILED: Failed to render validation timeline',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  static String _extractTimeDisplay(String ts) {
    final parsedDate = DateTime.tryParse(ts);
    if (parsedDate != null) {
      final hh = parsedDate.hour.toString().padLeft(2, '0');
      final mm = parsedDate.minute.toString().padLeft(2, '0');
      return '$hh:$mm';
    }
    return ts;
  }
}

class _ParsedTimelineEvent {
  final String timeDisplay;
  final String label;
  final String content;
  final bool isAlert;

  const _ParsedTimelineEvent({
    required this.timeDisplay,
    required this.label,
    required this.content,
    required this.isAlert,
  });
}
