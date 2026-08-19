// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';

part 'blueprint_config.freezed.dart';
part 'blueprint_config.g.dart';

/// Freezed domain model for Blueprint configurations.
/// Enforces Fail-Fast typing and strict UI layout mapping.
@Freezed(equal: false)
abstract class BlueprintConfig with _$BlueprintConfig {
  const BlueprintConfig._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory BlueprintConfig({
    @JsonKey(name: 'preset_view')
    @Default(PresetView.metrics1d)
    PresetView presetView,
  }) = _BlueprintConfig;

  factory BlueprintConfig.fromJson(Map<String, dynamic> json) =>
      _$BlueprintConfigFromJson(json);
}
