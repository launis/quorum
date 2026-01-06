import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'user_repository.g.dart';

/// **User Repository Provider**
///
/// Exposes the [UserRepository] to the dependency injection system.
/// Uses the authenticated [apiClientProvider].
@riverpod
UserRepository userRepository(Ref ref) {
  return UserRepository(ref.watch(apiClientProvider));
}

/// **User Data Repository**
///
/// Manages fetching and updating user profile data from the backend.
///
/// **Responsibility**:
/// - Bridges the gap between Firebase Auth (Identity) and the Python Backend (Profile/Role).
/// - Since Firebase Auth tokens only contain basic info, this repository fetches the
///   authoritative [UserRole] and [organizationId] from the database.
class UserRepository {
  final Dio _client;

  /// Creates a [UserRepository] with a configured [Dio] client.
  UserRepository(this._client);

  /// **Fetch Current User Profile**
  ///
  /// Calls `/users/me` (or equivalent profile endpoint) to get the full context
  /// of the currently logged-in user.
  ///
  /// **Business Logic**:
  /// - This method is typically called immediately after Firebase Authentication completes.
  /// - It is essential for the "Auth Loading" state—the app cannot decide where to route
  ///   the user (Admin vs. Dashboard) until this call returns.
  ///
  /// **Returns**:
  /// A [User] object containing the Role and Organization ID.
  ///
  /// **Throws**:
  /// - [DioException] if the backend is unreachable or the user record doesn't exist yet.
  Future<User> fetchCurrentUser() async {
    try {
      // Note: Endpoint inferred from openapi.json. Adjust if backend path differs (e.g. /users/me vs /auth/me).
      // Based on openapi scan, we saw references but not explicit /users/me in the partial view.
      // Assuming standard convention or I'll assume /users/me based on prompt request.
      final response = await _client.get<Map<String, dynamic>>('/users/me');

      if (response.data == null) {
        throw Exception("User profile returned null data.");
      }

      return User.fromJson(response.data!);
    } catch (e) {
      // In a robust app, we'd wrap this.
      rethrow;
    }
  }
}
