# backend_api.api.AdminApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**addBannedPhraseAdminBannedPhrasesPost**](AdminApi.md#addbannedphraseadminbannedphrasespost) | **POST** /admin/banned-phrases | Add Banned Phrase
[**createOrganizationAdminOrganizationsPost**](AdminApi.md#createorganizationadminorganizationspost) | **POST** /admin/organizations | Create Organization
[**createUserAdminUsersPost**](AdminApi.md#createuseradminuserspost) | **POST** /admin/users | Create User
[**deleteBannedPhraseAdminBannedPhrasesPhraseDelete**](AdminApi.md#deletebannedphraseadminbannedphrasesphrasedelete) | **DELETE** /admin/banned-phrases/{phrase} | Remove Banned Phrase
[**deleteUserAdminUsersUserIdDelete**](AdminApi.md#deleteuseradminusersuseriddelete) | **DELETE** /admin/users/{user_id} | Delete User
[**exportSeedDataAdminExportSeedDataPost**](AdminApi.md#exportseeddataadminexportseeddatapost) | **POST** /admin/export/seed-data | Export Seed Data
[**generateBannedPhrasesAdminBannedPhrasesGeneratePost**](AdminApi.md#generatebannedphrasesadminbannedphrasesgeneratepost) | **POST** /admin/banned-phrases/generate | Generate Banned Phrases
[**getAssignableRolesAdminUsersRolesGet**](AdminApi.md#getassignablerolesadminusersrolesget) | **GET** /admin/users/roles | Get Assignable Roles
[**getBannedPhrasesAdminBannedPhrasesGet**](AdminApi.md#getbannedphrasesadminbannedphrasesget) | **GET** /admin/banned-phrases | List Banned Phrases
[**getIngestionStatusAdminKnowledgeBaseStatusJobIdGet**](AdminApi.md#getingestionstatusadminknowledgebasestatusjobidget) | **GET** /admin/knowledge-base/status/{job_id} | Get Ingestion Status (Legacy)
[**getQueueStatsAdminSystemQueueGet**](AdminApi.md#getqueuestatsadminsystemqueueget) | **GET** /admin/system/queue | Get Queue Statistics
[**getTaskStatusAdminStatusJobIdGet**](AdminApi.md#gettaskstatusadminstatusjobidget) | **GET** /admin/status/{job_id} | Get Task Status
[**listOrganizationUsersAdminOrgOrganizationIdUsersGet**](AdminApi.md#listorganizationusersadminorgorganizationidusersget) | **GET** /admin/org/{organization_id}/users | List Organization Users
[**rebuildDatabaseAdminDatabaseRebuildPost**](AdminApi.md#rebuilddatabaseadmindatabaserebuildpost) | **POST** /admin/database/rebuild | Rebuild Database
[**resetFirestoreDbAdminDatabaseResetFirestorePost**](AdminApi.md#resetfirestoredbadmindatabaseresetfirestorepost) | **POST** /admin/database/reset/firestore | Reset Firestore
[**resetMockDbAdminDatabaseResetMockPost**](AdminApi.md#resetmockdbadmindatabaseresetmockpost) | **POST** /admin/database/reset/mock | Reset Mock Database
[**resetProdDbAdminDatabaseResetProdPost**](AdminApi.md#resetproddbadmindatabaseresetprodpost) | **POST** /admin/database/reset/prod | Reset Production Database
[**runSelfTestAdminSelfTestPost**](AdminApi.md#runselftestadminselftestpost) | **POST** /admin/self-test | Run System Self-Test
[**triggerIngestAdminIngestPost**](AdminApi.md#triggeringestadminingestpost) | **POST** /admin/ingest | Trigger Ingestion
[**updateUserAdminUsersUserIdPatch**](AdminApi.md#updateuseradminusersuseridpatch) | **PATCH** /admin/users/{user_id} | Update User
[**updateUserRoleAdminUserUserIdRolePut**](AdminApi.md#updateuserroleadminuseruseridroleput) | **PUT** /admin/user/{user_id}/role | Update User Role
[**uploadKnowledgeBaseAdminKnowledgeBaseUploadPost**](AdminApi.md#uploadknowledgebaseadminknowledgebaseuploadpost) | **POST** /admin/knowledge-base/upload | Upload and Ingest File


# **addBannedPhraseAdminBannedPhrasesPost**
> BannedPhraseResponse addBannedPhraseAdminBannedPhrasesPost(bannedPhraseRequest)

Add Banned Phrase

Adds a new phrase to the banned list.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final BannedPhraseRequest bannedPhraseRequest = ; // BannedPhraseRequest | 

try {
    final response = api.addBannedPhraseAdminBannedPhrasesPost(bannedPhraseRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->addBannedPhraseAdminBannedPhrasesPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bannedPhraseRequest** | [**BannedPhraseRequest**](BannedPhraseRequest.md)|  | 

### Return type

[**BannedPhraseResponse**](BannedPhraseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createOrganizationAdminOrganizationsPost**
> Organization createOrganizationAdminOrganizationsPost(organizationCreate, authorization)

Create Organization

Creates a new Tenant Organization.  Args:     request (OrganizationCreate): Payload for the new organization.     user (CurrentUserDep): The requesting user (must be ROOT).     auth_service (AuthServiceDep): Authentication service dependency.  Returns:     Organization: The created organization.  Raises:     HTTPException: If user is not ROOT (403) or creation fails.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final OrganizationCreate organizationCreate = ; // OrganizationCreate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createOrganizationAdminOrganizationsPost(organizationCreate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->createOrganizationAdminOrganizationsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organizationCreate** | [**OrganizationCreate**](OrganizationCreate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**Organization**](Organization.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createUserAdminUsersPost**
> UserAdminView createUserAdminUsersPost(userCreate, authorization)

Create User

Creates a new user under the active organization constraints.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final UserCreate userCreate = ; // UserCreate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createUserAdminUsersPost(userCreate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->createUserAdminUsersPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userCreate** | [**UserCreate**](UserCreate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**UserAdminView**](UserAdminView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteBannedPhraseAdminBannedPhrasesPhraseDelete**
> BannedPhraseResponse deleteBannedPhraseAdminBannedPhrasesPhraseDelete(phrase)

Remove Banned Phrase

Removes a phrase from the banned list.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String phrase = phrase_example; // String | Phrase to remove

try {
    final response = api.deleteBannedPhraseAdminBannedPhrasesPhraseDelete(phrase);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->deleteBannedPhraseAdminBannedPhrasesPhraseDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **phrase** | **String**| Phrase to remove | 

### Return type

[**BannedPhraseResponse**](BannedPhraseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteUserAdminUsersUserIdDelete**
> GenericActionResponse deleteUserAdminUsersUserIdDelete(userId, authorization)

Delete User

Deletes a user (Enforces Last Admin Protection).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String userId = userId_example; // String | Target User UID
final String authorization = authorization_example; // String | 

try {
    final response = api.deleteUserAdminUsersUserIdDelete(userId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->deleteUserAdminUsersUserIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userId** | **String**| Target User UID | 
 **authorization** | **String**|  | [optional] 

### Return type

[**GenericActionResponse**](GenericActionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exportSeedDataAdminExportSeedDataPost**
> AdminTaskResponse exportSeedDataAdminExportSeedDataPost(authorization)

Export Seed Data

Trigger seed data export task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.exportSeedDataAdminExportSeedDataPost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->exportSeedDataAdminExportSeedDataPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateBannedPhrasesAdminBannedPhrasesGeneratePost**
> GeneratedPhrasesResponse generateBannedPhrasesAdminBannedPhrasesGeneratePost(generatePhrasesRequest)

Generate Banned Phrases

Uses LLM to generate banned phrases.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final GeneratePhrasesRequest generatePhrasesRequest = ; // GeneratePhrasesRequest | 

try {
    final response = api.generateBannedPhrasesAdminBannedPhrasesGeneratePost(generatePhrasesRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->generateBannedPhrasesAdminBannedPhrasesGeneratePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **generatePhrasesRequest** | [**GeneratePhrasesRequest**](GeneratePhrasesRequest.md)|  | 

### Return type

[**GeneratedPhrasesResponse**](GeneratedPhrasesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAssignableRolesAdminUsersRolesGet**
> List<UserRole> getAssignableRolesAdminUsersRolesGet(authorization)

Get Assignable Roles

Returns the list of roles the currently authenticated user is allowed to assign.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.getAssignableRolesAdminUsersRolesGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->getAssignableRolesAdminUsersRolesGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;UserRole&gt;**](UserRole.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getBannedPhrasesAdminBannedPhrasesGet**
> List<Map<String, Object>> getBannedPhrasesAdminBannedPhrasesGet()

List Banned Phrases

Retrieves all banned phrases from the repository.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();

try {
    final response = api.getBannedPhrasesAdminBannedPhrasesGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->getBannedPhrasesAdminBannedPhrasesGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;Map&lt;String, Object&gt;&gt;**](Map.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getIngestionStatusAdminKnowledgeBaseStatusJobIdGet**
> Object getIngestionStatusAdminKnowledgeBaseStatusJobIdGet(jobId)

Get Ingestion Status (Legacy)

Legacy endpoint redirection.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String jobId = jobId_example; // String | UUID of the background job

try {
    final response = api.getIngestionStatusAdminKnowledgeBaseStatusJobIdGet(jobId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->getIngestionStatusAdminKnowledgeBaseStatusJobIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobId** | **String**| UUID of the background job | 

### Return type

**Object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getQueueStatsAdminSystemQueueGet**
> QueueStats getQueueStatsAdminSystemQueueGet(authorization)

Get Queue Statistics

Retrieves current metrics from the ArQ Redis queue.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.getQueueStatsAdminSystemQueueGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->getQueueStatsAdminSystemQueueGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**QueueStats**](QueueStats.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTaskStatusAdminStatusJobIdGet**
> TaskStatusResponse getTaskStatusAdminStatusJobIdGet(jobId)

Get Task Status

Retrieves the status of a specific background task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String jobId = jobId_example; // String | UUID of the background job

try {
    final response = api.getTaskStatusAdminStatusJobIdGet(jobId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->getTaskStatusAdminStatusJobIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobId** | **String**| UUID of the background job | 

### Return type

[**TaskStatusResponse**](TaskStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listOrganizationUsersAdminOrgOrganizationIdUsersGet**
> List<UserAdminView> listOrganizationUsersAdminOrgOrganizationIdUsersGet(organizationId, authorization)

List Organization Users

Retrieve all users for a specific organization (Admin View).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String organizationId = organizationId_example; // String | Organization ID
final String authorization = authorization_example; // String | 

try {
    final response = api.listOrganizationUsersAdminOrgOrganizationIdUsersGet(organizationId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->listOrganizationUsersAdminOrgOrganizationIdUsersGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organizationId** | **String**| Organization ID | 
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;UserAdminView&gt;**](UserAdminView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rebuildDatabaseAdminDatabaseRebuildPost**
> AdminTaskResponse rebuildDatabaseAdminDatabaseRebuildPost(authorization)

Rebuild Database

Trigger database rebuild task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.rebuildDatabaseAdminDatabaseRebuildPost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->rebuildDatabaseAdminDatabaseRebuildPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetFirestoreDbAdminDatabaseResetFirestorePost**
> AdminTaskResponse resetFirestoreDbAdminDatabaseResetFirestorePost(authorization)

Reset Firestore

Trigger firestore database reset task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.resetFirestoreDbAdminDatabaseResetFirestorePost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->resetFirestoreDbAdminDatabaseResetFirestorePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetMockDbAdminDatabaseResetMockPost**
> AdminTaskResponse resetMockDbAdminDatabaseResetMockPost(authorization)

Reset Mock Database

Trigger mock database reset task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.resetMockDbAdminDatabaseResetMockPost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->resetMockDbAdminDatabaseResetMockPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetProdDbAdminDatabaseResetProdPost**
> AdminTaskResponse resetProdDbAdminDatabaseResetProdPost(authorization)

Reset Production Database

Trigger production database reset task.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.resetProdDbAdminDatabaseResetProdPost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->resetProdDbAdminDatabaseResetProdPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runSelfTestAdminSelfTestPost**
> SelfTestResponse runSelfTestAdminSelfTestPost()

Run System Self-Test

Executes a self-test of LLM and Database connectivity.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();

try {
    final response = api.runSelfTestAdminSelfTestPost();
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->runSelfTestAdminSelfTestPost: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**SelfTestResponse**](SelfTestResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **triggerIngestAdminIngestPost**
> AsyncJobResponse triggerIngestAdminIngestPost(ingestRequest, authorization)

Trigger Ingestion

Triggers ingestion from a local file path.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final IngestRequest ingestRequest = ; // IngestRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.triggerIngestAdminIngestPost(ingestRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->triggerIngestAdminIngestPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ingestRequest** | [**IngestRequest**](IngestRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**AsyncJobResponse**](AsyncJobResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateUserAdminUsersUserIdPatch**
> UserAdminView updateUserAdminUsersUserIdPatch(userId, userUpdate, authorization)

Update User

Updates an existing user profile.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String userId = userId_example; // String | Target User UID
final UserUpdate userUpdate = ; // UserUpdate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateUserAdminUsersUserIdPatch(userId, userUpdate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->updateUserAdminUsersUserIdPatch: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userId** | **String**| Target User UID | 
 **userUpdate** | [**UserUpdate**](UserUpdate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**UserAdminView**](UserAdminView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateUserRoleAdminUserUserIdRolePut**
> UserAdminView updateUserRoleAdminUserUserIdRolePut(userId, updateRoleRequest, authorization)

Update User Role

Updates a user's role (Enforces hierarchy).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final String userId = userId_example; // String | User ID
final UpdateRoleRequest updateRoleRequest = ; // UpdateRoleRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateUserRoleAdminUserUserIdRolePut(userId, updateRoleRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->updateUserRoleAdminUserUserIdRolePut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userId** | **String**| User ID | 
 **updateRoleRequest** | [**UpdateRoleRequest**](UpdateRoleRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**UserAdminView**](UserAdminView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **uploadKnowledgeBaseAdminKnowledgeBaseUploadPost**
> AdminTaskResponse uploadKnowledgeBaseAdminKnowledgeBaseUploadPost(file, resetDb, modelStrategy, authorization)

Upload and Ingest File

Uploads and ingests a file into the knowledge base.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAdminApi();
final MultipartFile file = BINARY_DATA_HERE; // MultipartFile | File to ingest.
final bool resetDb = true; // bool | Clear KB first.
final String modelStrategy = modelStrategy_example; // String | LLM Strategy (fast, deep). Default: None (Basic Parsing).
final String authorization = authorization_example; // String | 

try {
    final response = api.uploadKnowledgeBaseAdminKnowledgeBaseUploadPost(file, resetDb, modelStrategy, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AdminApi->uploadKnowledgeBaseAdminKnowledgeBaseUploadPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **MultipartFile**| File to ingest. | 
 **resetDb** | **bool**| Clear KB first. | [optional] [default to false]
 **modelStrategy** | **String**| LLM Strategy (fast, deep). Default: None (Basic Parsing). | [optional] 
 **authorization** | **String**|  | [optional] 

### Return type

[**AdminTaskResponse**](AdminTaskResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

