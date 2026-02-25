# backend_api.model.BuilderWorkflowCreateRequest

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | Name of the new workflow. | 
**description** | **String** | Optional description. | [optional] [default to '']
**steps** | **List&lt;String&gt;** | List of step IDs. | [optional] [default to []]
**defaultModelMapping** | **Map&lt;String, String&gt;** |  | [optional] 
**uiSchema** | **Map&lt;String, Object&gt;** |  | [optional] 
**isPublic** | **bool** | If True, visible to all tenants (System Only). | [optional] [default to false]
**status** | **String** | Lifecycle status. | [optional] [default to 'draft']
**version** | **int** | Version number. | [optional] [default to 1]
**scoringLogic** | [**List&lt;Map&lt;String, Object&gt;&gt;**](Map.md) | Scoring configuration. | [optional] [default to []]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


