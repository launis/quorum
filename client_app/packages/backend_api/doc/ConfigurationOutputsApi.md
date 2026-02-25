# backend_api.api.ConfigurationOutputsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createOutputV1ConfigOutputsPost**](ConfigurationOutputsApi.md#createoutputv1configoutputspost) | **POST** /v1/config/outputs | Create Output Config
[**deleteOutputV1ConfigOutputsOutputIdDelete**](ConfigurationOutputsApi.md#deleteoutputv1configoutputsoutputiddelete) | **DELETE** /v1/config/outputs/{output_id} | Delete Output Config
[**getOutputV1ConfigOutputsOutputIdGet**](ConfigurationOutputsApi.md#getoutputv1configoutputsoutputidget) | **GET** /v1/config/outputs/{output_id} | Get Output Configuration
[**getOutputsV1ConfigOutputsGet**](ConfigurationOutputsApi.md#getoutputsv1configoutputsget) | **GET** /v1/config/outputs | List Output Configurations
[**updateOutputV1ConfigOutputsOutputIdPut**](ConfigurationOutputsApi.md#updateoutputv1configoutputsoutputidput) | **PUT** /v1/config/outputs/{output_id} | Update Output Config


# **createOutputV1ConfigOutputsPost**
> String createOutputV1ConfigOutputsPost(configComponentResponse)

Create Output Config

Creates a new output configuration.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationOutputsApi();
final ConfigComponentResponse configComponentResponse = ; // ConfigComponentResponse | 

try {
    final response = api.createOutputV1ConfigOutputsPost(configComponentResponse);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationOutputsApi->createOutputV1ConfigOutputsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **configComponentResponse** | [**ConfigComponentResponse**](ConfigComponentResponse.md)|  | 

### Return type

**String**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteOutputV1ConfigOutputsOutputIdDelete**
> bool deleteOutputV1ConfigOutputsOutputIdDelete(outputId)

Delete Output Config

Deletes an output configuration.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationOutputsApi();
final String outputId = outputId_example; // String | 

try {
    final response = api.deleteOutputV1ConfigOutputsOutputIdDelete(outputId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationOutputsApi->deleteOutputV1ConfigOutputsOutputIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **outputId** | **String**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOutputV1ConfigOutputsOutputIdGet**
> ConfigComponentResponse getOutputV1ConfigOutputsOutputIdGet(outputId)

Get Output Configuration

Retrieves a single output configuration by ID.  Args:     repo: Repository dependency.     output_id: Unique identifier for the output config.  Returns:     The matched config component.  Raises:     ResourceNotFoundError: If the config does not exist.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationOutputsApi();
final String outputId = outputId_example; // String | Output ID

try {
    final response = api.getOutputV1ConfigOutputsOutputIdGet(outputId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationOutputsApi->getOutputV1ConfigOutputsOutputIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **outputId** | **String**| Output ID | 

### Return type

[**ConfigComponentResponse**](ConfigComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOutputsV1ConfigOutputsGet**
> List<ConfigComponentResponse> getOutputsV1ConfigOutputsGet()

List Output Configurations

Retrieves all defined output configurations.  Args:     repo: Repository dependency.  Returns:     List of output config components.  Raises:     AppException: If retrieval fails.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationOutputsApi();

try {
    final response = api.getOutputsV1ConfigOutputsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationOutputsApi->getOutputsV1ConfigOutputsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;ConfigComponentResponse&gt;**](ConfigComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateOutputV1ConfigOutputsOutputIdPut**
> bool updateOutputV1ConfigOutputsOutputIdPut(outputId, componentUpdate)

Update Output Config

Updates an existing output configuration.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationOutputsApi();
final String outputId = outputId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateOutputV1ConfigOutputsOutputIdPut(outputId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationOutputsApi->updateOutputV1ConfigOutputsOutputIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **outputId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

