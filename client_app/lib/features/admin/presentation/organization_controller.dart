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
    final previousState = state;
    // 1. Optimistic Update
    // We try to keep the list visible. Ideally we'd append a temp org, 
    // but constructing it from raw map might be fragile without ID.
    // At minimum, we DON'T set state to loading (which hides the list).
    // If we want true optimistic, we'd need Organization.fromMap(data) with temp ID.
    // For now: Keep previous state visible (semi-optimistic).
    
    // state = const AsyncValue.loading(); // REMOVED (Pessimistic)
    
    try {
      // 2. API Call
      final repository = ref.read(organizationRepositoryProvider);
      final result = await repository.createOrganization(data);

      result.fold(
        (error) => throw error, // Trigger catch block
        (_) {
           // 3. Silent Invalidation
           ref.invalidateSelf();
        },
      );
    } catch (e, st) {
      // 4. Rollback / Error
      // If we did a list modification, we'd rollback here.
      // Since we just kept the list, we mainly need to show the error.
      // BUT we need to ensure state isn't stuck if we did something fancy.
      state = AsyncValue.error(e, st);
      // Wait, strict pattern says: Rollback then Rethrow.
      // Since we didn't mutate list, "Rollback" is just ensuring we have data?
      // Actually if we just set error, it replaces the list with error widget!
      // better: state = previousState (Data) + Action Error?
      // Riverpod AsyncValue doesn't support "Data + Side Error" well without generic.
      // So ensuring we rethrow for UI toast is key.
      state = previousState; 
      // We rethrow so the UI can show a SnackBar or Dialog error.
      rethrow;
    }
  }

  Future<void> updateOrganization(String id, Map<String, dynamic> data) async {
    final previousState = state;
    // 1. Optimistic (Keep List Visible)
    
    try {
      // 2. API Call
      final repository = ref.read(organizationRepositoryProvider);
      final result = await repository.updateOrganization(id, data);

      result.fold(
        (error) => throw error,
        (_) => ref.invalidateSelf(), // 3. Silent Invalidation
      );
    } catch (e) {
      // 4. Rollback
      state = previousState;
      rethrow;
    }
  }

  Future<AppError?> deleteOrganization(String id, {bool force = false}) async {
    final previousState = state;
    // 1. Optimistic (Remove from list immediately)
    if (previousState.value != null) {
      state = AsyncValue.data(
        previousState.value!.where((org) => org.id != id).toList()
      );
    }

    try {
      // 2. API Call
      final repository = ref.read(organizationRepositoryProvider);
      final result = await repository.deleteOrganization(id, force: force);

      return result.fold(
        (error) {
           // 4. Rollback on API failure
           state = previousState;
           return error; // Return error for UI handling (Dialog?)
        },
        (_) {
          // 3. Silent Invalidation (Sync)
          ref.invalidateSelf();
          return null;
        },
      );
    } catch (e, st) {
       // 4. Rollback on Exception
       state = previousState;
       // If unexpected exception
       state = AsyncValue.error(e, st);
       // Or return as AppError?
       return AppError.server(e.toString());
    }
  }
}
