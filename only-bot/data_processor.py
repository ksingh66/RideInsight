# data_processor.py

import pandas as pd
import os
from datetime import datetime

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
            self.summary.append(f"Successfully loaded data from: {self.csv_path}")
            self.summary.append(f"Dataset contains {len(self.df)} total bookings/rides.")
            self.summary.append(f"Columns present: {', '.join(self.df.columns)}\n")
        except Exception as e:
            self.summary.append(f"Error loading data: {str(e)}")
            raise
    
    def generate_basic_stats(self):
        """
        Generate basic statistical summaries for the Price column.
        This function specifically analyzes price data, providing key metrics
        that help understand the price distribution in the dataset.
        """
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
        missing = self.df.isnull().sum()
        if missing.any():
            self.summary.append("\nMissing Values Analysis:")
            for col, count in missing[missing > 0].items():
                percentage = (count / len(self.df)) * 100
                self.summary.append(f"{col}: {count} missing values ({percentage:.1f}%)")
    
    def generate_summary(self, output_file="data_summary.txt"):
        """
        Generate a complete summary of the dataset and save it to a file.
        
        Args:
            output_file (str): Name of the output file for the summary
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
            self.analyze_chauffer_earnings()  # Add the new analysis
            self.analyze_categories()
            
            # Write summary to file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, output_file)
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(self.summary))
            
            print(f"Summary successfully written to {output_path}")
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            raise

