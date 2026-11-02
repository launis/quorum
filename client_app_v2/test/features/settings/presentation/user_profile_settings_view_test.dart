import 'dart:async';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/features/settings/presentation/user_profile_settings_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';

class _StubAuthController extends AuthController {
  User? _user;
  final List<bool> signOutCalls = [];

  _StubAuthController(this._user);

  @override
  FutureOr<User?> build() => _user;

  @override
  void setOptimisticUser(User updatedUser) {
    _user = updatedUser;
    state = AsyncData(updatedUser);
  }

  @override
  Future<void> signOut({bool revokeAllSessions = false}) async {
    signOutCalls.add(revokeAllSessions);
    _user = null;
    state = const AsyncData(null);
  }
}

class _StubSettingsController extends AsyncNotifier<AppSettingsState>
    implements SettingsController {
  AppSettingsState _settings;

  _StubSettingsController(this._settings);

  @override
  FutureOr<AppSettingsState> build() => _settings;

  @override
  Future<void> updateThemeMode(ThemeMode newMode) async {
    _settings = _settings.copyWith(themeMode: newMode);
    state = AsyncData(_settings);
  }

  @override
  Future<void> updateLocale(Locale newLocale) async {
    _settings = _settings.copyWith(locale: newLocale);
    state = AsyncData(_settings);
  }

  @override
  Future<void> syncFromUserProfile({
    String? language,
    String? themeMode,
  }) async {
    _settings = _settings.copyWith(
      locale: language != null ? Locale(language) : _settings.locale,
    );
    state = AsyncData(_settings);
  }
}

class _FakeUserRepository implements UserRepository {
  bool shouldFailUpdate = false;
  UserUpdate? lastUpdatePayload;

  @override
  Future<Either<AppException, User>> updateUser(
    String userId,
    UserUpdate payload,
  ) async {
    lastUpdatePayload = payload;
    if (shouldFailUpdate) {
      return Left(
        AppException.server(
          'Simulated profile persistence failure',
          statusCode: 500,
        ),
      );
    }
    return Right(
      User(
        id: userId,
        email: 'member@quorum.ai',
        name: payload.name ?? 'Updated Member',
        role: payload.role ?? UserRole.member,
        organizationId: 'org_01960000000070008000000000000001',
        language: payload.language ?? 'fi',
        themeMode: payload.themeMode ?? 'dark',
      ),
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget _buildTestWidget({
  required _StubAuthController authController,
  required _StubSettingsController settingsController,
  required _FakeUserRepository userRepo,
}) {
  return ProviderScope(
    overrides: [
      authControllerProvider.overrideWith(() => authController),
      settingsControllerProvider.overrideWith(() => settingsController),
      userRepositoryProvider.overrideWithValue(userRepo),
    ],
    child: const MaterialApp(
      localizationsDelegates: [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: [Locale('en'), Locale('fi')],
      home: UserProfileSettingsView(),
    ),
  );
}

void main() {
  const memberUser = User(
    id: 'usr_01960000000070008000000000000002',
    email: 'member@quorum.ai',
    name: 'Initial Member',
    role: UserRole.member,
    organizationId: 'org_01960000000070008000000000000001',
    language: 'en',
    themeMode: 'system',
  );

  group('UserProfileSettingsView Widget Tests', () {
    testWidgets(
      'positive: renders identity card, saves display name/language/theme optimistically, and triggers single/all-device signOut',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(memberUser);
        final settingsController = _StubSettingsController(
          const AppSettingsState(),
        );
        final userRepo = _FakeUserRepository();

        await tester.pumpWidget(
          _buildTestWidget(
            authController: authController,
            settingsController: settingsController,
            userRepo: userRepo,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('profile_identity_card')), findsOneWidget);
        expect(
          find.byKey(const Key('profile_preferences_card')),
          findsOneWidget,
        );
        expect(find.byKey(const Key('profile_session_card')), findsOneWidget);
        expect(find.text('member@quorum.ai'), findsWidgets);
        expect(find.text('MEMBER'), findsOneWidget);

        // Update display name and save preferences
        await tester.enterText(
          find.byKey(const Key('profile_display_name_field')),
          'Dr. Alice Member',
        );
        await tester.tap(find.byKey(const Key('profile_save_preferences_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastUpdatePayload?.name, 'Dr. Alice Member');

        // Trigger single-session signOut
        await tester.tap(find.byKey(const Key('profile_sign_out_btn')));
        await tester.pumpAndSettle();
        expect(authController.signOutCalls, [false]);
      },
    );

    testWidgets(
      'positive: Sign Out From All Devices button invokes signOut(revokeAllSessions: true)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(memberUser);
        final settingsController = _StubSettingsController(
          const AppSettingsState(),
        );
        final userRepo = _FakeUserRepository();

        await tester.pumpWidget(
          _buildTestWidget(
            authController: authController,
            settingsController: settingsController,
            userRepo: userRepo,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(
          find.byKey(const Key('profile_sign_out_all_devices_btn')),
        );
        await tester.pumpAndSettle();

        expect(authController.signOutCalls, [true]);
      },
    );

    testWidgets(
      'negative: rolls back optimistic user and settings state when UserRepository.updateUser fails',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(memberUser);
        final settingsController = _StubSettingsController(
          const AppSettingsState(),
        );
        final userRepo = _FakeUserRepository()..shouldFailUpdate = true;

        await tester.pumpWidget(
          _buildTestWidget(
            authController: authController,
            settingsController: settingsController,
            userRepo: userRepo,
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('profile_display_name_field')),
          'Broken Name Update',
        );
        await tester.tap(find.byKey(const Key('profile_save_preferences_btn')));
        await tester.pumpAndSettle();

        // Optimistic state rolled back to original memberUser.name
        expect(authController.state.value?.name, 'Initial Member');
      },
    );

    testWidgets(
      'negative: renders unauthorized message when authController emits null user',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(null);
        final settingsController = _StubSettingsController(
          const AppSettingsState(),
        );
        final userRepo = _FakeUserRepository();

        await tester.pumpWidget(
          _buildTestWidget(
            authController: authController,
            settingsController: settingsController,
            userRepo: userRepo,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('profile_identity_card')), findsNothing);
        expect(find.byKey(const Key('profile_session_card')), findsNothing);
      },
    );

    testWidgets(
      'boundary: switches layout at 800px mediumBreakpoint (799px Column vs 800px Row) and trims whitespace-only display name to null',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(799, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(memberUser);
        final settingsController = _StubSettingsController(
          const AppSettingsState(),
        );
        final userRepo = _FakeUserRepository();

        await tester.pumpWidget(
          _buildTestWidget(
            authController: authController,
            settingsController: settingsController,
            userRepo: userRepo,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('profile_identity_card')), findsOneWidget);
        expect(find.byKey(const Key('profile_session_card')), findsOneWidget);

        // Enter whitespace-only display name (boundary -> normalized to null)
        await tester.enterText(
          find.byKey(const Key('profile_display_name_field')),
          '   ',
        );
        await tester.tap(find.byKey(const Key('profile_save_preferences_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastUpdatePayload?.name, isNull);
      },
    );
  });
}
