import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'env.g.dart';

@Riverpod(keepAlive: true)
Env env(Ref ref) {
  return Env();
}

class Env {
  Env() {
    _init();
  }

  void _init() {
    // Note: dotenv.load() must be called in main.dart before using this
    final apiUrl = dotenv.env['API_URL'];
    if (apiUrl == null || apiUrl.isEmpty) {
      throw Exception('CRITICAL: API_URL is missing from .env');
    }
  }

  String get apiUrl => dotenv.env['API_URL']!;
}
