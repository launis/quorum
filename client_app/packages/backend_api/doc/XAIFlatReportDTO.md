# backend_api.model.XAIFlatReportDTO

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**executionId** | **String** | The unique ID of the workflow execution. | 
**timestamp** | [**DateTime**](DateTime.md) | When this report was generated. | 
**verdict** | **String** | Final decision (e.g., 'Approved', 'Rejected'). | 
**scoreTotal** | **num** | The total calculated score (0.0 - 5.0). | 
**confidenceScore** | **num** | AI confidence in the result (0.0 - 1.0). | 
**topStrengthId** | **String** |  | [optional] 
**topWeaknessId** | **String** |  | [optional] 
**flattenedScores** | **Map&lt;String, num&gt;** | Key-value map of dimension IDs to their numeric scores. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


