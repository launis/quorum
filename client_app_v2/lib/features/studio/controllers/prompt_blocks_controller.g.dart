// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_blocks_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches a single Prompt Block natively by ID

@ProviderFor(promptBlockById)
final promptBlockByIdProvider = PromptBlockByIdFamily._();

/// Fetches a single Prompt Block natively by ID

final class PromptBlockByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
  /// Fetches a single Prompt Block natively by ID
  PromptBlockByIdProvider._({
    required PromptBlockByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'promptBlockByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$promptBlockByIdHash();

  @override
  String toString() {
    return r'promptBlockByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
    final argument = this.argument as String;
    return promptBlockById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is PromptBlockByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$promptBlockByIdHash() => r'a25fbc357d3224634be823e8b002db03bc3258a1';

/// Fetches a single Prompt Block natively by ID

final class PromptBlockByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
  PromptBlockByIdFamily._()
    : super(
        retry: null,
        name: r'promptBlockByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single Prompt Block natively by ID

  PromptBlockByIdProvider call(String id) =>
      PromptBlockByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'promptBlockByIdProvider';
}

@ProviderFor(PromptBlockForm)
final promptBlockFormProvider = PromptBlockFormFamily._();

final class PromptBlockFormProvider
    extends $AsyncNotifierProvider<PromptBlockForm, Map<String, dynamic>> {
  PromptBlockFormProvider._({
    required PromptBlockFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'promptBlockFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$promptBlockFormHash();

  @override
  String toString() {
    return r'promptBlockFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  PromptBlockForm create() => PromptBlockForm();

  @override
  bool operator ==(Object other) {
    return other is PromptBlockFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$promptBlockFormHash() => r'7aa4e76ff83c23c35ebbf8a918d081179a6ca2f1';

final class PromptBlockFormFamily extends $Family
    with
        $ClassFamilyOverride<
          PromptBlockForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
          String
        > {
  PromptBlockFormFamily._()
    : super(
        retry: null,
        name: r'promptBlockFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  PromptBlockFormProvider call(String configId) =>
      PromptBlockFormProvider._(argument: configId, from: this);

  @override
  String toString() => r'promptBlockFormProvider';
}

abstract class _$PromptBlockForm extends $AsyncNotifier<Map<String, dynamic>> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<Map<String, dynamic>> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>>,
                Map<String, dynamic>
              >,
              AsyncValue<Map<String, dynamic>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(PromptBlocksController)
final promptBlocksControllerProvider = PromptBlocksControllerProvider._();

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class PromptBlocksControllerProvider
    extends
        $AsyncNotifierProvider<
          PromptBlocksController,
          List<Map<String, dynamic>>
        > {
  /// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
  /// Implements Optimistic UI principles where possible.
  PromptBlocksControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'promptBlocksControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$promptBlocksControllerHash();

  @$internal
  @override
  PromptBlocksController create() => PromptBlocksController();
}

String _$promptBlocksControllerHash() =>
    r'04a6142248993bbeae6659e6e2d7cf3cb0a22528';

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$PromptBlocksController
    extends $AsyncNotifier<List<Map<String, dynamic>>> {
  FutureOr<List<Map<String, dynamic>>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<Map<String, dynamic>>>,
              List<Map<String, dynamic>>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<Map<String, dynamic>>>,
                List<Map<String, dynamic>>
              >,
              AsyncValue<List<Map<String, dynamic>>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
