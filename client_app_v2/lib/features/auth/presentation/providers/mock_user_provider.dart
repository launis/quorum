import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final mockUserProvider = NotifierProvider<MockUserNotifier, User?>(
  MockUserNotifier.new,
);

class MockUserNotifier extends Notifier<User?> {
  @override
  User? build() => null;
  void setUser(User? user) => state = user;
}
