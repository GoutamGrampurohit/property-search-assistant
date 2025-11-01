# 🏠 Property Search Chatbot

An AI-powered property search system that understands natural language queries without using LLMs. Built with **Python, Pandas, and Streamlit**.

## 🎯 Features

- ✅ Natural Language Understanding: Parse queries like "3BHK in Mumbai under 2 Cr"
- ✅ Smart Filtering: Extract city, BHK, budget, locality, and possession status
- ✅ Data-Driven Summaries: Generate factual summaries from CSV data
- ✅ Property Cards: Display formatted results with all details
- ✅ Fallback Search: Auto-expand search when no exact matches found
- ✅ No LLMs Required: Pure rule-based + regex parsing

## 📁 Project Structure

```
property-search-chatbot/
│
├── app.py                          # Streamlit frontend
├── backend/
│   ├── __init__.py
│   ├── data_loader.py              # CSV loading & merging
│   ├── query_parser.py             # NLP query extraction
│   ├── search_engine.py            # Search logic
│   └── summarizer.py               # Summary generation
│
├── data/
│   ├── project.csv
│   ├── ProjectConfiguration.csv
│   ├── ProjectConfigurationVariant.csv
│   └── ProjectAddress.csv
│
├── requirements.txt
└── README.md
```

## 🔧 How It Works

### 1. **Query Parser** (`query_parser.py`)
- Uses regex patterns to extract:
- City: Mumbai, Pune, etc.
- BHK: 1BHK, 2BHK, 3BHK, etc.
- Budget: "under 2 Cr", "below 80 lakh"
- Status: "ready to move", "under construction"
- Locality: Chembur, Baner, Wakad, etc.

### 2. **Search Engine** (`search_engine.py`)
- Applies filters to Pandas DataFrame
- Handles missing data gracefully
- Implements fallback search (relaxes filters if no results)
- Sorts and deduplicates results

### 3. **Summarizer** (`summarizer.py`)
- Generates fact-based summaries from data
- Creates formatted property cards
- Handles edge cases (no results, expanded search)

### 4. **Data Loader** (`data_loader.py`)
- Merges 4 CSV files into single DataFrame
- Cleans and standardizes data
- Converts prices to Crores
- Extracts BHK from configuration types

## 📊 Data Schema

The system expects these CSV columns:

### `project.csv`
- `id`, `projectName`, `status`, `possessionDate`, `projectCategory`, `slug`

### `ProjectConfiguration.csv`
- `id`, `projectId`, `type` (e.g., "2BHK", "3BHK")

### `ProjectConfigurationVariant.csv`
- `id`, `configurationId`, `bathrooms`, `balcony`, `carpetArea`, `price`

### `ProjectAddress.csv`
- `projectId`, `landmark`, `fullAddress`, `pincode`
