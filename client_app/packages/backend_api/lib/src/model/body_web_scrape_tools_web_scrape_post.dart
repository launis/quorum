//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'body_web_scrape_tools_web_scrape_post.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BodyWebScrapeToolsWebScrapePost {
  /// Returns a new [BodyWebScrapeToolsWebScrapePost] instance.
  BodyWebScrapeToolsWebScrapePost({

    required  this.url,
  });

  @JsonKey(
    
    name: r'url',
    required: true,
    
  )


  final String url;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BodyWebScrapeToolsWebScrapePost &&
      other.url == url;

    @override
    int get hashCode =>
        url.hashCode;

  factory BodyWebScrapeToolsWebScrapePost.fromJson(Map<String, dynamic> json) => _$BodyWebScrapeToolsWebScrapePostFromJson(json);

  Map<String, dynamic> toJson() => _$BodyWebScrapeToolsWebScrapePostToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

