import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/router/router.dart';

// Provider to fetch executions using SafeCast (No Freezed API DTOs)
final executionListProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
      final dio = ref.watch(apiClientProvider);
      final response = await dio.get('/execution/executions');

      final List<dynamic> data = SafeCast.safeList(response.data);
      return data.map((e) => SafeCast.safeMap(e)).toList();
    });

class DashboardView extends ConsumerWidget {
  const DashboardView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncExecutions = ref.watch(executionListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Executions Dashboard'),
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
        label: const Text('New Analysis'),
      ),
      body: asyncExecutions.when(
        data: (executions) {
          if (executions.isEmpty) {
            return const Center(child: Text('No executions found.'));
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

              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(
                    'Workflow: $workflowId',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text('ID: $id\nCreated: $dateStr'),
                  trailing: _buildStatusChip(status),
                  isThreeLine: true,
                  onTap: () {
                    // Navigate to details safely using GoRouter codegen
                    ExecutionRoute(executionId: id).go(context);
                  },
                ),
              );
            },
          );
        },
        error:
            (err, stack) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    'Failed to load executions:\n$err',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => ref.invalidate(executionListProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
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
