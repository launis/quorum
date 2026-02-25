//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'pdf_cancel_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PDFCancelResponse {
  /// Returns a new [PDFCancelResponse] instance.
  PDFCancelResponse({

    required  this.status,

    required  this.message,
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





    @override
    bool operator ==(Object other) => identical(this, other) || other is PDFCancelResponse &&
      other.status == status &&
      other.message == message;

    @override
    int get hashCode =>
        status.hashCode +
        message.hashCode;

  factory PDFCancelResponse.fromJson(Map<String, dynamic> json) => _$PDFCancelResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PDFCancelResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

