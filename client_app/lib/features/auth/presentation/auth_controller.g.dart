// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Authentication Controller**
///
/// Manages the global authentication state of the application.

@ProviderFor(AuthController)
final authControllerProvider = AuthControllerProvider._();

/// **Authentication Controller**
///
/// Manages the global authentication state of the application.
final class AuthControllerProvider
    extends $StreamNotifierProvider<AuthController, User?> {
  /// **Authentication Controller**
  ///
  /// Manages the global authentication state of the application.
  AuthControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authControllerHash();

  @$internal
  @override
  AuthController create() => AuthController();
}

String _$authControllerHash() => r'33b813b7a342da87e1bbf54fd7c22fdf91c96d62';

/// **Authentication Controller**
///
/// Manages the global authentication state of the application.

abstract class _$AuthController extends $StreamNotifier<User?> {
  Stream<User?> build();
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
