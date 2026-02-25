# backend_api.model.WorkflowResponse

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  | 
**name** | **String** |  | 
**description** | **String** |  | [optional] [default to '']
**steps** | [**List&lt;WorkflowStep&gt;**](WorkflowStep.md) |  | 
**defaultModelMapping** | **Map&lt;String, String&gt;** |  | [optional] [default to {}]
**uiSchema** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**isPublic** | **bool** |  | [optional] [default to false]
**status** | **String** |  | [optional] [default to 'draft']
**version** | **int** |  | [optional] [default to 1]
**scoringLogic** | [**List&lt;Map&lt;String, Object&gt;&gt;**](Map.md) |  | [optional] [default to []]
**createdAt** | [**dynamic**](dynamic.md) |  | [optional] 
**updatedAt** | [**dynamic**](dynamic.md) |  | [optional] 
**organizationId** | **String** |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


