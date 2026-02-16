"""
Face Enhancement & Restoration
"""

import cv2
import numpy as np

class FaceEnhancer:
    def __init__(self):
        self.enhancer = None
        self._load()
    
    def _load(self):
        try:
            from gfpgan import GFPGANer
            self.enhancer = GFPGANer(
                model_path='models/GFPGANv1.4.pth',
                upscale=2,
                arch='clean',
                channel_only=False,
                bg_upsampler=None
            )
        except:
            self.enhancer = None
    
    def enhance(self, img: np.ndarray, method: str = "auto") -> np.ndarray:
        if method == "auto":
            method = self._detect_quality(img)
        
        methods = {
            "super_resolution": self._super_res,
            "denoise": self._denoise,
            "deblur": self._deblur,
            "light": self._fix_light
        }
        
        return methods.get(method, self._fix_light)(img)
    
    def _detect_quality(self, img: np.ndarray) -> str:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if blur < 100:
            return "deblur"
        if self._noise(gray) > 10:
            return "denoise"
        if min(img.shape[:2]) < 128:
            return "super_resolution"
        return "light"
    
    def _noise(self, gray: np.ndarray) -> float:
        return np.std(gray) / np.mean(gray)
    
    def _super_res(self, img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]
        upscaled = cv2.resize(img, (w*4, h*4), interpolation=cv2.INTER_LANCZOS4)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        return cv2.filter2D(upscaled, -1, kernel)
    
    def _denoise(self, img: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    def _deblur(self, img: np.ndarray) -> np.ndarray:
        gaussian = cv2.GaussianBlur(img, (0, 0), 3)
        unsharp = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)
        kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
        return cv2.filter2D(unsharp, -1, kernel)
    
    def _fix_light(self, img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    
    def reconstruct(self, partial: np.ndarray) -> np.ndarray:
        h, w = partial.shape[:2]
        cx = w // 2
        
        left = partial[:, :cx]
        right = partial[:, cx:]
        
        left_det = cv2.Laplacian(cv2.cvtColor(left, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        right_det = cv2.Laplacian(cv2.cvtColor(right, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        
        if left_det > right_det * 1.5:
            mirrored = cv2.flip(left, 1)
            return np.hstack([left, mirrored])
        elif right_det > left_det * 1.5:
            mirrored = cv2.flip(right, 1)
            return np.hstack([mirrored, right])
        
        return partial
