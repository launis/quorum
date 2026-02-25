# backend_api.model.StepDefinition

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Unique step identifier | [optional] 
**slug** | **String** |  | [optional] 
**name** | **String** | Human-readable name | 
**description** | **String** |  | [optional] 
**taskKey** | **String** | Task Key (DB source) | [optional] [default to 'analyst']
**config** | **Map&lt;String, Object&gt;** | Configuration (DB source) | [optional] [default to {}]
**inputs** | **Map&lt;String, String&gt;** | Default Input Mapping | [optional] [default to {}]
**isMissingRegistry** | **bool** | Missing registry marker | [optional] [default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


