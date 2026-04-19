import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .stApp, body {
            background-color: #f5f7fb !important;
            color: #1f2937 !important;
        }

        #MainMenu, header, footer {
            visibility: hidden;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            background: transparent !important;
        }

        h1, h2, h3 {
            color: #1f2937 !important;
            font-weight: 700;
        }

        p, label, span, div {
            color: #1f2937;
        }

        div[data-testid="stMetric"] {
            background: white !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            color: #1f2937 !important;
        }

        div[data-baseweb="select"] * {
            background: white !important;
            color: #1f2937 !important;
        }

        div[role="listbox"] {
            background: white !important;
            color: #1f2937 !important;
            border: 1px solid #d1d5db !important;
        }

        div[role="option"] {
            background: white !important;
            color: #1f2937 !important;
        }

        div[role="option"]:hover {
            background: #f3f4f6 !important;
            color: #1f2937 !important;
        }

        ul {
            background: white !important;
            color: #1f2937 !important;
        }

        li {
            background: white !important;
            color: #1f2937 !important;
        }

        div[data-testid="stDateInput"] input,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            color: #1f2937 !important;
            background: white !important;
        }

        div[data-testid="stSlider"] * {
            color: #1f2937 !important;
        }

        button[kind="secondary"] {
            background: transparent !important;
            border: none !important;
            color: #374151 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
        }

        button[kind="secondary"]:hover {
            background: #e5e7eb !important;
        }

        .custom-logo {
            background: #005eb8;
            color: white !important;
            padding: 8px 14px;
            font-weight: 700;
            border-radius: 4px;
            display: inline-block;
        }

        .footer-text {
            text-align: center;
            color: #6b7280 !important;
            margin-top: 2rem;
            font-size: 0.95rem;
        }

        table {
            width: 100% !important;
            border-collapse: collapse !important;
            background: white !important;
            color: #1f2937 !important;
        }

        thead tr th {
            background: #f9fafb !important;
            color: #374151 !important;
            border: 1px solid #e5e7eb !important;
            padding: 10px !important;
            text-align: left !important;
        }

        tbody tr td {
            background: white !important;
            color: #1f2937 !important;
            border: 1px solid #e5e7eb !important;
            padding: 10px !important;
        }

        div[data-testid="stTable"] {
            background: white !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        div[data-testid="stDataFrame"] {
            background: white !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        div[data-testid="stDataFrame"] * {
            background: white !important;
            color: #1f2937 !important;
        }

        div[data-testid="stDataFrame"] [role="grid"] {
            background: white !important;
        }

        div[data-testid="stDataFrame"] [role="row"] {
            background: white !important;
        }

        div[data-testid="stDataFrame"] [role="columnheader"] {
            background: #f9fafb !important;
            color: #374151 !important;
        }

        div[data-testid="stDataFrame"] [role="gridcell"] {
            background: white !important;
            color: #1f2937 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )