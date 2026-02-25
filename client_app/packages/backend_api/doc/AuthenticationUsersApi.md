# backend_api.api.AuthenticationUsersApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createUserAuthUsersPost**](AuthenticationUsersApi.md#createuserauthuserspost) | **POST** /auth/users | Create User
[**deleteUserAuthUsersIdDelete**](AuthenticationUsersApi.md#deleteuserauthusersiddelete) | **DELETE** /auth/users/{id} | Delete User
[**getMyProfileAuthMeGet**](AuthenticationUsersApi.md#getmyprofileauthmeget) | **GET** /auth/me | Get My Profile
[**impersonateUserAuthImpersonatePost**](AuthenticationUsersApi.md#impersonateuserauthimpersonatepost) | **POST** /auth/impersonate | Impersonate User
[**listAvailableRolesAuthRolesGet**](AuthenticationUsersApi.md#listavailablerolesauthrolesget) | **GET** /auth/roles | List Available Roles
[**listUsersAuthUsersGet**](AuthenticationUsersApi.md#listusersauthusersget) | **GET** /auth/users | List Users
[**updateUserAuthUsersIdPatch**](AuthenticationUsersApi.md#updateuserauthusersidpatch) | **PATCH** /auth/users/{id} | Update User
[**verifyUserTokenAuthVerifyPost**](AuthenticationUsersApi.md#verifyusertokenauthverifypost) | **POST** /auth/verify | Verify User Token


# **createUserAuthUsersPost**
> User createUserAuthUsersPost(userCreate, authorization)

Create User

Create a new user.  Args:     request (Request): The HTTP Request object.     user_data (UserCreate): Payload for the new user.     current_user (CurrentUserDep): The requesting user (must be ROOT, ADMIN, or MANAGER).     auth_service (AuthServiceDep): Authentication service dependency.  Returns:     User: The created user profile.  Raises:     HTTPException: If permission denied (403) or validation fails (400).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final UserCreate userCreate = ; // UserCreate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createUserAuthUsersPost(userCreate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->createUserAuthUsersPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userCreate** | [**UserCreate**](UserCreate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**User**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteUserAuthUsersIdDelete**
> UserDeleteResponse deleteUserAuthUsersIdDelete(id, authorization)

Delete User

Delete a user.  Enforces Last Admin Protection.  Args:     id (str): The UID of the user to delete.     current_user (CurrentUserDep): The requesting user (ROOT or ADMIN).     auth_service (AuthServiceDep): Authorization service.     repo (RepositoryDep): Repository dependency.  Returns:     UserDeleteResponse: Status confirmation.  Raises:     HTTPException: Permission denied (403) or business logic error (400).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final String id = id_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.deleteUserAuthUsersIdDelete(id, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->deleteUserAuthUsersIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**UserDeleteResponse**](UserDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMyProfileAuthMeGet**
> User getMyProfileAuthMeGet(authorization)

Get My Profile

Get the currently authenticated user's profile.  Args:     current_user (CurrentUserDep): The authenticated user.     auth_service (AuthServiceDep): Auth service.  Returns:     User: The full user profile.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.getMyProfileAuthMeGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->getMyProfileAuthMeGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**User**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **impersonateUserAuthImpersonatePost**
> ImpersonationResponse impersonateUserAuthImpersonatePost(impersonationRequest, authorization)

Impersonate User

Generates an impersonation token for the target user. Requires ROOT.  Args:     request (ImpersonationRequest): Payload containing target_id.     current_user (CurrentUserDep): The requesting user (must be ROOT).     auth_service (AuthServiceDep): Auth service.  Returns:     ImpersonationResponse: The access token.  Raises:     HTTPException: If permission denied (403) or target not found (404).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final ImpersonationRequest impersonationRequest = ; // ImpersonationRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.impersonateUserAuthImpersonatePost(impersonationRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->impersonateUserAuthImpersonatePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **impersonationRequest** | [**ImpersonationRequest**](ImpersonationRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ImpersonationResponse**](ImpersonationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAvailableRolesAuthRolesGet**
> List<String> listAvailableRolesAuthRolesGet()

List Available Roles

List all valid User Roles.  Used by frontend for dynamic dropdowns (Zero Hardcoding).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();

try {
    final response = api.listAvailableRolesAuthRolesGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->listAvailableRolesAuthRolesGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**List&lt;String&gt;**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listUsersAuthUsersGet**
> List<User> listUsersAuthUsersGet(authorization)

List Users

List users visible to the current user (scoped by Organization).  Args:     current_user (CurrentUserDep): The requesting user.     auth_service (AuthServiceDep): Authorization service.  Returns:     list[User]: A list of accessible user profiles.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.listUsersAuthUsersGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->listUsersAuthUsersGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;User&gt;**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateUserAuthUsersIdPatch**
> User updateUserAuthUsersIdPatch(id, userUpdate, authorization)

Update User

Update a user (Role, Display Name, etc).  Args:     id (str): The UID of the user to update.     user_update (UserUpdate): Fields to update.     current_user (CurrentUserDep): Requesting user.     auth_service (AuthServiceDep): Authorization service.  Returns:     User: The updated user profile.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final String id = id_example; // String | 
final UserUpdate userUpdate = ; // UserUpdate | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateUserAuthUsersIdPatch(id, userUpdate, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->updateUserAuthUsersIdPatch: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**|  | 
 **userUpdate** | [**UserUpdate**](UserUpdate.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**User**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyUserTokenAuthVerifyPost**
> LoginResponse verifyUserTokenAuthVerifyPost(tokenPayload)

Verify User Token

Exchanges a Firebase ID Token (or mock token) for the Backend User Profile.  Args:     request (Request): The HTTP Request object.     payload (TokenPayload): The token payload.     auth_service (AuthServiceDep): Authentication service dependency.  Returns:     LoginResponse: The authenticated user profile and status.  Raises:     HTTPException: If the user is found in Firebase but not in the DB (404),                    or if the token is invalid (401).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAuthenticationUsersApi();
final TokenPayload tokenPayload = ; // TokenPayload | 

try {
    final response = api.verifyUserTokenAuthVerifyPost(tokenPayload);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AuthenticationUsersApi->verifyUserTokenAuthVerifyPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tokenPayload** | [**TokenPayload**](TokenPayload.md)|  | 

### Return type

[**LoginResponse**](LoginResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

