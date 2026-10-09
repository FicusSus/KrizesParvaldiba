"""
Crisis Prediction Service

This service implements crisis prediction using machine learning models.
It provides interfaces for training models, making predictions, and evaluating results.
"""

import asyncio
import json
import logging
import os
import pickle
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import polars as pl
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError
import structlog

from app.core.config import settings
from app.core.logger import get_logger
from app.models.crisis import CrisisSeverity, CrisisType
from app.services.data_processor import DataProcessor

logger = get_logger(__name__)


class CrisisPredictor:
    """
    Crisis prediction service using machine learning models.
    
    Features:
    - Multiple model types for different prediction tasks
    - Model training, saving, and loading
    - Real-time predictions
    - Model evaluation and metrics
    - Feature importance analysis
    """
    
    # Model types
    MODEL_TYPES = {
        "crisis_detection": "Crisis Detection Model",
        "severity_prediction": "Crisis Severity Prediction Model",
        "timeline_prediction": "Crisis Timeline Prediction Model",
        "impact_assessment": "Crisis Impact Assessment Model",
    }
    
    def __init__(self):
        """Initialize the crisis predictor."""
        self.models = {}  # Dict to store loaded models
        self.scalers = {}  # Dict to store feature scalers
        self.label_encoders = {}  # Dict to store label encoders
        self.data_processor = DataProcessor()
        self.model_dir = settings.MODEL_SAVE_PATH
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
    async def train_model(
        self,
        dataset_path: str,
        model_type: str = "crisis_detection",
        target_column: str = "crisis",
        features: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Train a crisis prediction model.
        
        Args:
            dataset_path: Path to training data
            model_type: Type of model to train
            target_column: Target column for supervised learning
            features: List of feature columns to use
            config: Training configuration
            test_size: Fraction of data to use for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Dict: Training results and metrics
        """
        logger.info("Training crisis prediction model", 
                   model_type=model_type, 
                   dataset_path=dataset_path)
        
        start_time = datetime.now()
        
        result = {
            "success": False,
            "model_type": model_type,
            "target_column": target_column,
            "features": features or [],
            "start_time": start_time.isoformat(),
            "end_time": None,
            "training_time": 0.0,
            "row_count": 0,
            "feature_count": 0,
            "metrics": {},
            "model_info": {},
            "error": None,
        }
        
        try:
            # Load and preprocess data
            df, metadata = await self._load_and_preprocess_data(
                dataset_path, features, config
            )
            
            result["row_count"] = metadata["row_count"]
            result["features"] = metadata["features"]
            result["feature_count"] = len(metadata["features"])
            
            # Split data
            if isinstance(df, pl.DataFrame):
                df = df.to_pandas()
            
            X = df[metadata["features"]]
            y = df[target_column]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=test_size, 
                random_state=random_state,
                stratify=y if len(y.unique()) < 10 else None  # Stratify for classification
            )
            
            # Get model configuration
            model_config = self._get_model_config(model_type, config)
            
            # Create and train model
            model = self._create_model(model_type, model_config)
            
            # Train the model
            logger.info("Starting model training")
            model.fit(X_train, y_train)
            
            # Evaluate model
            logger.info("Evaluating model")
            y_pred = model.predict(X_test)
            
            metrics = self._calculate_metrics(y_test, y_pred, model_type)
            result["metrics"] = metrics
            
            # Get model info
            model_info = self._get_model_info(model, model_type, model_config)
            result["model_info"] = model_info
            
            # Save the model
            model_name = f"{model_type}_{start_time.strftime('%Y%m%d_%H%M%S')}"
            await self.save_model(model, model_name, model_type, metadata)
            
            result["success"] = True
            result["model_name"] = model_name
            
        except Exception as e:
            logger.error("Model training failed", error=str(e))
            result["error"] = str(e)
            result["success"] = False
            
        finally:
            result["end_time"] = datetime.now().isoformat()
            result["training_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info("Model training completed", 
                   success=result["success"], 
                   training_time=result["training_time"])
        
        return result
    
    async def predict(
        self,
        data: Union[pd.DataFrame, pl.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
        model_type: str = "crisis_detection",
        model_version: str = "latest"
    ) -> Dict[str, Any]:
        """
        Make crisis predictions using a trained model.
        
        Args:
            data: Input data for prediction
            model_type: Type of model to use
            model_version: Version of model to use (or 'latest')
            
        Returns:
            Dict: Prediction results
        """
        logger.info("Making crisis prediction", model_type=model_type)
        
        start_time = datetime.now()
        
        result = {
            "success": False,
            "model_type": model_type,
            "model_version": model_version,
            "start_time": start_time.isoformat(),
            "end_time": None,
            "prediction_time": 0.0,
            "predictions": [],
            "probabilities": [],
            "error": None,
        }
        
        try:
            # Load the model
            model, model_info, scaler, label_encoders = await self.load_model(
                model_type, model_version
            )
            
            if model is None:
                raise ValueError(f"Model {model_type} ({model_version}) not found")
            
            # Prepare input data
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, list):
                data = pd.DataFrame(data)
            elif isinstance(data, dict):
                data = pd.DataFrame([data])
            
            # Check if we have the expected features
            expected_features = model_info.get("features", [])
            available_features = list(data.columns)
            
            missing_features = [f for f in expected_features if f not in available_features]
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            
            # Use only the expected features
            data = data[expected_features]
            
            # Preprocess data using the same scaler/encoders
            if scaler:
                data = scaler.transform(data)
            
            # Make predictions
            logger.info("Running predictions")
            
            if hasattr(model, "predict_proba"):
                # Classification model
                predictions = model.predict(data)
                probabilities = model.predict_proba(data)
                
                result["predictions"] = predictions.tolist()
                result["probabilities"] = probabilities.tolist()
            else:
                # Regression or other model
                predictions = model.predict(data)
                result["predictions"] = predictions.tolist()
            
            result["success"] = True
            
        except Exception as e:
            logger.error("Prediction failed", error=str(e))
            result["error"] = str(e)
            result["success"] = False
            
        finally:
            result["end_time"] = datetime.now().isoformat()
            result["prediction_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info("Prediction completed", 
                   success=result["success"], 
                   prediction_time=result["prediction_time"])
        
        return result
    
    async def _load_and_preprocess_data(
        self,
        dataset_path: str,
        features: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[Union[pd.DataFrame, pl.DataFrame], Dict[str, Any]]:
        """Load and preprocess data for training."""
        # Load data
        dataset_path_obj = Path(dataset_path)
        
        if dataset_path_obj.suffix == ".csv":
            df = pl.read_csv(dataset_path)
        elif dataset_path_obj.suffix == ".json":
            df = pl.read_ndjson(dataset_path)
        elif dataset_path_obj.suffix == ".parquet":
            df = pl.read_parquet(dataset_path)
        elif dataset_path_obj.suffix in [".xlsx", ".xls"]:
            df = pl.read_excel(dataset_path)
        else:
            raise ValueError(f"Unsupported file type: {dataset_path_obj.suffix}")
        
        # Clean data
        df = await self.data_processor.clean_data(df, config)
        
        # Extract features
        df = await self.data_processor.extract_features(df, config)
        
        # Determine features if not specified
        if features is None:
            # Exclude common non-feature columns
            exclude_columns = ["id", "date", "timestamp", "created_at", "updated_at"]
            features = [col for col in df.columns if col not in exclude_columns]
        
        # Ensure all specified features exist
        available_features = list(df.columns)
        valid_features = [f for f in features if f in available_features]
        
        metadata = {
            "row_count": df.height,
            "column_count": df.width,
            "features": valid_features,
            "columns": list(df.columns),
        }
        
        return df, metadata
    
    def _get_model_config(
        self,
        model_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get model configuration based on model type."""
        if config is None:
            config = {}
        
        default_configs = {
            "crisis_detection": {
                "algorithm": "random_forest",
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42,
                "class_weight": "balanced",
            },
            "severity_prediction": {
                "algorithm": "gradient_boosting",
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 5,
                "random_state": 42,
            },
            "timeline_prediction": {
                "algorithm": "random_forest",
                "n_estimators": 100,
                "max_depth": 8,
                "random_state": 42,
            },
            "impact_assessment": {
                "algorithm": "gradient_boosting",
                "n_estimators": 150,
                "learning_rate": 0.05,
                "max_depth": 6,
                "random_state": 42,
            },
        }
        
        # Merge default config with provided config
        default_config = default_configs.get(model_type, {})
        return {**default_config, **config}
    
    def _create_model(
        self,
        model_type: str,
        config: Dict[str, Any]
    ) -> BaseEstimator:
        """Create a model based on configuration."""
        algorithm = config.get("algorithm", "random_forest")
        
        if algorithm == "random_forest":
            model = RandomForestClassifier(
                n_estimators=config.get("n_estimators", 100),
                max_depth=config.get("max_depth", 10),
                random_state=config.get("random_state", 42),
                class_weight=config.get("class_weight", "balanced"),
                n_jobs=-1,  # Use all available cores
            )
        elif algorithm == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=config.get("n_estimators", 100),
                learning_rate=config.get("learning_rate", 0.1),
                max_depth=config.get("max_depth", 5),
                random_state=config.get("random_state", 42),
            )
        else:
            # Default to random forest
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1,
            )
        
        return model
    
    def _calculate_metrics(
        self,
        y_true,
        y_pred,
        model_type: str
    ) -> Dict[str, float]:
        """Calculate evaluation metrics for the model."""
        metrics = {}
        
        try:
            if model_type in ["crisis_detection", "severity_prediction"]:
                # Classification metrics
                metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
                metrics["f1_score"] = float(f1_score(y_true, y_pred, average="weighted"))
                metrics["precision"] = float(precision_score(y_true, y_pred, average="weighted"))
                metrics["recall"] = float(recall_score(y_true, y_pred, average="weighted"))
                
                # Per-class metrics for binary classification
                if len(y_true.unique()) == 2:
                    metrics["f1_binary"] = float(f1_score(y_true, y_pred))
                    metrics["precision_binary"] = float(precision_score(y_true, y_pred))
                    metrics["recall_binary"] = float(recall_score(y_true, y_pred))
                    
            else:
                # For now, use classification metrics for all
                # In production, you might have different metrics for regression
                metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
                metrics["f1_score"] = float(f1_score(y_true, y_pred, average="weighted"))
                
        except Exception as e:
            logger.warning("Failed to calculate metrics", error=str(e))
            metrics["error"] = str(e)
        
        return metrics
    
    def _get_model_info(
        self,
        model: BaseEstimator,
        model_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get information about the trained model."""
        info = {
            "model_type": model_type,
            "algorithm": config.get("algorithm", "unknown"),
            "config": config,
            "feature_importances": [],
        }
        
        # Get feature importances if available
        if hasattr(model, "feature_importances_"):
            try:
                importances = model.feature_importances_
                feature_names = model.feature_names_in_ if hasattr(model, "feature_names_in_") else []
                
                info["feature_importances"] = [
                    {"feature": name, "importance": float(imp)}
                    for name, imp in zip(feature_names, importances)
                ]
                
                # Sort by importance
                info["feature_importances"].sort(key=lambda x: x["importance"], reverse=True)
                
            except Exception as e:
                logger.warning("Failed to get feature importances", error=str(e))
        
        # Get other model attributes
        if hasattr(model, "classes_"):
            info["classes"] = model.classes_.tolist()
        if hasattr(model, "n_classes_"):
            info["n_classes"] = int(model.n_classes_)
        if hasattr(model, "n_features_in_"):
            info["n_features"] = int(model.n_features_in_)
        
        return info
    
    async def save_model(
        self,
        model: BaseEstimator,
        model_name: str,
        model_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Save a trained model to disk."""
        logger.info("Saving model", model_name=model_name, model_type=model_type)
        
        model_dir = self.model_dir / model_type
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model file
        model_path = model_dir / f"{model_name}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        
        # Save metadata
        metadata_path = model_dir / f"{model_name}_metadata.json"
        metadata["saved_at"] = datetime.now().isoformat()
        metadata["model_path"] = str(model_path)
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create version file
        version_path = model_dir / "versions.txt"
        with open(version_path, "a") as f:
            f.write(f"{model_name}\n")
        
        logger.info("Model saved successfully", path=str(model_path))
        return str(model_path)
    
    async def load_model(
        self,
        model_type: str,
        model_version: str = "latest"
    ) -> Tuple[Optional[BaseEstimator], Optional[Dict[str, Any]], Optional[Any], Optional[Dict[str, Any]]]:
        """
        Load a trained model from disk.
        
        Returns:
            Tuple of (model, metadata, scaler, label_encoders)
        """
        logger.info("Loading model", model_type=model_type, model_version=model_version)
        
        model_dir = self.model_dir / model_type
        
        if not model_dir.exists():
            logger.warning("Model directory not found", path=str(model_dir))
            return None, None, None, None
        
        # Get list of available models
        version_file = model_dir / "versions.txt"
        if not version_file.exists():
            logger.warning("No versions file found")
            return None, None, None, None
        
        with open(version_file, "r") as f:
            versions = [line.strip() for line in f.readlines() if line.strip()]
        
        if not versions:
            logger.warning("No model versions found")
            return None, None, None, None
        
        # Find the requested version
        if model_version == "latest":
            # Sort versions by timestamp (assuming format includes timestamp)
            versions.sort(reverse=True)
            selected_version = versions[0]
        else:
            if model_version not in versions:
                logger.warning("Model version not found", version=model_version)
                return None, None, None, None
            selected_version = model_version
        
        # Load model
        model_path = model_dir / f"{selected_version}.pkl"
        if not model_path.exists():
            logger.warning("Model file not found", path=str(model_path))
            return None, None, None, None
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            
            # Load metadata
            metadata_path = model_dir / f"{selected_version}_metadata.json"
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
            
            logger.info("Model loaded successfully", path=str(model_path))
            return model, metadata, None, None  # scaler and label_encoders would be loaded if they exist
            
        except Exception as e:
            logger.error("Failed to load model", error=str(e), path=str(model_path))
            return None, None, None, None
    
    async def list_models(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """List available models."""
        result = {"models": [], "total": 0}
        
        if model_type:
            # List models of specific type
            model_dir = self.model_dir / model_type
            if model_dir.exists():
                version_file = model_dir / "versions.txt"
                if version_file.exists():
                    with open(version_file, "r") as f:
                        versions = [line.strip() for line in f.readlines() if line.strip()]
                    
                    for version in versions:
                        metadata_path = model_dir / f"{version}_metadata.json"
                        if metadata_path.exists():
                            with open(metadata_path, "r") as f:
                                metadata = json.load(f)
                            result["models"].append({
                                "name": version,
                                "type": model_type,
                                "path": str(model_dir / f"{version}.pkl"),
                                "saved_at": metadata.get("saved_at"),
                                "features": metadata.get("features", []),
                            })
        else:
            # List all models
            for model_type_dir in self.model_dir.iterdir():
                if model_type_dir.is_dir():
                    version_file = model_type_dir / "versions.txt"
                    if version_file.exists():
                        with open(version_file, "r") as f:
                            versions = [line.strip() for line in f.readlines() if line.strip()]
                        
                        for version in versions:
                            metadata_path = model_type_dir / f"{version}_metadata.json"
                            if metadata_path.exists():
                                with open(metadata_path, "r") as f:
                                    metadata = json.load(f)
                                result["models"].append({
                                    "name": version,
                                    "type": model_type_dir.name,
                                    "path": str(model_type_dir / f"{version}.pkl"),
                                    "saved_at": metadata.get("saved_at"),
                                    "features": metadata.get("features", []),
                                })
        
        result["total"] = len(result["models"])
        return result
    
    async def predict_crisis_severity(
        self,
        data: Union[pd.DataFrame, pl.DataFrame, Dict[str, Any]],
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Predict crisis severity using a specialized model.
        
        Args:
            data: Input data with crisis features
            features: List of feature columns to use
            
        Returns:
            Dict: Prediction results with severity and confidence
        """
        result = await self.predict(data, "severity_prediction", "latest")
        
        # Map predictions to CrisisSeverity enum
        severity_map = {
            "low": CrisisSeverity.LOW,
            "medium": CrisisSeverity.MEDIUM,
            "high": CrisisSeverity.HIGH,
            "critical": CrisisSeverity.CRITICAL,
        }
        
        predictions = []
        for i, pred in enumerate(result.get("predictions", [])):
            severity = severity_map.get(str(pred).lower(), CrisisSeverity.MEDIUM)
            confidence = 0.8  # Placeholder - get from probabilities if available
            
            if result.get("probabilities") and i < len(result["probabilities"]):
                probs = result["probabilities"][i]
                if isinstance(probs, list) and len(probs) > 0:
                    confidence = float(max(probs))
            
            predictions.append({
                "severity": severity.value,
                "severity_enum": severity,
                "confidence": confidence,
                "raw_prediction": pred,
            })
        
        result["severity_predictions"] = predictions
        return result
    
    async def predict_crisis_type(
        self,
        data: Union[pd.DataFrame, pl.DataFrame, Dict[str, Any]],
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Predict crisis type using a specialized model.
        
        Args:
            data: Input data with crisis features
            features: List of feature columns to use
            
        Returns:
            Dict: Prediction results with crisis type and confidence
        """
        result = await self.predict(data, "crisis_detection", "latest")
        
        # Map predictions to CrisisType enum
        type_map = {
            "financial": CrisisType.FINANCIAL,
            "economic": CrisisType.ECONOMIC,
            "political": CrisisType.POLITICAL,
            "social": CrisisType.SOCIAL,
            "environmental": CrisisType.ENVIRONMENTAL,
            "health": CrisisType.HEALTH,
            "security": CrisisType.SECURITY,
        }
        
        predictions = []
        for i, pred in enumerate(result.get("predictions", [])):
            crisis_type = type_map.get(str(pred).lower(), CrisisType.OTHER)
            confidence = 0.8  # Placeholder
            
            if result.get("probabilities") and i < len(result["probabilities"]):
                probs = result["probabilities"][i]
                if isinstance(probs, list) and len(probs) > 0:
                    confidence = float(max(probs))
            
            predictions.append({
                "type": crisis_type.value,
                "type_enum": crisis_type,
                "confidence": confidence,
                "raw_prediction": pred,
            })
        
        result["type_predictions"] = predictions
        return result