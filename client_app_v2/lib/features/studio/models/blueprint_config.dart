// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'blueprint_config.freezed.dart';
part 'blueprint_config.g.dart';

/// Freezed domain model for Blueprint configurations.
/// Enforces Fail-Fast typing and strict UI layout mapping.
@freezed
abstract class BlueprintConfig with _$BlueprintConfig {
  const factory BlueprintConfig({
    @JsonKey(name: 'preset_view') @Default('1d_metrics') String presetView,
  }) = _BlueprintConfig;

  factory BlueprintConfig.fromJson(Map<String, dynamic> json) =>
      _$BlueprintConfigFromJson(json);
}
