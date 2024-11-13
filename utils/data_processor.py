import pandas as pd
import json
from typing import Dict, List, Tuple
import os

class DataProcessor:
    def __init__(self):
        self.categories = self._load_default_categories()
        
    def _load_default_categories(self) -> Dict:
        with open('assets/default_categories.json', 'r') as f:
            return json.load(f)['categories']
    
    def process_upload(self, uploaded_file) -> Tuple[pd.DataFrame, str]:
        """Process uploaded file and return DataFrame with basic validation"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                # Try reading as CSV first (comma-separated)
                try:
                    df = pd.read_csv(uploaded_file, sep=',')
                except:
                    # If comma-separated fails, try tab-separated
                    try:
                        df = pd.read_csv(uploaded_file, sep='\t')
                    except Exception as e:
                        return None, "Error processing TXT file: File must be comma or tab-separated"
            else:
                return None, "Unsupported file format. Please upload CSV, Excel, or TXT file."
            
            # Ensure required columns exist
            required_columns = ['Date', 'Description', 'Amount']
            if not all(col in df.columns for col in required_columns):
                return None, "Missing required columns. File must contain: Date, Description, Amount"
            
            # Clean and prepare data
            df['Date'] = pd.to_datetime(df['Date'])
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df['Category'] = 'Uncategorized'
            
            return df, "Success"
        except Exception as e:
            return None, f"Error processing file: {str(e)}"
    
    def categorize_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Automatically categorize transactions based on description keywords"""
        df = df.copy()
        
        for category, keywords in self.categories.items():
            mask = df['Description'].str.lower().apply(
                lambda x: any(keyword in x for keyword in keywords)
            )
            df.loc[mask, 'Category'] = category
            
        return df
    
    def update_transaction_category(self, df: pd.DataFrame, index: int, new_category: str) -> pd.DataFrame:
        """Update category for a specific transaction"""
        df = df.copy()
        df.loc[index, 'Category'] = new_category
        return df
    
    def get_spending_summary(self, df: pd.DataFrame) -> Dict:
        """Generate spending summary statistics"""
        summary = {
            'total_spent': df['Amount'].sum(),
            'by_category': df.groupby('Category')['Amount'].sum().to_dict(),
            'transaction_count': len(df),
            'date_range': (df['Date'].min().strftime('%Y-%m-%d'), 
                         df['Date'].max().strftime('%Y-%m-%d'))
        }
        return summary
