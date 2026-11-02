// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Coordinates tenant-scoped master data caches for invalidation on tenant switch or sign-out.

@ProviderFor(masterData)
final masterDataProvider = MasterDataProvider._();

/// Coordinates tenant-scoped master data caches for invalidation on tenant switch or sign-out.

final class MasterDataProvider
    extends $FunctionalProvider<AsyncValue<void>, void, FutureOr<void>>
    with $FutureModifier<void>, $FutureProvider<void> {
  /// Coordinates tenant-scoped master data caches for invalidation on tenant switch or sign-out.
  MasterDataProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'masterDataProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$masterDataHash();

  @$internal
  @override
  $FutureProviderElement<void> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<void> create(Ref ref) {
    return masterData(ref);
  }
}

String _$masterDataHash() => r'8daba405fccac89e755ccf0642bd19fc9d1856a0';

/// Holds active 2FA challenge or mandatory first-time TOTP enrollment state during authentication.

@ProviderFor(MfaSessionController)
final mfaSessionControllerProvider = MfaSessionControllerProvider._();

/// Holds active 2FA challenge or mandatory first-time TOTP enrollment state during authentication.
final class MfaSessionControllerProvider
    extends $NotifierProvider<MfaSessionController, MfaPendingState> {
  /// Holds active 2FA challenge or mandatory first-time TOTP enrollment state during authentication.
  MfaSessionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'mfaSessionControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$mfaSessionControllerHash();

  @$internal
  @override
  MfaSessionController create() => MfaSessionController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(MfaPendingState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<MfaPendingState>(value),
    );
  }
}

String _$mfaSessionControllerHash() =>
    r'97e562eb4b801516e995e525f0b154a7c1e2a1ab';

/// Holds active 2FA challenge or mandatory first-time TOTP enrollment state during authentication.

abstract class _$MfaSessionController extends $Notifier<MfaPendingState> {
  MfaPendingState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<MfaPendingState, MfaPendingState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<MfaPendingState, MfaPendingState>,
              MfaPendingState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// **Authentication Controller**
///
/// Manages global authentication state, mandatory 2FA challenge/enrollment,
/// 13-minute silent background token exchange, and the 5-step cryptographic logout pipeline.

@ProviderFor(AuthController)
final authControllerProvider = AuthControllerProvider._();

/// **Authentication Controller**
///
/// Manages global authentication state, mandatory 2FA challenge/enrollment,
/// 13-minute silent background token exchange, and the 5-step cryptographic logout pipeline.
final class AuthControllerProvider
    extends $AsyncNotifierProvider<AuthController, User?> {
  /// **Authentication Controller**
  ///
  /// Manages global authentication state, mandatory 2FA challenge/enrollment,
  /// 13-minute silent background token exchange, and the 5-step cryptographic logout pipeline.
  AuthControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authControllerHash();

  @$internal
  @override
  AuthController create() => AuthController();
}

String _$authControllerHash() => r'ec3fb155013bf573954798ee44070101237f5532';

/// **Authentication Controller**
///
/// Manages global authentication state, mandatory 2FA challenge/enrollment,
/// 13-minute silent background token exchange, and the 5-step cryptographic logout pipeline.

abstract class _$AuthController extends $AsyncNotifier<User?> {
  FutureOr<User?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<User?>, User?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<User?>, User?>,
              AsyncValue<User?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
