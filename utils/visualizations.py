import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from utils.budget_manager import BudgetManager

class VisualizationManager:
    def __init__(self):
        self.budget_manager = BudgetManager()
    
    def create_spending_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create pie chart of spending by category"""
        category_sums = df.groupby('Category')['Amount'].sum()
        
        fig = px.pie(
            values=category_sums.values,
            names=category_sums.index,
            title='Spending Distribution by Category',
            template='seaborn'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def create_spending_trend_line(self, df: pd.DataFrame) -> go.Figure:
        """Create line chart of spending over time"""
        daily_spending = df.groupby('Date')['Amount'].sum().reset_index()
        
        fig = px.line(
            daily_spending,
            x='Date',
            y='Amount',
            title='Daily Spending Trend',
            template='seaborn'
        )
        fig.update_layout(showlegend=False)
        return fig
    
    def create_category_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create bar chart of spending by category"""
        category_sums = df.groupby('Category')['Amount'].sum().sort_values(ascending=True)
        
        fig = px.bar(
            x=category_sums.values,
            y=category_sums.index,
            orientation='h',
            title='Spending by Category',
            template='seaborn'
        )
        fig.update_layout(
            xaxis_title='Total Amount',
            yaxis_title='Category',
            showlegend=False
        )
        return fig
    
    def create_budget_progress_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create budget progress chart showing spending vs budget for each category"""
        category_spending = df.groupby('Category')['Amount'].sum()
        budgets = self.budget_manager.get_all_budgets()
        
        categories = []
        spent_amounts = []
        budget_amounts = []
        percentages = []
        
        for budget in budgets:
            category = budget['category']
            if category in category_spending:
                spent = float(category_spending[category])
                budget_amount = float(budget['amount'])
                percentage = min((spent / budget_amount * 100), 100) if budget_amount > 0 else 100
                
                categories.append(category)
                spent_amounts.append(spent)
                budget_amounts.append(budget_amount)
                percentages.append(percentage)
        
        fig = go.Figure()
        
        # Add budget bars
        fig.add_trace(go.Bar(
            name='Budget',
            x=categories,
            y=budget_amounts,
            marker_color='lightgrey'
        ))
        
        # Add spending bars
        fig.add_trace(go.Bar(
            name='Spent',
            x=categories,
            y=spent_amounts,
            marker_color=['red' if p > 100 else 'green' for p in percentages]
        ))
        
        fig.update_layout(
            title='Budget vs Spending by Category',
            barmode='overlay',
            yaxis_title='Amount',
            template='seaborn'
        )
        
        return fig
    
    def create_category_comparison_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create comparison bar chart for categories across files"""
        fig = go.Figure()
        
        for column in df.columns:
            fig.add_trace(go.Bar(
                name=column,
                x=df.index,
                y=df[column],
                text=df[column].round(2),
                textposition='auto',
            ))
        
        fig.update_layout(
            title='Category-wise Spending Comparison',
            barmode='group',
            xaxis_title='Category',
            yaxis_title='Amount',
            template='seaborn',
            showlegend=True,
            legend_title='Files'
        )
        
        return fig
    
    def create_trend_comparison_chart(self, dfs: List[pd.DataFrame], labels: List[str]) -> go.Figure:
        """Create comparison line chart for spending trends across files"""
        fig = go.Figure()
        
        for df, label in zip(dfs, labels):
            daily_spending = df.groupby('Date')['Amount'].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=daily_spending['Date'],
                y=daily_spending['Amount'],
                mode='lines+markers',
                name=label
            ))
        
        fig.update_layout(
            title='Spending Trend Comparison',
            xaxis_title='Date',
            yaxis_title='Amount',
            template='seaborn',
            showlegend=True,
            legend_title='Files'
        )
        
        return fig
