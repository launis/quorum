import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'env.g.dart';

/// **Environment Configuration Service**
///
/// Manages environment-specific variables and configuration secrets.
/// This abstraction ensures the app is not hardcoded to specific URLs or keys,
/// facilitating movement between Dev (localhost), Staging, and Production.
///
/// **Source**:
/// Loads values from the `.env` file via `flutter_dotenv`.
///
/// **Business Logic**:
/// - Enforces the Zero-Compromise Pledge (Fail-Fast) by requiring all variables
///   to be present in the `.env` file. No silent fallbacks exist.
@riverpod
Env env(Ref ref) {
  return Env();
}

class Env {
  /// The base URL for the Python Backend API.
  ///
  /// Examples:
  /// - Local: `http://127.0.0.1:8000`
  /// - Prod: `https://api.cognitivequorum.com`
  static String get apiUrl {
    final url = dotenv.env['API_URL'];
    if (url == null || url.isEmpty) {
      throw AppException.validation('API_URL environment variable is missing from .env.');
    }
    return url;
  }
}

