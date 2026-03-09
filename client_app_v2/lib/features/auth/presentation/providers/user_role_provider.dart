import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';

final userRoleProvider = Provider<UserRole>((ref) {
  final authState = ref.watch(authControllerProvider);
  return authState.value?.role ?? UserRole.viewer;
});
