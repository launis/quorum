//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'package:dio/dio.dart';
import 'package:backend_api/src/auth/api_key_auth.dart';
import 'package:backend_api/src/auth/basic_auth.dart';
import 'package:backend_api/src/auth/bearer_auth.dart';
import 'package:backend_api/src/auth/oauth.dart';
import 'package:backend_api/src/api/admin_api.dart';
import 'package:backend_api/src/api/agents_api.dart';
import 'package:backend_api/src/api/audit_api.dart';
import 'package:backend_api/src/api/authentication_users_api.dart';
import 'package:backend_api/src/api/builder_api.dart';
import 'package:backend_api/src/api/components_api.dart';
import 'package:backend_api/src/api/config_models_api.dart';
import 'package:backend_api/src/api/configuration_api.dart';
import 'package:backend_api/src/api/configuration_agents_api.dart';
import 'package:backend_api/src/api/configuration_dimensions_api.dart';
import 'package:backend_api/src/api/configuration_matrices_api.dart';
import 'package:backend_api/src/api/configuration_outputs_api.dart';
import 'package:backend_api/src/api/execution_v1_api.dart';
import 'package:backend_api/src/api/executions_api.dart';
import 'package:backend_api/src/api/global_settings_api.dart';
import 'package:backend_api/src/api/knowledge_api.dart';
import 'package:backend_api/src/api/llm_api.dart';
import 'package:backend_api/src/api/models_api.dart';
import 'package:backend_api/src/api/ontology_api.dart';
import 'package:backend_api/src/api/organizations_api.dart';
import 'package:backend_api/src/api/playground_api.dart';
import 'package:backend_api/src/api/steps_api.dart';
import 'package:backend_api/src/api/tools_api.dart';
import 'package:backend_api/src/api/usage_api.dart';
import 'package:backend_api/src/api/workflows_api.dart';

class BackendApi {
  static const String basePath = r'http://localhost';

  final Dio dio;
  BackendApi({
    Dio? dio,
    String? basePathOverride,
    List<Interceptor>? interceptors,
  }) : this.dio =
           dio ??
           Dio(
             BaseOptions(
               baseUrl: basePathOverride ?? basePath,
               connectTimeout: const Duration(milliseconds: 5000),
               receiveTimeout: const Duration(milliseconds: 3000),
             ),
           ) {
    if (interceptors == null) {
      this.dio.interceptors.addAll([
        OAuthInterceptor(),
        BasicAuthInterceptor(),
        BearerAuthInterceptor(),
        ApiKeyAuthInterceptor(),
      ]);
    } else {
      this.dio.interceptors.addAll(interceptors);
    }
  }

  void setOAuthToken(String name, String token) {
    if (this.dio.interceptors.any((i) => i is OAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is OAuthInterceptor)
                  as OAuthInterceptor)
              .tokens[name] =
          token;
    }
  }

  void setBearerAuth(String name, String token) {
    if (this.dio.interceptors.any((i) => i is BearerAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BearerAuthInterceptor)
                  as BearerAuthInterceptor)
              .tokens[name] =
          token;
    }
  }

  void setBasicAuth(String name, String username, String password) {
    if (this.dio.interceptors.any((i) => i is BasicAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BasicAuthInterceptor)
              as BasicAuthInterceptor)
          .authInfo[name] = BasicAuthInfo(
        username,
        password,
      );
    }
  }

  void setApiKey(String name, String apiKey) {
    if (this.dio.interceptors.any((i) => i is ApiKeyAuthInterceptor)) {
      (this.dio.interceptors.firstWhere(
                    (element) => element is ApiKeyAuthInterceptor,
                  )
                  as ApiKeyAuthInterceptor)
              .apiKeys[name] =
          apiKey;
    }
  }

  /// Get AdminApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AdminApi getAdminApi() {
    return AdminApi(dio);
  }

  /// Get AgentsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AgentsApi getAgentsApi() {
    return AgentsApi(dio);
  }

  /// Get AuditApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AuditApi getAuditApi() {
    return AuditApi(dio);
  }

  /// Get AuthenticationUsersApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AuthenticationUsersApi getAuthenticationUsersApi() {
    return AuthenticationUsersApi(dio);
  }

  /// Get BuilderApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  BuilderApi getBuilderApi() {
    return BuilderApi(dio);
  }

  /// Get ComponentsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ComponentsApi getComponentsApi() {
    return ComponentsApi(dio);
  }

  /// Get ConfigModelsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigModelsApi getConfigModelsApi() {
    return ConfigModelsApi(dio);
  }

  /// Get ConfigurationApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigurationApi getConfigurationApi() {
    return ConfigurationApi(dio);
  }

  /// Get ConfigurationAgentsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigurationAgentsApi getConfigurationAgentsApi() {
    return ConfigurationAgentsApi(dio);
  }

  /// Get ConfigurationDimensionsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigurationDimensionsApi getConfigurationDimensionsApi() {
    return ConfigurationDimensionsApi(dio);
  }

  /// Get ConfigurationMatricesApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigurationMatricesApi getConfigurationMatricesApi() {
    return ConfigurationMatricesApi(dio);
  }

  /// Get ConfigurationOutputsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConfigurationOutputsApi getConfigurationOutputsApi() {
    return ConfigurationOutputsApi(dio);
  }

  /// Get ExecutionV1Api instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ExecutionV1Api getExecutionV1Api() {
    return ExecutionV1Api(dio);
  }

  /// Get ExecutionsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ExecutionsApi getExecutionsApi() {
    return ExecutionsApi(dio);
  }

  /// Get GlobalSettingsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  GlobalSettingsApi getGlobalSettingsApi() {
    return GlobalSettingsApi(dio);
  }

  /// Get KnowledgeApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  KnowledgeApi getKnowledgeApi() {
    return KnowledgeApi(dio);
  }

  /// Get LLMApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  LLMApi getLLMApi() {
    return LLMApi(dio);
  }

  /// Get ModelsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ModelsApi getModelsApi() {
    return ModelsApi(dio);
  }

  /// Get OntologyApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  OntologyApi getOntologyApi() {
    return OntologyApi(dio);
  }

  /// Get OrganizationsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  OrganizationsApi getOrganizationsApi() {
    return OrganizationsApi(dio);
  }

  /// Get PlaygroundApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  PlaygroundApi getPlaygroundApi() {
    return PlaygroundApi(dio);
  }

  /// Get StepsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  StepsApi getStepsApi() {
    return StepsApi(dio);
  }

  /// Get ToolsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ToolsApi getToolsApi() {
    return ToolsApi(dio);
  }

  /// Get UsageApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  UsageApi getUsageApi() {
    return UsageApi(dio);
  }

  /// Get WorkflowsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  WorkflowsApi getWorkflowsApi() {
    return WorkflowsApi(dio);
  }
}
