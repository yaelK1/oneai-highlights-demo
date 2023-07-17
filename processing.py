import oneai
import asyncio
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def process_pdf(highlight_amount, pdf_bytes, api_key):
    print(pdf_bytes)
    oneai.api_key = api_key
    higighlights_pipeline = oneai.Pipeline(
        [oneai.skills.Highlights(params={"amount": highlight_amount})]
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
        segment_highlights = segment_output.highlights
        offset = segment.output_spans[0].start
        for highlight in segment_highlights:
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
