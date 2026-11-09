import 'dart:async';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_user_provider.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_controller.g.dart';

// Mandatory 2FA Challenge/Enrollment, 13-Minute Silent Refresh, and 5-Step Logout Pipeline.

/// Coordinates tenant-scoped master data caches for invalidation on tenant switch or sign-out.
@riverpod
Future<void> masterData(Ref ref) async {}

/// Holds active 2FA challenge or mandatory first-time TOTP enrollment state during authentication.
@Riverpod(keepAlive: true)
class MfaSessionController extends _$MfaSessionController {
  @override
  MfaPendingState build() => const MfaPendingState();

  void setPendingState(MfaPendingState pending) {
    state = pending;
  }

  void reset() {
    state = const MfaPendingState();
  }
}

/// **Authentication Controller**
///
/// Manages global authentication state, mandatory 2FA challenge/enrollment,
/// 13-minute silent background token exchange, and the 5-step cryptographic logout pipeline.
@Riverpod(keepAlive: true)
class AuthController extends _$AuthController {
  Timer? _refreshTimer;
  String? _lastOrganizationId;

  /// Interval for silent background JWT refresh (minute 13, 2 minutes before 15-minute expiry).
  static const Duration silentRefreshInterval = Duration(minutes: 13);

  bool get hasActiveRefreshTimer =>
      _refreshTimer != null && _refreshTimer!.isActive;

  @override
  FutureOr<User?> build() async {
    ref.onDispose(() {
      _refreshTimer?.cancel();
      _refreshTimer = null;
    });

    final mockUser = ref.read(mockUserProvider);
    if (mockUser != null) {
      _lastOrganizationId = mockUser.organizationId;
      return mockUser;
    }

    final firebaseUser = await ref
        .read(authRepositoryProvider)
        .authStateChanges()
        .first;
    if (firebaseUser == null) return null;

    final result = await ref.read(userRepositoryProvider).fetchCurrentUser();
    return result.fold((error) => null, (user) {
      _lastOrganizationId = user.organizationId;
      return user;
    });
  }

  /// Orchestrates first-factor login, mandatory 2FA challenge/enrollment detection, and token exchange.
  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();

    final repo = ref.read(authRepositoryProvider);
    final result = await repo.signInWithEmailAndPassword(email, password);

    await result.fold(
      (error) async {
        if (error.errorCode == 'MFA_CHALLENGE_REQUIRED' ||
            error.errorCode == 'MFA_REQUIRED') {
          final pending = repo.pendingMfaState;
          if (pending != null) {
            ref
                .read(mfaSessionControllerProvider.notifier)
                .setPendingState(pending);
          }
          // Keep user unauthenticated until second factor is verified.
          state = const AsyncData(null);
          return;
        }
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (exchangeDto) async {
        await _applyAuthenticatedSession(exchangeDto);
      },
    );
  }

  /// Completes a 6-digit TOTP 2FA challenge and upgrades the session via `/iam/auth/exchange`.
  Future<void> verifyMfaChallenge(String totpCode) async {
    final result = await ref
        .read(authRepositoryProvider)
        .resolveMfaChallenge(totpCode);

    await result.fold(
      (error) async {
        throw error;
      },
      (exchangeDto) async {
        await _applyAuthenticatedSession(exchangeDto);
      },
    );
  }

  /// Completes mandatory first-time TOTP 2FA enrollment and upgrades the session via `/iam/auth/exchange`.
  Future<void> completeMfaEnrollment(String totpCode) async {
    final result = await ref
        .read(authRepositoryProvider)
        .completeTotpEnrollment(totpCode);

    await result.fold(
      (error) async {
        throw error;
      },
      (exchangeDto) async {
        await _applyAuthenticatedSession(exchangeDto);
      },
    );
  }

  /// Aborts an in-progress 2FA challenge or enrollment flow and returns to the primary sign-in form.
  Future<void> cancelMfaFlow() async {
    ref.read(authRepositoryProvider).clearPendingMfaState();
    ref.read(mfaSessionControllerProvider.notifier).reset();
    await ref.read(authRepositoryProvider).signOut();
    state = const AsyncData(null);
  }

  /// Applies a [TokenExchangeResponseDto] (from login or JIT task onboarding) to active session state.
  Future<void> applyTokenExchangeResponse(
    TokenExchangeResponseDto exchangeDto,
  ) async {
    await _applyAuthenticatedSession(exchangeDto);
  }

  /// Executes a silent background token refresh at `/api/v2/iam/auth/exchange`.
  Future<void> performSilentRefresh() async {
    final result = await ref.read(authRepositoryProvider).refreshSession();

    await result.fold(
      (error) async {
        ref
            .read(loggerServiceProvider)
            .warning(
              'AuthController',
              'Silent token refresh failed: ${error.detail}',
            );
      },
      (exchangeDto) async {
        if (_lastOrganizationId != null &&
            _lastOrganizationId != exchangeDto.user.organizationId) {
          _invalidateTenantProviders();
        }
        _lastOrganizationId = exchangeDto.user.organizationId;
        ref.read(mockTokenProvider.notifier).setToken(exchangeDto.accessToken);
        ref.read(mockUserProvider.notifier).setUser(exchangeDto.user);
        state = AsyncData(exchangeDto.user);
      },
    );
  }

  /// Updates the current user's profile state optimistically and rolls back on failure.
  void setOptimisticUser(User updatedUser) {
    if (_lastOrganizationId != null &&
        _lastOrganizationId != updatedUser.organizationId) {
      _invalidateTenantProviders();
    }
    _lastOrganizationId = updatedUser.organizationId;
    ref.read(mockUserProvider.notifier).setUser(updatedUser);
    state = AsyncData(updatedUser);
  }

  /// Deterministic 5-Step Logout Pipeline (`POST /api/v2/iam/auth/logout` + multi-tenant cache purge).
  Future<void> signOut({bool revokeAllSessions = false}) async {
    // 1. Cancel Background Refresh Timer First
    _refreshTimer?.cancel();
    _refreshTimer = null;

    final currentJwt = ref.read(mockTokenProvider);

    try {
      // 2. Bounded Server-Side Token Revocation (POST /api/v2/iam/auth/logout)
      if (currentJwt != null && currentJwt.trim().isNotEmpty) {
        await ref
            .read(authRepositoryProvider)
            .revokeServerSession(revokeAllSessions: revokeAllSessions);
      }
    } on DioException catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .warning(
            'AuthController',
            'Server logout request failed or JWT expired; completing local session destruction: ${e.message}\n$st',
          );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .warning(
            'AuthController',
            'Unexpected error during server logout; completing local session destruction: $e\n$st',
          );
    } finally {
      // 3. IdP & Local Credential Destruction
      try {
        await ref.read(authRepositoryProvider).signOut();
      } catch (e, st) {
        ref
            .read(loggerServiceProvider)
            .warning(
              'AuthController',
              'Firebase signOut warning during local cleanup: $e\n$st',
            );
      }
      ref.read(mockTokenProvider.notifier).setToken(null);
      ref.read(mockUserProvider.notifier).setUser(null);
      ref.read(mfaSessionControllerProvider.notifier).reset();
      _lastOrganizationId = null;

      // 4. Multi-Tenant Memory Cache Purge (tenant_data_isolation)
      _invalidateTenantProviders();

      // 5. Atomic Auth State Reset & GoRouter Redirect
      state = const AsyncData(null);
    }
  }

  Future<void> _applyAuthenticatedSession(
    TokenExchangeResponseDto exchangeDto,
  ) async {
    if (_lastOrganizationId != null &&
        _lastOrganizationId != exchangeDto.user.organizationId) {
      _invalidateTenantProviders();
    }
    _lastOrganizationId = exchangeDto.user.organizationId;

    ref.read(mockTokenProvider.notifier).setToken(exchangeDto.accessToken);
    ref.read(mockUserProvider.notifier).setUser(exchangeDto.user);
    ref.read(mfaSessionControllerProvider.notifier).reset();

    await ref
        .read(settingsControllerProvider.notifier)
        .syncFromUserProfile(
          language: exchangeDto.user.language,
          themeMode: exchangeDto.user.themeMode,
        );

    _scheduleSilentRefresh();
    state = AsyncData(exchangeDto.user);
  }

  void _scheduleSilentRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(silentRefreshInterval, (_) {
      unawaited(performSilentRefresh());
    });
  }

  void _invalidateTenantProviders() {
    ref.invalidate(masterDataProvider);
    ref.invalidate(allBlueprintsProvider);
    ref.invalidate(stepsControllerProvider);
    ref.invalidate(outputProfilesControllerProvider);
    ref.invalidate(executionListProvider);
    ref.invalidate(availableWorkflowsProvider);
    ref.invalidate(workflowsControllerProvider);
    ref.invalidate(promptBlocksControllerProvider);
  }
}
