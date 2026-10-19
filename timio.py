
import csv
from datetime import date
from pathlib import Path

import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

APP_TITLE = "Daily Time Reporting"
CSV_FILE = Path(__file__).resolve().parent / "data.csv"

CATEGORIES = ["service","service_troubleshooting","admin", "new_dev", "self_dev", "external_meeting", "support", "maintenance"]

CSV_COLUMNS = ["label", "date", "hour", "owner"]


# --------------------------------------------------
# CSV saving
# --------------------------------------------------

def save_entries(selected_date, owner, values):
    """Append completed category entries to the CSV file."""

    rows = []

    for category, value in zip(CATEGORIES, values):
        value = value.strip()

        # Ignore empty fields and zero defaults.
        if value == "":
            continue

        # Only allow non-negative whole-number digits.
        if not value.isascii() or not value.isdecimal():
            raise ValueError(
                f"{category}: enter a whole number using digits only."
            )

        if value.strip("0") == "":
            continue

        rows.append({
            "label": category,
            "date": selected_date.isoformat(),
            "hour": value,
            "owner": owner.strip(),
        })

    if not rows:
        raise ValueError("Please enter at least one category value.")

    # Create the header if the file does not exist or is empty.
    file_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0

    with CSV_FILE.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)

    return len(rows)


def handle_save():
    """Save the current form values and reset category widgets on success."""

    owner = st.session_state["owner"]
    if not owner.strip():
        st.session_state["save_error"] = "Please enter an owner name."
        return

    values = [
        st.session_state[f"value_{category}"]
        for category in CATEGORIES
    ]

    try:
        count = save_entries(st.session_state["selected_date"], owner, values)
    except (ValueError, OSError) as error:
        st.session_state["save_error"] = str(error)
        return

    selected_date = st.session_state["selected_date"]
    st.session_state["save_success"] = (
        f"Saved {count} entr{'y' if count == 1 else 'ies'} "
        f"for {selected_date.isoformat()}."
    )
    for category in CATEGORIES:
        st.session_state[f"value_{category}"] = "0"


# --------------------------------------------------
# Streamlit interface
# --------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📝",
    layout="centered",
)

st.title("📝 Daily Time Reporting")
st.write(
    "Select a date, enter the hours for your categories, "
    "and save your entries."
)

# Initialize the date before creating the date widget.
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# Date picker and Today button.
date_col, today_col = st.columns([3, 1])

with today_col:
    st.write("")
    st.write("")
    if st.button("Today", use_container_width=True):
        st.session_state.selected_date = date.today()

with date_col:
    selected_date = st.date_input(
        "Select date",
        key="selected_date",
        format="YYYY-MM-DD",
    )

st.divider()

# Owner input.
owner = st.text_input(
    "Owner",
    value="Sima",
    placeholder="Enter your name",
    key="owner",
)

st.subheader("Category values")
st.caption("Categories default to 0 and are saved only when you enter a non-zero value.")

# Category input fields.
for category in CATEGORIES:
    st.text_input(
        f"{category}",
        value="0",
        key=f"value_{category}",
        placeholder="Enter a number",
    )

st.divider()

# Save button.
st.button(
    "Save entries",
    type="primary",
    use_container_width=True,
    on_click=handle_save,
)

if "save_error" in st.session_state:
    st.error(st.session_state.pop("save_error"))
if "save_success" in st.session_state:
    st.success(st.session_state.pop("save_success"))

# Show where the data is stored.
st.caption(f"Data file: {CSV_FILE.name}")

# Download a copy of the accumulated CSV.
if CSV_FILE.exists() and CSV_FILE.stat().st_size > 0:
    st.download_button(
        label="Download CSV file",
        data=CSV_FILE.read_bytes(),
        file_name="data.csv",
        mime="text/csv",
        use_container_width=True,
    )
