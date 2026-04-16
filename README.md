# 🏠 AI Real Estate Agent

LLM Prompt Chaining + Supervised ML + Docker Deployment

## Project Overview
An AI-powered real estate agent that takes natural language property descriptions, extracts structured features using an LLM, predicts house prices using an ML model, and explains the prediction in plain English.

## Architecture
Query → LLM Stage 1 (extract features) → ML Model (predict price) → LLM Stage 2 (interpret) → Response

## Dataset
**Ames Housing** — 2,930 residential sales in Ames, Iowa with 80+ features.
- Selected 11 key features based on EDA and correlation analysis
- Engineered 3 features: House Age, Years Since Remod, Total Bath

## ML Pipeline
| Model | Test RMSE | R² |
|---|---|---|
| Ridge | $24,240 | 0.919 |
| Lasso | $24,212 | 0.919 |
| RandomForest | $25,661 | 0.909 |
| **XGBoost** | **$23,651** | **0.923** |

Best model: XGBoost with log-transformed target, 11 engineered features.

## LLM Prompt Chain
- **Stage 1:** Feature extraction from natural language → Pydantic-validated JSON
- **Stage 2:** Price interpretation with market context
- **Prompt Versioning:** V1 (detailed rules) vs V2 (few-shot examples) — V2 won
- **Model:** Claude Sonnet 4.6 via Anthropic API

## Tech Stack
- Python, scikit-learn, XGBoost
- FastAPI + Pydantic
- Anthropic Claude API
- Docker
- Streamlit

## Run Locally

### FastAPI (without Docker)
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker build -t real-estate-agent .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY="-" real-estate-agent
```

### Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

## API Usage
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "A nice house in Edwards with 2 bathrooms and a 2-car garage"}'
```

## Project Structure
ai-real-estate-agent/
├── app/
│   ├── main.py              # FastAPI app
│   ├── schemas.py            # Pydantic schemas
│   ├── prompts.py            # LLM prompts (Stage 1 + Stage 2)
│   └── prediction.py         # Model loading + feature engineering
├── ui/
│   └── streamlit_app.py      # Streamlit frontend
├── Dockerfile
├── requirements.txt
└── README.md

## Author
Jana | SE Factory AI Engineering Bootcamp