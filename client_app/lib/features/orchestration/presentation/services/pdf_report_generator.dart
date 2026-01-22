
import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:intl/intl.dart';

class PdfReportGenerator {
  
  Future<Uint8List> generate(ReportView view) async {
    final doc = pw.Document();
    
    // Default fallback (WinAnsi - special chars might look wrong but won't crash)
    pw.Font baseFont = pw.Font.helvetica();
    pw.Font boldFont = pw.Font.helveticaBold();
    pw.Font italicFont = pw.Font.helveticaOblique();

    try {
      // Attempt to load NotoSans (better Unicode support)
      baseFont = await PdfGoogleFonts.notoSansRegular();
      boldFont = await PdfGoogleFonts.notoSansBold();
      italicFont = await PdfGoogleFonts.notoSansItalic();
    } catch (e) {
      // Log error (in a real app, use a logger)
      // print('Font loading failed: $e');
      // Proceed with Helvetica logic
    }

    final theme = pw.ThemeData.withFont(
      base: baseFont,
      bold: boldFont,
      italic: italicFont,
    );

    doc.addPage(
      pw.MultiPage(
        pageTheme: pw.PageTheme(
          theme: theme,
          pageFormat: PdfPageFormat.a4,
          margin: const pw.EdgeInsets.all(32),
        ),
        build: (pw.Context context) {
          return [
            _buildHeader(view),
            pw.SizedBox(height: 20),
            ...view.sections.map((section) => _buildSection(section)).toList(),
            pw.Divider(),
            _buildFooter(),
          ];
        },
      ),
    );

    return doc.save();
  }

  pw.Widget _buildHeader(ReportView view) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          view.title.toUpperCase(),
          style: pw.TextStyle(fontSize: 20, fontWeight: pw.FontWeight.bold),
        ),
        pw.SizedBox(height: 4),
        pw.Text(
          "ID: ${view.viewId}",
          style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700),
        ),
        pw.SizedBox(height: 4),
        pw.Text(
          "Luotu: ${DateFormat('yyyy-MM-dd HH:mm').format(DateTime.now())}",
          style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700),
        ),
        pw.Divider(thickness: 2),
      ],
    );
  }

  pw.Widget _buildSection(UiSection section) {
    return pw.Container(
      margin: const pw.EdgeInsets.only(bottom: 16),
      padding: const pw.EdgeInsets.all(12),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey300),
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(4)),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
             section.title,
             style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: PdfColors.blue800),
          ),
          pw.SizedBox(height: 8),
          _renderSectionContent(section),
        ]
      )
    );
  }

  pw.Widget _renderSectionContent(UiSection section) {
    switch (section.type) {
      case 'SCORE_CARD':
        return _buildScoreCard(section.data);
      case 'MARKDOWN_BLOCK':
        return pw.Text(section.data['content'] ?? '');
      case 'LOGIC_ANALYSIS':
        return _buildLogicAnalysis(section.data);
      case 'DRIVER_PROFILE':
        return _buildDriverProfile(section.data);
      case 'ARCHIVIST_CHECK':
        return _buildArchivistCheck(section.data);
      // Fallback for others
      default:
        return _buildGenericMap(section.data);
    }
  }

  pw.Widget _buildScoreCard(Map<String, dynamic> data) {
    final score = data['total_score'];
    final verdict = data['verdict'];
    final dimensions = data['dimensions'] as List<dynamic>? ?? [];

    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Row(
          mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
          children: [
            pw.Text("Arvosana: $score", style: pw.TextStyle(fontSize: 18, fontWeight: pw.FontWeight.bold)),
            pw.Text(verdict ?? '', style: pw.TextStyle(fontSize: 16, fontStyle: pw.FontStyle.italic)),
          ]
        ),
        pw.SizedBox(height: 12),
        if (dimensions.isNotEmpty)
          pw.TableHelper.fromTextArray(
            headers: ['Ulottuvuus', 'Pisteet', 'Perustelu'],
            data: dimensions.map((d) => [
              d['label'] ?? '',
              d['score']?.toString() ?? '',
              d['reasoning'] ?? ''
            ]).toList(),
            headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold),
            cellAlignments: {
              0: pw.Alignment.centerLeft,
              1: pw.Alignment.center,
              2: pw.Alignment.centerLeft
            },
            columnWidths: {
               0: const pw.FixedColumnWidth(80),
               1: const pw.FixedColumnWidth(40),
               2: const pw.FlexColumnWidth(),
            }
          )
      ]
    );
  }

  pw.Widget _buildDriverProfile(Map<String, dynamic> data) {
      final role = data['driver_classification'] ?? 'N/A';
      final ratio = data['input_control_ratio'];
      final strategies = data['tunnistetut_strategiat'] as List<dynamic>? ?? [];

      return pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
           pw.Text("Rooli: $role", style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
           if (ratio != null) pw.Text("Kontrollisuhde: $ratio"),
           pw.SizedBox(height: 8),
           if (strategies.isNotEmpty)
             pw.Text("Strategiat: ${strategies.join(', ')}", style: const pw.TextStyle(fontSize: 10))
        ]
      );
  }

  pw.Widget _buildLogicAnalysis(Map<String, dynamic> data) {
      final toulmin = data['toulmin_analyysi'] as List<dynamic>? ?? [];
      final reasoning = data['reasoning_trace'];
      
      return pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
           if (reasoning != null) ...[
             pw.Text("Päättelyketju:", style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
             pw.Text(reasoning.toString(), style: const pw.TextStyle(fontSize: 10)),
             pw.SizedBox(height: 8),
           ],
           if (toulmin.isNotEmpty) ...[
             pw.Text("Argumentaatio:", style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
              ...toulmin.map((t) => pw.Container(
                margin: const pw.EdgeInsets.only(top: 4),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                     pw.Text("Väite: ${t['claim'] ?? ''}", style: const pw.TextStyle(fontSize: 10)),
                     pw.Text("Perustelu: ${t['warrant'] ?? ''}", style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
                  ]
                )
              )).toList()
           ]
        ]
      );
  }

  pw.Widget _buildArchivistCheck(Map<String, dynamic> data) {
      final analysis = data['analysis'];
      return pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text("Compliance-analyysi:", style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
           pw.Text(analysis != null && analysis.isNotEmpty ? analysis : "Ei analyysiä."),
        ]
      );
  }

  pw.Widget _buildGenericMap(Map<String, dynamic> data) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start, 
      children: data.entries.map((e) {
         // Skip complex nested objects in generic view for PDF safety
         if (e.value is Map || e.value is List) return pw.Container();
         return pw.Text("${e.key}: ${e.value}", style: const pw.TextStyle(fontSize: 10));
      }).toList()
    );
  }

  pw.Widget _buildFooter() {
     return pw.Center(
       child: pw.Text("Cognitive Quorum Audit Report - Generated Automatically", style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey))
     );
  }
}
