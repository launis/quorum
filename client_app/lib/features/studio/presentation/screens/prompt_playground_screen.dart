import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/code_editor_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'prompt_playground_screen.g.dart';

/// **Playground State**
class PlaygroundState {
  final String promptTemplate;
  final Map<String, String> variables;
  final String output;
  final bool isLoading;

  PlaygroundState({
    required this.promptTemplate,
    required this.variables,
    this.output = '',
    this.isLoading = false,
  });

  PlaygroundState copyWith({
    String? promptTemplate,
    Map<String, String>? variables,
    String? output,
    bool? isLoading,
  }) {
    return PlaygroundState(
      promptTemplate: promptTemplate ?? this.promptTemplate,
      variables: variables ?? this.variables,
      output: output ?? this.output,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

/// **Playground Controller**
@riverpod
class PlaygroundController extends _$PlaygroundController {
  @override
  PlaygroundState build() {
    return PlaygroundState(
      promptTemplate: 'Write a {{tone}} story about {{topic}}.',
      variables: {'tone': '', 'topic': ''},
    );
  }

  void updateTemplate(String template) {
    if (state.isLoading) return;

    // Extract variables: {{variable}}
    final regex = RegExp(r'\{\{(.*?)\}\}');
    final matches = regex.allMatches(template);
    final newKeys =
        matches
            .map((m) => m.group(1)?.trim() ?? '')
            .where((k) => k.isNotEmpty)
            .toSet();

    // Preserve existing values for keys that still exist
    final newVariables = <String, String>{};
    for (final key in newKeys) {
      newVariables[key] = state.variables[key] ?? '';
    }

    state = state.copyWith(promptTemplate: template, variables: newVariables);
  }

  void updateVariable(String key, String value) {
    final vars = Map<String, String>.from(state.variables);
    vars[key] = value;
    state = state.copyWith(variables: vars);
  }

  Future<void> runPrompt() async {
    state = state.copyWith(isLoading: true, output: '');

    try {
      final api = ref.read(apiClientProvider);

      // Match backend expectation:
      // class PlaygroundRequest(BaseModel):
      //    system_instruction: str
      //    user_message: str
      //    variables: Dict[str, str]

      // For this simple playground, we treat the template as system_instruction
      // and maybe empty user_message, or we could split UI?
      // The prompt implies just "promptTemplate". Let's assume template goes to system_instruction.

      final response = await api.post(
        '/builder/playground/run', // /api/v1 prefix added by client
        data: {
          'system_instruction': state.promptTemplate,
          'user_message': '', // Optional for now
          'variables': state.variables,
          'model_params': {},
        },
      );

      // Backend returns raw string response (based on my python impl)
      // or JSON? My python implementation returned `response` from LLMClient.
      // If LLMClient returns string, Fastapi returns string (JSON encoded "string").
      // Verify: `return response` in python -> `response.data` in Dio is user string.

      final result = response.data.toString();

      state = state.copyWith(isLoading: false, output: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, output: 'Error: $e');
    }
  }
}

/// **Prompt Playground Screen**
class PromptPlaygroundScreen extends ConsumerWidget {
  const PromptPlaygroundScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(playgroundControllerProvider);
    final controller = ref.read(playgroundControllerProvider.notifier);

    final isWide = MediaQuery.of(context).size.width > 800;

    // Inputs Column
    final inputs = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Prompt Template', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        CodeEditorField(
          label: '', // Label handled by title above
          initialValue: state.promptTemplate,
          onChanged: controller.updateTemplate,
        ),
        const SizedBox(height: 16),
        Text('Variables', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        if (state.variables.isEmpty)
          const Text(
            'No variables detected in template (use {{name}}).',
            style: TextStyle(color: Colors.grey),
          ),
        ...state.variables.entries.map((entry) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: TextFormField(
              initialValue: entry.value,
              decoration: InputDecoration(
                labelText: entry.key,
                border: const OutlineInputBorder(),
                filled: true,
              ),
              onChanged: (val) => controller.updateVariable(entry.key, val),
            ),
          );
        }),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: state.isLoading ? null : controller.runPrompt,
            icon:
                state.isLoading
                    ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                    : const Icon(Icons.play_arrow),
            label: Text(state.isLoading ? 'Running...' : 'Run Prompt'),
          ),
        ),
      ],
    );

    // Output Column
    final output = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Output', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Expanded(
          child: CodeEditorField(
            label: '',
            initialValue: state.output,
            onChanged:
                (
                  _,
                ) {}, // Read-only effectively (user can edit buffer but it resets on run)
            // Actually, CodeEditorField accepts onChanged. To make read-only we'd need to disable it.
            // For now, it's just a display view.
          ),
        ),
      ],
    );

    return Scaffold(
      appBar: AppBar(title: const Text('Prompt Playground')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child:
            isWide
                ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: SingleChildScrollView(child: inputs)),
                    const SizedBox(width: 24),
                    const VerticalDivider(width: 1),
                    const SizedBox(width: 24),
                    Expanded(child: output),
                  ],
                )
                : Column(
                  children: [
                    Expanded(child: SingleChildScrollView(child: inputs)),
                    const Divider(height: 32),
                    Expanded(child: output),
                  ],
                ),
      ),
    );
  }
}
