// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(RenderStatus)
final renderStatusProvider = RenderStatusProvider._();

final class RenderStatusProvider
    extends $NotifierProvider<RenderStatus, String?> {
  RenderStatusProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'renderStatusProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$renderStatusHash();

  @$internal
  @override
  RenderStatus create() => RenderStatus();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(String? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<String?>(value),
    );
  }
}

String _$renderStatusHash() => r'ad04910789136df8464db506fd5eb1c4f7c6da7f';

abstract class _$RenderStatus extends $Notifier<String?> {
  String? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<String?, String?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<String?, String?>,
              String?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.

@ProviderFor(ReportController)
final reportControllerProvider = ReportControllerFamily._();

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
final class ReportControllerProvider
    extends $AsyncNotifierProvider<ReportController, ReportDataDto> {
  /// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
  ReportControllerProvider._({
    required ReportControllerFamily super.from,
    required (String, {String lang, String variant}) super.argument,
  }) : super(
         retry: null,
         name: r'reportControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$reportControllerHash();

  @override
  String toString() {
    return r'reportControllerProvider'
        ''
        '$argument';
  }

  @$internal
  @override
  ReportController create() => ReportController();

  @override
  bool operator ==(Object other) {
    return other is ReportControllerProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$reportControllerHash() => r'132e2972a7a9f438b356d1c53dce53a5ea94accf';

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.

final class ReportControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          ReportController,
          AsyncValue<ReportDataDto>,
          ReportDataDto,
          FutureOr<ReportDataDto>,
          (String, {String lang, String variant})
        > {
  ReportControllerFamily._()
    : super(
        retry: null,
        name: r'reportControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.

  ReportControllerProvider call(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) => ReportControllerProvider._(
    argument: (executionId, lang: lang, variant: variant),
    from: this,
  );

  @override
  String toString() => r'reportControllerProvider';
}

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.

abstract class _$ReportController extends $AsyncNotifier<ReportDataDto> {
  late final _$args = ref.$arg as (String, {String lang, String variant});
  String get executionId => _$args.$1;
  String get lang => _$args.lang;
  String get variant => _$args.variant;

  FutureOr<ReportDataDto> build(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  });
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<ReportDataDto>, ReportDataDto>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ReportDataDto>, ReportDataDto>,
              AsyncValue<ReportDataDto>,
              Object?,
              Object?
            >;
    element.handleCreate(
      ref,
      () => build(_$args.$1, lang: _$args.lang, variant: _$args.variant),
    );
  }
}
