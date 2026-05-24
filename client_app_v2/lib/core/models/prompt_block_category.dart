import 'package:flutter/widgets.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:json_annotation/json_annotation.dart';

enum PromptBlockCategory {
  @JsonValue('matrix')
  matrix,
  @JsonValue('agent_role')
  agentRole,
  @JsonValue('task_definition')
  taskDefinition,
  @JsonValue('system_rule')
  systemRule,
  @JsonValue('protocol')
  protocol,
  @JsonValue('runtime_variables')
  runtimeVariables;

  String get id {
    switch (this) {
      case PromptBlockCategory.matrix:
        return 'matrix';
      case PromptBlockCategory.agentRole:
        return 'agent_role';
      case PromptBlockCategory.taskDefinition:
        return 'task_definition';
      case PromptBlockCategory.systemRule:
        return 'system_rule';
      case PromptBlockCategory.protocol:
        return 'protocol';
      case PromptBlockCategory.runtimeVariables:
        return 'runtime_variables';
    }
  }

  static PromptBlockCategory fromId(String value) {
    return PromptBlockCategory.values.firstWhere(
      (e) => e.id == value,
      orElse: () =>
          throw AppException.validation('Unknown PromptBlockCategory: $value'),
    );
  }
}

extension PromptBlockCategoryL10n on PromptBlockCategory {
  String displayName(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    switch (this) {
      case PromptBlockCategory.matrix:
        return l10n.categoryMatrix;
      case PromptBlockCategory.agentRole:
        return l10n.categoryAgentRole;
      case PromptBlockCategory.taskDefinition:
        return l10n.categoryTaskDefinition;
      case PromptBlockCategory.systemRule:
        return l10n.categorySystemRule;
      case PromptBlockCategory.protocol:
        return l10n.categoryProtocol;
      case PromptBlockCategory.runtimeVariables:
        return l10n.categoryRuntimeVariables;
    }
  }
}
