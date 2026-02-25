# backend_api.api.OrganizationsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createOrganizationOrganizationsPost**](OrganizationsApi.md#createorganizationorganizationspost) | **POST** /organizations/ | Create Organization
[**createOrganizationUserOrganizationsOrgIdUsersPost**](OrganizationsApi.md#createorganizationuserorganizationsorgiduserspost) | **POST** /organizations/{org_id}/users | Create Organization User
[**deleteOrganizationOrganizationsOrgIdDelete**](OrganizationsApi.md#deleteorganizationorganizationsorgiddelete) | **DELETE** /organizations/{org_id} | Delete Organization
[**deleteOrganizationUserOrganizationsOrgIdUsersTargetIdDelete**](OrganizationsApi.md#deleteorganizationuserorganizationsorgiduserstargetiddelete) | **DELETE** /organizations/{org_id}/users/{target_id} | Delete Organization User
[**getMyOrganizationOrganizationsMeGet**](OrganizationsApi.md#getmyorganizationorganizationsmeget) | **GET** /organizations/me | Get My Organization
[**getOrganizationOrganizationsOrgIdGet**](OrganizationsApi.md#getorganizationorganizationsorgidget) | **GET** /organizations/{org_id} | Get Organization
[**getOrganizationUsageOrganizationsOrgIdUsageGet**](OrganizationsApi.md#getorganizationusageorganizationsorgidusageget) | **GET** /organizations/{org_id}/usage | Get Organization Usage
[**listOrganizationsOrganizationsGet**](OrganizationsApi.md#listorganizationsorganizationsget) | **GET** /organizations/ | List Organizations
[**updateOrganizationOrganizationsOrgIdPut**](OrganizationsApi.md#updateorganizationorganizationsorgidput) | **PUT** /organizations/{org_id} | Update Organization


# **createOrganizationOrganizationsPost**
> OrganizationResponse createOrganizationOrganizationsPost(organizationCreateRequest, authorization)

Create Organization

Create a new Tenant Organization.  Args:     org (OrganizationCreateRequest): Organization details.     user (TokenData): Requesting user (ROOT required).     auth (AuthServiceDep): Authentication service.     repo (RepositoryDep): Repository dependency.     audit_service (AuditServiceDep): Audit logging service.  Returns:     OrganizationResponse: The created organization.  Raises:     HTTPException: If ID conflict (409).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final OrganizationCreateRequest organizationCreateRequest = ; // OrganizationCreateRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createOrganizationOrganizationsPost(organizationCreateRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->createOrganizationOrganizationsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organizationCreateRequest** | [**OrganizationCreateRequest**](OrganizationCreateRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createOrganizationUserOrganizationsOrgIdUsersPost**
> Object createOrganizationUserOrganizationsOrgIdUsersPost(orgId, organizationUserCreate, authorization)

Create Organization User

Create a user within an organization.  Enforces strict typing and no defaults.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final OrganizationUserCreate organizationUserCreate = ; // OrganizationUserCreate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createOrganizationUserOrganizationsOrgIdUsersPost(orgId, organizationUserCreate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->createOrganizationUserOrganizationsOrgIdUsersPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **organizationUserCreate** | [**OrganizationUserCreate**](OrganizationUserCreate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

**Object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteOrganizationOrganizationsOrgIdDelete**
> deleteOrganizationOrganizationsOrgIdDelete(orgId, force, authorization)

Delete Organization

Delete an organization.  Args:     org_id (str): Organization ID.     user (CurrentUserDep): Requesting user.     repo (RepositoryDep): Repository dependency.     audit_service (AuditServiceDep): Audit service.     force (bool): If True, delete even if users exist.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final bool force = true; // bool | 
final String authorization = authorization_example; // String | 

try {
    api.deleteOrganizationOrganizationsOrgIdDelete(orgId, force, authorization);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->deleteOrganizationOrganizationsOrgIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **force** | **bool**|  | [optional] [default to false]
 **authorization** | **String**|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteOrganizationUserOrganizationsOrgIdUsersTargetIdDelete**
> deleteOrganizationUserOrganizationsOrgIdUsersTargetIdDelete(orgId, targetId, authorization)

Delete Organization User

Delete a user from an organization.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final String targetId = targetId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    api.deleteOrganizationUserOrganizationsOrgIdUsersTargetIdDelete(orgId, targetId, authorization);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->deleteOrganizationUserOrganizationsOrgIdUsersTargetIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **targetId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMyOrganizationOrganizationsMeGet**
> OrganizationResponse getMyOrganizationOrganizationsMeGet(authorization)

Get My Organization

Get the organization of the current user.  Args:     user (CurrentUserDep): Requesting user.     repo (RepositoryDep): Repository dependency.  Returns:     OrganizationResponse: organization details.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.getMyOrganizationOrganizationsMeGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->getMyOrganizationOrganizationsMeGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganizationOrganizationsOrgIdGet**
> OrganizationResponse getOrganizationOrganizationsOrgIdGet(orgId, authorization)

Get Organization

Get organization details.  Args:     org_id (str): Organization ID.     user (CurrentUserDep): Requesting user.     repo (RepositoryDep): Repository dependency.  Returns:     OrganizationResponse: organization details.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getOrganizationOrganizationsOrgIdGet(orgId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->getOrganizationOrganizationsOrgIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganizationUsageOrganizationsOrgIdUsageGet**
> OrganizationUsageResponse getOrganizationUsageOrganizationsOrgIdUsageGet(orgId, authorization)

Get Organization Usage

Get current usage statistics and limits for an organization.  Args:     org_id (str): Organization ID.     user (CurrentUserDep): Requesting user.     repo (RepositoryDep): Repository dependency.  Returns:     OrganizationUsageResponse: Usage stats (cost, limits, percentage).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getOrganizationUsageOrganizationsOrgIdUsageGet(orgId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->getOrganizationUsageOrganizationsOrgIdUsageGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**OrganizationUsageResponse**](OrganizationUsageResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listOrganizationsOrganizationsGet**
> List<OrganizationResponse> listOrganizationsOrganizationsGet(authorization)

List Organizations

List all organizations.  Args:     user (TokenData): Requesting user (must be ROOT).     repo (RepositoryDep): Repository dependency.  Returns:     List[OrganizationResponse]: List of all organizations.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.listOrganizationsOrganizationsGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->listOrganizationsOrganizationsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;OrganizationResponse&gt;**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateOrganizationOrganizationsOrgIdPut**
> OrganizationResponse updateOrganizationOrganizationsOrgIdPut(orgId, organizationUpdate, authorization)

Update Organization

Update organization details.  Args:     org_id (str): Organization ID.     organization_update (OrganizationUpdate): Fields to update.     user (CurrentUserDep): Requesting user.     repo (RepositoryDep): Repository dependency.  Returns:     OrganizationResponse: Updated organization.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getOrganizationsApi();
final String orgId = orgId_example; // String | 
final OrganizationUpdate organizationUpdate = ; // OrganizationUpdate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateOrganizationOrganizationsOrgIdPut(orgId, organizationUpdate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling OrganizationsApi->updateOrganizationOrganizationsOrgIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **organizationUpdate** | [**OrganizationUpdate**](OrganizationUpdate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**OrganizationResponse**](OrganizationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

