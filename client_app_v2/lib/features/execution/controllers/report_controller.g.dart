// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

@ProviderFor(ReportController)
final reportControllerProvider = ReportControllerFamily._();

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.
final class ReportControllerProvider
    extends $AsyncNotifierProvider<ReportController, ReportDataDTO> {
  /// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
  ///
  /// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
  /// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.
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

String _$reportControllerHash() => r'01bc925b8931d283010ea37dfa26fe2c93796625';

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

final class ReportControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          ReportController,
          AsyncValue<ReportDataDTO>,
          ReportDataDTO,
          FutureOr<ReportDataDTO>,
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
  ///
  /// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
  /// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

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
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

abstract class _$ReportController extends $AsyncNotifier<ReportDataDTO> {
  late final _$args = ref.$arg as (String, {String lang, String variant});
  String get executionId => _$args.$1;
  String get lang => _$args.lang;
  String get variant => _$args.variant;

  FutureOr<ReportDataDTO> build(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  });
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<ReportDataDTO>, ReportDataDTO>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ReportDataDTO>, ReportDataDTO>,
              AsyncValue<ReportDataDTO>,
              Object?,
              Object?
            >;
    element.handleCreate(
      ref,
      () => build(_$args.$1, lang: _$args.lang, variant: _$args.variant),
    );
  }
}
