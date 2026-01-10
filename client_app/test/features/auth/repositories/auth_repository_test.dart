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
    const email = 'test@example.com';
    const password = 'pass';
    const token = 'firebase_token_123';

    final backendUserJson = {
      'user': {
        'uid': 'u-1',
        'email': email,
        'role': 'ADMIN',
        'organization_id': 'org-1',
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
      final user = await repository.signInWithEmailAndPassword(email, password);

      // 4. Verify
      expect(user.uid, 'u-1');
      expect(user.role, app_user.UserRole.admin);

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
      const uid = 'mock-user';
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

      final user = await repository.debugSignInWithMockToken(uid);

      expect(user.uid, 'u-1');
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
