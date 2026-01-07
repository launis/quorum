import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class FileInputField extends StatefulWidget {
  final String label;
  final IconData? icon;
  final PlatformFile? value; // Current value (file object)
  final ValueChanged<PlatformFile> onFileSelected;
  final VoidCallback onClear;
  final String? Function(PlatformFile?)? validator;

  const FileInputField({
    super.key,
    required this.label,
    required this.onFileSelected,
    required this.onClear,
    this.icon,
    this.value,
    this.validator,
  });

  @override
  State<FileInputField> createState() => _FileInputFieldState();
}

class _FileInputFieldState extends State<FileInputField> {
  bool _isLoading = false;

  Future<void> _pickFile() async {
    setState(() => _isLoading = true);
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt', 'md', 'json', 'log', 'pdf', 'docx'],
        withData: kIsWeb, // Only load bytes in memory on Web
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        widget.onFileSelected(file);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error reading file: $e')));
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final fileName = widget.value?.name;
    final hasFile = fileName != null;

    return FormField<PlatformFile>(
      validator: widget.validator,
      initialValue: widget.value,
      builder: (state) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              onTap: _pickFile,
              borderRadius: BorderRadius.circular(4),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: widget.label,
                  border: const OutlineInputBorder(),
                  prefixIcon: widget.icon != null ? Icon(widget.icon) : null,
                  errorText: state.errorText,
                  suffixIcon:
                      _isLoading
                          ? const Padding(
                            padding: EdgeInsets.all(12.0),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                          : hasFile
                          ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: widget.onClear,
                          )
                          : const Icon(Icons.attach_file),
                ),
                child: Text(
                  fileName ?? 'Select a file...',
                  style: TextStyle(
                    color:
                        hasFile
                            ? Theme.of(context).textTheme.bodyMedium?.color
                            : Theme.of(context).hintColor,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
            if (hasFile)
              Padding(
                padding: const EdgeInsets.only(top: 4, left: 12),
                child: Text(
                  'File: ${widget.value!.name} (${widget.value!.size} bytes)',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
          ],
        );
      },
    );
  }
}
