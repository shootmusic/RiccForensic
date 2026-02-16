"""
Deepfake & Manipulation Detection
"""

import cv2
import numpy as np

class DeepfakeDetector:
    def __init__(self):
        self.methods = ["ela", "noise", "cfa", "copy_move", "face_artifacts"]
    
    def analyze(self, image_path: str) -> dict:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Cannot load image"}
        
        results = {
            "file": image_path,
            "manipulation_score": 0.0,
            "methods": {},
            "verdict": "Authentic"
        }
        
        results["methods"]["ela"] = self._ela(img)
        results["methods"]["noise"] = self._noise(img)
        results["methods"]["cfa"] = self._cfa(img)
        results["methods"]["copy_move"] = self._copy_move(img)
        results["methods"]["face_artifacts"] = self._face_artifacts(img)
        
        scores = [m["score"] for m in results["methods"].values() if "score" in m]
        results["manipulation_score"] = np.mean(scores) if scores else 0
        
        if results["manipulation_score"] > 0.7:
            results["verdict"] = "HIGHLY SUSPICIOUS"
        elif results["manipulation_score"] > 0.4:
            results["verdict"] = "SUSPICIOUS"
        
        return results
    
    def _ela(self, img: np.ndarray, quality: int = 90) -> dict:
        _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        compressed = cv2.imdecode(buf, 1)
        
        diff = cv2.absdiff(img, compressed)
        ela = cv2.multiply(diff, (10, 10, 10, 10))
        gray = cv2.cvtColor(ela, cv2.COLOR_BGR2GRAY)
        score = np.mean(gray) / 255.0
        
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        suspicious = [{"x": x, "y": y, "w": w, "h": h} 
                     for cnt in contours if cv2.contourArea(cnt) > 1000 
                     for x, y, w, h in [cv2.boundingRect(cnt)]]
        
        return {"score": min(score * 2, 1.0), "areas": suspicious[:5]}
    
    def _noise(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        median = cv2.medianBlur(gray, 3)
        diff = cv2.absdiff(gray, median)
        
        h, w = diff.shape
        block_size = 32
        noises = [np.std(diff[y:y+block_size, x:x+block_size]) 
                 for y in range(0, h, block_size) 
                 for x in range(0, w, block_size) 
                 if diff[y:y+block_size, x:x+block_size].size > 0]
        
        return {"score": min(np.std(noises) / 50.0, 1.0), "variance": float(np.std(noises))}
    
    def _cfa(self, img: np.ndarray) -> dict:
        b, g, r = cv2.split(img)
        corr_rg = np.corrcoef(r.flatten(), g.flatten())[0,1]
        corr_bg = np.corrcoef(b.flatten(), g.flatten())[0,1]
        score = 1.0 - ((corr_rg + corr_bg) / 2)
        
        return {"score": max(0, min(score, 1)), "correlations": {"r_g": float(corr_rg), "b_g": float(corr_bg)}}
    
    def _copy_move(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create(nfeatures=1000)
        kp, des = orb.detectAndCompute(gray, None)
        
        if des is None or len(des) < 10:
            return {"score": 0, "matches": 0}
        
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des, des)
        
        suspicious = sum(1 for m in matches 
                        if m.distance < 30 
                        and 20 < np.linalg.norm(np.array(kp[m.queryIdx].pt) - np.array(kp[m.trainIdx].pt)) < 200)
        
        return {"score": min(suspicious / 50.0, 1.0), "matches": suspicious}
    
    def _face_artifacts(self, img: np.ndarray) -> dict:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        artifacts = []
        
        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi)
            
            if len(eyes) == 2:
                eye1 = cv2.resize(roi[eyes[0][1]:eyes[0][1]+eyes[0][3], eyes[0][0]:eyes[0][0]+eyes[0][2]], (50, 30))
                eye2 = cv2.resize(roi[eyes[1][1]:eyes[1][1]+eyes[1][3], eyes[1][0]:eyes[1][0]+eyes[1][2]], (50, 30))
                
                if np.corrcoef(eye1.flatten(), eye2.flatten())[0,1] > 0.95:
                    artifacts.append("symmetric_eyes")
        
        return {"score": len(artifacts) * 0.3, "artifacts": artifacts}
