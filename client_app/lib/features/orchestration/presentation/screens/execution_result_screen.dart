import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/result_dashboard.dart';
import 'package:go_router/go_router.dart';
import 'package:printing/printing.dart';
import 'package:client_app/features/orchestration/presentation/services/pdf_report_generator.dart';
import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:client_app/app_config.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ExecutionResultScreen extends ConsumerWidget {
  final String executionId;

  const ExecutionResultScreen({super.key, required this.executionId});

  Future<void> _downloadPdf(BuildContext context, WidgetRef ref, String executionId) async {
     try {
       // Fetch Data (Re-using logic from ResultDashboard ideally, but for now fetching here)
       // Optimization: Could cache the ReportView in a provider to avoid re-fetch.
       final url = Uri.parse('${AppConfig.apiBaseUrl}/executions/$executionId/view');
       final response = await http.get(url);
       
       if (response.statusCode != 200) {
         throw Exception('Failed to fetch report data');
       }
       
       final jsonMap = json.decode(utf8.decode(response.bodyBytes));
       final view = ReportView.fromJson(jsonMap);

       // Generate PDF
       final generator = PdfReportGenerator();
       final pdfBytes = await generator.generate(view);

       // Print / Share
       await Printing.layoutPdf(
         onLayout: (format) async => pdfBytes,
         name: 'Audit_Report_$executionId.pdf',
       );

     } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Virhe PDF luonnissa: $e')),
          );
        }
     }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // We assume the user shouldn't be here if it's running,
    // but we can still watch it. Logically we might not need polling here,
    // but executionStreamProvider handles it.
    final asyncExecution = ref.watch(executionStreamProvider(executionId));
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.resultsTitle),
        actions: [
          // Actions
          IconButton(
            onPressed: () => _downloadPdf(context, ref, executionId),
            icon: const Icon(Icons.download),
            tooltip: l10n.downloadReportTooltip,
          ),
        ],

      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: asyncExecution.when(
            data: (execution) {
              if (execution is ExecutionCompleted) {
                return ResultDashboard(execution: execution);
              } else {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(l10n.analysisNotComplete),
                      const SizedBox(height: 16),
                      FilledButton.icon(
                        onPressed:
                            () => context.go(
                              '/dashboard/executions/$executionId/monitor',
                            ),
                        icon: const Icon(Icons.visibility),
                        label: Text(l10n.goToMonitor),
                      ),
                    ],
                  ),
                );
              }
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error:
                (err, stack) => Center(child: Text(l10n.failedToLoad('$err'))),
          ),
        ),
      ),
    );
  }
}
