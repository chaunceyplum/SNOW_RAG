Sure! Here's the complete `README.md` content formatted into a single file, ready to copy and paste:

---

```markdown
# 🧠 Snowflake Docs RAG API

This project is a FastAPI web application that:

- Scrapes [Snowflake documentation](https://docs.snowflake.com)
- Parses and stores the docs in MongoDB Atlas
- Generates vector embeddings using `ollama` with `nomic-embed-text`
- Enables semantic search over documentation via MongoDB Atlas Vector Search
- Uses `llama3.2` via `ollama` to answer user queries in a RAG (Retrieval-Augmented Generation) flow

---

## 🚀 Features

- 🕸️ `/scrape`: Scrape Snowflake documentation
- 📦 `/load_data`: Generate embeddings and load docs into MongoDB
- 🤖 `/question`: Ask a question and get an LLM-powered answer with real doc context
- 🧹 `/delete`: Clear the database
- 👋 `/`: Basic health check endpoint

---

## 🛠 Requirements

- Python 3.9+
- MongoDB Atlas account
- [ollama](https://ollama.com/) installed locally with models:
  - `nomic-embed-text`
  - `llama3.2`
- A `.env` file with MongoDB credentials:
```

MONGODB_USERNAME=your_username  
MONGODB_PASSWORD=your_password

````

---

## 📦 Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/snowflake-docs-rag-api.git
cd snowflake-docs-rag-api
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start `ollama` and pull required models:

```bash
ollama run nomic-embed-text
ollama run llama3.2
```

4. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

---

## 🔌 Endpoints

### `GET /scrape?start_url=<optional_url>`

Scrapes Snowflake docs (defaults to homepage). Stores pages as JSON in `./snowflake_docs`.

### `GET /load_data`

Loads scraped JSON files into MongoDB with vector embeddings using `nomic-embed-text`.

### `POST /question`

Submit a query and get a response based on relevant document context and `llama3.2`.

**Request Body (as form or query parameter):**

```json
{
  "query": "How do I create a table in Snowflake?"
}
```

### `DELETE /delete`

Deletes all documents in the `SNOWFLAKE_DOC` collection.

### `GET /`

Health check. Returns `{"message": "Hello World"}`.

---

## 📁 Folder Structure

```
.
├── main.py                # FastAPI app
├── snowflake_docs/        # Stores scraped JSON doc pages
├── .env                   # MongoDB credentials
├── requirements.txt       # Python dependencies
└── README.md              # You are here
```

---

## 🧠 How It Works

1. **Scrape:** Pull docs from Snowflake, parse titles, headers, paragraphs, and links.
2. **Store:** Save pages locally in JSON and in MongoDB Atlas.
3. **Embed:** Create dense vector representations of page content.
4. **Query:** Convert user input into a vector, retrieve relevant docs, and use them as context for an LLM to answer the question.

---

## ✨ Future Ideas

- Add streaming responses to `/question`
- Add authentication
- Support scraping other technical sites
- Export RAG conversations to logs or dashboards

---

## 🧑‍💻 Author

Made by [Your Name](https://github.com/yourusername)  
Feel free to reach out or open an issue!

---

## 📜 License

MIT License

```

Let me know if you'd like a `requirements.txt` to go with this, or want help publishing it to GitHub!
```
