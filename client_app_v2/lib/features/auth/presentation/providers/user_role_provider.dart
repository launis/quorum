import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';

part 'user_role_provider.g.dart';

@Riverpod(keepAlive: true)
UserRole userRole(Ref ref) {
  final authState = ref.watch(authControllerProvider);
  return authState.value?.role ?? UserRole.viewer;
}
