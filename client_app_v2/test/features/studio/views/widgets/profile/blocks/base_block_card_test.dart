import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

void main() {
  testWidgets(
    'BaseBlockCard renders title, subtitle, icon, body, dragHandle, and handles toggle when included',
    (WidgetTester tester) async {
      bool toggled = true;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BaseBlockCard(
              blockType: TargetBlockType.metadataBlock,
              title: 'Metadata Block',
              subtitle: 'Includes metadata details',
              icon: Icons.info,
              isIncluded: true,
              onToggle: (val) {
                toggled = val;
              },
              body: const Text('Child Body Content'),
              dragHandle: const Icon(Icons.drag_handle),
            ),
          ),
        ),
      );

      expect(find.text('Metadata Block'), findsOneWidget);
      expect(find.text('Includes metadata details'), findsOneWidget);
      expect(find.text('Child Body Content'), findsOneWidget);
      expect(find.byType(Divider), findsOneWidget);
      expect(find.byIcon(Icons.drag_handle), findsOneWidget);
      expect(find.byType(Switch), findsOneWidget);

      await tester.tap(find.byType(Switch));
      await tester.pump();

      expect(toggled, isFalse);
    },
  );

  testWidgets(
    'BaseBlockCard suppresses body, divider, and empty subtitle when excluded (negative/boundary)',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BaseBlockCard(
              blockType: TargetBlockType.metadataBlock,
              title: 'Excluded Block',
              subtitle: '',
              icon: Icons.block,
              isIncluded: false,
              onToggle: (_) {},
              body: const Text('Hidden Body Content'),
            ),
          ),
        ),
      );

      expect(find.text('Excluded Block'), findsOneWidget);
      expect(find.text('Hidden Body Content'), findsNothing);
      expect(find.byType(Divider), findsNothing);
      expect(find.byType(Text), findsOneWidget);
    },
  );

  testWidgets(
    'BaseBlockCard contains horizontal overflow with extreme long strings in narrow layout (boundary)',
    (WidgetTester tester) async {
      final longTitle = 'A' * 300;
      final longSubtitle = 'B' * 300;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 220,
              child: BaseBlockCard(
                blockType: TargetBlockType.metadataBlock,
                title: longTitle,
                subtitle: longSubtitle,
                icon: Icons.summarize,
                isIncluded: true,
                onToggle: (_) {},
                dragHandle: const Icon(Icons.drag_indicator),
              ),
            ),
          ),
        ),
      );

      expect(tester.takeException(), isNull);
      expect(find.text(longTitle), findsOneWidget);
      expect(find.text(longSubtitle), findsOneWidget);
    },
  );
}
