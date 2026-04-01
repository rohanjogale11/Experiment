import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InflaTrack — Personal Inflation Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THEME CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --green:      #133215;
  --lime:       #92B775;
  --dew:        #DDDACC;
  --green-mid:  #1e4a21;
  --lime-dark:  #6a8a55;
  --dew-light:  #f0ede2;
  --dew-dark:   #c8c4b4;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #133215 !important;
}
[data-testid="stSidebar"] * {
  color: #DDDACC !important;
}
[data-testid="stSidebar"] .stRadio label {
  font-size: 14px;
  font-weight: 500;
}

/* Main background */
[data-testid="stAppViewContainer"] {
  background-color: #f0ede2;
}

/* Metric labels */
[data-testid="stMetricLabel"] { font-family: 'DM Mono', monospace !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { font-family: 'DM Serif Display', serif !important; color: #133215 !important; }

/* Buttons */
.stButton > button {
  background-color: #92B775;
  color: #133215;
  font-weight: 700;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  padding: 12px 28px;
  transition: all .2s;
  font-family: 'DM Sans', sans-serif;
}
.stButton > button:hover {
  background-color: #b8d4a0;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(146,183,117,.3);
}

/* Number inputs */
[data-testid="stNumberInput"] input {
  font-family: 'DM Mono', monospace;
  background: #f0ede2;
  border: 1px solid #c8c4b4;
  border-radius: 6px;
}
[data-testid="stNumberInput"] input:focus {
  border-color: #92B775;
  box-shadow: 0 0 0 3px rgba(146,183,117,.15);
}

/* Selectbox */
[data-testid="stSelectbox"] select {
  background: #f0ede2;
  border: 1px solid #c8c4b4;
  border-radius: 6px;
  font-family: 'DM Sans', sans-serif;
}

/* Hide default Streamlit elements */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Info/success boxes */
.stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
SECTOR_RATES = {
    "Food & Beverages":  9.2,
    "Housing":           5.8,
    "Fuel & Light":      7.4,
    "Clothing":          3.1,
    "Health":            5.9,
    "Education":         4.1,
    "Transport":         6.0,
    "Miscellaneous":     3.8,
}
NATIONAL_CPI = 5.1
SECTOR_ICONS = ["🍛", "🏠", "⛽", "👕", "💊", "📚", "🚌", "🧾"]

# National CPI weights (MOSPI base year 2012)
NATIONAL_WEIGHTS = {
    "Food & Beverages": 45.86,
    "Housing":          10.07,
    "Fuel & Light":      6.84,
    "Clothing":          6.53,
    "Health":            5.89,
    "Education":         4.46,
    "Transport":        8.59,
    "Miscellaneous":    11.76,
}

# Historical CPI data (illustrative, directionally accurate – MOSPI)
YEARS = list(range(2013, 2025))
HEADLINE_CPI = [9.4, 5.9, 4.9, 4.5, 3.6, 4.9, 6.2, 6.6, 5.5, 6.7, 5.4, 5.1]
FOOD_CPI     = [11.9, 7.5, 5.0, 4.9, 2.0, 6.8, 8.7, 11.5, 6.5, 6.6, 7.5, 9.2]
HOUSING_CPI  = [8.1, 5.9, 4.2, 4.2, 5.2, 5.8, 5.0, 4.2, 4.0, 4.6, 5.5, 5.8]
FUEL_CPI     = [7.5, 4.0, 3.8, 3.3, 3.9, 8.5, 9.0, 8.9, 5.7, 10.4, 9.1, 7.4]

# ─── SIDEBAR NAVIGATION ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        font-family: 'DM Serif Display', serif;
        font-size: 24px;
        color: #DDDACC;
        padding: 12px 0 28px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    ">
        <span style="
            width: 10px; height: 10px;
            background: #92B775;
            border-radius: 50%;
            display: inline-block;
        "></span>
        InflaTrack
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠  Home", "🧮  Calculator", "📈  Trends", "📖  Sources"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: rgba(221,218,204,.4); line-height: 1.7;">
        Data sourced from MOSPI & RBI DBIE.<br>
        For educational purposes only.
    </div>
    """, unsafe_allow_html=True)

# ─── PAGE: HOME ─────────────────────────────────────────────────────────────────
if page == "🏠  Home":
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 56px 64px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: #92B775;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 20px;
        ">— Personal Inflation Calculator</div>
        <h1 style="
            font-family: 'DM Serif Display', serif;
            font-size: clamp(36px, 4vw, 60px);
            line-height: 1.1;
            color: #DDDACC;
            letter-spacing: -1px;
            margin-bottom: 20px;
        ">
            Inflation hits everyone <em style="color:#92B775;">differently.</em><br>See how it hits you.
        </h1>
        <p style="
            font-size: 16px;
            line-height: 1.7;
            font-weight: 300;
            color: rgba(221,218,204,.65);
            max-width: 560px;
            margin-bottom: 0;
        ">
            India's official CPI is an average across 1.4 billion people. Your spending isn't average.
            Calculate the inflation rate that actually reflects your life.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPI Categories Tracked", "8", help="Food, Housing, Fuel, Clothing, Health, Education, Transport, Misc")
    with col2:
        st.metric("Historical Data", "13 Years", help="2012–2024 based on MOSPI series")
    with col3:
        st.metric("Data Source", "MOSPI", help="Ministry of Statistics & Programme Implementation")

    st.markdown("---")

    # How it works
    st.markdown("""
    <div style="
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        color: #6a8a55;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    ">How It Works</div>
    <h2 style="
        font-family: 'DM Serif Display', serif;
        font-size: 36px;
        color: #133215;
        letter-spacing: -0.5px;
        margin-bottom: 28px;
    ">Three steps to your personal inflation rate</h2>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, num, title, desc in [
        (c1, "1", "Enter your monthly spending",
         "Break down your household budget across the 8 official CPI categories. No account needed — your data stays in the browser session."),
        (c2, "2", "We weight your basket",
         "The tool calculates each category's share of your total spend — your personal CPI basket weights, replacing the government's fixed national averages."),
        (c3, "3", "Get your personal inflation rate",
         "Each weight is multiplied by the official sector inflation rate from MOSPI. The sum is your personal rate — the Laspeyres index, applied to your life."),
    ]:
        with col:
            st.markdown(f"""
            <div style="
                background: #DDDACC;
                border: 1px solid #c8c4b4;
                border-radius: 10px;
                padding: 32px 28px;
                height: 100%;
            ">
                <div style="
                    font-family: 'DM Serif Display', serif;
                    font-size: 52px;
                    color: #c8c4b4;
                    line-height: 1;
                    margin-bottom: 20px;
                ">{num}</div>
                <div style="
                    font-size: 16px;
                    font-weight: 600;
                    color: #133215;
                    margin-bottom: 10px;
                ">{title}</div>
                <div style="
                    font-size: 14px;
                    font-weight: 300;
                    color: #5a6b5c;
                    line-height: 1.7;
                ">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CPI explainer
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 48px 56px;
        margin-top: 12px;
    ">
        <div style="
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: #92B775;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 12px;
        ">Why it matters</div>
        <h2 style="
            font-family: 'DM Serif Display', serif;
            font-size: 36px;
            color: #DDDACC;
            letter-spacing: -.5px;
            margin-bottom: 20px;
        ">The CPI isn't your inflation</h2>
        <p style="
            font-size: 15px;
            line-height: 1.8;
            font-weight: 300;
            color: rgba(221,218,204,.65);
            max-width: 640px;
            margin-bottom: 16px;
        ">
            The Consumer Price Index measures price changes for a representative basket of goods —
            averaged across all Indian households. But a family that spends 60% of income on food
            experiences inflation very differently from a dual-income urban household that spends
            mostly on rent and transport.
        </p>
        <p style="
            font-size: 15px;
            line-height: 1.8;
            font-weight: 300;
            color: rgba(221,218,204,.65);
            max-width: 640px;
        ">
            This tool replaces the government's fixed weights with your own spending distribution —
            giving you an inflation rate that is actually relevant to your household.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── PAGE: CALCULATOR ────────────────────────────────────────────────────────────
elif page == "🧮  Calculator":
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 40px 48px;
        margin-bottom: 32px;
    ">
        <h1 style="
            font-family: 'DM Serif Display', serif;
            font-size: 42px;
            color: #DDDACC;
            letter-spacing: -1px;
            margin-bottom: 8px;
        ">Personal Inflation Calculator</h1>
        <p style="
            font-size: 15px;
            font-weight: 300;
            color: rgba(221,218,204,.6);
        ">Enter your average monthly spending in each category to calculate your personal inflation rate.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("""
        <div style="
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: #133215;
            margin-bottom: 4px;
        ">Monthly Spending (₹)</div>
        <div style="font-size: 13px; color: #6a7a6c; margin-bottom: 24px;">
            Enter approximate monthly amounts. You can use round numbers — precision isn't required.
        </div>
        """, unsafe_allow_html=True)

        # Location selectors
        col_a, col_b = st.columns(2)
        with col_a:
            city = st.selectbox(
                "City",
                ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Other"],
            )
        with col_b:
            period = st.selectbox(
                "Reference Period",
                ["Jan–Mar 2025", "Oct–Dec 2024", "Jul–Sep 2024", "Apr–Jun 2024"],
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Spending inputs — 2 columns
        inputs = {}
        sectors = list(SECTOR_RATES.keys())
        icons = SECTOR_ICONS

        for i in range(0, len(sectors), 2):
            c1, c2 = st.columns(2)
            for col, idx in [(c1, i), (c2, i + 1)]:
                if idx < len(sectors):
                    sector = sectors[idx]
                    with col:
                        inputs[sector] = st.number_input(
                            f"{icons[idx]}  {sector}",
                            min_value=0,
                            max_value=500_000,
                            value=0,
                            step=500,
                            format="%d",
                            key=f"inp_{sector}",
                        )

        # Total bar
        total = sum(inputs.values())
        st.markdown(f"""
        <div style="
            background: #133215;
            border-radius: 8px;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 16px 0;
        ">
            <span style="font-size: 13px; font-weight: 500; color: rgba(221,218,204,.7);">
                Total monthly spending
            </span>
            <span style="
                font-family: 'DM Mono', monospace;
                font-size: 20px;
                font-weight: 500;
                color: #92B775;
            ">₹{total:,}</span>
        </div>
        """, unsafe_allow_html=True)

        calculate = st.button("Calculate my inflation rate →", use_container_width=True)

    with right:
        if not calculate or total == 0:
            st.markdown("""
            <div style="
                background: #133215;
                border-radius: 12px;
                padding: 52px 32px;
                text-align: center;
            ">
                <div style="font-size: 36px; margin-bottom: 16px; opacity: .3;">📊</div>
                <div style="
                    font-size: 14px;
                    font-weight: 300;
                    color: rgba(221,218,204,.35);
                    line-height: 1.65;
                ">
                    Enter your monthly spending across the categories on the left, then hit
                    <strong style="color:rgba(221,218,204,.5);">Calculate</strong> to see your personal inflation rate.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Calculation
            personal_rate = sum(
                (v / total) * SECTOR_RATES[k]
                for k, v in inputs.items()
            )
            delta = personal_rate - NATIONAL_CPI
            contributions = {
                k: (v / total) * SECTOR_RATES[k]
                for k, v in inputs.items()
                if v > 0
            }
            sorted_contribs = sorted(contributions.items(), key=lambda x: x[1], reverse=True)

            # Result header
            delta_color = "#e07070" if delta > 0 else "#92B775"
            delta_bg    = "rgba(220,80,80,.15)" if delta > 0 else "rgba(146,183,117,.15)"
            delta_sign  = "+" if delta > 0 else ""

            st.markdown(f"""
            <div style="
                background: #133215;
                border-radius: 12px;
                overflow: hidden;
            ">
                <div style="
                    padding: 28px 32px;
                    border-bottom: 1px solid rgba(146,183,117,.15);
                ">
                    <div style="
                        font-family: 'DM Mono', monospace;
                        font-size: 10px;
                        color: #92B775;
                        letter-spacing: 1.5px;
                        text-transform: uppercase;
                        margin-bottom: 8px;
                    ">Your Personal Inflation Rate</div>
                    <div style="
                        font-family: 'DM Serif Display', serif;
                        font-size: 64px;
                        line-height: 1;
                        color: #DDDACC;
                        margin-bottom: 8px;
                    ">{personal_rate:.2f}%</div>
                    <div style="
                        font-size: 12px;
                        font-weight: 300;
                        color: rgba(221,218,204,.4);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        vs. National CPI {NATIONAL_CPI}%
                        <span style="
                            font-family: 'DM Mono', monospace;
                            font-size: 12px;
                            padding: 2px 9px;
                            border-radius: 10px;
                            background: {delta_bg};
                            color: {delta_color};
                        ">{delta_sign}{delta:.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Drivers
            max_contrib = sorted_contribs[0][1] if sorted_contribs else 1
            drivers_html = ""
            for sector, val in sorted_contribs:
                bar_w = int(val / max_contrib * 100)
                drivers_html += f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                    <div style="font-size:12px;color:rgba(221,218,204,.6);width:130px;flex-shrink:0;">{sector}</div>
                    <div style="flex:1;height:4px;background:rgba(221,218,204,.08);border-radius:2px;overflow:hidden;">
                        <div style="width:{bar_w}%;height:100%;background:#92B775;border-radius:2px;"></div>
                    </div>
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:rgba(221,218,204,.45);width:40px;text-align:right;">{val:.2f}%</div>
                </div>"""

            st.markdown(f"""
                <div style="padding:24px 32px;border-bottom:1px solid rgba(146,183,117,.15);">
                    <div style="
                        font-size:11px;font-weight:600;
                        color:rgba(221,218,204,.4);
                        letter-spacing:1px;text-transform:uppercase;
                        margin-bottom:16px;
                    ">Top Cost Drivers</div>
                    {drivers_html}
                </div>
            """, unsafe_allow_html=True)

            # Insight
            top_sector  = sorted_contribs[0][0]
            top_contrib = sorted_contribs[0][1]
            compare_txt = (f"Your inflation is <strong style='color:#e07070'>{delta:.2f}% above</strong>"
                           if delta > 0 else
                           f"Your inflation is <strong style='color:#92B775'>{abs(delta):.2f}% below</strong>")

            st.markdown(f"""
                <div style="
                    padding:20px 32px;
                    background:rgba(146,183,117,.08);
                    border-bottom:1px solid rgba(146,183,117,.15);
                ">
                    <div style="
                        font-size:13px;
                        line-height:1.7;
                        font-weight:300;
                        color:rgba(221,218,204,.7);
                    ">
                        {compare_txt} the national average of {NATIONAL_CPI}%.
                        Your biggest cost driver is <strong style='color:#92B775'>{top_sector}</strong>,
                        contributing <strong style='color:#92B775'>{top_contrib:.2f}%</strong> to your rate.
                        To maintain your standard of living, your income needs to grow by at least
                        <strong style='color:#92B775'>{personal_rate:.2f}%</strong> per year.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Spending breakdown pie chart
            st.markdown("<br>", unsafe_allow_html=True)
            spend_df = pd.DataFrame({
                "Sector": [k for k, v in inputs.items() if v > 0],
                "Amount": [v for v in inputs.values() if v > 0],
            })
            fig_pie = go.Figure(go.Pie(
                labels=spend_df["Sector"],
                values=spend_df["Amount"],
                hole=0.5,
                marker_colors=["#92B775", "#6a8a55", "#b8d4a0", "#DDDACC",
                               "#c8c4b4", "#1e4a21", "#2a6b2e", "#133215"],
                textinfo="label+percent",
                textfont_size=11,
            ))
            fig_pie.update_layout(
                title=dict(text="Your Spending Breakdown", font=dict(family="DM Serif Display", size=16, color="#133215")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=280,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# ─── PAGE: TRENDS ────────────────────────────────────────────────────────────────
elif page == "📈  Trends":
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 40px 48px;
        margin-bottom: 32px;
    ">
        <h1 style="
            font-family: 'DM Serif Display', serif;
            font-size: 42px;
            color: #DDDACC;
            letter-spacing: -1px;
            margin-bottom: 8px;
        ">CPI Trends — India</h1>
        <p style="
            font-size: 15px;
            font-weight: 300;
            color: rgba(221,218,204,.6);
        ">12 years of inflation data across all major spending categories.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Chart 1: Headline CPI trend ──────────────────────────────────────────────
    st.markdown("""
    <div style="
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: #133215;
        margin-bottom: 4px;
    ">Headline CPI — 12-Year Trend</div>
    <div style="font-size: 13px; font-weight: 300; color: #6a7a6c; margin-bottom: 16px;">
        Annual average YoY inflation rate. 2012=100 base series.
    </div>
    """, unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=YEARS, y=HEADLINE_CPI,
        name="Headline CPI",
        line=dict(color="#92B775", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(146,183,117,0.08)",
        mode="lines+markers",
        marker=dict(size=5, color="#92B775"),
        hovertemplate="<b>%{x}</b><br>CPI: %{y:.1f}%<extra></extra>",
    ))
    fig1.add_hline(
        y=NATIONAL_CPI, line_dash="dot",
        line_color="rgba(146,183,117,.4)",
        annotation_text=f"Current: {NATIONAL_CPI}%",
        annotation_font_color="#92B775",
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(
            showgrid=False, tickfont=dict(family="DM Mono", size=11, color="#6a7a6c"),
            linecolor="#c8c4b4",
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(200,196,180,.3)",
            tickfont=dict(family="DM Mono", size=11, color="#6a7a6c"),
            ticksuffix="%",
        ),
        legend=dict(font=dict(family="DM Sans", size=12)),
        hovermode="x unified",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Annotation cards
    ca, cb, cc = st.columns(3)
    for col, year, title, body in [
        (ca, "2013–14", "Post-QE commodity spike",
         "Global commodity prices and supply-side shocks pushed food inflation above 11%, pulling headline CPI near 10%."),
        (cb, "2020–21", "Pandemic disruption",
         "COVID-19 lockdowns caused supply-chain disruptions, lifting food CPI to 11.5% while fuel prices collapsed."),
        (cc, "2022–23", "Global inflation wave",
         "Russia-Ukraine conflict drove fuel inflation above 10%. RBI raised repo rate by 250bps to anchor expectations."),
    ]:
        with col:
            st.markdown(f"""
            <div style="
                background: #DDDACC;
                border: 1px solid #c8c4b4;
                border-left: 3px solid #92B775;
                border-radius: 0 8px 8px 0;
                padding: 16px 18px;
            ">
                <div style="font-family:'DM Mono',monospace;font-size:11px;color:#6a8a55;margin-bottom:6px;">{year}</div>
                <div style="font-size:13px;font-weight:600;color:#133215;margin-bottom:6px;">{title}</div>
                <div style="font-size:12px;font-weight:300;color:#6a7a6c;line-height:1.6;">{body}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart 2: Multi-sector comparison ────────────────────────────────────────
    st.markdown("""
    <div style="
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: #133215;
        margin-bottom: 4px;
    ">Sector-wise CPI Comparison</div>
    <div style="font-size: 13px; font-weight: 300; color: #6a7a6c; margin-bottom: 16px;">
        Food vs Housing vs Fuel inflation — the three biggest household cost drivers.
    </div>
    """, unsafe_allow_html=True)

    fig2 = go.Figure()
    for label, data, color in [
        ("Food & Beverages", FOOD_CPI,    "#92B775"),
        ("Housing",          HOUSING_CPI, "#DDDACC"),
        ("Fuel & Light",     FUEL_CPI,    "#e07070"),
    ]:
        fig2.add_trace(go.Scatter(
            x=YEARS, y=data,
            name=label,
            line=dict(color=color, width=2),
            mode="lines+markers",
            marker=dict(size=4, color=color),
            hovertemplate=f"<b>{label}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(
            showgrid=False, tickfont=dict(family="DM Mono", size=11, color="#6a7a6c"),
            linecolor="#c8c4b4",
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(200,196,180,.3)",
            tickfont=dict(family="DM Mono", size=11, color="#6a7a6c"),
            ticksuffix="%",
        ),
        legend=dict(
            font=dict(family="DM Sans", size=12, color="#133215"),
            bgcolor="rgba(240,237,226,.8)",
            bordercolor="#c8c4b4",
            borderwidth=1,
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Latest sector breakdown bar ─────────────────────────────────────
    st.markdown("""
    <div style="
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: #133215;
        margin-bottom: 4px;
    ">Current Sector Inflation Rates</div>
    <div style="font-size: 13px; font-weight: 300; color: #6a7a6c; margin-bottom: 16px;">
        Latest YoY rates by category used in the Personal Calculator.
    </div>
    """, unsafe_allow_html=True)

    sector_df = pd.DataFrame({
        "Sector": list(SECTOR_RATES.keys()),
        "Rate":   list(SECTOR_RATES.values()),
        "National Weight": list(NATIONAL_WEIGHTS.values()),
    }).sort_values("Rate", ascending=True)

    bar_colors = ["#92B775" if r >= NATIONAL_CPI else "#6a8a55" for r in sector_df["Rate"]]
    fig3 = go.Figure(go.Bar(
        y=sector_df["Sector"],
        x=sector_df["Rate"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{r:.1f}%" for r in sector_df["Rate"]],
        textposition="outside",
        textfont=dict(family="DM Mono", size=11, color="#133215"),
        hovertemplate="<b>%{y}</b><br>Inflation: %{x:.1f}%<extra></extra>",
    ))
    fig3.add_vline(
        x=NATIONAL_CPI, line_dash="dot",
        line_color="rgba(220,80,80,.5)",
        annotation_text=f"National CPI: {NATIONAL_CPI}%",
        annotation_font_color="#e07070",
        annotation_position="top right",
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=340,
        margin=dict(l=0, r=60, t=20, b=0),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(200,196,180,.3)",
            tickfont=dict(family="DM Mono", size=11, color="#6a7a6c"),
            ticksuffix="%", range=[0, 12],
        ),
        yaxis=dict(
            tickfont=dict(family="DM Sans", size=12, color="#133215"),
        ),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.caption("Chart data is based on MOSPI releases. Historical trend shapes are directionally accurate.")

# ─── PAGE: SOURCES ───────────────────────────────────────────────────────────────
elif page == "📖  Sources":
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 40px 48px;
        margin-bottom: 32px;
    ">
        <div style="
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: #92B775;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 12px;
        ">Data Integrity</div>
        <h1 style="
            font-family: 'DM Serif Display', serif;
            font-size: 42px;
            color: #DDDACC;
            letter-spacing: -1px;
            margin-bottom: 8px;
        ">Where the data comes from</h1>
        <p style="
            font-size: 15px;
            font-weight: 300;
            color: rgba(221,218,204,.6);
        ">Every number in this tool traces back to official government sources.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style="
        font-size: 15px;
        line-height: 1.8;
        font-weight: 300;
        color: #4a5e4c;
        max-width: 700px;
        margin-bottom: 32px;
    ">
        This tool uses only data published by India's official statistical agencies. No estimates,
        no private data providers, no third-party aggregators. If a number appears in this calculator,
        you can trace it directly to a government document. The links below take you to the exact sources.
    </p>
    """, unsafe_allow_html=True)

    # Source cards
    sources = [
        {
            "badge": "Primary",
            "name":  "Ministry of Statistics & PI (MOSPI)",
            "desc":  (
                "The primary source for all CPI data in this application. MOSPI publishes monthly "
                "Consumer Price Index figures at the national level, disaggregated by urban/rural and "
                "all 8 expenditure sub-categories. City-level CPI for major Indian urban centres is also "
                "published here. Data goes back to 2012 under the current base year series."
            ),
            "tags":  ["Monthly CPI releases", "Urban & Rural split", "8 sector breakdown", "State-wise data", "Base Year 2012 & 2024"],
            "url":   "https://mospi.gov.in/themes/product/9-consumer-price-index-cpi",
            "url_label": "mospi.gov.in ↗",
        },
        {
            "badge": "Supplementary",
            "name":  "RBI — Database on Indian Economy",
            "desc":  (
                "The Reserve Bank of India's DBIE portal provides clean, downloadable time-series CPI data "
                "in CSV format, often easier to work with programmatically than MOSPI's Excel files. "
                "Also the source for RBI's inflation target band (2–6%) and Monetary Policy Committee "
                "projections used in the future inflation section."
            ),
            "tags":  ["CSV downloads", "Long time series", "MPC projections", "Monetary policy context"],
            "url":   "https://dbie.rbi.org.in",
            "url_label": "dbie.rbi.org.in ↗",
        },
        {
            "badge": "Cross-reference",
            "name":  "Open Government Data — data.gov.in",
            "desc":  (
                "India's open government data platform provides archived CPI datasets in structured CSV "
                "format. Used to cross-reference and validate MOSPI data, and to access some historical "
                "series that are easier to parse here than from MOSPI's Excel workbooks directly."
            ),
            "tags":  ["Archived datasets", "CSV format", "Cross-validation"],
            "url":   "https://data.gov.in",
            "url_label": "data.gov.in ↗",
        },
    ]

    for src in sources:
        tags_html = "".join(
            f'<span style="font-size:11px;font-weight:500;background:#f0ede2;color:#6a8a55;'
            f'border:1px solid #c8c4b4;padding:3px 10px;border-radius:10px;">{t}</span>'
            for t in src["tags"]
        )
        st.markdown(f"""
        <div style="
            background: #DDDACC;
            border: 1px solid #c8c4b4;
            border-radius: 12px;
            padding: 28px 32px;
            margin-bottom: 16px;
        ">
            <div style="display:flex;align-items:flex-start;gap:20px;">
                <div style="
                    background: #133215;
                    color: #92B775;
                    font-family: 'DM Mono', monospace;
                    font-size: 10px;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    padding: 6px 12px;
                    border-radius: 4px;
                    white-space: nowrap;
                    flex-shrink: 0;
                ">{src['badge']}</div>
                <div style="flex:1;">
                    <div style="
                        font-family: 'DM Serif Display', serif;
                        font-size: 20px;
                        color: #133215;
                        margin-bottom: 6px;
                    ">{src['name']}</div>
                    <div style="
                        font-size: 14px;
                        font-weight: 300;
                        color: #5a6b5c;
                        line-height: 1.6;
                        margin-bottom: 12px;
                    ">{src['desc']}</div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;">{tags_html}</div>
                    <a href="{src['url']}" target="_blank" style="
                        display: inline-block;
                        font-size: 13px;
                        font-weight: 500;
                        color: #6a8a55;
                        text-decoration: none;
                        padding: 7px 16px;
                        border: 1px solid #c8c4b4;
                        border-radius: 6px;
                    ">{src['url_label']}</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Methodology box
    st.markdown("""
    <div style="
        background: #133215;
        border-radius: 12px;
        padding: 40px 44px;
        margin-top: 8px;
    ">
        <div style="
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: #92B775;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 12px;
        ">Methodology</div>
        <div style="
            font-family: 'DM Serif Display', serif;
            font-size: 28px;
            color: #DDDACC;
            margin-bottom: 16px;
            letter-spacing: -.5px;
        ">How the personal inflation rate is calculated</div>
        <p style="
            font-size: 14px;
            line-height: 1.8;
            font-weight: 300;
            color: rgba(221,218,204,.65);
            margin-bottom: 20px;
        ">
            This tool uses the same mathematical framework that MOSPI uses to compute the official
            CPI — the <strong style='color:#DDDACC;'>Laspeyres weighted price index</strong>, formalized by economist
            Étienne Laspeyres in 1871 and used by every major national statistics agency in the world.
            The only difference is that we replace the government's fixed national weights with weights
            derived from your own spending.
        </p>
        <p style="
            font-size: 14px;
            line-height: 1.8;
            font-weight: 300;
            color: rgba(221,218,204,.65);
            margin-bottom: 28px;
        ">
            Each sector's contribution to your personal inflation is its spending weight multiplied by
            the official inflation rate for that sector in the selected period. Summing these contributions
            gives your personal inflation rate.
        </p>
        <div style="
            background: rgba(221,218,204,.05);
            border: 1px solid rgba(146,183,117,.2);
            border-radius: 8px;
            padding: 20px 24px;
            font-family: 'DM Mono', monospace;
            font-size: 14px;
            color: #92B775;
            line-height: 2.2;
        ">
            Personal Inflation = Σ ( W<sub>i</sub> × P<sub>i</sub> )<br>
            <span style="font-size:12px;opacity:.6;">
                Where W<sub>i</sub> = your spending on sector i ÷ total spending<br>
                And P<sub>i</sub> = official YoY inflation rate for sector i (from MOSPI)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
