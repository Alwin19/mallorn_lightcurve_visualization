import os
import streamlit as st
from avocado import settings
from avocado.dataset import Dataset
import matplotlib.pyplot as plt

# -----------------------------
# CONFIGURATION
# -----------------------------
settings["data_directory"] = "./data"

@st.cache_resource
def load_dataset():
    # Loading the mallorn dataset
    return Dataset.load("mallorn_train")

st.set_page_config(page_title="Avocado Viewer", layout="wide")
st.title("🌌 Avocado Light Curve Viewer")

# -----------------------------
# LOAD DATASET
# -----------------------------
with st.spinner("Loading dataset..."):
    dataset = load_dataset()

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("Data Filtering")

# 1. Filter by Class OR true_class (mapped to SpecType)
# We map the UI label to the actual DataFrame column name
filter_options = {"None": None, "Class": "class", "SpecType": "true_class"}
selected_label = st.sidebar.radio("Filter by:", list(filter_options.keys()))
filter_column = filter_options[selected_label]

filtered_metadata = dataset.metadata

if filter_column:
    unique_vals = sorted(list(dataset.metadata[filter_column].unique()))
    selected_val = st.sidebar.selectbox(f"Select {selected_label}:", unique_vals)
    filtered_metadata = dataset.metadata[dataset.metadata[filter_column] == selected_val]

st.sidebar.divider()
st.sidebar.header("Object Selection")

# 2. Search Box Logic (Enhanced to sync with Index)
search_id = st.sidebar.text_input("Search by Object ID (e.g., '12345'):")

# Initialize the index we want to display
target_index = 0

if search_id:
    if search_id in filtered_metadata.index:
        # Find where this ID is in the CURRENT filtered list
        target_index = filtered_metadata.index.get_loc(search_id)
        st.sidebar.success(f"Found {search_id} at index {target_index}")
    else:
        st.sidebar.warning("ID not found in current filtered view.")

# 3. Synchronized Index Selection (Slider + Number Input)
max_idx = len(filtered_metadata) - 1

# If max_idx is -1 (empty filter), handle gracefully
if max_idx >= 0:
    idx_col1, idx_col2 = st.sidebar.columns([2, 1])
    
    with idx_col1:
        # The slider value is driven by target_index if search is used
        index_slider = st.slider("Index Slider", 0, max_idx, value=int(target_index))
    with idx_col2:
        index_num = st.number_input("Index #", 0, max_idx, value=index_slider)

    # Final Object ID determined by the synchronized inputs
    object_id = filtered_metadata.index[index_num]
else:
    st.error("No data matches the selected filters.")
    st.stop()

# Plot Settings
st.sidebar.divider()
st.sidebar.header("Plot Settings")
show_gp = st.sidebar.checkbox("Show Gaussian Process (GP)", value=True)
show_uncert = st.sidebar.checkbox("Show Uncertainties", value=True)

# -----------------------------
# DISPLAY METADATA & PLOT
# -----------------------------
obj = dataset.get_object(object_id=object_id)
metadata = obj.metadata

# Note: 'true_class' is treated as SpecType here
actual_class = metadata.get("class", "Unknown")
spec_type = metadata.get("true_class", "N/A")
host_specz = metadata.get("host_specz", "N/A")

st.markdown(f"### Currently Viewing: **{object_id}**")

# Using columns for a cleaner "Dashboard" look
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Class", actual_class)
m_col2.metric("SpecType (true_class)", spec_type)
m_col3.metric("Redshift (z)", f"{host_specz:.4f}" if isinstance(host_specz, float) else host_specz)

# Plotting the light curve
fig, ax = plt.subplots(figsize=(10, 6))
fig = obj.plot_light_curve(show_gp=show_gp, uncertainties=show_uncert, ax=ax)

st.pyplot(fig)