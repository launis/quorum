//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'web_scrape_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WebScrapeResponse {
  /// Returns a new [WebScrapeResponse] instance.
  WebScrapeResponse({

    required  this.url,

    required  this.content,
  });

      /// The target URL.
  @JsonKey(
    
    name: r'url',
    required: true,
    
  )


  final String url;



      /// Scraped content.
  @JsonKey(
    
    name: r'content',
    required: true,
    
  )


  final String content;





    @override
    bool operator ==(Object other) => identical(this, other) || other is WebScrapeResponse &&
      other.url == url &&
      other.content == content;

    @override
    int get hashCode =>
        url.hashCode +
        content.hashCode;

  factory WebScrapeResponse.fromJson(Map<String, dynamic> json) => _$WebScrapeResponseFromJson(json);

  Map<String, dynamic> toJson() => _$WebScrapeResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

