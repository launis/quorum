//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'pdf_queued_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PDFQueuedResponse {
  /// Returns a new [PDFQueuedResponse] instance.
  PDFQueuedResponse({

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
    bool operator ==(Object other) => identical(this, other) || other is PDFQueuedResponse &&
      other.status == status &&
      other.message == message;

    @override
    int get hashCode =>
        status.hashCode +
        message.hashCode;

  factory PDFQueuedResponse.fromJson(Map<String, dynamic> json) => _$PDFQueuedResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PDFQueuedResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

