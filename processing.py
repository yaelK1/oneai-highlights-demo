import oneai
import asyncio
import streamlit as st


def process_pdf(highlight_amount, pdf_bytes, api_key):
    oneai.api_key = api_key
    higighlights_pipeline = oneai.Pipeline(
        [oneai.skills.Highlights(params={"amount": highlight_amount})]
    )
    segments_pipeline = oneai.Pipeline(
        [
            oneai.skills.PDFExtractText(params={"engine": "v2"}),
            oneai.skills.SplitByTopic(),
        ]
    )
    segments = asyncio.run(segments_pipeline.run_async(pdf_bytes))
    st.write(segments)
