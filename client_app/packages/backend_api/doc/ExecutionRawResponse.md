# backend_api.model.ExecutionRawResponse

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  | 
**workflowId** | **String** |  | 
**status** | **String** |  | 
**startedAt** | [**DateTime**](DateTime.md) |  | 
**completedAt** | [**DateTime**](DateTime.md) |  | 
**durationSeconds** | **num** |  | [optional] 
**inputs** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**results** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**state** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**userId** | **String** |  | 
**agentOutputs** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**hookOutputs** | **Map&lt;String, Object&gt;** |  | [optional] [default to {}]
**xaiReport** | **String** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


