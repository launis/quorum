// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

import 'matrix_scorecard_dto.dart';
import 'synthesis_config_dto.dart';
import '../../../shared/models/i18n_text.dart';
import '../../../core/models/enums.dart';
import '../../../shared/models/sdui_block_dto.dart';

part 'report_layout_dto.freezed.dart';
part 'report_layout_dto.g.dart';

@Freezed(equal: false)
abstract class ReportLayoutDto with _$ReportLayoutDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportLayoutDto({
    @JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)
    @Default(PresetView.defaultView)
    PresetView presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<MatrixScorecardRowDto> axes,
    @JsonKey(name: 'target_blocks') List<String>? targetBlocks,
    @JsonKey(
      name: 'text_delivery_mode',
      unknownEnumValue: TextDeliveryMode.full,
    )
    @Default(TextDeliveryMode.full)
    TextDeliveryMode textDeliveryMode,
    @JsonKey(name: 'is_synthesis_enabled')
    @Default(true)
    bool isSynthesisEnabled,
    SynthesisConfigDto? synthesis,
    @JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? synthesisBlocks,
    @JsonKey(name: 'matrix_visible_columns')
    @Default([])
    List<String> matrixVisibleColumns,
    @JsonKey(name: 'matrix_column_labels')
    @Default({})
    Map<String, I18nText> matrixColumnLabels,
    @JsonKey(name: 'extension_labels')
    @Default({})
    Map<String, I18nText> extensionLabels,
  }) = _ReportLayoutDto;

  factory ReportLayoutDto.fromJson(Map<String, dynamic> json) =>
      _$ReportLayoutDtoFromJson(json);
}
