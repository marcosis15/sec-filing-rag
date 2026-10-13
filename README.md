# SEC 10-K Filing RAG

Ask plain-English questions about Tesla's latest annual report (10-K) and get answers grounded in the filing's own text.

This is a retrieval-augmented generation (RAG) pipeline written in Python. It downloads the filing from SEC EDGAR, cleans and splits it into passages, stores their embeddings in a vector database, and, for each question, retrieves the most relevant passages and has an LLM answer from them.

## How it works

```
SEC EDGAR  ->  clean HTML  ->  chunk  ->  embed  ->  ChromaDB
                                                        |
question -> embed -> top-3 similar chunks -> Gemini -> answer
```

1. **Fetch.** Calls the SEC EDGAR submissions API for Tesla (CIK 0001318605), finds the most recent 10-K, and downloads the filing's HTML.
2. **Clean.** BeautifulSoup removes scripts, styles, and hidden elements and returns plain text, saved to `data/`.
3. **Chunk.** Splits the text into 1,000-character passages with a 200-character overlap, so sentences cut at a boundary still appear whole in a neighboring chunk. The FY2025 filing produced 495 chunks.
4. **Embed.** Each chunk becomes a 1,024-dimensional vector with Voyage AI's `voyage-4` model, sent in batches of 10.
5. **Store.** Vectors and text are saved in a persistent ChromaDB collection (`tesla_10k`). The index is built once and reused on later runs.
6. **Retrieve.** The question is embedded the same way, and the 3 closest chunks are returned.
7. **Generate.** The retrieved passages and the question are sent to Gemini, which answers using that context.

## Setup

Requires Python 3.10+ and API keys for [Voyage AI](https://www.voyageai.com/) and [Google Gemini](https://ai.google.dev/).

```bash
git clone https://github.com/marcosis15/sec-filing-rag.git
cd sec-filing-rag
python -m venv venv
venv\Scripts\activate          # Windows (use: source venv/bin/activate on Mac/Linux)
pip install requests beautifulsoup4 python-dotenv voyageai chromadb google-genai
```

Create a `.env` file in the project folder:

```
VOYAGE_API_KEY=your-voyage-key
GEMINI_API_KEY=your-gemini-key
```

The SEC asks every script to identify itself. In `fetch_filings.py`, set the `User-Agent` header to your own name and email.

## Run

```bash
python fetch_filings.py
```

The first run downloads and indexes the filing (about a minute, mostly embedding calls). Later runs reuse the saved index and go straight to the question at the bottom of the script, which you can change:

```python
print(ask("What was Tesla's total revenue?", collection))
```

### Example

> **Q:** What was Tesla's total revenue?
> **A:** *(paste the answer your run printed here)*

## Limitations

- **One company.** The CIK and file names are hard-coded for Tesla.
- **Simple chunking.** Fixed-size character windows ignore sentence and section boundaries, which can split a table or an idea in half.
- **No citations.** Answers don't yet show which passages they came from, so a reader can't check them against the filing.
- **No evaluation.** I haven't built a set of question/answer pairs to measure retrieval accuracy.
- **LLM availability.** Gemini occasionally returns a 503 "high demand" error; re-running usually fixes it.

## Next steps

- Show the retrieved passages alongside each answer, as citations
- Section-aware chunking that keeps tables and headings together
- Support any company by ticker
- A small Streamlit web interface
- A test set of questions to measure how often the right passage is retrieved

## Stack

Python, Requests, BeautifulSoup, Voyage AI embeddings, ChromaDB, Google Gemini
