// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'sdui_block_dto.freezed.dart';
part 'sdui_block_dto.g.dart';

@Freezed(unionKey: 'block_type')
sealed class SduiBlockDTO with _$SduiBlockDTO {
  const SduiBlockDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('paragraph')
  const factory SduiBlockDTO.paragraph({
    required String text,
    @Default([]) List<int> citations,
    @JsonKey(name: 'exact_quotes') @Default([]) List<String> exactQuotes,
  }) = SduiParagraphBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('bullet_list')
  const factory SduiBlockDTO.bulletList({
    required List<SduiBulletListItemDTO> items,
  }) = SduiBulletListBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('alert_box')
  const factory SduiBlockDTO.alertBox({
    required String text,
    required String severity,
    @Default([]) List<int> citations,
    @JsonKey(name: 'exact_quotes') @Default([]) List<String> exactQuotes,
  }) = SduiAlertBoxBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('hero_insight')
  const factory SduiBlockDTO.heroInsight({
    required String text,
    @Default([]) List<int> citations,
    @JsonKey(name: 'exact_quotes') @Default([]) List<String> exactQuotes,
  }) = SduiHeroInsightBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('markdown')
  const factory SduiBlockDTO.markdown({required String text}) =
      SduiMarkdownBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('quote_card')
  const factory SduiBlockDTO.quoteCard({
    required String quote,
    @JsonKey(name: 'source_aliases') required List<String> sourceAliases,
    required List<dynamic> citations,
  }) = SduiQuoteCardBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('warning_card')
  const factory SduiBlockDTO.warningCard({
    required String message,
    @JsonKey(name: 'quote_text') String? quoteText,
  }) = SduiWarningCardBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('n_a_card')
  const factory SduiBlockDTO.nACard({
    @JsonKey(name: 'short_circuit_reason_tda_ids')
    required List<String> shortCircuitReasonTdaIds,
    required String message,
  }) = SduiNACardBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('grid')
  const factory SduiBlockDTO.grid({required List<dynamic> items}) =
      SduiGridBlock;

  factory SduiBlockDTO.fromJson(Map<String, dynamic> json) =>
      _$SduiBlockDTOFromJson(json);
}

@Freezed(equal: false)
abstract class SduiBulletListItemDTO with _$SduiBulletListItemDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory SduiBulletListItemDTO({
    required String text,
    @Default([]) List<int> citations,
    @JsonKey(name: 'exact_quotes') @Default([]) List<String> exactQuotes,
  }) = _SduiBulletListItemDTO;

  factory SduiBulletListItemDTO.fromJson(Map<String, dynamic> json) =>
      _$SduiBulletListItemDTOFromJson(json);
}
