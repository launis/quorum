# backend_api.model.SystemSettings

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**maintenanceMode** | **bool** | If True, only ROOT can login/act. | [optional] [default to false]
**allowSignups** | **bool** | If True, new users can register. | [optional] [default to true]
**globalBanner** | **String** |  | [optional] 
**defaultModelStrategy** | **String** | Default LLM strategy for new agents. | [optional] [default to 'fast']
**enableBetaFeatures** | **bool** | Toggle experimental features. | [optional] [default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


