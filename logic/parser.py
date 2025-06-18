# parser.py
# Contains logic to detect document types (e.g., attendance, invoice) based on DataFrame content.
# Used by backend to classify uploaded documents for specialized processing.

def detect_document_type(df):
    # Try to fix rows where header is duplicated
    df = df.dropna(how="all")  # remove fully empty rows

    cols = [str(col).lower().strip() for col in df.columns]
    attendance_keywords = [
        "student", "present", "absent", "p", "a", "attendance", "roll", "name", "employee", "reg no", "register", "roll no", "rollno", "enrollment", "attended", "total classes", "attendance %", "attendance%", "attn", "att.", "attd", "attnd", "attendence"
    ]
    # Require at least two different attendance keywords in columns
    col_matches = set()
    for col in cols:
        for key in attendance_keywords:
            if key in col:
                col_matches.add(key)
    # At least 2 attendance keywords in columns, at least 3 columns, and at least 50% of columns are attendance keywords
    if len(col_matches) >= 2 and len(df.columns) >= 3 and (len(col_matches) / len(df.columns)) >= 0.5 and len(df) >= 2:
        return "attendance"

    # Invoice detection (as before)
    sample_text = " ".join(str(val).lower() for val in df.head(10).values.flatten())
    if any(col in ["item", "product", "description"] for col in cols) and (
        any("price" in col or "cost" in col for col in cols)
        or any(word in sample_text for word in ["rs", "₹", "$", "price", "total"])
    ):
        return "invoice"

    return "unknown"
