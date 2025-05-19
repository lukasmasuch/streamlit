import streamlit as st

st.title("Dropdown Button Example")

# Basic usage
st.header("Basic usage")
action = st.dropdown_button("Open Menu", options=["Item One", "Item Two", "Item Three"])
st.write("Selected:", action)

if action == "Item One":
    st.write("You selected Item One!")
elif action == "Item Two":
    st.write("You selected Item Two!")
elif action == "Item Three":
    st.write("You selected Item Three!")

# Advanced usage
st.header("Advanced usage")

# File menu example
st.subheader("File menu")
file_options = ["Save", "Save As", "Export"]
file_action = st.dropdown_button("File", options=file_options, type="primary", icon=":material/file:")

if file_action:
    st.success(f"Selected: {file_action}")
    
    if file_action == "Export":
        file_type = st.selectbox("Export as:", ["PDF", "HTML", "Plain Text"])
        st.write(f"Exporting as {file_type}...")
        
# Settings menu example
st.subheader("Settings menu with emoji icon")
settings_options = ["Profile", "Preferences", "Logout"]
settings_action = st.dropdown_button("Settings", options=settings_options, icon="⚙️", type="secondary")

if settings_action:
    st.info(f"Opening {settings_action}...")
    
# More examples
st.header("More styling options")
col1, col2, col3 = st.columns(3)

with col1:
    primary = st.dropdown_button("Primary", options=["Option 1", "Option 2"], type="primary")
    st.caption("Primary style")
    
with col2:
    secondary = st.dropdown_button("Secondary", options=["Option 1", "Option 2"], type="secondary")
    st.caption("Secondary style (default)")
    
with col3:
    tertiary = st.dropdown_button("Tertiary", options=["Option 1", "Option 2"], type="tertiary")
    st.caption("Tertiary style")
    
# Full width example
st.header("Full width dropdown button")
fw_action = st.dropdown_button(
    "Full Width Menu", 
    options=["Item 1", "Item 2", "Item 3"],
    use_container_width=True
)
st.write("Selected:", fw_action)

# Disabled button example
st.header("Disabled dropdown button")
st.dropdown_button("Disabled Menu", options=["Can't click this"], disabled=True)