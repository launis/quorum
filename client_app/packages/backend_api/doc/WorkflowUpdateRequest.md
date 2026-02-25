# backend_api.model.WorkflowUpdateRequest

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** |  | [optional] 
**description** | **String** | New description. | [optional] [default to '']
**steps** | **List&lt;String&gt;** |  | [optional] 
**uiSchema** | **Map&lt;String, Object&gt;** |  | [optional] 
**defaultModelMapping** | **Map&lt;String, String&gt;** |  | [optional] 
**isPublic** | **bool** |  | [optional] 
**status** | **String** |  | [optional] 
**version** | **int** |  | [optional] 
**scoringLogic** | [**List&lt;Map&lt;String, Object&gt;&gt;**](Map.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


