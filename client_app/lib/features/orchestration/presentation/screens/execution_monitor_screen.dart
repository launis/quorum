import 'package:client_app/features/orchestration/domain/models/assessment_view.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/presentation/widgets/execution_timeline.dart';
import 'package:client_app/core/ui/error_view.dart';

class ExecutionMonitorScreen extends ConsumerStatefulWidget {
  final String executionId;

  const ExecutionMonitorScreen({super.key, required this.executionId});

  @override
  ConsumerState<ExecutionMonitorScreen> createState() =>
      _ExecutionMonitorScreenState();
}

class _ExecutionMonitorScreenState extends ConsumerState<ExecutionMonitorScreen>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // 1. Auto-Refresh logic on Resume (Wake from sleep)
    if (state == AppLifecycleState.resumed) {
      _refresh();
    }
  }

  void _refresh() {
    // Force invalidation of the specific execution stream
    ref.invalidate(assessmentStreamProvider(widget.executionId));
  }

  @override
  Widget build(BuildContext context) {
    final asyncExecution = ref.watch(
      assessmentStreamProvider(widget.executionId),
    );
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.monitorTitle(widget.executionId.substring(0, 8))),
        actions: [
          // 2. Manual Refresh Button
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: l10n.refresh,
            onPressed: _refresh,
          ),
        ],
      ),
      body: asyncExecution.when(
        data: (assessment) {
          // Auto-redirect if completed (logic might need adjustment based on AssessmentView fields)
          // For now, checks if finalScore is present or specific statusLabel
          if (assessment.finalScore != null) {
            // ...
          }
          return _MonitorView(assessment: assessment);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) {
          final errorText = err.toString();
          // Check for Not Found error (either by code or type name)
          if (errorText.contains('404') ||
              errorText.contains('notFound') ||
              errorText.contains('Resource not found')) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.search_off, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text(
                    l10n.executionNotFound,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text('This execution may have been deleted.'),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: () => context.go('/dashboard'),
                    icon: const Icon(Icons.arrow_back),
                    label: const Text('Back to Dashboard'),
                  ),
                ],
              ),
            );
          }
          return ErrorView(
            error: err,
            onRetry: _refresh,
            retryLabel: l10n.retry,
          );
        },
      ),
      floatingActionButton:
          asyncExecution.asData?.value.uiVariant == 'success'
              ? FloatingActionButton.extended(
                onPressed:
                    () => context.go(
                      '/dashboard/executions/${widget.executionId}/report',
                    ),
                label: Text(l10n.viewResults),
                icon: const Icon(Icons.arrow_forward),
                backgroundColor: Colors.green,
              )
              : null,
    );
  }
}

class _MonitorView extends StatelessWidget {
  final AssessmentView assessment;

  const _MonitorView({required this.assessment});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final color = _getVariantColor(assessment.uiVariant);
    final isRunning =
        assessment.statusLabel.toLowerCase().contains("analysoidaan") ||
        assessment.statusLabel.contains("..."); // Heuristic or explicit field?

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1000),
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            // Status Card
            Card(
              color: color.withValues(alpha: 0.1),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    ListTile(
                      leading:
                          isRunning
                              ? SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 3,
                                  color: color,
                                ),
                              )
                              : Icon(
                                _getVariantIcon(assessment.uiVariant),
                                color: color,
                                size: 32,
                              ),
                      title: Text(
                        assessment.statusLabel,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      subtitle: Text(assessment.statusMessage),
                    ),
                    if (assessment.showWarningBanner)
                      Container(
                        margin: const EdgeInsets.only(top: 16),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.orange.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.orange),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.warning_amber,
                              color: Colors.orange,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                "Warning: Non-standard conditions detected.",
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),

            // Steps Progress (Timeline)
            if (assessment.steps.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: Text(
                  "Vaiheet",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              ExecutionTimeline(steps: assessment.steps, compact: true),
            ],

            if (assessment.uiVariant == 'success') ...[
              const SizedBox(height: 16),
              _CompletionBanner(executionId: assessment.sessionId),
            ],
            const SizedBox(height: 16),

            // Hint for raw data
            Center(
              child: TextButton.icon(
                icon: const Icon(Icons.code),
                label: Text(l10n.viewRawDataComingSoon),
                onPressed: () {
                  // Placeholder for raw data modal or route
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getVariantColor(String variant) {
    return switch (variant) {
      'success' => Colors.green,
      'warning' => Colors.orange,
      'error' => Colors.red,
      _ => Colors.blue, // default/info
    };
  }

  IconData _getVariantIcon(String variant) {
    return switch (variant) {
      'success' => Icons.check_circle,
      'warning' => Icons.warning,
      'error' => Icons.error,
      _ => Icons.info,
    };
  }
}

class _CompletionBanner extends StatelessWidget {
  final String executionId;

  const _CompletionBanner({required this.executionId});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.withValues(alpha: 0.5)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  l10n.analysisCompletedSuccess,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Colors.green,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed:
                  () => context.go('/dashboard/executions/$executionId/report'),
              icon: const Icon(Icons.visibility),
              label: Text(l10n.viewFullReport),
              style: FilledButton.styleFrom(backgroundColor: Colors.green),
            ),
          ),
        ],
      ),
    );
  }
}
