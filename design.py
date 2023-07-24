import streamlit as st


def style():
    st.markdown(
        """
        <style>
        body {
            background-color: #1D1C29;
            color: #FFFFFF;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #1D1C29;
        }
        div[data-baseweb="select"] {
            background-color: #36344B;
        }
        .stButton > button:first-child {
            background-color: #36344B;
            color: #B3B3B3;
            font-size: 10px;
        }
        div.stButton > button:hover {
            background-color: #1D1C29;
            color: #B3B3B3;
            border-color: #B3B3B3;
        }
        div.stButton > button:focus {
            background-color: #1D1C29;
            color: #B3B3B3;
            border-color: #B3B3B3;
            box-shadow: none;
        }
        div.object-container {
            background-color: #1D1C29;
        }
        .stTextInput > div > input {
            color: #FFFFFF;
        }
        .stTextInput > label {
            color: #FFFFFF;
        }
        .stSelectbox > label {
            color: #FFFFFF;
        }   
        .stSubheader > label {
            color: #FFFFFF;
        }   
        iframe {
            background-color: #15151F;
        }
        
        /* Adjust text color in the table */
        .stDataFrame td {
            color: #FFFFFF;
        }
        
        /* Make the text color lighter */
        body, p, h1, h2, h3, h4, h5, h6, span, div {
            color: #D0D0D0; /* You can adjust the color to your desired lighter shade */
        }
        </style>
        <script>
        // Apply custom style to select box options
        const selectOptions = document.querySelectorAll('.st-af');
        for (const option of selectOptions) {
            option.style.color = '#4A4A4A'; // You can adjust the color to your desired darker shade
        }
        </script>
        """,
        unsafe_allow_html=True,
    )
