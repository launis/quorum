# backend_api.model.LLMProviderConfig

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Configuration ID (unique key). | 
**provider** | **String** | Provider type (e.g. 'openai', 'vertex_ai'). | 
**modelName** | **String** | Model identifier (e.g. 'gpt-4', 'gemini-pro'). | 
**apiKey** | **String** |  | [optional] 
**baseUrl** | **String** |  | [optional] 
**temperature** | **num** | Sampling temperature. | [optional] [default to 0.7]
**tpmLimit** | **int** | Tokens per minute limit. 0=unlimited. | 
**rpmLimit** | **int** | Requests per minute limit. 0=unlimited. | 
**defaultMaxTokens** | **int** |  | [optional] 
**vertexLocation** | **String** |  | [optional] 
**supportsGrounding** | **bool** | Whether this model supports Google Search Grounding. | [optional] [default to false]
**isActive** | **bool** | Whether this provider is active. | [optional] [default to true]
**additionalParams** | **Map&lt;String, Object&gt;** | Additional provider-specific parameters. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


