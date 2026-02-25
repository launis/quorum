# backend_api.api.KnowledgeApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getIngestionStatusV1ConfigKnowledgeIngestJobIdGet**](KnowledgeApi.md#getingestionstatusv1configknowledgeingestjobidget) | **GET** /v1/config/knowledge/ingest/{job_id} | Get Ingestion Status
[**getKnowledgeStatusV1ConfigKnowledgeStatusGet**](KnowledgeApi.md#getknowledgestatusv1configknowledgestatusget) | **GET** /v1/config/knowledge/status | Get Knowledge Status
[**ingestKnowledgeBaseV1ConfigKnowledgeIngestPost**](KnowledgeApi.md#ingestknowledgebasev1configknowledgeingestpost) | **POST** /v1/config/knowledge/ingest | Ingest Knowledge Base
[**resetKnowledgeBaseV1ConfigKnowledgeResetDelete**](KnowledgeApi.md#resetknowledgebasev1configknowledgeresetdelete) | **DELETE** /v1/config/knowledge/reset | Reset Knowledge Base


# **getIngestionStatusV1ConfigKnowledgeIngestJobIdGet**
> KnowledgeJobStatusResponse getIngestionStatusV1ConfigKnowledgeIngestJobIdGet(jobId)

Get Ingestion Status

Polls the status of an ingestion job.  Args:     job_id (str): The unique identifier of the ingestion job.  Returns:     KnowledgeJobStatusResponse: The current state of the job (status, progress, stage, result, error).  Raises:     AppException: If the job_id is not found (404 JOB_NOT_FOUND).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getKnowledgeApi();
final String jobId = jobId_example; // String | 

try {
    final response = api.getIngestionStatusV1ConfigKnowledgeIngestJobIdGet(jobId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling KnowledgeApi->getIngestionStatusV1ConfigKnowledgeIngestJobIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jobId** | **String**|  | 

### Return type

[**KnowledgeJobStatusResponse**](KnowledgeJobStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getKnowledgeStatusV1ConfigKnowledgeStatusGet**
> KnowledgeStatusResponse getKnowledgeStatusV1ConfigKnowledgeStatusGet()

Get Knowledge Status

Checks the status of the Knowledge Base.  Returns:     KnowledgeStatusResponse: Contains a boolean indicating if documents exist,                              and counts of documents and precedents.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getKnowledgeApi();

try {
    final response = api.getKnowledgeStatusV1ConfigKnowledgeStatusGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling KnowledgeApi->getKnowledgeStatusV1ConfigKnowledgeStatusGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**KnowledgeStatusResponse**](KnowledgeStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ingestKnowledgeBaseV1ConfigKnowledgeIngestPost**
> KnowledgeIngestResponse ingestKnowledgeBaseV1ConfigKnowledgeIngestPost(file, language, modelStrategy)

Ingest Knowledge Base

Starts an asynchronous knowledge base ingestion job.  This endpoint accepts a file upload (DOCX or MD), initiates an asynchronous processing task, and returns a job ID for polling status.  Args:     background_tasks (BackgroundTasks): FastAPI background task manager.     file (UploadFile): The file to ingest (docx, md).     service (KnowledgeBaseServiceDep): The knowledge base service dependency.     language (str): Language code of the document (e.g. 'en', 'fi', 'auto').                   Defaults to \"auto\".  Returns:     KnowledgeIngestResponse: A generic response containing the 'job_id'.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getKnowledgeApi();
final MultipartFile file = BINARY_DATA_HERE; // MultipartFile | 
final String language = language_example; // String | 
final String modelStrategy = modelStrategy_example; // String | 

try {
    final response = api.ingestKnowledgeBaseV1ConfigKnowledgeIngestPost(file, language, modelStrategy);
    print(response);
} on DioException catch (e) {
    print('Exception when calling KnowledgeApi->ingestKnowledgeBaseV1ConfigKnowledgeIngestPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **MultipartFile**|  | 
 **language** | **String**|  | [optional] [default to 'auto']
 **modelStrategy** | **String**|  | [optional] 

### Return type

[**KnowledgeIngestResponse**](KnowledgeIngestResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetKnowledgeBaseV1ConfigKnowledgeResetDelete**
> KnowledgeResetResponse resetKnowledgeBaseV1ConfigKnowledgeResetDelete()

Reset Knowledge Base

Resets the Knowledge Base by deleting all items.  Args:     service (KnowledgeBaseServiceDep): The knowledge base service dependency.  Returns:     KnowledgeResetResponse: Success message.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getKnowledgeApi();

try {
    final response = api.resetKnowledgeBaseV1ConfigKnowledgeResetDelete();
    print(response);
} on DioException catch (e) {
    print('Exception when calling KnowledgeApi->resetKnowledgeBaseV1ConfigKnowledgeResetDelete: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**KnowledgeResetResponse**](KnowledgeResetResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

