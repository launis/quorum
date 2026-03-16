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
    extends $AsyncNotifierProvider<ReportController, SduiRenderPayload> {
  /// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
  ///
  /// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
  /// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.
  ReportControllerProvider._({
    required ReportControllerFamily super.from,
    required (String, {String lang}) super.argument,
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

String _$reportControllerHash() => r'8fcd29796d381c15177c8f6d2fc9871f5549b5ae';

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

final class ReportControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          ReportController,
          AsyncValue<SduiRenderPayload>,
          SduiRenderPayload,
          FutureOr<SduiRenderPayload>,
          (String, {String lang})
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

  ReportControllerProvider call(String executionId, {String lang = 'fi'}) =>
      ReportControllerProvider._(
        argument: (executionId, lang: lang),
        from: this,
      );

  @override
  String toString() => r'reportControllerProvider';
}

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.

abstract class _$ReportController extends $AsyncNotifier<SduiRenderPayload> {
  late final _$args = ref.$arg as (String, {String lang});
  String get executionId => _$args.$1;
  String get lang => _$args.lang;

  FutureOr<SduiRenderPayload> build(String executionId, {String lang = 'fi'});
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<SduiRenderPayload>, SduiRenderPayload>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<SduiRenderPayload>, SduiRenderPayload>,
              AsyncValue<SduiRenderPayload>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args.$1, lang: _$args.lang));
  }
}
