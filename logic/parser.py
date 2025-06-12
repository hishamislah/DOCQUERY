def detect_document_type(df):
    # Try to fix rows where header is duplicated
    df = df.dropna(how="all")  # remove fully empty rows

    # Convert first two rows to check values
    sample_text = " ".join(str(val).lower() for val in df.head(5).values.flatten())
    cols = [str(col).lower().strip() for col in df.columns]

    if "student" in sample_text or "present" in sample_text or "absent" in sample_text or "p" in sample_text or "a" in sample_text:
        return "attendance"

    if any(col in ["item", "product", "description"] for col in cols) and (
        any("price" in col or "cost" in col for col in cols)
        or any(word in sample_text for word in ["rs", "₹", "$", "price", "total"])
    ):
        return "invoice"

    return "unknown"
