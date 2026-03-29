import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'mock_auth_provider.g.dart';

@Riverpod(keepAlive: true)
class MockToken extends _$MockToken {
  @override
  String? build() => null;
  void setToken(String? token) => state = token;
}
