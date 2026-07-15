import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
// import 'package:client_app/features/execution/models/global_synthesis_dto.dart';
// import 'package:client_app/features/execution/views/widgets/sdui_node_renderer.dart';
// import 'package:client_app/l10n/gen/app_localizations.dart';
// import 'package:client_app/core/theme/app_spacing.dart';
// import 'package:client_app/shared/widgets/output_renderer.dart';

// Phase 3, Step 2: Create ReportRendererV2Widget
class ReportRendererV2Widget extends StatelessWidget {
  final ReportDataDto payload;
  final String executionId;

  const ReportRendererV2Widget({
    super.key,
    required this.payload,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      primary: false,
      children: [
        // Phase 3, Step 2: Build globalSynthesis and globalMetrics summary
        // TODO(Phase C4): Migrate to content_blocks for synthesis and results
        // if (payload.globalSynthesis != null)
        //   _buildExecutiveSummary(context, payload.globalSynthesis!),

        // ...payload.results.map(
        //   (atom) => Padding(
        //     padding: const EdgeInsets.only(
        //       bottom: AppSpacing.s8,
        //       left: AppSpacing.s16,
        //       right: AppSpacing.s16,
        //     ),
        //     child: SduiNodeRenderer(executionId: executionId, result: atom),
        //   ),
        // ),

        // [BLOCKED] Phase 3, Step 2: Integrate DiagnosticScorecardWidget and XAIEvidenceBox
        // Architectural Contradiction: Phase 1 models (ReportDataDto) do not contain
        // evaluativeMatrices, informationalMatrices, or mcpToolAudit data, so these widgets
        // cannot be rendered or passed the required DTOs natively without violating
        // strict schema mapping.
      ],
    );
  }

  // Widget _buildExecutiveSummary(
  //   BuildContext context,
  //   GlobalSynthesisDTO synthesis,
  // ) {
  //   if (synthesis.executiveSummary == null ||
  //       synthesis.executiveSummary!.isEmpty) {
  //     return const SizedBox.shrink(); // Allowed here only as conditional omission, not error hiding.
  //   }
  //
  //   return Padding(
  //     padding: AppSpacing.p16,
  //     child: Column(
  //       crossAxisAlignment: CrossAxisAlignment.start,
  //       children: [
  //         Text(
  //           AppLocalizations.of(context)!.reportExecutiveSummary,
  //           style: const TextStyle(
  //             fontSize: 22,
  //             fontWeight: FontWeight.bold,
  //             letterSpacing: -0.5,
  //           ),
  //         ),
  //         AppSpacing.h16,
  //         Container(
  //           width: double.infinity,
  //           padding: AppSpacing.p16,
  //           decoration: BoxDecoration(
  //             color: Colors.white,
  //             border: Border(
  //               left: BorderSide(
  //                 color: Theme.of(context).primaryColor,
  //                 width: 4,
  //               ),
  //             ),
  //             boxShadow: [
  //               BoxShadow(
  //                 color: Colors.black.withValues(alpha: 0.05),
  //                 blurRadius: 4,
  //                 offset: const Offset(0, 2),
  //               ),
  //             ],
  //           ),
  //           child: OutputRenderer(markdownContent: synthesis.executiveSummary!),
  //         ),
  //         if (synthesis.urgencyLevel != null) ...[
  //           AppSpacing.h16,
  //           Text(
  //             'Urgency Level: ${synthesis.urgencyLevel}',
  //             style: const TextStyle(fontWeight: FontWeight.bold),
  //           ),
  //         ],
  //       ],
  //     ),
  //   );
  // }
}
