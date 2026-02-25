# backend_api.api.ConfigModelsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deleteModelConfigV1ConfigModelsProviderIdDelete**](ConfigModelsApi.md#deletemodelconfigv1configmodelsprovideriddelete) | **DELETE** /v1/config/models/{provider_id} | Delete Model Config
[**getAgentMappingsV1ConfigModelsMappingsGet**](ConfigModelsApi.md#getagentmappingsv1configmodelsmappingsget) | **GET** /v1/config/models/mappings | Get Agent Mappings
[**listModelOptionsV1ConfigModelsOptionsGet**](ConfigModelsApi.md#listmodeloptionsv1configmodelsoptionsget) | **GET** /v1/config/models/options | List Model Options
[**listModelsV1ConfigModelsGet**](ConfigModelsApi.md#listmodelsv1configmodelsget) | **GET** /v1/config/models | List Models
[**testModelConnectionV1ConfigModelsTestPost**](ConfigModelsApi.md#testmodelconnectionv1configmodelstestpost) | **POST** /v1/config/models/test | Test Model Connection
[**updateAgentMappingsV1ConfigModelsMappingsPut**](ConfigModelsApi.md#updateagentmappingsv1configmodelsmappingsput) | **PUT** /v1/config/models/mappings | Update Agent Mappings
[**updateModelConfigV1ConfigModelsProviderIdPut**](ConfigModelsApi.md#updatemodelconfigv1configmodelsprovideridput) | **PUT** /v1/config/models/{provider_id} | Update Model Config


# **deleteModelConfigV1ConfigModelsProviderIdDelete**
> deleteModelConfigV1ConfigModelsProviderIdDelete(providerId)

Delete Model Config

Delete a specific provider strategy configuration.  Enforces Reference Integrity (Workflow Usage) and System Integrity (Default Strategy). Strictly requires 'provider/strategy' format.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();
final String providerId = providerId_example; // String | 

try {
    api.deleteModelConfigV1ConfigModelsProviderIdDelete(providerId);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->deleteModelConfigV1ConfigModelsProviderIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **providerId** | **String**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentMappingsV1ConfigModelsMappingsGet**
> Map<String, String> getAgentMappingsV1ConfigModelsMappingsGet()

Get Agent Mappings

Get the current Agent to Model Strategy mappings. Returns: dict[str, str] mapping Agent IDs to \"provider/strategy\" strings.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();

try {
    final response = api.getAgentMappingsV1ConfigModelsMappingsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->getAgentMappingsV1ConfigModelsMappingsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**Map&lt;String, String&gt;**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listModelOptionsV1ConfigModelsOptionsGet**
> ModelOptionsResponse listModelOptionsV1ConfigModelsOptionsGet()

List Model Options

Fetch available model options from external providers (Google, OpenAI).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();

try {
    final response = api.listModelOptionsV1ConfigModelsOptionsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->listModelOptionsV1ConfigModelsOptionsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ModelOptionsResponse**](ModelOptionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listModelsV1ConfigModelsGet**
> List<LLMProviderConfig> listModelsV1ConfigModelsGet()

List Models

List all available LLM providers and their current configuration.  Supports nested structure: models[provider][strategy]. Returns flattened list with id=\"{provider}/{strategy}\".

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();

try {
    final response = api.listModelsV1ConfigModelsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->listModelsV1ConfigModelsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;LLMProviderConfig&gt;**](LLMProviderConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **testModelConnectionV1ConfigModelsTestPost**
> AdHocTestResponse testModelConnectionV1ConfigModelsTestPost(adHocTestRequest)

Test Model Connection

Execute an ephemeral LLM request to test credentials/latency.  Does NOT use the database configuration unless strategy_id is specifically requested. Returns status=\"error\" instead of 500 for expected connection failures (User Feedback).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();
final AdHocTestRequest adHocTestRequest = ; // AdHocTestRequest | 

try {
    final response = api.testModelConnectionV1ConfigModelsTestPost(adHocTestRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->testModelConnectionV1ConfigModelsTestPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **adHocTestRequest** | [**AdHocTestRequest**](AdHocTestRequest.md)|  | 

### Return type

[**AdHocTestResponse**](AdHocTestResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAgentMappingsV1ConfigModelsMappingsPut**
> Map<String, String> updateAgentMappingsV1ConfigModelsMappingsPut(requestBody)

Update Agent Mappings

Update Agent to Model Strategy mappings.  Expects dict mapping Agent IDs to \"provider/strategy\" strings.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();
final Map<String, String> requestBody = Object; // Map<String, String> | 

try {
    final response = api.updateAgentMappingsV1ConfigModelsMappingsPut(requestBody);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->updateAgentMappingsV1ConfigModelsMappingsPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **requestBody** | [**Map&lt;String, String&gt;**](String.md)|  | 

### Return type

**Map&lt;String, String&gt;**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateModelConfigV1ConfigModelsProviderIdPut**
> LLMProviderConfig updateModelConfigV1ConfigModelsProviderIdPut(providerId, lLMProviderConfig)

Update Model Config

Update configuration for a specific provider strategy.  'provider_id' MUST be complex path 'provider/strategy'. Legacy flat IDs are strictly rejected.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigModelsApi();
final String providerId = providerId_example; // String | 
final LLMProviderConfig lLMProviderConfig = ; // LLMProviderConfig | 

try {
    final response = api.updateModelConfigV1ConfigModelsProviderIdPut(providerId, lLMProviderConfig);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigModelsApi->updateModelConfigV1ConfigModelsProviderIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **providerId** | **String**|  | 
 **lLMProviderConfig** | [**LLMProviderConfig**](LLMProviderConfig.md)|  | 

### Return type

[**LLMProviderConfig**](LLMProviderConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

