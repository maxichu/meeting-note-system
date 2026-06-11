import streamlit as st
from analyze import extract_speakers, extract_action_items, extract_action_items_with_owners
from db import init_db, save_meeting, get_all_meetings, save_speakers, get_speakers_by_meeting, save_action_items, get_action_items_by_meeting

st.set_page_config(page_title="Meeting Intelligence Assistant", page_icon="棣冩憫")
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
        speaker_counts = extract_speakers(text_to_save.strip())
        save_speakers(meeting_id, speaker_counts)
        action_items = extract_action_items_with_owners(text_to_save.strip())
        save_action_items(meeting_id, action_items)
        st.success(f"Meeting notes saved successfully! (ID: {meeting_id})")



st.markdown("---")
st.subheader("Meeting History")

meetings = get_all_meetings()
if not meetings:
    st.info("No meeting notes saved yet. Use the form above to add one.")
else:
    for meeting in meetings:
        with st.expander(f"Meeting #{meeting['id']} - {meeting['created_at']}"):
            st.text(meeting['raw_text'])

            speakers = get_speakers_by_meeting(meeting['id'])
            if speakers:
                st.markdown('**Speakers:**')
                for s in speakers:
                    st.write(f"{s['name']} -> {s['statement_count']}")

            items = get_action_items_by_meeting(meeting['id'])
            if items:
                st.markdown('**Action Items:**')
                for n, a in enumerate(items, 1):
                    owner = a['owner'] if a['owner'] else 'Unassigned'
                    st.write(f"{n}. {a['text']}")
                    st.write(f"   Owner: {owner}")
