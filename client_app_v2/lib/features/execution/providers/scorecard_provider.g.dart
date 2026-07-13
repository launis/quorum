// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scorecard_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(scorecard)
final scorecardProvider = ScorecardFamily._();

final class ScorecardProvider
    extends
        $FunctionalProvider<
          AsyncValue<ScorecardResponseDto>,
          ScorecardResponseDto,
          FutureOr<ScorecardResponseDto>
        >
    with
        $FutureModifier<ScorecardResponseDto>,
        $FutureProvider<ScorecardResponseDto> {
  ScorecardProvider._({
    required ScorecardFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'scorecardProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$scorecardHash();

  @override
  String toString() {
    return r'scorecardProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ScorecardResponseDto> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ScorecardResponseDto> create(Ref ref) {
    final argument = this.argument as String;
    return scorecard(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ScorecardProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$scorecardHash() => r'0affd2311cc3be6cf61afce58a8db89e9b6d9c1b';

final class ScorecardFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ScorecardResponseDto>, String> {
  ScorecardFamily._()
    : super(
        retry: null,
        name: r'scorecardProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ScorecardProvider call(String executionId) =>
      ScorecardProvider._(argument: executionId, from: this);

  @override
  String toString() => r'scorecardProvider';
}
