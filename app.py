import streamlit as st
from db import init_db, save_meeting

st.set_page_config(page_title="Meeting Intelligence Assistant", page_icon="📝")
st.title("Meeting Intelligence Assistant")

init_db()

st.markdown("Upload or type meeting notes below. Supported formats: **TXT**, **Markdown**, **PDF**.")

manual_text = st.text_area(
    "Type or paste meeting notes",
    height=250,
    placeholder=(
        "2026-06-10 Engineering Sync\n\n"
        "Alice:\n"
        "Search performance degraded after deployment.\n\n"
        "Bob:\n"
        "Root cause may be missing database index."
    ),
)

uploaded_file = st.file_uploader(
    "Or upload a file",
    type=["txt", "md", "pdf"],
    help="Accepted formats: .txt, .md, .pdf",
)

file_text = None
if uploaded_file is not None:
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            import pdfplumber

            with pdfplumber.open(uploaded_file) as pdf:
                file_text = "\n".join(
                    page.extract_text() or "" for page in pdf.pages
                )
            if not file_text.strip():
                st.error(
                    "Could not extract text from this PDF. "
                    "It may contain scanned images with no selectable text."
                )
                file_text = None
        else:
            file_text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        file_text = None

    if file_text is not None:
        with st.expander("Preview extracted text", expanded=True):
            preview = file_text[:1000]
            if len(file_text) > 1000:
                preview += "..."
            st.text(preview)

text_to_save = file_text if file_text is not None else manual_text

if st.button("Save Notes", type="primary"):
    if not text_to_save.strip():
        st.warning("Please enter or upload meeting notes before saving.")
    else:
        meeting_id = save_meeting(text_to_save.strip())
        st.success(f"Meeting notes saved successfully! (ID: {meeting_id})")
