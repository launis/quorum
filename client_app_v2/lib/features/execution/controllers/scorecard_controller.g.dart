// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scorecard_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
/// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.

@ProviderFor(ScorecardController)
final scorecardControllerProvider = ScorecardControllerFamily._();

/// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
/// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.
final class ScorecardControllerProvider
    extends $AsyncNotifierProvider<ScorecardController, ScorecardResponseDto> {
  /// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
  /// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.
  ScorecardControllerProvider._({
    required ScorecardControllerFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'scorecardControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$scorecardControllerHash();

  @override
  String toString() {
    return r'scorecardControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  ScorecardController create() => ScorecardController();

  @override
  bool operator ==(Object other) {
    return other is ScorecardControllerProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$scorecardControllerHash() =>
    r'154fae769a22f5fbcf7b64d0a5e52ff7f3a9a3bc';

/// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
/// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.

final class ScorecardControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          ScorecardController,
          AsyncValue<ScorecardResponseDto>,
          ScorecardResponseDto,
          FutureOr<ScorecardResponseDto>,
          String
        > {
  ScorecardControllerFamily._()
    : super(
        retry: null,
        name: r'scorecardControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
  /// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.

  ScorecardControllerProvider call(String executionId) =>
      ScorecardControllerProvider._(argument: executionId, from: this);

  @override
  String toString() => r'scorecardControllerProvider';
}

/// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
/// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.

abstract class _$ScorecardController
    extends $AsyncNotifier<ScorecardResponseDto> {
  late final _$args = ref.$arg as String;
  String get executionId => _$args;

  FutureOr<ScorecardResponseDto> build(String executionId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<ScorecardResponseDto>, ScorecardResponseDto>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<ScorecardResponseDto>,
                ScorecardResponseDto
              >,
              AsyncValue<ScorecardResponseDto>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
