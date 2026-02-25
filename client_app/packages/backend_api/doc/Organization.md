# backend_api.model.Organization

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Unique Organization ID (e.g. 'nokia-v1') | [optional] 
**slug** | **String** |  | [optional] 
**name** | **String** | Display Name | 
**createdAt** | [**DateTime**](DateTime.md) |  | [optional] 
**isActive** | **bool** | Subscription status | [optional] [default to true]
**tier** | **String** | Service Tier | [optional] [default to 'standard']
**contactEmail** | **String** |  | [optional] 
**billingId** | **String** |  | [optional] 
**subscriptionStatus** | [**SubscriptionStatus**](SubscriptionStatus.md) | Current billing status | [optional] [default to SubscriptionStatus.trial]
**quotaLimit** | **num** | Monthly API call quota (USD) | [optional] [default to 10.0]
**tpmLimit** | **int** | Tokens Per Minute Limit | [optional] [default to 100000]
**rpmLimit** | **int** | Requests Per Minute Limit | [optional] [default to 60]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


