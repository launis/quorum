import re
from pathlib import Path

file_path = Path(r"c:\src\quorum\backend_v2\templates\report_template.jinja2")
content = file_path.read_text(encoding="utf-8")

# Replace macro signature
content = content.replace(
    "{% macro render_sdui_blocks(blocks) %}",
    "{% macro render_sdui_blocks(blocks, level=0, charts=none) %}"
)

# Replace the dispatch logic at the end of the macro
dispatch_start = "{% elif block.block_type is defined and block.block_type == '3d_matrix' %}"
dispatch_end = "{% endmacro %}"

dispatch_replacement = """{% elif block.block_type is defined and block.block_type in ['3d_matrix', '2d_compare'] %}
                {% if level == 0 and charts and loop.index0 in charts %}
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{{ charts[loop.index0] }}" style="max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 8px;" />
                </div>
                {% endif %}
            {% elif block.block_type is defined and block.block_type == '1d_metrics' %}
                {% if block.axes is defined %}
                {% for axis in block.axes %}
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <h3 style="margin: 0; color: #1a1a1a; font-size: 16px;">{{ axis.name }}</h3>
                            {% if axis.score_display_label %}
                            <div style="display: flex; align-items: center; gap: 8px;">
                                {% if axis.contextual_override %}
                                <span style="color: #f57c00; font-size: 12px; font-weight: 500;">⚠️ {{ l10n.evidence_rejected }}</span>
                                {% endif %}
                                <div style="background-color: #e3f2fd; color: #1976D2; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 14px;">
                                    {{ axis.score_display_label }}
                                </div>
                            </div>
                            {% endif %}
                        </div>
                        
                        {% if axis.description %}
                            <div style="font-size: 12px; color: #666; font-style: italic; margin-bottom: 8px;">{{ axis.description }}</div>
                        {% endif %}
                        
                        {% if axis.ui_plot_ratio != None %}
                            <div style="margin: 12px 0 8px 0; background-color: #eee; border-radius: 6px; height: 12px; width: 100%; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, rgba(33,150,243,0.6) 0%, rgba(33,150,243,1) 100%); height: 100%; width: {{ axis.ui_plot_ratio * 100 }}%; border-radius: 6px;"></div>
                            </div>
                        {% endif %}
                        
                        {% if axis.inner_sdui_blocks %}
                            <div style="margin-top: 15px;">
                                {{ render_sdui_blocks(axis.inner_sdui_blocks, level=level+1) }}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
                {% endif %}
            {% elif block.block_type is defined and block.block_type == 'matrix_summary' %}
                {% set visible_cols = block.matrix_visible_columns if block.matrix_visible_columns else [] %}
                {% if visible_cols and block.axes %}
                <div style="page-break-before: always; margin-top: 30px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; background-color: #fff; border: 1px solid #e0e0e0;">
                        <thead>
                            <tr style="background-color: #f5f5f5; border-bottom: 2px solid #ccc;">
                                {% if 'label' in visible_cols %}<th style="padding: 12px 10px; width: 25%; color: #333; font-weight: 700;">{{ l10n.lblLogicMatrix }}</th>{% endif %}
                                {% if 'distribution' in visible_cols or 'atomic_breakdown' in visible_cols %}<th style="padding: 12px 10px; width: 20%; color: #333; font-weight: 700;">{{ l10n.atomicBreakdownTitle }}</th>{% endif %}
                                {% if 'row_explanation' in visible_cols %}<th style="padding: 12px 10px; width: 20%; color: #333; font-weight: 700;">{{ l10n.rowExplanationTitle }}</th>{% endif %}
                                {% if 'quotes' in visible_cols %}<th style="padding: 12px 10px; width: 25%; color: #333; font-weight: 700;">Lainaukset (quotes)</th>{% endif %}
                                {% if 'normalized_score' in visible_cols %}<th style="padding: 12px 10px; width: 10%; color: #333; font-weight: 700;">{{ l10n.normalizedScore }}</th>{% endif %}
                                {% if 'score' in visible_cols %}<th style="padding: 12px 10px; width: 10%; color: #333; font-weight: 700;">{{ l10n.score }}</th>{% endif %}
                            </tr>
                        </thead>
                        <tbody>
                        {% for axis in block.axes %}
                            <tr style="border-bottom: 1px solid #eee;">
                                {% if 'label' in visible_cols %}
                                <td style="padding: 10px; vertical-align: top;">
                                    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">{{ axis.name }}{% if axis.is_evaluative %} *{% endif %}</div>
                                    {% if axis.description %}
                                    <div style="font-size: 10px; color: #666; font-weight: normal; line-height: 1.3;">{{ axis.description }}</div>
                                    {% endif %}
                                </td>
                                {% endif %}
                                {% if 'distribution' in visible_cols or 'atomic_breakdown' in visible_cols %}
                                <td style="padding: 10px; color: #555; vertical-align: top;">
                                    {% set lvl = axis.level_breakdown or {} %}
                                    {% set lvl_names = axis.level_names or {} %}
                                    {% if lvl %}
                                        <div style="margin: 0; font-size: 10px; line-height: 1.3;">
                                        {% for key, val in lvl.items() | sort(reverse=True, attribute='0') %}
                                            {% set hit_str = val if val is string else (val.hits ~ '/' ~ val.total) %}
                                            {% set name = lvl_names[key] if key in lvl_names else ('T' ~ key) %}
                                            {% set numLvl = (key | float | int) if '.' in key else (key | int) %}
                                            <div style="margin-bottom: 2px;">{{ numLvl }} - {{ name }}: {{ hit_str }}</div>
                                        {% endfor %}
                                        </div>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                {% endif %}
                                {% if 'row_explanation' in visible_cols %}
                                <td style="padding: 10px; color: #444; font-style: italic; font-size: 10px; vertical-align: top;">
                                    {{ axis.row_explanation }}
                                </td>
                                {% endif %}
                                {% if 'quotes' in visible_cols %}
                                <td style="padding: 10px; vertical-align: top; font-size: 10px;">
                                    {% set evaluated_atoms = axis.evaluated_atoms or [] %}
                                    {% if evaluated_atoms %}
                                        {% set grouped_atoms = evaluated_atoms | group_atoms_by_level %}
                                        {% for lvl, atoms in grouped_atoms.items() | sort(reverse=True, attribute='0') %}
                                            {% set lvl_name = axis.level_names[lvl|string] if axis.level_names and (lvl|string) in axis.level_names else '' %}
                                            <div style="font-weight: bold; margin-bottom: 4px; font-size: 11px;">{{ lvl }} - {{ lvl_name }}</div>
                                            {% set has_rendered = false %}
                                            {% for atom in atoms %}
                                                {% set status = (atom.status or '') | lower %}
                                                {% if status not in ['skipped', 'none', 'dlq'] and 'chunk processing failed' not in (atom.semantic_reasoning or '')|lower %}
                                                    <div style="margin-bottom: 8px;">
                                                        <div style="font-weight: {{ 'bold' if status in ['pass', 'contested'] else 'normal' }}; color: #333;">
                                                            - {{ atom.chart_display_label }}
                                                        </div>
                                                        {% if atom.exact_quotes %}
                                                            {% for quote in atom.exact_quotes %}
                                                                <div style="margin-top: 2px; color: #555;">
                                                                    {% if quote.display_name %}
                                                                        <span style="background-color: #e3f2fd; border: 1px solid #bbdefb; padding: 1px 4px; border-radius: 2px; font-size: 8px; font-weight: bold; color: #1565c0; margin-right: 4px;">{{ quote.display_name | upper }}</span>
                                                                    {% endif %}
                                                                    "{{ quote.quote }}"
                                                                    {% if quote.verified_source_ids %}
                                                                        <br><span style="font-size: 10px; color: #1976D2; font-weight: bold;">(Lähde: {{ quote.verified_source_ids | join(', ') }})</span>
                                                                    {% endif %}
                                                                </div>
                                                            {% endfor %}
                                                        {% endif %}
                                                    </div>
                                                    {% set has_rendered = true %}
                                                {% endif %}
                                            {% endfor %}
                                            {% if not has_rendered %}
                                                <div style="color: #999; font-style: italic; margin-bottom: 8px;">- N/A</div>
                                            {% endif %}
                                        {% endfor %}
                                    {% else %}
                                        <div style="color: #999; font-style: italic;">- N/A</div>
                                    {% endif %}
                                </td>
                                {% endif %}
                                {% if 'normalized_score' in visible_cols %}
                                <td style="padding: 10px; font-weight: bold; color: #2E7D32; vertical-align: top;">
                                    {% if axis.ui_plot_ratio != None %}
                                        <div style="background-color: #e8f5e9; border: 1px solid #c8e6c9; padding: 4px 8px; border-radius: 4px; display: inline-block;">
                                            {{ "%.1f"|format(axis.ui_plot_ratio * 100) }}%
                                        </div>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                {% endif %}
                                {% if 'score' in visible_cols %}
                                <td style="padding: 10px; font-weight: bold; color: #1565C0; vertical-align: top;">
                                    {% if axis.score_display_label %}
                                        {{ axis.score_display_label }}
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                {% endif %}
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    {% set has_evaluative = false %}
                    {% for axis in block.axes %}
                        {% if axis.is_evaluative %}{% set has_evaluative = true %}{% endif %}
                    {% endfor %}
                    {% if has_evaluative %}
                    <div style="font-size: 11px; color: #666; margin-top: 8px; font-style: italic;">
                        {{ l10n.matrixEvaluativeAsteriskLegend }}
                    </div>
                    {% endif %}
                </div>
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endmacro %}"""

start_idx = content.find(dispatch_start)
end_idx = content.find(dispatch_end) + len(dispatch_end)

content = content[:start_idx] + dispatch_replacement + content[end_idx:]

# Replace the initial call
content = content.replace(
    "{{ render_sdui_blocks(report_data.inner_sdui_blocks) }}",
    "{{ render_sdui_blocks(report_data.inner_sdui_blocks, level=0, charts=charts) }}"
)

# Remove the legacy layout loop and matrix summary
delete_start = "{% if report_data.inner_sdui_blocks is defined %}"
delete_end = "{% if report_data.mcp_tool_audit %}"

start_del_idx = content.find(delete_start)
end_del_idx = content.find(delete_end)

if start_del_idx != -1 and end_del_idx != -1:
    content = content[:start_del_idx] + content[end_del_idx:]

file_path.write_text(content, encoding="utf-8")
