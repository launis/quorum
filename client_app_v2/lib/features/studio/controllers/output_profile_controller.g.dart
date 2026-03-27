// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'output_profile_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(OutputProfilesController)
final outputProfilesControllerProvider = OutputProfilesControllerProvider._();

/// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class OutputProfilesControllerProvider
    extends
        $AsyncNotifierProvider<
          OutputProfilesController,
          List<Map<String, dynamic>>
        > {
  /// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
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
    r'6c456ffc4e204f6f947a86902c1ec996cd71a228';

/// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$OutputProfilesController
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

/// Fetches a single Output Profile natively by ID

@ProviderFor(outputProfileById)
final outputProfileByIdProvider = OutputProfileByIdFamily._();

/// Fetches a single Output Profile natively by ID

final class OutputProfileByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
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
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
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

String _$outputProfileByIdHash() => r'7bdc2c14f9d0631fc83959621253eef5d201ad27';

/// Fetches a single Output Profile natively by ID

final class OutputProfileByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
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
    extends $AsyncNotifierProvider<OutputProfileForm, Map<String, dynamic>> {
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

String _$outputProfileFormHash() => r'4d6c0dfff081030f360f936f507a556ee9371676';

final class OutputProfileFormFamily extends $Family
    with
        $ClassFamilyOverride<
          OutputProfileForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
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

abstract class _$OutputProfileForm
    extends $AsyncNotifier<Map<String, dynamic>> {
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
