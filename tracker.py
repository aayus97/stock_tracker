# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import logging
# from tenacity import retry, stop_after_attempt, wait_fixed
# import os
# from datetime import datetime
#
# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#
# class MeroLaganiStockTracker:
#     def __init__(self):
#         self.base_url = "https://merolagani.com"
#         self.history_file = "stock_history.csv"
#
#     # def get_stock_prices(self):
#     #     """
#     #     Scrapes stock prices from merolagani.com.
#     #     Returns:
#     #         pandas.DataFrame: Stock data with columns such as Symbol, LTP, etc.
#     #     """
#     #     try:
#     #         response = requests.get(f"{self.base_url}/LatestMarket.aspx")
#     #         response.raise_for_status()
#     #
#     #         soup = BeautifulSoup(response.text, 'html.parser')
#     #         table = soup.find("table", {"class": "table"})
#     #
#     #         if not table:
#     #             logging.error("Could not find the stock data table.")
#     #             return None
#     #
#     #         # Extract headers
#     #         headers = [th.text.strip() if th.text.strip() else "Unnamed" for th in table.find_all("th")]
#     #
#     #         # Handle duplicate headers
#     #         from collections import Counter
#     #         counts = Counter(headers)
#     #         headers = [
#     #             f"{header}_{i}" if counts[header] > 1 else header
#     #             for i, header in enumerate(headers)
#     #         ]
#     #
#     #         # Extract rows
#     #         rows = []
#     #         for tr in table.find_all("tr")[1:]:  # Skip the header row
#     #             row = [td.text.strip() for td in tr.find_all("td")]
#     #             if len(row) < len(headers):  # Handle missing columns
#     #                 row.extend([None] * (len(headers) - len(row)))
#     #             rows.append(row)
#     #
#     #         # Convert to DataFrame
#     #         stock_data = pd.DataFrame(rows, columns=headers)
#     #
#     #         # Clean and preprocess data
#     #         if "LTP" in stock_data.columns:
#     #             stock_data["LTP"] = pd.to_numeric(stock_data["LTP"].str.replace(",", ""), errors="coerce")
#     #         stock_data.dropna(subset=["Symbol", "LTP"], inplace=True)
#     #
#     #         return stock_data
#     #     except Exception as e:
#     #         logging.error(f"Error fetching stock prices: {e}")
#     #         return None
#
#     @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
#     def get_stock_prices(self):
#         """
#         Scrapes stock prices from merolagani.com.
#         """
#         try:
#             response = requests.get(f"{self.base_url}/LatestMarket.aspx")
#             response.raise_for_status()
#
#             soup = BeautifulSoup(response.text, 'html.parser')
#             table = soup.find("table", {"class": "table"})
#
#             if not table:
#                 logging.error("Could not find the stock data table.")
#                 return None
#
#             # Extract headers
#             headers = [th.text.strip() if th.text.strip() else "Unnamed" for th in table.find_all("th")]
#
#             # Handle duplicate headers
#             from collections import Counter
#             counts = Counter(headers)
#             headers = [
#                 f"{header}_{i}" if counts[header] > 1 else header
#                 for i, header in enumerate(headers)
#             ]
#
#             # Extract rows
#             rows = []
#             for tr in table.find_all("tr")[1:]:
#                 row = [td.text.strip() for td in tr.find_all("td")]
#                 if len(row) < len(headers):
#                     row.extend([None] * (len(headers) - len(row)))
#                 rows.append(row)
#
#             # Convert to DataFrame
#             stock_data = pd.DataFrame(rows, columns=headers)
#
#             # Add date column
#             stock_data['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#             # Clean data
#             if "LTP" in stock_data.columns:
#                 stock_data["LTP"] = pd.to_numeric(stock_data["LTP"].str.replace(",", ""), errors="coerce")
#             stock_data.dropna(subset=["Symbol", "LTP"], inplace=True)
#
#             return stock_data
#         except Exception as e:
#             logging.error(f"Error fetching stock prices: {e}")
#             return None
#
#     def track_stocks(self, stock_names):
#         """
#         Filter and track specific stocks from the scraped data.
#         """
#         stock_data = self.get_stock_prices()
#         if stock_data is not None and 'Symbol' in stock_data.columns:
#             tracked_data = stock_data[stock_data['Symbol'].isin(stock_names)]
#             return tracked_data
#         else:
#             logging.warning("No data available or 'Symbol' column missing.")
#             return None
#
#     def set_alert(self, stock_name, threshold, direction="up"):
#         """
#         Set alerts for specific stocks based on price threshold.
#         """
#         stock_data = self.track_stocks([stock_name])
#         if stock_data is not None and not stock_data.empty and 'LTP' in stock_data.columns:
#             try:
#                 current_price = float(stock_data['LTP'].iloc[0])
#                 if direction == "up" and current_price >= threshold:
#                     logging.info(f"ALERT: {stock_name} price has risen to {current_price}")
#                 elif direction == "down" and current_price <= threshold:
#                     logging.info(f"ALERT: {stock_name} price has dropped to {current_price}")
#             except ValueError:
#                 logging.error(f"Could not parse price for {stock_name}.")
#         else:
#             logging.warning(f"{stock_name} not found in the data or 'LTP' column missing.")
#
#     def save_to_history(self, stock_data):
#         """
#         Save stock data to a historical CSV file.
#         Appends to the file if it already exists.
#         """
#         try:
#             if os.path.exists(self.history_file):
#                 existing_data = pd.read_csv(self.history_file)
#                 combined_data = pd.concat([existing_data, stock_data], ignore_index=True)
#                 combined_data.to_csv(self.history_file, index=False)
#             else:
#                 stock_data.to_csv(self.history_file, index=False)
#             logging.info("Stock data saved to history.")
#         except Exception as e:
#             logging.error(f"Failed to save stock data to history: {e}")
#
#     def load_history(self):
#         """
#         Load the historical stock data from a CSV file.
#         """
#         try:
#             if os.path.exists(self.history_file):
#                 return pd.read_csv(self.history_file)
#             else:
#                 logging.warning("No historical data found.")
#                 return None
#         except Exception as e:
#             logging.error(f"Failed to load historical data: {e}")
#             return None


import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# Load email credentials from environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MeroLaganiStockTracker:
    def __init__(self):
        self.base_url = "https://merolagani.com"

    def get_stock_prices(self):
        """
        Scrapes stock prices from merolagani.com.
        """
        try:
            response = requests.get(f"{self.base_url}/LatestMarket.aspx")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", {"class": "table"})

            if not table:
                logging.error("Could not find the stock data table.")
                return None

            # Extract headers
            headers = [th.text.strip() if th.text.strip() else "Unnamed" for th in table.find_all("th")]

            # Handle duplicate headers
            from collections import Counter
            counts = Counter(headers)
            headers = [
                f"{header}_{i}" if counts[header] > 1 else header
                for i, header in enumerate(headers)
            ]

            # Extract rows
            rows = []
            for tr in table.find_all("tr")[1:]:
                row = [td.text.strip() for td in tr.find_all("td")]
                if len(row) < len(headers):
                    row.extend([None] * (len(headers) - len(row)))
                rows.append(row)

            # Convert to DataFrame
            stock_data = pd.DataFrame(rows, columns=headers)

            # Add date column
            stock_data['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Clean data
            if "LTP" in stock_data.columns:
                stock_data["LTP"] = pd.to_numeric(stock_data["LTP"].str.replace(",", ""), errors="coerce")
            stock_data.dropna(subset=["Symbol", "LTP"], inplace=True)

            return stock_data
        except Exception as e:
            logging.error(f"Error fetching stock prices: {e}")
            return None

    def send_email_alert(subject, body, recipient):
        """
        Function to send email alerts.
        """
        try:
            message = MIMEMultipart()
            message["From"] = EMAIL_USER
            message["To"] = recipient
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(EMAIL_USER, EMAIL_PASS)
                server.sendmail(EMAIL_USER, recipient, message.as_string())

            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

# Main Scheduler
if __name__ == "__main__":
    tracker = MeroLaganiStockTracker()
    stock_data = tracker.get_stock_prices()

    if stock_data is not None:
        # Save and email
        recipient_email = "paudelaayus@gmail.com"  # Replace with the recipient's email
        tracker.send_email_alert(stock_data, recipient_email)
    else:
        logging.error("No stock data available.")
