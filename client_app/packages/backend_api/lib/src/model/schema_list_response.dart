//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/schema_info.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'schema_list_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SchemaListResponse {
  /// Returns a new [SchemaListResponse] instance.
  SchemaListResponse({

    required  this.items,
  });

  @JsonKey(
    
    name: r'items',
    required: true,
    
  )


  final Map<String, SchemaInfo> items;





    @override
    bool operator ==(Object other) => identical(this, other) || other is SchemaListResponse &&
      other.items == items;

    @override
    int get hashCode =>
        items.hashCode;

  factory SchemaListResponse.fromJson(Map<String, dynamic> json) => _$SchemaListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SchemaListResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

