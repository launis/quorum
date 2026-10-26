import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Primary runtime search query parameter keys bound dynamically by the backend.
const Set<String> _kRuntimeQueryKeys = <String>{
  'query',
  'q',
  'search_query',
  'search_term',
};

/// Resolved pairing of a gateway tool and its canonical namespaced alias.
class _ResolvedMcpToolEntry {
  final String namespacedAlias;
  final AllowedMcpTool tool;
  final Map<String, McpToolSchemaPropertyDto> configurableProperties;

  const _ResolvedMcpToolEntry({
    required this.namespacedAlias,
    required this.tool,
    required this.configurableProperties,
  });
}

/// Schema-driven configuration panel for pinning static MCP tool parameter overrides per step.
///
/// Dynamically inspects `AllowedMcpTool.inputSchema.properties` for each selected tool in
/// `allowedMcpTools` and renders type-appropriate controls (dropdowns for enums, switches
/// for booleans, numeric fields with min/max bounds for numbers/integers, and text inputs
/// for strings).
class McpToolParamsPanel extends StatelessWidget {
  final List<String> allowedMcpTools;
  final Map<String, Map<String, Object?>> mcpToolParams;
  final List<McpGateway> mcpGateways;
  final ValueChanged<Map<String, Map<String, Object?>>> onChanged;

  const McpToolParamsPanel({
    super.key,
    required this.allowedMcpTools,
    required this.mcpToolParams,
    required this.mcpGateways,
    required this.onChanged,
  });

  List<_ResolvedMcpToolEntry> _resolveSelectedTools() {
    if (allowedMcpTools.isEmpty || mcpGateways.isEmpty) {
      return const <_ResolvedMcpToolEntry>[];
    }

    final Map<String, AllowedMcpTool> aliasLookup = <String, AllowedMcpTool>{};
    for (final gateway in mcpGateways) {
      for (final tool in gateway.tools) {
        if (tool.enabled && tool.toolId.isNotEmpty) {
          final alias = '${gateway.slug}__${tool.toolId}';
          aliasLookup[alias] = tool;
        }
      }
    }

    final List<_ResolvedMcpToolEntry> entries = <_ResolvedMcpToolEntry>[];
    for (final alias in allowedMcpTools) {
      final tool = aliasLookup[alias];
      if (tool == null) {
        continue;
      }
      final Map<String, McpToolSchemaPropertyDto> configurable =
          <String, McpToolSchemaPropertyDto>{};
      for (final entry in tool.inputSchema.properties.entries) {
        if (!_kRuntimeQueryKeys.contains(entry.key)) {
          configurable[entry.key] = entry.value;
        }
      }
      if (configurable.isNotEmpty) {
        entries.add(
          _ResolvedMcpToolEntry(
            namespacedAlias: alias,
            tool: tool,
            configurableProperties: configurable,
          ),
        );
      }
    }
    return entries;
  }

  void _updateToolParam(
    String namespacedAlias,
    String paramKey,
    Object? value,
  ) {
    final Map<String, Map<String, Object?>> nextParams =
        <String, Map<String, Object?>>{
          for (final entry in mcpToolParams.entries)
            entry.key: Map<String, Object?>.from(entry.value),
        };

    final Map<String, Object?> toolMap = Map<String, Object?>.from(
      nextParams[namespacedAlias] ?? const <String, Object?>{},
    );

    if (value == null) {
      toolMap.remove(paramKey);
    } else {
      toolMap[paramKey] = value;
    }

    if (toolMap.isEmpty) {
      nextParams.remove(namespacedAlias);
    } else {
      nextParams[namespacedAlias] = toolMap;
    }

    onChanged(nextParams);
  }

  void _resetToolParams(String namespacedAlias) {
    final Map<String, Map<String, Object?>> nextParams =
        <String, Map<String, Object?>>{
          for (final entry in mcpToolParams.entries)
            if (entry.key != namespacedAlias)
              entry.key: Map<String, Object?>.from(entry.value),
        };
    onChanged(nextParams);
  }

  @override
  Widget build(BuildContext context) {
    final resolvedTools = _resolveSelectedTools();
    if (resolvedTools.isEmpty) {
      return const Column(children: <Widget>[]);
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final currentLocale = Localizations.localeOf(context).languageCode;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        AppSpacing.h16,
        Text(
          l10n.mcpToolParamsPanelTitle,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        AppSpacing.h12,
        ...resolvedTools.map((entry) {
          final toolName = entry.tool.name.get(currentLocale);
          if (toolName.trim().isEmpty) {
            throw AppException.validation(
              'Fail-Fast: MCP tool ${entry.namespacedAlias} lacks required translation for locale $currentLocale or en fallback.',
            );
          }
          final Map<String, Object?> currentOverrides =
              mcpToolParams[entry.namespacedAlias] ?? const <String, Object?>{};
          final bool hasOverrides = currentOverrides.isNotEmpty;

          return Card(
            elevation: AppSpacing.s2,
            margin: const EdgeInsets.only(bottom: AppSpacing.s16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSpacing.s12),
            ),
            child: Padding(
              padding: AppSpacing.p16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Row(
                    children: <Widget>[
                      Expanded(
                        child: Text(
                          toolName,
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      AppSpacing.w8,
                      Flexible(
                        child: Container(
                          padding: AppSpacing.p8,
                          decoration: BoxDecoration(
                            color: theme.colorScheme.primaryContainer,
                            borderRadius: BorderRadius.circular(AppSpacing.s8),
                          ),
                          child: Text(
                            entry.namespacedAlias,
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onPrimaryContainer,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      if (hasOverrides) ...<Widget>[
                        AppSpacing.w8,
                        TextButton.icon(
                          key: ValueKey<String>(
                            'mcp_param_reset_${entry.namespacedAlias}',
                          ),
                          style: TextButton.styleFrom(
                            enabledMouseCursor: SystemMouseCursors.click,
                          ),
                          onPressed: () =>
                              _resetToolParams(entry.namespacedAlias),
                          icon: const Icon(Icons.refresh),
                          label: Text(l10n.mcpToolParamsResetButton),
                        ),
                      ],
                    ],
                  ),
                  AppSpacing.h12,
                  ...entry.configurableProperties.entries.map((propEntry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
                      child: _buildPropertyControl(
                        context: context,
                        l10n: l10n,
                        namespacedAlias: entry.namespacedAlias,
                        propName: propEntry.key,
                        prop: propEntry.value,
                        currentValue: currentOverrides[propEntry.key],
                      ),
                    );
                  }),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildPropertyControl({
    required BuildContext context,
    required AppLocalizations l10n,
    required String namespacedAlias,
    required String propName,
    required McpToolSchemaPropertyDto prop,
    required Object? currentValue,
  }) {
    final enumValues = prop.enumValues;
    if (enumValues != null && enumValues.isNotEmpty) {
      final String? selectedEnum =
          currentValue is String && enumValues.contains(currentValue)
          ? currentValue
          : null;
      return DropdownButtonFormField<String?>(
        key: ValueKey<String>(
          'mcp_param_enum_${namespacedAlias}_${propName}_$selectedEnum',
        ),
        isExpanded: true,
        initialValue: selectedEnum,
        decoration: InputDecoration(
          labelText: propName,
          helperText: prop.description.isNotEmpty ? prop.description : null,
          border: const OutlineInputBorder(),
        ),
        items: <DropdownMenuItem<String?>>[
          DropdownMenuItem<String?>(
            value: null,
            child: Text(
              l10n.mcpToolParamsUseDefaultOption,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          ...enumValues.map(
            (val) => DropdownMenuItem<String?>(
              value: val,
              child: Text(val, overflow: TextOverflow.ellipsis),
            ),
          ),
        ],
        onChanged: (String? newValue) {
          _updateToolParam(namespacedAlias, propName, newValue);
        },
      );
    }

    if (prop.type == JsonSchemaPropertyType.boolean) {
      final bool effectiveBool = currentValue is bool
          ? currentValue
          : (prop.defaultValue is bool ? prop.defaultValue as bool : false);
      return SwitchListTile(
        key: ValueKey<String>('mcp_param_bool_${namespacedAlias}_$propName'),
        mouseCursor: SystemMouseCursors.click,
        contentPadding: EdgeInsets.zero,
        title: Text(propName, overflow: TextOverflow.ellipsis),
        subtitle: prop.description.isNotEmpty
            ? Text(prop.description, overflow: TextOverflow.ellipsis)
            : null,
        value: effectiveBool,
        onChanged: (bool newValue) {
          _updateToolParam(namespacedAlias, propName, newValue);
        },
      );
    }

    if (prop.type == JsonSchemaPropertyType.integer ||
        prop.type == JsonSchemaPropertyType.number) {
      final String? hintText = prop.defaultValue != null
          ? l10n.mcpToolParamsDefaultHint(prop.defaultValue.toString())
          : null;
      return _SchemaTextParamField(
        fieldKey: ValueKey<String>(
          'mcp_param_num_${namespacedAlias}_$propName',
        ),
        labelText: propName,
        helperText: prop.description.isNotEmpty ? prop.description : null,
        hintText: hintText,
        keyboardType: TextInputType.number,
        currentValue: currentValue,
        onChanged: (String rawText) {
          final trimmed = rawText.trim();
          if (trimmed.isEmpty) {
            _updateToolParam(namespacedAlias, propName, null);
            return;
          }
          final num? parsed = prop.type == JsonSchemaPropertyType.integer
              ? int.tryParse(trimmed)
              : double.tryParse(trimmed);
          if (parsed == null) {
            return;
          }
          if (prop.minimum != null && parsed < prop.minimum!) {
            return;
          }
          if (prop.maximum != null && parsed > prop.maximum!) {
            return;
          }
          _updateToolParam(namespacedAlias, propName, parsed);
        },
      );
    }

    final String? hintText = prop.defaultValue != null
        ? l10n.mcpToolParamsDefaultHint(prop.defaultValue.toString())
        : null;
    return _SchemaTextParamField(
      fieldKey: ValueKey<String>('mcp_param_str_${namespacedAlias}_$propName'),
      labelText: propName,
      helperText: prop.description.isNotEmpty ? prop.description : null,
      hintText: hintText,
      keyboardType: TextInputType.text,
      maxLength: prop.maxLength,
      currentValue: currentValue,
      onChanged: (String rawText) {
        final trimmed = rawText.trim();
        if (trimmed.isEmpty) {
          _updateToolParam(namespacedAlias, propName, null);
          return;
        }
        if (prop.minLength != null && trimmed.length < prop.minLength!) {
          return;
        }
        if (prop.maxLength != null && trimmed.length > prop.maxLength!) {
          return;
        }
        _updateToolParam(namespacedAlias, propName, trimmed);
      },
    );
  }
}

class _SchemaTextParamField extends StatefulWidget {
  final Key fieldKey;
  final String labelText;
  final String? helperText;
  final String? hintText;
  final TextInputType keyboardType;
  final int? maxLength;
  final Object? currentValue;
  final ValueChanged<String> onChanged;

  const _SchemaTextParamField({
    required this.fieldKey,
    required this.labelText,
    this.helperText,
    this.hintText,
    required this.keyboardType,
    this.maxLength,
    required this.currentValue,
    required this.onChanged,
  });

  @override
  State<_SchemaTextParamField> createState() => _SchemaTextParamFieldState();
}

class _SchemaTextParamFieldState extends State<_SchemaTextParamField> {
  late final TextEditingController _controller;
  late final FocusNode _focusNode;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.currentValue?.toString() ?? '',
    );
    _focusNode = FocusNode();
  }

  @override
  void didUpdateWidget(covariant _SchemaTextParamField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.currentValue == null && oldWidget.currentValue != null) {
      _controller.clear();
    } else if (widget.currentValue != null &&
        widget.currentValue != oldWidget.currentValue &&
        _controller.text.trim() != widget.currentValue.toString()) {
      _controller.text = widget.currentValue.toString();
    }
  }

  @override
  void dispose() {
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      key: widget.fieldKey,
      controller: _controller,
      focusNode: _focusNode,
      keyboardType: widget.keyboardType,
      maxLength: widget.maxLength,
      decoration: InputDecoration(
        labelText: widget.labelText,
        helperText: widget.helperText,
        hintText: widget.hintText,
        border: const OutlineInputBorder(),
      ),
      onChanged: widget.onChanged,
    );
  }
}
