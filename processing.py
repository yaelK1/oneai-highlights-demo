import oneai
import asyncio
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def highlight_is_mostly_name(highlight, names):
    heighlight_start = highlight.output_spans[0].start
    heighlight_end = highlight.output_spans[0].end
    for name in names:
        name_start = name.output_spans[0].start
        name_end = name.output_spans[0].end
        if (
            heighlight_start <= name_start <= heighlight_end
            or heighlight_start <= name_end <= heighlight_end
        ):
            name_to_highlight_ratio = (
                min(name_end, heighlight_end) - max(name_start, heighlight_start)
            ) / (heighlight_end - heighlight_start)
            if name_to_highlight_ratio > 0.5:
                return True
    return False


def process_pdf(highlight_amount, pdf_bytes, api_key):
    with st.spinner(text="In progress..."):
        oneai.api_key = api_key
        higighlights_pipeline = oneai.Pipeline(
            [oneai.skills.Highlights(params={"amount": "less"}), oneai.skills.Names()]
        )
        segments_pipeline = oneai.Pipeline(
            [
                oneai.skills.PDFExtractText(params={"engine": "v2"}),
                oneai.skills.SplitByTopic(amount=highlight_amount),
            ]
        )
        output = asyncio.run(segments_pipeline.run_async(pdf_bytes))
        segments = output.pdf_text.segments
        pages = [l for l in output.pdf_text.pdf_labels if l.name == "PAGE"]
        highlights = []
        for segment in segments:
            segment_output = higighlights_pipeline.run(segment.span_text)
            segment_names = segment_output.names
            segment_highlights = segment_output.highlights
            offset = segment.output_spans[0].start
            for highlight in segment_highlights:
                if not highlight_is_mostly_name(highlight, segment_names):
                    highlight.pages = []
                    highlight.segment_text = segment.span_text
                    highlight.start = offset + int(highlight.output_spans[0].start)
                    highlight.end = offset + int(highlight.output_spans[0].end)
                    highlight.score = float(highlight.data["score"])
                    highlight.highlight = highlight.span_text
                    for page in pages:
                        page.start = int(page.output_spans[0].start)
                        page.end = int(page.output_spans[0].end)
                        if (
                            page.start <= highlight.start <= page.end
                            or page.start <= highlight.end <= page.end
                        ):
                            highlight.pages.append(page.data["numeric_value"])
                    highlights.append(highlight)
        return highlights
