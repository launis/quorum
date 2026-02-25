# backend_api.api.LLMApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batchCompletionLlmBatchCompletionPost**](LLMApi.md#batchcompletionllmbatchcompletionpost) | **POST** /llm/batch-completion | Batch Completion
[**generateCompletionLlmCompletionPost**](LLMApi.md#generatecompletionllmcompletionpost) | **POST** /llm/completion | Direct Completion
[**getModelConfigLlmConfigGet**](LLMApi.md#getmodelconfigllmconfigget) | **GET** /llm/config | Get Model Registry
[**listProvidersLlmProvidersGet**](LLMApi.md#listprovidersllmprovidersget) | **GET** /llm/providers | List Providers
[**updateModelConfigLlmConfigPost**](LLMApi.md#updatemodelconfigllmconfigpost) | **POST** /llm/config | Update Model Registry


# **batchCompletionLlmBatchCompletionPost**
> BatchLLMResponse batchCompletionLlmBatchCompletionPost(batchCompletionRequest, authorization)

Batch Completion

Processes multiple completion requests in parallel.  Args:     batch (BatchCompletionRequest): List of requests.     registry (RegistryDep): Registry dependency.     user (CurrentUserDep): Authenticated user.     repo (RepositoryDep): Data repository.  Returns:     BatchLLMResponse: List of results (success or error) for each request.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getLLMApi();
final BatchCompletionRequest batchCompletionRequest = ; // BatchCompletionRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.batchCompletionLlmBatchCompletionPost(batchCompletionRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling LLMApi->batchCompletionLlmBatchCompletionPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batchCompletionRequest** | [**BatchCompletionRequest**](BatchCompletionRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**BatchLLMResponse**](BatchLLMResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateCompletionLlmCompletionPost**
> LLMResponse generateCompletionLlmCompletionPost(completionRequest, authorization)

Direct Completion

Directly invokes the LLM using the specified strategy.  Supports structured output if schema is provided.  Args:     request (CompletionRequest): The prompt and settings.     registry (RegistryDep): Registry dependency to resolve strategies.     user (CurrentUserDep): Authenticated user (required for rate limits).     repo (RepositoryDep): Data repository.  Returns:     LLMResponse: Result object containing the generated content.  Raises:     HTTPException: If strategy is invalid (400) or generation fails (500).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getLLMApi();
final CompletionRequest completionRequest = ; // CompletionRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.generateCompletionLlmCompletionPost(completionRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling LLMApi->generateCompletionLlmCompletionPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **completionRequest** | [**CompletionRequest**](CompletionRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**LLMResponse**](LLMResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getModelConfigLlmConfigGet**
> ModelRegistryResponse getModelConfigLlmConfigGet()

Get Model Registry

Retrieves the active model registry, which maps abstract strategies (e.g., 'fast') to concrete models.  Args:     handler: Dependency.  Returns:     ModelRegistryResponse: The registry configuration object.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getLLMApi();

try {
    final response = api.getModelConfigLlmConfigGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling LLMApi->getModelConfigLlmConfigGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ModelRegistryResponse**](ModelRegistryResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listProvidersLlmProvidersGet**
> ProviderListResponse listProvidersLlmProvidersGet()

List Providers

Returns information about active LLM providers and availability.  Args:     handler (LLMHandlerDep): LLM Handler.  Returns:     ProviderListResponse: Strategies map and API key status.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getLLMApi();

try {
    final response = api.listProvidersLlmProvidersGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling LLMApi->listProvidersLlmProvidersGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ProviderListResponse**](ProviderListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateModelConfigLlmConfigPost**
> ModelRegistryUpdateResponse updateModelConfigLlmConfigPost(modelRegistryUpdate)

Update Model Registry

Updates the system's model registry configuration in the database.  Args:     update (ModelRegistryUpdate): The new configuration.     registry (RegistryDep): Registry dependency.  Returns:     ModelRegistryUpdateResponse: Status and the updated registry.  Raises:     HTTPException: If database update fails (500).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getLLMApi();
final ModelRegistryUpdate modelRegistryUpdate = ; // ModelRegistryUpdate | 

try {
    final response = api.updateModelConfigLlmConfigPost(modelRegistryUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling LLMApi->updateModelConfigLlmConfigPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **modelRegistryUpdate** | [**ModelRegistryUpdate**](ModelRegistryUpdate.md)|  | 

### Return type

[**ModelRegistryUpdateResponse**](ModelRegistryUpdateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

