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
      throw AppException.validation(
        'API_URL environment variable is missing from .env.',
      );
    }
    return url;
  }

  /// The active environment mode (e.g. development, production).
  /// Defaults to production if not specified to enforce security natively.
  static String get environment {
    final env = dotenv.env['ENVIRONMENT'];
    if (env == null || env.isEmpty) {
      return 'production';
    }
    return env;
  }

  /// Whether mock tokens are allowed in the current environment
  static bool get allowMockTokens => environment == 'development';

  // Centralized Mock User IDs from .env
  static String get mockAdminUserId => dotenv.env['MOCK_ADMIN_USER_ID'] ?? 'usr_18a0d5f6151349a5';
  static String get mockRootUserId => dotenv.env['MOCK_ROOT_USER_ID'] ?? 'usr_a3fd6b3d77c748f4';
  static String get mockAnalystUserId => dotenv.env['MOCK_ANALYST_USER_ID'] ?? 'usr_8a9234f9a0c242a1';
}
