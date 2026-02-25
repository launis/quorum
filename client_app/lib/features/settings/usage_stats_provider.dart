import 'package:client_app/features/admin/data/organization_repository.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'usage_stats_provider.g.dart';

class UsageStats {
  final double usedCost;
  final double costLimit;
  final int tpmLimit;
  final int rpmLimit;
  final double percentage;
  final String period;
  
  // New telemetry
  final int totalRuns;
  final int totalProcessingTimeMs;
  final Map<String, int> modelsUsed;
  final Map<String, int> workflowsUsed;

  const UsageStats({
    required this.usedCost,
    required this.costLimit,
    required this.tpmLimit,
    required this.rpmLimit,
    required this.percentage,
    required this.period,
    this.totalRuns = 0,
    this.totalProcessingTimeMs = 0,
    this.modelsUsed = const {},
    this.workflowsUsed = const {},
  });
}

// Allow passing scope (e.g. "user", "org", "system") to the provider
@riverpod
Future<UsageStats> usageStats(Ref ref, {String scope = "org"}) async {
  final userAsync = ref.watch(authControllerProvider);
  final user = userAsync.asData?.value;

  if (user == null || user.organizationId == null) {
    // Return empty/zero stats if no user or org
    return const UsageStats(
      usedCost: 0,
      costLimit: 1,
      tpmLimit: 0,
      rpmLimit: 0,
      percentage: 0,
      period: '',
    );
  }

  final repo = ref.watch(organizationRepositoryProvider);
  final result = await repo.getDetailedUsage(user.organizationId!, scope: scope);

  return result.fold(
    (error) => throw error, // Let UI handle error state
    (data) => UsageStats(
      usedCost: (data['total_cost_usd'] as num).toDouble(),
      costLimit: (data['quota_limit_usd'] as num).toDouble(),
      tpmLimit: (data['tpm_limit'] as num).toInt(),
      rpmLimit: (data['rpm_limit'] as num).toInt(),
      percentage: (data['percentage_used'] as num).toDouble() / 100.0,
      period: data['period'] as String,
      totalRuns: (data['total_runs'] as num?)?.toInt() ?? 0,
      totalProcessingTimeMs: (data['total_processing_time_ms'] as num?)?.toInt() ?? 0,
      modelsUsed: (data['models_used'] as Map<String, dynamic>?)?.map((k, v) => MapEntry(k, (v as num).toInt())) ?? {},
      workflowsUsed: (data['workflows_used'] as Map<String, dynamic>?)?.map((k, v) => MapEntry(k, (v as num).toInt())) ?? {},
    ),
  );
}
