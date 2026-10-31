import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'env.g.dart';

/// **Environment Configuration Service**
///
/// Manages environment-specific variables and configuration secrets.
/// This abstraction ensures the app is not hardcoded to specific URLs or keys,
/// facilitating movement between Dev and Production.
///
/// **Source**:
/// Loads values from the `.env` file via `flutter_dotenv`.
///
/// **Business Logic**:
/// - Enforces the Zero-Compromise Pledge (Fail-Fast) by requiring all variables
///   to be present in the `.env` file. No silent fallbacks exist.
@Riverpod(keepAlive: true)
Env env(Ref ref) {
  return const Env();
}

class Env {
  const Env();

  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  static String _requireNonEmpty(String key) {
    if (!dotenv.isInitialized) {
      throw AppException.validation(
        'Fail-Fast: Environment configuration is not initialized when reading $key.',
      );
    }
    final raw = dotenv.env[key];
    if (raw == null || raw.trim().isEmpty) {
      throw AppException.validation(
        '$key environment variable is missing from .env.',
      );
    }
    return raw.trim();
  }

  static String _requireMockUserId(String key) {
    final value = _requireNonEmpty(key);
    final validated = _idValidator.fromJson(value);
    if (!validated.startsWith('usr_')) {
      throw AppException.validation(
        'Invalid Opaque User ID prefix for $key: "$validated". Expected "usr_" prefix.',
      );
    }
    return validated;
  }

  /// The base URL for the Python Backend API.
  static String get apiUrl => _requireNonEmpty('API_URL');

  /// The active environment mode (specifically: development or production).
  static String get environment => _requireNonEmpty('ENVIRONMENT');

  /// Whether mock tokens are allowed in the current environment.
  static bool get allowMockTokens =>
      dotenv.isInitialized &&
      dotenv.env['ENVIRONMENT']?.trim() == 'development';

  /// Centralized Mock User IDs from .env enforced via 32-hex UUIDv7 validation.
  static String get mockAdminUserId => _requireMockUserId('MOCK_ADMIN_USER_ID');

  static String get mockRootUserId => _requireMockUserId('MOCK_ROOT_USER_ID');

  static String get mockAnalystUserId =>
      _requireMockUserId('MOCK_ANALYST_USER_ID');

  static String get mockMemberUserId =>
      _requireMockUserId('MOCK_MEMBER_USER_ID');

  static String get mockViewerUserId =>
      _requireMockUserId('MOCK_VIEWER_USER_ID');
}
