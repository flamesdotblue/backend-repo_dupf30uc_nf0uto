import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr, conint, confloat

app = FastAPI(title="Overlay Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Overlay(BaseModel):
    id: int
    name: constr(min_length=1, max_length=100)
    type: constr(min_length=1)  # e.g., 'text' | 'image' | 'box'
    x: confloat(ge=0, le=100) = 10.0  # percentage
    y: confloat(ge=0, le=100) = 10.0  # percentage
    w: confloat(ge=0, le=100) = 20.0  # percentage
    h: confloat(ge=0, le=100) = 10.0  # percentage
    opacity: confloat(ge=0.0, le=1.0) = 1.0
    color: constr(min_length=1) = "#ff0000"
    content: Optional[str] = None  # text or image URL
    visible: bool = True


class OverlayCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    type: constr(min_length=1)
    x: confloat(ge=0, le=100) = 10.0
    y: confloat(ge=0, le=100) = 10.0
    w: confloat(ge=0, le=100) = 20.0
    h: confloat(ge=0, le=100) = 10.0
    opacity: confloat(ge=0.0, le=1.0) = 1.0
    color: constr(min_length=1) = "#ff0000"
    content: Optional[str] = None
    visible: bool = True


class OverlayUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    type: Optional[constr(min_length=1)] = None
    x: Optional[confloat(ge=0, le=100)] = None
    y: Optional[confloat(ge=0, le=100)] = None
    w: Optional[confloat(ge=0, le=100)] = None
    h: Optional[confloat(ge=0, le=100)] = None
    opacity: Optional[confloat(ge=0.0, le=1.0)] = None
    color: Optional[constr(min_length=1)] = None
    content: Optional[str] = None
    visible: Optional[bool] = None


# In-memory storage
_overlays: List[Overlay] = []
_next_id: int = 1


@app.get("/")
def read_root():
    return {"message": "Overlay Manager API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/overlays", response_model=List[Overlay])
def list_overlays():
    return _overlays


@app.post("/api/overlays", response_model=Overlay, status_code=201)
def create_overlay(payload: OverlayCreate):
    global _next_id
    overlay = Overlay(id=_next_id, **payload.dict())
    _next_id += 1
    _overlays.append(overlay)
    return overlay


@app.get("/api/overlays/{overlay_id}", response_model=Overlay)
def get_overlay(overlay_id: int):
    for ov in _overlays:
        if ov.id == overlay_id:
            return ov
    raise HTTPException(status_code=404, detail="Overlay not found")


@app.put("/api/overlays/{overlay_id}", response_model=Overlay)
def update_overlay(overlay_id: int, payload: OverlayUpdate):
    for idx, ov in enumerate(_overlays):
        if ov.id == overlay_id:
            data = ov.dict()
            updates = {k: v for k, v in payload.dict().items() if v is not None}
            data.update(updates)
            updated = Overlay(**data)
            _overlays[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Overlay not found")


@app.delete("/api/overlays/{overlay_id}", status_code=204)
def delete_overlay(overlay_id: int):
    global _overlays
    for idx, ov in enumerate(_overlays):
        if ov.id == overlay_id:
            _overlays.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Overlay not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
