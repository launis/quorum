import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';

import 'package:client_app/shared/widgets/generic_grid.dart';
import 'package:client_app/shared/widgets/score_card_radar.dart';

import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/shared/widgets/validation_timeline_widget.dart';
import 'package:client_app/shared/widgets/specialist_section.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';

class ResultDashboard extends StatelessWidget {
  final Map<String, dynamic> rawResult;
  final Map<String, dynamic>? reportView;

  const ResultDashboard({super.key, required this.rawResult, this.reportView});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Column(
        children: [
          TabBar(
            labelColor: Theme.of(context).colorScheme.primary,
            unselectedLabelColor: Theme.of(
              context,
            ).colorScheme.onSurfaceVariant,
            tabs: [
              Tab(icon: Icon(Icons.dashboard_outlined), text: 'Raportti'),
              Tab(
                icon: Icon(Icons.description_outlined),
                text: 'Tiivistetty Data (Flat)',
              ),
              Tab(
                icon: Icon(Icons.data_object_outlined),
                text: 'Koko Raakadata',
              ),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                // Tab 1: Server-Driven Dashboard (BFF)
                if (reportView != null)
                  _buildDynamicDashboard(context, reportView!)
                else
                  Center(
                    child: Text(
                      AppLocalizations.of(context)?.sharedNoReportData ??
                          "Raporttidataa ei ole saatavilla.",
                    ),
                  ),

                // Tab 2: Flat Report JSON
                _buildFlatDataView(context, rawResult),

                // Tab 3: Complete Raw JSON
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
    Map<String, dynamic> view,
  ) {
    // 1. SDUI Protocol: We respect backend signals without string parsing
    final metrics = view['metrics'] as Map<String, dynamic>?;
    final bool isHitlRequired = metrics?['hitl_required'] == true;
    final bool hasWarning = metrics?['has_warning'] == true;

    final bool showWarning = isHitlRequired || hasWarning;

    // We only display feedback exactly as given by backend
    final String? feedback =
        metrics?['coach_feedback']?.toString() ??
        metrics?['warning_message']?.toString();

    final systemNotification =
        view['systemNotification'] as Map<String, dynamic>?;
    final blocks = view['blocks'] as List<dynamic>? ?? [];
    final references = view['references'] as List<dynamic>? ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildHeader(context, view),
          const SizedBox(height: 16),
          if (showWarning) ...[
            _buildWarningBanner(context, isHitlRequired, hasWarning, feedback),
            const SizedBox(height: 24),
          ],
          if (systemNotification != null) ...[
            _buildSystemNotificationBanner(context, systemNotification),
            const SizedBox(height: 24),
          ],
          ...blocks.map((blockRaw) {
            final block = blockRaw as Map<String, dynamic>;
            return Padding(
              padding: const EdgeInsets.only(bottom: 24.0),
              child: _renderBlock(context, block, view),
            );
          }),
          if (references.isNotEmpty) ...[
            const Divider(height: 48),
            _buildReferencesSection(context, references),
          ],
        ],
      ),
    );
  }

  Widget _buildReferencesSection(
    BuildContext context,
    List<dynamic> references,
  ) {
    // Group by intent
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
          'Lähdeluettelo & Viitteet',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (searchRefs.isNotEmpty)
          _buildRefGroup(context, 'Analytiikan Haut', Icons.search, searchRefs),
        if (groundRefs.isNotEmpty)
          _buildRefGroup(
            context,
            'Faktantarkistus (Vertex AI Grounding)',
            Icons.public,
            groundRefs,
          ),
        if (kbRefs.isNotEmpty)
          _buildRefGroup(
            context,
            'Organisaation Linjaukset & Tietopankki',
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
    List<dynamic> refs,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24.0),
      child: Container(
        padding: EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(8.0),
          border: Border.all(
            color: Theme.of(
              context,
            ).colorScheme.onSurfaceVariant.withValues(alpha: 0.2),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: Theme.of(context).colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8.0),
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16.0,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16.0),
            ...refs.map((refRaw) {
              final ref = refRaw as Map<String, dynamic>;
              final refTitle = ref['title']?.toString();
              final refId = ref['id']?.toString() ?? 'Reference';
              final refSnippet = ref['snippet']?.toString() ?? '';
              final refUrl = ref['url']?.toString();

              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (refTitle != null && refTitle.isNotEmpty)
                          ? '$refId - $refTitle'
                          : refId,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14.0,
                        height: 1.4,
                      ),
                    ),
                    if (refSnippet.isNotEmpty) ...[
                      const SizedBox(height: 6.0),
                      Text(
                        refSnippet,
                        style: TextStyle(
                          fontSize: 13.0,
                          color: Theme.of(context).colorScheme.onSurface,
                          height: 1.5,
                        ),
                        softWrap: true,
                        overflow: TextOverflow.visible,
                      ),
                    ],
                    if (refUrl != null && refUrl.isNotEmpty) ...[
                      const SizedBox(height: 6.0),
                      InkWell(
                        onTap: () {
                          // Allow copying URL in a real app or use url_launcher
                        },
                        child: Text(
                          refUrl,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.primary,
                            decoration: TextDecoration.underline,
                            fontSize: 12.0,
                          ),
                          softWrap: true,
                          overflow: TextOverflow.visible,
                        ),
                      ),
                    ],
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemNotificationBanner(
    BuildContext context,
    Map<String, dynamic> notification,
  ) {
    final level = notification['level']?.toString() ?? 'info';
    final isDanger = level == 'danger';
    final bgColor = isDanger
        ? Theme.of(context).colorScheme.error
        : Theme.of(context).colorScheme.error;
    final borderColor = isDanger
        ? Theme.of(context).colorScheme.error
        : Theme.of(context).colorScheme.error;
    final iconColor = isDanger
        ? Theme.of(context).colorScheme.error
        : Theme.of(context).colorScheme.error;
    final textColor = isDanger
        ? Theme.of(context).colorScheme.error
        : Colors.deepOrange[900];

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        border: Border(left: BorderSide(color: borderColor, width: 4)),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(8),
          bottomRight: Radius.circular(8),
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: iconColor),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  notification['title']?.toString() ?? 'Notification',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: iconColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            notification['message']?.toString() ?? '',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: textColor),
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
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    String title = "Huomioitavaa";
    if (hitl)
      title = "Ihmisen tarkistus vaaditaan (HITL)";
    else if (backendWarning)
      title = "Järjestelmän varoitus";

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.error),
      ),
      padding: const EdgeInsets.all(16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_rounded, color: colorScheme.error, size: 28),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: colorScheme.onErrorContainer,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (feedback != null && feedback.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    feedback,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onErrorContainer.withValues(
                        alpha: 0.9,
                      ),
                    ),
                  ),
                ] else ...[
                  const SizedBox(height: 8),
                  Text(
                    "Järjestelmä suosittelee tulosten manuaalista tarkistamista rakenteellisten tai loogisten poikkeamien vuoksi.",
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onErrorContainer.withValues(
                        alpha: 0.8,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, Map<String, dynamic> view) {
    final intent = view['intent']?.toString();
    Color statusColor = Theme.of(context).colorScheme.onSurfaceVariant;
    if (intent == 'success')
      statusColor = Color(0xFF2E7D32);
    else if (intent == 'warning')
      statusColor = Theme.of(context).colorScheme.error;
    else if (intent == 'danger')
      statusColor = Theme.of(context).colorScheme.error;

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: statusColor, width: 2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Text(
              view['title']?.toString().toUpperCase() ?? 'RAPORTTI',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: statusColor,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 8),
            Text(
              'Tulostettu: ${_formatDateTime(DateTime.now())}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
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
    Map<String, dynamic> block,
    Map<String, dynamic> view,
  ) {
    final blockType = block['type']?.toString();
    final blockId = block['id']?.toString() ?? '';
    final blockLabel = block['label']?.toString() ?? '';
    final blockValue = block['value'];

    switch (blockType) {
      case 'card':
        try {
          if (blockValue != null &&
              blockValue is Map &&
              blockValue.containsKey('dimensions')) {
            return ScoreCardRadar(cardData: blockValue as Map<String, dynamic>);
          }
        } catch (e) {
          ProviderScope.containerOf(context)
              .read(loggerServiceProvider)
              .error('Report', 'Error rendering ScoreCard: $e', e);
          return ErrorView(
            error: "Error rendering ScoreCard: $e",
            compact: true,
          );
        }
        return SpecialistSection(
          title: blockLabel,
          type: blockId,
          data: blockValue is Map<String, dynamic> ? blockValue : {},
          metrics: view['metrics'] as Map<String, dynamic>? ?? {},
        );

      case 'metric':
        return GenericGrid(
          title: blockLabel,
          data: blockValue is Map<String, dynamic> ? blockValue : {},
        );

      case 'paragraph':
        final content = blockValue is Map<String, dynamic>
            ? blockValue['content'] as String? ?? ''
            : blockValue?.toString() ?? '';

        if (blockId == 'coach-markdown') {
          return Card(
            elevation: 2,
            margin: const EdgeInsets.only(bottom: 16.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Color(0xFF2E7D32),
                    Theme.of(context).colorScheme.secondary,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF2E7D32), width: 2),
              ),
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF2E7D32),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.psychology_alt,
                          color: Theme.of(context).colorScheme.surface,
                          size: 24,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          blockLabel.isNotEmpty
                              ? blockLabel
                              : AppLocalizations.of(context)!.stepCoach,
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: const Color(0xFF2E7D32),
                              ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: const Color(0xFF2E7D32)),
                  const SizedBox(height: 16),
                  OutputRenderer(markdownContent: content),
                ],
              ),
            ),
          );
        }

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (blockLabel.isNotEmpty) ...[
                  Text(
                    blockLabel,
                    style: Theme.of(context).textTheme.titleMedium,
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
          final events = blockValue is Map<String, dynamic>
              ? blockValue['events'] as List<dynamic>? ?? []
              : [];
          return ValidationTimelineWidget(title: blockLabel, events: events);
        }

        final items = blockValue is Map<String, dynamic>
            ? blockValue['items'] as List<dynamic>? ?? []
            : [];
        return Card(
          child: Semantics(
            excludeSemantics: Platform.isWindows,
            child: ExpansionTile(
              title: Text(blockLabel),
              children: items.map<Widget>((e) {
                final itemObj = e is Map ? e : {};
                return ListTile(
                  leading: Icon(
                    Icons.source_outlined,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  title: Text(
                    itemObj['source']?.toString() ??
                        AppLocalizations.of(context)!.lblSource,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 4.0),
                    child: Text(itemObj['content']?.toString() ?? ''),
                  ),
                  dense: true,
                );
              }).toList(),
            ),
          ),
        );

      default:
        debugPrint('UI FALLBACK ACTIVATED: Unknown Block Type: $blockType');
        return ErrorView(
          error: "Unknown Block Type: $blockType",
          compact: true,
        );
    }
  }

  void _flattenMap(
    Map<String, dynamic> source,
    Map<String, dynamic> target,
    String prefix,
  ) {
    source.forEach((key, value) {
      final lKey = key.toLowerCase();
      // Skip massive trace fields, inputs, IDs, and raw thoughts or history logs
      if (lKey.contains('thought') ||
          lKey.contains('trace') ||
          lKey.contains('history') ||
          lKey.contains('message') ||
          lKey.contains('token') ||
          lKey == 'inputs' ||
          lKey == 'step_names' ||
          lKey == 'step_results' ||
          lKey.endsWith('_text') || // e.g. history_text, reflection_text
          lKey == 'id' ||
          lKey.endsWith('_id'))
        return;

      // Convert snake_case to PascalCase
      final parts = key.split('_');
      final pascalKey = parts
          .where((p) => p.isNotEmpty)
          .map((p) => p[0].toUpperCase() + p.substring(1))
          .join('');

      // Avoid redundant prefixes (e.g. StepJudgeJudgeScore -> StepJudgeScore)
      String effectiveKey = pascalKey;
      if (prefix.isNotEmpty) {
        if (pascalKey.startsWith(prefix)) {
          effectiveKey = pascalKey;
        } else {
          effectiveKey = '$prefix$pascalKey';
        }
      }

      // Strip UUID prefixes (with optional dashes and optional 'V' or 'v' suffix)
      final uuidRegex = RegExp(
        r'^[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}V?',
        caseSensitive: false,
      );
      effectiveKey = effectiveKey.replaceAll(uuidRegex, '');

      // If the key becomes completely empty, fallback backwards
      if (effectiveKey.isEmpty) effectiveKey = pascalKey;

      if (value is Map) {
        // Skip massive metadata maps or raw tool returns
        if (key == 'metadata' || key == 'tool_calls') return;
        _flattenMap(value as Map<String, dynamic>, target, effectiveKey);
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
        // Skip adding if the EXACT SAME string value is already in the target, preventing workflow traversal repetition
        if (!target.containsValue(strVal)) {
          target[effectiveKey] = value;
        }
      }
    });
  }

  Widget _buildFlatDataView(BuildContext context, Map<String, dynamic> data) {
    final Map<String, dynamic> dataToShow = {};
    try {
      if (data.containsKey('context_variables')) {
        final ctx = data['context_variables'] as Map<String, dynamic>;
        _flattenMap(ctx, dataToShow, '');
      } else if (data.containsKey('step_results')) {
        final steps = data['step_results'] as Map<String, dynamic>;
        _flattenMap(steps, dataToShow, '');
      } else {
        _flattenMap(data, dataToShow, '');
      }
    } catch (e) {
      ProviderScope.containerOf(context)
          .read(loggerServiceProvider)
          .error('Report', 'Flat Report parsing failed: $e', e);
      dataToShow['_info'] =
          AppLocalizations.of(context)?.sharedFlatReportNoData ??
          'Flat Report dataa ei löytynyt tästä ajosta.';
    }

    const encoder = JsonEncoder.withIndent('  ');
    final jsonString = encoder.convert(dataToShow);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: SelectableText(
        jsonString,
        style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
      ),
    );
  }

  Widget _buildRawDataView(BuildContext context, Map<String, dynamic> data) {
    // User specifically requested to see the full raw workflow output data
    // rather than just the narrowed down flat_report.
    final dataToShow = data;

    // Use JsonEncoder to pretty print
    const encoder = JsonEncoder.withIndent('  ');
    final jsonString = encoder.convert(dataToShow);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: SelectableText(
        jsonString,
        style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
      ),
    );
  }
}
