import 'dart:typed_data';

import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/orchestration/presentation/widgets/file_uploader.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **FileUploadField**
///
/// SDUI widget for uploading files.
/// Selects a file, uploads it immediately to `/api/v1/config/knowledge/upload`,
/// and returns the uploaded file's ID (or URL) to the form via [onChanged].
class FileUploadField extends ConsumerStatefulWidget {
  final String label;
  final String? initialValue; // Could be a File ID or Name
  final ValueChanged<String> onChanged;

  const FileUploadField({
    super.key,
    required this.label,
    this.initialValue,
    required this.onChanged,
  });

  @override
  ConsumerState<FileUploadField> createState() => _FileUploadFieldState();
}

class _FileUploadFieldState extends ConsumerState<FileUploadField> {
  // We store the ID internally as the "value" of this field.
  // We also track file name for display if available.
  String? _uploadedId;
  String? _fileName;
  bool _isUploading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _uploadedId = widget.initialValue;
    // If initialValue acts as ID, we might not know the filename unless we fetch it.
    // For now, we just display the ID or "File Set" if initialValue is present.
  }

  Future<void> _uploadFile(Uint8List bytes, String name) async {
    setState(() {
      _isUploading = true;
      _fileName = name; // Optimistic update of name
    });

    try {
      final api = ref.read(apiClientProvider);
      
      // FormData for upload
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: name),
      });

      final response = await api.post(
        '/v1/config/knowledge/upload',
        data: formData,
      );

      // Assume response returns { "id": "...", "url": "..." }
      // We'll use "id" as the form value.
      final data = response.data as Map<String, dynamic>;
      final fileId = data['id'] as String;

      setState(() {
        _uploadedId = fileId;
        _isUploading = false;
      });

      widget.onChanged(fileId);
    } catch (e) {
      setState(() {
        _isUploading = false;
        _error = 'Upload failed: $e';
        _fileName = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // If we have an uploaded ID but no filename (e.g. initialValue was id),
    // we show the ID as the name.
    final displayName = _fileName ?? (_uploadedId != null ? 'File ID: $_uploadedId' : null);

    return FileUploader(
      label: widget.label,
      initialFileName: displayName,
      isLoading: _isUploading,
      errorText: _error,
      onFileSelected: (file) async {
        setState(() {
          _error = null;
        });

        final bytes = file.bytes;
        final name = file.name;

        if (bytes == null) {
          setState(() => _error = 'File data not available');
          return;
        }

        await _uploadFile(bytes, name);
      },
    );
  }
}
