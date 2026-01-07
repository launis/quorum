import 'package:flutter/material.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/feedback_section.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/deep_dive_expander.dart';
import 'package:client_app/features/orchestration/presentation/widgets/output_renderer.dart';

// New Visualizations
import 'package:client_app/features/orchestration/presentation/widgets/results/comparison_matrix.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/evidence_dashboard.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/pre_mortem_card.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/audit_trail_viewer.dart';

class ResultDashboard extends StatelessWidget {
  final Execution execution;

  const ResultDashboard({super.key, required this.execution});

  @override
  Widget build(BuildContext context) {
    // Only render if completed and has result
    if (execution is! ExecutionCompleted) {
      return const Center(child: Text('Analysis not completed.'));
    }

    final rawResult = (execution as ExecutionCompleted).result;
    final data = Map<String, dynamic>.from(rawResult);

    final reportRaw = data['Report'];
    final report =
        (reportRaw is Map)
            ? Map<String, dynamic>.from(reportRaw)
            : <String, dynamic>{};

    final sysStatusRaw = data['System_Status'];
    final sysStatus =
        (sysStatusRaw is Map)
            ? Map<String, dynamic>.from(sysStatusRaw)
            : <String, dynamic>{};

    // Check for Dual Matrix Data (Comparison)
    // Logic from renderer.py: Check comparison_data in Report OR in Raw_Steps fallback
    Map<String, dynamic>? comparisonData;
    if (report['comparison_data'] != null) {
      comparisonData = Map<String, dynamic>.from(
        report['comparison_data'] as Map,
      );
    } else {
      // Fallback logic
      final raw = data['Raw_Steps'] as Map<String, dynamic>?;
      final stepRep = raw?['step_reporter'] as Map<String, dynamic>?;
      if (stepRep?['comparison_data'] != null) {
        comparisonData = Map<String, dynamic>.from(
          stepRep!['comparison_data'] as Map,
        );
      }
    }

    // Matrix Mode logic:
    // If comparisonData exists, we prefer rendering Matrix over standard Scores
    final bool showDualMatrix = comparisonData != null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // 1. High Level Verdict
          _buildVerdictSection(context, report, sysStatus),
          const SizedBox(height: 24),

          // 2. Scores OR Matrix
          if (showDualMatrix) ...[
            ComparisonMatrix(comparisonData: comparisonData),
          ] else ...[
            _buildScoresSection(context, report),
          ],
          const SizedBox(height: 24),

          // 3. Feedback
          _buildFeedbackSection(context, report),
          const SizedBox(height: 24),

          // 4. Evidence & Logic (New)
          EvidenceDashboard(report: report),
          const SizedBox(height: 16),

          // 5. Pre-Mortem (New)
          PreMortemCard(report: report),
          const SizedBox(height: 16),

          // 6. Profile & Interaction
          _buildProfileAndInteraction(context, data, report),
          const SizedBox(height: 16),

          // 7. Full Report (Deep Dive)
          _buildDeepDive(context, data, report),
          const SizedBox(height: 16),

          // 8. Audit Trail (Log)
          AuditTrailViewer(data: data),
          const SizedBox(height: 48), // Bottom padding
        ],
      ),
    );
  }

  Widget _buildVerdictSection(
    BuildContext context,
    Map<String, dynamic> report,
    Map<String, dynamic> sysStatus,
  ) {
    final verdict = report['final_verdict'] as String? ?? 'N/A';
    final reliability =
        (report['confidence'] is num)
            ? ((report['confidence'] as num) * 100).toInt()
            : 0;
    final risk = sysStatus['riski_taso'] as String? ?? 'N/A';

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text('Verdict', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 4),
            Text(
              verdict,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).primaryColor,
              ),
              textAlign: TextAlign.center,
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildMetric(context, 'Reliability', '$reliability%'),
                _buildMetric(context, 'Risk Level', risk),
                _buildMetric(
                  context,
                  'System Status',
                  sysStatus['status'] as String? ?? 'Done',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetric(BuildContext context, String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }

  Widget _buildScoresSection(
    BuildContext context,
    Map<String, dynamic> report,
  ) {
    final scoresRaw = report['scores'] ?? report['pisteet'];
    if (scoresRaw == null || scoresRaw is! Map) return const SizedBox.shrink();

    final scores = Map<String, dynamic>.from(scoresRaw);

    // Max scale
    final sMax = (report['scale_max'] as num?)?.toDouble() ?? 5.0;

    // Filter valid keys
    final entries =
        scores.entries.where((e) => !e.key.endsWith('_selitys')).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Evaluation Scores',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2, // 2 columns mostly ok
            childAspectRatio: 1.8,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: entries.length,
          itemBuilder: (context, index) {
            final entry = entries[index];
            final label = entry.key.replaceAll('_', ' ').toUpperCase();

            // Handle value
            double val = 0;
            String? desc;

            if (entry.value is num) {
              val = (entry.value as num).toDouble();
            } else if (entry.value is Map) {
              val = ((entry.value as Map)['arvosana'] as num? ?? 0).toDouble();
              desc = (entry.value as Map)['perustelu'] as String?;
            }

            // Try to find separate explanation
            if (desc == null && scores.containsKey('${entry.key}_selitys')) {
              desc = scores['${entry.key}_selitys'] as String?;
            }

            return ScoreCard(
              label: label,
              value: val,
              maxValue: sMax,
              description: desc,
            );
          },
        ),
      ],
    );
  }

  Widget _buildFeedbackSection(
    BuildContext context,
    Map<String, dynamic> report,
  ) {
    // Explicitly handle list casting safely
    final actionsRaw = report['kehitystoimenpiteet'];
    final actions =
        (actionsRaw is List)
            ? actionsRaw.map((e) => e.toString()).toList()
            : <String>[];

    final recsRaw = report['kehitysehdotukset'];
    final recs =
        (recsRaw is List)
            ? recsRaw.map((e) => e.toString()).toList()
            : <String>[];

    return Column(
      children: [
        FeedbackSection(
          title: 'Coaching Actions',
          items: actions,
          color: Colors.amber[800],
          icon: Icons.school_outlined,
        ),
        if (actions.isNotEmpty) const SizedBox(height: 16),
        FeedbackSection(
          title: 'Recommendations',
          items: recs,
          color: Colors.blue[700],
          icon: Icons.rocket_launch_outlined,
        ),
      ],
    );
  }

  Widget _buildProfileAndInteraction(
    BuildContext context,
    Map<String, dynamic> data,
    Map<String, dynamic> report,
  ) {
    // Fallback logic
    var profileRaw = report['psykologinen_profiili'];
    var interactionRaw = report['vuorovaikutus_analyysi'];

    final raw = data['Raw_Steps'] as Map<String, dynamic>? ?? {};

    if (profileRaw == null && raw['step_profiler'] != null) {
      profileRaw = raw['step_profiler'];
    }
    if (interactionRaw == null && raw['step_interaction'] != null) {
      interactionRaw = raw['step_interaction'];
    }

    if (profileRaw == null && interactionRaw == null) {
      return const SizedBox.shrink();
    }

    final profile =
        (profileRaw is Map) ? Map<String, dynamic>.from(profileRaw) : null;
    final interaction =
        (interactionRaw is Map)
            ? Map<String, dynamic>.from(interactionRaw)
            : null;

    return Column(
      children: [
        if (profile != null) ...[
          DeepDiveExpander(
            title: 'Psychological Profile',
            icon: Icons.psychology,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _keyValue(
                  'Profile',
                  (profile['psykologinen_profiili'] ?? profile['profiili'])
                      as String?,
                ),
                _keyValue(
                  'Intent',
                  (profile['intentio_analyysi'] ?? profile['intentio'])
                      as String?,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Biases:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                _buildStringList(
                  profile['tunnistetut_vinoumat'] ?? profile['vinoumat'],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],
        if (interaction != null) ...[
          DeepDiveExpander(
            title: 'Interaction Dynamics',
            icon: Icons.hub,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _keyValue(
                  'Role',
                  (interaction['driver_classification'] ?? interaction['rooli'])
                      as String?,
                ),
                _keyValue(
                  'Control Ratio',
                  '${interaction['input_control_ratio'] ?? interaction['control_ratio'] ?? 0}',
                ),
                const SizedBox(height: 8),
                const Text(
                  'Strategies:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                _buildStringList(
                  interaction['tunnistetut_strategiat'] ??
                      interaction['strategiat'],
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  // Helper to safely build list of text widgets from dynamic list
  Widget _buildStringList(dynamic listRaw) {
    if (listRaw is! List || listRaw.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          listRaw.map((b) {
            if (b is Map) {
              return Text('• ${b['nimi']}: ${b['selitys']}');
            }
            return Text('• $b');
          }).toList(),
    );
  }

  Widget _buildDeepDive(
    BuildContext context,
    Map<String, dynamic> data,
    Map<String, dynamic> report,
  ) {
    // XAI Report
    String? xai = report['xai_report_formatted'] as String?;

    // Fallback 1: Try other keys in Report
    if (xai == null || xai.isEmpty) {
      xai = report['xai_report'] as String?;
    }

    // Fallback 2: Check Raw_Steps (step_xai or step_reporter)
    if (xai == null || xai.isEmpty) {
      final raw = data['Raw_Steps'] as Map?;
      if (raw != null) {
        final stepXai = raw['step_xai'] as Map?;
        final stepRep = raw['step_reporter'] as Map?;

        if (stepXai != null) {
          xai =
              stepXai['xai_report_formatted'] as String? ??
              stepXai['final_report'] as String?;
        }
        if ((xai == null || xai.isEmpty) && stepRep != null) {
          xai =
              stepRep['xai_report_formatted'] as String? ??
              stepRep['final_report'] as String?;
        }
      }
    }

    return DeepDiveExpander(
      title: 'Full Analysis Report (Markdown)',
      icon: Icons.description_outlined,
      initiallyExpanded: false,
      child:
          (xai != null && xai.isNotEmpty)
              ? OutputRenderer(markdownContent: xai)
              : const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'No detailed report content available (xai_report_formatted missing).',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    color: Colors.grey,
                  ),
                ),
              ),
    );
  }

  Widget _keyValue(String key, String? value) {
    if (value == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$key: ', style: const TextStyle(fontWeight: FontWeight.bold)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
