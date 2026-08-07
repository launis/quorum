import re

def update_graphs():
    with open("backend_v2/services/sdui/adapters/matrix_graphs_adapter.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Add MarkdownBlock import if missing
    if "MarkdownBlock" not in content:
        content = content.replace("ParagraphBlock,", "ParagraphBlock,\n    MarkdownBlock,")

    # The existing code has:
    #                 if layout_def.description:
    #                     blocks.append(
    #                         ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
    #                     )
    #                 if section_blocks:
    #                     blocks.extend(section_blocks)

    # Let's replace the inner part of the loop.
    
    old_code = """                if layout_def.description:
                    blocks.append(
                        ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
                    )

                if section_blocks:
                    blocks.extend(section_blocks)

                if preset_view in ["3d_matrix", "2d_compare"] or text_delivery_mode != "none":
                    if preset_view == "3d_matrix":
                        blocks.append(SduiRadarChartBlock(title=layout_def.title, axes=axes))
                    elif preset_view == "2d_compare":
                        blocks.append(SduiScatterPlotBlock(title=layout_def.title, axes=axes))
                    elif preset_view == "1d_metrics":
                        blocks.append(SduiMetrics1DBlock(title=layout_def.title, axes=axes))
                    elif preset_view == "text_only":
                        for axis in axes:
                            blocks.extend(axis.inner_sdui_blocks)"""
                            
    new_code = """                # 1. Layout Title Block
                if layout_def.title:
                    blocks.append(MarkdownBlock(text=f"### {layout_def.title}"))

                # 2. Layout Text Explanation Block
                if layout_def.description:
                    blocks.append(ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[]))

                if section_blocks:
                    blocks.extend(section_blocks)

                if preset_view in ["3d_matrix", "2d_compare"] or text_delivery_mode != "none":
                    if preset_view == "3d_matrix":
                        blocks.append(SduiRadarChartBlock(title=None, axes=axes))
                    elif preset_view == "2d_compare":
                        blocks.append(SduiScatterPlotBlock(title=None, axes=axes))
                    elif preset_view == "1d_metrics":
                        blocks.append(SduiMetrics1DBlock(title=None, axes=axes))
                        
                    # Also, if they want axis-level text for text_only:
                    if preset_view == "text_only":
                        for axis in axes:
                            if text_delivery_mode in ["full", "titles_only"]:
                                blocks.append(ParagraphBlock(text=f"**{axis.name}**", exact_quotes=[], citations=[]))
                            if text_delivery_mode == "full" and axis.row_explanation:
                                blocks.append(MarkdownBlock(text=axis.row_explanation))
"""
    # Wait, the plan specifically says:
    # "build the ParagraphBlock and MarkdownBlock directly inside the adapter's build method using the data from MatrixScorecardRowDTO.name and MatrixScorecardRowDTO.row_explanation"
    # So axis.name and axis.row_explanation ARE used! 
    # Let me adjust `new_code` for text_only.

    new_code_2 = """                if section_blocks:
                    blocks.extend(section_blocks)

                if preset_view in ["3d_matrix", "2d_compare", "1d_metrics"]:
                    if layout_def.title:
                        blocks.append(MarkdownBlock(text=f"### {layout_def.title}"))
                    if layout_def.description:
                        blocks.append(ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[]))
                        
                    if preset_view == "3d_matrix":
                        blocks.append(SduiRadarChartBlock(title=None, axes=axes))
                    elif preset_view == "2d_compare":
                        blocks.append(SduiScatterPlotBlock(title=None, axes=axes))
                    elif preset_view == "1d_metrics":
                        blocks.append(SduiMetrics1DBlock(title=None, axes=axes))
                elif preset_view == "text_only" and text_delivery_mode != "none":
                    if layout_def.title:
                        blocks.append(MarkdownBlock(text=f"### {layout_def.title}"))
                    if layout_def.description:
                        blocks.append(ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[]))
                    
                    for axis in axes:
                        if text_delivery_mode in ["full", "titles_only"]:
                            blocks.append(ParagraphBlock(text=f"**{axis.name}**", exact_quotes=[], citations=[]))
                        if text_delivery_mode == "full" and axis.row_explanation:
                            blocks.append(MarkdownBlock(text=axis.row_explanation))
"""

    content = content.replace(old_code, new_code_2)

    with open("backend_v2/services/sdui/adapters/matrix_graphs_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

def update_summary_table():
    with open("backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py", "r", encoding="utf-8") as f:
        content = f.read()

    if "MarkdownBlock" not in content:
        content = content.replace("ParagraphBlock,", "ParagraphBlock,\n    MarkdownBlock,")

    old_code = """                if layout_def.description:
                    blocks.append(
                        ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
                    )

                if section_blocks:
                    blocks.extend(section_blocks)

                blocks.append(
                    SduiMatrixTableBlock(
                        title=layout_def.title,
                        axes=axes,
                        matrix_column_labels=layout_def.matrix_column_labels,
                        matrix_visible_columns=layout_def.matrix_visible_columns,
                        extension_labels=context.profile.extension_labels,
                    )
                )"""
                
    new_code = """                if layout_def.title:
                    blocks.append(MarkdownBlock(text=f"### {layout_def.title}"))
                    
                if layout_def.description:
                    blocks.append(
                        ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
                    )

                if section_blocks:
                    blocks.extend(section_blocks)

                blocks.append(
                    SduiMatrixTableBlock(
                        title=None,
                        axes=axes,
                        matrix_column_labels=layout_def.matrix_column_labels,
                        matrix_visible_columns=layout_def.matrix_visible_columns,
                        extension_labels=context.profile.extension_labels,
                    )
                )"""

    content = content.replace(old_code, new_code)
    
    with open("backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

update_graphs()
update_summary_table()
print("Updated adapters")
