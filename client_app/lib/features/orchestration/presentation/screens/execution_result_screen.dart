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
import 'package:file_saver/file_saver.dart'; // Added import
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';

enum _PdfStatus { idle, downloading, ready, error }

class ExecutionResultScreen extends ConsumerStatefulWidget {
  final String executionId;

  const ExecutionResultScreen({super.key, required this.executionId});

  @override
  ConsumerState<ExecutionResultScreen> createState() => _ExecutionResultScreenState();
}

class _ExecutionResultScreenState extends ConsumerState<ExecutionResultScreen> {
  _PdfStatus _status = _PdfStatus.idle;
  double _progress = 0.0;
  String _message = '';
  Uint8List? _pdfBytes;
  http.Client? _activeClient;

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
    
    // Call backend cancel if desired: DELETE /executions/$id/pdf/cancel
    // For now client-side stop is enough UX.
  }

  Future<void> _openPdf() async {
    if (_pdfBytes != null) {
      // Use FileSaver to download instead of Printing to avoid Print Dialog
      final timestamp = DateFormat('yyyyMMdd_HHmm').format(DateTime.now());
      await FileSaver.instance.saveFile(
        name: 'AUDIT_REPORT_${widget.executionId}_$timestamp.pdf', // Explicit extension
        bytes: _pdfBytes!,
        mimeType: MimeType.pdf,
      );
    }
  }

  Future<void> _startDownload() async {
    setState(() {
      _status = _PdfStatus.downloading;
      _progress = 0.0;
      _message = 'Aloitetaan...';
      _pdfBytes = null;
    });

    try {
      final auth = ref.read(firebaseAuthInstanceProvider);
      final user = auth?.currentUser;
      String? token = (user != null) ? await user.getIdToken() : ref.read(mockTokenProvider);

      if (token == null) throw Exception('Ei kirjautumista');

      final url = Uri.parse('${AppConfig.apiBaseUrl}/executions/${widget.executionId}/pdf/download');
      
      // 1. Initial Check
      var response = await http.get(url, headers: {'Authorization': 'Bearer $token'});

      if (response.statusCode == 200) {
        // Ready immediately (Cached)
        if (mounted) {
            setState(() {
              _pdfBytes = response.bodyBytes;
              _status = _PdfStatus.ready;
              _message = 'Valmis';
              _progress = 1.0;
            });
            // Optional: Auto-open if cached? User wanted manual open button.
        }
        return;
      }

      if (response.statusCode == 202) {
         // 2. Start SSE
         final progressUrl = Uri.parse('${AppConfig.apiBaseUrl}/executions/${widget.executionId}/pdf/progress');
         _activeClient = http.Client();
         final request = http.Request('GET', progressUrl);
         request.headers['Authorization'] = 'Bearer $token';
         request.headers['Accept'] = 'text/event-stream';

         final streamResponse = await _activeClient!.send(request);
         
         await for (final chunk in streamResponse.stream.transform(utf8.decoder)) {
             final lines = chunk.split('\n');
             for (final line in lines) {
               if (line.startsWith('data: ')) {
                  try {
                      final jsonStr = line.substring(6).trim();
                      if (jsonStr.isEmpty) continue;

                      if (jsonStr.contains('"progress"')) {
                          final progressMatch = RegExp(r'"progress"\s*:\s*([\d\.]+)').firstMatch(jsonStr);
                          final val = double.tryParse(progressMatch?.group(1) ?? '0') ?? 0.0;
                          
                          if (mounted) {
                              setState(() {
                                _progress = val;
                                _message = '${(val*100).toInt()}%';
                              });
                          }

                          if (val >= 1.0) {
                              _activeClient?.close();
                              // Fetch Result
                              final finalResp = await http.get(url, headers: {'Authorization': 'Bearer $token'});
                              if (finalResp.statusCode == 200 && mounted) {
                                  setState(() {
                                      _pdfBytes = finalResp.bodyBytes;
                                      _status = _PdfStatus.ready;
                                  });
                              }
                              return;
                          }
                      }
                  } catch (e) { /* ignore parse error */ }
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
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Virhe: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final asyncExecution = ref.watch(executionStreamProvider(widget.executionId));
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
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
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
                         onPressed: () => context.go('/dashboard/executions/${widget.executionId}/monitor'),
                         icon: const Icon(Icons.visibility),
                         label: Text(l10n.goToMonitor),
                       ),
                    ],
                  ),
                );
              }
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (err, stack) => Center(child: Text(l10n.failedToLoad('$err'))),
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
                    child: CircularProgressIndicator(value: _progress, strokeWidth: 2)
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _message, 
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis
                  ),
                ),
                InkWell(
                    onTap: _cancelDownload,
                    child: const Icon(Icons.close, size: 18),
                )
              ],
            ),
          );

        case _PdfStatus.ready:
          return FilledButton.icon(
              onPressed: _openPdf,
              style: FilledButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
              ),
              icon: const Icon(Icons.download), // Changed to Download Icon
              label: const Text("Lataa PDF"), // Changed to Download Text
          );
        
        case _PdfStatus.error:
           return IconButton(
              onPressed: _startDownload,
              icon: const Icon(Icons.refresh, color: Colors.red),
              tooltip: "Yritä uudelleen",
           );

        case _PdfStatus.idle:
        default:
          return IconButton(
            onPressed: _startDownload,
            icon: const Icon(Icons.download),
            tooltip: l10n.downloadReportTooltip,
          );
      }
  }
}
