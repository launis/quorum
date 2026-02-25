# backend_api.api.AuditApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getAuditLogsAuditLogsGet**](AuditApi.md#getauditlogsauditlogsget) | **GET** /audit/logs | Get Audit Logs


# **getAuditLogsAuditLogsGet**
> List<AuditEvent> getAuditLogsAuditLogsGet(organizationId, actorId, action, limit, authorization)

Get Audit Logs

Retrieve audit logs.  Role Rules: - ROOT: Can see logs for ANY organization or system-wide (if org_id is None). - ADMIN: Can ONLY see logs for THEIR OWN organization. - MEMBER: Cannot see audit logs (403).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuditApi();
final String organizationId = organizationId_example; // String | Filter by Organization ID
final String actorId = actorId_example; // String | Filter by Actor UID
final String action = action_example; // String | Filter by Action type
final int limit = 56; // int | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getAuditLogsAuditLogsGet(organizationId, actorId, action, limit, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuditApi->getAuditLogsAuditLogsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organizationId** | **String**| Filter by Organization ID | [optional] 
 **actorId** | **String**| Filter by Actor UID | [optional] 
 **action** | **String**| Filter by Action type | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;AuditEvent&gt;**](AuditEvent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

