# backend_api.api.ExecutionsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancelExecutionExecutionsExecutionIdCancelDelete**](ExecutionsApi.md#cancelexecutionexecutionsexecutionidcanceldelete) | **DELETE** /executions/{execution_id}/cancel | Cancel Execution
[**cancelPdfGenerationExecutionsExecutionIdPdfCancelDelete**](ExecutionsApi.md#cancelpdfgenerationexecutionsexecutionidpdfcanceldelete) | **DELETE** /executions/{execution_id}/pdf/cancel | Cancel PDF Generation
[**createExecutionExecutionsPost**](ExecutionsApi.md#createexecutionexecutionspost) | **POST** /executions/ | Create Execution
[**deleteExecutionExecutionsExecutionIdDelete**](ExecutionsApi.md#deleteexecutionexecutionsexecutioniddelete) | **DELETE** /executions/{execution_id} | Delete Execution
[**downloadExecutionPdfExecutionsExecutionIdPdfDownloadGet**](ExecutionsApi.md#downloadexecutionpdfexecutionsexecutionidpdfdownloadget) | **GET** /executions/{execution_id}/pdf/download | Download Execution PDF
[**getExecutionExecutionsExecutionIdGet**](ExecutionsApi.md#getexecutionexecutionsexecutionidget) | **GET** /executions/{execution_id} | Get Execution Details
[**getExecutionJsonExportExecutionsExecutionIdJsonGet**](ExecutionsApi.md#getexecutionjsonexportexecutionsexecutionidjsonget) | **GET** /executions/{execution_id}/json | Export Execution JSON
[**getExecutionRawExecutionsExecutionIdRawGet**](ExecutionsApi.md#getexecutionrawexecutionsexecutionidrawget) | **GET** /executions/{execution_id}/raw | Get Raw Execution Data
[**getExecutionViewExecutionsExecutionIdViewGet**](ExecutionsApi.md#getexecutionviewexecutionsexecutionidviewget) | **GET** /executions/{execution_id}/view | Get Execution Report View (BFF)
[**getFlatReportExecutionsExecutionIdFlatGet**](ExecutionsApi.md#getflatreportexecutionsexecutionidflatget) | **GET** /executions/{execution_id}/flat | Get Flat Report (Integration)
[**getPdfProgressExecutionsExecutionIdPdfProgressGet**](ExecutionsApi.md#getpdfprogressexecutionsexecutionidpdfprogressget) | **GET** /executions/{execution_id}/pdf/progress | Track PDF Generation Progress
[**getPdfReportExecutionsExecutionIdPdfGet**](ExecutionsApi.md#getpdfreportexecutionsexecutionidpdfget) | **GET** /executions/{execution_id}/pdf | Download PDF Report
[**getRecentExecutionsExecutionsRecentGet**](ExecutionsApi.md#getrecentexecutionsexecutionsrecentget) | **GET** /executions/recent | Get Recent Executions
[**monitorExecutionExecutionsExecutionIdEventsGet**](ExecutionsApi.md#monitorexecutionexecutionsexecutionideventsget) | **GET** /executions/{execution_id}/events | Monitor Execution (SSE)


# **cancelExecutionExecutionsExecutionIdCancelDelete**
> ExecutionCancelResponse cancelExecutionExecutionsExecutionIdCancelDelete(executionId, authorization)

Cancel Execution

Signals the workflow engine to cancel the running execution.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.cancelExecutionExecutionsExecutionIdCancelDelete(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->cancelExecutionExecutionsExecutionIdCancelDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionCancelResponse**](ExecutionCancelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancelPdfGenerationExecutionsExecutionIdPdfCancelDelete**
> PDFCancelResponse cancelPdfGenerationExecutionsExecutionIdPdfCancelDelete(executionId, authorization)

Cancel PDF Generation

Cancels the download process and cleans up files.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.cancelPdfGenerationExecutionsExecutionIdPdfCancelDelete(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->cancelPdfGenerationExecutionsExecutionIdPdfCancelDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**PDFCancelResponse**](PDFCancelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createExecutionExecutionsPost**
> ExecutionResponse createExecutionExecutionsPost(authorization)

Create Execution

Creates a new execution for a given workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.createExecutionExecutionsPost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->createExecutionExecutionsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionResponse**](ExecutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteExecutionExecutionsExecutionIdDelete**
> ExecutionDeleteResponse deleteExecutionExecutionsExecutionIdDelete(executionId, authorization)

Delete Execution

Delete an execution record.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.deleteExecutionExecutionsExecutionIdDelete(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->deleteExecutionExecutionsExecutionIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionDeleteResponse**](ExecutionDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **downloadExecutionPdfExecutionsExecutionIdPdfDownloadGet**
> ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet downloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(executionId, checkLocal, authorization)

Download Execution PDF

Securely download the PDF report. Enqueues generation if missing.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final bool checkLocal = true; // bool | 
final String authorization = authorization_example; // String | 

try {
    final response = api.downloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(executionId, checkLocal, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->downloadExecutionPdfExecutionsExecutionIdPdfDownloadGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **checkLocal** | **bool**|  | [optional] [default to false]
 **authorization** | **String**|  | [optional] 

### Return type

[**ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet**](ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getExecutionExecutionsExecutionIdGet**
> ExecutionResponse getExecutionExecutionsExecutionIdGet(executionId, authorization)

Get Execution Details

Get execution details by ID. Returns standardized ExecutionResponse.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getExecutionExecutionsExecutionIdGet(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getExecutionExecutionsExecutionIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionResponse**](ExecutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getExecutionJsonExportExecutionsExecutionIdJsonGet**
> ReportView getExecutionJsonExportExecutionsExecutionIdJsonGet(executionId)

Export Execution JSON

Returns the execution report as a raw JSON dump (Common Intermediate Representation).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 

try {
    final response = api.getExecutionJsonExportExecutionsExecutionIdJsonGet(executionId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getExecutionJsonExportExecutionsExecutionIdJsonGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 

### Return type

[**ReportView**](ReportView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getExecutionRawExecutionsExecutionIdRawGet**
> ExecutionRawResponse getExecutionRawExecutionsExecutionIdRawGet(executionId, authorization)

Get Raw Execution Data

Returns complete raw execution data including agent and hook outputs.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getExecutionRawExecutionsExecutionIdRawGet(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getExecutionRawExecutionsExecutionIdRawGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionRawResponse**](ExecutionRawResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getExecutionViewExecutionsExecutionIdViewGet**
> ReportView getExecutionViewExecutionsExecutionIdViewGet(executionId, acceptLanguage, authorization)

Get Execution Report View (BFF)

Returns the SDUI-optimized view model for the Report UI.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String acceptLanguage = acceptLanguage_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getExecutionViewExecutionsExecutionIdViewGet(executionId, acceptLanguage, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getExecutionViewExecutionsExecutionIdViewGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **acceptLanguage** | **String**|  | [optional] 
 **authorization** | **String**|  | [optional] 

### Return type

[**ReportView**](ReportView.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getFlatReportExecutionsExecutionIdFlatGet**
> XAIFlatReportDTO getFlatReportExecutionsExecutionIdFlatGet(executionId, authorization)

Get Flat Report (Integration)

Returns the machine-readable flat report (XAIFlatReportDTO).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getFlatReportExecutionsExecutionIdFlatGet(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getFlatReportExecutionsExecutionIdFlatGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**XAIFlatReportDTO**](XAIFlatReportDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPdfProgressExecutionsExecutionIdPdfProgressGet**
> Object getPdfProgressExecutionsExecutionIdPdfProgressGet(executionId, authorization)

Track PDF Generation Progress

Server-Sent Events (SSE) for PDF generation progress.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getPdfProgressExecutionsExecutionIdPdfProgressGet(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getPdfProgressExecutionsExecutionIdPdfProgressGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

**Object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPdfReportExecutionsExecutionIdPdfGet**
> getPdfReportExecutionsExecutionIdPdfGet(executionId, authorization)

Download PDF Report

Generates and returns the PDF report.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    api.getPdfReportExecutionsExecutionIdPdfGet(executionId, authorization);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getPdfReportExecutionsExecutionIdPdfGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRecentExecutionsExecutionsRecentGet**
> List<ExecutionResponse> getRecentExecutionsExecutionsRecentGet(limit, authorization)

Get Recent Executions

Get a list of recent executions.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final int limit = 56; // int | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getRecentExecutionsExecutionsRecentGet(limit, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->getRecentExecutionsExecutionsRecentGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 10]
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;ExecutionResponse&gt;**](ExecutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **monitorExecutionExecutionsExecutionIdEventsGet**
> Object monitorExecutionExecutionsExecutionIdEventsGet(executionId, view, acceptLanguage)

Monitor Execution (SSE)

Server-Sent Events alias for monitoring.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionsApi();
final String executionId = executionId_example; // String | 
final String view = view_example; // String | 
final String acceptLanguage = acceptLanguage_example; // String | 

try {
    final response = api.monitorExecutionExecutionsExecutionIdEventsGet(executionId, view, acceptLanguage);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionsApi->monitorExecutionExecutionsExecutionIdEventsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **view** | **String**|  | [optional] [default to 'assessment']
 **acceptLanguage** | **String**|  | [optional] 

### Return type

**Object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

