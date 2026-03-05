import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'dart:convert';
import 'dart:io';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_grid.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_table.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card_radar.dart';
import 'package:client_app/features/orchestration/domain/models/xai_report.dart'; // Provides ScoreCardItem
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';

import 'package:client_app/features/orchestration/presentation/widgets/output_renderer.dart';
import 'package:client_app/features/orchestration/presentation/widgets/validation_timeline_widget.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/specialist_section.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

final reportViewProvider = FutureProvider.autoDispose.family<SemanticReport, String>((ref, execId) async {
  debugPrint('Fetching ReportView for $execId via Repository (Auth)');
  final task = ref.watch(executionRepositoryProvider).getReportView(execId);
  final result = await task.run().timeout(
    const Duration(seconds: 15),
    onTimeout: () => throw Exception('Aikakatkaisu: Palvelin ei vastannut 15 sekuntiin.'),
  );
  return result.fold(
    (error) {
      debugPrint('Error fetching report view: $error');
      throw Exception(error.toString());
    },
    (view) => view,
  );
});

class ResultDashboard extends ConsumerWidget {
  final Execution execution;

  const ResultDashboard({super.key, required this.execution});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (execution is! ExecutionCompleted) {
      return const Center(child: Text('Analysis not completed.'));
    }

    final rawResult = (execution as ExecutionCompleted).result;
    final reportAsync = ref.watch(reportViewProvider(execution.id));

    return DefaultTabController(
      length: 3,
      child: Column(
        children: [
          const TabBar(
            labelColor: Colors.blue,
            unselectedLabelColor: Colors.grey,
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
                reportAsync.when(
                  data: (view) => _buildDynamicDashboard(context, view),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => Center(child: Text("Virhe: $error")),
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

  Widget _buildDynamicDashboard(BuildContext context, SemanticReport view) {
    // 1. SDUI Protocol: We respect backend signals without string parsing
    final bool isHitlRequired = view.metrics?['hitl_required'] == true;
    final bool hasWarning = view.metrics?['has_warning'] == true;

    final bool showWarning = isHitlRequired || hasWarning;

    // We only display feedback exactly as given by backend
    final String? feedback =
        view.metrics?['coach_feedback']?.toString() ??
        view.metrics?['warning_message']?.toString();

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
          if (view.systemNotification != null) ...[
            _buildSystemNotificationBanner(context, view.systemNotification!),
            const SizedBox(height: 24),
          ],
          ...view.blocks.map((block) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 24.0),
              child: _renderBlock(context, block, view),
            );
          }),
          if (view.references.isNotEmpty) ...[
            const Divider(height: 48),
            _buildReferencesSection(context, view.references),
          ],
        ],
      ),
    );
  }

  Widget _buildReferencesSection(
    BuildContext context,
    List<ReferenceItem> references,
  ) {
    // Group by intent
    final searchRefs =
        references.where((r) => r.intent == ReferenceIntent.search).toList();
    final groundRefs =
        references.where((r) => r.intent == ReferenceIntent.grounding).toList();
    final kbRefs =
        references
            .where((r) => r.intent == ReferenceIntent.internalKb)
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
    List<ReferenceItem> refs,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24.0),
      child: Container(
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(8.0),
          border: Border.all(color: Colors.grey.withOpacity(0.2)),
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
            ...refs.map((ref) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (ref.title != null && ref.title!.isNotEmpty)
                          ? '${ref.id} - ${ref.title}'
                          : ref.id,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14.0,
                        height: 1.4,
                      ),
                    ),
                    if (ref.snippet.isNotEmpty) ...[
                      const SizedBox(height: 6.0),
                      Text(
                        ref.snippet,
                        style: const TextStyle(
                          fontSize: 13.0,
                          color: Colors.black87,
                          height: 1.5,
                        ),
                        softWrap: true,
                        overflow: TextOverflow.visible,
                      ),
                    ],
                    if (ref.url != null && ref.url!.isNotEmpty) ...[
                      const SizedBox(height: 6.0),
                      InkWell(
                        onTap: () {
                          // Allow copying URL in a real app or use url_launcher
                        },
                        child: Text(
                          ref.url!,
                          style: const TextStyle(
                            color: Colors.blue,
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
    SystemNotification notification,
  ) {
    final isDanger = notification.level == 'danger';
    final bgColor = isDanger ? Colors.red[50] : Colors.orange[50];
    final borderColor = isDanger ? Colors.red : Colors.orange;
    final iconColor = isDanger ? Colors.red[800] : Colors.orange[800];
    final textColor = isDanger ? Colors.red[900] : Colors.deepOrange[900];

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        border: Border(left: BorderSide(color: borderColor!, width: 4)),
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
                  notification.title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: iconColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            notification.message,
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

  Widget _buildHeader(BuildContext context, SemanticReport view) {
    Color statusColor = Colors.grey;
    if (view.intent == SemanticIntent.success)
      statusColor = Colors.green;
    else if (view.intent == SemanticIntent.warning)
      statusColor = Colors.orange;
    else if (view.intent == SemanticIntent.danger)
      statusColor = Colors.red;

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
              view.title.toUpperCase(),
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: statusColor,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Tulostettu: ${_formatDateTime(DateTime.now())}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
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
    SemanticBlock block,
    SemanticReport view,
  ) {
    switch (block.type) {
      case BlockType.card:
        try {
          if (block.value != null &&
              block.value is Map &&
              (block.value as Map).containsKey('dimensions')) {
            final card = ScoreCardItem.fromJson(
              block.value as Map<String, dynamic>,
            );
            return ScoreCardRadar(card: card);
          }
        } catch (e) {
          return ErrorView(
            error: "Error rendering ScoreCard: $e",
            compact: true,
          );
        }
        return SpecialistSection(
          title: block.label ?? '',
          type: block.id,
          data:
              block.value is Map<String, dynamic>
                  ? block.value as Map<String, dynamic>
                  : {},
          metrics: view.metrics,
        );

      case BlockType.metric:
        return GenericGrid(
          title: block.label ?? '',
          data:
              block.value is Map<String, dynamic>
                  ? block.value as Map<String, dynamic>
                  : {},
        );

      case BlockType.dataGrid:
        return GenericTable(
          title: block.label ?? '',
          data:
              block.value is Map<String, dynamic>
                  ? block.value as Map<String, dynamic>
                  : {},
        );

      case BlockType.paragraph:
        final content =
            block.value is Map<String, dynamic>
                ? (block.value as Map<String, dynamic>)['content'] as String? ??
                    ''
                : block.value?.toString() ?? '';

        if (block.id == 'coach-markdown') {
          return Card(
            elevation: 2,
            margin: const EdgeInsets.only(bottom: 16.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.green[50]!, Colors.teal[50]!],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.green[200]!, width: 2),
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
                          color: Colors.green[600],
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.psychology_alt,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          block.label?.isNotEmpty == true
                              ? block.label!
                              : AppLocalizations.of(context)!.stepCoach,
                          style: Theme.of(
                            context,
                          ).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.green[900],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: Colors.green),
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
                if (block.label != null && block.label!.isNotEmpty) ...[
                  Text(
                    block.label!,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const Divider(),
                ],
                OutputRenderer(markdownContent: content),
              ],
            ),
          ),
        );

      case BlockType.list:
        if (block.id == 'timeline-feed') {
          final events =
              block.value is Map<String, dynamic>
                  ? (block.value as Map<String, dynamic>)['events']
                          as List<dynamic>? ??
                      []
                  : [];
          return ValidationTimelineWidget(
            title: block.label ?? '',
            events: events,
          );
        }

        final items =
            block.value is Map<String, dynamic>
                ? (block.value as Map<String, dynamic>)['items']
                        as List<dynamic>? ??
                    []
                : [];
        return Card(
          child: Semantics(
            excludeSemantics: Platform.isWindows,
            child: ExpansionTile(
              title: Text(block.label ?? ''),
              children:
                  items.map<Widget>((e) {
                    return ListTile(
                      leading: const Icon(
                        Icons.source_outlined,
                        color: Colors.blueGrey,
                      ),
                      title: Text(
                        e['source']?.toString() ?? AppLocalizations.of(context)!.lblSource,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Text(e['content']?.toString() ?? ''),
                      ),
                      dense: true,
                    );
                  }).toList(),
            ),
          ),
        );

      default:
        debugPrint('UI FALLBACK ACTIVATED: Unknown Block Type: ${block.type}');
        return ErrorView(
          error: "Unknown Block Type: ${block.type}",
          compact: true,
        );
    }
  }

  void _flattenMap(Map<String, dynamic> source, Map<String, dynamic> target, String prefix) {
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
          lKey.endsWith('_id')) return;
          
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
      final uuidRegex = RegExp(r'^[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}V?', caseSensitive: false);
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
      debugPrint('Koko datan parsiminen flat_reportia varten epäonnistui: $e');
      dataToShow['_info'] = 'Flat Report dataa ei löytynyt tästä ajosta.';
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
