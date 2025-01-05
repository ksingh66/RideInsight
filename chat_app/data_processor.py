# data_processor.py

import pandas as pd
import os
from datetime import datetime
from .Chatbot import Chatbot

class DataSummarizer:
    def __init__(self, csv_path):
        """
        Initialize the DataSummarizer with a path to the CSV file.
        
        Args:
            csv_path (str): Path to the CSV file to analyze
        """
        # Convert the provided path to an absolute path
        self.csv_path = os.path.abspath(csv_path)
        self.df = None
        self.summary = []
        
        # Print the path information for debugging
        print(f"CSV path set to: {self.csv_path}")
        print(f"Current working directory: {os.getcwd()}")
    
    def load_data(self):
        """Load the CSV file into a pandas DataFrame."""
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(
                    f"CSV file not found at '{self.csv_path}'. "
                    f"Current working directory is '{os.getcwd()}'"
                )
            
            self.df = pd.read_csv(self.csv_path)
            
            column_names = self.df.columns.tolist()
            Standardizer = Chatbot()
            prompt = f"""You are a data standardization assistant that maps CSV column names to standardized versions for a luxury chauffeur service booking system while strictly maintaining the original order.
                        Input columns: {column_names}
                        Rules for standardization:
                        - The output list MUST maintain the exact same order as the input list
                        - Each output element corresponds to the input element at the same position
                        - Only use these exact standardized names:
                        "Booking" - for booking/reservation/confirmation numbers
                        "PAX" - for passenger/client/customer names
                        "Chauffer" - for driver/chauffer/operator names
                        "Pickup" - for pickup location/origin/start point
                        "Dropoff" - for dropoff/destination/end point
                        "Price" - for cost/fare/amount/price/rate
                        "Date" - for date/time/schedule information
                        "Notes" - for comments/remarks/special instructions/additional information
                        - If a column doesn't match any of these categories, keep it unchanged
                        - Return ONLY a Python list containing the standardized column names
                        - The list must be properly formatted with square brackets and quoted strings
                        - Do not include ANY explanatory text, just the Python list
                        - If there are more columns given to you than the standardized names, pick the ones most likely to fir the standardized names.
                        - Do not add new columns and do not reduce columns.
                        Example:
                        Input:  ["confirmation_number", "customer_name", "driver_name", "origin_address", "destination_address", "trip_fare", "pickup_time", "special_requests"]
                        Output: ["Booking", "PAX", "Chauffer", "Pickup", "Dropoff", "Price", "Date", "Notes"]

                        Standardize these columns:{column_names}"""

            try:
                standardized_columns = Standardizer.generate_response(prompt)
                # You'll need to parse this string response into a list
                standardized_columns = self.parse_llm_response(standardized_columns)
                # Then rename your DataFrame columns
                self.df.columns = standardized_columns  # Make sure this is a list!

                
                # Add to summary after successful standardization
                self.summary.append(f"Successfully loaded data from: {self.csv_path}")
                self.summary.append(f"Dataset contains {len(self.df)} total bookings/rides/calls.")
                self.summary.append(f"Columns standardized and present: {', '.join(self.df.columns)}\n")

            except Exception as e:
                print(f"Column standardization failed: {e}")
                # Continue with original column names
                self.summary.append("Column standardization failed - using original column names")
        except Exception as e:
            self.summary.append(f"Error loading data: {str(e)}")
            raise

    def parse_llm_response(self,response_string):
            """
            Parse the LLM's response string into a Python list of column names.
            
            Args:
                response_string (str): The raw response from the LLM
                
            Returns:
                list: A list of standardized column names
                
            Raises:
                ValueError: If the response can't be properly parsed into a list
            """
            try:
                # First, clean up the response string
                cleaned_response = response_string.strip()
                
                # Remove any extra whitespace or newlines
                cleaned_response = ' '.join(cleaned_response.split())
                
                # The response should start with '[' and end with ']'
                if not (cleaned_response.startswith('[') and cleaned_response.endswith(']')):
                    raise ValueError("Response is not in the expected list format")
                    
                # Remove the brackets
                content = cleaned_response[1:-1]
                
                # Split by commas and clean up each item
                columns = [
                    item.strip().strip('"\'')  # Remove quotes and whitespace
                    for item in content.split(',')
                    if item.strip()  # Skip empty items
                ]
                
                # Verify we have at least one column name
                if not columns:
                    raise ValueError("No column names found in response")
                    
                return columns
        
            except Exception as e:
                raise ValueError(f"Failed to parse LLM response: {str(e)}")
            
    def generate_basic_stats(self):
        """
        Generate basic statistical summaries for the Price column.
        This function specifically analyzes price data, providing key metrics
        that help understand the price distribution in the dataset.
        """
        # First, check if we have data to work with
        if self.df is None:
            print("Debug: Data not loaded yet. Please call load_data() first.")
            self.summary.append("\nWarning: Attempted to generate statistics before loading data.")
            return  # Exit the function early
        try:
            # Check if Price column exists in the DataFrame
            if 'Price' not in self.df.columns:
                self.summary.append("\nError: Price column not found in the dataset.")
                return
        except:
            print("PRICE NOT FOUND ERROR")
        # Calculate statistics for Price column
        price_stats = self.df['Price'].describe()
        
        # Add a section header for price analysis
        self.summary.append("\nPrice Analysis:")
        
        # Format currency values with commas for better readability
        self.summary.append(f"Average Price: ${price_stats['mean']:,.2f}")
        self.summary.append(f"Minimum Price: ${price_stats['min']:,.2f}")
        self.summary.append(f"Maximum Price: ${price_stats['max']:,.2f}")
        self.summary.append(f"Standard Deviation: ${price_stats['std']:,.2f}")
        
        # Add additional helpful statistics
        self.summary.append(f"Median Price: ${price_stats['50%']:,.2f}")
        
        # Calculate the number of items above average price
        above_average = len(self.df[self.df['Price'] > price_stats['mean']])
        percentage_above = (above_average / len(self.df)) * 100
        self.summary.append(f"\nPrice Distribution:")
        self.summary.append(f"{percentage_above:.1f}% of items are above the average price")
        
    def analyze_chauffer_earnings(self):
        """
        Analyze earnings per chauffer, calculating both average and total earnings.
        This analysis helps understand the distribution of earnings across different chauffers
        and identifies top performers in terms of revenue generation.
        """
        if self.df is None:
            print("Debug: Data not loaded yet. Please call load_data() first.")
            self.summary.append("\nWarning: Attempted to generate statistics before loading data.")
            return  # Exit the function early

        try:
            # Check if necessary columns exist
            if 'Chauffer' not in self.df.columns or 'Price' not in self.df.columns:
                self.summary.append("\nError: Required columns (Chauffer or Price) not found in the dataset.")
                return

            # Group by Chauffer and calculate statistics
            chauffer_stats = self.df.groupby('Chauffer').agg({
                'Price': ['count', 'mean', 'sum']
            }).round(2)

            # Rename columns for clarity
            chauffer_stats.columns = ['Total_Bookings', 'Average_Earning', 'Total_Earning']
            
            # Sort by total earnings in descending order
            chauffer_stats = chauffer_stats.sort_values('Total_Earning', ascending=False)

            # Add section                       header
            self.summary.append("\nChauffer Earnings Analysis:")
            
            # Add overall statistics
            total_company_earnings = chauffer_stats['Total_Earning'].sum()
            average_chauffer_earnings = chauffer_stats['Total_Earning'].mean()
            
            self.summary.append(f"\nCompany-wide Statistics:")
            self.summary.append(f"Total Company Earnings: ${total_company_earnings:,.2f}")
            self.summary.append(f"Average Earnings per Chauffer: ${average_chauffer_earnings:,.2f}")
            
            # Add individual chauffer statistics
            self.summary.append(f"\nIndividual Chauffer Performance:")
            for chauffer in chauffer_stats.index:
                stats = chauffer_stats.loc[chauffer]
                self.summary.append(f"\nChauffer: {chauffer}")
                self.summary.append(f"Total Bookings: {stats['Total_Bookings']}")
                self.summary.append(f"Average Earning per Booking: ${stats['Average_Earning']:,.2f}")
                self.summary.append(f"Total Earnings: ${stats['Total_Earning']:,.2f}")

            # Add performance insights
            top_earner = chauffer_stats.index[0]
            top_earning = chauffer_stats.loc[top_earner, 'Total_Earning']
            self.summary.append(f"\nPerformance Insights:")
            self.summary.append(f"Top earning chauffer: {top_earner} (${top_earning:,.2f})")
            
            # Calculate and add the percentage of total earnings for top performers
            top_3_earnings = chauffer_stats['Total_Earning'].head(3).sum()
            top_3_percentage = (top_3_earnings / total_company_earnings) * 100
            self.summary.append(f"Top 3 chauffers account for {top_3_percentage:.1f}% of total earnings")

        except Exception as e:
            self.summary.append(f"\nError analyzing chauffer earnings: {str(e)}")
   
    def analyze_categories(self):
        """Analyze categorical columns and their distributions."""
        if self.df is None:
            print("Debug: Data not loaded yet. Please call load_data() first.")
            self.summary.append("\nWarning: Attempted to generate statistics before loading data.")
            return  # Exit the function early
        
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            total_count = len(self.df)
            
            self.summary.append(f"\nDistribution for {col}:")
            for value, count in value_counts.head(6).items():
                percentage = (count / total_count) * 100
                self.summary.append(f"{value}: {count} ({percentage:.1f}%)")
            
            if len(value_counts) > 5:
                self.summary.append(f"... and {len(value_counts) - 6} more unique values")
    
    def check_missing_values(self):
        """Analyze missing values in the dataset."""
        if self.df is None:
            print("Debug: Data not loaded yet. Please call load_data() first.")
            self.summary.append("\nWarning: Attempted to generate statistics before loading data.")
            return  # Exit the function early
        missing = self.df.isnull().sum()
        if missing.any():
            self.summary.append("\nMissing Values Analysis:")
            for col, count in missing[missing > 0].items():
                percentage = (count / len(self.df)) * 100
                self.summary.append(f"{col}: {count} missing values ({percentage:.1f}%)")
    def analyze_notes(self):
        """Analyze the each ride that contained notes"""
        if self.df is None:
            print("Debug: Data not loaded yet. Please call load_data() first.")
            self.summary.append("\nWarning: Attempted to generate statistics before loading data.")
            return  # Exit the function early
        
        # Check if Notes column exists
        if 'Notes' not in self.df.columns:
            self.summary.append("\nError: Notes column not found in the dataset.")
            return
        
        # Filter rows that have non-null and non-empty notes
        notes_df = self.df[
            self.df['Notes'].notna() & 
            (self.df['Notes'].str.strip() != '')
        ]

        # Add section header
        self.summary.append("\nDetailed Notes Analysis:")
        self.summary.append(f"Total rides with notes: {len(notes_df)}")
        self.summary.append(f"Percentage of rides with notes: {(len(notes_df) / len(self.df)) * 100:.1f}%\n")

        # Analyze each ride with notes
        for idx, row in notes_df.iterrows():
            self.summary.append(f"\nRide Details ({idx + 1}):")
            # Add all available information for the ride
            for column in self.df.columns:
                if pd.notna(row[column]) and str(row[column]).strip():
                    self.summary.append(f"{column}: {row[column]}")

            # Add a separator between rides
            self.summary.append("-" * 50)
        
        
    def generate_summary(self, output_file):
        """
        Generate a complete summary of the dataset and save it to a file.
        
        Args:
            output_file (str): Full path where the summary should be saved
        """
        try:
            # Clear any existing summary
            self.summary = []
            
            # Add timestamp
            self.summary.append(f"Data Analysis Summary")
            self.summary.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Perform all analyses
            self.load_data()
            self.check_missing_values()
            self.generate_basic_stats()
            self.analyze_chauffer_earnings()
            self.analyze_categories()
            self.analyze_notes()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write summary to file using the provided path
            with open(output_file, 'w') as f:
                f.write('\n'.join(self.summary))
            
            print(f"Summary successfully written to {output_file}")
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            raise
