# backend_api.api.ConfigurationMatricesApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createMatrixV1ConfigMatricesPost**](ConfigurationMatricesApi.md#creatematrixv1configmatricespost) | **POST** /v1/config/matrices | Create Matrix
[**deleteMatrixV1ConfigMatricesMatrixIdDelete**](ConfigurationMatricesApi.md#deletematrixv1configmatricesmatrixiddelete) | **DELETE** /v1/config/matrices/{matrix_id} | Delete Matrix
[**getMatricesV1ConfigMatricesGet**](ConfigurationMatricesApi.md#getmatricesv1configmatricesget) | **GET** /v1/config/matrices | List Matrices
[**getMatrixV1ConfigMatricesMatrixIdGet**](ConfigurationMatricesApi.md#getmatrixv1configmatricesmatrixidget) | **GET** /v1/config/matrices/{matrix_id} | Get Matrix
[**updateMatrixV1ConfigMatricesMatrixIdPut**](ConfigurationMatricesApi.md#updatematrixv1configmatricesmatrixidput) | **PUT** /v1/config/matrices/{matrix_id} | Update Matrix


# **createMatrixV1ConfigMatricesPost**
> String createMatrixV1ConfigMatricesPost(matrixComponentResponse)

Create Matrix

Creates a new evaluation matrix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationMatricesApi();
final MatrixComponentResponse matrixComponentResponse = ; // MatrixComponentResponse | 

try {
    final response = api.createMatrixV1ConfigMatricesPost(matrixComponentResponse);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationMatricesApi->createMatrixV1ConfigMatricesPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **matrixComponentResponse** | [**MatrixComponentResponse**](MatrixComponentResponse.md)|  | 

### Return type

**String**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteMatrixV1ConfigMatricesMatrixIdDelete**
> bool deleteMatrixV1ConfigMatricesMatrixIdDelete(matrixId)

Delete Matrix

Deletes an evaluation matrix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationMatricesApi();
final String matrixId = matrixId_example; // String | 

try {
    final response = api.deleteMatrixV1ConfigMatricesMatrixIdDelete(matrixId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationMatricesApi->deleteMatrixV1ConfigMatricesMatrixIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **matrixId** | **String**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMatricesV1ConfigMatricesGet**
> List<MatrixComponentResponse> getMatricesV1ConfigMatricesGet()

List Matrices

Retrieves all defined evaluation matrices.  Args:     repo: Repository dependency.  Returns:     List of matrix components.  Raises:     AppException: If retrieval fails.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationMatricesApi();

try {
    final response = api.getMatricesV1ConfigMatricesGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationMatricesApi->getMatricesV1ConfigMatricesGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;MatrixComponentResponse&gt;**](MatrixComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMatrixV1ConfigMatricesMatrixIdGet**
> MatrixComponentResponse getMatrixV1ConfigMatricesMatrixIdGet(matrixId)

Get Matrix

Retrieves a single evaluation matrix by ID.  Args:     repo: Repository dependency.     matrix_id: Unique identifier for the matrix.  Returns:     The matched matrix component.  Raises:     ResourceNotFoundError: If the matrix does not exist.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationMatricesApi();
final String matrixId = matrixId_example; // String | Matrix ID

try {
    final response = api.getMatrixV1ConfigMatricesMatrixIdGet(matrixId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationMatricesApi->getMatrixV1ConfigMatricesMatrixIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **matrixId** | **String**| Matrix ID | 

### Return type

[**MatrixComponentResponse**](MatrixComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateMatrixV1ConfigMatricesMatrixIdPut**
> bool updateMatrixV1ConfigMatricesMatrixIdPut(matrixId, componentUpdate)

Update Matrix

Updates an existing evaluation matrix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationMatricesApi();
final String matrixId = matrixId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateMatrixV1ConfigMatricesMatrixIdPut(matrixId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationMatricesApi->updateMatrixV1ConfigMatricesMatrixIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **matrixId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

