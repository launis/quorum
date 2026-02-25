# backend_api.api.BuilderApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cloneStepBuilderStepsClonePost**](BuilderApi.md#clonestepbuilderstepsclonepost) | **POST** /builder/steps/clone | Clone Step
[**compileFusionBuilderCompilePost**](BuilderApi.md#compilefusionbuildercompilepost) | **POST** /builder/compile | Compile Fusion
[**copyWorkflowBuilderWorkflowsWorkflowIdCopyPost**](BuilderApi.md#copyworkflowbuilderworkflowsworkflowidcopypost) | **POST** /builder/workflows/{workflow_id}/copy | Copy Workflow
[**createCustomStepBuilderStepsCreateCustomPost**](BuilderApi.md#createcustomstepbuilderstepscreatecustompost) | **POST** /builder/steps/create-custom | Create Custom Step
[**createWorkflowBuilderWorkflowsPost**](BuilderApi.md#createworkflowbuilderworkflowspost) | **POST** /builder/workflows | Create Workflow
[**deleteWorkflowBuilderWorkflowsWorkflowIdDelete**](BuilderApi.md#deleteworkflowbuilderworkflowsworkflowiddelete) | **DELETE** /builder/workflows/{workflow_id} | Delete Workflow
[**generateIdBuilderUtilsGenerateIdGet**](BuilderApi.md#generateidbuilderutilsgenerateidget) | **GET** /builder/utils/generate-id | Generate ID
[**getAvailableAgentsBuilderConfigAgentsGet**](BuilderApi.md#getavailableagentsbuilderconfigagentsget) | **GET** /builder/config/agents | List Agent Class Metadata
[**getComponentSchemaBuilderSchemaComponentTypeGet**](BuilderApi.md#getcomponentschemabuilderschemacomponenttypeget) | **GET** /builder/schema/{component_type} | Get Component Schema
[**getFusionRulesBuilderConfigFusionRulesGet**](BuilderApi.md#getfusionrulesbuilderconfigfusionrulesget) | **GET** /builder/config/fusion-rules | Get Fusion Rules
[**getPromptTypesBuilderConfigPromptTypesGet**](BuilderApi.md#getprompttypesbuilderconfigprompttypesget) | **GET** /builder/config/prompt-types | Get Prompt Types
[**getSeedDataBuilderSeedDataGet**](BuilderApi.md#getseeddatabuilderseeddataget) | **GET** /builder/seed_data | Get Seed Data
[**getStepDetailsBuilderStepsStepIdGet**](BuilderApi.md#getstepdetailsbuilderstepsstepidget) | **GET** /builder/steps/{step_id} | Get Step Details
[**getWorkflowBuilderWorkflowsWorkflowIdGet**](BuilderApi.md#getworkflowbuilderworkflowsworkflowidget) | **GET** /builder/workflows/{workflow_id} | Get Workflow
[**getWorkflowTemplateBuilderConfigTemplateGet**](BuilderApi.md#getworkflowtemplatebuilderconfigtemplateget) | **GET** /builder/config/template | Get Template
[**listStepsBuilderStepsGet**](BuilderApi.md#liststepsbuilderstepsget) | **GET** /builder/steps | List Steps
[**listWorkflowsBuilderWorkflowsGet**](BuilderApi.md#listworkflowsbuilderworkflowsget) | **GET** /builder/workflows | List Workflows
[**previewChainBuilderWorkflowsWorkflowIdChainPreviewGet**](BuilderApi.md#previewchainbuilderworkflowsworkflowidchainpreviewget) | **GET** /builder/workflows/{workflow_id}/chain-preview | Preview Full Chain
[**previewStepBuilderStepsStepIdPreviewPost**](BuilderApi.md#previewstepbuilderstepsstepidpreviewpost) | **POST** /builder/steps/{step_id}/preview | Preview Step Prompt
[**runPromptBuilderPlaygroundRunPost**](BuilderApi.md#runpromptbuilderplaygroundrunpost) | **POST** /builder/playground/run | Run Prompt
[**updateStepBuilderStepsStepIdPut**](BuilderApi.md#updatestepbuilderstepsstepidput) | **PUT** /builder/steps/{step_id} | Update Step
[**updateWorkflowBuilderWorkflowsWorkflowIdPut**](BuilderApi.md#updateworkflowbuilderworkflowsworkflowidput) | **PUT** /builder/workflows/{workflow_id} | Update Workflow
[**validateConnectionBuilderValidatePost**](BuilderApi.md#validateconnectionbuildervalidatepost) | **POST** /builder/validate | Validate Connection


# **cloneStepBuilderStepsClonePost**
> StepDTO cloneStepBuilderStepsClonePost(bodyCloneStepBuilderStepsClonePost)

Clone Step

V2: Clone a step to a new Custom Step (Copy-on-Write).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final BodyCloneStepBuilderStepsClonePost bodyCloneStepBuilderStepsClonePost = ; // BodyCloneStepBuilderStepsClonePost | 

try {
    final response = api.cloneStepBuilderStepsClonePost(bodyCloneStepBuilderStepsClonePost);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->cloneStepBuilderStepsClonePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bodyCloneStepBuilderStepsClonePost** | [**BodyCloneStepBuilderStepsClonePost**](BodyCloneStepBuilderStepsClonePost.md)|  | 

### Return type

[**StepDTO**](StepDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compileFusionBuilderCompilePost**
> CompilationResponse compileFusionBuilderCompilePost(compileRequest)

Compile Fusion

V2: Prompt Fusion Compilation.  Replaces a sequence of steps with a compatible Composite Step (Panel).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final CompileRequest compileRequest = ; // CompileRequest | 

try {
    final response = api.compileFusionBuilderCompilePost(compileRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->compileFusionBuilderCompilePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compileRequest** | [**CompileRequest**](CompileRequest.md)|  | 

### Return type

[**CompilationResponse**](CompilationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **copyWorkflowBuilderWorkflowsWorkflowIdCopyPost**
> WorkflowResponse copyWorkflowBuilderWorkflowsWorkflowIdCopyPost(workflowId, copyWorkflowRequest)

Copy Workflow

Deep Copy a workflow structure (Shallow copy of steps).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String workflowId = workflowId_example; // String | 
final CopyWorkflowRequest copyWorkflowRequest = ; // CopyWorkflowRequest | 

try {
    final response = api.copyWorkflowBuilderWorkflowsWorkflowIdCopyPost(workflowId, copyWorkflowRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->copyWorkflowBuilderWorkflowsWorkflowIdCopyPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 
 **copyWorkflowRequest** | [**CopyWorkflowRequest**](CopyWorkflowRequest.md)|  | 

### Return type

[**WorkflowResponse**](WorkflowResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCustomStepBuilderStepsCreateCustomPost**
> StepDTO createCustomStepBuilderStepsCreateCustomPost(customStepCreateRequest)

Create Custom Step

Creates a new custom step definition server-side with proper defaults.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final CustomStepCreateRequest customStepCreateRequest = ; // CustomStepCreateRequest | 

try {
    final response = api.createCustomStepBuilderStepsCreateCustomPost(customStepCreateRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->createCustomStepBuilderStepsCreateCustomPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **customStepCreateRequest** | [**CustomStepCreateRequest**](CustomStepCreateRequest.md)|  | 

### Return type

[**StepDTO**](StepDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createWorkflowBuilderWorkflowsPost**
> WorkflowResponse createWorkflowBuilderWorkflowsPost(builderWorkflowCreateRequest, authorization)

Create Workflow

Create a new workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final BuilderWorkflowCreateRequest builderWorkflowCreateRequest = ; // BuilderWorkflowCreateRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.createWorkflowBuilderWorkflowsPost(builderWorkflowCreateRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->createWorkflowBuilderWorkflowsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **builderWorkflowCreateRequest** | [**BuilderWorkflowCreateRequest**](BuilderWorkflowCreateRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**WorkflowResponse**](WorkflowResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteWorkflowBuilderWorkflowsWorkflowIdDelete**
> BuilderWorkflowDeleteResponse deleteWorkflowBuilderWorkflowsWorkflowIdDelete(workflowId, authorization)

Delete Workflow

Delete a workflow AND its orphan steps (Garbage Collection).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String workflowId = workflowId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.deleteWorkflowBuilderWorkflowsWorkflowIdDelete(workflowId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->deleteWorkflowBuilderWorkflowsWorkflowIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**BuilderWorkflowDeleteResponse**](BuilderWorkflowDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateIdBuilderUtilsGenerateIdGet**
> GeneratedIdResponse generateIdBuilderUtilsGenerateIdGet(prefix)

Generate ID

Generates a unique ID with optional prefix.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String prefix = prefix_example; // String | 

try {
    final response = api.generateIdBuilderUtilsGenerateIdGet(prefix);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->generateIdBuilderUtilsGenerateIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prefix** | **String**|  | [optional] [default to 'custom_step']

### Return type

[**GeneratedIdResponse**](GeneratedIdResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAvailableAgentsBuilderConfigAgentsGet**
> List<AgentMetadataDTO> getAvailableAgentsBuilderConfigAgentsGet()

List Agent Class Metadata

Returns metadata for all registered agents, used for the Builder Toolbox.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();

try {
    final response = api.getAvailableAgentsBuilderConfigAgentsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getAvailableAgentsBuilderConfigAgentsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;AgentMetadataDTO&gt;**](AgentMetadataDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getComponentSchemaBuilderSchemaComponentTypeGet**
> ComponentSchemaResponse getComponentSchemaBuilderSchemaComponentTypeGet(componentType, authorization)

Get Component Schema

Retrieve the JSON Schema for a specific component type (SDUI).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String componentType = componentType_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.getComponentSchemaBuilderSchemaComponentTypeGet(componentType, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getComponentSchemaBuilderSchemaComponentTypeGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **componentType** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ComponentSchemaResponse**](ComponentSchemaResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getFusionRulesBuilderConfigFusionRulesGet**
> List<FusionRuleDTO> getFusionRulesBuilderConfigFusionRulesGet()

Get Fusion Rules

Returns validation rules for prompt fusion.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();

try {
    final response = api.getFusionRulesBuilderConfigFusionRulesGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getFusionRulesBuilderConfigFusionRulesGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;FusionRuleDTO&gt;**](FusionRuleDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPromptTypesBuilderConfigPromptTypesGet**
> List<String> getPromptTypesBuilderConfigPromptTypesGet()

Get Prompt Types

Returns list of component types that can be used as prompts.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();

try {
    final response = api.getPromptTypesBuilderConfigPromptTypesGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getPromptTypesBuilderConfigPromptTypesGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**List&lt;String&gt;**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSeedDataBuilderSeedDataGet**
> SeedDataResponse getSeedDataBuilderSeedDataGet(authorization)

Get Seed Data

Retrieves the raw seed data configuration (components, steps, workflows).  Now scoped by User Role (Root sees all).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.getSeedDataBuilderSeedDataGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getSeedDataBuilderSeedDataGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**SeedDataResponse**](SeedDataResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStepDetailsBuilderStepsStepIdGet**
> StepDTO getStepDetailsBuilderStepsStepIdGet(stepId)

Get Step Details

V2: Get full configuration of a step.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.getStepDetailsBuilderStepsStepIdGet(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getStepDetailsBuilderStepsStepIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepDTO**](StepDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowBuilderWorkflowsWorkflowIdGet**
> WorkflowResponse getWorkflowBuilderWorkflowsWorkflowIdGet(workflowId)

Get Workflow

Get details of a specific workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String workflowId = workflowId_example; // String | 

try {
    final response = api.getWorkflowBuilderWorkflowsWorkflowIdGet(workflowId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getWorkflowBuilderWorkflowsWorkflowIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 

### Return type

[**WorkflowResponse**](WorkflowResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowTemplateBuilderConfigTemplateGet**
> WorkflowTemplate getWorkflowTemplateBuilderConfigTemplateGet()

Get Template

Returns a valid empty workflow template.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();

try {
    final response = api.getWorkflowTemplateBuilderConfigTemplateGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->getWorkflowTemplateBuilderConfigTemplateGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**WorkflowTemplate**](WorkflowTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listStepsBuilderStepsGet**
> List<StepDTO> listStepsBuilderStepsGet()

List Steps

List all available steps.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();

try {
    final response = api.listStepsBuilderStepsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->listStepsBuilderStepsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;StepDTO&gt;**](StepDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listWorkflowsBuilderWorkflowsGet**
> List<WorkflowResponse> listWorkflowsBuilderWorkflowsGet(authorization)

List Workflows

List all workflows visible to the current user.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String authorization = authorization_example; // String | 

try {
    final response = api.listWorkflowsBuilderWorkflowsGet(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->listWorkflowsBuilderWorkflowsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**List&lt;WorkflowResponse&gt;**](WorkflowResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **previewChainBuilderWorkflowsWorkflowIdChainPreviewGet**
> ChainPreviewResponse previewChainBuilderWorkflowsWorkflowIdChainPreviewGet(workflowId)

Preview Full Chain

Generates a markdown preview of the entire workflow chain.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String workflowId = workflowId_example; // String | 

try {
    final response = api.previewChainBuilderWorkflowsWorkflowIdChainPreviewGet(workflowId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->previewChainBuilderWorkflowsWorkflowIdChainPreviewGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 

### Return type

[**ChainPreviewResponse**](ChainPreviewResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **previewStepBuilderStepsStepIdPreviewPost**
> StepPreviewResponse previewStepBuilderStepsStepIdPreviewPost(stepId)

Preview Step Prompt

Previews the LLM prompt for a step.  Uses PromptBuilder to construct the full system prompt and fetch user prompt template.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.previewStepBuilderStepsStepIdPreviewPost(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->previewStepBuilderStepsStepIdPreviewPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepPreviewResponse**](StepPreviewResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runPromptBuilderPlaygroundRunPost**
> PlaygroundResponse runPromptBuilderPlaygroundRunPost(playgroundRequest)

Run Prompt

Executes a prompt template with variables against the LLM.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final PlaygroundRequest playgroundRequest = ; // PlaygroundRequest | 

try {
    final response = api.runPromptBuilderPlaygroundRunPost(playgroundRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->runPromptBuilderPlaygroundRunPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **playgroundRequest** | [**PlaygroundRequest**](PlaygroundRequest.md)|  | 

### Return type

[**PlaygroundResponse**](PlaygroundResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateStepBuilderStepsStepIdPut**
> StepDTO updateStepBuilderStepsStepIdPut(stepId, stepUpdateRequest)

Update Step

V2: Update a step configuration.  WARNING: This modifies the global step definition.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String stepId = stepId_example; // String | 
final StepUpdateRequest stepUpdateRequest = ; // StepUpdateRequest | 

try {
    final response = api.updateStepBuilderStepsStepIdPut(stepId, stepUpdateRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->updateStepBuilderStepsStepIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 
 **stepUpdateRequest** | [**StepUpdateRequest**](StepUpdateRequest.md)|  | 

### Return type

[**StepDTO**](StepDTO.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWorkflowBuilderWorkflowsWorkflowIdPut**
> WorkflowResponse updateWorkflowBuilderWorkflowsWorkflowIdPut(workflowId, workflowUpdateRequest, authorization)

Update Workflow

Update an existing workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final String workflowId = workflowId_example; // String | 
final WorkflowUpdateRequest workflowUpdateRequest = ; // WorkflowUpdateRequest | 
final String authorization = authorization_example; // String | 

try {
    final response = api.updateWorkflowBuilderWorkflowsWorkflowIdPut(workflowId, workflowUpdateRequest, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->updateWorkflowBuilderWorkflowsWorkflowIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 
 **workflowUpdateRequest** | [**WorkflowUpdateRequest**](WorkflowUpdateRequest.md)|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**WorkflowResponse**](WorkflowResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validateConnectionBuilderValidatePost**
> ValidationResponse validateConnectionBuilderValidatePost(validationRequest)

Validate Connection

Validates connection between two steps based on Agent I/O contracts.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getBuilderApi();
final ValidationRequest validationRequest = ; // ValidationRequest | 

try {
    final response = api.validateConnectionBuilderValidatePost(validationRequest);
    print(response);
} on DioException catch (e) {
    print('Exception when calling BuilderApi->validateConnectionBuilderValidatePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **validationRequest** | [**ValidationRequest**](ValidationRequest.md)|  | 

### Return type

[**ValidationResponse**](ValidationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

