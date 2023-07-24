import base64
import io
import os
import streamlit as st
import pandas as pd
from processing import process_pdf
from PIL import Image
from design import style


def show_results(highlights):
    df = pd.DataFrame(
        [
            [h.highlight, h.score, h.pages, h.context]
            for h in highlights
            if h is not None
        ],
        columns=["Highlight", "Score", "Pages", "Context"],
    )
    max_length = df["Highlight"].str.len().max()
    style = f"<style>.highlight-col {{ width: {max_length}ch; }}</style>"
    style += "<style>.pages-col, .score-col { width: 50px; }</style>"

    # Create a new DataFrame column with highlights in bold within the context
    df["Highlighted_Context"] = df.apply(
        lambda row: row["Context"].replace(
            row["Highlight"], f" **{row['Highlight']}** "
        ),
        axis=1,
    )

    # Drop the original "Highlight" and "Context" columns
    df.drop(columns=["Context"], inplace=True)

    # Rename the new column to "Context"
    df.rename(columns={"Highlighted_Context": "Context"}, inplace=True)

    # Convert the DataFrame to an HTML table
    df_html = df.to_html(
        columns=["Highlight", "Score", "Pages", "Context"], index=False, justify="left"
    )

    # Add custom styles and the HTML table
    df_html = df_html.replace("<table", f"{style}<table")

    # Display the HTML table in Streamlit
    st.markdown(df_html, unsafe_allow_html=True)

    # Convert DataFrame to CSV data and generate a download link for the CSV file
    csv_data = df.to_csv(index=False)
    b64 = base64.b64encode(csv_data.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="highlights.csv">Download Highlights CSV</a>'
    st.markdown(href, unsafe_allow_html=True)


def start_app():
    style()
    image = Image.open("logo.png")
    col1, col2 = st.columns([2, 3])
    col1.title("One AI demo")
    col2.image(image, width=500)
    api_key = st.text_input("Enter your API key")
    highlight_amount = st.selectbox(
        "Select amount of highlights", ["less", "normal", "more"]
    )
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    col3, col4 = st.columns([1, 1])
    # show_all_highlights = False
    col3, col4 = st.columns([1, 1])
    with col3:
        submit_button = st.button("Run")
        if submit_button:
            if api_key is None:
                st.write("Please enter your API key")
            elif pdf_file is not None:
                with open("uploaded_file.pdf", "wb") as f:
                    f.write(pdf_file.getvalue())
                with open("uploaded_file.pdf", "rb") as f:
                    try:
                        highlights = process_pdf(highlight_amount, f, api_key)
                        if highlights is not None:
                            show_results(highlights)
                        with open("uploaded_file.pdf", "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        os.remove("uploaded_file.pdf")
                    except Exception as e:
                        st.write(e)
            else:
                st.write("Please upload a PDF file")
    # with col4:
    #     switch = tog.st_toggle_switch(
    #         label="Show all highlights",
    #         key="show_all_highlights",
    #         label_after=True,
    #     )
    #     if switch:
    #         show_all_highlights = True
    #     else:
    #         show_all_highlights = False
