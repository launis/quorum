// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_data_v2_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.

@ProviderFor(ReportDataV2)
final reportDataV2Provider = ReportDataV2Family._();

/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.
final class ReportDataV2Provider
    extends $NotifierProvider<ReportDataV2, ReportDataDto?> {
  /// Fetches and holds the raw [ReportDataDto] payload for a given execution.
  /// Follows tenant_data_isolation: the state is scoped by executionId.
  ReportDataV2Provider._({
    required ReportDataV2Family super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'reportDataV2Provider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$reportDataV2Hash();

  @override
  String toString() {
    return r'reportDataV2Provider'
        ''
        '($argument)';
  }

  @$internal
  @override
  ReportDataV2 create() => ReportDataV2();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ReportDataDto? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ReportDataDto?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is ReportDataV2Provider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$reportDataV2Hash() => r'9dc1213435d5eb88fc3a5a1c997c33898ef8dc19';

/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.

final class ReportDataV2Family extends $Family
    with
        $ClassFamilyOverride<
          ReportDataV2,
          ReportDataDto?,
          ReportDataDto?,
          ReportDataDto?,
          String
        > {
  ReportDataV2Family._()
    : super(
        retry: null,
        name: r'reportDataV2Provider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches and holds the raw [ReportDataDto] payload for a given execution.
  /// Follows tenant_data_isolation: the state is scoped by executionId.

  ReportDataV2Provider call(String executionId) =>
      ReportDataV2Provider._(argument: executionId, from: this);

  @override
  String toString() => r'reportDataV2Provider';
}

/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.

abstract class _$ReportDataV2 extends $Notifier<ReportDataDto?> {
  late final _$args = ref.$arg as String;
  String get executionId => _$args;

  ReportDataDto? build(String executionId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ReportDataDto?, ReportDataDto?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ReportDataDto?, ReportDataDto?>,
              ReportDataDto?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
