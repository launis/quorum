# backend_api.api.StepsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createStepV1ConfigStepsPost**](StepsApi.md#createstepv1configstepspost) | **POST** /v1/config/steps | Create Step
[**deleteStepV1ConfigStepsStepIdDelete**](StepsApi.md#deletestepv1configstepsstepiddelete) | **DELETE** /v1/config/steps/{step_id} | Delete Step
[**getStepV1ConfigStepsStepIdGet**](StepsApi.md#getstepv1configstepsstepidget) | **GET** /v1/config/steps/{step_id} | Get Step
[**getStepsV1ConfigStepsGet**](StepsApi.md#getstepsv1configstepsget) | **GET** /v1/config/steps | List Steps
[**updateStepV1ConfigStepsStepIdPut**](StepsApi.md#updatestepv1configstepsstepidput) | **PUT** /v1/config/steps/{step_id} | Update Step


# **createStepV1ConfigStepsPost**
> StepDefinition createStepV1ConfigStepsPost(stepDefinition)

Create Step

Creates a new step. Pydantic validator adapts legacy input to DB schema.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getStepsApi();
final StepDefinition stepDefinition = ; // StepDefinition | 

try {
    final response = api.createStepV1ConfigStepsPost(stepDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling StepsApi->createStepV1ConfigStepsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepDefinition** | [**StepDefinition**](StepDefinition.md)|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteStepV1ConfigStepsStepIdDelete**
> StepDeleteResponse deleteStepV1ConfigStepsStepIdDelete(stepId)

Delete Step

Deletes a step.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getStepsApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.deleteStepV1ConfigStepsStepIdDelete(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling StepsApi->deleteStepV1ConfigStepsStepIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepDeleteResponse**](StepDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStepV1ConfigStepsStepIdGet**
> StepDefinition getStepV1ConfigStepsStepIdGet(stepId)

Get Step

Retrieves a single step by ID.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getStepsApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.getStepV1ConfigStepsStepIdGet(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling StepsApi->getStepV1ConfigStepsStepIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStepsV1ConfigStepsGet**
> List<StepDefinition> getStepsV1ConfigStepsGet()

List Steps

Retrieves all defined steps. Pydantic model handles adaptation automatically.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getStepsApi();

try {
    final response = api.getStepsV1ConfigStepsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling StepsApi->getStepsV1ConfigStepsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;StepDefinition&gt;**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateStepV1ConfigStepsStepIdPut**
> StepDefinition updateStepV1ConfigStepsStepIdPut(stepId, stepDefinition)

Update Step

Updates an existing step.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getStepsApi();
final String stepId = stepId_example; // String | 
final StepDefinition stepDefinition = ; // StepDefinition | 

try {
    final response = api.updateStepV1ConfigStepsStepIdPut(stepId, stepDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling StepsApi->updateStepV1ConfigStepsStepIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 
 **stepDefinition** | [**StepDefinition**](StepDefinition.md)|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

