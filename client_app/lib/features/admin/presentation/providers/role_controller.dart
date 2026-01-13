import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'role_controller.g.dart';

@riverpod
Future<List<UserRole>> assignableRoles(Ref ref) async {
  final repository = ref.watch(adminRepositoryProvider);
  final result = await repository.fetchAssignableRoles();

  return result.fold(
    (error) =>
        [], // Return empty on error or handle differently? Empty safe for UI fallback (shows nothing vs crashing)
    (roles) => roles,
  );
}
