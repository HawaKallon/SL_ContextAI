# 🇸🇱 Sierra Leone Context AI

A comprehensive Retrieval-Augmented Generation (RAG) system designed to provide culturally sensitive and contextually accurate information about Sierra Leone. This AI assistant understands Sierra Leone's unique history, culture, politics, economy, and current affairs.

## 🌟 Features

- **Multi-domain Knowledge Base**: Covers history, culture, politics, economy, and general topics
- **Context-Aware Responses**: Provides culturally sensitive answers relevant to Sierra Leoneans
- **Multiple Data Sources**: Integrates Wikipedia articles, news websites, PDFs, and custom links
- **Real-time Streaming**: FastAPI-based web interface with streaming responses
- **Source Citations**: Always provides sources for transparency and verification
- **Simple Explanations**: Uses everyday language, not academic jargon

## 🏗️ Architecture

### Core Components

1. **Main Application** (`main.py`): Interactive CLI interface for querying the AI
2. **Web API** (`api.py`): FastAPI-based REST API with streaming responses
3. **Data Collection** (`data_collection.py`): Orchestrates data gathering from multiple sources
4. **Data Loading** (`data_loading.py`): Processes and chunks documents into vector stores
5. **Scrapers** (`scrapers/`): Modular web scraping for different content sources

### Knowledge Categories

- **History**: Civil war (1991-2002), independence (1961), colonial period, post-war recovery
- **Culture**: Ethnic diversity (Temne, Mende, Limba, Krio), languages, traditions, music, food, religion
- **Politics**: Multi-party democracy, paramount chiefs, governance, elections
- **Economy**: Mining (diamonds, iron ore), agriculture, fishing, development challenges
- **General**: Geography, demographics, health, education, current issues

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Hugging Face API token
- Internet connection for data collection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SL_ContextAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "HUGGINGFACEHUB_API_TOKEN=your_token_here" > .env
   ```

### Usage

#### Option 1: Interactive CLI
```bash
python main.py
```

#### Option 2: Web API
```bash
python api.py
# API available at http://localhost:8000
```

#### Option 3: Minimal Web UI
- Open `bot_example.html` in your browser to chat with the assistant.
- Ensure the API is running locally on `http://localhost:8000`.
- If your API runs on a different URL, update the `API_BASE` constant in `bot_example.html`:

```javascript
const API_BASE = "http://localhost:8000";
```

Tip: If accessing the API over the internet (e.g., via ngrok), replace the value above with your public URL.

## 📊 Data Collection & Management

### Automatic Data Collection

Run the comprehensive data collection process:

```bash
python data_collection.py
```

This will:
1. **Scrape links** from `data/links.txt`
2. **Collect Wikipedia articles** on Sierra Leone topics
3. **Gather news articles** from Sierra Leone news websites
4. **Process and save** all content to category folders

### Manual Data Addition

#### Adding PDFs
Simply place PDF files in the appropriate category folder:
```
data/
├── culture/
│   ├── your_culture_document.pdf
│   └── another_culture_file.pdf
├── history/
│   └── historical_document.pdf
└── ...
```

#### Adding Custom Links
Edit `data/links.txt` to include your URLs:

```txt
# Sierra Leone AI - Links Collection
[general]
https://statehouse.gov.sl
https://sierralii.gov.sl

[culture]
https://example.com/krio-culture
https://example.com/mende-traditions

[history]
https://example.com/sl-history
```

### Creating Vector Stores

After adding new data, create/update vector stores:

```bash
python data_loading.py
```

## 🔧 Technical Details

### AI Models Used

- **LLM**: Mixtral-8x7B-Instruct-v0.1 (via Hugging Face)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-V2
- **Vector Store**: FAISS (Facebook AI Similarity Search)

### Document Processing

- **Chunk Size**: 1500 characters
- **Chunk Overlap**: 300 characters
- **Supported Formats**: `.txt`, `.pdf`
- **Text Splitting**: RecursiveCharacterTextSplitter with intelligent separators

### Data Sources

1. **Wikipedia Scraper**: Extracts articles on Sierra Leone topics
2. **News Scraper**: Collects articles from Sierra Leone news websites
3. **Links Scraper**: Processes URLs from `data/links.txt`
4. **PDF Loader**: Extracts text from PDF documents
5. **Manual Documents**: Direct text file additions

## 📁 Project Structure

```
SL_ContextAI/
├── data/                          # Knowledge base data
│   ├── culture/                   # Cultural information
│   ├── economy/                   # Economic data
│   ├── general/                   # General topics
│   ├── history/                   # Historical information
│   ├── politics/                  # Political information
│   └── links.txt                  # Custom URL collection
├── scrapers/                      # Web scraping modules
│   ├── wikipedia_scraper.py       # Wikipedia content extraction
│   ├── news_scraper.py           # News website scraping
│   └── links_scraper.py          # Custom links processing
├── vectorstores/                  # FAISS vector stores
│   ├── culture_faiss/
│   ├── economy_faiss/
│   ├── general_faiss/
│   ├── history_faiss/
│   └── politics_faiss/
├── main.py                        # CLI interface
├── api.py                         # FastAPI web interface
├── data_collection.py             # Data gathering orchestrator
├── data_loading.py               # Document processing & vectorization
└── requirements.txt              # Python dependencies
```

## 🌐 API Endpoints

### Web Interface
- `GET /`: API information and documentation
- `POST /query`: Submit questions and get responses
- `GET /about`: System capabilities and context information

### Example API Usage

```python
import requests

# Query the AI
response = requests.post("http://localhost:8000/query", json={
    "question": "What is the role of paramount chiefs in Sierra Leone?"
})

print(response.json()["answer"])
```

## 🔍 Example Questions

The AI can answer questions like:

- **History**: "Why did the civil war start and how did it end?"
- **Culture**: "How does the Krio language work?"
- **Politics**: "What is the role of paramount chiefs in Sierra Leone?"
- **Economy**: "What are Sierra Leone's biggest economic challenges?"
- **General**: "What is life like in Freetown?"

## 🛠️ Development

### Adding New Data Sources

1. **Create a new scraper** in `scrapers/`
2. **Add it to** `data_collection.py`
3. **Run data collection** to gather new content
4. **Update vector stores** with `data_loading.py`

### Customizing Categories

To add new knowledge categories:

1. **Update** `categories` list in `main.py` and `data_loading.py`
2. **Create** corresponding folder in `data/`
3. **Add** category keywords in `classify_question()` method
4. **Update** prompts and context information

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Sierra Leone community for cultural context
- Hugging Face for AI models and infrastructure
- LangChain for RAG framework
- Wikipedia contributors for comprehensive information

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

