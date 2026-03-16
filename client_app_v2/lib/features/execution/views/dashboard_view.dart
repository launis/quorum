import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';

// Provider to fetch executions using SafeCast (No Freezed API DTOs)
final executionListProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
      // 1. Riverpod SWR Caching (Stale-While-Revalidate)
      // Keep this list in RAM for 5 minutes after leaving the screen.
      // Next time the user quickly navigates back, they see immediate cached data.
      ref.cacheFor(const Duration(minutes: 5));

      final dio = ref.watch(apiClientProvider);
      final response = await dio.get('/execution/executions');

      final List<dynamic> data = SafeCast.safeList(response.data);
      return data.map((e) => SafeCast.safeMap(e)).toList();
    });

class DashboardView extends ConsumerStatefulWidget {
  const DashboardView({super.key});

  @override
  ConsumerState<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends ConsumerState<DashboardView> with RouteAware {
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final route = ModalRoute.of(context);
    if (route != null) {
      routeObserver.subscribe(this, route);
    }
  }

  @override
  void dispose() {
    routeObserver.unsubscribe(this);
    super.dispose();
  }

  @override
  void didPopNext() {
    // Called when the top route has been popped off, and the current route shows up.
    // E.g., user returns from ExecutionView to DashboardView.
    // We aggressively invalidate the cache here so it fetches fresh status.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.invalidate(executionListProvider);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    // 1. Initial aggressive load logic
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        // ref.invalidate(executionListProvider);
      }
    });

    final asyncExecutions = ref.watch(executionListProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.executionsDashboardTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(executionListProvider),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => const NewExecutionRoute().go(context),
        icon: const Icon(Icons.add),
        label: Text(AppLocalizations.of(context)!.newAnalysis),
      ),
      body: asyncExecutions.when(
        data: (executions) {
          if (executions.isEmpty) {
            return Center(
              child: Text(AppLocalizations.of(context)!.noExecutions),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: executions.length,
            itemBuilder: (context, index) {
              final exec = executions[index];
              final id = SafeCast.safeString(exec['id']);
              final status = SafeCast.safeString(exec['status']);
              final workflowId = SafeCast.safeString(exec['workflow_id']);
              final createdAt = SafeCast.safeString(exec['created_at']);

                // Formatting date
              String dateStr = createdAt;
              if (createdAt.isNotEmpty) {
                try {
                  final dt = DateTime.parse(createdAt).toLocal();
                  dateStr =
                      '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
                } catch (_) {}
              }

              // Metrics
              final costEstimate = SafeCast.safeDouble(exec['cost_estimate']);
              final totalTokens = SafeCast.safeInt(exec['total_tokens']);
              
              String metricsStr = '';
               if (totalTokens > 0 || costEstimate > 0) {
                 metricsStr = '\nCost: \$${costEstimate.toStringAsFixed(6)} | Tokens: $totalTokens';
              }

              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(
                    'Workflow: $workflowId',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text('ID: $id\nCreated: $dateStr$metricsStr'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildStatusChip(status),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        tooltip: 'Delete Execution',
                        onPressed: () => _confirmDelete(context, ref, id),
                      ),
                    ],
                  ),
                  isThreeLine: true,
                  onTap: () {
                    // Navigate to details safely using GoRouter codegen
                    if (status.toLowerCase() == 'completed') {
                      ExecutionReportRoute(executionId: id).go(context);
                    } else {
                      ExecutionRoute(executionId: id).go(context);
                    }
                  },
                ),
              );
            },
          );
        },
        error:
            (err, stack) => ErrorView(
              error: err,
              stackTrace: stack,
              onRetry: () => ref.invalidate(executionListProvider),
            ),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    String id,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(AppLocalizations.of(context)!.confirmDeletionTitle),
            content: Text(AppLocalizations.of(context)!.confirmDeletionMessage),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(false),
                child: Text(AppLocalizations.of(context)!.cancel),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                onPressed: () => Navigator.of(ctx).pop(true),
                child: Text(AppLocalizations.of(context)!.delete),
              ),
            ],
          ),
    );

    if (confirmed == true && context.mounted) {
      try {
        final dio = ref.read(apiClientProvider);
        await dio.delete('/execution/executions/$id');
        ref.invalidate(executionListProvider);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                AppLocalizations.of(context)!.executionDeletedSuccessfully,
              ),
            ),
          );
        }
      } catch (e) {
        if (context.mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                l10n.failedToDeleteExecution(errorMsg),
              ),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  Widget _buildStatusChip(String status) {
    Color bgColor = Colors.grey;
    final s = status.toLowerCase();
    if (s == 'completed') bgColor = Colors.green;
    if (s == 'failed') bgColor = Colors.red;
    if (s == 'running' || s == 'pending') bgColor = Colors.blue;

    return Chip(
      label: Text(
        status.toUpperCase(),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
      backgroundColor: bgColor,
      side: BorderSide.none,
    );
  }
}
