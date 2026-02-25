# backend_api.model.WorkflowConfigDefinition

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Workflow UUID | [optional] 
**slug** | **String** |  | [optional] 
**name** | **String** | Workflow Name | 
**description** | **String** |  | [optional] 
**sequence** | **List&lt;String&gt;** | Ordered list of Step IDs | [optional] [default to []]
**steps** | [**Steps**](Steps.md) |  | [optional] 
**uiSchema** | **Map&lt;String, Object&gt;** |  | [optional] 
**defaultModelMapping** | **Map&lt;String, String&gt;** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


