import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
from processing import process_pdf
from PIL import Image


def show_results(highlights):
    df = pd.DataFrame(
        [[h.highlight, h.score, h.pages, h.segment_text] for h in highlights],
        columns=["highlight", "score", "pages", "segment_text"],
    )
    AgGrid(df)


def display_pdf(pdf_file):
    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_file}" width="700" height="950" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def start_app():
    image = Image.open("logo.png")
    col1, col2 = st.columns([2, 1])
    col1.title("One AI demo")
    col2.image(image, width=200)
    st.write("Upload PDF file to extract highlights from it")
    api_key = st.text_input("Enter your API key")
    highlight_amount = st.selectbox(
        "Select amount of highlights", ["less", "normal", "more"]
    )
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    submit_button = st.button("Run")
    if submit_button:
        if api_key is None:
            st.write("Please enter your API key")
        elif pdf_file is not None:
            highlights = process_pdf(highlight_amount, pdf_file, api_key)
            show_results(highlights)
            pdf_file = pdf_file.getvalue().decode("utf-8")
            display_pdf(pdf_file)
        else:
            st.write("Please upload a PDF file")
