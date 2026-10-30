// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_blocks_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches a single Prompt Block natively by ID.

@ProviderFor(promptBlockById)
final promptBlockByIdProvider = PromptBlockByIdFamily._();

/// Fetches a single Prompt Block natively by ID.

final class PromptBlockByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<PromptBlock>,
          PromptBlock,
          FutureOr<PromptBlock>
        >
    with $FutureModifier<PromptBlock>, $FutureProvider<PromptBlock> {
  /// Fetches a single Prompt Block natively by ID.
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

String _$promptBlockByIdHash() => r'8d0545f8b8db6d846aa942aa5bd7fccec7da93b3';

/// Fetches a single Prompt Block natively by ID.

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

  /// Fetches a single Prompt Block natively by ID.

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

String _$promptBlockFormHash() => r'd54d5541a406ed56eab45d934db08e10b7d523a4';

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

/// Controller managing Prompt Blocks strictly using strongly typed [PromptBlock] models.
/// Implements optimistic UI updates with automatic state rollback on failure.

@ProviderFor(PromptBlocksController)
final promptBlocksControllerProvider = PromptBlocksControllerProvider._();

/// Controller managing Prompt Blocks strictly using strongly typed [PromptBlock] models.
/// Implements optimistic UI updates with automatic state rollback on failure.
final class PromptBlocksControllerProvider
    extends $AsyncNotifierProvider<PromptBlocksController, List<PromptBlock>> {
  /// Controller managing Prompt Blocks strictly using strongly typed [PromptBlock] models.
  /// Implements optimistic UI updates with automatic state rollback on failure.
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
    r'f7f6030775ad77c1ddf6d2c49f939307141cdacb';

/// Controller managing Prompt Blocks strictly using strongly typed [PromptBlock] models.
/// Implements optimistic UI updates with automatic state rollback on failure.

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
