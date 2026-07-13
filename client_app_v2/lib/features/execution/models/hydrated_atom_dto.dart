// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../../core/models/enums.dart';

part 'hydrated_atom_dto.freezed.dart';
part 'hydrated_atom_dto.g.dart';

@freezed
abstract class HydratedAtomDTO with _$HydratedAtomDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory HydratedAtomDTO({
    @JsonKey(name: 'sdui_component') required SDUIComponentType sduiComponent,
    @JsonKey(name: 'resolved_claim') required String resolvedClaim,
    @JsonKey(name: 'source_quote') String? sourceQuote,
  }) = _HydratedAtomDTO;

  factory HydratedAtomDTO.fromJson(Map<String, dynamic> json) =>
      _$HydratedAtomDTOFromJson(json);
}
