//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'schema_info.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SchemaInfo {
  /// Returns a new [SchemaInfo] instance.
  SchemaInfo({

    required  this.schema,

     this.example,
  });

  @JsonKey(
    
    name: r'schema',
    required: true,
    
  )


  final Map<String, Object> schema;



  @JsonKey(
    
    name: r'example',
    required: false,
    
  )


  final dynamic? example;





    @override
    bool operator ==(Object other) => identical(this, other) || other is SchemaInfo &&
      other.schema == schema &&
      other.example == example;

    @override
    int get hashCode =>
        schema.hashCode +
        (example == null ? 0 : example.hashCode);

  factory SchemaInfo.fromJson(Map<String, dynamic> json) => _$SchemaInfoFromJson(json);

  Map<String, dynamic> toJson() => _$SchemaInfoToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

