# backend_api.api.ConfigurationDimensionsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createDimensionV1ConfigDimensionsPost**](ConfigurationDimensionsApi.md#createdimensionv1configdimensionspost) | **POST** /v1/config/dimensions | Create Dimension
[**deleteDimensionV1ConfigDimensionsDimensionIdDelete**](ConfigurationDimensionsApi.md#deletedimensionv1configdimensionsdimensioniddelete) | **DELETE** /v1/config/dimensions/{dimension_id} | Delete Dimension
[**getDimensionV1ConfigDimensionsDimensionIdGet**](ConfigurationDimensionsApi.md#getdimensionv1configdimensionsdimensionidget) | **GET** /v1/config/dimensions/{dimension_id} | Get Dimension
[**getDimensionsV1ConfigDimensionsGet**](ConfigurationDimensionsApi.md#getdimensionsv1configdimensionsget) | **GET** /v1/config/dimensions | List Dimensions
[**updateDimensionV1ConfigDimensionsDimensionIdPut**](ConfigurationDimensionsApi.md#updatedimensionv1configdimensionsdimensionidput) | **PUT** /v1/config/dimensions/{dimension_id} | Update Dimension


# **createDimensionV1ConfigDimensionsPost**
> String createDimensionV1ConfigDimensionsPost(dimensionDefinition)

Create Dimension

Creates a new evaluation dimension.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationDimensionsApi();
final DimensionDefinition dimensionDefinition = ; // DimensionDefinition | 

try {
    final response = api.createDimensionV1ConfigDimensionsPost(dimensionDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationDimensionsApi->createDimensionV1ConfigDimensionsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimensionDefinition** | [**DimensionDefinition**](DimensionDefinition.md)|  | 

### Return type

**String**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteDimensionV1ConfigDimensionsDimensionIdDelete**
> bool deleteDimensionV1ConfigDimensionsDimensionIdDelete(dimensionId)

Delete Dimension

Deletes an evaluation dimension.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationDimensionsApi();
final String dimensionId = dimensionId_example; // String | 

try {
    final response = api.deleteDimensionV1ConfigDimensionsDimensionIdDelete(dimensionId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationDimensionsApi->deleteDimensionV1ConfigDimensionsDimensionIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimensionId** | **String**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDimensionV1ConfigDimensionsDimensionIdGet**
> DimensionDefinition getDimensionV1ConfigDimensionsDimensionIdGet(dimensionId)

Get Dimension

Retrieves a single evaluation dimension by ID.  Args:     repo: Repository dependency.     dimension_id: Unique identifier for the dimension.  Returns:     The matched dimension component.  Raises:     ResourceNotFoundError: If the dimension does not exist.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationDimensionsApi();
final String dimensionId = dimensionId_example; // String | Dimension ID

try {
    final response = api.getDimensionV1ConfigDimensionsDimensionIdGet(dimensionId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationDimensionsApi->getDimensionV1ConfigDimensionsDimensionIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimensionId** | **String**| Dimension ID | 

### Return type

[**DimensionDefinition**](DimensionDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDimensionsV1ConfigDimensionsGet**
> List<DimensionDefinition> getDimensionsV1ConfigDimensionsGet()

List Dimensions

Retrieves all defined evaluation dimensions.  Args:     repo: Repository dependency.  Returns:     List of dimension components.  Raises:     AppException: If retrieval fails.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationDimensionsApi();

try {
    final response = api.getDimensionsV1ConfigDimensionsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationDimensionsApi->getDimensionsV1ConfigDimensionsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;DimensionDefinition&gt;**](DimensionDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateDimensionV1ConfigDimensionsDimensionIdPut**
> bool updateDimensionV1ConfigDimensionsDimensionIdPut(dimensionId, componentUpdate)

Update Dimension

Updates an existing evaluation dimension.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationDimensionsApi();
final String dimensionId = dimensionId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateDimensionV1ConfigDimensionsDimensionIdPut(dimensionId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationDimensionsApi->updateDimensionV1ConfigDimensionsDimensionIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimensionId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

