import 'dart:convert';
import 'dart:typed_data';
import 'package:intl/intl.dart'; // Added for DateFormat
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/result_dashboard.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/app_config.dart';
import 'package:http/http.dart' as http;
// Still imported just in case, or remove if unused? Keep for safety.
import 'package:file_picker/file_picker.dart'; // Added import for native save dialog
import 'package:url_launcher/url_launcher.dart'; // Added import for opening local files
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';

import 'dart:io'; // Added for File check
import 'package:shared_preferences/shared_preferences.dart'; // Added for caching

enum _PdfStatus { idle, downloading, ready, error }

class ExecutionResultScreen extends ConsumerStatefulWidget {
  final String executionId;

  const ExecutionResultScreen({super.key, required this.executionId});

  @override
  ConsumerState<ExecutionResultScreen> createState() =>
      _ExecutionResultScreenState();
}

class _ExecutionResultScreenState extends ConsumerState<ExecutionResultScreen> {
  _PdfStatus _status = _PdfStatus.idle;
  double _progress = 0.0;
  String _message = '';
  String _downloadedFilename = '';
  http.Client? _activeClient;
  Uint8List? _pdfBytes;

  @override
  void dispose() {
    _activeClient?.close();
    super.dispose();
  }

  void _cancelDownload() {
    _activeClient?.close();
    setState(() {
      _status = _PdfStatus.idle;
      _message = '';
      _progress = 0.0;
    });
  }

  Future<void> _openSavedFile(String path) async {
    if (await canLaunchUrl(Uri.file(path))) {
      await launchUrl(Uri.file(path));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Avataan tiedosto...'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Virhe: Ei voida avata tiedostoa: $path'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _saveAndOpenPdf() async {
    if (_pdfBytes != null) {
      try {
        final fallbackTimestamp = DateFormat('yyyyMMdd_HHmm').format(DateTime.now());
        final fallbackFilename = 'AUDIT_REPORT_${widget.executionId}_$fallbackTimestamp.pdf';
        var suggestedFilename = _downloadedFilename.isNotEmpty ? _downloadedFilename : fallbackFilename;
        
        if (!suggestedFilename.toLowerCase().endsWith('.pdf')) {
          suggestedFilename += '.pdf';
        }

        // Ask user for save location with a native Save As dialog
        final String? path = await FilePicker.platform.saveFile(
          dialogTitle: 'Tallenna pdf-raportti',
          fileName: suggestedFilename,
          type: FileType.custom,
          allowedExtensions: ['pdf'],
        );

        if (path != null && path.isNotEmpty) {
          String finalPath = path;
          // Pakotetaan .pdf pääte, jos Windowsin FilePicker on poistanut sen
          if (!finalPath.toLowerCase().endsWith('.pdf')) {
            finalPath += '.pdf';
          }

          // Write the bytes explicitly to the chosen path
          final file = File(finalPath);
          await file.writeAsBytes(_pdfBytes!);

          // Cache the path
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('pdf_path_${widget.executionId}', finalPath);

          // Open it
          await _openSavedFile(finalPath);
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Virhe tallennuksessa: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  Future<void> _handleDownloadAction() async {
    // 1. Check Cache First
    final prefs = await SharedPreferences.getInstance();
    final cachedPath = prefs.getString('pdf_path_${widget.executionId}');

    if (cachedPath != null) {
      final file = File(cachedPath);
      if (await file.exists()) {
        await _openSavedFile(cachedPath);
        return;
      }
    }

    // 2. Start Download if not found
    await _startDownload();
  }

  String _extractFilenameFromHeader(http.Response response) {
    final contentDisposition = response.headers['content-disposition'];
    if (contentDisposition != null) {
      // Parses both `filename="name.pdf"` and `filename=name.pdf`
      final match = RegExp(r'filename="?([^";]+)"?').firstMatch(contentDisposition);
      if (match != null && match.groupCount >= 1) {
        return match.group(1)!.trim();
      }
    }
    return '';
  }

  Future<void> _startDownload() async {
    setState(() {
      _status = _PdfStatus.downloading;
      _progress = 0.0;
      _message = 'Tarkistetaan...';
      _pdfBytes = null;
      _downloadedFilename = '';
    });

    try {
      final auth = ref.read(firebaseAuthInstanceProvider);
      final user = auth?.currentUser;
      String? token =
          (user != null)
              ? await user.getIdToken()
              : ref.read(mockTokenProvider);

      if (token == null) throw Exception('Ei kirjautumista');

      // Skip "check_local" backend call as we rely on client-side cache now,
      // or we can keep it as fallback, but for now let's simplify to direct download.
      setState(() => _message = "Aloitetaan lataus...");
      final url = Uri.parse(
        '${AppConfig.apiBaseUrl}/executions/${widget.executionId}/pdf/download',
      );

      var response = await http.get(
        url,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        // Ready immediately (Cached)
        final filename = _extractFilenameFromHeader(response);
        if (mounted) {
          setState(() {
            _pdfBytes = response.bodyBytes;
            _status = _PdfStatus.ready;
            _message = 'Valmis';
            _progress = 1.0;
            _downloadedFilename = filename;
          });
          // Manual Open
        }
        return;
      }

      if (response.statusCode == 202) {
        // 3. Start SSE
        final progressUrl = Uri.parse(
          '${AppConfig.apiBaseUrl}/executions/${widget.executionId}/pdf/progress',
        );
        _activeClient = http.Client();
        final request = http.Request('GET', progressUrl);
        request.headers['Authorization'] = 'Bearer $token';
        request.headers['Accept'] = 'text/event-stream';

        final streamResponse = await _activeClient!.send(request);

        await for (final chunk in streamResponse.stream.transform(
          utf8.decoder,
        )) {
          final lines = chunk.split('\n');
          for (final line in lines) {
            if (line.startsWith('data: ')) {
              try {
                final jsonStr = line.substring(6).trim();
                if (jsonStr.isEmpty) continue;

                if (jsonStr.contains('"progress"')) {
                  final progressMatch = RegExp(
                    r'"progress"\s*:\s*([\d\.]+)',
                  ).firstMatch(jsonStr);
                  final val =
                      double.tryParse(progressMatch?.group(1) ?? '0') ?? 0.0;

                  if (mounted) {
                    setState(() {
                      _progress = val;
                      _message = '${(val * 100).toInt()}%';
                    });
                  }

                  if (val >= 1.0) {
                    _activeClient?.close();
                    // Fetch Result
                    final finalResp = await http.get(
                      url,
                      headers: {'Authorization': 'Bearer $token'},
                    );
                    if (finalResp.statusCode == 200 && mounted) {
                      final filename = _extractFilenameFromHeader(finalResp);
                      setState(() {
                        _pdfBytes = finalResp.bodyBytes;
                        _status = _PdfStatus.ready;
                        _downloadedFilename = filename;
                      });
                      // Auto-save on first generation?
                      // User aid: "ekalla kerralla lataa itse omalle koneelle"
                      // So we should probably invoke _openPdf() automatically here?
                      _saveAndOpenPdf();
                    }
                    return;
                  }
                }
              } catch (e) {
                /* ignore parse error */
              }
            }
          }
        }
      } else {
        throw Exception('Virhe: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _status = _PdfStatus.error;
          _message = 'Virhe';
        });
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Virhe: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final asyncExecution = ref.watch(
      executionStreamProvider(widget.executionId),
    );
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.resultsTitle),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: _buildActionWidget(l10n),
          ),
        ],
      ),
      body: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: SizedBox.expand(
            child: asyncExecution.when(
              data: (execution) {
                if (execution is ExecutionCompleted) {
                  return ResultDashboard(execution: execution);
                } else {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(l10n.analysisNotComplete),
                        const SizedBox(height: 16),
                        FilledButton.icon(
                          onPressed:
                              () => context.go(
                                '/dashboard/executions/${widget.executionId}/monitor',
                              ),
                          icon: const Icon(Icons.visibility),
                          label: Text(l10n.goToMonitor),
                        ),
                      ],
                    ),
                  );
                }
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error:
                  (err, stack) =>
                      Center(child: Text(l10n.failedToLoad('$err'))),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActionWidget(AppLocalizations l10n) {
    switch (_status) {
      case _PdfStatus.downloading:
        return Container(
          width: 180,
          height: 36,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(18),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Row(
            children: [
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  value: _progress,
                  strokeWidth: 2,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _message,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              InkWell(
                onTap: _cancelDownload,
                child: const Icon(Icons.close, size: 18),
              ),
            ],
          ),
        );

      case _PdfStatus.ready:
        return FilledButton.icon(
          onPressed: _saveAndOpenPdf,
          style: FilledButton.styleFrom(
            backgroundColor: Colors.green,
            foregroundColor: Colors.white,
          ),
          icon: const Icon(Icons.download), // Changed to Download Icon
          label: const Text("Lataa PDF"), // Changed to Download Text
        );

      case _PdfStatus.error:
        return IconButton(
          onPressed: _handleDownloadAction,
          icon: const Icon(Icons.refresh, color: Colors.red),
          tooltip: "Yritä uudelleen",
        );

      case _PdfStatus.idle:
        return IconButton(
          onPressed: _handleDownloadAction,
          icon: const Icon(Icons.download),
          tooltip: l10n.downloadReportTooltip,
        );
    }
  }
}
