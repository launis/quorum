// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'role_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(assignableRoles)
final assignableRolesProvider = AssignableRolesProvider._();

final class AssignableRolesProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<UserRole>>,
          List<UserRole>,
          FutureOr<List<UserRole>>
        >
    with $FutureModifier<List<UserRole>>, $FutureProvider<List<UserRole>> {
  AssignableRolesProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'assignableRolesProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$assignableRolesHash();

  @$internal
  @override
  $FutureProviderElement<List<UserRole>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<UserRole>> create(Ref ref) {
    return assignableRoles(ref);
  }
}

String _$assignableRolesHash() => r'c371a880ffce642fc3449ed3754fddb891569c3d';
