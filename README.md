# 💳 Credit Card Default Prediction & Portfolio Risk Segmentation

> **An end-to-end Cards portfolio analytics case study** — combining SQL, Python, Power BI, and Excel to predict customer default risk, segment the portfolio, and propose data-driven Risk Appetite Metrics.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-MI%20Pack-217346?logo=microsoftexcel&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## 📌 Project Overview

This project simulates the work of a **Portfolio Analytics team** in a consumer-lending bank. Using a real-world dataset of **30,000 credit-card customers**, I built a full analytics pipeline covering:

- **Performance monitoring** (KPIs, default rates, utilisation, delinquency)
- **Predictive modelling** (default probability)
- **Customer segmentation** (risk tiers via clustering)
- **MI reporting** (Power BI dashboard + Excel pack + Executive PowerPoint)
- **Risk Appetite recommendations** (data-led thresholds for portfolio strategy)

The goal: **demonstrate how an analyst can turn raw portfolio data into actionable insights that influence credit strategy, balance risk and reward, and keep the customer at the heart of decisions.**

---

## 🎯 Business Problem

A consumer-lending bank needs to:

1. **Monitor** the performance of its credit-card portfolio.
2. **Predict** which customers are likely to default in the next month.
3. **Segment** customers into risk tiers to inform credit-limit and collections strategy.
4. **Communicate** insights clearly to senior, non-technical stakeholders.

---

## 📂 Dataset

**Source:** UCI Machine Learning Repository — *Default of Credit Card Clients Dataset*

- **Size:** 30,000 customers, 24 features
- **Period:** 6 months of payment history
- **Target Variable:** `default.payment.next.month` (1 = default, 0 = no default)
- **Features include:** credit limit, demographics (age, sex, education, marital status), past-payment status (PAY_0 to PAY_6), bill amounts, and previous payments

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **Data Storage & Querying** | PostgreSQL, SQLite, SQL |
| **Data Analysis & Modelling** | Python (Pandas, NumPy, Scikit-learn, XGBoost, SHAP) |
| **Visualisation** | Power BI, Matplotlib, Seaborn |
| **Reporting** | Microsoft Excel (Pivot Tables, Power Query), PowerPoint |
| **Version Control** | Git, GitHub |

---

## 📁 Repository Structure

```
credit-card-portfolio-analytics/
│
├── README.md
├── data/
│   └── credit_card_clients.csv
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_portfolio_kpis.sql
│   └── 03_segmentation_queries.sql
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_default_prediction.ipynb
│   └── 03_risk_segmentation.ipynb
├── excel/
│   └── Portfolio_MI_Dashboard.xlsx
├── powerbi/
│   └── Cards_Portfolio_Dashboard.pbix
├── presentation/
│   └── Executive_Summary.pptx
└── images/
    ├── powerbi_dashboard.png
    ├── shap_summary.png
    └── risk_segments.png
```

---

## 🔍 Methodology

### 1. SQL — Portfolio KPI Layer

Built reusable SQL queries to compute key portfolio metrics directly from the database:

- Overall **default rate** and trend over time
- **Credit utilisation ratio** (bill amount / credit limit) by segment
- **Delinquency roll-rates** (1 → 2 → 3 months past due)
- **Vintage analysis** by demographic cohort
- **Exposure at default** by risk band

> 📄 See [`sql/02_portfolio_kpis.sql`](sql/02_portfolio_kpis.sql) for the full query suite.

### 2. Exploratory Data Analysis (Python)

- Distribution analysis across age, credit limit, and education
- Correlation heatmap of all numerical features
- Default-rate breakdown by demographic segment
- Identified that **customers with 2+ months of late payment history show ~7x higher default probability**

### 3. Predictive Modelling

Built and compared three classification models:

| Model | ROC-AUC | Precision | Recall |
|---|---|---|---|
| Logistic Regression | 0.72 | 0.68 | 0.34 |
| Random Forest | 0.76 | 0.65 | 0.38 |
| **XGBoost** | **0.78** | **0.69** | **0.41** |

**XGBoost** was selected as the champion model based on overall AUC and recall on the default class.

### 4. Explainability with SHAP

Used **SHAP values** to interpret the XGBoost model's predictions — critical for credit-risk modelling under regulatory frameworks that require transparent, explainable lending decisions.

**Top default drivers identified:**
1. Most recent payment status (PAY_0)
2. Credit utilisation ratio
3. Past payment history (PAY_2, PAY_3)
4. Age and credit limit

![SHAP Summary](images/shap_summary.png)

### 5. Customer Risk Segmentation

Applied **K-Means clustering** to segment customers into 4 risk tiers:

| Tier | % of Portfolio | Default Rate | Recommendation |
|---|---|---|---|
| **Tier 1 – Low Risk** | 38% | 6% | Eligible for credit-limit increases |
| **Tier 2 – Moderate** | 31% | 14% | Maintain current limits, monitor |
| **Tier 3 – Elevated** | 21% | 28% | Restrict utilisation, proactive engagement |
| **Tier 4 – High Risk** | 10% | 52% | Early collections, limit reduction |

### 6. MI Reporting Pack

#### Power BI Dashboard
Interactive dashboard built for senior stakeholders covering:
- Portfolio at a glance (exposure, default rate, utilisation)
- Trend analysis (default rate over time)
- Demographic and risk-tier filters
- Drill-through to customer-level views

![Power BI Dashboard](images/powerbi_dashboard.png)

#### Excel MI Pack
- Variance analysis (actual default rate vs. forecast benchmark)
- Pivot tables by demographic and risk tier
- Conditional-formatted thresholds aligned to Risk Appetite

#### Executive PowerPoint
A 5-slide stakeholder-ready summary translating complex analytics into clear business actions.

---

## 💡 Key Insights & Recommendations

1. **Past payment behaviour is the single strongest predictor of future default** — supporting investment in early-warning indicators within the MI suite.
2. **Tier 4 customers (10% of portfolio) drive 35%+ of total default exposure** — proactive collections strategy here delivers the highest ROI.
3. **Credit utilisation above 80% correlates strongly with default** — a candidate Risk Appetite Metric for ongoing monitoring.
4. **Education level shows surprising lift** — a feature worth integrating into next-generation scorecards.

---

## 🎯 Skills Demonstrated

- ✅ **SQL** — complex queries, CTEs, window functions, KPI computation
- ✅ **Python** — Pandas, Scikit-learn, XGBoost, SHAP
- ✅ **Statistical Modelling** — classification, evaluation, explainability
- ✅ **Customer Segmentation** — K-Means clustering, risk-tier framework
- ✅ **Power BI** — interactive, stakeholder-ready dashboards
- ✅ **Advanced Excel** — pivot tables, Power Query, variance analysis
- ✅ **Stakeholder Communication** — PowerPoint storytelling for non-technical audiences
- ✅ **Risk & Compliance Awareness** — explainable AI, responsible-lending principles

---

## 🚀 How to Run This Project

### Prerequisites
```
Python 3.10+
PostgreSQL 14+ (or SQLite)
Power BI Desktop (free)
Microsoft Excel
```

### Setup
```bash
# Clone the repo
git clone https://github.com/<your-username>/credit-card-portfolio-analytics.git
cd credit-card-portfolio-analytics

# Install dependencies
pip install -r requirements.txt

# Load data into your database
psql -U <user> -d <database> -f sql/01_create_tables.sql
```

### Run Notebooks
```bash
jupyter notebook notebooks/01_EDA.ipynb
```

### Open Dashboards
- Power BI: open `powerbi/Cards_Portfolio_Dashboard.pbix`
- Excel: open `excel/Portfolio_MI_Dashboard.xlsx`

---

## 📈 Future Enhancements

- [ ] Integrate **IFRS 9 expected credit loss (ECL)** staging logic
- [ ] Add a **Snowflake** layer to demonstrate cloud-warehouse querying
- [ ] Build a **Streamlit web app** for interactive default-risk scoring
- [ ] Implement **monitoring of model drift** with automated alerts

---

## 👤 About the Author

**Samiur Rahman**
Data & Portfolio Analytics | DBA Researcher | MSc Data Analytics

📍 Leeds, UK
📧 srjobs129@gmail.com
🔗 [LinkedIn](https://www.linkedin.com/) | [GitHub](https://github.com/)

> *Currently undertaking a Doctorate in Business Administration with a research focus on data-driven decision-making in financial services.*

---

## 📜 Licence

This project is released under the MIT Licence — feel free to fork, adapt, and learn from it.

## 🙏 Acknowledgements

- **UCI Machine Learning Repository** — for the publicly available dataset
- **Yeh, I. C., & Lien, C. H. (2009)** — original research paper introducing the dataset

---

⭐ **If you found this project useful, please consider giving it a star!**
