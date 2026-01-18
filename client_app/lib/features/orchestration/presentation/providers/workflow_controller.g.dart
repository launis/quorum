// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches workflows for the current user.
///
/// **IMPORTANT**: This provider depends on [authStateProvider] to ensure
/// auth token is available before making API calls. This prevents the
/// race condition where workflows load before authentication is ready.

@ProviderFor(workflowList)
final workflowListProvider = WorkflowListProvider._();

/// Fetches workflows for the current user.
///
/// **IMPORTANT**: This provider depends on [authStateProvider] to ensure
/// auth token is available before making API calls. This prevents the
/// race condition where workflows load before authentication is ready.

final class WorkflowListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Workflow>>,
          List<Workflow>,
          FutureOr<List<Workflow>>
        >
    with $FutureModifier<List<Workflow>>, $FutureProvider<List<Workflow>> {
  /// Fetches workflows for the current user.
  ///
  /// **IMPORTANT**: This provider depends on [authStateProvider] to ensure
  /// auth token is available before making API calls. This prevents the
  /// race condition where workflows load before authentication is ready.
  WorkflowListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowListHash();

  @$internal
  @override
  $FutureProviderElement<List<Workflow>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Workflow>> create(Ref ref) {
    return workflowList(ref);
  }
}

String _$workflowListHash() => r'f713b4d237414bdc5bb7619b26574569700d61e2';
