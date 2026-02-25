# backend_api.api.ComponentsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createComponentV1ConfigComponentsPost**](ComponentsApi.md#createcomponentv1configcomponentspost) | **POST** /v1/config/components | Create Component
[**deleteComponentV1ConfigComponentsCompIdDelete**](ComponentsApi.md#deletecomponentv1configcomponentscompiddelete) | **DELETE** /v1/config/components/{comp_id} | Delete Component
[**getComponentV1ConfigComponentsCompIdGet**](ComponentsApi.md#getcomponentv1configcomponentscompidget) | **GET** /v1/config/components/{comp_id} | Get Component
[**getComponentsV1ConfigComponentsGet**](ComponentsApi.md#getcomponentsv1configcomponentsget) | **GET** /v1/config/components | List Components
[**listRegistryItemsV1ConfigComponentsRegistryItemsGet**](ComponentsApi.md#listregistryitemsv1configcomponentsregistryitemsget) | **GET** /v1/config/components/registry_items | List Registry Components
[**updateComponentV1ConfigComponentsCompIdPut**](ComponentsApi.md#updatecomponentv1configcomponentscompidput) | **PUT** /v1/config/components/{comp_id} | Update Component


# **createComponentV1ConfigComponentsPost**
> TextComponentResponse createComponentV1ConfigComponentsPost(componentCreate)

Create Component

Creates a new configuration component.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();
final ComponentCreate componentCreate = ; // ComponentCreate | 

try {
    final response = api.createComponentV1ConfigComponentsPost(componentCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->createComponentV1ConfigComponentsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **componentCreate** | [**ComponentCreate**](ComponentCreate.md)|  | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteComponentV1ConfigComponentsCompIdDelete**
> ComponentDeleteResponse deleteComponentV1ConfigComponentsCompIdDelete(compId)

Delete Component

Deletes a component if it is not referenced by any existing steps OR executions.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();
final String compId = compId_example; // String | 

try {
    final response = api.deleteComponentV1ConfigComponentsCompIdDelete(compId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->deleteComponentV1ConfigComponentsCompIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**|  | 

### Return type

[**ComponentDeleteResponse**](ComponentDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getComponentV1ConfigComponentsCompIdGet**
> TextComponentResponse getComponentV1ConfigComponentsCompIdGet(compId)

Get Component

Retrieves a single component by ID or Name.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();
final String compId = compId_example; // String | Component ID or Name

try {
    final response = api.getComponentV1ConfigComponentsCompIdGet(compId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->getComponentV1ConfigComponentsCompIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**| Component ID or Name | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getComponentsV1ConfigComponentsGet**
> List<TextComponentResponse> getComponentsV1ConfigComponentsGet(type, excludeType)

List Components

Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).  Args:     repo (RepositoryDep): Repository dependency.     type (str | None): Optional filter by component type.     exclude_type (list[str] | None): Optional types to exclude (defaults to agents/processors).  Returns:     list[ComponentResponse]: List of configuration components.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();
final String type = type_example; // String | 
final List<String> excludeType = ; // List<String> | 

try {
    final response = api.getComponentsV1ConfigComponentsGet(type, excludeType);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->getComponentsV1ConfigComponentsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | **String**|  | [optional] 
 **excludeType** | [**List&lt;String&gt;**](String.md)|  | [optional] 

### Return type

[**List&lt;TextComponentResponse&gt;**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listRegistryItemsV1ConfigComponentsRegistryItemsGet**
> List<RegistryComponentItem> listRegistryItemsV1ConfigComponentsRegistryItemsGet()

List Registry Components

Retrieves all system components directly from the Repository.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();

try {
    final response = api.listRegistryItemsV1ConfigComponentsRegistryItemsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->listRegistryItemsV1ConfigComponentsRegistryItemsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;RegistryComponentItem&gt;**](RegistryComponentItem.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateComponentV1ConfigComponentsCompIdPut**
> TextComponentResponse updateComponentV1ConfigComponentsCompIdPut(compId, componentUpdate)

Update Component

Updates an existing component's content and metadata.  Args:     comp_id (str): The ID of the component to update.     update (ComponentUpdate): The new data.     repo (RepositoryDep): Repository dependency.  Returns:     ComponentResponse: The updated component.  Raises:     HTTPException: If not found (404).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getComponentsApi();
final String compId = compId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateComponentV1ConfigComponentsCompIdPut(compId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ComponentsApi->updateComponentV1ConfigComponentsCompIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

