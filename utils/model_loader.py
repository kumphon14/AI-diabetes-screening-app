import json
import joblib
import sys
import __main__
from pathlib import Path
from datetime import datetime

from utils.input_preprocessor import (
    BMIRestorationTransformer,
    BloodGlucosePolicyATransformer,
    FeatureDropper,
)


class ModelLoader:
    """
    Production-ready Model Loader
    New deployment design:
    - Main artifact      : calibrated_model.joblib
    - Config             : deployment_config.json
    - Full inference     : done through exported full pipeline
    """

    def __init__(self, model_dir: str = "model", verbose: bool = True):
        self.model_dir = Path(model_dir)

        self.model = None
        self.config = None
        self.selected_features = None
        self.selected_threshold = None

        self._loaded = False
        self.verbose = verbose

    # =========================
    # Logging helper
    # =========================
    def _log(self, message: str):
        if self.verbose:
            print(f"[ModelLoader] {datetime.now().strftime('%H:%M:%S')} | {message}")

    # =========================
    # Public method
    # =========================
    def load(self):
        """Load all model artifacts only once"""
        if self._loaded:
            self._log("Model already loaded. Skipping reload.")
            return self

        self._log("Starting model loading...")

        try:
            self._load_config()
            self._load_model()

            self._loaded = True

            self._log("Model loaded successfully ✅")
            self._print_summary()

        except Exception as e:
            self._log(f"❌ Failed to load model: {str(e)}")
            raise

        return self

    # =========================
    # Internal loaders
    # =========================
    def _load_config(self):
        path = self.model_dir / "deployment_config.json"

        self._log(f"Loading deployment config from {path}")

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.selected_features = self.config.get("selected_features", [])
        self.selected_threshold = float(self.config.get("selected_threshold", 0.50))

        if not self.selected_features:
            raise ValueError("selected_features not found in deployment_config.json")

        self._log(
            f"Config loaded ({len(self.selected_features)} features, "
            f"threshold={self.selected_threshold:.3f})"
        )

    def _register_custom_classes_for_unpickling(self):
        """
        Register custom classes in namespaces referenced by old pickled artifacts.

        This is needed because the exported joblib may reference classes from:
        - __main__
        - utils.predictor
        """
        # Register on __main__
        setattr(__main__, "BMIRestorationTransformer", BMIRestorationTransformer)
        setattr(__main__, "BloodGlucosePolicyATransformer", BloodGlucosePolicyATransformer)
        setattr(__main__, "FeatureDropper", FeatureDropper)

        # Register on utils.predictor if module already exists
        predictor_module = sys.modules.get("utils.predictor")
        if predictor_module is not None:
            setattr(predictor_module, "BMIRestorationTransformer", BMIRestorationTransformer)
            setattr(
                predictor_module,
                "BloodGlucosePolicyATransformer",
                BloodGlucosePolicyATransformer,
            )
            setattr(predictor_module, "FeatureDropper", FeatureDropper)

        self._log("Custom classes registered for unpickling.")

    def _load_model(self):
        path = self.model_dir / "calibrated_model.joblib"

        self._log(f"Loading calibrated pipeline from {path}")

        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        self._register_custom_classes_for_unpickling()
        self.model = joblib.load(path)

        self._log(f"Calibrated model loaded: {type(self.model)}")

    # =========================
    # Summary output
    # =========================
    def _print_summary(self):
        print("\n========== MODEL LOADER SUMMARY ==========")
        print(f"Model directory      : {self.model_dir}")
        print(f"Model artifact       : calibrated_model.joblib")
        print(f"Model type           : {type(self.model)}")
        print(f"Total features       : {len(self.selected_features)}")
        print(f"Selected threshold   : {self.selected_threshold:.3f}")

        print("\nSelected Features:")
        for i, f in enumerate(self.selected_features, 1):
            print(f"{i:2d}. {f}")

        print("==========================================\n")

    # =========================
    # Health check
    # =========================
    def health_check(self):
        """
        Verify all components are loaded and usable
        """
        status = {
            "model_loaded": self.model is not None,
            "config_loaded": self.config is not None,
            "feature_count": len(self.selected_features) if self.selected_features else 0,
            "selected_threshold": self.selected_threshold,
        }

        self._log(f"Health check: {status}")
        return status

    # =========================
    # Debug utilities
    # =========================
    def debug_paths(self):
        """Check required file existence"""
        files = {
            "config": self.model_dir / "deployment_config.json",
            "model": self.model_dir / "calibrated_model.joblib",
        }

        print("\n=== FILE PATH DEBUG ===")
        for name, path in files.items():
            print(f"{name}: {path} | exists={path.exists()}")
        print("========================\n")

    def debug_feature_alignment(self, input_dict: dict):
        """
        Check if input contains required top-level features
        """
        self._ensure_loaded()

        missing = []
        for f in self.selected_features:
            if f not in input_dict:
                missing.append(f)

        print("\n=== FEATURE ALIGNMENT DEBUG ===")
        if missing:
            print("Missing features:", missing)
        else:
            print("All required features present ✅")
        print("===============================\n")

    # =========================
    # Getters
    # =========================
    def get_model(self):
        self._ensure_loaded()
        return self.model

    def get_config(self):
        self._ensure_loaded()
        return self.config

    def get_selected_features(self):
        self._ensure_loaded()
        return self.selected_features

    def get_selected_threshold(self):
        self._ensure_loaded()
        return self.selected_threshold

    # =========================
    # Safety check
    # =========================
    def _ensure_loaded(self):
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call .load() first.")


# =========================
# Singleton instance
# =========================
_model_loader_instance = None


def get_model_loader(verbose: bool = True):
    global _model_loader_instance

    if _model_loader_instance is None:
        _model_loader_instance = ModelLoader(verbose=verbose).load()

    return _model_loader_instance