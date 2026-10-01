import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Professional Financial Palette (Clean, High Contrast, Non-Neon)
COLOR_PALETTE = ["#2563EB", "#059669", "#D97706", "#4F46E5", "#0891B2", "#64748B"]

def draw_allocation_pie(summary_data):
    df = pd.DataFrame(summary_data)
    if 'total_percentage' not in df.columns or 'asset_class' not in df.columns or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No Allocation Data", font=dict(family="Outfit, sans-serif", size=15, color="#64748B")),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF"
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
        textfont=dict(family="Inter, sans-serif", size=12, color="#FFFFFF"),
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter, sans-serif", size=12, color="#334155")
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(t=20, b=30, l=10, r=10),
        font=dict(family="Outfit, sans-serif", color="#0F172A")
    )
    return fig

def draw_comparison_bar(compare_data):
    df = pd.DataFrame(compare_data)
    if 'model_name' not in df.columns or 'allocation_percentage' not in df.columns or 'asset_class' not in df.columns or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No Model Data", font=dict(family="Outfit, sans-serif", size=15, color="#64748B")),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF"
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
    fig.update_traces(
        texttemplate='%{y:.1f}%',
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#FFFFFF', size=11, family='Inter, sans-serif')
    )
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=360,
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        xaxis=dict(
            gridcolor="#E2E8F0", 
            title=dict(text="", font=dict(family="Outfit, sans-serif", size=13, color="#1E293B")),
            tickfont=dict(color="#1E293B", size=12, family="Outfit, sans-serif")
        ),
        yaxis=dict(
            gridcolor="#E2E8F0", 
            title=dict(text="Allocation (%)", font=dict(family="Outfit, sans-serif", size=12, color="#1E293B")),
            tickfont=dict(color="#334155", size=11),
            range=[0, 105]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter, sans-serif", size=11, color="#334155")
        ),
        margin=dict(t=40, b=30, l=40, r=20)
    )
    return fig

def draw_grouped_comparison_bar(compare_data):
    df = pd.DataFrame(compare_data)
    if 'model_name' not in df.columns or 'allocation_percentage' not in df.columns or 'asset_class' not in df.columns or df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="No Model Data", font=dict(family="Outfit, sans-serif", size=15, color="#64748B")),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF"
        )
        return fig
        
    fig = px.bar(
        df,
        x='asset_class',
        y='allocation_percentage',
        color='model_name',
        color_discrete_sequence=["#2563EB", "#059669"],
        barmode='group',
        labels={'allocation_percentage': 'Allocation (%)', 'model_name': 'Risk Model', 'asset_class': 'Asset Class'}
    )
    fig.update_traces(
        texttemplate='%{y:.1f}%',
        textposition='outside',
        textfont=dict(color='#0F172A', size=11, family='Inter, sans-serif')
    )
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=360,
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        xaxis=dict(
            gridcolor="#E2E8F0", 
            title=dict(text="", font=dict(family="Outfit, sans-serif", size=13, color="#1E293B")),
            tickfont=dict(color="#1E293B", size=12, family="Outfit, sans-serif")
        ),
        yaxis=dict(
            gridcolor="#E2E8F0", 
            title=dict(text="Allocation (%)", font=dict(family="Outfit, sans-serif", size=12, color="#1E293B")),
            tickfont=dict(color="#334155", size=11),
            range=[0, max(df['allocation_percentage'].max() * 1.25, 45) if not df.empty else 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter, sans-serif", size=11, color="#334155")
        ),
        margin=dict(t=40, b=30, l=40, r=20)
    )
    return fig
