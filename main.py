import streamlit as st

from processing import process_pdf


def start_app():
    st.title("One AI demo")
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
        elif highlight_amount is None:
            highlight_amount = "normal"
        elif pdf_file is not None:
            st.write("Running...")
            pdf_bytes = pdf_file.getvalue()
            process_pdf(highlight_amount, pdf_bytes, api_key)
        else:
            st.write("Please upload a PDF file")
