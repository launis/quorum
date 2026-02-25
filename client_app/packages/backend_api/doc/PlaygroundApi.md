# backend_api.api.PlaygroundApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**runPromptBuilderPlaygroundRunPost**](PlaygroundApi.md#runpromptbuilderplaygroundrunpost) | **POST** /builder/playground/run | Run Prompt


# **runPromptBuilderPlaygroundRunPost**
> PlaygroundResponse runPromptBuilderPlaygroundRunPost(playgroundRequest)

Run Prompt

Executes a prompt template with variables against the LLM.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getPlaygroundApi();
final PlaygroundRequest playgroundRequest = ; // PlaygroundRequest | 

try {
    final response = api.runPromptBuilderPlaygroundRunPost(playgroundRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling PlaygroundApi->runPromptBuilderPlaygroundRunPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **playgroundRequest** | [**PlaygroundRequest**](PlaygroundRequest.md)|  | 

### Return type

[**PlaygroundResponse**](PlaygroundResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

