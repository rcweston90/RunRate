import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

class VisualizationManager:
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
