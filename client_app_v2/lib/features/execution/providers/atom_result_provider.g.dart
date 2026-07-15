// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'atom_result_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Returns `ReportDataDto.results`.
/// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.

@ProviderFor(atomResults)
final atomResultsProvider = AtomResultsFamily._();

/// Returns `ReportDataDto.results`.
/// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.

final class AtomResultsProvider
    extends
        $FunctionalProvider<
          List<AtomResultDTO>,
          List<AtomResultDTO>,
          List<AtomResultDTO>
        >
    with $Provider<List<AtomResultDTO>> {
  /// Returns `ReportDataDto.results`.
  /// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.
  AtomResultsProvider._({
    required AtomResultsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'atomResultsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$atomResultsHash();

  @override
  String toString() {
    return r'atomResultsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<List<AtomResultDTO>> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  List<AtomResultDTO> create(Ref ref) {
    final argument = this.argument as String;
    return atomResults(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(List<AtomResultDTO> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<List<AtomResultDTO>>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is AtomResultsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$atomResultsHash() => r'73f3d4265bb63578c02af21618ba9c95256eed13';

/// Returns `ReportDataDto.results`.
/// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.

final class AtomResultsFamily extends $Family
    with $FunctionalFamilyOverride<List<AtomResultDTO>, String> {
  AtomResultsFamily._()
    : super(
        retry: null,
        name: r'atomResultsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Returns `ReportDataDto.results`.
  /// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.

  AtomResultsProvider call(String executionId) =>
      AtomResultsProvider._(argument: executionId, from: this);

  @override
  String toString() => r'atomResultsProvider';
}
