// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'output_profile_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing Studio Output Profiles using Strict Freezed models.
/// Implements Optimistic UI principles where possible.

@ProviderFor(OutputProfilesController)
final outputProfilesControllerProvider = OutputProfilesControllerProvider._();

/// Controller managing Studio Output Profiles using Strict Freezed models.
/// Implements Optimistic UI principles where possible.
final class OutputProfilesControllerProvider
    extends
        $AsyncNotifierProvider<OutputProfilesController, List<OutputProfile>> {
  /// Controller managing Studio Output Profiles using Strict Freezed models.
  /// Implements Optimistic UI principles where possible.
  OutputProfilesControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'outputProfilesControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$outputProfilesControllerHash();

  @$internal
  @override
  OutputProfilesController create() => OutputProfilesController();
}

String _$outputProfilesControllerHash() =>
    r'c83718e5d0dfaad86315bc2c8ef86822e9ad08ee';

/// Controller managing Studio Output Profiles using Strict Freezed models.
/// Implements Optimistic UI principles where possible.

abstract class _$OutputProfilesController
    extends $AsyncNotifier<List<OutputProfile>> {
  FutureOr<List<OutputProfile>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<OutputProfile>>, List<OutputProfile>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<OutputProfile>>, List<OutputProfile>>,
              AsyncValue<List<OutputProfile>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Fetches a single Output Profile natively by ID

@ProviderFor(outputProfileById)
final outputProfileByIdProvider = OutputProfileByIdFamily._();

/// Fetches a single Output Profile natively by ID

final class OutputProfileByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<OutputProfile>,
          OutputProfile,
          FutureOr<OutputProfile>
        >
    with $FutureModifier<OutputProfile>, $FutureProvider<OutputProfile> {
  /// Fetches a single Output Profile natively by ID
  OutputProfileByIdProvider._({
    required OutputProfileByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'outputProfileByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$outputProfileByIdHash();

  @override
  String toString() {
    return r'outputProfileByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<OutputProfile> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<OutputProfile> create(Ref ref) {
    final argument = this.argument as String;
    return outputProfileById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is OutputProfileByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$outputProfileByIdHash() => r'e63a5f666c1fab9916b391b15a7f97898763d97e';

/// Fetches a single Output Profile natively by ID

final class OutputProfileByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<OutputProfile>, String> {
  OutputProfileByIdFamily._()
    : super(
        retry: null,
        name: r'outputProfileByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single Output Profile natively by ID

  OutputProfileByIdProvider call(String id) =>
      OutputProfileByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'outputProfileByIdProvider';
}

@ProviderFor(OutputProfileForm)
final outputProfileFormProvider = OutputProfileFormFamily._();

final class OutputProfileFormProvider
    extends $AsyncNotifierProvider<OutputProfileForm, OutputProfile> {
  OutputProfileFormProvider._({
    required OutputProfileFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'outputProfileFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$outputProfileFormHash();

  @override
  String toString() {
    return r'outputProfileFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  OutputProfileForm create() => OutputProfileForm();

  @override
  bool operator ==(Object other) {
    return other is OutputProfileFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$outputProfileFormHash() => r'c51e36f4ebc94c29df302147926d4b0ad68ac972';

final class OutputProfileFormFamily extends $Family
    with
        $ClassFamilyOverride<
          OutputProfileForm,
          AsyncValue<OutputProfile>,
          OutputProfile,
          FutureOr<OutputProfile>,
          String
        > {
  OutputProfileFormFamily._()
    : super(
        retry: null,
        name: r'outputProfileFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  OutputProfileFormProvider call(String configId) =>
      OutputProfileFormProvider._(argument: configId, from: this);

  @override
  String toString() => r'outputProfileFormProvider';
}

abstract class _$OutputProfileForm extends $AsyncNotifier<OutputProfile> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<OutputProfile> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<OutputProfile>, OutputProfile>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<OutputProfile>, OutputProfile>,
              AsyncValue<OutputProfile>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
