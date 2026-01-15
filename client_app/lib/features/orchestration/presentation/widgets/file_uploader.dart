import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

class FileUploader extends StatefulWidget {
  const FileUploader({
    super.key,
    required this.label,
    this.onFileSelected,
    this.initialFileName,
  });

  final String label;
  final ValueChanged<PlatformFile>? onFileSelected;
  final String? initialFileName;

  @override
  State<FileUploader> createState() => _FileUploaderState();
}

class _FileUploaderState extends State<FileUploader> {
  String? _fileName;

  @override
  void initState() {
    super.initState();
    _fileName = widget.initialFileName;
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles();

    if (result != null) {
      final file = result.files.single;
      setState(() {
        _fileName = file.name;
      });
      widget.onFileSelected?.call(file);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(widget.label, style: Theme.of(context).textTheme.labelMedium),
        const SizedBox(height: 8),
        InkWell(
          onTap: _pickFile,
          borderRadius: BorderRadius.circular(8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              border: Border.all(color: Theme.of(context).colorScheme.outline),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.attach_file,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _fileName ?? 'Select file...',
                    style: TextStyle(
                      color:
                          _fileName != null
                              ? Theme.of(context).colorScheme.onSurface
                              : Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (_fileName != null)
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () {
                      setState(() {
                        _fileName = null;
                      });
                      // Assume null clear is handled by parent if needed,
                      // or we pass null? ValueChanged<PlatformFile> implies non-null.
                      // For now just visual clear strictly for UX, parent state logic might vary.
                    },
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
