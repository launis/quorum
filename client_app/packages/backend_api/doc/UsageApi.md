# backend_api.api.UsageApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getOrganizationUsageV1UsageOrganizationOrgIdGet**](UsageApi.md#getorganizationusagev1usageorganizationorgidget) | **GET** /v1/usage/organization/{org_id} | Get Organization Usage
[**getSystemUsageV1UsageSystemGet**](UsageApi.md#getsystemusagev1usagesystemget) | **GET** /v1/usage/system | Get System Usage
[**getUserUsageV1UsageUserUserIdGet**](UsageApi.md#getuserusagev1usageuseruseridget) | **GET** /v1/usage/user/{user_id} | Get User Usage


# **getOrganizationUsageV1UsageOrganizationOrgIdGet**
> UsageReport getOrganizationUsageV1UsageOrganizationOrgIdGet(orgId, since, authorization)

Get Organization Usage

Get usage statistics for a specific organization.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getUsageApi();
final String orgId = orgId_example; // String | 
final String since = since_example; // String | ISO timestamp to filter from
final String authorization = authorization_example; // String | 

try {
    final response = api.getOrganizationUsageV1UsageOrganizationOrgIdGet(orgId, since, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling UsageApi->getOrganizationUsageV1UsageOrganizationOrgIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**|  | 
 **since** | **String**| ISO timestamp to filter from | [optional] 
 **authorization** | **String**|  | [optional] 

### Return type

[**UsageReport**](UsageReport.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSystemUsageV1UsageSystemGet**
> UsageReport getSystemUsageV1UsageSystemGet(since, authorization)

Get System Usage

Get system-wide usage statistics (Root only).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getUsageApi();
final String since = since_example; // String | ISO timestamp to filter from (e.g., '2026-02-01T00:00:00Z')
final String authorization = authorization_example; // String | 

try {
    final response = api.getSystemUsageV1UsageSystemGet(since, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling UsageApi->getSystemUsageV1UsageSystemGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **since** | **String**| ISO timestamp to filter from (e.g., '2026-02-01T00:00:00Z') | [optional] 
 **authorization** | **String**|  | [optional] 

### Return type

[**UsageReport**](UsageReport.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserUsageV1UsageUserUserIdGet**
> UsageReport getUserUsageV1UsageUserUserIdGet(userId, since, authorization)

Get User Usage

Get usage statistics for a specific user.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getUsageApi();
final String userId = userId_example; // String | 
final String since = since_example; // String | ISO timestamp to filter from
final String authorization = authorization_example; // String | 

try {
    final response = api.getUserUsageV1UsageUserUserIdGet(userId, since, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling UsageApi->getUserUsageV1UsageUserUserIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userId** | **String**|  | 
 **since** | **String**| ISO timestamp to filter from | [optional] 
 **authorization** | **String**|  | [optional] 

### Return type

[**UsageReport**](UsageReport.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

