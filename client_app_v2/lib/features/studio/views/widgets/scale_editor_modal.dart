import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class ScaleEditorModal extends StatefulWidget {
  final MatrixScale initialScale;

  const ScaleEditorModal({super.key, required this.initialScale});

  @override
  State<ScaleEditorModal> createState() => _ScaleEditorModalState();
}

class _ScaleEditorModalState extends State<ScaleEditorModal> {
  late MatrixScale _editableScale;

  @override
  void initState() {
    super.initState();
    _editableScale = widget.initialScale.copyWith();
  }

  void _save() {
    Navigator.of(context).pop(_editableScale);
  }

  void _addClaim() {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.add(
        MatrixClaim(
          label: const I18nText(defaultLocale: 'en', translations: {'en': ''}),
          tdaAssertions: [
            TDAAssertion.create(
              conceptDescription: 'CRITICAL MANDATE: ',
              inverseEvidence: false,
              aggregationMode: AggregationMode.exists,
            ),
          ],
        ),
      );
      _editableScale = _editableScale.copyWith(claims: claims);
    });
  }

  void _removeClaim(int index) {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.removeAt(index);
      _editableScale = _editableScale.copyWith(claims: claims);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final claims = _editableScale.claims;

    return Dialog(
      insetPadding: AppSpacing.p16,
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.editDimension),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.of(context).pop(),
          ),
          actions: [
            FilledButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check),
              label: Text(l10n.save),
            ),
            AppSpacing.w8,
          ],
        ),
        body: SingleChildScrollView(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                initialValue: _editableScale.score.toString(),
                decoration: InputDecoration(
                  labelText: l10n.scaleGradeScoreLabel,
                  border: const OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (val) {
                  final parsed = int.tryParse(val);
                  if (parsed != null) {
                    _editableScale = _editableScale.copyWith(score: parsed);
                  }
                },
              ),
              AppSpacing.h16,
              I18nTextField(
                label: l10n.scaleGradeNameLabel,
                initialData:
                    _editableScale.name ??
                    const I18nText(
                      defaultLocale: 'en',
                      translations: {'en': ''},
                    ),
                onChanged: (val) {
                  _editableScale = _editableScale.copyWith(name: val);
                },
              ),
              AppSpacing.h16,
              TextFormField(
                initialValue: _editableScale.aiLabel,
                decoration: InputDecoration(
                  labelText: l10n.scaleGradeAiLabel,
                  border: const OutlineInputBorder(),
                ),
                onChanged: (val) {
                  _editableScale = _editableScale.copyWith(aiLabel: val.trim());
                },
              ),
              AppSpacing.h16,
              Text(
                l10n.scaleClaimsTitle,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              AppSpacing.h8,
              ...claims.asMap().entries.map((entry) {
                final index = entry.key;
                final claim = entry.value;

                return Card(
                  margin: AppSpacing.p16,
                  color: Theme.of(context).colorScheme.surface,
                  child: Padding(
                    padding: AppSpacing.p12,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              l10n.scaleClaimIndexTitle(index + 1),
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            IconButton(
                              icon: Icon(
                                Icons.delete,
                                color: Theme.of(context).colorScheme.error,
                              ),
                              onPressed: () => _removeClaim(index),
                              tooltip: l10n.scaleRemoveClaimTooltip,
                            ),
                          ],
                        ),
                        AppSpacing.h8,
                        I18nTextField(
                          label: l10n.scaleClaimTranslationLabel,
                          initialData: claim.label,
                          onChanged: (val) {
                            setState(() {
                              final newClaims = List<MatrixClaim>.from(
                                _editableScale.claims,
                              );
                              newClaims[index] = claim.copyWith(label: val);
                              _editableScale = _editableScale.copyWith(
                                claims: newClaims,
                              );
                            });
                          },
                        ),
                        AppSpacing.h16,
                        const Divider(),
                        AppSpacing.h8,
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              l10n.scaleTdaTitle(claim.tdaAssertions.length),
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            TextButton.icon(
                              onPressed: () {
                                setState(() {
                                  final newTdas = List<TDAAssertion>.from(
                                    claim.tdaAssertions,
                                  );
                                  newTdas.add(
                                    TDAAssertion.create(
                                      conceptDescription: '',
                                      inverseEvidence: false,
                                      aggregationMode: AggregationMode.exists,
                                      evaluationTrack:
                                          EvaluationTrack.cognitiveJudgement,
                                    ),
                                  );
                                  final newClaims = List<MatrixClaim>.from(
                                    _editableScale.claims,
                                  );
                                  newClaims[index] = claim.copyWith(
                                    tdaAssertions: newTdas,
                                  );
                                  _editableScale = _editableScale.copyWith(
                                    claims: newClaims,
                                  );
                                });
                              },
                              icon: const Icon(Icons.add, size: 18),
                              label: Text(l10n.scaleAddTdaBtn),
                            ),
                          ],
                        ),
                        AppSpacing.h8,
                        ...claim.tdaAssertions.asMap().entries.map((tdaEntry) {
                          final tdaIdx = tdaEntry.key;
                          final tda = tdaEntry.value;

                          return Card(
                            margin: AppSpacing.p12,
                            color: Theme.of(
                              context,
                            ).colorScheme.surfaceContainerLow,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(6),
                              side: BorderSide(
                                color: Theme.of(
                                  context,
                                ).colorScheme.outlineVariant,
                              ),
                            ),
                            child: Padding(
                              padding: AppSpacing.p8,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        l10n.scaleAssertionIndexTitle(
                                          tdaIdx + 1,
                                          tda.tdaId,
                                        ),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                      IconButton(
                                        icon: const Icon(
                                          Icons.delete_outline,
                                          size: 18,
                                        ),
                                        onPressed: () {
                                          setState(() {
                                            final newTdas =
                                                List<TDAAssertion>.from(
                                                  claim.tdaAssertions,
                                                )..removeAt(tdaIdx);
                                            final newClaims =
                                                List<MatrixClaim>.from(
                                                  _editableScale.claims,
                                                );
                                            newClaims[index] = claim.copyWith(
                                              tdaAssertions: newTdas,
                                            );
                                            _editableScale = _editableScale
                                                .copyWith(claims: newClaims);
                                          });
                                        },
                                        tooltip: l10n.scaleRemoveTdaTooltip,
                                      ),
                                    ],
                                  ),
                                  AppSpacing.h8,
                                  DropdownButtonFormField<EvaluationTrack>(
                                    initialValue: tda.evaluationTrack,
                                    decoration: InputDecoration(
                                      labelText: l10n.scaleEvaluationTrackLabel,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    items: EvaluationTrack.values.map((track) {
                                      return DropdownMenuItem<EvaluationTrack>(
                                        value: track,
                                        child: Text(
                                          track ==
                                                  EvaluationTrack
                                                      .extractiveSensor
                                              ? l10n.scaleTrackSensor
                                              : l10n.scaleTrackJudgement,
                                        ),
                                      );
                                    }).toList(),
                                    onChanged: (newTrack) {
                                      if (newTrack != null) {
                                        setState(() {
                                          final newTdas =
                                              List<TDAAssertion>.from(
                                                claim.tdaAssertions,
                                              );
                                          newTdas[tdaIdx] = tda.copyWith(
                                            evaluationTrack: newTrack,
                                          );
                                          final newClaims =
                                              List<MatrixClaim>.from(
                                                _editableScale.claims,
                                              );
                                          newClaims[index] = claim.copyWith(
                                            tdaAssertions: newTdas,
                                          );
                                          _editableScale = _editableScale
                                              .copyWith(claims: newClaims);
                                        });
                                      }
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.conceptDescription,
                                    decoration: InputDecoration(
                                      labelText:
                                          l10n.scaleConceptDescriptionLabel,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    maxLines: 2,
                                    validator: (val) {
                                      if (val == null ||
                                          val.trim().length <
                                              SystemUiConstraints
                                                  .tdaConceptMinLength
                                                  .value) {
                                        return l10n.tdaConceptMinLengthError(
                                          SystemUiConstraints
                                              .tdaConceptMinLength
                                              .value,
                                        );
                                      }
                                      return null;
                                    },
                                    onChanged: (newDesc) {
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          conceptDescription: newDesc,
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.anchorTarget,
                                    decoration: InputDecoration(
                                      labelText: l10n.tdaAnchorTarget,
                                      helperText: l10n.tdaAnchorTargetHelper,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    onChanged: (newVal) {
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          anchorTarget: newVal.trim().isEmpty
                                              ? null
                                              : newVal.trim(),
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  DropdownButtonFormField<String>(
                                    initialValue: tda.boundingBoxScope,
                                    decoration: InputDecoration(
                                      labelText: l10n.tdaBoundingBox,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    items: const [
                                      DropdownMenuItem(
                                        value: 'sentence',
                                        child: Text('Sentence'),
                                      ),
                                      DropdownMenuItem(
                                        value: 'paragraph',
                                        child: Text('Paragraph'),
                                      ),
                                      DropdownMenuItem(
                                        value: 'adjacent_paragraphs',
                                        child: Text('Adjacent Paragraphs'),
                                      ),
                                      DropdownMenuItem(
                                        value: 'document',
                                        child: Text('Document'),
                                      ),
                                    ],
                                    onChanged: (newVal) {
                                      if (newVal != null) {
                                        setState(() {
                                          final newTdas =
                                              List<TDAAssertion>.from(
                                                claim.tdaAssertions,
                                              );
                                          newTdas[tdaIdx] = tda.copyWith(
                                            boundingBoxScope: newVal,
                                          );
                                          final newClaims =
                                              List<MatrixClaim>.from(
                                                _editableScale.claims,
                                              );
                                          newClaims[index] = claim.copyWith(
                                            tdaAssertions: newTdas,
                                          );
                                          _editableScale = _editableScale
                                              .copyWith(claims: newClaims);
                                        });
                                      }
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.extractionRule,
                                    decoration: InputDecoration(
                                      labelText: l10n.tdaExtractionRule,
                                      helperText: l10n.tdaExtractionRuleHelper,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    maxLines: 2,
                                    onChanged: (newVal) {
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          extractionRule: newVal.trim().isEmpty
                                              ? null
                                              : newVal.trim(),
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.antiPatterns
                                        .map((a) => a.pattern)
                                        .join('\n'),
                                    decoration: InputDecoration(
                                      labelText: l10n.scaleAntiPatternsLabel,
                                      helperText: l10n.scaleAntiPatternsHelper,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    maxLines: 2,
                                    onChanged: (newAntiStr) {
                                      final parsedAnti = newAntiStr
                                          .split('\n')
                                          .map((e) => e.trim())
                                          .where((e) => e.isNotEmpty)
                                          .map(
                                            (e) => AntiPattern(
                                              pattern: e,
                                              allowsContextualExcuse: false,
                                            ),
                                          )
                                          .toList();
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          antiPatterns: parsedAnti,
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.contrastiveExample,
                                    decoration: InputDecoration(
                                      labelText:
                                          l10n.scaleContrastiveExampleLabel,
                                      helperText:
                                          l10n.scaleContrastiveExampleHelper,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    maxLines: 2,
                                    onChanged: (newVal) {
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          contrastiveExample:
                                              newVal.trim().isEmpty
                                              ? null
                                              : newVal.trim(),
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.acceptanceCriteria
                                        .map((a) => a.instruction)
                                        .join('\n'),
                                    decoration: InputDecoration(
                                      labelText:
                                          l10n.scaleAcceptanceCriteriaLabel,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    maxLines: 2,
                                    onChanged: (newAccStr) {
                                      final parsedAcc = newAccStr
                                          .split('\n')
                                          .map((e) => e.trim())
                                          .where((e) => e.isNotEmpty)
                                          .map(
                                            (e) => AcceptanceCriterion(
                                              instruction: e,
                                              requiresContextualOverride: false,
                                            ),
                                          )
                                          .toList();
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          acceptanceCriteria: parsedAcc,
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  TextFormField(
                                    initialValue: tda.syntacticAnchors.join(
                                      ', ',
                                    ),
                                    decoration: InputDecoration(
                                      labelText:
                                          l10n.scaleSyntacticAnchorsLabel,
                                      helperText:
                                          l10n.scaleSyntacticAnchorsHelper,
                                      border: const OutlineInputBorder(),
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 8,
                                          ),
                                    ),
                                    onChanged: (newAnchorsStr) {
                                      final parsed = newAnchorsStr
                                          .split(',')
                                          .map((e) => e.trim())
                                          .where((e) => e.isNotEmpty)
                                          .toList();
                                      setState(() {
                                        final newTdas = List<TDAAssertion>.from(
                                          claim.tdaAssertions,
                                        );
                                        newTdas[tdaIdx] = tda.copyWith(
                                          syntacticAnchors: parsed,
                                        );
                                        final newClaims =
                                            List<MatrixClaim>.from(
                                              _editableScale.claims,
                                            );
                                        newClaims[index] = claim.copyWith(
                                          tdaAssertions: newTdas,
                                        );
                                        _editableScale = _editableScale
                                            .copyWith(claims: newClaims);
                                      });
                                    },
                                  ),
                                  AppSpacing.h8,
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              l10n.scaleEnforcePreFlightTitle,
                                              style: const TextStyle(
                                                fontSize: 13,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            AppSpacing.h4,
                                            Text(
                                              l10n.scaleEnforcePreFlightDesc,
                                              style: TextStyle(
                                                fontSize: 11,
                                                color: Theme.of(
                                                  context,
                                                ).colorScheme.onSurfaceVariant,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      AppSpacing.w8,
                                      Switch(
                                        value: tda.enforcePreFlight,
                                        onChanged: (newVal) {
                                          setState(() {
                                            final newTdas =
                                                List<TDAAssertion>.from(
                                                  claim.tdaAssertions,
                                                );
                                            newTdas[tdaIdx] = tda.copyWith(
                                              enforcePreFlight: newVal,
                                            );
                                            final newClaims =
                                                List<MatrixClaim>.from(
                                                  _editableScale.claims,
                                                );
                                            newClaims[index] = claim.copyWith(
                                              tdaAssertions: newTdas,
                                            );
                                            _editableScale = _editableScale
                                                .copyWith(claims: newClaims);
                                          });
                                        },
                                      ),
                                    ],
                                  ),
                                  AppSpacing.h8,
                                  Row(
                                    children: [
                                      Expanded(
                                        child:
                                            DropdownButtonFormField<
                                              AggregationMode
                                            >(
                                              initialValue: tda.aggregationMode,
                                              decoration: InputDecoration(
                                                labelText: l10n
                                                    .scaleAggregationModeLabel,
                                                border:
                                                    const OutlineInputBorder(),
                                                contentPadding:
                                                    const EdgeInsets.symmetric(
                                                      horizontal: 10,
                                                      vertical: 8,
                                                    ),
                                              ),
                                              items: AggregationMode.values.map(
                                                (mode) {
                                                  return DropdownMenuItem<
                                                    AggregationMode
                                                  >(
                                                    value: mode,
                                                    child: Text(
                                                      mode ==
                                                              AggregationMode
                                                                  .exists
                                                          ? 'EXISTS'
                                                          : 'ALL_MUST_COMPLY',
                                                    ),
                                                  );
                                                },
                                              ).toList(),
                                              onChanged: (newMode) {
                                                if (newMode != null) {
                                                  setState(() {
                                                    final newTdas =
                                                        List<TDAAssertion>.from(
                                                          claim.tdaAssertions,
                                                        );
                                                    newTdas[tdaIdx] = tda
                                                        .copyWith(
                                                          aggregationMode:
                                                              newMode,
                                                        );
                                                    final newClaims =
                                                        List<MatrixClaim>.from(
                                                          _editableScale.claims,
                                                        );
                                                    newClaims[index] = claim
                                                        .copyWith(
                                                          tdaAssertions:
                                                              newTdas,
                                                        );
                                                    _editableScale =
                                                        _editableScale.copyWith(
                                                          claims: newClaims,
                                                        );
                                                  });
                                                }
                                              },
                                            ),
                                      ),
                                      AppSpacing.w8,
                                      Row(
                                        children: [
                                          Text(
                                            l10n.scaleInverseLabel,
                                            style: const TextStyle(
                                              fontSize: 12,
                                            ),
                                          ),
                                          Switch(
                                            value: tda.inverseEvidence,
                                            onChanged: (newVal) {
                                              setState(() {
                                                final newTdas =
                                                    List<TDAAssertion>.from(
                                                      claim.tdaAssertions,
                                                    );
                                                newTdas[tdaIdx] = tda.copyWith(
                                                  inverseEvidence: newVal,
                                                );
                                                final newClaims =
                                                    List<MatrixClaim>.from(
                                                      _editableScale.claims,
                                                    );
                                                newClaims[index] = claim
                                                    .copyWith(
                                                      tdaAssertions: newTdas,
                                                    );
                                                _editableScale = _editableScale
                                                    .copyWith(
                                                      claims: newClaims,
                                                    );
                                              });
                                            },
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),

                                  if (tda.evaluationTrack ==
                                      EvaluationTrack.extractiveSensor) ...[
                                    AppSpacing.h8,
                                    TextFormField(
                                      initialValue: tda.factsToFind.join(', '),
                                      decoration: InputDecoration(
                                        labelText: l10n.scaleFactsToFindLabel,
                                        helperText: l10n.scaleFactsToFindHelper,
                                        border: const OutlineInputBorder(),
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                              horizontal: 10,
                                              vertical: 8,
                                            ),
                                      ),
                                      onChanged: (newFactsStr) {
                                        final parsedFacts = newFactsStr
                                            .split(',')
                                            .map((e) => e.trim())
                                            .where((e) => e.isNotEmpty)
                                            .toList();
                                        setState(() {
                                          final newTdas =
                                              List<TDAAssertion>.from(
                                                claim.tdaAssertions,
                                              );
                                          newTdas[tdaIdx] = tda.copyWith(
                                            factsToFind: parsedFacts,
                                          );
                                          final newClaims =
                                              List<MatrixClaim>.from(
                                                _editableScale.claims,
                                              );
                                          newClaims[index] = claim.copyWith(
                                            tdaAssertions: newTdas,
                                          );
                                          _editableScale = _editableScale
                                              .copyWith(claims: newClaims);
                                        });
                                      },
                                    ),
                                    AppSpacing.h8,
                                    TextFormField(
                                      initialValue: tda.logicalExpression,
                                      decoration: InputDecoration(
                                        labelText:
                                            l10n.scaleLogicalExpressionLabel,
                                        helperText:
                                            l10n.scaleLogicalExpressionHelper,
                                        border: const OutlineInputBorder(),
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                              horizontal: 10,
                                              vertical: 8,
                                            ),
                                      ),
                                      onChanged: (newExpr) {
                                        setState(() {
                                          final newTdas =
                                              List<TDAAssertion>.from(
                                                claim.tdaAssertions,
                                              );
                                          newTdas[tdaIdx] = tda.copyWith(
                                            logicalExpression:
                                                newExpr.trim().isEmpty
                                                ? null
                                                : newExpr.trim(),
                                          );
                                          final newClaims =
                                              List<MatrixClaim>.from(
                                                _editableScale.claims,
                                              );
                                          newClaims[index] = claim.copyWith(
                                            tdaAssertions: newTdas,
                                          );
                                          _editableScale = _editableScale
                                              .copyWith(claims: newClaims);
                                        });
                                      },
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                );
              }),
              AppSpacing.h8,
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton.icon(
                  onPressed: _addClaim,
                  icon: const Icon(Icons.add),
                  label: Text(l10n.matrixAddCriterion),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
