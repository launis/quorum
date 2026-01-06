import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/auth_interceptor.dart';

part 'mock_auth_provider.g.dart';

/// **Mock Token Provider**
///
/// Stores the 'fake' JWT token when running in Debug/Mock mode without Firebase.
/// This allows the [AuthInterceptor] to sign requests with `mock-token:uid`.
@riverpod
class MockToken extends _$MockToken {
  @override
  String? build() {
    return null; // Default: No mock token
  }

  void setToken(String? token) {
    state = token;
  }
}
