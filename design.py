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
        /* Custom styles for MuiGrid-root and MuiGrid-item classes */
        .MuiGrid-root, .MuiGrid-item {
            background-color: #36344B;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
