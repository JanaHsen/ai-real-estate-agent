import anthropic
import json
import os
from fastapi import FastAPI
from app.schemas import QueryRequest, PredictionResponse, ExtractedFeatures
from app.prompts import STAGE1_PROMPT, STAGE2_PROMPT
from app.prediction import predict_price, TRAIN_STATS

app = FastAPI(title="AI Real Estate Agent", version="1.0")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SUGGESTIONS = [
    "Living area size (e.g., '1500 sqft')",
    "Number of bedrooms and bathrooms",
    "Kitchen quality (e.g., 'nice kitchen', 'outdated kitchen')",
    "Garage (e.g., '2-car finished garage')",
    "Neighborhood in Ames (e.g., 'Edwards', 'Stone Brook')",
    "Year built (e.g., 'built in 1995')",
    "Fireplaces (e.g., '2 fireplaces')",
    "Overall condition (e.g., 'well-maintained', 'needs work')"
]

EXAMPLE = "Try something like: 'A 1500 sqft house in Edwards with 2 bathrooms, a nice kitchen, and a 2-car garage, built in 1995'"


def extract_features(query: str) -> ExtractedFeatures:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=STAGE1_PROMPT,
        messages=[{"role": "user", "content": query}]
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return ExtractedFeatures(**json.loads(raw.strip()))


def interpret_prediction(features: ExtractedFeatures, price: float) -> str:
    non_null = {k: v for k, v in features.model_dump().items()
                if k not in ["extracted_fields", "missing_fields"] and v is not None}
    
    user_msg = f"""Property features: {json.dumps(non_null, indent=2)}
Predicted price: ${price:,.0f}
Market statistics: {json.dumps(TRAIN_STATS, indent=2)}
Missing features: {features.missing_fields}
Please interpret this prediction for the homebuyer."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=STAGE2_PROMPT,
        messages=[{"role": "user", "content": user_msg}]
    )
    return response.content[0].text


@app.post("/predict", response_model=PredictionResponse)
def predict(request: QueryRequest):
    # Handle empty input
    if not request.query.strip():
        return PredictionResponse(
            success=False,
            message="You haven't written anything!",
            suggestions=SUGGESTIONS,
            example=EXAMPLE
        )

    try:
        # Stage 1: Extract
        features = extract_features(request.query)

        # Handle gibberish
        if len(features.extracted_fields) == 0:
            return PredictionResponse(
                success=False,
                message="I couldn't find any property details in your description.",
                suggestions=SUGGESTIONS,
                example=EXAMPLE
            )

        # Predict
        price = predict_price(features)

        # Stage 2: Interpret
        interpretation = interpret_prediction(features, price)

        return PredictionResponse(
            success=True,
            features=features,
            predicted_price=price,
            interpretation=interpretation,
            confidence_note=f"Based on {len(features.extracted_fields)}/12 features. "
                           f"{len(features.missing_fields)} features were filled with defaults."
        )

    except Exception as e:
        return PredictionResponse(
            success=False,
            message="Something went wrong. Please try again.",
            suggestions=SUGGESTIONS,
            example=EXAMPLE
        )