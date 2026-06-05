import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// This widget reproduces the exact StateError caused by conditionally executing
/// a hook based on a state transition, violating Flutter Hooks deterministic ordering.
class BadHookWidget extends HookWidget {
  final bool simulateDataLoaded;

  const BadHookWidget({Key? key, required this.simulateDataLoaded})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    final controller = useTextEditingController(text: 'test');

    // THE BUG: Conditionally executing a hook based on state
    final value = simulateDataLoaded
        ? 'data_loaded'
        : useValueListenable(controller).text;

    // A subsequent hook to trigger the mismatch
    useMemoized(() => print('Memoized hook executed'));

    return Text(value);
  }
}

void main() {
  testWidgets(
    'RCA: Conditional hook execution causes StateError (Type mismatch between hooks)',
    (WidgetTester tester) async {
      // Frame 1: loading state (simulateDataLoaded = false)
      // Sequence: useTextEditingController -> useValueListenable -> useMemoized
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: BadHookWidget(simulateDataLoaded: false)),
        ),
      );

      // Frame 2: data state (simulateDataLoaded = true)
      // Sequence: useTextEditingController -> useMemoized
      // EXPECTED: StateError due to skipping useValueListenable
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: BadHookWidget(simulateDataLoaded: true)),
        ),
      );
    },
  );
}
