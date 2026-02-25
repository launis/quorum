import 'package:backend_api/src/model/ad_hoc_test_request.dart';
import 'package:backend_api/src/model/ad_hoc_test_response.dart';
import 'package:backend_api/src/model/admin_task_response.dart';
import 'package:backend_api/src/model/agent_component_response.dart';
import 'package:backend_api/src/model/agent_definition.dart';
import 'package:backend_api/src/model/agent_metadata_dto.dart';
import 'package:backend_api/src/model/agent_run_response.dart';
import 'package:backend_api/src/model/async_job_response.dart';
import 'package:backend_api/src/model/audit_event.dart';
import 'package:backend_api/src/model/banned_phrase_request.dart';
import 'package:backend_api/src/model/banned_phrase_response.dart';
import 'package:backend_api/src/model/batch_completion_request.dart';
import 'package:backend_api/src/model/batch_llm_response.dart';
import 'package:backend_api/src/model/body_citation_lookup_tools_citation_lookup_post.dart';
import 'package:backend_api/src/model/body_clone_step_builder_steps_clone_post.dart';
import 'package:backend_api/src/model/body_run_agent_agents_agent_name_run_post.dart';
import 'package:backend_api/src/model/body_web_scrape_tools_web_scrape_post.dart';
import 'package:backend_api/src/model/builder_workflow_create_request.dart';
import 'package:backend_api/src/model/builder_workflow_delete_response.dart';
import 'package:backend_api/src/model/chain_preview_response.dart';
import 'package:backend_api/src/model/citation_lookup_response.dart';
import 'package:backend_api/src/model/compilation_response.dart';
import 'package:backend_api/src/model/compile_request.dart';
import 'package:backend_api/src/model/completion_request.dart';
import 'package:backend_api/src/model/component_create.dart';
import 'package:backend_api/src/model/component_delete_response.dart';
import 'package:backend_api/src/model/component_schema_response.dart';
import 'package:backend_api/src/model/component_update.dart';
import 'package:backend_api/src/model/concept_extraction_response.dart';
import 'package:backend_api/src/model/config_component_response.dart';
import 'package:backend_api/src/model/config_workflow_delete_response.dart';
import 'package:backend_api/src/model/copy_workflow_request.dart';
import 'package:backend_api/src/model/custom_step_create_request.dart';
import 'package:backend_api/src/model/dimension_definition.dart';
import 'package:backend_api/src/model/dimension_delete_response.dart';
import 'package:backend_api/src/model/execution_cancel_response.dart';
import 'package:backend_api/src/model/execution_delete_response.dart';
import 'package:backend_api/src/model/execution_raw_response.dart';
import 'package:backend_api/src/model/execution_response.dart';
import 'package:backend_api/src/model/fusion_rule_dto.dart';
import 'package:backend_api/src/model/generate_phrases_request.dart';
import 'package:backend_api/src/model/generated_id_response.dart';
import 'package:backend_api/src/model/generated_phrases_response.dart';
import 'package:backend_api/src/model/generic_action_response.dart';
import 'package:backend_api/src/model/http_validation_error.dart';
import 'package:backend_api/src/model/impersonation_request.dart';
import 'package:backend_api/src/model/impersonation_response.dart';
import 'package:backend_api/src/model/ingest_request.dart';
import 'package:backend_api/src/model/knowledge_ingest_response.dart';
import 'package:backend_api/src/model/knowledge_job_status_response.dart';
import 'package:backend_api/src/model/knowledge_reset_response.dart';
import 'package:backend_api/src/model/knowledge_status_response.dart';
import 'package:backend_api/src/model/llm_provider_config.dart';
import 'package:backend_api/src/model/llm_response.dart';
import 'package:backend_api/src/model/location_inner.dart';
import 'package:backend_api/src/model/login_response.dart';
import 'package:backend_api/src/model/matrix_component_response.dart';
import 'package:backend_api/src/model/matrix_content_dto.dart';
import 'package:backend_api/src/model/model_options_response.dart';
import 'package:backend_api/src/model/model_registry_response.dart';
import 'package:backend_api/src/model/model_registry_update.dart';
import 'package:backend_api/src/model/model_registry_update_response.dart';
import 'package:backend_api/src/model/organization.dart';
import 'package:backend_api/src/model/organization_create.dart';
import 'package:backend_api/src/model/organization_create_request.dart';
import 'package:backend_api/src/model/organization_response.dart';
import 'package:backend_api/src/model/organization_update.dart';
import 'package:backend_api/src/model/organization_usage_response.dart';
import 'package:backend_api/src/model/organization_user_create.dart';
import 'package:backend_api/src/model/pdf_cancel_response.dart';
import 'package:backend_api/src/model/pdf_download_check_response.dart';
import 'package:backend_api/src/model/pdf_queued_response.dart';
import 'package:backend_api/src/model/percent.dart';
import 'package:backend_api/src/model/playground_request.dart';
import 'package:backend_api/src/model/playground_response.dart';
import 'package:backend_api/src/model/problem_detail.dart';
import 'package:backend_api/src/model/provider_list_response.dart';
import 'package:backend_api/src/model/queue_stats.dart';
import 'package:backend_api/src/model/registry_component_item.dart';
import 'package:backend_api/src/model/report_view.dart';
import 'package:backend_api/src/model/response_download_execution_pdf_executions_execution_id_pdf_download_get.dart';
import 'package:backend_api/src/model/schema_info.dart';
import 'package:backend_api/src/model/schema_list_response.dart';
import 'package:backend_api/src/model/schema_response.dart';
import 'package:backend_api/src/model/seed_data_response.dart';
import 'package:backend_api/src/model/self_test_response.dart';
import 'package:backend_api/src/model/step_dto.dart';
import 'package:backend_api/src/model/step_definition.dart';
import 'package:backend_api/src/model/step_delete_response.dart';
import 'package:backend_api/src/model/step_preview_response.dart';
import 'package:backend_api/src/model/step_update_request.dart';
import 'package:backend_api/src/model/steps.dart';
import 'package:backend_api/src/model/system_notification.dart';
import 'package:backend_api/src/model/system_settings.dart';
import 'package:backend_api/src/model/task_status_response.dart';
import 'package:backend_api/src/model/text_component_response.dart';
import 'package:backend_api/src/model/text_extraction_response.dart';
import 'package:backend_api/src/model/token_payload.dart';
import 'package:backend_api/src/model/token_usage.dart';
import 'package:backend_api/src/model/ui_section.dart';
import 'package:backend_api/src/model/update_role_request.dart';
import 'package:backend_api/src/model/usage_report.dart';
import 'package:backend_api/src/model/user.dart';
import 'package:backend_api/src/model/user_admin_view.dart';
import 'package:backend_api/src/model/user_create.dart';
import 'package:backend_api/src/model/user_delete_response.dart';
import 'package:backend_api/src/model/user_update.dart';
import 'package:backend_api/src/model/validation_error.dart';
import 'package:backend_api/src/model/validation_report_response.dart';
import 'package:backend_api/src/model/validation_request.dart';
import 'package:backend_api/src/model/validation_response.dart';
import 'package:backend_api/src/model/web_scrape_response.dart';
import 'package:backend_api/src/model/workflow_config_create.dart';
import 'package:backend_api/src/model/workflow_config_definition.dart';
import 'package:backend_api/src/model/workflow_config_update.dart';
import 'package:backend_api/src/model/workflow_response.dart';
import 'package:backend_api/src/model/workflow_step.dart';
import 'package:backend_api/src/model/workflow_template.dart';
import 'package:backend_api/src/model/workflow_update_request.dart';
import 'package:backend_api/src/model/xai_flat_report_dto.dart';

final _regList = RegExp(r'^List<(.*)>$');
final _regSet = RegExp(r'^Set<(.*)>$');
final _regMap = RegExp(r'^Map<String,(.*)>$');

  ReturnType deserialize<ReturnType, BaseType>(dynamic value, String targetType, {bool growable= true}) {
      switch (targetType) {
        case 'String':
          return '$value' as ReturnType;
        case 'int':
          return (value is int ? value : int.parse('$value')) as ReturnType;
        case 'bool':
          if (value is bool) {
            return value as ReturnType;
          }
          final valueString = '$value'.toLowerCase();
          return (valueString == 'true' || valueString == '1') as ReturnType;
        case 'double':
          return (value is double ? value : double.parse('$value')) as ReturnType;
        case 'AdHocTestRequest':
          return AdHocTestRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AdHocTestResponse':
          return AdHocTestResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AdminTaskResponse':
          return AdminTaskResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AgentComponentResponse':
          return AgentComponentResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AgentDefinition':
          return AgentDefinition.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AgentMetadataDTO':
          return AgentMetadataDTO.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AgentRunResponse':
          return AgentRunResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AsyncJobResponse':
          return AsyncJobResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'AuditEvent':
          return AuditEvent.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BannedPhraseRequest':
          return BannedPhraseRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BannedPhraseResponse':
          return BannedPhraseResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BatchCompletionRequest':
          return BatchCompletionRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BatchLLMResponse':
          return BatchLLMResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BodyCitationLookupToolsCitationLookupPost':
          return BodyCitationLookupToolsCitationLookupPost.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BodyCloneStepBuilderStepsClonePost':
          return BodyCloneStepBuilderStepsClonePost.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BodyRunAgentAgentsAgentNameRunPost':
          return BodyRunAgentAgentsAgentNameRunPost.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BodyWebScrapeToolsWebScrapePost':
          return BodyWebScrapeToolsWebScrapePost.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BuilderWorkflowCreateRequest':
          return BuilderWorkflowCreateRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'BuilderWorkflowDeleteResponse':
          return BuilderWorkflowDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ChainPreviewResponse':
          return ChainPreviewResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CitationLookupResponse':
          return CitationLookupResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CompilationResponse':
          return CompilationResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CompileRequest':
          return CompileRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CompletionRequest':
          return CompletionRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ComponentCreate':
          return ComponentCreate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ComponentDeleteResponse':
          return ComponentDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ComponentSchemaResponse':
          return ComponentSchemaResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ComponentUpdate':
          return ComponentUpdate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ConceptExtractionResponse':
          return ConceptExtractionResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ConfigComponentResponse':
          return ConfigComponentResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ConfigWorkflowDeleteResponse':
          return ConfigWorkflowDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CopyWorkflowRequest':
          return CopyWorkflowRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'CustomStepCreateRequest':
          return CustomStepCreateRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'DimensionDefinition':
          return DimensionDefinition.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'DimensionDeleteResponse':
          return DimensionDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ExecutionCancelResponse':
          return ExecutionCancelResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ExecutionDeleteResponse':
          return ExecutionDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ExecutionRawResponse':
          return ExecutionRawResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ExecutionResponse':
          return ExecutionResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'FusionRuleDTO':
          return FusionRuleDTO.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'GeneratePhrasesRequest':
          return GeneratePhrasesRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'GeneratedIdResponse':
          return GeneratedIdResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'GeneratedPhrasesResponse':
          return GeneratedPhrasesResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'GenericActionResponse':
          return GenericActionResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'HTTPValidationError':
          return HTTPValidationError.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ImpersonationRequest':
          return ImpersonationRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ImpersonationResponse':
          return ImpersonationResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'IngestRequest':
          return IngestRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'KnowledgeIngestResponse':
          return KnowledgeIngestResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'KnowledgeJobStatusResponse':
          return KnowledgeJobStatusResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'KnowledgeResetResponse':
          return KnowledgeResetResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'KnowledgeStatusResponse':
          return KnowledgeStatusResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'LLMProviderConfig':
          return LLMProviderConfig.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'LLMResponse':
          return LLMResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'LocationInner':
          return LocationInner.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'LoginResponse':
          return LoginResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'MatrixComponentResponse':
          return MatrixComponentResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'MatrixContentDTO':
          return MatrixContentDTO.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ModelOptionsResponse':
          return ModelOptionsResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ModelRegistryResponse':
          return ModelRegistryResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ModelRegistryUpdate':
          return ModelRegistryUpdate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ModelRegistryUpdateResponse':
          return ModelRegistryUpdateResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'Organization':
          return Organization.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationCreate':
          return OrganizationCreate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationCreateRequest':
          return OrganizationCreateRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationResponse':
          return OrganizationResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationUpdate':
          return OrganizationUpdate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationUsageResponse':
          return OrganizationUsageResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'OrganizationUserCreate':
          return OrganizationUserCreate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'PDFCancelResponse':
          return PDFCancelResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'PDFDownloadCheckResponse':
          return PDFDownloadCheckResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'PDFQueuedResponse':
          return PDFQueuedResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'Percent':
          return Percent.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'PlaygroundRequest':
          return PlaygroundRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'PlaygroundResponse':
          return PlaygroundResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ProblemDetail':
          return ProblemDetail.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ProviderListResponse':
          return ProviderListResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'QueueStats':
          return QueueStats.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'RegistryComponentItem':
          return RegistryComponentItem.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ReportView':
          return ReportView.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet':
          return ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SchemaInfo':
          return SchemaInfo.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SchemaListResponse':
          return SchemaListResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SchemaResponse':
          return SchemaResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SectionType':
          
          
        case 'SeedDataResponse':
          return SeedDataResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SelfTestResponse':
          return SelfTestResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'StepDTO':
          return StepDTO.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'StepDefinition':
          return StepDefinition.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'StepDeleteResponse':
          return StepDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'StepPreviewResponse':
          return StepPreviewResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'StepUpdateRequest':
          return StepUpdateRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'Steps':
          return Steps.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SubscriptionStatus':
          
          
        case 'SystemNotification':
          return SystemNotification.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'SystemSettings':
          return SystemSettings.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'TaskStatusResponse':
          return TaskStatusResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'TextComponentResponse':
          return TextComponentResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'TextExtractionResponse':
          return TextExtractionResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'TokenPayload':
          return TokenPayload.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'TokenUsage':
          return TokenUsage.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UiSection':
          return UiSection.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UpdateRoleRequest':
          return UpdateRoleRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UsageReport':
          return UsageReport.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'User':
          return User.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UserAdminView':
          return UserAdminView.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UserCreate':
          return UserCreate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UserDeleteResponse':
          return UserDeleteResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'UserRole':
          
          
        case 'UserUpdate':
          return UserUpdate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ValidationError':
          return ValidationError.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ValidationReportResponse':
          return ValidationReportResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ValidationRequest':
          return ValidationRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'ValidationResponse':
          return ValidationResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WebScrapeResponse':
          return WebScrapeResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowConfigCreate':
          return WorkflowConfigCreate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowConfigDefinition':
          return WorkflowConfigDefinition.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowConfigUpdate':
          return WorkflowConfigUpdate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowResponse':
          return WorkflowResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowStep':
          return WorkflowStep.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowTemplate':
          return WorkflowTemplate.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'WorkflowUpdateRequest':
          return WorkflowUpdateRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
        case 'XAIFlatReportDTO':
          return XAIFlatReportDTO.fromJson(value as Map<String, dynamic>) as ReturnType;
        default:
          RegExpMatch? match;

          if (value is List && (match = _regList.firstMatch(targetType)) != null) {
            targetType = match![1]!; // ignore: parameter_assignments
            return value
              .map<BaseType>((dynamic v) => deserialize<BaseType, BaseType>(v, targetType, growable: growable))
              .toList(growable: growable) as ReturnType;
          }
          if (value is Set && (match = _regSet.firstMatch(targetType)) != null) {
            targetType = match![1]!; // ignore: parameter_assignments
            return value
              .map<BaseType>((dynamic v) => deserialize<BaseType, BaseType>(v, targetType, growable: growable))
              .toSet() as ReturnType;
          }
          if (value is Map && (match = _regMap.firstMatch(targetType)) != null) {
            targetType = match![1]!.trim(); // ignore: parameter_assignments
            return Map<String, BaseType>.fromIterables(
              value.keys as Iterable<String>,
              value.values.map((dynamic v) => deserialize<BaseType, BaseType>(v, targetType, growable: growable)),
            ) as ReturnType;
          }
          break;
    }
    throw Exception('Cannot deserialize');
  }