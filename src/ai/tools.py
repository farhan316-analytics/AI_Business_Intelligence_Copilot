from src.analytics.business_metrics import (
    get_business_kpis,
    get_monthly_sales,
    get_country_performance,
    get_product_performance,
    get_customer_performance,
    get_top_products,
    get_top_customers,
    get_revenue_declines,
)


TOOLS = {
    "business_kpis": {
        "function": get_business_kpis,
        "description": (
            "Returns overall business KPIs including total revenue, "
            "quantity sold, orders, customers, products, countries, "
            "and average order value."
        ),
    },

    "monthly_sales": {
        "function": get_monthly_sales,
        "description": (
            "Returns monthly revenue, quantity, orders, customers, "
            "average order value, previous month revenue, and revenue growth."
        ),
    },

    "country_performance": {
        "function": get_country_performance,
        "description": (
            "Returns sales performance by country including revenue, "
            "quantity, orders, customers, and average order value."
        ),
    },

    "product_performance": {
        "function": get_product_performance,
        "description": (
            "Returns product-level performance including quantity sold, "
            "revenue, orders, customers, and average order value."
        ),
    },

    "customer_performance": {
        "function": get_customer_performance,
        "description": (
            "Returns customer-level performance including orders, "
            "quantity, revenue, first order date, last order date, "
            "and average order value."
        ),
    },

    "top_products": {
        "function": get_top_products,
        "description": (
            "Returns products ranked by revenue."
        ),
    },

    "top_customers": {
        "function": get_top_customers,
        "description": (
            "Returns customers ranked by revenue."
        ),
    },

    "revenue_declines": {
        "function": get_revenue_declines,
        "description": (
            "Returns months with the largest revenue declines "
            "compared with the previous month."
        ),
    },
}


def list_tools():
    """Return the available business intelligence tools."""

    return {
        name: details["description"]
        for name, details in TOOLS.items()
    }


if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS INTELLIGENCE COPILOT")
    print("AVAILABLE AI TOOLS")
    print("=" * 70)

    for name, description in list_tools().items():
        print(f"\n{name}")
        print(f"  {description}")

    print("\n" + "=" * 70)
    print(f"TOTAL TOOLS: {len(TOOLS)}")
    print("=" * 70)