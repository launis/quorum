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

// Phase 5, Step 5.3: Strongly typed ResultDashboard models without Map<String, Object?>.
@immutable
class ResultDashboardNodeValue {
  final String? stringValue;
  final num? numberValue;
  final bool? boolValue;
  final List<String>? stringListValue;
  final Map<String, ResultDashboardNodeValue>? nestedEntries;

  const ResultDashboardNodeValue.text(String this.stringValue)
    : numberValue = null,
      boolValue = null,
      stringListValue = null,
      nestedEntries = null;

  const ResultDashboardNodeValue.number(num this.numberValue)
    : stringValue = null,
      boolValue = null,
      stringListValue = null,
      nestedEntries = null;

  const ResultDashboardNodeValue.flag(bool this.boolValue)
    : stringValue = null,
      numberValue = null,
      stringListValue = null,
      nestedEntries = null;

  const ResultDashboardNodeValue.stringList(List<String> this.stringListValue)
    : stringValue = null,
      numberValue = null,
      boolValue = null,
      nestedEntries = null;

  const ResultDashboardNodeValue.nested(
    Map<String, ResultDashboardNodeValue> this.nestedEntries,
  ) : stringValue = null,
      numberValue = null,
      boolValue = null,
      stringListValue = null;

  String? get scalarDisplayValue =>
      stringValue ?? numberValue?.toString() ?? boolValue?.toString();

  String toJsonValueString({int indent = 0}) {
    if (nestedEntries != null) {
      return _formatNodeMapJson(nestedEntries!, indent: indent);
    }
    if (stringListValue != null) {
      return '[${stringListValue!.map(jsonEncode).join(', ')}]';
    }
    if (numberValue != null) {
      return numberValue.toString();
    }
    if (boolValue != null) {
      return boolValue.toString();
    }
    return jsonEncode(stringValue ?? '');
  }
}

String _formatNodeMapJson(
  Map<String, ResultDashboardNodeValue> nodeMap, {
  int indent = 0,
}) {
  if (nodeMap.isEmpty) {
    return '{}';
  }
  final currentIndent = '  ' * indent;
  final childIndent = '  ' * (indent + 1);
  final lines = nodeMap.entries
      .map(
        (entry) =>
            '$childIndent${jsonEncode(entry.key)}: ${entry.value.toJsonValueString(indent: indent + 1)}',
      )
      .join(',\n');
  return '{\n$lines\n$currentIndent}';
}

@immutable
class ResultDashboardRawData {
  final Map<String, ResultDashboardNodeValue>? entries;
  final Map<String, ResultDashboardNodeValue>? contextVariables;
  final Map<String, ResultDashboardNodeValue>? stepResults;
  final bool hasInvalidContextVariables;
  final bool hasInvalidStepResults;

  const ResultDashboardRawData({
    this.entries,
    this.contextVariables,
    this.stepResults,
    this.hasInvalidContextVariables = false,
    this.hasInvalidStepResults = false,
  });

  Map<String, ResultDashboardNodeValue> toFullNodeMap() {
    return <String, ResultDashboardNodeValue>{
      if (contextVariables != null)
        'context_variables': ResultDashboardNodeValue.nested(contextVariables!),
      if (stepResults != null)
        'step_results': ResultDashboardNodeValue.nested(stepResults!),
      ...?entries,
    };
  }
}

@immutable
class ResultDashboardMetricsData {
  final bool hitlRequired;
  final bool hasWarning;
  final String? coachFeedback;
  final String? warningMessage;
  final SpecialistSectionMetrics? specialistMetrics;

  const ResultDashboardMetricsData({
    this.hitlRequired = false,
    this.hasWarning = false,
    this.coachFeedback,
    this.warningMessage,
    this.specialistMetrics,
  });
}

@immutable
class ResultDashboardNotificationData {
  final String level;
  final String? title;
  final String? message;

  const ResultDashboardNotificationData({
    this.level = 'info',
    this.title,
    this.message,
  });
}

@immutable
class ResultDashboardSourceListItemData {
  final String? source;
  final String? content;

  const ResultDashboardSourceListItemData({this.source, this.content});
}

@immutable
class ResultDashboardBlockData {
  final String type;
  final String id;
  final String label;
  final String? paragraphContent;
  final ScoreCardRadarData? radarData;
  final SpecialistSectionData? specialistData;
  final GenericGridData? metricGridData;
  final List<ValidationTimelineEvent>? timelineEvents;
  final List<ResultDashboardSourceListItemData>? listItems;

  const ResultDashboardBlockData({
    required this.type,
    required this.id,
    required this.label,
    this.paragraphContent,
    this.radarData,
    this.specialistData,
    this.metricGridData,
    this.timelineEvents,
    this.listItems,
  });
}

@immutable
class ResultDashboardReferenceData {
  final String id;
  final String intent;
  final String? title;
  final String? snippet;
  final String? url;

  const ResultDashboardReferenceData({
    required this.id,
    required this.intent,
    this.title,
    this.snippet,
    this.url,
  });
}

@immutable
class ResultDashboardViewData {
  final String? title;
  final String? intent;
  final ResultDashboardMetricsData? metrics;
  final ResultDashboardNotificationData? systemNotification;
  final List<ResultDashboardBlockData>? blocks;
  final List<ResultDashboardReferenceData>? references;
  final bool hasInvalidBlocksPayload;

  const ResultDashboardViewData({
    this.title,
    this.intent,
    this.metrics,
    this.systemNotification,
    this.blocks,
    this.references,
    this.hasInvalidBlocksPayload = false,
  });
}

class ResultDashboard extends ConsumerWidget {
  final ResultDashboardRawData rawResult;
  final ResultDashboardViewData? reportView;

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
    ResultDashboardViewData view,
  ) {
    try {
      if (view.hasInvalidBlocksPayload) {
        throw AppException.validation(
          'Fail-Fast: reportView["blocks"] must be a List.',
        );
      }

      final metrics = view.metrics;
      final systemNotification = view.systemNotification;
      final parsedBlocks = view.blocks ?? const <ResultDashboardBlockData>[];
      final referencesList =
          view.references ?? const <ResultDashboardReferenceData>[];

      for (var i = 0; i < referencesList.length; i++) {
        final refId = referencesList[i].id.trim();
        if (refId.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Reference at index $i is missing a valid non-empty "id".',
          );
        }
      }

      final isHitlRequired = metrics?.hitlRequired ?? false;
      final hasWarning = metrics?.hasWarning ?? false;
      final showWarning = isHitlRequired || hasWarning;

      final feedback = metrics?.coachFeedback ?? metrics?.warningMessage;

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
            if (referencesList.isNotEmpty) ...[
              const Divider(height: AppSpacing.s24),
              AppSpacing.h16,
              _buildReferencesSection(context, referencesList),
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
    List<ResultDashboardReferenceData> references,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final searchRefs = references.where((r) => r.intent == 'search').toList();
    final groundRefs = references
        .where((r) => r.intent == 'grounding')
        .toList();
    final kbRefs = references.where((r) => r.intent == 'internal_kb').toList();

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
    List<ResultDashboardReferenceData> refs,
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
              final refTitle = ref.title?.trim();
              final refId = ref.id.trim();
              final refSnippet = ref.snippet?.trim() ?? '';
              final refUrl = ref.url?.trim();

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
    ResultDashboardNotificationData notification,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final semanticColors = context.semanticColors;

    final level = notification.level;
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

    final rawTitle = notification.title?.trim() ?? '';
    final effectiveTitle = rawTitle.isNotEmpty
        ? rawTitle
        : l10n.sharedSystemNotificationDefaultTitle;
    final rawMessage = notification.message ?? '';

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

  Widget _buildHeader(BuildContext context, ResultDashboardViewData view) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final semanticColors = context.semanticColors;

    final intent = view.intent;
    Color statusColor = colorScheme.onSurfaceVariant;
    if (intent == 'success') {
      statusColor = semanticColors.success;
    } else if (intent == 'warning') {
      statusColor = semanticColors.warning;
    } else if (intent == 'danger') {
      statusColor = colorScheme.error;
    }

    final rawTitle = view.title?.trim() ?? '';
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
    ResultDashboardBlockData block,
    ResultDashboardViewData view,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    try {
      final blockType = block.type.trim();
      final blockId = block.id.trim();
      final blockLabel = block.label.trim();

      switch (blockType) {
        case 'card':
          if (block.radarData != null) {
            return ScoreCardRadar(cardData: block.radarData!);
          }
          if (block.specialistData != null) {
            return SpecialistSection(
              title: blockLabel,
              type: blockId,
              data: block.specialistData!,
              metrics:
                  view.metrics?.specialistMetrics ??
                  const SpecialistSectionMetrics(),
            );
          }
          throw AppException.validation(
            'Fail-Fast: Card block "$blockId" requires radarData or specialistData.',
          );

        case 'metric':
          if (block.metricGridData == null) {
            throw AppException.validation(
              'Fail-Fast: Metric block "$blockId" requires metricGridData.',
            );
          }
          return GenericGrid(title: blockLabel, data: block.metricGridData!);

        case 'paragraph':
          final content = block.paragraphContent ?? '';

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
          if (blockId == 'timeline-feed') {
            final events =
                block.timelineEvents ?? const <ValidationTimelineEvent>[];
            return ValidationTimelineWidget(title: blockLabel, events: events);
          }

          final parsedItems =
              block.listItems ?? const <ResultDashboardSourceListItemData>[];

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
                  final rawSource = itemObj.source?.trim() ?? '';
                  final rawContent = itemObj.content ?? '';
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
    Map<String, ResultDashboardNodeValue> source,
    Map<String, ResultDashboardNodeValue> target,
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

      if (value.nestedEntries != null) {
        if (key == 'metadata' || key == 'tool_calls') return;
        _flattenMap(value.nestedEntries!, target, effectiveKey);
      } else if (value.stringListValue != null) {
        final listVal = value.stringListValue!;
        if (listVal.isEmpty) {
          target[effectiveKey] = const ResultDashboardNodeValue.text('[]');
        } else {
          target[effectiveKey] = ResultDashboardNodeValue.text(
            listVal.join(', '),
          );
        }
      } else {
        final strVal = value.scalarDisplayValue;
        if (strVal != null && strVal.isNotEmpty) {
          final alreadyContains = target.values.any(
            (existing) => existing.scalarDisplayValue == strVal,
          );
          if (!alreadyContains) {
            target[effectiveKey] = value;
          }
        }
      }
    });
  }

  Widget _buildFlatDataView(
    BuildContext context,
    WidgetRef ref,
    ResultDashboardRawData data,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final dataToShow = <String, ResultDashboardNodeValue>{};

    try {
      if (data.hasInvalidContextVariables) {
        throw AppException.validation(
          'Fail-Fast: rawResult["context_variables"] must be a valid nested map.',
        );
      }
      if (data.hasInvalidStepResults) {
        throw AppException.validation(
          'Fail-Fast: rawResult["step_results"] must be a valid nested map.',
        );
      }

      if (data.contextVariables != null) {
        _flattenMap(data.contextVariables!, dataToShow, '');
      } else if (data.stepResults != null) {
        _flattenMap(data.stepResults!, dataToShow, '');
      } else if (data.entries != null) {
        _flattenMap(data.entries!, dataToShow, '');
      }

      if (dataToShow.isEmpty) {
        dataToShow['_info'] = ResultDashboardNodeValue.text(
          l10n.sharedFlatReportNoData,
        );
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

    final jsonString = _formatNodeMapJson(dataToShow);

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: SelectableText(
        jsonString,
        style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
      ),
    );
  }

  Widget _buildRawDataView(BuildContext context, ResultDashboardRawData data) {
    final theme = Theme.of(context);
    final jsonString = _formatNodeMapJson(data.toFullNodeMap());

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: SelectableText(
        jsonString,
        style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
      ),
    );
  }
}
