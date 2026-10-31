import 'package:client_app/core/theme/app_spacing.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('app_spacing.dart Design Token & Layout Invariant Tests', () {
    test(
      'Positive: AppSpacing numeric scale, EdgeInsets padding, and SizedBox spacers match exact design token specifications',
      () {
        expect(AppSpacing.s2, equals(2.0));
        expect(AppSpacing.s4, equals(4.0));
        expect(AppSpacing.s6, equals(6.0));
        expect(AppSpacing.s8, equals(8.0));
        expect(AppSpacing.s12, equals(12.0));
        expect(AppSpacing.s16, equals(16.0));
        expect(AppSpacing.s24, equals(24.0));
        expect(AppSpacing.s300, equals(300.0));

        expect(AppSpacing.p8, equals(const EdgeInsets.all(8.0)));
        expect(AppSpacing.p12, equals(const EdgeInsets.all(12.0)));
        expect(AppSpacing.p16, equals(const EdgeInsets.all(16.0)));
        expect(AppSpacing.p24, equals(const EdgeInsets.all(24.0)));

        expect(AppSpacing.h2.height, equals(2.0));
        expect(AppSpacing.h4.height, equals(4.0));
        expect(AppSpacing.h8.height, equals(8.0));
        expect(AppSpacing.h12.height, equals(12.0));
        expect(AppSpacing.h16.height, equals(16.0));
        expect(AppSpacing.h24.height, equals(24.0));

        expect(AppSpacing.w4.width, equals(4.0));
        expect(AppSpacing.w8.width, equals(8.0));
        expect(AppSpacing.w12.width, equals(12.0));
        expect(AppSpacing.w16.width, equals(16.0));
        expect(AppSpacing.w24.width, equals(24.0));
      },
    );

    test(
      'Negative/Boundary 1: Directional SizedBox tokens enforce orthogonal null axis and strict monotonic scale progression',
      () {
        // Vertical spacers must never constrain width (orthogonal axis must be null)
        for (final verticalBox in <SizedBox>[
          AppSpacing.h2,
          AppSpacing.h4,
          AppSpacing.h8,
          AppSpacing.h12,
          AppSpacing.h16,
          AppSpacing.h24,
        ]) {
          expect(verticalBox.width, isNull);
          expect(verticalBox.child, isNull);
          expect(verticalBox.height, isNotNull);
          expect(verticalBox.height! > 0, isTrue);
        }

        // Horizontal spacers must never constrain height (orthogonal axis must be null)
        for (final horizontalBox in <SizedBox>[
          AppSpacing.w4,
          AppSpacing.w8,
          AppSpacing.w12,
          AppSpacing.w16,
          AppSpacing.w24,
        ]) {
          expect(horizontalBox.height, isNull);
          expect(horizontalBox.child, isNull);
          expect(horizontalBox.width, isNotNull);
          expect(horizontalBox.width! > 0, isTrue);
        }

        // Strict monotonic boundary progression across the spacing scale
        final scale = <double>[
          AppSpacing.s2,
          AppSpacing.s4,
          AppSpacing.s6,
          AppSpacing.s8,
          AppSpacing.s12,
          AppSpacing.s16,
          AppSpacing.s24,
          AppSpacing.s300,
        ];
        for (var i = 0; i < scale.length - 1; i++) {
          expect(scale[i] < scale[i + 1], isTrue);
        }
      },
    );

    testWidgets(
      'Negative/Boundary 2: AppSpacing padding and spacer widgets enforce exact geometric offsets inside tighten/unbounded Flex boundaries',
      (WidgetTester tester) async {
        final firstKey = UniqueKey();
        final secondKey = UniqueKey();
        final paddedChildKey = UniqueKey();

        await tester.pumpWidget(
          Directionality(
            textDirection: TextDirection.ltr,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Padding(
                  padding: AppSpacing.p16,
                  child: SizedBox(key: paddedChildKey, width: 50, height: 20),
                ),
                AppSpacing.h12,
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    SizedBox(key: firstKey, width: 10, height: 10),
                    AppSpacing.w24,
                    SizedBox(key: secondKey, width: 10, height: 10),
                  ],
                ),
              ],
            ),
          ),
        );

        final paddedRect = tester.getRect(find.byKey(paddedChildKey));
        expect(paddedRect.left, equals(AppSpacing.s16));
        expect(paddedRect.top, equals(AppSpacing.s16));

        final firstRect = tester.getRect(find.byKey(firstKey));
        final secondRect = tester.getRect(find.byKey(secondKey));

        // Vertical separation between padded container bottom (20 + 32 = 52) and Row top must equal h12 (12.0)
        expect(
          firstRect.top - (paddedRect.bottom + AppSpacing.s16),
          equals(AppSpacing.s12),
        );

        // Horizontal separation between first and second box in Row must equal w24 (24.0)
        expect(secondRect.left - firstRect.right, equals(AppSpacing.s24));
      },
    );
  });
}
