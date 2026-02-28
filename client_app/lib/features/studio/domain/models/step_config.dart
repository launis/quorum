import 'package:freezed_annotation/freezed_annotation.dart';

part 'step_config.freezed.dart';
part 'step_config.g.dart';

@freezed
sealed class StepConfig with _$StepConfig {
  const factory StepConfig({
    required String id,
    required String name,
    String? description,
    @JsonKey(name: 'task_key') @Default('analyst') String taskKey,
    @JsonKey(name: 'config') @Default({}) Map<String, dynamic> config,

    // Legacy support (optional, if API sends it, we can ignore or store it)
    // We stick to RAW access for Flutter as requested ("Simple")
  }) = _StepConfig;

  factory StepConfig.fromJson(Map<String, dynamic> json) =>
      _$StepConfigFromJson(json);
}
