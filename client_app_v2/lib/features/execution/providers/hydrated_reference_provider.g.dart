// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'hydrated_reference_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
/// in O(1) time without nested loops, enforcing the Topo-Graph rules.

@ProviderFor(hydratedReference)
final hydratedReferenceProvider = HydratedReferenceFamily._();

/// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
/// in O(1) time without nested loops, enforcing the Topo-Graph rules.

final class HydratedReferenceProvider
    extends
        $FunctionalProvider<
          HydratedAtomDTO?,
          HydratedAtomDTO?,
          HydratedAtomDTO?
        >
    with $Provider<HydratedAtomDTO?> {
  /// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
  /// in O(1) time without nested loops, enforcing the Topo-Graph rules.
  HydratedReferenceProvider._({
    required HydratedReferenceFamily super.from,
    required (String, String) super.argument,
  }) : super(
         retry: null,
         name: r'hydratedReferenceProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$hydratedReferenceHash();

  @override
  String toString() {
    return r'hydratedReferenceProvider'
        ''
        '$argument';
  }

  @$internal
  @override
  $ProviderElement<HydratedAtomDTO?> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  HydratedAtomDTO? create(Ref ref) {
    final argument = this.argument as (String, String);
    return hydratedReference(ref, argument.$1, argument.$2);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(HydratedAtomDTO? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<HydratedAtomDTO?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is HydratedReferenceProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$hydratedReferenceHash() => r'059e277f6add326bc9f4561c8c36d14b80c101f9';

/// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
/// in O(1) time without nested loops, enforcing the Topo-Graph rules.

final class HydratedReferenceFamily extends $Family
    with $FunctionalFamilyOverride<HydratedAtomDTO?, (String, String)> {
  HydratedReferenceFamily._()
    : super(
        retry: null,
        name: r'hydratedReferenceProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
  /// in O(1) time without nested loops, enforcing the Topo-Graph rules.

  HydratedReferenceProvider call(String executionId, String tdaId) =>
      HydratedReferenceProvider._(argument: (executionId, tdaId), from: this);

  @override
  String toString() => r'hydratedReferenceProvider';
}
