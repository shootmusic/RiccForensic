"""
Face Processing Engine
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict
import hashlib
import urllib.request
import zipfile
import os

class FaceEngine:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.analyzer = None
        self._init()
    
    def _init(self):
        try:
            import insightface
            from insightface.app import FaceAnalysis
            
            model_name = 'antelopev2'
            model_path = self.models_dir / model_name
            
            # Auto-download kalau model gak ada
            if not model_path.exists():
                self._download_model(model_name)
            
            self.analyzer = FaceAnalysis(
                name=model_name,
                root=str(self.models_dir),
                providers=['CPUExecutionProvider']
            )
            self.analyzer.prepare(ctx_id=0, det_size=(640, 640))
            print(f"[FaceEngine] {model_name} loaded")
            
        except Exception as e:
            print(f"[FaceEngine] Error: {e}")
            self.analyzer = None
    
    def _download_model(self, model_name: str):
        """Auto-download model kalau gak ada"""
        url = f"https://github.com/deepinsight/insightface/releases/download/v0.7/{model_name}.zip"
        zip_path = self.models_dir / f"{model_name}.zip"
        
        print(f"[FaceEngine] Downloading {model_name} (~300MB)...")
        print(f"[FaceEngine] URL: {url}")
        
        try:
            # Cek space
            stat = os.statvfs(self.models_dir)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_gb < 0.5:
                raise Exception(f"Disk space low: {free_gb:.1f}GB free. Need ~300MB.")
            
            # Download
            urllib.request.urlretrieve(url, zip_path)
            print(f"[FaceEngine] Extracting...")
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(self.models_dir)
            
            # Hapus zip
            zip_path.unlink()
            print(f"[FaceEngine] {model_name} ready")
            
        except Exception as e:
            print(f"[FaceEngine] Download failed: {e}")
            print(f"[FaceEngine] Please download manually:")
            print(f"  cd models && wget {url} && unzip {model_name}.zip")
            raise
    
    def process(self, image_path: str) -> Dict:
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Cannot load image"}
        
        faces = self._detect(img)
        
        if not faces:
            enhanced = self._enhance(img)
            faces = self._detect(enhanced)
            
            if not faces:
                return {
                    "success": False,
                    "error": "No face detected",
                    "suggestions": ["Use clearer photo", "Front-facing view", "Avoid obstructions"]
                }
        
        target = self._select_best(faces)
        return self._extract(img, target)
    
    def _detect(self, img: np.ndarray) -> List:
        if not self.analyzer:
            return []
        return self.analyzer.get(img)
    
    def _select_best(self, faces: List):
        return max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]) * f.det_score)
    
    def _extract(self, img: np.ndarray, face) -> Dict:
        x1, y1, x2, y2 = map(int, face.bbox)
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        crop = img[y1:y2, x1:x2]
        emb = face.embedding
        face_hash = self._hash(emb)
        
        return {
            "success": True,
            "hash": face_hash,
            "embedding": emb.tolist(),
            "confidence": float(face.det_score),
            "bbox": [x1, y1, x2, y2],
            "crop": crop,
            "landmarks": face.landmark_2d_106.tolist() if hasattr(face, 'landmark_2d_106') else []
        }
    
    def _hash(self, embedding: np.ndarray) -> str:
        normalized = embedding / np.linalg.norm(embedding)
        quantized = np.round(normalized * 1000).astype(np.int32)
        return hashlib.sha256(quantized.tobytes()).hexdigest()[:16]
    
    def _enhance(self, img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    def compare(self, img1_path: str, img2_path: str) -> Dict:
        r1 = self.process(img1_path)
        r2 = self.process(img2_path)
        
        if not r1.get("success") or not r2.get("success"):
            return {"match": False, "error": "Face processing failed"}
        
        emb1 = np.array(r1["embedding"])
        emb2 = np.array(r2["embedding"])
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return {
            "match": similarity > 0.65,
            "similarity": float(similarity),
            "confidence": float(similarity * 100),
            "threshold": 0.65,
            "verdict": "SAME PERSON" if similarity > 0.65 else "DIFFERENT PERSON"
        }
    
    def save(self, face_data: Dict, output_path: str):
        cv2.imwrite(output_path, face_data["crop"])
