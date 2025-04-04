import streamlit as st
from utils.local.ingest import process_local_uploads
from utils.local.deduplication import prune_local_records

def handle_local_upload():
    if st.session_state.dataset_source != "Local Dataset":
        return

    st.sidebar.markdown("**Upload Your Images**")
    st.sidebar.info("Upload PNG, JPG, JPEG images (JSON optional).")

    uploaded_files = st.sidebar.file_uploader(
        "Select local image files",
        type=["png", "jpg", "jpeg", "json"],
        accept_multiple_files=True
    )

    if "uploaded_filenames" not in st.session_state:
        st.session_state.uploaded_filenames = set()
    if "skipped_uploads" not in st.session_state:
        st.session_state.skipped_uploads = []

    if uploaded_files:
        new_uploads = [f for f in uploaded_files if f.name not in st.session_state.uploaded_filenames]

        if new_uploads:
            result = process_local_uploads(new_uploads, force_rename=False)
            new_records = result["records"]
            skipped_names = result["skipped"]

            for f in new_uploads:
                st.session_state.uploaded_filenames.add(f.name)
            st.session_state.skipped_uploads = list(set(st.session_state.skipped_uploads + skipped_names))

            filtered = prune_local_records(new_records)
            st.session_state.local_records.extend(filtered)

            st.success(f"Uploaded {len(filtered)} file(s). Click 'LLM closed Q&A' to process.")
        else:
            st.info("No new files detected (already uploaded above).")

    if st.session_state.skipped_uploads:
        st.warning("Some files were already processed. Select which to rename and reprocess:")
        selected = st.multiselect(
            "Files to rename and re-upload:",
            st.session_state.skipped_uploads,
            key="reupload_selection"
        )

        if st.button("Force Upload Selected Duplicates"):
            to_force = [f for f in uploaded_files if f.name in selected]
            forced = process_local_uploads(to_force, force_rename=True)

            st.session_state.local_records = prune_local_records(st.session_state.local_records)
            st.session_state.local_records = forced["records"] + st.session_state.local_records

            for f in to_force:
                st.session_state.uploaded_filenames.add(f.name)

            st.session_state.skipped_uploads = [f for f in st.session_state.skipped_uploads if f not in selected]

            st.success(f"Renamed and uploaded {len(forced['records'])} file(s).")
