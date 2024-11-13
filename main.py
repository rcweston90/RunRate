import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.visualizations import VisualizationManager
from utils.category_manager import CategoryManager
from utils.budget_manager import BudgetManager
import io

# Initialize managers
data_processor = DataProcessor()
viz_manager = VisualizationManager()
category_manager = CategoryManager()
budget_manager = BudgetManager()

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
    tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Transactions", "Category Management", "Budget Management"])
    
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
        
        # Budget progress chart
        st.plotly_chart(
            viz_manager.create_budget_progress_chart(st.session_state.df),
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
            
            # Show budget status if available
            budget_status = budget_manager.get_budget_status(
                selected_category,
                filtered_df['Amount'].sum()
            )
            if budget_status['has_budget']:
                st.info(f"""
                Budget Status for {selected_category}:
                - Budget: ${budget_status['budget_amount']:,.2f}
                - Spent: ${budget_status['spent']:,.2f}
                - Remaining: ${budget_status['remaining']:,.2f}
                - Used: {budget_status['percentage_used']:.1f}%
                """)
        
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
        
        # Create three columns for better organization
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("#### Add New Category")
            new_category = st.text_input("Category Name")
            new_keywords = st.text_input("Keywords (comma-separated)")
            
            if st.button("Add Category"):
                if new_category and new_keywords:
                    success, message = category_manager.add_category(
                        new_category,
                        [k.strip().lower() for k in new_keywords.split(",")]
                    )
                    if success:
                        st.success(message)
                        # Recategorize transactions with new category
                        st.session_state.df = data_processor.categorize_transactions(st.session_state.df)
                    else:
                        st.error(message)
        
        with col2:
            st.write("#### Manage Existing Categories")
            existing_category = st.selectbox(
                "Select Category",
                category_manager.get_all_categories()
            )
            
            # Show if it's a default category
            is_default = category_manager.is_default_category(existing_category)
            st.info("Default Category" if is_default else "Custom Category")
            
            # Show existing keywords
            st.write("Current Keywords:")
            keywords = category_manager.get_category_keywords(existing_category)
            for keyword in keywords:
                st.text(f"• {keyword}")
            
            # Remove category button (only for custom categories)
            if not is_default:
                if st.button("Remove Category"):
                    success, message = category_manager.remove_category(existing_category)
                    if success:
                        st.success(message)
                        # Reset selection to avoid errors
                        st.experimental_rerun()
                    else:
                        st.error(message)
        
        with col3:
            st.write("#### Manage Keywords")
            # Add keyword to existing category
            new_keyword = st.text_input("New Keyword")
            
            if st.button("Add Keyword"):
                if new_keyword:
                    success, message = category_manager.add_keyword(
                        existing_category,
                        new_keyword.strip()
                    )
                    if success:
                        st.success(message)
                        # Recategorize transactions with new keyword
                        st.session_state.df = data_processor.categorize_transactions(st.session_state.df)
                    else:
                        st.error(message)
            
            # Remove keyword
            keyword_to_remove = st.selectbox(
                "Select Keyword to Remove",
                category_manager.get_category_keywords(existing_category)
            )
            
            if st.button("Remove Keyword"):
                success, message = category_manager.remove_keyword(
                    existing_category,
                    keyword_to_remove
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    with tab4:
        st.subheader("Budget Management")
        
        # Create two columns for budget management
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Set Budget")
            budget_category = st.selectbox(
                "Select Category",
                category_manager.get_all_categories(),
                key="budget_category"
            )
            
            current_budget = budget_manager.get_budget(budget_category)
            budget_amount = st.number_input(
                "Budget Amount",
                min_value=0.0,
                value=float(current_budget['amount']) if current_budget else 0.0,
                step=10.0
            )
            
            budget_period = st.selectbox(
                "Budget Period",
                ["monthly", "yearly"],
                index=0 if not current_budget else ["monthly", "yearly"].index(current_budget['period'])
            )
            
            if st.button("Set Budget"):
                success, message = budget_manager.set_budget(
                    budget_category,
                    budget_amount,
                    budget_period
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        with col2:
            st.write("#### Current Budgets")
            budgets = budget_manager.get_all_budgets()
            
            if not budgets:
                st.info("No budgets set yet")
            else:
                for budget in budgets:
                    category = budget['category']
                    amount = budget['amount']
                    period = budget['period']
                    
                    st.write(f"**{category}**")
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"Amount: ${amount:,.2f}")
                    with col2:
                        st.write(f"Period: {period}")
                    with col3:
                        if st.button("Remove", key=f"remove_{category}"):
                            success, message = budget_manager.remove_budget(category)
                            if success:
                                st.success(message)
                                st.experimental_rerun()
                            else:
                                st.error(message)

else:
    st.info("Please upload a file to begin analysis")
