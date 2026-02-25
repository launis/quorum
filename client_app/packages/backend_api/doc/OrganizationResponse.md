# backend_api.model.OrganizationResponse

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  | 
**name** | **String** |  | 
**tier** | **String** |  | 
**contactEmail** | **String** |  | [optional] 
**createdAt** | **String** |  | [optional] 
**billingId** | **String** |  | [optional] 
**subscriptionStatus** | [**SubscriptionStatus**](SubscriptionStatus.md) |  | [optional] [default to SubscriptionStatus.trial]
**quotaLimit** | **num** |  | [optional] [default to 10.0]
**tpmLimit** | **int** |  | [optional] [default to 100000]
**rpmLimit** | **int** |  | [optional] [default to 60]
**status** | **String** |  | [optional] [default to 'PENDING']

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


