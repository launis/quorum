import 'package:flutter/material.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/xai_report.dart';
import 'package:client_app/features/orchestration/domain/models/evaluation_result.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card_radar.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/feedback_section.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/deep_dive_expander.dart';
import 'package:client_app/features/orchestration/presentation/widgets/output_renderer.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/audit_trail_viewer.dart';

class ResultDashboard extends StatelessWidget {
  final Execution execution;

  const ResultDashboard({super.key, required this.execution});

  @override
  Widget build(BuildContext context) {
    if (execution is! ExecutionCompleted) {
      return const Center(child: Text('Analysis not completed.'));
    }

    final rawResult = (execution as ExecutionCompleted).result;
    
    // --- Parse XAI Report with Fallbacks ---
    // --- Parse XAI Report with Fallbacks ---
    XAIReport? xaiReport;
    try {
        dynamic xaiData;
        
    		    // Strategy 1: Top-level (Direct)
		    if (rawResult.containsKey('step_xai')) {
		         xaiData = rawResult['step_xai'];
             debugPrint('DEBUG: Found step_xai (Strategy 1): $xaiData');
		    }
		    // Strategy 2: Nested in 'step_results' (Standard Workflow Output)
		    else if (rawResult.containsKey('step_results')) {
		         final stepResults = rawResult['step_results'];
             debugPrint('DEBUG: Found step_results (Strategy 2): ${stepResults.keys}');
		         if (stepResults is Map && stepResults.containsKey('step_xai')) {
		             xaiData = stepResults['step_xai'];
                 debugPrint('DEBUG: Found step_xai inside step_results: $xaiData');
		         } else {
                 debugPrint('DEBUG: step_xai NOT found in step_results.');
             }
		    } else {
             debugPrint('DEBUG: No step_xai and no step_results found in rawResult. Keys: ${rawResult.keys}');
        }

		    if (xaiData != null && xaiData is Map<String, dynamic>) {
		         xaiReport = XAIReport.fromJson(xaiData);
             debugPrint('DEBUG: Successfully parsed XAIReport. ScoreCards count: ${xaiReport.scoreCards.length}');
             if (xaiReport.scoreCards.isEmpty) {
                 debugPrint('DEBUG: XAIReport parsed but scoreCards is empty! Raw xaiData["score_cards"]: ${xaiData["score_cards"]}');
             }
		    } else if (xaiData != null) {
            debugPrint('DEBUG: xaiData found but is not a Map: $xaiData');
        }
    } catch (e) {
        debugPrint('XAIReport parsing failed: $e');
    }

    // If we have a robust XAI Report with ScoreCards, show the new Dashboard.
    final bool useV2Dashboard = xaiReport != null && xaiReport.scoreCards.isNotEmpty;

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.dashboard_outlined), text: 'License'),
              Tab(icon: Icon(Icons.data_object_outlined), text: 'Raw Data'),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                // Tab 1: Cognitive License Dashboard
                useV2Dashboard 
                    ? _buildCognitiveDashboard(context, xaiReport!) 
                    : const Center(child: Text("Report format not supported or incomplete.")),
                
                // Tab 2: Raw Audit Trail & Deep Dives
                _buildRawDataView(context, rawResult, xaiReport),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // --- V2 Dashboard Builder ---
  Widget _buildCognitiveDashboard(BuildContext context, XAIReport report) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
            // 1. Executive Header
            _buildExecutiveHeader(context, report),
            const SizedBox(height: 24),

            // 2. Score Cards (Judges)
            Text(
                "Evaluation Matrices",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...report.scoreCards.map((card) => ScoreCardRadar(card: card)),
            const SizedBox(height: 24),

            // 3. Coaching & Recommendations
            _buildCoachingSection(context, report),
            const SizedBox(height: 24),

            // 4. Markdown Report (Formatted)
            if (report.xaiReportFormatted != null)
                DeepDiveExpander(
                    title: 'Full Analysis Report',
                    icon: Icons.article_outlined,
                    initiallyExpanded: false,
                    child: OutputRenderer(markdownContent: report.xaiReportFormatted!),
                ),
            const SizedBox(height: 48),
        ],
      ),
    );
  }
  Widget _buildExecutiveHeader(BuildContext context, XAIReport report) {
      final colorScheme = Theme.of(context).colorScheme;
      
      // Determine color based on confidence
      final confidence = report.confidenceScore;
      final Color statusColor = confidence > 0.8 
            ? Colors.green 
            : (confidence > 0.5 ? Colors.orange : Colors.red);

      return Card(
          elevation: 2,
          color: colorScheme.surfaceContainer,
          child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                  children: [
                      Text(
                          report.finalVerdict.toUpperCase(),
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.w900,
                              color: statusColor,
                              letterSpacing: 1.2,
                          ),
                          textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      Text(
                          report.executiveSummary,
                          style: Theme.of(context).textTheme.bodyLarge,
                          textAlign: TextAlign.center,
                      ),
                      const Divider(height: 32),
                      Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                              _metric(context, "Confidence", "${(confidence * 100).toInt()}%"),
                              _metric(context, "Valid Checksum", report.semanttinenTarkistussumma.substring(0, 6)),
                              _metric(context, "Version", report.metadata['versio']?.toString() ?? "2.0"),
                          ],
                      )
                  ],
              ),
          ),
      );
  }

  Widget _metric(BuildContext context, String label, String value) {
      return Column(
          children: [
              Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              Text(label, style: Theme.of(context).textTheme.labelSmall),
          ],
      );
  }

  Widget _buildCoachingSection(BuildContext context, XAIReport report) {
      // Parse recommendations if they are newline separated or similar, 
      // but XAIReport definition says fields like analysisRecommendations are Strings blocks.
      // We might want to render them as Markdown or split them.
      // For now, using FeedbackSection which expects List<String>.
      
      // Heuristic splitting if it's a markdown list
      List<String> splitMarkdownList(String text) {
          return text.split('\n')
              .map((e) => e.trim())
              .where((e) => e.startsWith('- ') || e.startsWith('* '))
              .map((e) => e.substring(2))
              .toList();
      }

      final recs = splitMarkdownList(report.analysisRecommendations);
      final opps = splitMarkdownList(report.analysisOpportunities);

      return Column(
          children: [
              if (recs.isEmpty && report.analysisRecommendations.isNotEmpty) 
                  // Fallback if not a list
                  _simpleCard(context, "Recommendations", report.analysisRecommendations, Colors.blue),

              if (recs.isNotEmpty)
                FeedbackSection(
                    title: 'Recommendations',
                    items: recs,
                    color: Colors.blue[700],
                    icon: Icons.rocket_launch_outlined,
                ),
            
              const SizedBox(height: 16),

              if (opps.isNotEmpty)
                FeedbackSection(
                    title: 'Opportunities',
                    items: opps,
                    color: Colors.amber[800],
                    icon: Icons.lightbulb_outline,
                ),
          ],
      );
  }
  
  Widget _simpleCard(BuildContext context, String title, String content, Color? color) {
      return Card(
          child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                      Row(children: [
                          Icon(Icons.info_outline, color: color),
                          const SizedBox(width: 8),
                          Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                      ]),
                      const SizedBox(height: 8),
                      Text(content),
                  ],
              ),
          ),
      );
  }

  // --- Raw Data View (Similar to Old Dashboard) ---
  Widget _buildRawDataView(BuildContext context, Map<String, dynamic> data, XAIReport? report) {
      // Reuses parts of the old dashboard or just the Audit Trail + Deep Dives
      return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
              children: [
                  AuditTrailViewer(data: data),
                  const SizedBox(height: 24),
                  if (report != null) ...[
                      DeepDiveExpander(
                          title: "Methodological Log",
                          icon: Icons.history_edu,
                          child: Text(report.metodologinenLoki),
                      ),
                  ]
              ],
          ),
      );
  }


}
