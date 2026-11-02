import 'dart:async';

import 'package:client_app/core/state/mutation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _MutationHookHarness<T> extends HookWidget {
  final void Function(T data)? onSuccess;
  final void Function(Object error)? onError;
  final void Function(MutationState<T> mutationState) onBuild;

  const _MutationHookHarness({
    super.key,
    this.onSuccess,
    this.onError,
    required this.onBuild,
  });

  @override
  Widget build(BuildContext context) {
    final mutation = useMutation<T>(onSuccess: onSuccess, onError: onError);
    onBuild(mutation);
    return const SizedBox();
  }
}

void main() {
  group('MutationState Unit Tests', () {
    test(
      'Positive: accurately evaluates idle, loading, success, and error state getters',
      () {
        Future<String?> dummyMutate(Future<String> Function() action) async =>
            action();

        final idleState = MutationState<String>(
          state: null,
          mutate: dummyMutate,
        );
        expect(idleState.isIdle, isTrue);
        expect(idleState.isLoading, isFalse);
        expect(idleState.hasError, isFalse);
        expect(idleState.isSuccess, isFalse);
        expect(idleState.value, isNull);
        expect(idleState.error, isNull);
        expect(idleState.stackTrace, isNull);

        final loadingState = MutationState<String>(
          state: const AsyncValue.loading(),
          mutate: dummyMutate,
        );
        expect(loadingState.isIdle, isFalse);
        expect(loadingState.isLoading, isTrue);
        expect(loadingState.hasError, isFalse);
        expect(loadingState.isSuccess, isFalse);

        final successState = MutationState<String>(
          state: const AsyncValue.data('ok'),
          mutate: dummyMutate,
        );
        expect(successState.isIdle, isFalse);
        expect(successState.isLoading, isFalse);
        expect(successState.hasError, isFalse);
        expect(successState.isSuccess, isTrue);
        expect(successState.value, equals('ok'));

        final trace = StackTrace.current;
        final err = Exception('failed');
        final errorState = MutationState<String>(
          state: AsyncValue.error(err, trace),
          mutate: dummyMutate,
        );
        expect(errorState.isIdle, isFalse);
        expect(errorState.isLoading, isFalse);
        expect(errorState.hasError, isTrue);
        expect(errorState.isSuccess, isFalse);
        expect(errorState.error, same(err));
        expect(errorState.stackTrace, same(trace));
      },
    );
  });

  group('useMutation Hook Tests', () {
    testWidgets(
      'Positive: transitions Idle -> Loading -> Success and triggers onSuccess callback',
      (WidgetTester tester) async {
        late MutationState<int> capturedState;
        int? successValue;
        final completer = Completer<int>();

        await tester.pumpWidget(
          MaterialApp(
            home: _MutationHookHarness<int>(
              onSuccess: (val) => successValue = val,
              onBuild: (state) => capturedState = state,
            ),
          ),
        );

        expect(capturedState.isIdle, isTrue);

        final futureResult = capturedState.mutate(() => completer.future);
        await tester.pump();

        expect(capturedState.isLoading, isTrue);
        expect(capturedState.isSuccess, isFalse);

        completer.complete(42);
        final result = await futureResult;
        await tester.pump();

        expect(result, equals(42));
        expect(successValue, equals(42));
        expect(capturedState.isSuccess, isTrue);
        expect(capturedState.value, equals(42));
        expect(capturedState.hasError, isFalse);
      },
    );

    testWidgets(
      'Negative 1: captures Exception into AsyncError, calls onError, and returns null',
      (WidgetTester tester) async {
        late MutationState<String> capturedState;
        Object? capturedError;
        final expectedException = Exception('network timeout');

        await tester.pumpWidget(
          MaterialApp(
            home: _MutationHookHarness<String>(
              onError: (err) => capturedError = err,
              onBuild: (state) => capturedState = state,
            ),
          ),
        );

        final result = await capturedState.mutate(() async {
          throw expectedException;
        });
        await tester.pump();

        expect(result, isNull);
        expect(capturedError, same(expectedException));
        expect(capturedState.hasError, isTrue);
        expect(capturedState.isSuccess, isFalse);
        expect(capturedState.error, same(expectedException));
        expect(capturedState.stackTrace, isNotNull);
      },
    );

    testWidgets(
      'Negative 2 (Fail-Fast): rethrows programmer Error subclasses without swallowing into UI state',
      (WidgetTester tester) async {
        late MutationState<String> capturedState;
        Object? capturedErrorCallback;

        await tester.pumpWidget(
          MaterialApp(
            home: _MutationHookHarness<String>(
              onError: (err) => capturedErrorCallback = err,
              onBuild: (state) => capturedState = state,
            ),
          ),
        );

        await expectLater(
          () => capturedState.mutate(() async {
            throw StateError('Programmer invariant violation');
          }),
          throwsA(isA<StateError>()),
        );
        expect(capturedErrorCallback, isNull);
      },
    );

    testWidgets(
      'Regression: unmounting widget while mutation action is in-flight does not throw disposed ValueNotifier error on completion or error',
      (WidgetTester tester) async {
        late MutationState<void> capturedErrorState;
        var errorCallbackInvoked = false;
        final errorCompleter = Completer<void>();

        await tester.pumpWidget(
          MaterialApp(
            home: _MutationHookHarness<void>(
              onError: (_) => errorCallbackInvoked = true,
              onBuild: (state) => capturedErrorState = state,
            ),
          ),
        );

        final inFlightErrorFuture = capturedErrorState.mutate(
          () => errorCompleter.future,
        );
        await tester.pump();
        expect(capturedErrorState.isLoading, isTrue);

        // Simulate route transition unmounting the host widget while action is awaiting network response
        await tester.pumpWidget(const MaterialApp(home: SizedBox()));

        errorCompleter.completeError(
          Exception('HTTP 500 STORAGE_ACCESS_FAILED'),
        );
        await inFlightErrorFuture;
        await tester.pump();

        expect(errorCallbackInvoked, isFalse);
        expect(tester.takeException(), isNull);

        late MutationState<String> capturedSuccessState;
        var successCallbackInvoked = false;
        final successCompleter = Completer<String>();

        await tester.pumpWidget(
          MaterialApp(
            home: _MutationHookHarness<String>(
              onSuccess: (_) => successCallbackInvoked = true,
              onBuild: (state) => capturedSuccessState = state,
            ),
          ),
        );

        final inFlightSuccessFuture = capturedSuccessState.mutate(
          () => successCompleter.future,
        );
        await tester.pump();
        expect(capturedSuccessState.isLoading, isTrue);

        await tester.pumpWidget(const MaterialApp(home: SizedBox()));

        successCompleter.complete('ok_after_unmount');
        final successResult = await inFlightSuccessFuture;
        await tester.pump();

        expect(successResult, 'ok_after_unmount');
        expect(successCallbackInvoked, isFalse);
        expect(tester.takeException(), isNull);
      },
    );
  });

  group('MutationButton Widget Tests', () {
    testWidgets(
      'Positive: renders label/icon/child variants and invokes mutate when pressed',
      (WidgetTester tester) async {
        var actionCalled = false;
        final idleMutation = MutationState<String>(
          state: null,
          mutate: (action) async {
            actionCalled = true;
            return action();
          },
        );

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  MutationButton<String>(
                    mutation: idleMutation,
                    label: 'Save Plain',
                    action: () async => 'saved',
                  ),
                  MutationButton<String>(
                    mutation: idleMutation,
                    label: 'Save Icon',
                    icon: Icons.save,
                    action: () async => 'saved',
                  ),
                  MutationButton<String>(
                    mutation: idleMutation,
                    label: 'Ignored Label',
                    child: const KeyedSubtree(
                      key: ValueKey('custom_child'),
                      child: Icon(Icons.check),
                    ),
                    action: () async => 'saved',
                  ),
                ],
              ),
            ),
          ),
        );

        expect(find.text('Save Plain'), findsOneWidget);
        expect(find.text('Save Icon'), findsOneWidget);
        expect(find.byIcon(Icons.save), findsOneWidget);
        expect(find.byKey(const ValueKey('custom_child')), findsOneWidget);

        await tester.tap(find.text('Save Plain'));
        await tester.pump();
        expect(actionCalled, isTrue);
      },
    );

    testWidgets(
      'Boundary: disables FilledButton when loading or when action is null',
      (WidgetTester tester) async {
        var mutateCalled = false;
        final loadingMutation = MutationState<String>(
          state: const AsyncValue.loading(),
          mutate: (action) async {
            mutateCalled = true;
            return action();
          },
        );
        final idleMutation = MutationState<String>(
          state: null,
          mutate: (action) async {
            mutateCalled = true;
            return action();
          },
        );

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  MutationButton<String>(
                    mutation: loadingMutation,
                    label: 'Loading Action',
                    action: () async => 'done',
                  ),
                  MutationButton<String>(
                    mutation: idleMutation,
                    label: 'Null Action Plain',
                  ),
                  MutationButton<String>(
                    mutation: idleMutation,
                    label: 'Null Action Icon',
                    icon: Icons.lock,
                  ),
                ],
              ),
            ),
          ),
        );

        expect(find.byType(CircularProgressIndicator), findsOneWidget);
        expect(find.text('Loading Action'), findsNothing);

        await tester.tap(find.byType(CircularProgressIndicator));
        await tester.tap(find.text('Null Action Plain'));
        await tester.tap(find.text('Null Action Icon'));
        await tester.pump();

        expect(mutateCalled, isFalse);
      },
    );
  });
}
