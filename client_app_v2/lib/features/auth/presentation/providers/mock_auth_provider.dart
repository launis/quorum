import 'package:flutter_riverpod/flutter_riverpod.dart';

final mockTokenProvider = NotifierProvider<MockTokenNotifier, String?>(
  MockTokenNotifier.new,
);

class MockTokenNotifier extends Notifier<String?> {
  @override
  String? build() => null;
  void setToken(String? token) => state = token;
}
