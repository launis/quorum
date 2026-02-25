# backend_api.model.AuditEvent

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  | 
**timestamp** | [**DateTime**](DateTime.md) |  | 
**actorId** | **String** |  | 
**action** | **String** |  | 
**organizationId** | **String** |  | [optional] 
**targetId** | **String** |  | [optional] 
**details** | **Map&lt;String, Object&gt;** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


