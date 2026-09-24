import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import altair as alt

from src.ai.copilot import ask_copilot
from src.analytics.business_metrics import (
    get_business_kpis,
    get_monthly_sales,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Business Intelligence Copilot",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    .info-card {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">📊 AI Business Intelligence Copilot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Ask natural-language questions about your e-commerce business
    and get answers powered by verified PostgreSQL analytics.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("🤖 AI Copilot")

    st.markdown(
        """
        **Qwen 2.5 7B**

        ↓

        **Verified Analytics Tools**

        ↓

        **PostgreSQL**

        ↓

        **Business Insights**
        """
    )

    st.divider()

    st.subheader("💡 Try asking")

    st.markdown(
        """
        - What is our total revenue?
        - Which country generates the most revenue?
        - What are our top 5 products?
        - Which customers generate the most revenue?
        - Which months had the biggest revenue declines?
        - What is our profit margin?
        """
    )

    st.divider()

    st.caption("Data source: UCI Online Retail II")
    st.caption("LLM: Qwen 2.5 7B via Ollama")
    st.caption("Database: PostgreSQL")


# ---------------------------------------------------------
# LIVE BUSINESS KPIs
# ---------------------------------------------------------

try:

    kpi_data = get_business_kpis()

    if hasattr(kpi_data, "iloc"):
        kpi = kpi_data.iloc[0]

        total_revenue = float(kpi["total_revenue"])
        total_orders = int(kpi["total_orders"])
        total_customers = int(kpi["total_customers"])
        average_order_value = float(
            kpi["average_order_value"]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💰 Total Revenue",
                f"£{total_revenue / 1_000_000:.2f}M",
            )

        with col2:
            st.metric(
                "🛒 Total Orders",
                f"{total_orders / 1_000:.2f}K",
            )

        with col3:
            st.metric(
                "👥 Customers",
                f"{total_customers / 1_000:.2f}K",
            )

        with col4:
            st.metric(
                "📦 Average Order Value",
                f"£{average_order_value:,.2f}",
            )

except Exception as e:

    st.warning(
        f"Unable to load business KPIs: {e}"
    )

# ---------------------------------------------------------
# LATEST COMPLETE MONTH
# ---------------------------------------------------------

try:

    monthly_data = get_monthly_sales()

    if hasattr(monthly_data, "copy"):

        monthly_df = monthly_data.copy()

        # December 2011 is incomplete, so exclude it
        complete_months = monthly_df[
            monthly_df["year_month"] != "2011-12"
        ].copy()

        if not complete_months.empty:

            latest_month = complete_months.iloc[-1]

            month_name = latest_month["year_month"]
            month_revenue = float(
                latest_month["revenue"]
            )
            month_orders = int(
                latest_month["orders"]
            )
            month_customers = int(
                latest_month["customers"]
            )
            month_aov = float(
                latest_month["average_order_value"]
            )
            month_growth = float(
                latest_month["revenue_growth_pct"]
            )

            st.markdown(
                "### 📅 Latest Complete Month"
            )

            st.caption(
                f"{month_name} · December 2011 excluded because "
                "it is an incomplete period."
            )

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric(
                    "Revenue",
                    f"£{month_revenue / 1_000_000:.2f}M",
                    delta=f"{month_growth:+.2f}% MoM",
                )

            with m2:
                st.metric(
                    "Orders",
                    f"{month_orders:,}",
                )

            with m3:
                st.metric(
                    "Customers",
                    f"{month_customers:,}",
                )

            with m4:
                st.metric(
                    "Average Order Value",
                    f"£{month_aov:,.2f}",
                )

except Exception as e:

    st.warning(
        f"Unable to load latest month metrics: {e}"
    )

# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------------
# CHART FUNCTION
# ---------------------------------------------------------

def display_chart(tool_name, tool_result):

    if tool_result is None:
        return

    # Convert DataFrame directly
    if isinstance(tool_result, pd.DataFrame):

        df = tool_result.copy()

    # Convert list of dictionaries
    elif isinstance(tool_result, list):

        if not tool_result:
            return

        df = pd.DataFrame(tool_result)

    else:
        return


    # -----------------------------------------------------
    # MONTHLY SALES
    # -----------------------------------------------------

    if tool_name == "monthly_sales":

        if "year_month" in df.columns and "revenue" in df.columns:

            chart_df = df[
                [
                    "year_month",
                    "revenue",
                    "revenue_growth_pct",
                ]
            ].copy()

            chart_df["year_month"] = (
                chart_df["year_month"].astype(str)
            )

            chart_df = chart_df.sort_values(
                "year_month"
            )

            # Mark incomplete December 2011
            chart_df["period_status"] = "Complete month"

            chart_df.loc[
                chart_df["year_month"] == "2011-12",
                "period_status"
            ] = "Partial month — data through Dec 9"

            # -------------------------------------------------
            # MAIN REVENUE LINE
            # -------------------------------------------------

            line = (
                alt.Chart(chart_df)
                .mark_line(
                    strokeWidth=3,
                )
                .encode(
                    x=alt.X(
                        "year_month:N",
                        title="Month",
                        sort=None,
                        axis=alt.Axis(
                            labelAngle=-45
                        ),
                    ),
                    y=alt.Y(
                        "revenue:Q",
                        title="Revenue (£)",
                        axis=alt.Axis(
                            format=",.0f"
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "year_month:N",
                            title="Month",
                        ),
                        alt.Tooltip(
                            "revenue:Q",
                            title="Revenue",
                            format=",.2f",
                        ),
                        alt.Tooltip(
                            "revenue_growth_pct:Q",
                            title="MoM Growth",
                            format=".2f",
                        ),
                        alt.Tooltip(
                            "period_status:N",
                            title="Period",
                        ),
                    ],
                )
            )

            # -------------------------------------------------
            # REVENUE POINTS
            # -------------------------------------------------

            points = (
                alt.Chart(chart_df)
                .mark_circle(
                    size=80,
                )
                .encode(
                    x=alt.X(
                        "year_month:N",
                        sort=None,
                    ),
                    y=alt.Y(
                        "revenue:Q",
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "year_month:N",
                            title="Month",
                        ),
                        alt.Tooltip(
                            "revenue:Q",
                            title="Revenue",
                            format=",.2f",
                        ),
                        alt.Tooltip(
                            "revenue_growth_pct:Q",
                            title="MoM Growth",
                            format=".2f",
                        ),
                        alt.Tooltip(
                            "period_status:N",
                            title="Period",
                        ),
                    ],
                )
            )

            # -------------------------------------------------
            # REVENUE LABELS
            # -------------------------------------------------

            labels = (
                alt.Chart(chart_df)
                .mark_text(
                    dy=-12,
                    fontSize=11,
                )
                .encode(
                    x=alt.X(
                        "year_month:N",
                        sort=None,
                    ),
                    y=alt.Y(
                        "revenue:Q",
                    ),
                    text=alt.Text(
                        "revenue:Q",
                        format=",.0f",
                    ),
                )
            )

            # -------------------------------------------------
            # PARTIAL MONTH WARNING
            # -------------------------------------------------

            partial_month = (
                alt.Chart(
                    chart_df[
                        chart_df["year_month"] == "2011-12"
                    ]
                )
                .mark_text(
                    dy=-38,
                    fontSize=12,
                    fontWeight="bold",
                )
                .encode(
                    x=alt.X(
                        "year_month:N",
                        sort=None,
                    ),
                    y=alt.Y(
                        "revenue:Q",
                    ),
                    text=alt.value(
                        "⚠ Partial month"
                    ),
                )
            )

            chart = (
                line
                + points
                + labels
                + partial_month
            ).properties(
                height=450,
            )

            st.subheader(
                "📈 Monthly Revenue Trend"
            )

            st.caption(
                "⚠ December 2011 contains data only through December 9 "
                "and should not be compared directly with complete months."
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )


    # -----------------------------------------------------
    # COUNTRY PERFORMANCE
    # -----------------------------------------------------

    elif tool_name == "country_performance":

        if "country" in df.columns and "revenue" in df.columns:

            chart_df = df[
                ["country", "revenue"]
            ].copy()

            chart_df = chart_df.sort_values(
                "revenue",
                ascending=False,
            ).head(10)

            chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    cornerRadiusEnd=5
                )
                .encode(
                    y=alt.Y(
                        "country:N",
                        sort="-x",
                        title=None,
                        axis=alt.Axis(
                            labelLimit=180
                        ),
                    ),
                    x=alt.X(
                        "revenue:Q",
                        title="Revenue (£)",
                        axis=alt.Axis(
                            format=",.0f"
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "country:N",
                            title="Country",
                        ),
                        alt.Tooltip(
                            "revenue:Q",
                            title="Revenue",
                            format=",.2f",
                        ),
                    ],
                )
                .properties(
                    height=400,
                )
            )

            st.subheader("🌍 Top 10 Countries by Revenue")

            st.altair_chart(
                chart,
                use_container_width=True,
            )


    # -----------------------------------------------------
    # PRODUCT PERFORMANCE
    # -----------------------------------------------------

    elif tool_name in [
        "product_performance",
        "top_products",
    ]:

        if "description" in df.columns and "revenue" in df.columns:

            chart_df = df[
                ["description", "revenue"]
            ].copy()

            chart_df = chart_df.sort_values(
                "revenue",
                ascending=False,
            ).head(10)

            # Shorten very long product names for the chart
            chart_df["display_name"] = (
                chart_df["description"]
                .astype(str)
                .str[:45]
            )

            chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    cornerRadiusEnd=5
                )
                .encode(
                    y=alt.Y(
                        "display_name:N",
                        sort="-x",
                        title=None,
                        axis=alt.Axis(
                            labelLimit=320
                        ),
                    ),
                    x=alt.X(
                        "revenue:Q",
                        title="Revenue (£)",
                        axis=alt.Axis(
                            format=",.0f"
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "description:N",
                            title="Product",
                        ),
                        alt.Tooltip(
                            "revenue:Q",
                            title="Revenue",
                            format=",.2f",
                        ),
                    ],
                )
                .properties(
                    height=450,
                )
            )

            st.subheader("🏆 Top Products by Revenue")

            st.altair_chart(
                chart,
                use_container_width=True,
            )


    # -----------------------------------------------------
    # CUSTOMER PERFORMANCE
    # -----------------------------------------------------

    elif tool_name in [
        "customer_performance",
        "top_customers",
    ]:

        if "customer_id" in df.columns and "revenue" in df.columns:

            chart_df = df[
                ["customer_id", "revenue"]
            ].copy()

            chart_df = chart_df.sort_values(
                "revenue",
                ascending=False,
            ).head(10)

            chart_df["customer_id"] = (
                chart_df["customer_id"]
                .astype(str)
            )

            chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    cornerRadiusEnd=5
                )
                .encode(
                    y=alt.Y(
                        "customer_id:N",
                        sort="-x",
                        title=None,
                    ),
                    x=alt.X(
                        "revenue:Q",
                        title="Revenue (£)",
                        axis=alt.Axis(
                            format=",.0f"
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "customer_id:N",
                            title="Customer ID",
                        ),
                        alt.Tooltip(
                            "revenue:Q",
                            title="Revenue",
                            format=",.2f",
                        ),
                    ],
                )
                .properties(
                    height=450,
                )
            )

            st.subheader(
                "👥 Top Customers by Revenue"
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )


    # -----------------------------------------------------
    # REVENUE DECLINES
    # -----------------------------------------------------

    elif tool_name == "revenue_declines":

        if (
            "year_month" in df.columns
            and "revenue_growth_pct" in df.columns
        ):

            chart_df = df[
                [
                    "year_month",
                    "revenue_growth_pct",
                ]
            ].copy()

            # Keep only negative month-over-month changes
            chart_df = chart_df[
                chart_df["revenue_growth_pct"] < 0
            ].copy()

            # Convert decline to positive magnitude
            # for easier horizontal-bar visualization
            chart_df["decline_magnitude"] = (
                chart_df["revenue_growth_pct"].abs()
            )

            # Largest decline first
            chart_df = chart_df.sort_values(
                "decline_magnitude",
                ascending=False,
            ).head(10)

            chart_df["year_month"] = (
                chart_df["year_month"].astype(str)
            )

            # -------------------------------------------------
            # DECLINE CHART
            # -------------------------------------------------

            chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    cornerRadiusEnd=5
                )
                .encode(
                    y=alt.Y(
                        "year_month:N",
                        sort="-x",
                        title=None,
                    ),
                    x=alt.X(
                        "decline_magnitude:Q",
                        title="Revenue Decline (%)",
                        axis=alt.Axis(
                            format=".0f"
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "year_month:N",
                            title="Month",
                        ),
                        alt.Tooltip(
                            "revenue_growth_pct:Q",
                            title="MoM Change",
                            format=".2f",
                        ),
                    ],
                )
                .properties(
                    height=400,
                )
            )

            st.subheader(
                "📉 Largest Revenue Declines"
            )

            st.caption(
                "Ranked by the magnitude of negative "
                "month-over-month revenue changes. "
                "December 2011 is a partial month."
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )

# ---------------------------------------------------------
# QUICK BUSINESS QUESTIONS
# ---------------------------------------------------------

st.subheader("💡 Quick Business Questions")

quick_questions = [
    "What is our total revenue?",
    "Show me our monthly sales trend",
    "What are our top 5 products by revenue?",
    "Which country generates the most revenue?",
    "Which customers generate the most revenue?",
    "Which months had the biggest revenue declines?",
]

cols = st.columns(3)

selected_question = None

for index, quick_question in enumerate(quick_questions):

    with cols[index % 3]:

        if st.button(
            quick_question,
            use_container_width=True,
            key=f"quick_question_{index}",
        ):
            selected_question = quick_question


# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------

typed_question = st.chat_input(
    "Ask a business question..."
)

question = selected_question or typed_question


if question:

    # Show user question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


    # AI response
    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing your business data..."
        ):

            try:

                result = ask_copilot(question)

                answer = result["answer"]

                tool_name = result["tool_name"]

                tool_result = result["tool_result"]


                # -------------------------------------------------
                # AI ANSWER
                # -------------------------------------------------

                st.markdown(answer)


                # -------------------------------------------------
                # CHART
                # -------------------------------------------------

                display_chart(
                    tool_name,
                    tool_result,
                )


                # Save only text in chat history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )


            except Exception as e:
                st.error(
                    "⚠️ I couldn't complete that analysis. "
                    "Please try again or ask another business question."
    )