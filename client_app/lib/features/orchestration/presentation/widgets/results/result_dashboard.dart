
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_grid.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_table.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card_radar.dart';
import 'package:client_app/features/orchestration/domain/models/xai_report.dart'; // Provides ScoreCardItem

import 'package:client_app/features/orchestration/presentation/widgets/output_renderer.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/specialist_section.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/audit_trail_viewer.dart';
import 'package:client_app/app_config.dart';

class ResultDashboard extends StatefulWidget {
  final Execution execution;

  const ResultDashboard({super.key, required this.execution});

  @override
  State<ResultDashboard> createState() => _ResultDashboardState();
}

class _ResultDashboardState extends State<ResultDashboard> {
  late Future<ReportView> _reportViewFuture;

  @override
  void initState() {
    super.initState();
    _reportViewFuture = _fetchReportView();
  }

  Future<ReportView> _fetchReportView() async {
    // 1. If we have the view model directly in execution (future optimization), return it.
    // 2. Otherwise fetch from BFF endpoint.
    final execId = widget.execution.id;
    final url = Uri.parse('${AppConfig.apiBaseUrl}/executions/$execId/view');
    
    debugPrint('Fetching ReportView from: $url');
    
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        // UTF-8 decoding is critical for Finnish characters
        final jsonMap = json.decode(utf8.decode(response.bodyBytes));
        return ReportView.fromJson(jsonMap);
      } else {
        throw Exception('Failed to load report view: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error fetching report view: $e');
      // Fallback: If fetch fails (offline/dev), try to construct it locally? 
      // For now, rethrow to show error state.
      rethrow;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.execution is! ExecutionCompleted) {
      return const Center(child: Text('Analysis not completed.'));
    }

    final rawResult = (widget.execution as ExecutionCompleted).result;

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            labelColor: Colors.blue,
            unselectedLabelColor: Colors.grey,
            tabs: [
              Tab(icon: Icon(Icons.dashboard_outlined), text: 'Raportti'),
              Tab(icon: Icon(Icons.data_object_outlined), text: 'Raaka Data'),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                // Tab 1: Server-Driven Dashboard (BFF)
                FutureBuilder<ReportView>(
                  future: _reportViewFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Center(child: CircularProgressIndicator());
                    } else if (snapshot.hasError) {
                      return Center(child: Text("Virhe: ${snapshot.error}"));
                    } else if (!snapshot.hasData) {
                       return const Center(child: Text("Raporttia ei löytynyt."));
                    }
                    return _buildDynamicDashboard(context, snapshot.data!);
                  },
                ),
                
                // Tab 2: Raw JSON
                _buildRawDataView(context, rawResult),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDynamicDashboard(BuildContext context, ReportView view) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildHeader(context, view),
          const SizedBox(height: 24),
          ...view.sections.map((section) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 24.0),
              child: _renderSection(context, section),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, ReportView view) {
    Color statusColor = Colors.grey;
    if (view.statusTheme == 'success') statusColor = Colors.green;
    else if (view.statusTheme == 'warning') statusColor = Colors.orange;
    else if (view.statusTheme == 'danger') statusColor = Colors.red;

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
                color: statusColor
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _renderSection(BuildContext context, UiSection section) {
    switch (section.type) {
      case 'SCORE_CARD':
        // Fallback or specific renderer? 
        // BFF sends "data" which matches ScoreCard model structure mostly.
        try {
           final card = ScoreCardItem.fromJson(section.data); // Use ScoreCardItem from xai_report.dart
           return ScoreCardRadar(card: card); 
        } catch (e) {
           return Text("Error rendering ScoreCard: $e");
        }

      case 'KEY_VALUE_GRID':
        return GenericGrid(title: section.title, data: section.data);

      case 'DATA_TABLE':
        return GenericTable(title: section.title, data: section.data);

      case 'MARKDOWN_BLOCK':
        final content = section.data['content'] as String? ?? '';
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                    if (section.title.isNotEmpty) ...[
                        Text(section.title, style: Theme.of(context).textTheme.titleMedium),
                        const Divider(),
                    ],
                    OutputRenderer(markdownContent: content),
                ]
            ),
          ),
        );

      case 'TIMELINE_FEED':
        // Reuse AuditTrail logic or simplified list?
        // BFF Timeline is a list of events.
        final events = section.data['events'] as List<dynamic>? ?? [];
        return Card(
             child: ExpansionTile(
                title: Text(section.title),
                children: events.map((e) => ListTile(
                    leading: Text(e['timestamp'] ?? '', style: const TextStyle(fontSize: 10)),
                    title: Text(e['label'] ?? ''),
                    subtitle: Text(e['content'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis),
                )).toList(),
             ),
        );

      // --- Specialist Sections (Backbone) ---
      case 'LOGIC_ANALYSIS':
      case 'STRESS_TEST':
      case 'CAUSAL_ANALYSIS':
      case 'PERFORMATIVITY_CHECK':
      case 'FACT_CHECK':
      case 'PROFILER_ANALYSIS':
      case 'ARCHIVIST_CHECK':
      case 'DRIVER_PROFILE':
        return SpecialistSection(
          title: section.title,
          type: section.type, 
          data: section.data,
        );

      default:
        return Card(
          color: Colors.red[50],
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text("Unknown Section Type: ${section.type}"),
          ),
        );
    }
  }

  Widget _buildRawDataView(BuildContext context, Map<String, dynamic> data) {
      // Use JsonEncoder to pretty print
      const encoder = JsonEncoder.withIndent('  ');
      final jsonString = encoder.convert(data);

      return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: SelectableText(
            jsonString,
            style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
          ),
      );
  }
}
