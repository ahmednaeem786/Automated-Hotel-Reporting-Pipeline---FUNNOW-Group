import pandas as pd


def process_hotel_data(file_path, test_email="abhu0013@student.monash.edu"):
    """
    Reads hotel data, calculates performance thresholds,
    and tags each hotel's performance status.
    """
    # Load the mock dataset
    df = pd.read_csv(file_path)

    # Calculate thresholds (using median to avoid possible skew from massive outliers)
    median_revenue = df["revenue"].median()
    median_orders = df["Order"].median()

    # Function to determine status for each row
    def determine_status(row):
        if row["revenue"] >= median_revenue and row["Order"] >= median_orders:
            return "Performing Well"
        elif row["revenue"] < median_revenue and row["Order"] < median_orders:
            return "Needs Improvement"
        else:
            return "Mixed Results"

    # New column storing performance status based on thresholds
    df["performance_status"] = df.apply(determine_status, axis=1)

    # Using personal email for testing purposes; in production, this would be replaced with the actual boss's email
    df["Boss Gmail"] = test_email

    return df, median_revenue, median_orders


# Quick test block to ensure it works when run directly
if __name__ == "__main__":
    # Ensure this matches the exact name of your downloaded CSV
    file_name = "data\`hotel-report_data_N8N_Mock_Data - Sheet1.csv"

    processed_df, revenue_threshold, order_thresh = process_hotel_data(file_name)

    print(f"Revenue Threshold (Median): ${revenue_threshold}")
    print(f"Order Threshold (Median): {order_thresh} bookings\n")
    print(processed_df[["brandname", "revenue", "Order", "performance_status"]])
