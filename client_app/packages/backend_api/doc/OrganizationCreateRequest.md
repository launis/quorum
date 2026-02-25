# backend_api.model.OrganizationCreateRequest

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  | [optional] 
**name** | **String** |  | 
**tier** | **String** |  | [optional] [default to 'standard']
**contactEmail** | **String** |  | [optional] 
**billingId** | **String** |  | [optional] 
**subscriptionStatus** | [**SubscriptionStatus**](SubscriptionStatus.md) |  | [optional] [default to SubscriptionStatus.trial]
**quotaLimit** | **num** |  | [optional] [default to 10.0]
**settingsOverride** | **Map&lt;String, Object&gt;** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


