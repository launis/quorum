import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';

part 'output_profile.freezed.dart';
part 'output_profile.g.dart';

@Freezed(equal: false)
abstract class OutputLayoutBlock with _$OutputLayoutBlock {
  const OutputLayoutBlock._();

  const factory OutputLayoutBlock({
    @Default('default') String presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<String> steps,
    @Default([]) List<String> targetBlocks,
    @Default(true) bool showText,
  }) = _OutputLayoutBlock;

  factory OutputLayoutBlock.fromJson(Map<String, dynamic> json) =>
      _$OutputLayoutBlockFromJson(json);
}

@Freezed(equal: false)
abstract class OutputProfile with _$OutputProfile {
  const OutputProfile._();

  const factory OutputProfile({
    @StrictOpaqueIdConverter() required String id,
    @Default('') String slug,
    @StrictOpaqueIdConverter() required String workflowId,
    required I18nText name,
    required I18nText description,
    @Default('original') String displayScale,
    @Default([]) List<OutputLayoutBlock> layouts,
  }) = _OutputProfile;

  factory OutputProfile.fromJson(Map<String, dynamic> json) =>
      _$OutputProfileFromJson(json);
}

@Freezed(equal: false)
abstract class EmbeddedOutputProfile with _$EmbeddedOutputProfile {
  const EmbeddedOutputProfile._();

  const factory EmbeddedOutputProfile({
    required I18nText name,
    @Default('original') String displayScale,
    @Default([]) List<OutputLayoutBlock> layouts,
  }) = _EmbeddedOutputProfile;

  factory EmbeddedOutputProfile.fromJson(Map<String, dynamic> json) =>
      _$EmbeddedOutputProfileFromJson(json);
}
