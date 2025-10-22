# Smart Heating Predictor ML Engine
# Author: prezes9732

import numpy as np
from datetime import datetime, timedelta
import json
import os
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MLEngine:
    """Machine Learning Engine for Smart Heating Predictor."""
    
    def __init__(self, hass):
        """Initialize the ML Engine."""
        self.hass = hass
        self.model_data = {}
        
    async def predict_heating_demand(self, current_temp, target_temp, outdoor_temp):
        """Predict heating demand based on input parameters."""
        try:
            # Simple prediction logic - to be expanded
            temp_diff = target_temp - current_temp
            outdoor_factor = max(0.1, (20 - outdoor_temp) / 20)
            prediction = max(0, min(100, temp_diff * 10 * outdoor_factor))
            return round(prediction, 2)
        except Exception as e:
            _LOGGER.error("Error in prediction: %s", e)
            return 0.0
            
    async def update_model(self, data):
        """Update the ML model with new data."""
        # Model update logic placeholder
        # Initialize ML engine properties
        self.training_data = []
        self.is_trained = False
        self.learning_mode = True
        self.anomaly_detection_enabled = True
        self.anomaly_threshold = 2.0  # Default 2°C/5min
        self.training_history = []
        
    def add_training_sample(self, features, heat_on_time):
        """Add a training sample."""
        sample = {
            "features": features,
            "heat_on_time": heat_on_time,
            "timestamp": datetime.now().isoformat()
        }
        self.training_data.append(sample)
        _LOGGER.debug(f"Added training sample. Total samples: {len(self.training_data)}")
        
    def train_model(self):
        """Train the ML model with collected data."""
        if len(self.training_data) < 10:
            _LOGGER.warning("Not enough training data. Need at least 10 samples.")
            return False
            
        _LOGGER.info(f"Training model with {len(self.training_data)} samples")
        
        try:
            # Simplified training - in production would use actual ML
            self.model_data["trained_samples"] = len(self.training_data)
            self.model_data["last_training"] = datetime.now().isoformat()
            self.is_trained = True
            
            _LOGGER.info("Model training completed successfully")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error training model: {e}")
            return False
    
    def predict_preheat_time(self, features):
        """Predict required preheat time."""
        if not self.is_trained:
            # Default prediction when not trained
            return 30
            
        # Simplified prediction logic
        temp_diff = features.get("target_temp", 20) - features.get("current_temp", 18)
        outdoor_factor = max(0.5, (20 - features.get("outdoor_temp", 10)) / 20)
        
        preheat_time = max(5, min(120, temp_diff * 10 * outdoor_factor))
        return round(preheat_time)
    
    def collect_features(self, thermostat_data, weather_temp, weather_humidity, target_temp, current_time):
        """Collect feature vector from current state."""
        features = {
            "current_temp": thermostat_data.get("current_temp", 20),
            "target_temp": target_temp,
            "outdoor_temp": weather_temp,
            "outdoor_humidity": weather_humidity,
            "hour": current_time.hour,
            "weekday": current_time.weekday(),
            "temp_diff": target_temp - thermostat_data.get("current_temp", 20)
        }
        return features
    
    def detect_anomaly(self, features, predicted_time):
        """Detect anomalies in heating behavior."""
        if not self.anomaly_detection_enabled or len(self.training_data) < 20:
            return None
            
        # Calculate expected range based on training data
        recent_samples = self.training_data[-20:]
        avg_time = sum(s["heat_on_time"] for s in recent_samples) / len(recent_samples)
        
        deviation = abs(predicted_time - avg_time)
        threshold = self.anomaly_threshold * 5  # Convert °C/5min to minutes
        
        if deviation > threshold:
            return {
                "type": "heating_time_anomaly",
                "predicted": predicted_time,
                "expected": avg_time,
                "deviation": deviation
            }
        
        return None
    
    def save_model(self, filepath):
        """Save model to file."""
        try:
            data = {
                "training_data": self.training_data,
                "model_data": self.model_data,
                "is_trained": self.is_trained
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f)
                
            _LOGGER.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath):
        """Load model from file."""
        try:
            if not os.path.exists(filepath):
                _LOGGER.info("No saved model found")
                return False
                
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            self.training_data = data.get("training_data", [])
            self.model_data = data.get("model_data", {})
            self.is_trained = data.get("is_trained", False)
            
            _LOGGER.info(f"Model loaded from {filepath} with {len(self.training_data)} samples")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error loading model: {e}")
            return False


class HeatingPredictor(MLEngine):
    """Heating predictor using ML Engine."""
    
    def __init__(self, hass, config_dir):
        """Initialize predictor."""
        super().__init__(hass)
        self.model_path = os.path.join(config_dir, f"{DOMAIN}_model.json")
        self.load_model(self.model_path)
        
    def save(self):
        """Save predictor state."""
        return self.save_model(self.model_path)
