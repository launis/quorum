# backend_api.api.OntologyApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deleteDimensionV1ConfigOntologyDimensionsDimIdDelete**](OntologyApi.md#deletedimensionv1configontologydimensionsdimiddelete) | **DELETE** /v1/config/ontology/dimensions/{dim_id} | Delete Dimension
[**deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0**](OntologyApi.md#deletedimensionv1configontologydimensionsdimiddelete_0) | **DELETE** /v1/config/ontology/dimensions/{dim_id} | Delete Dimension
[**getKnownDimensionsV1ConfigOntologyDimensionsGet**](OntologyApi.md#getknowndimensionsv1configontologydimensionsget) | **GET** /v1/config/ontology/dimensions | Get Known Dimensions
[**getKnownDimensionsV1ConfigOntologyDimensionsGet_0**](OntologyApi.md#getknowndimensionsv1configontologydimensionsget_0) | **GET** /v1/config/ontology/dimensions | Get Known Dimensions
[**updateDimensionV1ConfigOntologyDimensionsDimIdPut**](OntologyApi.md#updatedimensionv1configontologydimensionsdimidput) | **PUT** /v1/config/ontology/dimensions/{dim_id} | Update Dimension
[**updateDimensionV1ConfigOntologyDimensionsDimIdPut_0**](OntologyApi.md#updatedimensionv1configontologydimensionsdimidput_0) | **PUT** /v1/config/ontology/dimensions/{dim_id} | Update Dimension


# **deleteDimensionV1ConfigOntologyDimensionsDimIdDelete**
> DimensionDeleteResponse deleteDimensionV1ConfigOntologyDimensionsDimIdDelete(dimId)

Delete Dimension

Deletes a dimension if it is not used in any matrix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();
final String dimId = dimId_example; // String | 

try {
    final response = api.deleteDimensionV1ConfigOntologyDimensionsDimIdDelete(dimId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->deleteDimensionV1ConfigOntologyDimensionsDimIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimId** | **String**|  | 

### Return type

[**DimensionDeleteResponse**](DimensionDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0**
> DimensionDeleteResponse deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0(dimId)

Delete Dimension

Deletes a dimension if it is not used in any matrix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();
final String dimId = dimId_example; // String | 

try {
    final response = api.deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0(dimId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimId** | **String**|  | 

### Return type

[**DimensionDeleteResponse**](DimensionDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getKnownDimensionsV1ConfigOntologyDimensionsGet**
> List<DimensionDefinition> getKnownDimensionsV1ConfigOntologyDimensionsGet()

Get Known Dimensions

Returns specific allowed dimension IDs from the ontology table.  Auto-seeds defaults if table is empty.  Args:     repo (RepositoryDep): Repository dependency.  Returns:     list[DimensionDefinition]: Sorted list of dimensions.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();

try {
    final response = api.getKnownDimensionsV1ConfigOntologyDimensionsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->getKnownDimensionsV1ConfigOntologyDimensionsGet: $e\n');
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

# **getKnownDimensionsV1ConfigOntologyDimensionsGet_0**
> List<DimensionDefinition> getKnownDimensionsV1ConfigOntologyDimensionsGet_0()

Get Known Dimensions

Returns specific allowed dimension IDs from the ontology table.  Auto-seeds defaults if table is empty.  Args:     repo (RepositoryDep): Repository dependency.  Returns:     list[DimensionDefinition]: Sorted list of dimensions.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();

try {
    final response = api.getKnownDimensionsV1ConfigOntologyDimensionsGet_0();
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->getKnownDimensionsV1ConfigOntologyDimensionsGet_0: $e\n');
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

# **updateDimensionV1ConfigOntologyDimensionsDimIdPut**
> DimensionDefinition updateDimensionV1ConfigOntologyDimensionsDimIdPut(dimId, dimensionDefinition)

Update Dimension

Updates an existing dimension.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();
final String dimId = dimId_example; // String | 
final DimensionDefinition dimensionDefinition = ; // DimensionDefinition | 

try {
    final response = api.updateDimensionV1ConfigOntologyDimensionsDimIdPut(dimId, dimensionDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->updateDimensionV1ConfigOntologyDimensionsDimIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimId** | **String**|  | 
 **dimensionDefinition** | [**DimensionDefinition**](DimensionDefinition.md)|  | 

### Return type

[**DimensionDefinition**](DimensionDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateDimensionV1ConfigOntologyDimensionsDimIdPut_0**
> DimensionDefinition updateDimensionV1ConfigOntologyDimensionsDimIdPut_0(dimId, dimensionDefinition)

Update Dimension

Updates an existing dimension.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOntologyApi();
final String dimId = dimId_example; // String | 
final DimensionDefinition dimensionDefinition = ; // DimensionDefinition | 

try {
    final response = api.updateDimensionV1ConfigOntologyDimensionsDimIdPut_0(dimId, dimensionDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OntologyApi->updateDimensionV1ConfigOntologyDimensionsDimIdPut_0: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimId** | **String**|  | 
 **dimensionDefinition** | [**DimensionDefinition**](DimensionDefinition.md)|  | 

### Return type

[**DimensionDefinition**](DimensionDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

