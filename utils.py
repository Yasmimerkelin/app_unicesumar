import streamlit as st


def add_logo(path):
    st.logo(image=path, icon_image=path)
    st.html("""
    <style>
        [alt=Logo] {
        height: 8rem;
        width: 8rem;
        display: block;
        margin-left: auto;
        margin-right: auto;
            
        }
    </style>
            """)


def apply_custom_styles():
    css_styles = """
    <style>
        h1 {
            margin-top: -3rem;
        }
    </style>
    """
    st.html(css_styles)


def customize_button_color():
    # Change color of st.button
    st.html("""
    <style>
            .row-widget.stButton > button {
            background-color: #c7141a;
            color: white;
            padding: -2.5rem -2rem;
            
        }
        .row-widget.stButton > button:hover {
            background-color: #493aa0;
            color: white;
        }
    </style>
    """)
