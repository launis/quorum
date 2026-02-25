# backend_api.model.User

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **String** | User email address | 
**displayName** | **String** |  | [optional] 
**role** | [**UserRole**](UserRole.md) | Assigned permission role | [optional] [default to UserRole.MEMBER]
**organizationId** | **String** |  | [optional] 
**isActive** | **bool** | Is the account active? | [optional] [default to true]
**language** | **String** | Preferred UI language | [optional] [default to 'fi']
**themeMode** | **String** | Preferred Theme Mode | [optional] [default to 'system']
**id** | **String** | Unique ID (matches Firebase UID if used) | [optional] 
**slug** | **String** |  | [optional] 
**createdAt** | [**DateTime**](DateTime.md) | ISO 8601 Timestamp | 
**createdBy** | **String** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


