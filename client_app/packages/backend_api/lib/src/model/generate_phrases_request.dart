//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'generate_phrases_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class GeneratePhrasesRequest {
  /// Returns a new [GeneratePhrasesRequest] instance.
  GeneratePhrasesRequest({

     this.language = 'en',
  });

      /// Target language code (e.g., 'en').
  @JsonKey(
    defaultValue: 'en',
    name: r'language',
    required: false,
    
  )


  final String? language;





    @override
    bool operator ==(Object other) => identical(this, other) || other is GeneratePhrasesRequest &&
      other.language == language;

    @override
    int get hashCode =>
        language.hashCode;

  factory GeneratePhrasesRequest.fromJson(Map<String, dynamic> json) => _$GeneratePhrasesRequestFromJson(json);

  Map<String, dynamic> toJson() => _$GeneratePhrasesRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

