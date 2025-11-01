# 🏠 Property Search Chatbot

An AI-powered property search system that understands natural language queries without using LLMs. Built with **Python, Pandas, and Streamlit**.

## 🎯 Features

- ✅ **Natural Language Understanding**: Parse queries like "3BHK in Mumbai under 2 Cr"
- ✅ **Smart Filtering**: Extract city, BHK, budget, locality, and possession status
- ✅ **Data-Driven Summaries**: Generate factual summaries from CSV data
- ✅ **Property Cards**: Display formatted results with all details
- ✅ **Fallback Search**: Auto-expand search when no exact matches found
- ✅ **No LLMs Required**: Pure rule-based + regex parsing

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

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd property-search-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your CSV files
Place your CSV files in the `data/` folder:
- `project.csv`
- `ProjectConfiguration.csv`
- `ProjectConfigurationVariant.csv`
- `ProjectAddress.csv`

## ▶️ Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 💬 Example Queries

Try these natural language queries:

1. **Basic Search**
   - "Show me 3BHK apartments in Mumbai"
   - "2BHK properties in Pune"

2. **With Budget**
   - "3BHK under 2 crores in Mumbai"
   - "Apartments under 80 lakh in Chembur"

3. **With Locality**
   - "2BHK near Hinjewadi under 1.5 Cr"
   - "Properties in Ravet Pune"

4. **With Status**
   - "Ready to move 3BHK in Mumbai"
   - "Under construction properties in Baner"

5. **Complex Queries**
   - "Ready to move 2BHK in Chembur under 1.2 Cr"
   - "Show me 4BHK apartments near Kharadi under 3 Cr"

## 🔧 How It Works

### 1. **Query Parser** (`query_parser.py`)
- Uses regex patterns to extract:
  - **City**: Mumbai, Pune, etc.
  - **BHK**: 1BHK, 2BHK, 3BHK, etc.
  - **Budget**: "under 2 Cr", "below 80 lakh"
  - **Status**: "ready to move", "under construction"
  - **Locality**: Chembur, Baner, Wakad, etc.

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

## 🎨 Customization

### Add More Cities
Edit `query_parser.py`:
```python
self.city_patterns = [
    r'\b(mumbai|pune|delhi|bangalore|hyderabad|chennai)\b',
]
```

### Add More Localities
Edit `query_parser.py`:
```python
self.localities = [
    'chembur', 'wakad', 'baner', 'your-locality',
    # ... add more
]
```

### Adjust Search Logic
Edit `search_engine.py`:
- Modify filter tolerance
- Change sorting logic
- Add more ranking factors

## 🔮 Optional: Semantic Search

To add semantic search with embeddings:

1. Install libraries:
```bash
pip install sentence-transformers faiss-cpu
```

2. Create `semantic_search.py`:
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticSearch:
    def __init__(self, df):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.df = df
        self.index = self._build_index()
    
    def _build_index(self):
        # Create text representations
        texts = self.df.apply(
            lambda x: f"{x['projectName']} {x['type']} {x['fullAddress']}", 
            axis=1
        ).tolist()
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        return index
    
    def search(self, query, top_k=10):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            top_k
        )
        return self.df.iloc[indices[0]]
```

3. Integrate into `search_engine.py`

## 📝 TODO / Enhancements

- [ ] Add amenities filtering (gym, pool, parking)
- [ ] Implement project comparison feature
- [ ] Add location-based radius search
- [ ] Export search results to Excel/PDF
- [ ] Add user authentication and saved searches
- [ ] Implement price trend analysis
- [ ] Add map visualization with Plotly/Folium

## 🐛 Troubleshooting

### "No module named 'backend'"
Make sure you're running from the project root directory.

### "CSV file not found"
Ensure all 4 CSV files are in the `data/` folder.

### No results found
Try:
- Broader queries (remove locality/status filters)
- Higher budget
- Different city/locality names

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ without LLMs** | Uses only rule-based NLP + Pandas
