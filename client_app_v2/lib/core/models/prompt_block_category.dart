enum PromptBlockCategory {
  matrix('Evaluation Matrix'),
  agentRole('Agent Role Persona'),
  taskDefinition('Task Definition'),
  systemRule('System Rule / Heuristic'),
  protocol('Execution Protocol');

  final String displayName;
  const PromptBlockCategory(this.displayName);

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
    }
  }

  static PromptBlockCategory fromId(String value) {
    return PromptBlockCategory.values.firstWhere(
      (e) => e.id == value,
      orElse: () => PromptBlockCategory.systemRule,
    );
  }
}
