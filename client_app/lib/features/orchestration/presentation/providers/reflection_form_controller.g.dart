// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reflection_form_controller.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReflectionFormState _$ReflectionFormStateFromJson(Map<String, dynamic> json) =>
    _ReflectionFormState(
      inputMode:
          $enumDecodeNullable(
            _$ReflectionInputModeEnumMap,
            json['inputMode'],
          ) ??
          ReflectionInputMode.guided,
      q1Goal: json['q1Goal'] as String? ?? '',
      q2Falsification: json['q2Falsification'] as String? ?? '',
      q3Synthesis: json['q3Synthesis'] as String? ?? '',
      q4Argumentation: json['q4Argumentation'] as String? ?? '',
      freeText: json['freeText'] as String? ?? '',
    );

Map<String, dynamic> _$ReflectionFormStateToJson(
  _ReflectionFormState instance,
) => <String, dynamic>{
  'inputMode': _$ReflectionInputModeEnumMap[instance.inputMode]!,
  'q1Goal': instance.q1Goal,
  'q2Falsification': instance.q2Falsification,
  'q3Synthesis': instance.q3Synthesis,
  'q4Argumentation': instance.q4Argumentation,
  'freeText': instance.freeText,
};

const _$ReflectionInputModeEnumMap = {
  ReflectionInputMode.guided: 'guided',
  ReflectionInputMode.text: 'text',
  ReflectionInputMode.file: 'file',
};

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ReflectionFormController)
final reflectionFormControllerProvider = ReflectionFormControllerProvider._();

final class ReflectionFormControllerProvider
    extends
        $AsyncNotifierProvider<ReflectionFormController, ReflectionFormState> {
  ReflectionFormControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'reflectionFormControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$reflectionFormControllerHash();

  @$internal
  @override
  ReflectionFormController create() => ReflectionFormController();
}

String _$reflectionFormControllerHash() =>
    r'930554e9459ae857e0e20fa2bd2352a3be12a34b';

abstract class _$ReflectionFormController
    extends $AsyncNotifier<ReflectionFormState> {
  FutureOr<ReflectionFormState> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<ReflectionFormState>, ReflectionFormState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ReflectionFormState>, ReflectionFormState>,
              AsyncValue<ReflectionFormState>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
