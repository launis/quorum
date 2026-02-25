# backend_api.api.ToolsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**citationLookupToolsCitationLookupPost**](ToolsApi.md#citationlookuptoolscitationlookuppost) | **POST** /tools/citation-lookup | Resolve Citations
[**extractConceptsFromFileOrTextToolsExtractConceptsPost**](ToolsApi.md#extractconceptsfromfileortexttoolsextractconceptspost) | **POST** /tools/extract-concepts | Extract Concepts from Content
[**extractTextToolsExtractTextPost**](ToolsApi.md#extracttexttoolsextracttextpost) | **POST** /tools/extract-text | Extract Text from File
[**webScrapeToolsWebScrapePost**](ToolsApi.md#webscrapetoolswebscrapepost) | **POST** /tools/web-scrape | Scrape Web Page


# **citationLookupToolsCitationLookupPost**
> CitationLookupResponse citationLookupToolsCitationLookupPost(bodyCitationLookupToolsCitationLookupPost)

Resolve Citations

Uses the Knowledge Base Service to find context for citations.  Args:     kb_service (KnowledgeBaseService): Injected KB service.     queries (List[str]): List of citation keys or queries.  Returns:     CitationLookupResponse: Map of query to resolved context.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getToolsApi();
final BodyCitationLookupToolsCitationLookupPost bodyCitationLookupToolsCitationLookupPost = ; // BodyCitationLookupToolsCitationLookupPost | 

try {
    final response = api.citationLookupToolsCitationLookupPost(bodyCitationLookupToolsCitationLookupPost);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ToolsApi->citationLookupToolsCitationLookupPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bodyCitationLookupToolsCitationLookupPost** | [**BodyCitationLookupToolsCitationLookupPost**](BodyCitationLookupToolsCitationLookupPost.md)|  | 

### Return type

[**CitationLookupResponse**](CitationLookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **extractConceptsFromFileOrTextToolsExtractConceptsPost**
> ConceptExtractionResponse extractConceptsFromFileOrTextToolsExtractConceptsPost(text, file)

Extract Concepts from Content

Extracts domain concepts from either raw text or an uploaded file.  Args:     kb_service (KnowledgeBaseService): Injected KB service.     doc_service (DocumentService): Injected document service.     text (str): Raw text input.     file (UploadFile): File input.  Returns:     ConceptExtractionResponse: Extracted concepts.  Raises:     HTTPException: If no input provided (400) or extraction errors (500).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getToolsApi();
final String text = text_example; // String | 
final MultipartFile file = BINARY_DATA_HERE; // MultipartFile | 

try {
    final response = api.extractConceptsFromFileOrTextToolsExtractConceptsPost(text, file);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ToolsApi->extractConceptsFromFileOrTextToolsExtractConceptsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text** | **String**|  | [optional] 
 **file** | **MultipartFile**|  | [optional] 

### Return type

[**ConceptExtractionResponse**](ConceptExtractionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **extractTextToolsExtractTextPost**
> TextExtractionResponse extractTextToolsExtractTextPost(text, file)

Extract Text from File

Deep-parse a PDF/DOCX file and return raw text.  Args:     file (UploadFile): The binary file to process.     doc_service (DocumentService): Injected document service.     text (str | None): Optional text fallback.  Returns:     TextExtractionResponse: Filename and extracted text.  Raises:     HTTPException: If extraction fails (500).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getToolsApi();
final String text = text_example; // String | 
final MultipartFile file = BINARY_DATA_HERE; // MultipartFile | 

try {
    final response = api.extractTextToolsExtractTextPost(text, file);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ToolsApi->extractTextToolsExtractTextPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text** | **String**|  | [optional] 
 **file** | **MultipartFile**|  | [optional] 

### Return type

[**TextExtractionResponse**](TextExtractionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **webScrapeToolsWebScrapePost**
> WebScrapeResponse webScrapeToolsWebScrapePost(bodyWebScrapeToolsWebScrapePost)

Scrape Web Page

Scrapes a public web page.  Protected against SSRF (Server-Side Request Forgery). Blocks requests to localhost and private IP ranges.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getToolsApi();
final BodyWebScrapeToolsWebScrapePost bodyWebScrapeToolsWebScrapePost = ; // BodyWebScrapeToolsWebScrapePost | 

try {
    final response = api.webScrapeToolsWebScrapePost(bodyWebScrapeToolsWebScrapePost);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ToolsApi->webScrapeToolsWebScrapePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bodyWebScrapeToolsWebScrapePost** | [**BodyWebScrapeToolsWebScrapePost**](BodyWebScrapeToolsWebScrapePost.md)|  | 

### Return type

[**WebScrapeResponse**](WebScrapeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

