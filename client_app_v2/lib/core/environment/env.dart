import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
/// - Provides a safe fallback for the `API_URL` to `http://localhost:8000` to ensure
///   local development works out-of-the-box.
class Env {
  /// The base URL for the Python Backend API.
  ///
  /// Examples:
  /// - Local: `http://localhost:8000`
  /// - Prod: `https://api.cognitivequorum.com`
  static String get apiUrl => dotenv.env['API_URL'] ?? 'http://127.0.0.1:8000';
}

final envProvider = Provider<Env>((ref) => Env());
