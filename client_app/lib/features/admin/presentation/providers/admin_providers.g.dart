// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'admin_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Organization Users Provider**
///
/// Fetches the list of users for a given organization.
/// Used in the User Management screen.

@ProviderFor(orgUsers)
final orgUsersProvider = OrgUsersFamily._();

/// **Organization Users Provider**
///
/// Fetches the list of users for a given organization.
/// Used in the User Management screen.

final class OrgUsersProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<User>>,
          List<User>,
          FutureOr<List<User>>
        >
    with $FutureModifier<List<User>>, $FutureProvider<List<User>> {
  /// **Organization Users Provider**
  ///
  /// Fetches the list of users for a given organization.
  /// Used in the User Management screen.
  OrgUsersProvider._({
    required OrgUsersFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'orgUsersProvider',
         isAutoDispose: false,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$orgUsersHash();

  @override
  String toString() {
    return r'orgUsersProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<User>> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<List<User>> create(Ref ref) {
    final argument = this.argument as String;
    return orgUsers(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is OrgUsersProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$orgUsersHash() => r'6017a77e590240c9cf110a187835a96104a788e2';

/// **Organization Users Provider**
///
/// Fetches the list of users for a given organization.
/// Used in the User Management screen.

final class OrgUsersFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<User>>, String> {
  OrgUsersFamily._()
    : super(
        retry: null,
        name: r'orgUsersProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: false,
      );

  /// **Organization Users Provider**
  ///
  /// Fetches the list of users for a given organization.
  /// Used in the User Management screen.

  OrgUsersProvider call(String orgId) =>
      OrgUsersProvider._(argument: orgId, from: this);

  @override
  String toString() => r'orgUsersProvider';
}

/// **System Queue Stats Provider**
///
/// Polls the backend for queue statistics every 5 seconds.
/// Used in the Dashboard or Admin Panel header.

@ProviderFor(systemQueueStats)
final systemQueueStatsProvider = SystemQueueStatsProvider._();

/// **System Queue Stats Provider**
///
/// Polls the backend for queue statistics every 5 seconds.
/// Used in the Dashboard or Admin Panel header.

final class SystemQueueStatsProvider
    extends
        $FunctionalProvider<
          AsyncValue<QueueStats>,
          QueueStats,
          Stream<QueueStats>
        >
    with $FutureModifier<QueueStats>, $StreamProvider<QueueStats> {
  /// **System Queue Stats Provider**
  ///
  /// Polls the backend for queue statistics every 5 seconds.
  /// Used in the Dashboard or Admin Panel header.
  SystemQueueStatsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'systemQueueStatsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$systemQueueStatsHash();

  @$internal
  @override
  $StreamProviderElement<QueueStats> $createElement($ProviderPointer pointer) =>
      $StreamProviderElement(pointer);

  @override
  Stream<QueueStats> create(Ref ref) {
    return systemQueueStats(ref);
  }
}

String _$systemQueueStatsHash() => r'146b106e2c3c5fd2d0309485af804fc0e5379851';

/// **User Role Controller**
///
/// Manages the state of role update operations.
/// Handles the `updateUserRole` logic and invalidates the user list on success.

@ProviderFor(UserRoleController)
final userRoleControllerProvider = UserRoleControllerProvider._();

/// **User Role Controller**
///
/// Manages the state of role update operations.
/// Handles the `updateUserRole` logic and invalidates the user list on success.
final class UserRoleControllerProvider
    extends $AsyncNotifierProvider<UserRoleController, void> {
  /// **User Role Controller**
  ///
  /// Manages the state of role update operations.
  /// Handles the `updateUserRole` logic and invalidates the user list on success.
  UserRoleControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'userRoleControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$userRoleControllerHash();

  @$internal
  @override
  UserRoleController create() => UserRoleController();
}

String _$userRoleControllerHash() =>
    r'bce082fc7211de01885c92178f44d540defeba46';

/// **User Role Controller**
///
/// Manages the state of role update operations.
/// Handles the `updateUserRole` logic and invalidates the user list on success.

abstract class _$UserRoleController extends $AsyncNotifier<void> {
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
