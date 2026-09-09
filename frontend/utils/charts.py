import plotly.express as px
import pandas as pd

def draw_allocation_pie(summary_data):
    df = pd.DataFrame(summary_data)
    if 'total_percentage' not in df.columns or 'asset_class' not in df.columns:
        return px.pie(title="No Data")
    
    fig = px.pie(
        df, 
        values='total_percentage', 
        names='asset_class', 
        title='Asset Class Allocation',
        hole=0.4
    )
    return fig

def draw_comparison_bar(compare_data):
    df = pd.DataFrame(compare_data)
    if 'model_name' not in df.columns or 'allocation_percentage' not in df.columns or 'asset_class' not in df.columns:
        return px.bar(title="No Data")
        
    fig = px.bar(
        df,
        x='model_name',
        y='allocation_percentage',
        color='asset_class',
        title='Risk Model Comparison (Asset Class %)',
        barmode='stack'
    )
    return fig
