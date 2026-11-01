import 'dart:convert';
import 'dart:io';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/generic_grid.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/shared/widgets/score_card_radar.dart';
import 'package:client_app/shared/widgets/specialist_section.dart';
import 'package:client_app/shared/widgets/validation_timeline_widget.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ResultDashboard extends ConsumerWidget {
  final Map<String, Object?> rawResult;
  final Map<String, Object?>? reportView;

  const ResultDashboard({super.key, required this.rawResult, this.reportView});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return DefaultTabController(
      length: 3,
      child: Column(
        children: [
          TabBar(
            labelColor: colorScheme.primary,
            unselectedLabelColor: colorScheme.onSurfaceVariant,
            tabs: [
              Tab(
                icon: const Icon(Icons.dashboard_outlined),
                text: l10n.report,
              ),
              Tab(
                icon: const Icon(Icons.description_outlined),
                text: l10n.sharedTabFlatData,
              ),
              Tab(
                icon: const Icon(Icons.data_object_outlined),
                text: l10n.sharedTabRawData,
              ),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                if (reportView != null)
                  _buildDynamicDashboard(context, ref, reportView!)
                else
                  Center(
                    child: Text(
                      l10n.sharedNoReportData,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                _buildFlatDataView(context, ref, rawResult),
                _buildRawDataView(context, rawResult),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDynamicDashboard(
    BuildContext context,
    WidgetRef ref,
    Map<String, Object?> view,
  ) {
    try {
      final rawMetrics = view['metrics'];
      if (rawMetrics != null && rawMetrics is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: reportView["metrics"] must be a Map<String, Object?>.',
        );
      }
      final metrics = rawMetrics as Map<String, Object?>?;

      final rawSystemNotification = view['systemNotification'];
      if (rawSystemNotification != null &&
          rawSystemNotification is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: reportView["systemNotification"] must be a Map<String, Object?>.',
        );
      }
      final systemNotification = rawSystemNotification as Map<String, Object?>?;

      final rawBlocks = view['blocks'];
      if (rawBlocks != null && rawBlocks is! List<dynamic>) {
        throw AppException.validation(
          'Fail-Fast: reportView["blocks"] must be a List.',
        );
      }
      final blocksList = rawBlocks as List<dynamic>? ?? const <dynamic>[];
      final parsedBlocks = <Map<String, Object?>>[];
      for (var i = 0; i < blocksList.length; i++) {
        final item = blocksList[i];
        if (item is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Block at index $i must be a Map<String, Object?>.',
          );
        }
        parsedBlocks.add(item);
      }

      final rawReferences = view['references'];
      if (rawReferences != null && rawReferences is! List<dynamic>) {
        throw AppException.validation(
          'Fail-Fast: reportView["references"] must be a List.',
        );
      }
      final referencesList =
          rawReferences as List<dynamic>? ?? const <dynamic>[];
      final parsedReferences = <Map<String, Object?>>[];
      for (var i = 0; i < referencesList.length; i++) {
        final item = referencesList[i];
        if (item is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Reference at index $i must be a Map<String, Object?>.',
          );
        }
        final refId = item['id']?.toString().trim() ?? '';
        if (refId.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Reference at index $i is missing a valid non-empty "id".',
          );
        }
        parsedReferences.add(item);
      }

      final isHitlRequired = metrics?['hitl_required'] == true;
      final hasWarning = metrics?['has_warning'] == true;
      final showWarning = isHitlRequired || hasWarning;

      final feedback =
          metrics?['coach_feedback']?.toString() ??
          metrics?['warning_message']?.toString();

      return SingleChildScrollView(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context, view),
            AppSpacing.h16,
            if (showWarning) ...[
              _buildWarningBanner(
                context,
                isHitlRequired,
                hasWarning,
                feedback,
              ),
              AppSpacing.h24,
            ],
            if (systemNotification != null) ...[
              _buildSystemNotificationBanner(context, systemNotification),
              AppSpacing.h24,
            ],
            ...parsedBlocks.map(
              (block) => Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s24),
                child: _renderBlock(context, ref, block, view),
              ),
            ),
            if (parsedReferences.isNotEmpty) ...[
              const Divider(height: AppSpacing.s24),
              AppSpacing.h16,
              _buildReferencesSection(context, parsedReferences),
            ],
          ],
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ResultDashboard',
            'VALIDATION_FAILED: Failed to render dynamic dashboard',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildReferencesSection(
    BuildContext context,
    List<Map<String, Object?>> references,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final searchRefs = references
        .where((r) => r['intent'] == 'search')
        .toList();
    final groundRefs = references
        .where((r) => r['intent'] == 'grounding')
        .toList();
    final kbRefs = references
        .where((r) => r['intent'] == 'internal_kb')
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          l10n.sharedReferencesSectionTitle,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        AppSpacing.h16,
        if (searchRefs.isNotEmpty)
          _buildRefGroup(
            context,
            l10n.sharedRefGroupSearch,
            Icons.search,
            searchRefs,
          ),
        if (groundRefs.isNotEmpty)
          _buildRefGroup(
            context,
            l10n.sharedRefGroupGrounding,
            Icons.public,
            groundRefs,
          ),
        if (kbRefs.isNotEmpty)
          _buildRefGroup(
            context,
            l10n.sharedRefGroupKnowledgeBase,
            Icons.library_books,
            kbRefs,
          ),
      ],
    );
  }

  Widget _buildRefGroup(
    BuildContext context,
    String title,
    IconData icon,
    List<Map<String, Object?>> refs,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s24),
      child: Container(
        padding: AppSpacing.p16,
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(AppSpacing.s8),
          border: Border.all(
            color: colorScheme.onSurfaceVariant.withValues(alpha: 0.2),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: colorScheme.primary, size: AppSpacing.s24),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            AppSpacing.h16,
            ...refs.map((ref) {
              final refTitle = ref['title']?.toString().trim();
              final refId = ref['id']!.toString().trim();
              final refSnippet = ref['snippet']?.toString().trim() ?? '';
              final refUrl = ref['url']?.toString().trim();

              return Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (refTitle != null && refTitle.isNotEmpty)
                          ? '$refId - $refTitle'
                          : refId,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (refSnippet.isNotEmpty) ...[
                      AppSpacing.h4,
                      Text(
                        refSnippet,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurface,
                        ),
                        softWrap: true,
                        overflow: TextOverflow.visible,
                      ),
                    ],
                    if (refUrl != null && refUrl.isNotEmpty) ...[
                      AppSpacing.h4,
                      InkWell(
                        mouseCursor: SystemMouseCursors.click,
                        onTap: () {
                          Clipboard.setData(ClipboardData(text: refUrl));
                        },
                        child: Text(
                          refUrl,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: colorScheme.primary,
                            decoration: TextDecoration.underline,
                          ),
                          softWrap: true,
                          overflow: TextOverflow.visible,
                        ),
                      ),
                    ],
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemNotificationBanner(
    BuildContext context,
    Map<String, Object?> notification,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final semanticColors = context.semanticColors;

    final level = notification['level']?.toString() ?? 'info';
    final isDanger = level == 'danger';
    final isWarning = level == 'warning';

    final Color bgColor;
    final Color borderColor;
    final Color iconColor;
    final Color textColor;

    if (isDanger) {
      bgColor = colorScheme.errorContainer;
      borderColor = colorScheme.error;
      iconColor = colorScheme.error;
      textColor = colorScheme.onErrorContainer;
    } else if (isWarning) {
      bgColor = semanticColors.warning.withValues(alpha: 0.15);
      borderColor = semanticColors.warning;
      iconColor = semanticColors.warning;
      textColor = colorScheme.onSurface;
    } else {
      bgColor = colorScheme.secondaryContainer;
      borderColor = colorScheme.secondary;
      iconColor = colorScheme.secondary;
      textColor = colorScheme.onSecondaryContainer;
    }

    final rawTitle = notification['title']?.toString().trim() ?? '';
    final effectiveTitle = rawTitle.isNotEmpty
        ? rawTitle
        : l10n.sharedSystemNotificationDefaultTitle;
    final rawMessage = notification['message']?.toString() ?? '';

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        border: Border(
          left: BorderSide(color: borderColor, width: AppSpacing.s4),
        ),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(AppSpacing.s8),
          bottomRight: Radius.circular(AppSpacing.s8),
        ),
      ),
      padding: AppSpacing.p16,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: iconColor),
              AppSpacing.w8,
              Expanded(
                child: Text(
                  effectiveTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: iconColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          Text(
            rawMessage,
            style: theme.textTheme.bodySmall?.copyWith(color: textColor),
          ),
        ],
      ),
    );
  }

  Widget _buildWarningBanner(
    BuildContext context,
    bool hitl,
    bool backendWarning,
    String? feedback,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    String title = l10n.sharedWarningTitleDefault;
    if (hitl) {
      title = l10n.sharedWarningTitleHitl;
    } else if (backendWarning) {
      title = l10n.sharedWarningTitleSystem;
    }

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(AppSpacing.s12),
        border: Border.all(color: colorScheme.error),
      ),
      padding: AppSpacing.p16,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            color: colorScheme.error,
            size: AppSpacing.s24,
          ),
          AppSpacing.w16,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: colorScheme.onErrorContainer,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                AppSpacing.h8,
                if (feedback != null && feedback.isNotEmpty)
                  Text(
                    feedback,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onErrorContainer.withValues(
                        alpha: 0.9,
                      ),
                    ),
                  )
                else
                  Text(
                    l10n.sharedWarningDefaultMessage,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onErrorContainer.withValues(
                        alpha: 0.8,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, Map<String, Object?> view) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final semanticColors = context.semanticColors;

    final intent = view['intent']?.toString();
    Color statusColor = colorScheme.onSurfaceVariant;
    if (intent == 'success') {
      statusColor = semanticColors.success;
    } else if (intent == 'warning') {
      statusColor = semanticColors.warning;
    } else if (intent == 'danger') {
      statusColor = colorScheme.error;
    }

    final rawTitle = view['title']?.toString().trim() ?? '';
    final headerTitle = rawTitle.isNotEmpty
        ? rawTitle.toUpperCase()
        : l10n.reportTitleFallback;

    return Card(
      elevation: AppSpacing.s4,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: statusColor, width: AppSpacing.s2),
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p24,
        child: Column(
          children: [
            Text(
              headerTitle,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: statusColor,
              ),
              textAlign: TextAlign.center,
            ),
            AppSpacing.h8,
            Text(
              l10n.printedAtTimestamp(_formatDateTime(DateTime.now())),
              style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.day.toString().padLeft(2, '0')}.${dt.month.toString().padLeft(2, '0')}.${dt.year} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }

  Widget _renderBlock(
    BuildContext context,
    WidgetRef ref,
    Map<String, Object?> block,
    Map<String, Object?> view,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    try {
      final blockType = block['type']?.toString().trim() ?? '';
      final blockId = block['id']?.toString().trim() ?? '';
      final blockLabel = block['label']?.toString().trim() ?? '';
      final blockValue = block['value'];

      switch (blockType) {
        case 'card':
          if (blockValue is! Map<String, Object?>) {
            throw AppException.validation(
              'Fail-Fast: Card block "$blockId" value must be a Map<String, Object?>.',
            );
          }
          if (blockValue.containsKey('dimensions')) {
            return ScoreCardRadar(cardData: blockValue);
          }
          final rawMetrics = view['metrics'];
          final metricsMap = rawMetrics is Map<String, Object?>
              ? rawMetrics
              : const <String, Object?>{};
          return SpecialistSection(
            title: blockLabel,
            type: blockId,
            data: blockValue,
            metrics: metricsMap,
          );

        case 'metric':
          if (blockValue is! Map<String, Object?>) {
            throw AppException.validation(
              'Fail-Fast: Metric block "$blockId" value must be a Map<String, Object?>.',
            );
          }
          return GenericGrid(title: blockLabel, data: blockValue);

        case 'paragraph':
          final String content;
          if (blockValue is Map<String, Object?>) {
            content = blockValue['content']?.toString() ?? '';
          } else {
            content = blockValue?.toString() ?? '';
          }

          if (blockId == 'coach-markdown') {
            return Card(
              elevation: AppSpacing.s2,
              margin: const EdgeInsets.only(bottom: AppSpacing.s16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSpacing.s12),
              ),
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      colorScheme.primaryContainer.withValues(alpha: 0.25),
                      colorScheme.secondaryContainer.withValues(alpha: 0.25),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(AppSpacing.s12),
                  border: Border.all(
                    color: colorScheme.primary,
                    width: AppSpacing.s2,
                  ),
                ),
                padding: AppSpacing.p16,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: AppSpacing.p8,
                          decoration: BoxDecoration(
                            color: colorScheme.primary,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.psychology_alt,
                            color: colorScheme.onPrimary,
                            size: AppSpacing.s24,
                          ),
                        ),
                        AppSpacing.w12,
                        Expanded(
                          child: Text(
                            blockLabel.isNotEmpty ? blockLabel : l10n.stepCoach,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: colorScheme.primary,
                            ),
                          ),
                        ),
                      ],
                    ),
                    AppSpacing.h16,
                    Divider(color: colorScheme.primary),
                    AppSpacing.h16,
                    OutputRenderer(markdownContent: content),
                  ],
                ),
              ),
            );
          }

          return Card(
            child: Padding(
              padding: AppSpacing.p16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (blockLabel.isNotEmpty) ...[
                    Text(
                      blockLabel,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleMedium,
                    ),
                    const Divider(),
                  ],
                  OutputRenderer(markdownContent: content),
                ],
              ),
            ),
          );

        case 'list':
          if (blockValue is! Map<String, Object?>) {
            throw AppException.validation(
              'Fail-Fast: List block "$blockId" value must be a Map<String, Object?>.',
            );
          }
          if (blockId == 'timeline-feed') {
            final rawEvents = blockValue['events'];
            if (rawEvents != null && rawEvents is! List<dynamic>) {
              throw AppException.validation(
                'Fail-Fast: Timeline block events must be a List.',
              );
            }
            final events = rawEvents as List<dynamic>? ?? const <dynamic>[];
            return ValidationTimelineWidget(title: blockLabel, events: events);
          }

          final rawItems = blockValue['items'];
          if (rawItems != null && rawItems is! List<dynamic>) {
            throw AppException.validation(
              'Fail-Fast: List block items must be a List.',
            );
          }
          final items = rawItems as List<dynamic>? ?? const <dynamic>[];
          final parsedItems = <Map<String, Object?>>[];
          for (var i = 0; i < items.length; i++) {
            final item = items[i];
            if (item is! Map<String, Object?>) {
              throw AppException.validation(
                'Fail-Fast: List block item at index $i must be a Map<String, Object?>.',
              );
            }
            parsedItems.add(item);
          }

          return Card(
            child: Semantics(
              excludeSemantics: Platform.isWindows,
              child: ExpansionTile(
                title: Text(
                  blockLabel,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                children: parsedItems.map<Widget>((itemObj) {
                  final rawSource = itemObj['source']?.toString().trim() ?? '';
                  final rawContent = itemObj['content']?.toString() ?? '';
                  return ListTile(
                    leading: Icon(
                      Icons.source_outlined,
                      color: colorScheme.onSurfaceVariant,
                    ),
                    title: Text(
                      rawSource.isNotEmpty ? rawSource : l10n.lblSource,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: AppSpacing.s4),
                      child: Text(rawContent),
                    ),
                    dense: true,
                  );
                }).toList(),
              ),
            ),
          );

        default:
          throw AppException.validation(
            'Fail-Fast: Unknown or unsupported block type "$blockType".',
          );
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ResultDashboard',
            'VALIDATION_FAILED: Failed to render report block',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  void _flattenMap(
    Map<String, Object?> source,
    Map<String, Object?> target,
    String prefix,
  ) {
    source.forEach((key, value) {
      final lKey = key.toLowerCase();
      if (lKey.contains('thought') ||
          lKey.contains('trace') ||
          lKey.contains('history') ||
          lKey.contains('message') ||
          lKey.contains('token') ||
          lKey == 'inputs' ||
          lKey == 'step_names' ||
          lKey == 'step_results' ||
          lKey.endsWith('_text') ||
          lKey == 'id' ||
          lKey.endsWith('_id')) {
        return;
      }

      final parts = key.split('_');
      final pascalKey = parts
          .map((p) {
            if (p.isEmpty) return p;
            return p.replaceFirstMapped(
              RegExp(r'^.'),
              (m) => m.group(0)!.toUpperCase(),
            );
          })
          .join('');

      String effectiveKey = pascalKey;
      if (prefix.isNotEmpty) {
        if (pascalKey.startsWith(prefix)) {
          effectiveKey = pascalKey;
        } else {
          effectiveKey = '$prefix$pascalKey';
        }
      }

      final uuidRegex = RegExp(
        r'^[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}V?',
        caseSensitive: false,
      );
      effectiveKey = effectiveKey.replaceAll(uuidRegex, '');

      if (effectiveKey.isEmpty) {
        effectiveKey = pascalKey;
      }

      if (value is Map<String, Object?>) {
        if (key == 'metadata' || key == 'tool_calls') return;
        _flattenMap(value, target, effectiveKey);
      } else if (value is List) {
        if (value.isEmpty) {
          target[effectiveKey] = '[]';
        } else if (value.first is String || value.first is num) {
          target[effectiveKey] = value.join(', ');
        } else {
          target[effectiveKey] = '[${value.length} items]';
        }
      } else if (value != null && value.toString().isNotEmpty) {
        final strVal = value.toString();
        if (!target.containsValue(strVal)) {
          target[effectiveKey] = value;
        }
      }
    });
  }

  Widget _buildFlatDataView(
    BuildContext context,
    WidgetRef ref,
    Map<String, Object?> data,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final Map<String, Object?> dataToShow = {};

    try {
      if (data.containsKey('context_variables')) {
        final rawCtx = data['context_variables'];
        if (rawCtx is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: rawResult["context_variables"] must be a Map<String, Object?>.',
          );
        }
        _flattenMap(rawCtx, dataToShow, '');
      } else if (data.containsKey('step_results')) {
        final rawSteps = data['step_results'];
        if (rawSteps is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: rawResult["step_results"] must be a Map<String, Object?>.',
          );
        }
        _flattenMap(rawSteps, dataToShow, '');
      } else {
        _flattenMap(data, dataToShow, '');
      }

      if (dataToShow.isEmpty) {
        dataToShow['_info'] = l10n.sharedFlatReportNoData;
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ResultDashboard',
            'VALIDATION_FAILED: Flat Report parsing failed',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }

    const encoder = JsonEncoder.withIndent('  ');
    final jsonString = encoder.convert(dataToShow);

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: SelectableText(
        jsonString,
        style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
      ),
    );
  }

  Widget _buildRawDataView(BuildContext context, Map<String, Object?> data) {
    final theme = Theme.of(context);
    const encoder = JsonEncoder.withIndent('  ');
    final jsonString = encoder.convert(data);

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: SelectableText(
        jsonString,
        style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
      ),
    );
  }
}
