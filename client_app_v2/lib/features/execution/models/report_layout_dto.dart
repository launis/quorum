// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

import 'matrix_scorecard_dto.dart';
import 'synthesis_config_dto.dart';
import '../../../shared/models/i18n_text.dart';

part 'report_layout_dto.freezed.dart';
part 'report_layout_dto.g.dart';

@Freezed(equal: false)
abstract class ReportLayoutDto with _$ReportLayoutDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportLayoutDto({
    @JsonKey(name: 'preset_view') required String presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<MatrixScorecardRowDto> axes,
    @JsonKey(name: 'text_delivery_mode')
    @Default('full')
    String textDeliveryMode,
    @JsonKey(name: 'is_synthesis_enabled')
    @Default(true)
    bool isSynthesisEnabled,
    SynthesisConfigDto? synthesis,
    @JsonKey(name: 'synthesis_blocks')
    List<Map<String, dynamic>>? synthesisBlocks,
  }) = _ReportLayoutDto;

  factory ReportLayoutDto.fromJson(Map<String, dynamic> json) =>
      _$ReportLayoutDtoFromJson(json);
}
