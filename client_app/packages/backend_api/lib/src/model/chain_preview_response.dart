//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'chain_preview_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ChainPreviewResponse {
  /// Returns a new [ChainPreviewResponse] instance.
  ChainPreviewResponse({

    required  this.markdownContent,
  });

      /// The full Markdown concatenation of all step prompts.
  @JsonKey(
    
    name: r'markdown_content',
    required: true,
    
  )


  final String markdownContent;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ChainPreviewResponse &&
      other.markdownContent == markdownContent;

    @override
    int get hashCode =>
        markdownContent.hashCode;

  factory ChainPreviewResponse.fromJson(Map<String, dynamic> json) => _$ChainPreviewResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ChainPreviewResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

