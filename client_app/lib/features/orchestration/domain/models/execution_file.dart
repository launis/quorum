import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_file.freezed.dart';
part 'execution_file.g.dart';

@freezed
sealed class ExecutionFile with _$ExecutionFile {
  const factory ExecutionFile({
    required String name,
    String? path,
    List<int>? bytes,
  }) = _ExecutionFile;

  factory ExecutionFile.fromJson(Map<String, dynamic> json) =>
      _$ExecutionFileFromJson(json);
}
