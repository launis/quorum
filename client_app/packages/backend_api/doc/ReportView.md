# backend_api.model.ReportView

## Load the model package
```dart
import 'package:backend_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**viewId** | **String** | The Execution ID | 
**title** | **String** | Page title | [optional] [default to 'Auditintiraportti']
**statusTheme** | **String** | Visual theme: 'success' | 'warning' | 'danger' | [optional] [default to 'success']
**sections** | [**List&lt;UiSection&gt;**](UiSection.md) | Ordered list of UI sections | [optional] 
**metrics** | **Map&lt;String, Object&gt;** |  | [optional] 
**systemNotification** | [**SystemNotification**](SystemNotification.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


