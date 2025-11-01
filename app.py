import os
import streamlit as st
from avocado import settings
from avocado.dataset import Dataset
import matplotlib.pyplot as plt

# -----------------------------
# CONFIGURATION
# -----------------------------
settings["data_directory"] = "./data"

# Load dataset once
@st.cache_resource
def load_dataset():
    dataset = Dataset.load("mallorn_train")
    return dataset

st.title("🌌 Avocado Light Curve Viewer")
st.markdown("Interactively explore astronomical objects in the Mallorn training dataset.")

# -----------------------------
# LOAD DATASET
# -----------------------------
with st.spinner("Loading dataset..."):
    dataset = load_dataset()

# -----------------------------
# USER INPUT
# -----------------------------
# Get list of available object classes (metadata)
object_classes = [""] + sorted(list(dataset.metadata["class"].unique()))
selected_class = st.selectbox("Select object class:", object_classes)

# Filter by class if selected
if selected_class:
    class_data = dataset.metadata[dataset.metadata["class"] == selected_class]
else:
    class_data = dataset.metadata

# Index selector
index = st.slider("Select object index", 0, len(class_data) - 1, 0)

# -----------------------------
# DISPLAY PLOT
# -----------------------------
object_id = class_data.index[index]
obj = dataset.get_object(object_id=object_id)
# Extract metadata safely
metadata = obj.metadata
class_type = metadata.get("true_class", "Unknown")
host_specz = metadata.get("host_specz", "N/A")  # Redshift field
object_name = metadata.get("object_id", object_id)

st.markdown(
    f"### Class: **{class_type}**"
)

st.markdown(f"Object: **{object_name}**     /    Host Specz (z): **{host_specz}**")

fig, ax = plt.subplots(figsize=(10, 6))  # optional: set size
fig = obj.plot_light_curve(show_gp=True, uncertainties=True, ax=ax)

st.pyplot(fig)