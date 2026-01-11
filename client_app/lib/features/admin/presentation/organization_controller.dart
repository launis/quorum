import 'package:client_app/features/admin/data/organization_repository.dart';
import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/core/error/app_error.dart';

part 'organization_controller.g.dart';

@Riverpod(keepAlive: true)
class OrganizationList extends _$OrganizationList {
  @override
  Future<List<Organization>> build() async {
    return _fetchOrganizations();
  }

  Future<List<Organization>> _fetchOrganizations() async {
    final repository = ref.watch(organizationRepositoryProvider);
    final result = await repository.fetchOrganizations();

    return result.fold((error) => throw error, (orgs) => orgs);
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchOrganizations());
  }

  Future<void> addOrganization(Map<String, dynamic> data) async {
    final repository = ref.read(organizationRepositoryProvider);
    state = const AsyncValue.loading();

    final result = await repository.createOrganization(data);

    result.fold(
      (error) => state = AsyncValue.error(error, StackTrace.current),
      (_) => refresh(),
    );
  }

  Future<void> updateOrganization(String id, Map<String, dynamic> data) async {
    final repository = ref.read(organizationRepositoryProvider);
    state = const AsyncValue.loading();

    final result = await repository.updateOrganization(id, data);

    result.fold(
      (error) => state = AsyncValue.error(error, StackTrace.current),
      (_) => refresh(),
    );
  }

  Future<AppError?> deleteOrganization(String id, {bool force = false}) async {
    final repository = ref.read(organizationRepositoryProvider);
    final previousState = state;
    state = const AsyncValue.loading();

    final result = await repository.deleteOrganization(id, force: force);

    return result.fold(
      (error) {
        // Special handling for 409 Conflict (ORG_HAS_USERS)
        // Note: validation is done in UI based on error code/message.
        // We just ensure state is restored so UI can check the error.

        // Always restore list state to previous (success) state instead of refreshing
        // This keeps the UI stable while dialog is shown, regardless of error type.
        state = previousState;

        return error;
      },
      (_) {
        refresh();
        return null;
      },
    );
  }
}
