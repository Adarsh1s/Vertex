import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLOR_PALETTE = ["#6366F1", "#10B981", "#F59E0B", "#EC4899", "#06B6D4", "#8B5CF6"]

def draw_allocation_pie(summary_data):
    df = pd.DataFrame(summary_data)
    if 'total_percentage' not in df.columns or 'asset_class' not in df.columns or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No Allocation Data", font=dict(family="Outfit", size=16, color="#9CA3AF")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
    
    fig = px.pie(
        df, 
        values='total_percentage', 
        names='asset_class', 
        hole=0.55,
        color_discrete_sequence=COLOR_PALETTE
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        marker=dict(line=dict(color='#0B0F19', width=2))
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=12, color="#D1D5DB")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=30, l=10, r=10),
        font=dict(family="Outfit", color="#F9FAFB")
    )
    return fig

def draw_comparison_bar(compare_data):
    df = pd.DataFrame(compare_data)
    if 'model_name' not in df.columns or 'allocation_percentage' not in df.columns or 'asset_class' not in df.columns or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No Model Data", font=dict(family="Outfit", size=16, color="#9CA3AF")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
        
    fig = px.bar(
        df,
        x='model_name',
        y='allocation_percentage',
        color='asset_class',
        color_discrete_sequence=COLOR_PALETTE,
        barmode='stack',
        labels={'allocation_percentage': 'Allocation (%)', 'model_name': 'Risk Model', 'asset_class': 'Asset Class'}
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#E5E7EB"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=dict(font=dict(family="Outfit", size=13))),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=dict(font=dict(family="Outfit", size=13))),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=12, color="#D1D5DB")
        ),
        margin=dict(t=20, b=40, l=20, r=20)
    )
    return fig
