import 'package:client_app/core/environment/env.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Centralized application configuration facade.
///
/// Delegates API endpoint resolution strictly to [Env.apiUrl] as the Single
/// Source of Truth so no localhost, emulator loopback, or placeholder URLs are
/// hardcoded in client source files.
class AppConfig {
  const AppConfig._();

  /// Resolves and validates the canonical backend API base URL from [Env.apiUrl].
  ///
  /// Throws [AppException.validation] if the environment has not been
  /// initialized or if `API_URL` is missing or not a valid HTTP/HTTPS URI.
  static String get apiBaseUrl {
    if (!dotenv.isInitialized) {
      throw AppException.validation(
        'Fail-Fast: Environment configuration is not initialized.',
      );
    }
    return validateApiBaseUrl(Env.apiUrl);
  }

  /// Validates and normalizes a raw API base URL string.
  ///
  /// Strips trailing slashes so downstream path joins remain deterministic,
  /// and enforces an explicit `http` or `https` scheme with a non-empty host.
  static String validateApiBaseUrl(String rawUrl) {
    var normalized = rawUrl.trim();
    while (normalized.endsWith('/')) {
      normalized = normalized.replaceRange(
        normalized.length - 1,
        normalized.length,
        '',
      );
    }

    if (normalized.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: API_URL cannot be empty or whitespace.',
      );
    }

    final uri = Uri.tryParse(normalized);
    if (uri == null ||
        !uri.hasScheme ||
        (uri.scheme != 'http' && uri.scheme != 'https') ||
        uri.host.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Invalid API_URL configuration: "$rawUrl". Expected an absolute http or https URI.',
      );
    }

    return normalized;
  }
}
