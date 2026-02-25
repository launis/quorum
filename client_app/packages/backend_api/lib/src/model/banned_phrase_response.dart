//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'banned_phrase_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BannedPhraseResponse {
  /// Returns a new [BannedPhraseResponse] instance.
  BannedPhraseResponse({

    required  this.status,

    required  this.phrase,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'phrase',
    required: true,
    
  )


  final String phrase;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BannedPhraseResponse &&
      other.status == status &&
      other.phrase == phrase;

    @override
    int get hashCode =>
        status.hashCode +
        phrase.hashCode;

  factory BannedPhraseResponse.fromJson(Map<String, dynamic> json) => _$BannedPhraseResponseFromJson(json);

  Map<String, dynamic> toJson() => _$BannedPhraseResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

