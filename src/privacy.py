"""
Privacy Utilities
-----------------
Provides anonymization for datasets.
"""

def anonymize(df):
    """
    Hash customer identifiers to remove PII.
    """

    df["customer_id"] = (
        df["customer_id"]
        .astype(str)
        .apply(hash)
    )

    return df