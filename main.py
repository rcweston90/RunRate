import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.visualizations import VisualizationManager
from utils.category_manager import CategoryManager
import io

# Initialize managers
data_processor = DataProcessor()
viz_manager = VisualizationManager()
category_manager = CategoryManager()

# Set page config
st.set_page_config(
    page_title="Financial Data Analysis",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None

# Title and description
st.title("Financial Data Analysis Platform")
st.markdown("""
Upload your financial data to analyze spending patterns and manage categories.
Supported formats: CSV, Excel, TXT (comma or tab-delimited)
""")

# File upload section
uploaded_file = st.file_uploader(
    "Upload your financial data file",
    type=['csv', 'xlsx', 'xls', 'txt']
)

if uploaded_file is not None:
    # Process uploaded file
    df, message = data_processor.process_upload(uploaded_file)
    
    if df is not None:
        st.session_state.df = df
        st.success("File uploaded successfully!")
    else:
        st.error(message)

# Main analysis section
if st.session_state.df is not None:
    # Categorize transactions
    if 'categorized' not in st.session_state:
        st.session_state.df = data_processor.categorize_transactions(st.session_state.df)
        st.session_state.categorized = True
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Analysis", "Transactions", "Category Management"])
    
    with tab1:
        # Summary metrics
        summary = data_processor.get_spending_summary(st.session_state.df)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Spent", f"${summary['total_spent']:,.2f}")
        with col2:
            st.metric("Number of Transactions", summary['transaction_count'])
        with col3:
            st.metric("Date Range", f"{summary['date_range'][0]} to {summary['date_range'][1]}")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                viz_manager.create_spending_pie_chart(st.session_state.df),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                viz_manager.create_category_bar_chart(st.session_state.df),
                use_container_width=True
            )
        
        st.plotly_chart(
            viz_manager.create_spending_trend_line(st.session_state.df),
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Transaction Details")
        
        # Category filter
        selected_category = st.selectbox(
            "Filter by Category",
            ["All"] + category_manager.get_all_categories()
        )
        
        # Filter and display transactions
        filtered_df = st.session_state.df
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        
        # Display editable dataframe
        st.dataframe(
            filtered_df[['Date', 'Description', 'Amount', 'Category']],
            hide_index=True
        )
        
        # Export button
        if st.button("Export Data"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="processed_transactions.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.subheader("Category Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Add New Category")
            new_category = st.text_input("Category Name")
            new_keywords = st.text_input("Keywords (comma-separated)")
            
            if st.button("Add Category"):
                if new_category and new_keywords:
                    category_manager.add_category(
                        new_category,
                        [k.strip() for k in new_keywords.split(",")]
                    )
                    st.success(f"Added category: {new_category}")
        
        with col2:
            st.write("Add Keywords to Existing Category")
            existing_category = st.selectbox(
                "Select Category",
                category_manager.get_all_categories()
            )
            new_keyword = st.text_input("New Keyword")
            
            if st.button("Add Keyword"):
                if new_keyword:
                    if category_manager.add_keyword(existing_category, new_keyword.strip()):
                        st.success(f"Added keyword to {existing_category}")
                    else:
                        st.error("Failed to add keyword")

else:
    st.info("Please upload a file to begin analysis")
