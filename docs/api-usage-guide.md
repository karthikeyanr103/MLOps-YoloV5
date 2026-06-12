# API Usage Guide

## Interactive Documentation

Run the service and open:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## Upload Request

All prediction endpoints accept multipart form data with one `file` field.
JPEG, PNG, and WebP files up to 10 MB are accepted.

```bash
curl -X POST "http://localhost:8000/api/v1/classification/predict" \
  -F "file=@sample.jpg"
```

```python
import requests

with open("sample.jpg", "rb") as image:
    response = requests.post(
        "http://localhost:8000/api/v1/object-detection/predict",
        files={"file": ("sample.jpg", image, "image/jpeg")},
        timeout=30,
    )
response.raise_for_status()
print(response.json())
```

## Sample Responses

Classification:

```json
{"task":"classification","model_status":"yolov5s","prediction_type":"detected_scene_objects","predictions":[{"label":"person","confidence":0.94}]}
```

Counting:

```json
{"task":"counting","model_status":"yolov5s","total_count":3,"counts_by_class":{"person":2,"car":1}}
```

Segmentation:

```json
{"task":"segmentation","model_status":"yolov5s-seg","segments":[{"label":"person","class_id":0,"confidence":0.91,"coverage_percent":18.4,"box":{"x_min":80,"y_min":42,"x_max":390,"y_max":610}}],"overlay":"data:image/png;base64,..."}
```

The `overlay` field is a transparent PNG data URL containing the decoded
instance masks. Object detection:

```json
{"task":"object_detection","model_status":"yolov5s","detections":[{"label":"person","class_id":0,"confidence":0.92,"box":{"x_min":96,"y_min":86,"x_max":461,"y_max":389}}]}
```

`model_status` identifies the active detector (`yolov5s`) or segmentation
model (`yolov5s-seg`).

## Errors

| Status | Meaning |
| --- | --- |
| `400` | Empty or invalid image |
| `413` | Upload exceeds 10 MB |
| `415` | Unsupported content type |
| `422` | Missing multipart `file` field |
| `500` | Model loading or inference failure |
