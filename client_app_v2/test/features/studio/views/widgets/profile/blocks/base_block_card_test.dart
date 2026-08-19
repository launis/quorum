import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

void main() {
  testWidgets('BaseBlockCard renders title, icon, and handles toggle', (
    WidgetTester tester,
  ) async {
    bool toggled = false;

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
          ),
        ),
      ),
    );

    expect(find.text('Metadata Block'), findsOneWidget);
    expect(find.text('Includes metadata details'), findsOneWidget);
    expect(find.byType(Switch), findsOneWidget);

    await tester.tap(find.byType(Switch));
    await tester.pump();

    expect(toggled, isFalse);
  });
}
