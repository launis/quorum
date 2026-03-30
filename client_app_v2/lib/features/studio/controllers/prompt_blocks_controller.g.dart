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
          AsyncValue<PromptBlock>,
          PromptBlock,
          FutureOr<PromptBlock>
        >
    with $FutureModifier<PromptBlock>, $FutureProvider<PromptBlock> {
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
  $FutureProviderElement<PromptBlock> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<PromptBlock> create(Ref ref) {
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

String _$promptBlockByIdHash() => r'e1cb851ed60f34d21f72668ca80a8bf837030812';

/// Fetches a single Prompt Block natively by ID

final class PromptBlockByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<PromptBlock>, String> {
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
    extends $AsyncNotifierProvider<PromptBlockForm, PromptBlock> {
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

String _$promptBlockFormHash() => r'e6709320a2c425bad7fb6950a5f7bc4ec953794e';

final class PromptBlockFormFamily extends $Family
    with
        $ClassFamilyOverride<
          PromptBlockForm,
          AsyncValue<PromptBlock>,
          PromptBlock,
          FutureOr<PromptBlock>,
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

abstract class _$PromptBlockForm extends $AsyncNotifier<PromptBlock> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<PromptBlock> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<PromptBlock>, PromptBlock>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<PromptBlock>, PromptBlock>,
              AsyncValue<PromptBlock>,
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
    extends $AsyncNotifierProvider<PromptBlocksController, List<PromptBlock>> {
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
    r'fc2ca506a7328ee48e427ac4740101657313161b';

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$PromptBlocksController
    extends $AsyncNotifier<List<PromptBlock>> {
  FutureOr<List<PromptBlock>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<PromptBlock>>, List<PromptBlock>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<PromptBlock>>, List<PromptBlock>>,
              AsyncValue<List<PromptBlock>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
