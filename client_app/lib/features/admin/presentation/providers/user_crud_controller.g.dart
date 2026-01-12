// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_crud_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **User CRUD Controller**
///
/// Manages the state of user creation, update, and deletion operations.
/// Uses riverpod_generator for type-safe provider generation.

@ProviderFor(UserCrudController)
final userCrudControllerProvider = UserCrudControllerProvider._();

/// **User CRUD Controller**
///
/// Manages the state of user creation, update, and deletion operations.
/// Uses riverpod_generator for type-safe provider generation.
final class UserCrudControllerProvider
    extends $AsyncNotifierProvider<UserCrudController, void> {
  /// **User CRUD Controller**
  ///
  /// Manages the state of user creation, update, and deletion operations.
  /// Uses riverpod_generator for type-safe provider generation.
  UserCrudControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'userCrudControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$userCrudControllerHash();

  @$internal
  @override
  UserCrudController create() => UserCrudController();
}

String _$userCrudControllerHash() =>
    r'96f8f7169ffeb6ec5ff5cd3f54354ac54a509294';

/// **User CRUD Controller**
///
/// Manages the state of user creation, update, and deletion operations.
/// Uses riverpod_generator for type-safe provider generation.

abstract class _$UserCrudController extends $AsyncNotifier<void> {
  FutureOr<void> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<void>, void>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<void>, void>,
              AsyncValue<void>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
