//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'generated_phrases_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class GeneratedPhrasesResponse {
  /// Returns a new [GeneratedPhrasesResponse] instance.
  GeneratedPhrasesResponse({

    required  this.status,

    required  this.message,

    required  this.addedPhrases,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'message',
    required: true,
    
  )


  final String message;



  @JsonKey(
    
    name: r'added_phrases',
    required: true,
    
  )


  final List<String> addedPhrases;





    @override
    bool operator ==(Object other) => identical(this, other) || other is GeneratedPhrasesResponse &&
      other.status == status &&
      other.message == message &&
      other.addedPhrases == addedPhrases;

    @override
    int get hashCode =>
        status.hashCode +
        message.hashCode +
        addedPhrases.hashCode;

  factory GeneratedPhrasesResponse.fromJson(Map<String, dynamic> json) => _$GeneratedPhrasesResponseFromJson(json);

  Map<String, dynamic> toJson() => _$GeneratedPhrasesResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

