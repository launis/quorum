// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_artifact_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches the list of all report artifacts for a given execution.

@ProviderFor(executionReports)
final executionReportsProvider = ExecutionReportsFamily._();

/// Fetches the list of all report artifacts for a given execution.

final class ExecutionReportsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ReportArtifactSummary>>,
          List<ReportArtifactSummary>,
          FutureOr<List<ReportArtifactSummary>>
        >
    with
        $FutureModifier<List<ReportArtifactSummary>>,
        $FutureProvider<List<ReportArtifactSummary>> {
  /// Fetches the list of all report artifacts for a given execution.
  ExecutionReportsProvider._({
    required ExecutionReportsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'executionReportsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$executionReportsHash();

  @override
  String toString() {
    return r'executionReportsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<ReportArtifactSummary>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ReportArtifactSummary>> create(Ref ref) {
    final argument = this.argument as String;
    return executionReports(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ExecutionReportsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$executionReportsHash() => r'dee13f8b780819985c3e43042b4afd6d27bc331e';

/// Fetches the list of all report artifacts for a given execution.

final class ExecutionReportsFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<List<ReportArtifactSummary>>,
          String
        > {
  ExecutionReportsFamily._()
    : super(
        retry: null,
        name: r'executionReportsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches the list of all report artifacts for a given execution.

  ExecutionReportsProvider call(String executionId) =>
      ExecutionReportsProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionReportsProvider';
}

/// Fetches the full detailed domain model for a report artifact.

@ProviderFor(reportDetail)
final reportDetailProvider = ReportDetailFamily._();

/// Fetches the full detailed domain model for a report artifact.

final class ReportDetailProvider
    extends
        $FunctionalProvider<
          AsyncValue<ReportArtifact>,
          ReportArtifact,
          FutureOr<ReportArtifact>
        >
    with $FutureModifier<ReportArtifact>, $FutureProvider<ReportArtifact> {
  /// Fetches the full detailed domain model for a report artifact.
  ReportDetailProvider._({
    required ReportDetailFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'reportDetailProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$reportDetailHash();

  @override
  String toString() {
    return r'reportDetailProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ReportArtifact> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ReportArtifact> create(Ref ref) {
    final argument = this.argument as String;
    return reportDetail(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportDetailProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$reportDetailHash() => r'7acb886c2c433f30c3cec3b6b1c95948baeea6d3';

/// Fetches the full detailed domain model for a report artifact.

final class ReportDetailFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ReportArtifact>, String> {
  ReportDetailFamily._()
    : super(
        retry: null,
        name: r'reportDetailProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches the full detailed domain model for a report artifact.

  ReportDetailProvider call(String reportId) =>
      ReportDetailProvider._(argument: reportId, from: this);

  @override
  String toString() => r'reportDetailProvider';
}

/// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.

@ProviderFor(reportSdui)
final reportSduiProvider = ReportSduiFamily._();

/// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.

final class ReportSduiProvider
    extends
        $FunctionalProvider<
          AsyncValue<ReportDataDto>,
          ReportDataDto,
          FutureOr<ReportDataDto>
        >
    with $FutureModifier<ReportDataDto>, $FutureProvider<ReportDataDto> {
  /// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.
  ReportSduiProvider._({
    required ReportSduiFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'reportSduiProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$reportSduiHash();

  @override
  String toString() {
    return r'reportSduiProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ReportDataDto> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ReportDataDto> create(Ref ref) {
    final argument = this.argument as String;
    return reportSdui(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportSduiProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$reportSduiHash() => r'c1c376e01dd1c46232c62ac5bbe6fdb2dc8b5160';

/// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.

final class ReportSduiFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ReportDataDto>, String> {
  ReportSduiFamily._()
    : super(
        retry: null,
        name: r'reportSduiProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.

  ReportSduiProvider call(String reportId) =>
      ReportSduiProvider._(argument: reportId, from: this);

  @override
  String toString() => r'reportSduiProvider';
}

/// Fetches tabular B2B evidence scorecard rows.

@ProviderFor(reportRows)
final reportRowsProvider = ReportRowsFamily._();

/// Fetches tabular B2B evidence scorecard rows.

final class ReportRowsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ReportRowItem>>,
          List<ReportRowItem>,
          FutureOr<List<ReportRowItem>>
        >
    with
        $FutureModifier<List<ReportRowItem>>,
        $FutureProvider<List<ReportRowItem>> {
  /// Fetches tabular B2B evidence scorecard rows.
  ReportRowsProvider._({
    required ReportRowsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'reportRowsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$reportRowsHash();

  @override
  String toString() {
    return r'reportRowsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<ReportRowItem>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ReportRowItem>> create(Ref ref) {
    final argument = this.argument as String;
    return reportRows(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ReportRowsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$reportRowsHash() => r'6486854e4e8cf3aaf56f5ebfbc30c493af9abf2b';

/// Fetches tabular B2B evidence scorecard rows.

final class ReportRowsFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<ReportRowItem>>, String> {
  ReportRowsFamily._()
    : super(
        retry: null,
        name: r'reportRowsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches tabular B2B evidence scorecard rows.

  ReportRowsProvider call(String reportId) =>
      ReportRowsProvider._(argument: reportId, from: this);

  @override
  String toString() => r'reportRowsProvider';
}

/// Controller managing report lifecycle mutations (create, regenerate, delete).

@ProviderFor(ReportArtifactActions)
final reportArtifactActionsProvider = ReportArtifactActionsProvider._();

/// Controller managing report lifecycle mutations (create, regenerate, delete).
final class ReportArtifactActionsProvider
    extends $NotifierProvider<ReportArtifactActions, AsyncValue<void>> {
  /// Controller managing report lifecycle mutations (create, regenerate, delete).
  ReportArtifactActionsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'reportArtifactActionsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$reportArtifactActionsHash();

  @$internal
  @override
  ReportArtifactActions create() => ReportArtifactActions();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AsyncValue<void> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AsyncValue<void>>(value),
    );
  }
}

String _$reportArtifactActionsHash() =>
    r'82aacd1da9fc291df7e595131b0d5139b14cf810';

/// Controller managing report lifecycle mutations (create, regenerate, delete).

abstract class _$ReportArtifactActions extends $Notifier<AsyncValue<void>> {
  AsyncValue<void> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<void>, AsyncValue<void>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<void>, AsyncValue<void>>,
              AsyncValue<void>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
