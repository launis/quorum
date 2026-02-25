import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/usage/data/usage_repository.dart';
import 'package:client_app/features/usage/domain/models/usage_report.dart';

part 'usage_controller.g.dart';

@riverpod
class SystemUsageController extends _$SystemUsageController {
  @override
  Future<UsageReport> build() async {
    return _fetchUsage();
  }

  Future<UsageReport> _fetchUsage() async {
    final repository = ref.watch(usageRepositoryProvider);
    final result = await repository.fetchSystemUsage();
    return result.fold((error) => throw error, (report) => report);
  }

  Future<void> refresh() async {
    // 1. Optimistic / Silent Invalidation Pattern (Keep current state visible)
    state = const AsyncValue.loading();
    // 2. Fetch new data
    state = await AsyncValue.guard(() => _fetchUsage());
  }
}

@riverpod
class OrganizationUsageController extends _$OrganizationUsageController {
  @override
  Future<UsageReport> build(String orgId) async {
    return _fetchUsage(orgId);
  }

  Future<UsageReport> _fetchUsage(String orgId) async {
    final repository = ref.watch(usageRepositoryProvider);
    final result = await repository.fetchOrganizationUsage(orgId);
    return result.fold((error) => throw error, (report) => report);
  }

  Future<void> refresh() async {
    // 1. Optimistic / Silent Invalidation Pattern
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchUsage(orgId));
  }
}

@riverpod
class UserUsageController extends _$UserUsageController {
  @override
  Future<UsageReport> build() async {
    return _fetchUsage();
  }

  Future<UsageReport> _fetchUsage() async {
    final repository = ref.watch(usageRepositoryProvider);
    final result = await repository.fetchUserUsage();
    return result.fold((error) => throw error, (report) => report);
  }

  Future<void> refresh() async {
    // 1. Optimistic / Silent Invalidation Pattern
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchUsage());
  }
}
