# backend_api.model.WorkflowStep

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Unique step identifier, e.g., 'safety_check' | [optional] 
**slug** | **String** |  | [optional] 
**name** | **String** | Human-readable name of the step | 
**description** | **String** |  | [optional] 
**taskKey** | **String** | Registry Task Name (matches @register_task name) | 
**inputs** | **Map&lt;String, String&gt;** | Maps task inputs to state values. Example: {'text': '$inputs.history_text'} | [optional] 
**config** | **Map&lt;String, Object&gt;** | Optional static config for the task | [optional] 
**isMissingRegistry** | **bool** | UI Helper: True if this step references a task_key not in the backend registry. | [optional] [default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


