# backend_api.api.ConfigurationApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createComponentV1ConfigComponentsPost**](ConfigurationApi.md#createcomponentv1configcomponentspost) | **POST** /v1/config/components | Create Component
[**createStepV1ConfigStepsPost**](ConfigurationApi.md#createstepv1configstepspost) | **POST** /v1/config/steps | Create Step
[**createWorkflowV1ConfigWorkflowsPost**](ConfigurationApi.md#createworkflowv1configworkflowspost) | **POST** /v1/config/workflows | Create Workflow
[**deleteComponentV1ConfigComponentsCompIdDelete**](ConfigurationApi.md#deletecomponentv1configcomponentscompiddelete) | **DELETE** /v1/config/components/{comp_id} | Delete Component
[**deleteStepV1ConfigStepsStepIdDelete**](ConfigurationApi.md#deletestepv1configstepsstepiddelete) | **DELETE** /v1/config/steps/{step_id} | Delete Step
[**deleteWorkflowV1ConfigWorkflowsWfIdDelete**](ConfigurationApi.md#deleteworkflowv1configworkflowswfiddelete) | **DELETE** /v1/config/workflows/{wf_id} | Delete Workflow
[**getComponentV1ConfigComponentsCompIdGet**](ConfigurationApi.md#getcomponentv1configcomponentscompidget) | **GET** /v1/config/components/{comp_id} | Get Component
[**getComponentsV1ConfigComponentsGet**](ConfigurationApi.md#getcomponentsv1configcomponentsget) | **GET** /v1/config/components | List Components
[**getModelSchemaV1ConfigSchemasModelNameGet**](ConfigurationApi.md#getmodelschemav1configschemasmodelnameget) | **GET** /v1/config/schemas/{model_name} | Get Model JSON Schema
[**getSchemasV1ConfigSchemasGet**](ConfigurationApi.md#getschemasv1configschemasget) | **GET** /v1/config/schemas | List Schemas
[**getStepV1ConfigStepsStepIdGet**](ConfigurationApi.md#getstepv1configstepsstepidget) | **GET** /v1/config/steps/{step_id} | Get Step
[**getStepsV1ConfigStepsGet**](ConfigurationApi.md#getstepsv1configstepsget) | **GET** /v1/config/steps | List Steps
[**getWorkflowV1ConfigWorkflowsWfIdGet**](ConfigurationApi.md#getworkflowv1configworkflowswfidget) | **GET** /v1/config/workflows/{wf_id} | Get Workflow
[**getWorkflowsV1ConfigWorkflowsGet**](ConfigurationApi.md#getworkflowsv1configworkflowsget) | **GET** /v1/config/workflows | List Workflows
[**listRegistryItemsV1ConfigComponentsRegistryItemsGet**](ConfigurationApi.md#listregistryitemsv1configcomponentsregistryitemsget) | **GET** /v1/config/components/registry_items | List Registry Components
[**updateComponentV1ConfigComponentsCompIdPut**](ConfigurationApi.md#updatecomponentv1configcomponentscompidput) | **PUT** /v1/config/components/{comp_id} | Update Component
[**updateStepV1ConfigStepsStepIdPut**](ConfigurationApi.md#updatestepv1configstepsstepidput) | **PUT** /v1/config/steps/{step_id} | Update Step
[**updateWorkflowV1ConfigWorkflowsWfIdPut**](ConfigurationApi.md#updateworkflowv1configworkflowswfidput) | **PUT** /v1/config/workflows/{wf_id} | Update Workflow
[**validateFlowV1ConfigWorkflowsValidateFlowPost**](ConfigurationApi.md#validateflowv1configworkflowsvalidateflowpost) | **POST** /v1/config/workflows/validate-flow | Validate Flow


# **createComponentV1ConfigComponentsPost**
> TextComponentResponse createComponentV1ConfigComponentsPost(componentCreate)

Create Component

Creates a new configuration component.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final ComponentCreate componentCreate = ; // ComponentCreate | 

try {
    final response = api.createComponentV1ConfigComponentsPost(componentCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->createComponentV1ConfigComponentsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **componentCreate** | [**ComponentCreate**](ComponentCreate.md)|  | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createStepV1ConfigStepsPost**
> StepDefinition createStepV1ConfigStepsPost(stepDefinition)

Create Step

Creates a new step. Pydantic validator adapts legacy input to DB schema.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final StepDefinition stepDefinition = ; // StepDefinition | 

try {
    final response = api.createStepV1ConfigStepsPost(stepDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->createStepV1ConfigStepsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepDefinition** | [**StepDefinition**](StepDefinition.md)|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createWorkflowV1ConfigWorkflowsPost**
> WorkflowConfigDefinition createWorkflowV1ConfigWorkflowsPost(workflowConfigCreate)

Create Workflow

Create a new workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final WorkflowConfigCreate workflowConfigCreate = ; // WorkflowConfigCreate | 

try {
    final response = api.createWorkflowV1ConfigWorkflowsPost(workflowConfigCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->createWorkflowV1ConfigWorkflowsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowConfigCreate** | [**WorkflowConfigCreate**](WorkflowConfigCreate.md)|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteComponentV1ConfigComponentsCompIdDelete**
> ComponentDeleteResponse deleteComponentV1ConfigComponentsCompIdDelete(compId)

Delete Component

Deletes a component if it is not referenced by any existing steps OR executions.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String compId = compId_example; // String | 

try {
    final response = api.deleteComponentV1ConfigComponentsCompIdDelete(compId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->deleteComponentV1ConfigComponentsCompIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**|  | 

### Return type

[**ComponentDeleteResponse**](ComponentDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteStepV1ConfigStepsStepIdDelete**
> StepDeleteResponse deleteStepV1ConfigStepsStepIdDelete(stepId)

Delete Step

Deletes a step.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.deleteStepV1ConfigStepsStepIdDelete(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->deleteStepV1ConfigStepsStepIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepDeleteResponse**](StepDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteWorkflowV1ConfigWorkflowsWfIdDelete**
> ConfigWorkflowDeleteResponse deleteWorkflowV1ConfigWorkflowsWfIdDelete(wfId)

Delete Workflow

Delete a workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String wfId = wfId_example; // String | 

try {
    final response = api.deleteWorkflowV1ConfigWorkflowsWfIdDelete(wfId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->deleteWorkflowV1ConfigWorkflowsWfIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 

### Return type

[**ConfigWorkflowDeleteResponse**](ConfigWorkflowDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getComponentV1ConfigComponentsCompIdGet**
> TextComponentResponse getComponentV1ConfigComponentsCompIdGet(compId)

Get Component

Retrieves a single component by ID or Name.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String compId = compId_example; // String | Component ID or Name

try {
    final response = api.getComponentV1ConfigComponentsCompIdGet(compId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getComponentV1ConfigComponentsCompIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**| Component ID or Name | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getComponentsV1ConfigComponentsGet**
> List<TextComponentResponse> getComponentsV1ConfigComponentsGet(type, excludeType)

List Components

Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).  Args:     repo (RepositoryDep): Repository dependency.     type (str | None): Optional filter by component type.     exclude_type (list[str] | None): Optional types to exclude (defaults to agents/processors).  Returns:     list[ComponentResponse]: List of configuration components.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String type = type_example; // String | 
final List<String> excludeType = ; // List<String> | 

try {
    final response = api.getComponentsV1ConfigComponentsGet(type, excludeType);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getComponentsV1ConfigComponentsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | **String**|  | [optional] 
 **excludeType** | [**List&lt;String&gt;**](String.md)|  | [optional] 

### Return type

[**List&lt;TextComponentResponse&gt;**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getModelSchemaV1ConfigSchemasModelNameGet**
> SchemaResponse getModelSchemaV1ConfigSchemasModelNameGet(modelName)

Get Model JSON Schema

Returns the JSON Schema for a registered Pydantic model. citations: dynamic

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String modelName = modelName_example; // String | 

try {
    final response = api.getModelSchemaV1ConfigSchemasModelNameGet(modelName);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getModelSchemaV1ConfigSchemasModelNameGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **modelName** | **String**|  | 

### Return type

[**SchemaResponse**](SchemaResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSchemasV1ConfigSchemasGet**
> SchemaListResponse getSchemasV1ConfigSchemasGet()

List Schemas

Get all available JSON Schemas (Global Registry).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();

try {
    final response = api.getSchemasV1ConfigSchemasGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getSchemasV1ConfigSchemasGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**SchemaListResponse**](SchemaListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStepV1ConfigStepsStepIdGet**
> StepDefinition getStepV1ConfigStepsStepIdGet(stepId)

Get Step

Retrieves a single step by ID.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String stepId = stepId_example; // String | 

try {
    final response = api.getStepV1ConfigStepsStepIdGet(stepId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getStepV1ConfigStepsStepIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStepsV1ConfigStepsGet**
> List<StepDefinition> getStepsV1ConfigStepsGet()

List Steps

Retrieves all defined steps. Pydantic model handles adaptation automatically.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();

try {
    final response = api.getStepsV1ConfigStepsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getStepsV1ConfigStepsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;StepDefinition&gt;**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowV1ConfigWorkflowsWfIdGet**
> WorkflowConfigDefinition getWorkflowV1ConfigWorkflowsWfIdGet(wfId)

Get Workflow

Get a specific workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String wfId = wfId_example; // String | 

try {
    final response = api.getWorkflowV1ConfigWorkflowsWfIdGet(wfId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getWorkflowV1ConfigWorkflowsWfIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowsV1ConfigWorkflowsGet**
> List<WorkflowConfigDefinition> getWorkflowsV1ConfigWorkflowsGet()

List Workflows

List all workflows.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();

try {
    final response = api.getWorkflowsV1ConfigWorkflowsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->getWorkflowsV1ConfigWorkflowsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;WorkflowConfigDefinition&gt;**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listRegistryItemsV1ConfigComponentsRegistryItemsGet**
> List<RegistryComponentItem> listRegistryItemsV1ConfigComponentsRegistryItemsGet()

List Registry Components

Retrieves all system components directly from the Repository.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();

try {
    final response = api.listRegistryItemsV1ConfigComponentsRegistryItemsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->listRegistryItemsV1ConfigComponentsRegistryItemsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;RegistryComponentItem&gt;**](RegistryComponentItem.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateComponentV1ConfigComponentsCompIdPut**
> TextComponentResponse updateComponentV1ConfigComponentsCompIdPut(compId, componentUpdate)

Update Component

Updates an existing component's content and metadata.  Args:     comp_id (str): The ID of the component to update.     update (ComponentUpdate): The new data.     repo (RepositoryDep): Repository dependency.  Returns:     ComponentResponse: The updated component.  Raises:     HTTPException: If not found (404).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String compId = compId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateComponentV1ConfigComponentsCompIdPut(compId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->updateComponentV1ConfigComponentsCompIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

[**TextComponentResponse**](TextComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateStepV1ConfigStepsStepIdPut**
> StepDefinition updateStepV1ConfigStepsStepIdPut(stepId, stepDefinition)

Update Step

Updates an existing step.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String stepId = stepId_example; // String | 
final StepDefinition stepDefinition = ; // StepDefinition | 

try {
    final response = api.updateStepV1ConfigStepsStepIdPut(stepId, stepDefinition);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->updateStepV1ConfigStepsStepIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**|  | 
 **stepDefinition** | [**StepDefinition**](StepDefinition.md)|  | 

### Return type

[**StepDefinition**](StepDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWorkflowV1ConfigWorkflowsWfIdPut**
> WorkflowConfigDefinition updateWorkflowV1ConfigWorkflowsWfIdPut(wfId, workflowConfigUpdate)

Update Workflow

Update a workflow definition.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final String wfId = wfId_example; // String | 
final WorkflowConfigUpdate workflowConfigUpdate = ; // WorkflowConfigUpdate | 

try {
    final response = api.updateWorkflowV1ConfigWorkflowsWfIdPut(wfId, workflowConfigUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->updateWorkflowV1ConfigWorkflowsWfIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 
 **workflowConfigUpdate** | [**WorkflowConfigUpdate**](WorkflowConfigUpdate.md)|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validateFlowV1ConfigWorkflowsValidateFlowPost**
> ValidationReportResponse validateFlowV1ConfigWorkflowsValidateFlowPost(workflowConfigCreate)

Validate Flow

Dry run validation.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationApi();
final WorkflowConfigCreate workflowConfigCreate = ; // WorkflowConfigCreate | 

try {
    final response = api.validateFlowV1ConfigWorkflowsValidateFlowPost(workflowConfigCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationApi->validateFlowV1ConfigWorkflowsValidateFlowPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowConfigCreate** | [**WorkflowConfigCreate**](WorkflowConfigCreate.md)|  | 

### Return type

[**ValidationReportResponse**](ValidationReportResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

