# 🏎️ VISU — Automobile Engine & Body Explorer

An interactive data dashboard built with **Streamlit** exploring the 1985 Ward's Automotive Yearbook dataset (205 records).

## 🔗 Live App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://royalcoderpro-visu.streamlit.app)

**→ [https://royalcoderpro-visu.streamlit.app](https://royalcoderpro-visu.streamlit.app)**

---

## Features

- **Interactive Engine & Body Explorer** — visual HTML panel with car body diagrams and engine specs
- **Descriptive Statistics** — filter by body style, engine type, and fuel type with live KPI cards
- **Distribution Plots** — histograms for price, horsepower, MPG, engine size, and more
- **Price by Body Style** — bar chart comparing average price across body types
- **HP & MPG by Engine Type** — dual-axis comparison
- **Price vs. Horsepower** — scatter plot with engine-type coloring
- **Correlation with Price** — horizontal bar chart of feature correlations
- **Cars by Make (Top 15)** — ranked bar chart
- **Drive-Wheel Distribution** — pie chart breakdown

---

## Project Structure

```
VISU/
├── app.py                  # Streamlit UI orchestration
├── backend/
│   ├── data.py             # Data loading & filtering
│   └── charts.py           # Matplotlib chart functions
├── frontend/
│   └── explorer.html       # Interactive HTML explorer (base64 images)
├── Automobile.ipynb        # EDA notebook
├── Automobile_data.csv     # Raw dataset
└── requirements.txt
```

---

## Run Locally

```bash
git clone https://github.com/RoyalCoderPRO/VISU.git
cd VISU
pip install -r requirements.txt
streamlit run app.py
```

---

## Dataset

**1985 Ward's Automotive Yearbook** — 205 automobile records with attributes including make, body style, engine type, fuel type, horsepower, price, MPG, and more.
