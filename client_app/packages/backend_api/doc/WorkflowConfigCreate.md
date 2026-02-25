# backend_api.model.WorkflowConfigCreate

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | New Workflow UUID | [optional] 
**slug** | **String** |  | [optional] 
**name** | **String** | Workflow Name | 
**sequence** | **List&lt;String&gt;** | List of Step IDs | [optional] [default to []]
**description** | **String** |  | [optional] 
**defaultModelMapping** | **Map&lt;String, String&gt;** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


