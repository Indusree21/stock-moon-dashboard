import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="🌙 Stock vs Moon Phases Dashboard 📈",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .moon-emoji {
        font-size: 3rem;
        text-align: center;
    }
    .insight-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2a5298;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Moon phases data
MOON_PHASES = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
MOON_NAMES = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 
              'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent']

@st.cache_data
def generate_stock_moon_data(days=30):
    """Generate stock and moon phase data"""
    data = []
    today = datetime.now()
    base_price = 145
    
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        
        # Calculate moon phase (simplified)
        days_since_new_moon = (date.timestamp() / (24 * 60 * 60)) % 29.5
        phase_index = int((days_since_new_moon / 29.5) * 8)
        
        # Generate price change with moon influence
        price_change = random.uniform(-4, 4)
        
        # Moon phase influence
        if phase_index == 4:  # Full moon - bullish
            price_change += random.uniform(0.5, 1.5)
        elif phase_index == 0:  # New moon - bearish
            price_change -= random.uniform(0.5, 1.2)
        
        base_price += price_change
        base_price = max(base_price, 100)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Price': round(base_price, 2),
            'Moon_Phase_Index': phase_index,
            'Moon_Emoji': MOON_PHASES[phase_index],
            'Moon_Name': MOON_NAMES[phase_index],
            'Price_Change': round(price_change, 2)
        })
    
    return pd.DataFrame(data)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌙 Stock Market Lunar Analysis 📈</h1>
        <p>Exploring the mystical connection between moon phases and market movements</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate data
    df = generate_stock_moon_data()
    latest_data = df.iloc[-1]
    previous_data = df.iloc[-2]
    
    # Sidebar controls
    st.sidebar.header("🎛️ Dashboard Controls")
    days_to_show = st.sidebar.slider("Days to Display", 7, 30, 30)
    show_moon_correlation = st.sidebar.checkbox("Show Moon Correlation", True)
    show_predictions = st.sidebar.checkbox("Show AI Predictions", True)
    
    # Filter data based on selection
    df_filtered = df.tail(days_to_show)
    
    # Current Status Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="moon-emoji">{latest_data['Moon_Emoji']}</div>
        <p style="text-align: center; font-weight: bold;">{latest_data['Moon_Name']}</p>
        """, unsafe_allow_html=True)
    
    with col2:
        price_change = latest_data['Price'] - previous_data['Price']
        price_change_pct = (price_change / previous_data['Price']) * 100
        st.metric(
            "Current Price", 
            f"${latest_data['Price']:.2f}",
            f"{price_change_pct:+.1f}%"
        )
    
    with col3:
        avg_return = df['Price_Change'].mean()
        st.metric(
            "Avg Daily Change",
            f"{avg_return:+.2f}%",
            "Last 30 days"
        )
    
    with col4:
        volatility = df['Price_Change'].std()
        st.metric(
            "Volatility",
            f"{volatility:.2f}%",
            "Standard Deviation"
        )
    
    # AI Prediction Box
    if show_predictions:
        price_trend = (latest_data['Price'] - previous_data['Price']) / previous_data['Price'] * 100
        
        if latest_data['Moon_Name'] == 'Full Moon':
            prediction = "🔮 AI predicts: High volume trading likely. Bullish sentiment expected."
        elif latest_data['Moon_Name'] == 'New Moon':
            prediction = "🔮 AI predicts: Volatile trading expected. Consider defensive positions."
        else:
            prediction = "🔮 AI predicts: Moderate market conditions. Watch for trends."
        
        st.info(f"**🤖 AI Prediction:** {prediction}")
    
    st.divider()
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Stock Price Trend")
        
        # Create stock price chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_filtered['Date'],
            y=df_filtered['Price'],
            mode='lines+markers',
            name='Stock Price',
            line=dict(color='#2a5298', width=3),
            hovertemplate='<b>Date:</b> %{x}<br>' +
                         '<b>Price:</b> $%{y:.2f}<br>' +
                         '<b>Moon:</b> %{customdata}<br>' +
                         '<extra></extra>',
            customdata=df_filtered['Moon_Name']
        ))
        
        if show_moon_correlation:
            # Add moon phase annotations
            for idx, row in df_filtered.iterrows():
                if idx % 3 == 0:  # Show every 3rd moon phase to avoid clutter
                    fig.add_annotation(
                        x=row['Date'],
                        y=row['Price'],
                        text=row['Moon_Emoji'],
                        showarrow=False,
                        yshift=20,
                        font=dict(size=16)
                    )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌙 Moon Phase Performance")
        
        # Calculate average returns by moon phase
        phase_performance = df.groupby('Moon_Name').agg({
            'Price_Change': ['mean', 'count']
        }).round(2)
        
        phase_performance.columns = ['Avg_Return', 'Count']
        phase_performance = phase_performance.reset_index()
        
        # Create bar chart
        fig = px.bar(
            phase_performance,
            x='Moon_Name',
            y='Avg_Return',
            color='Avg_Return',
            color_continuous_scale=['red', 'yellow', 'green'],
            title="Average Return by Moon Phase"
        )
        
        fig.update_layout(
            xaxis_title="Moon Phase",
            yaxis_title="Average Return (%)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Insights Section
    st.subheader("🔍 Correlation Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        full_moon_data = df[df['Moon_Name'] == 'Full Moon']
        full_moon_avg = full_moon_data['Price_Change'].mean()
        st.markdown(f"""
        <div class="insight-card">
            <h3>🌕 Full Moon Effect</h3>
            <p><strong>Average Return:</strong> {full_moon_avg:+.2f}%</p>
            <p>Historically shows {"bullish" if full_moon_avg > 0 else "bearish"} tendency</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        new_moon_data = df[df['Moon_Name'] == 'New Moon']
        new_moon_avg = new_moon_data['Price_Change'].mean()
        st.markdown(f"""
        <div class="insight-card">
            <h3>🌑 New Moon Effect</h3>
            <p><strong>Average Return:</strong> {new_moon_avg:+.2f}%</p>
            <p>Tends to show {"bullish" if new_moon_avg > 0 else "bearish"} sentiment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        quarter_phases = df[df['Moon_Name'].isin(['First Quarter', 'Last Quarter'])]
        quarter_avg = quarter_phases['Price_Change'].mean()
        st.markdown(f"""
        <div class="insight-card">
            <h3>🌓 Quarter Phases</h3>
            <p><strong>Average Return:</strong> {quarter_avg:+.2f}%</p>
            <p>Shows moderate {"positive" if quarter_avg > 0 else "negative"} performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Features
    st.subheader("⚡ Interactive Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎲 Predict Tomorrow"):
            next_phase_idx = random.randint(0, 7)
            next_price_change = random.uniform(-3, 3)
            
            if next_phase_idx == 4:  # Full moon
                next_price_change += 1.0
            
            next_price = latest_data['Price'] + next_price_change
            
            st.success(f"""
            **Tomorrow's Prediction:**
            - Price: ${next_price:.2f} ({next_price_change:+.1f}%)
            - Moon: {MOON_PHASES[next_phase_idx]} {MOON_NAMES[next_phase_idx]}
            """)
    
    with col2:
        if st.button("🌙 Best Moon Phase"):
            impact_analysis = {}
            for phase in MOON_NAMES:
                phase_data = df[df['Moon_Name'] == phase]
                if len(phase_data) > 0:
                    impact_analysis[phase] = phase_data['Price_Change'].mean()
            
            best_phase = max(impact_analysis, key=impact_analysis.get)
            
            st.info(f"""
            **Best Performing Phase:**
            {best_phase} ({impact_analysis[best_phase]:+.1f}% avg return)
            """)
    
    # Data Table
    with st.expander("📊 View Raw Data"):
        st.dataframe(
            df[['Date', 'Price', 'Moon_Name', 'Moon_Emoji', 'Price_Change']].tail(10),
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>📊 This dashboard is for entertainment purposes only. Not financial advice! 🌙</p>
        <p>Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()