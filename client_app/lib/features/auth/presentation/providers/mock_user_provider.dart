import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'mock_user_provider.g.dart';

@Riverpod(keepAlive: true)
class MockUser extends _$MockUser {
  @override
  User? build() {
    return null;
  }

  void setUser(User? user) {
    state = user;
  }
}
