import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/features/reports/controllers/report_artifact_controller.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/dialogs/create_report_dialog.dart';
import 'package:client_app/features/reports/views/widgets/report_artifact_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_saver/file_saver.dart';

/// Comprehensive Master-Detail reports management view adhering to Desktop Pro Tool UX.
class ExecutionReportsView extends ConsumerStatefulWidget {
  final String executionId;
  final String? initialReportId;
  final String? workflowId;

  const ExecutionReportsView({
    super.key,
    required this.executionId,
    this.initialReportId,
    this.workflowId,
  });

  @override
  ConsumerState<ExecutionReportsView> createState() =>
      _ExecutionReportsViewState();
}

class _ExecutionReportsViewState extends ConsumerState<ExecutionReportsView>
    with SingleTickerProviderStateMixin {
  String? _selectedReportId;
  late final TabController _tabController;
  final _searchController = TextEditingController();
  String _searchFilter = '';

  @override
  void initState() {
    super.initState();
    _selectedReportId = widget.initialReportId;
    _tabController = TabController(length: 4, vsync: this);
    _searchController.addListener(() {
      setState(() {
        _searchFilter = _searchController.text.trim().toLowerCase();
      });
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openCreateDialog() async {
    final result = await showDialog<ReportArtifactSummary>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => CreateReportDialog(
        executionId: widget.executionId,
        workflowId: widget.workflowId,
      ),
    );

    if (result != null && mounted) {
      setState(() {
        _selectedReportId = result.id;
      });
    }
  }

  Future<void> _downloadPdf(String reportId) async {
    try {
      final client = ref.read(reportsClientProvider);
      final bytes = await client.downloadPdf(reportId);
      await FileSaver.instance.saveAs(
        name: 'report_$reportId',
        bytes: bytes,
        fileExtension: 'pdf',
        mimeType: MimeType.pdf,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppLocalizations.of(context)!.downloadSuccess),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lataus epäonnistui: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _downloadExcel(String reportId) async {
    try {
      final client = ref.read(reportsClientProvider);
      final bytes = await client.downloadExcel(reportId);
      await FileSaver.instance.saveAs(
        name: 'report_$reportId',
        bytes: bytes,
        fileExtension: 'xlsx',
        mimeType: MimeType.microsoftExcel,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppLocalizations.of(context)!.downloadSuccess),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lataus epäonnistui: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _downloadCsv(String reportId) async {
    try {
      final client = ref.read(reportsClientProvider);
      final bytes = await client.downloadCsv(reportId);
      await FileSaver.instance.saveAs(
        name: 'report_$reportId',
        bytes: bytes,
        fileExtension: 'csv',
        mimeType: MimeType.csv,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppLocalizations.of(context)!.downloadSuccess),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lataus epäonnistui: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final reportsAsync = ref.watch(
      executionReportsProvider(widget.executionId),
    );
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.reportsTitle),
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: FilledButton.icon(
                icon: const Icon(Icons.add),
                label: Text(l10n.createReportButtonLabel),
                onPressed: _openCreateDialog,
              ),
            ),
          ],
        ),
        body: switch (reportsAsync) {
          AsyncLoading() => const Center(child: CircularProgressIndicator()),
          AsyncError(:final error, :final stackTrace) => ErrorView(
            error: error,
            stackTrace: stackTrace,
            onRetry: () =>
                ref.invalidate(executionReportsProvider(widget.executionId)),
          ),
          AsyncData(:final value) => _buildReportsData(
            context,
            value,
            l10n,
            theme,
            colorScheme,
          ),
        },
      ),
    );
  }

  Widget _buildReportsData(
    BuildContext context,
    List<ReportArtifactSummary> reports,
    AppLocalizations l10n,
    ThemeData theme,
    ColorScheme colorScheme,
  ) {
    if (reports.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.description_outlined,
              size: 64,
              color: colorScheme.outline,
            ),
            AppSpacing.h16,
            Text(
              l10n.reportsCountSubtitle(0),
              style: theme.textTheme.titleMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            AppSpacing.h16,
            FilledButton.icon(
              icon: const Icon(Icons.add),
              label: Text(l10n.createReportButtonLabel),
              onPressed: _openCreateDialog,
            ),
          ],
        ),
      );
    }

    // Ensure selection exists
    if (_selectedReportId == null ||
        !reports.any((r) => r.id == _selectedReportId)) {
      _selectedReportId = reports.first.id;
    }

    final filteredReports = reports.where((r) {
      if (_searchFilter.isEmpty) return true;
      return r.title.toLowerCase().contains(_searchFilter) ||
          r.id.toLowerCase().contains(_searchFilter) ||
          r.profileId.toLowerCase().contains(_searchFilter);
    }).toList();

    final selectedSummary = reports.firstWhere(
      (r) => r.id == _selectedReportId,
      orElse: () => reports.first,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 900;

        if (isWide) {
          return Row(
            children: [
              // Lateral Master Sidebar (Sticky 280px)
              SizedBox(
                width: 280,
                child: _buildMasterSidebar(
                  reports: reports,
                  filteredReports: filteredReports,
                  l10n: l10n,
                ),
              ),
              const VerticalDivider(width: 1),
              // Detail Canvas
              Expanded(child: _buildDetailCanvas(selectedSummary, l10n)),
            ],
          );
        } else {
          // Compact Top-Bar Selector
          return Column(
            children: [
              _buildTopBarSelector(reports, l10n),
              const Divider(height: 1),
              Expanded(child: _buildDetailCanvas(selectedSummary, l10n)),
            ],
          );
        }
      },
    );
  }

  Widget _buildMasterSidebar({
    required List<ReportArtifactSummary> reports,
    required List<ReportArtifactSummary> filteredReports,
    required AppLocalizations l10n,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      color: colorScheme.surfaceContainerLowest,
      padding: AppSpacing.p12,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  l10n.reportsTitle,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: colorScheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${filteredReports.length} / ${reports.length}',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: colorScheme.onSecondaryContainer,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          OutlinedButton.icon(
            icon: const Icon(Icons.add, size: 18),
            label: Text(l10n.createReportButtonLabel),
            onPressed: _openCreateDialog,
          ),
          if (reports.length > 10) ...[
            AppSpacing.h8,
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                isDense: true,
                prefixIcon: const Icon(Icons.search, size: 18),
                hintText: 'Hae raportteja...',
                suffixIcon: _searchFilter.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        onPressed: () => _searchController.clear(),
                      )
                    : null,
                border: const OutlineInputBorder(),
              ),
            ),
          ],
          AppSpacing.h12,
          Expanded(
            child: ListView.separated(
              itemCount: filteredReports.length,
              separatorBuilder: (context, index) => AppSpacing.h8,
              itemBuilder: (context, index) {
                final r = filteredReports[index];
                return ReportArtifactCard(
                  report: r,
                  isSelected: r.id == _selectedReportId,
                  onSelect: () => setState(() => _selectedReportId = r.id),
                  onDownloadPdf: () => _downloadPdf(r.id),
                  onDownloadExcel: () => _downloadExcel(r.id),
                  onDownloadCsv: () => _downloadCsv(r.id),
                  onRegenerate: () {
                    ref
                        .read(reportArtifactActionsProvider.notifier)
                        .regenerateReport(
                          reportId: r.id,
                          executionId: widget.executionId,
                        );
                  },
                  onDelete: () {
                    ref
                        .read(reportArtifactActionsProvider.notifier)
                        .deleteReport(
                          reportId: r.id,
                          executionId: widget.executionId,
                        );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopBarSelector(
    List<ReportArtifactSummary> reports,
    AppLocalizations l10n,
  ) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: AppSpacing.p12,
      child: Row(
        children: [
          OutlinedButton.icon(
            icon: const Icon(Icons.add, size: 16),
            label: Text(l10n.createReportButtonLabel),
            onPressed: _openCreateDialog,
          ),
          AppSpacing.w12,
          for (final r in reports) ...[
            ChoiceChip(
              label: Text(r.title),
              selected: r.id == _selectedReportId,
              onSelected: (selected) {
                if (selected) {
                  setState(() => _selectedReportId = r.id);
                }
              },
            ),
            AppSpacing.w8,
          ],
        ],
      ),
    );
  }

  Widget _buildDetailCanvas(
    ReportArtifactSummary report,
    AppLocalizations l10n,
  ) {
    final client = ref.read(reportsClientProvider);
    final detailAsync = ref.watch(reportDetailProvider(report.id));
    final currentStatus = detailAsync.asData?.value.status ?? report.status;
    final isReady = currentStatus == ReportStatus.ready;
    final isGeneratingOrPending =
        currentStatus == ReportStatus.generating ||
        currentStatus == ReportStatus.pending;

    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1200),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Action Bar Header
            Padding(
              padding: AppSpacing.p16,
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final isCompactRow = constraints.maxWidth < 520;
                  final titleWidget = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        report.title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        '${report.id} • ${report.locale.toUpperCase()} • ${report.profileId}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.outline,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  );

                  final actionsWidget = Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    alignment: WrapAlignment.end,
                    children: [
                      OutlinedButton.icon(
                        icon: const Icon(
                          Icons.picture_as_pdf_outlined,
                          size: 18,
                        ),
                        label: const Text('PDF'),
                        onPressed: isReady
                            ? () => _downloadPdf(report.id)
                            : null,
                      ),
                      OutlinedButton.icon(
                        icon: const Icon(Icons.table_chart_outlined, size: 18),
                        label: const Text('Excel'),
                        onPressed: isReady
                            ? () => _downloadExcel(report.id)
                            : null,
                      ),
                      OutlinedButton.icon(
                        icon: const Icon(Icons.description_outlined, size: 18),
                        label: const Text('CSV'),
                        onPressed: isReady
                            ? () => _downloadCsv(report.id)
                            : null,
                      ),
                      FilledButton.tonalIcon(
                        icon: const Icon(Icons.refresh, size: 18),
                        label: Text(l10n.retryReportGenerationLabel),
                        onPressed: isGeneratingOrPending
                            ? null
                            : () {
                                ref
                                    .read(
                                      reportArtifactActionsProvider.notifier,
                                    )
                                    .regenerateReport(
                                      reportId: report.id,
                                      executionId: widget.executionId,
                                    );
                              },
                      ),
                    ],
                  );

                  if (isCompactRow) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [titleWidget, AppSpacing.h12, actionsWidget],
                    );
                  } else {
                    return Row(
                      children: [
                        Expanded(child: titleWidget),
                        AppSpacing.w16,
                        actionsWidget,
                      ],
                    );
                  }
                },
              ),
            ),
            const Divider(height: 1),

            // Tab Navigation Header
            TabBar(
              controller: _tabController,
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              tabs: [
                Tab(text: l10n.tabInteractiveView),
                Tab(text: l10n.tabPdfPreview),
                Tab(text: l10n.tabTabularRows),
                Tab(text: l10n.tabTelemetryMetadata),
              ],
            ),

            // Tab Content Panes
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 1: Interactive SDUI View
                  _buildInteractiveTab(report),
                  // Tab 2: PDF Preview
                  _buildPdfTab(report, client),
                  // Tab 3: Tabular Rows
                  _buildRowsTab(report),
                  // Tab 4: Telemetry & Metadata
                  _buildMetadataTab(report.id),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractiveTab(ReportArtifactSummary reportSummary) {
    final detailAsync = ref.watch(reportDetailProvider(reportSummary.id));
    final currentStatus =
        detailAsync.asData?.value.status ?? reportSummary.status;

    if (currentStatus == ReportStatus.generating ||
        currentStatus == ReportStatus.pending) {
      final l10n = AppLocalizations.of(context)!;
      final theme = Theme.of(context);
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            AppSpacing.h16,
            Text(
              l10n.reportStatusGenerating,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    if (currentStatus == ReportStatus.failed) {
      final l10n = AppLocalizations.of(context)!;
      final theme = Theme.of(context);
      final errorMessage = detailAsync.asData?.value.errorMessage;

      return Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Card(
            elevation: 2,
            margin: AppSpacing.p24,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(
                color: theme.colorScheme.error.withValues(alpha: 0.3),
              ),
            ),
            child: Padding(
              padding: AppSpacing.p24,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.error_outline,
                    size: 48,
                    color: theme.colorScheme.error,
                  ),
                  AppSpacing.h16,
                  Text(
                    l10n.reportGenerationFailedNotice,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  if (errorMessage != null && errorMessage.isNotEmpty) ...[
                    AppSpacing.h12,
                    Container(
                      padding: AppSpacing.p12,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.errorContainer.withValues(
                          alpha: 0.3,
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        errorMessage,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontFamily: 'monospace',
                          color: theme.colorScheme.onErrorContainer,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                  AppSpacing.h24,
                  FilledButton.icon(
                    icon: const Icon(Icons.refresh, size: 18),
                    label: Text(l10n.retryReportGenerationLabel),
                    onPressed: () {
                      ref
                          .read(reportArtifactActionsProvider.notifier)
                          .regenerateReport(
                            reportId: reportSummary.id,
                            executionId: widget.executionId,
                          );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    final sduiAsync = ref.watch(reportSduiProvider(reportSummary.id));

    return AppErrorBoundary(
      child: sduiAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Padding(
            padding: AppSpacing.p24,
            child: Text(
              'SDUI-lataus epäonnistui: $err',
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        ),
        data: (sduiPayload) => SingleChildScrollView(
          child: ReportRendererV2Widget(
            payload: sduiPayload,
            executionId: widget.executionId,
          ),
        ),
      ),
    );
  }

  Widget _buildPdfTab(
    ReportArtifactSummary reportSummary,
    ReportsClient client,
  ) {
    final detailAsync = ref.watch(reportDetailProvider(reportSummary.id));
    final currentStatus =
        detailAsync.asData?.value.status ?? reportSummary.status;
    final isReady = currentStatus == ReportStatus.ready;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final pdfUrl = client.getPdfDownloadUrl(reportSummary.id);

    return AppErrorBoundary(
      child: Center(
        child: Card(
          margin: AppSpacing.p24,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: AppSpacing.p24,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.picture_as_pdf_outlined,
                  size: 64,
                  color: colorScheme.primary,
                ),
                AppSpacing.h16,
                Text(
                  l10n.downloadPdfTooltip,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                AppSpacing.h8,
                Text(
                  pdfUrl,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    color: colorScheme.outline,
                  ),
                ),
                AppSpacing.h24,
                FilledButton.icon(
                  icon: const Icon(Icons.download),
                  label: Text(l10n.downloadPdfTooltip),
                  onPressed: isReady
                      ? () => _downloadPdf(reportSummary.id)
                      : null,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRowsTab(ReportArtifactSummary reportSummary) {
    final detailAsync = ref.watch(reportDetailProvider(reportSummary.id));
    final currentStatus =
        detailAsync.asData?.value.status ?? reportSummary.status;

    if (currentStatus == ReportStatus.generating ||
        currentStatus == ReportStatus.pending) {
      final l10n = AppLocalizations.of(context)!;
      final theme = Theme.of(context);
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            AppSpacing.h16,
            Text(
              l10n.reportStatusGenerating,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    if (currentStatus == ReportStatus.failed) {
      final l10n = AppLocalizations.of(context)!;
      final theme = Theme.of(context);
      return Center(
        child: Text(
          l10n.reportGenerationFailedNotice,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.error,
          ),
        ),
      );
    }

    final rowsAsync = ref.watch(reportRowsProvider(reportSummary.id));

    return AppErrorBoundary(
      child: switch (rowsAsync) {
        AsyncLoading() => const Center(child: CircularProgressIndicator()),
        AsyncError(:final error, :final stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
          onRetry: () => ref.invalidate(reportRowsProvider(reportSummary.id)),
        ),
        AsyncData(:final value) =>
          value.isEmpty
              ? const Center(child: Text('Ei taulukkorivejä saatavilla.'))
              : SingleChildScrollView(
                  padding: AppSpacing.p16,
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('Kriteeri / Metriikka')),
                      DataColumn(label: Text('Pisteet')),
                      DataColumn(label: Text('Maksimi')),
                      DataColumn(label: Text('Perustelu & Sitaatti')),
                    ],
                    rows: value.map((row) {
                      return DataRow(
                        cells: [
                          DataCell(Text(row.metricLabel)),
                          DataCell(Text(row.score.toStringAsFixed(1))),
                          DataCell(Text(row.maxScale.toStringAsFixed(1))),
                          DataCell(
                            ConstrainedBox(
                              constraints: const BoxConstraints(maxWidth: 400),
                              child: Text(
                                row.reasoning ?? row.quote ?? '-',
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                ),
      },
    );
  }

  Widget _buildMetadataTab(String reportId) {
    final detailAsync = ref.watch(reportDetailProvider(reportId));
    final theme = Theme.of(context);

    return AppErrorBoundary(
      child: switch (detailAsync) {
        AsyncLoading() => const Center(child: CircularProgressIndicator()),
        AsyncError(:final error, :final stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
          onRetry: () => ref.invalidate(reportDetailProvider(reportId)),
        ),
        AsyncData(:final value) => Builder(
          builder: (context) {
            final meta = value.metadata;
            final paths = value.storagePaths;

            return SingleChildScrollView(
              padding: AppSpacing.p24,
              child: Card(
                child: Padding(
                  padding: AppSpacing.p24,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Suorituksen & Telemetrian Metatiedot',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Divider(),
                      AppSpacing.h12,
                      _buildMetaRow('Raportin ID', value.id),
                      _buildMetaRow('Suorituksen ID', value.executionId),
                      _buildMetaRow('Työnkulun ID', value.workflowId),
                      _buildMetaRow('Esitysprofiili', value.profileId),
                      _buildMetaRow('Luotu', value.createdAt.toIso8601String()),
                      _buildMetaRow(
                        'Päivitetty',
                        value.updatedAt.toIso8601String(),
                      ),
                      AppSpacing.h16,
                      Text(
                        'FinOps & LLM -kulutus',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Divider(),
                      AppSpacing.h8,
                      _buildMetaRow(
                        'Kustannus (USD)',
                        '\$${meta.costUsd?.toStringAsFixed(4) ?? "0.0000"}',
                      ),
                      _buildMetaRow('Kesto', '${meta.durationMs ?? 0} ms'),
                      _buildMetaRow(
                        'Tokeneita käytetty',
                        '${meta.tokensUsed ?? 0}',
                      ),
                      _buildMetaRow(
                        'Päättelytokeneita',
                        '${meta.thinkingTokens ?? 0}',
                      ),
                      _buildMetaRow('Mallin nimi', meta.llmModel ?? '-'),
                      _buildMetaRow('Palveluntarjoaja', meta.provider ?? '-'),
                      AppSpacing.h16,
                      Text(
                        'Tiedostopolut levyltä',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Divider(),
                      AppSpacing.h8,
                      _buildMetaRow('PDF-polku', paths.pdfPath ?? '-'),
                      _buildMetaRow(
                        'SDUI JSON -polku',
                        paths.sduiJsonPath ?? '-',
                      ),
                      _buildMetaRow('Excel-polku', paths.excelPath ?? '-'),
                      _buildMetaRow('CSV-polku', paths.csvPath ?? '-'),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      },
    );
  }

  Widget _buildMetaRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 180,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: SelectableText(
              value,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }
}
