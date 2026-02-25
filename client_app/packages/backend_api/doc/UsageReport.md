# backend_api.model.UsageReport

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scope** | **String** | Scope of the report (system, organization, user). | 
**entityId** | **String** |  | [optional] 
**period** | **String** | Reporting period (e.g., '2026-02', 'all-time'). | 
**usage** | [**TokenUsage**](TokenUsage.md) | Aggregated token and cost statistics. | [optional] 
**quotaLimitUsd** | **num** |  | [optional] 
**percentageUsed** | **num** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


