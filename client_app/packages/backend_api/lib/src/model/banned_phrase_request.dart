//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'banned_phrase_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BannedPhraseRequest {
  /// Returns a new [BannedPhraseRequest] instance.
  BannedPhraseRequest({

    required  this.phrase,
  });

      /// The phrase to ban.
  @JsonKey(
    
    name: r'phrase',
    required: true,
    
  )


  final String phrase;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BannedPhraseRequest &&
      other.phrase == phrase;

    @override
    int get hashCode =>
        phrase.hashCode;

  factory BannedPhraseRequest.fromJson(Map<String, dynamic> json) => _$BannedPhraseRequestFromJson(json);

  Map<String, dynamic> toJson() => _$BannedPhraseRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

