import oneai
import asyncio
import streamlit as st
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


def highlight_is_mostly_name_and_number(highlight, names, numbers):
    heighlight_start = highlight.output_spans[0].start
    heighlight_end = highlight.output_spans[0].end
    names_in_highlight_spans = []
    numbers_in_highlight_spans = []
    for name in names:
        name_start = name.output_spans[0].start
        name_end = name.output_spans[0].end
        if not (name_start >= heighlight_end or name_end <= heighlight_start):
            spans = [min(name_end, heighlight_end), max(name_start, heighlight_start)]
            names_in_highlight_spans.append(spans)
    for number in numbers:
        number_start = number.output_spans[0].start
        number_end = number.output_spans[0].end
        if not (number_start >= heighlight_end or number_end <= heighlight_start):
            spans = [
                min(number_end, heighlight_end),
                max(number_start, heighlight_start),
            ]
            numbers_in_highlight_spans.append(spans)
    label_spans = []
    for name_span in names_in_highlight_spans:
        label_spans.extend(
            i for i in range(name_span[1], name_span[0]) if i not in label_spans
        )
    for number_span in numbers_in_highlight_spans:
        label_spans.extend(
            i for i in range(number_span[1], number_span[0]) if i not in label_spans
        )
    label_span_length = len(label_spans)
    highlight_span_length = heighlight_end - heighlight_start
    label_span_ratio = label_span_length / highlight_span_length
    if label_span_ratio > 0.5:
        return True
    return False


def process_highlight(highlight, pages, segment):
    highlight.pages = []
    # offset = segment.output_spans[0].start
    highlight.segment_text = segment.span_text
    # highlight.start = offset + int(highlight.output_spans[0].start)
    highlight.start = highlight.output_spans[0].start
    # highlight.end = offset + int(highlight.output_spans[0].end)
    highlight.end = highlight.output_spans[0].end
    highlight.highlight = highlight.span_text
    words_context = 30
    highlight.context = (
        (
            " ".join(
                highlight.segment_text[: highlight.start].split(" ")[-words_context:]
            )
            + highlight.highlight
            + " ".join(
                highlight.segment_text[highlight.end :].split(" ")[:words_context]
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
    return highlight


def return_segment_highlights(segment, pages, show_all_highlights=True):
    if show_all_highlights:
        higighlights_pipeline = oneai.Pipeline(
            [
                oneai.skills.Highlights(params={"amount": "less"}),
            ]
        )
    else:
        higighlights_pipeline = oneai.Pipeline(
            [
                oneai.skills.Highlights(params={"amount": "less"}),
                oneai.skills.Names(),
                oneai.skills.Numbers(),
            ]
        )
    try:
        segment_output = higighlights_pipeline.run(segment.span_text)
        segment_highlights = segment_output.highlights
        highlights = []
        for highlight in segment_highlights:
            if show_all_highlights:
                highlight_processed = process_highlight(highlight, pages, segment)
                highlights.append(highlight_processed)
            else:
                segment_names = segment_output.names
                segment_numbers = segment_output.numbers
                if not (
                    highlight_is_mostly_name(highlight, segment_names)
                    or highlight_is_mostly_name_and_number(
                        highlight, segment_names, segment_numbers
                    )
                ):
                    highlight_processed = process_highlight(highlight, pages, segment)
                    highlights.append(highlight_processed)
        return [highlights, None]
    except Exception as e:
        return [None, e]


def process_pdf(highlight_amount, pdf_bytes, api_key, show_all_highlights=True):
    with st.spinner(text="In progress..."):
        oneai.api_key = api_key
        segments_pipeline = oneai.Pipeline(
            [
                oneai.skills.PDFExtractText(params={"engine": "v2"}),
                oneai.skills.SplitByTopic(amount=highlight_amount, subheadings=False),
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
                ) = return_segment_highlights(segment, pages, show_all_highlights)
                if highlights_segment is not None:
                    highlights.extend(highlights_segment)
                else:
                    st.error(error_while_segment_higlight)
            if len(highlights) == 0:
                st.error(error_while_segment_higlight)
                return None
            highlight_text_distinct = []
            distinct_highlights = []
            for highlight in highlights:
                if highlight.span_text not in highlight_text_distinct:
                    highlight_text_distinct.append(highlight.span_text)
                    distinct_highlights.append(highlight)
            return distinct_highlights
        except Exception as e:
            st.error("Error while processing the PDF file")
            st.error(e)
