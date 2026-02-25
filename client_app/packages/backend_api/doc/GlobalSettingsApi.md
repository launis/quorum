# backend_api.api.GlobalSettingsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getSettingsSettingsGet**](GlobalSettingsApi.md#getsettingssettingsget) | **GET** /settings | Get Settings
[**updateSettingsSettingsPatch**](GlobalSettingsApi.md#updatesettingssettingspatch) | **PATCH** /settings | Update Settings


# **getSettingsSettingsGet**
> SystemSettings getSettingsSettingsGet()

Get Settings

Retrieves the current global system connection settings.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getGlobalSettingsApi();

try {
    final response = api.getSettingsSettingsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling GlobalSettingsApi->getSettingsSettingsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**SystemSettings**](SystemSettings.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateSettingsSettingsPatch**
> SystemSettings updateSettingsSettingsPatch(systemSettings, authorization)

Update Settings

Updates global system settings.  Requires ROOT.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getGlobalSettingsApi();
final SystemSettings systemSettings = ; // SystemSettings | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateSettingsSettingsPatch(systemSettings, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling GlobalSettingsApi->updateSettingsSettingsPatch: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **systemSettings** | [**SystemSettings**](SystemSettings.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**SystemSettings**](SystemSettings.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

