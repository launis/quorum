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
import 'package:client_app/features/orchestration/presentation/widgets/sdui/specialist_section.dart';
import 'package:client_app/core/ui/error_view.dart';

class ResultDashboard extends ConsumerStatefulWidget {
  final Execution execution;

  const ResultDashboard({super.key, required this.execution});

  @override
  ConsumerState<ResultDashboard> createState() => _ResultDashboardState();
}

class _ResultDashboardState extends ConsumerState<ResultDashboard> {
  late Future<SemanticReport> _reportViewFuture;

  @override
  void initState() {
    super.initState();
    _reportViewFuture = _fetchReportView();
  }

  Future<SemanticReport> _fetchReportView() async {
    final execId = widget.execution.id;
    debugPrint('Fetching ReportView for $execId via Repository (Auth)');

    // Use the Authenticated Repository via Riverpod
    final task = ref.read(executionRepositoryProvider).getReportView(execId);

    // Run with 15s timeout to prevent infinite spinner
    final result = await task.run().timeout(
      const Duration(seconds: 15),
      onTimeout:
          () =>
              throw Exception(
                'Aikakatkaisu: Palvelin ei vastannut 15 sekuntiin.',
              ),
    );

    return result.fold((error) {
      debugPrint('Error fetching report view: $error');
      throw Exception(error.toString());
    }, (view) => view);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.execution is! ExecutionCompleted) {
      return const Center(child: Text('Analysis not completed.'));
    }

    final rawResult = (widget.execution as ExecutionCompleted).result;

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
                FutureBuilder<SemanticReport>(
                  future: _reportViewFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Center(child: CircularProgressIndicator());
                    } else if (snapshot.hasError) {
                      return Center(child: Text("Virhe: ${snapshot.error}"));
                    } else if (!snapshot.hasData) {
                      return const Center(
                        child: Text("Raporttia ei löytynyt."),
                      );
                    }
                    return _buildDynamicDashboard(context, snapshot.data!);
                  },
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
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Card(
        elevation: 1,
        child: ExpansionTile(
          initiallyExpanded: true,
          leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
          title: Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          children:
              refs.map((ref) {
                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 8.0,
                  ),
                  title: Text(
                    (ref.title != null && ref.title!.isNotEmpty)
                        ? '${ref.id} - ${ref.title}'
                        : ref.id,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (ref.snippet.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          ref.snippet,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      if (ref.url != null && ref.url!.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          ref.url!,
                          style: const TextStyle(
                            color: Colors.blue,
                            decoration: TextDecoration.underline,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                );
              }).toList(),
        ),
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
          ],
        ),
      ),
    );
  }

  Widget _renderBlock(
    BuildContext context,
    SemanticBlock block,
    SemanticReport view,
  ) {
    switch (block.type) {
      case BlockType.card:
        try {
          if (block.value != null && block.value is Map && (block.value as Map).containsKey('dimensions')) {
            final card = ScoreCardItem.fromJson(block.value as Map<String, dynamic>);
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
          data: block.value is Map<String, dynamic> ? block.value as Map<String, dynamic> : {},
          metrics: view.metrics,
        );

      case BlockType.metric:
        return GenericGrid(title: block.label ?? '', data: block.value is Map<String, dynamic> ? block.value as Map<String, dynamic> : {});

      case BlockType.dataGrid:
        return GenericTable(title: block.label ?? '', data: block.value is Map<String, dynamic> ? block.value as Map<String, dynamic> : {});

      case BlockType.paragraph:
        final content = block.value is Map<String, dynamic> ? (block.value as Map<String, dynamic>)['content'] as String? ?? '' : block.value?.toString() ?? '';
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
          final events = block.value is Map<String, dynamic> ? (block.value as Map<String, dynamic>)['events'] as List<dynamic>? ?? [] : [];
          return Card(
            child: Semantics(
              excludeSemantics: Platform.isWindows,
              child: ExpansionTile(
                title: Text(block.label ?? ''),
                children: events.map<Widget>((e) {
                  final ts = e['timestamp'] as String? ?? '';
                  String timeDisplay = ts;
                  if (ts.length >= 16) {
                    final tIndex = ts.indexOf('T');
                    if (tIndex != -1 && tIndex + 5 < ts.length) {
                      timeDisplay = ts.substring(tIndex + 1, tIndex + 6);
                    }
                  }

                  return ListTile(
                    leading: Container(
                      width: 50,
                      alignment: Alignment.centerRight,
                      child: Text(
                        timeDisplay,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    title: Text(
                      e['label'] ?? '',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(e['content'] ?? ''),
                    dense: true,
                  );
                }).toList(),
              ),
            ),
          );
        }

        final items = block.value is Map<String, dynamic> ? (block.value as Map<String, dynamic>)['items'] as List<dynamic>? ?? [] : [];
        return Card(
          child: Semantics(
            excludeSemantics: Platform.isWindows,
            child: ExpansionTile(
              title: Text(block.label ?? ''),
              children: items.map<Widget>((e) {
                return ListTile(
                  leading: const Icon(
                    Icons.source_outlined,
                    color: Colors.blueGrey,
                  ),
                  title: Text(
                    e['source']?.toString() ?? 'Lähdetieto',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(e['content']?.toString() ?? ''),
                  dense: true,
                );
              }).toList(),
            ),
          ),
        );

      default:
        debugPrint(
          'UI FALLBACK ACTIVATED: Unknown Block Type: ${block.type}',
        );
        return ErrorView(
          error: "Unknown Block Type: ${block.type}",
          compact: true,
        );
    }
  }

  Widget _buildFlatDataView(BuildContext context, Map<String, dynamic> data) {
    // Extract XAIFlatReportDTO if available, otherwise show empty/error
    Map<String, dynamic>? flatReport;
    try {
      if (data.containsKey('context_variables')) {
        final ctx = data['context_variables'] as Map<String, dynamic>;
        if (ctx.containsKey('step_xai') && ctx['step_xai'] is Map) {
          final stepXai = ctx['step_xai'] as Map<String, dynamic>;
          if (stepXai.containsKey('flat_report') &&
              stepXai['flat_report'] is Map) {
            flatReport = stepXai['flat_report'] as Map<String, dynamic>;
          }
        }
      } else if (data.containsKey('step_results')) {
        final steps = data['step_results'] as Map<String, dynamic>;
        if (steps.containsKey('step_xai') && steps['step_xai'] is Map) {
          final stepXai = steps['step_xai'] as Map<String, dynamic>;
          if (stepXai.containsKey('flat_report') &&
              stepXai['flat_report'] is Map) {
            flatReport = stepXai['flat_report'] as Map<String, dynamic>;
          }
        }
      }
    } catch (e) {
      debugPrint('Koko datan parsiminen flat_reportia varten epäonnistui: $e');
    }

    final dataToShow =
        flatReport ?? {'_info': 'Flat Report dataa ei löytynyt tästä ajosta.'};

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
