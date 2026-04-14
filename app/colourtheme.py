import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5f7fb;
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
        }

        h1, h2, h3 {
            color: #1f2937;
            font-weight: 700;
        }

        p, label, div {
            color: #1f2937;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem;
        }

        div[data-testid="stDataFrame"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
        }

        table {
            background-color: white !important;
            color: #1f2937 !important;
        }

        thead tr th {
            background-color: #f9fafb !important;
            color: #374151 !important;
        }

        tbody tr td {
            background-color: white !important;
            color: #1f2937 !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            color: #1f2937 !important;
        }

        div[data-testid="stDateInput"] input,
        div[data-testid="stTextInput"] input {
            color: #1f2937 !important;
        }

        div[data-testid="stSlider"] * {
            color: #1f2937 !important;
        }

        button[kind="secondary"] {
            background: transparent;
            border: none;
            color: #374151;
            font-weight: 500;
            border-radius: 8px;
        }

        button[kind="secondary"]:hover {
            background: #e5e7eb;
        }

        .custom-logo {
            background: #005eb8;
            color: white;
            padding: 8px 14px;
            font-weight: 700;
            border-radius: 4px;
            display: inline-block;
        }

        .footer-text {
            text-align: center;
            color: #6b7280;
            margin-top: 2rem;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )