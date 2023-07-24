import oneai
import asyncio
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def highlight_is_mostly_name(highlight, names):
    heighlight_start = highlight.output_spans[0].start
    heighlight_end = highlight.output_spans[0].end
    names_in_highlight_lengthes = []
    for name in names:
        name_start = name.output_spans[0].start
        name_end = name.output_spans[0].end
        if not (name_start >= heighlight_end or name_end <= heighlight_start):
            name_to_highlight_length = min(name_end, heighlight_end) - max(
                name_start, heighlight_start
            )
            names_in_highlight_lengthes.append(name_to_highlight_length)
    name_to_highlight_ratio = sum(names_in_highlight_lengthes) / (
        heighlight_end - heighlight_start
    )
    if name_to_highlight_ratio > 0.5:
        return True
    return False


def return_segment_highlights(segment, pages):
    higighlights_pipeline = oneai.Pipeline(
        [oneai.skills.Highlights(params={"amount": "less"}), oneai.skills.Names()]
    )
    try:
        segment_output = higighlights_pipeline.run(segment.span_text)
        segment_names = segment_output.names
        segment_highlights = segment_output.highlights
        offset = segment.output_spans[0].start
        highlights = []
        errpr_while_segment_higlight = None
        for highlight in segment_highlights:
            if not highlight_is_mostly_name(highlight, segment_names):
                highlight.pages = []
                highlight.segment_text = segment.span_text
                highlight.start = offset + int(highlight.output_spans[0].start)
                highlight.end = offset + int(highlight.output_spans[0].end)
                highlight.highlight = highlight.span_text
                words_context = 30
                highlight.context = (
                    (
                        " ".join(
                            highlight.segment_text[: highlight.start].split(" ")[
                                -words_context:
                            ]
                        )
                        + highlight.highlight
                        + " ".join(
                            highlight.segment_text[highlight.end :].split(" ")[
                                :words_context
                            ]
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                highlight.score = float(highlight.data["score"])
                for page in pages:
                    page.start = int(page.output_spans[0].start)
                    page.end = int(page.output_spans[0].end)
                    if (
                        page.start <= highlight.start <= page.end
                        or page.start <= highlight.end <= page.end
                    ):
                        highlight.pages.append(page.data["numeric_value"])
                    highlights.append(highlight)
        return [highlights, errpr_while_segment_higlight]
    except Exception as e:
        return [None, e]


def process_pdf(highlight_amount, pdf_bytes, api_key):
    with st.spinner(text="In progress..."):
        oneai.api_key = api_key
        segments_pipeline = oneai.Pipeline(
            [
                oneai.skills.PDFExtractText(params={"engine": "v2"}),
                oneai.skills.SplitByTopic(amount=highlight_amount),
            ]
        )
        try:
            output = asyncio.run(segments_pipeline.run_async(pdf_bytes))
            segments = output.pdf_text.segments
            pages = [l for l in output.pdf_text.pdf_labels if l.name == "PAGE"]
            highlights = []
            for segment in segments:
                (
                    highlights_segment,
                    error_while_segment_higlight,
                ) = return_segment_highlights(segment, pages)
                if highlights_segment is not None:
                    highlights.extend(highlights_segment)
            if len(highlights) == 0:
                st.error(error_while_segment_higlight)
                return None
            return highlights

        except Exception as e:
            st.error("Error while processing the PDF file")
            st.error(e)
