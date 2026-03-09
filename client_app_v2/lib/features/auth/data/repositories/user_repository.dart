import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepository(ref.watch(apiClientProvider));
});

class UserRepository {
  final Dio _client;
  UserRepository(this._client);

  Future<Either<AppError, User>> fetchCurrentUser() async {
    try {
      final response = await _client.get<Map<String, dynamic>>('/iam/users/me');
      if (response.data == null) return const Left(AppError.server(null));
      return Right(User.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.response?.statusCode == 404)
        return const Left(AppError.notFound(''));
      if (e.response?.statusCode == 401)
        return const Left(AppError.unauthorized());
      return const Left(AppError.server(null));
    } catch (e) {
      return const Left(AppError.unknown());
    }
  }

  Future<Either<AppError, User>> updateProfile(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.patch<Map<String, dynamic>>(
        '/iam/users/me',
        data: data,
      );
      if (response.data == null) return const Left(AppError.server(null));
      return Right(User.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.response?.statusCode == 400)
        return const Left(AppError.validation(ValidationErrorReason.unknown));
      return const Left(AppError.server(null));
    } catch (e) {
      return const Left(AppError.unknown());
    }
  }
}
