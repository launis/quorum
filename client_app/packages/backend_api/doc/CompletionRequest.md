# backend_api.model.CompletionRequest

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **String** | The primary prompt text. | 
**systemInstruction** | **String** |  | [optional] 
**modelStrategy** | **String** | Strategy key (fast, deep, etc) or direct model name. | [optional] [default to 'fast']
**responseSchema** | **Map&lt;String, Object&gt;** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


