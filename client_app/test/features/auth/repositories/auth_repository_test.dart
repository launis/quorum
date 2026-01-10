import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart' as app_user;
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import '../../../helpers/test_helper.mocks.dart';

void main() {
  late MockFirebaseAuth mockFirebaseAuth;
  late MockDio mockDio;
  late AuthRepository repository;
  late MockUserCredential mockUserCredential;
  late MockUser mockFirebaseUser;

  setUp(() {
    mockFirebaseAuth = MockFirebaseAuth();
    mockDio = MockDio();
    mockUserCredential = MockUserCredential();
    mockFirebaseUser = MockUser();

    // Inject mocks
    repository = AuthRepository(mockFirebaseAuth, mockDio);
  });

  group('AuthRepository', () {
    // Aligned with backend/seed/seed_data.json
    const email = 'root@example.com';
    const password = 'pass';
    const token = 'firebase_token_root_master';

    final backendUserJson = {
      'user': {
        'uid': 'root_master',
        'email': email,
        'role': 'ROOT',
        'organization_id': 'system',
        'display_name': 'System Root',
        'created_at': '2026-01-01T00:00:00',
        'language': 'fi',
        'theme_mode': 'system',
      },
    };

    test('signInWithEmailAndPassword success flow', () async {
      // 1. Setup Firebase mocks
      when(
        mockFirebaseAuth.signInWithEmailAndPassword(
          email: email,
          password: password,
        ),
      ).thenAnswer((_) async => mockUserCredential);

      when(mockUserCredential.user).thenReturn(mockFirebaseUser);
      when(mockFirebaseUser.getIdToken()).thenAnswer((_) async => token);

      // 2. Setup Backend Verify mock
      when(
        mockDio.post<Map<String, dynamic>>(
          '/auth/verify',
          data: {'token': token},
        ),
      ).thenAnswer(
        (_) async => Response(
          data: backendUserJson,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/'),
        ),
      );

      // 3. Call method
      final result = await repository.signInWithEmailAndPassword(
        email,
        password,
      );

      // 4. Verify
      expect(result.isRight(), true);
      final user = result.getRight().toNullable()!;
      expect(user.uid, 'root_master');
      expect(user.role, app_user.UserRole.root);
      expect(user.organizationId, 'system');

      verify(
        mockFirebaseAuth.signInWithEmailAndPassword(
          email: email,
          password: password,
        ),
      ).called(1);
      verify(
        mockDio.post<Map<String, dynamic>>(
          '/auth/verify',
          data: {'token': token},
        ),
      ).called(1);
    });

    test('debugSignInWithMockToken calls backend directly', () async {
      const uid = 'root_master';
      when(
        mockDio.post<Map<String, dynamic>>(
          '/auth/verify',
          data: {'token': 'mock-token:$uid'},
        ),
      ).thenAnswer(
        (_) async => Response(
          data: backendUserJson,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/'),
        ),
      );

      final result = await repository.debugSignInWithMockToken(uid);

      expect(result.isRight(), true);
      final user = result.getRight().toNullable()!;
      expect(user.uid, 'root_master');
      verify(
        mockDio.post<Map<String, dynamic>>(
          '/auth/verify',
          data: {'token': 'mock-token:$uid'},
        ),
      ).called(1);
      verifyZeroInteractions(mockFirebaseAuth);
    });
  });
}
