import pandas as pd
import os

def load_document(file):
    filename = file.name
    ext = os.path.splitext(filename)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(file)
    elif ext == ".xlsx":
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")