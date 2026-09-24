# AI Business Intelligence Copilot

> An AI-powered Business Intelligence application that converts natural-language business questions into verified analytics and interactive business insights using Qwen 2.5, PostgreSQL, Python, and Streamlit.

## Overview

The AI Business Intelligence Copilot allows business users to ask natural-language questions about e-commerce performance.

Examples:

- What is our total revenue?
- Which country generates the most revenue?
- What are our top 5 products by revenue?
- Which customers generate the most revenue?
- Which months had the biggest revenue declines?

The application uses Qwen 2.5 7B through Ollama to understand the user's question, select a verified analytics tool, retrieve data from PostgreSQL, and generate a business-oriented response.

## Tech Stack

- Python
- PostgreSQL
- Pandas
- SQL
- Qwen 2.5 7B
- Ollama
- Streamlit
- Altair
- Power BI

## Architecture

The application follows a verified analytics workflow:

```text
Business User
      ↓
Streamlit Interface
      ↓
Qwen 2.5 7B via Ollama
      ↓
Analytics Tool Selection
      ↓
Verified Python Analytics Functions
      ↓
PostgreSQL
      ↓
Verified Business Metrics
      ↓
Qwen Business Explanation
      ↓
Interactive Streamlit Visualization
```

## Dataset

The project uses the **UCI Online Retail II** dataset.

**Source:** UCI Machine Learning Repository  
**Dataset:** Online Retail II  
**Period:** December 2009 – December 2011

The dataset contains transactional e-commerce information including:

- Invoice
- Product
- Quantity
- Invoice Date
- Unit Price
- Customer ID
- Country

## Data Preparation

The raw dataset contains more than 1 million transaction rows.

The data preparation process includes:

- Removing exact duplicate rows
- Excluding cancellation invoices from positive sales analysis
- Excluding negative quantities from the positive sales fact table
- Excluding zero or negative prices
- Preserving missing Customer IDs for appropriate customer-status handling
- Excluding service/operational codes from product analytics
- Saving the cleaned analytical dataset as Parquet

**Final cleaned sales dataset:** 1,003,484 rows

## Database & Data Warehouse

The cleaned transaction data is stored in PostgreSQL using a dimensional data model.

### Database

- Database: `ai_bi_copilot`
- Schema: `analytics`
- Database: PostgreSQL

### Data Model

The warehouse consists of:

- `fact_sales` — transactional sales data
- `dim_date` — date and time attributes
- `dim_product` — product information
- `dim_customer` — customer information

The `fact_sales` table connects to the dimension tables through foreign keys, allowing efficient business analysis across products, customers, dates, and countries.

### Analytics Views

Business metrics are exposed through PostgreSQL analytical views including:

- `vw_kpis`
- `vw_monthly_sales`
- `vw_country_sales`
- `vw_product_sales`
- `vw_customer_sales`
- `vw_top_products`
- `vw_top_customers`

## AI Analytics Tools

The Copilot uses verified analytics tools to answer business questions.

Available tools include:

- **Business KPIs** — overall revenue, quantity, orders, customers, products, countries, and AOV
- **Monthly Sales** — monthly revenue, orders, customers, AOV, and revenue growth
- **Country Performance** — sales performance by country
- **Product Performance** — product-level sales performance
- **Customer Performance** — customer-level sales performance
- **Top Products** — products ranked by revenue
- **Top Customers** — customers ranked by revenue
- **Revenue Declines** — periods with the largest month-over-month revenue declines

The AI selects the relevant analytics tool based on the user's question and uses the returned data as the source of truth for its response.

## Interactive Dashboard

The Streamlit application provides an interactive interface for business analysis.

The dashboard includes:

- Executive KPI cards
- Monthly revenue trend analysis
- Country performance analysis
- Top product analysis
- Top customer analysis
- Revenue decline analysis
- Natural-language business questions
- AI-generated business insights

Charts are generated dynamically from verified analytics results returned by the PostgreSQL-backed analytics layer.

The application also highlights incomplete periods where relevant, such as December 2011, which contains data only through December 9.

## Demo

The application provides an interactive Streamlit interface where users can ask business questions in natural language.

### Example Questions

- What is our total revenue?
- Show me our monthly sales trend.
- What are our top 5 products by revenue?
- Which country generates the most revenue?
- Which customers generate the most revenue?
- Which months had the biggest revenue declines?

The Copilot converts these questions into verified analytical workflows and presents the results using business-focused explanations and interactive visualizations.

## Setup & Installation

1. Clone the repository

```bash
git clone https://github.com/farhan316-analytics/AI_Business_Intelligence_Copilot.git
cd AI_Business_Intelligence_Copilot

2. Create a virtual environment
python -m venv .venv
Activate it on Windows:
.\.venv\Scripts\Activate.ps1

3. Install dependencies
pip install -r requirements.txt

4. Configure PostgreSQL
Create the PostgreSQL database:
ai_bi_copilot
Configure the database connection required by the project.

5. Install and run Ollama
Install Ollama and download the Qwen model:
ollama pull qwen2.5:7b
Start Ollama before running the application.

6. Run the Streamlit application
streamlit run app/app.py
The application will open in the browser and provide the AI Business Intelligence Copilot interface.

Save it.

**When done, say `done`.**

Continue the README setup

- Step 8: add key business metrics & results

Continue the README setup

- :chatgpt-content-reference{index="0"}

```

## Key Business Metrics

The cleaned dataset contains:

| Metric | Value |
|---|---:|
| Total Revenue | £19.67M |
| Total Quantity Sold | 11.19M |
| Total Orders | 39.57K |
| Identified Customers | 5.86K |
| Products | 4,907 |
| Countries | 43 |
| Average Order Value | £497.06 |

These metrics are calculated from the verified PostgreSQL analytics layer and are used by the AI Copilot when answering business questions.

### Example Business Insights

The Copilot can identify:

- Overall revenue performance
- Monthly revenue growth and declines
- Highest-performing countries
- Top products by revenue
- Highest-value customers
- Periods with significant revenue declines

The AI provides explanations based on verified analytical results rather than generating business metrics from the language model itself.

## Project Structure

```text
AI_Business_Intelligence_Copilot/
│
├── app/
│   └── app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── ai/
│   │   ├── copilot.py
│   │   ├── llm.py
│   │   └── tools.py
│   │
│   ├── analytics/
│   │   └── business_metrics.py
│   │
│   └── data/
│
├── sql/
│
├── powerbi/
│
├── requirements.txt
└── README.md

```

## Limitations & Data Considerations

- The dataset does not contain product cost information, so profit and profit margin cannot be calculated.
- Customer-level analysis is limited to transactions with available customer identification.
- December 2011 is an incomplete period, with data available only through December 9.
- Revenue trends describe observed changes in the dataset and do not automatically establish the causes behind those changes.
- AI-generated explanations are based on verified analytics returned by the system and should be interpreted within the available dataset context.
- The project is designed for analytical decision support rather than autonomous business decision-making.

## Future Improvements

Planned improvements for the AI Business Intelligence Copilot include:

- Natural-language SQL generation with query validation
- More advanced anomaly detection
- Automated business KPI monitoring
- Customer segmentation and RFM analysis
- Sales forecasting integration
- Automated executive reporting
- Additional Power BI dashboards
- Support for additional business datasets
- Improved AI reasoning and multi-step analytical workflows
- Deployment as a production-ready cloud application

## Author

**Mohammad Farhan**

MBA — Business Analytics & Artificial Intelligence  
Middlesex University Dubai

### Connect

- GitHub: https://github.com/farhan316-analytics
- Portfolio: https://farhan-analytics.lovable.app/

---

⭐ If you find this project useful, consider starring the repository.

