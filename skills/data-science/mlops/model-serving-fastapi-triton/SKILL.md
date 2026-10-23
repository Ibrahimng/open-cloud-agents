---
name: model-serving-fastapi-triton
description: Architect and deploy production machine learning inference servers with dynamic batching, GPU acceleration, health checks, and ONNX Runtime / Triton integration.
---

# Production ML Model Serving Architecture

## Key Requirements for Low-Latency Inference
1. **Dynamic Request Batching**: Group concurrent single-item incoming HTTP requests into a single tensor batch to maximize GPU/CPU vectorization efficiency.
2. **Model Serialization**: Export trained PyTorch / TensorFlow weights to **ONNX** or **TensorRT** for optimized runtime kernels and cross-framework portability.
3. **Warm-up Requests**: Run synthetic forward passes during container startup before declaring the pod healthy in `readinessProbe`.

## Reference ONNX Runtime Inference Service (Python)

```python
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="ML Inference Service")

# Load model session once at application startup
session = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

class PredictRequest(BaseModel):
    features: List[float]

class PredictResponse(BaseModel):
    prediction: float
    confidence: float

@app.post("/v1/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    input_tensor = np.array([request.features], dtype=np.float32)
    outputs = session.run(None, {input_name: input_tensor})
    logits = outputs[0][0]
    
    # Softmax / Sigmoid output extraction
    prob = 1.0 / (1.0 + np.exp(-logits))
    return PredictResponse(prediction=round(float(prob)), confidence=float(prob))

@app.get("/healthz")
def health():
    return {"status": "ready"}
```

