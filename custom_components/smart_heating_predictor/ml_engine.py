# Smart Heating Predictor ML Engine
# Author: prezes9732
# Simple prediction engine using only standard Python libraries
# No external dependencies (numpy, scikit-learn) - HAOS compatible

from datetime import datetime, timedelta
import json
import os
import logging
import math
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MLEngine:
    """Simple prediction engine for Smart Heating - no ML dependencies."""
    
    def __init__(self, hass, data_dir):
        """Initialize the prediction engine."""
        self.hass = hass
        self.data_dir = data_dir
        self.training_data = []
        self.is_trained = False
        self.learning_mode = True
        self.anomaly_threshold = 2.5
        self.model_params = {
            'heating_rate': 0.5,  # degrees per minute
            'cooling_rate': 0.1,  # degrees per minute
            'outdoor_factor': 1.0,
            'thermal_mass': 1.0
        }
        self._load_model()
    
    def collect_features(self, thermostat_data, outdoor_temp, outdoor_humidity, target_temp, current_time):
        """Collect features for prediction."""
        features = {
            'outdoor_temp': outdoor_temp,
            'outdoor_humidity': outdoor_humidity,
            'target_temp': target_temp,
            'hour': current_time.hour,
            'weekday': current_time.weekday(),
            'month': current_time.month,
            'current_temp': thermostat_data.get('current_temp', 20),
            'temp_delta': thermostat_data.get('temp_delta', 0)
        }
        return features
    
    def detect_anomaly(self, features, temp_change_rate):
        """Detect anomalies like open window or cooking."""
        if abs(temp_change_rate) > self.anomaly_threshold:
            _LOGGER.info(f"Anomaly detected: rapid temperature change {temp_change_rate}°C/min")
            return True
        return False
    
    def add_training_sample(self, features, heat_on_time):
        """Add training sample."""
        self.training_data.append({
            'features': features,
            'label': heat_on_time,
            'timestamp': datetime.now().isoformat()
        })
    
    def train_model(self):
        """Train model using simple statistical approach."""
        if len(self.training_data) < 100:
            _LOGGER.warning("Insufficient data for training")
            return False
        
        try:
            # Calculate average heating rates based on temperature differences
            heating_times = []
            temp_diffs = []
            outdoor_temps = []
            
            for sample in self.training_data:
                features = sample['features']
                heat_time = sample['label']
                temp_diff = features['target_temp'] - features['current_temp']
                
                if temp_diff > 0 and heat_time > 0:
                    heating_times.append(heat_time)
                    temp_diffs.append(temp_diff)
                    outdoor_temps.append(features['outdoor_temp'])
            
            if len(heating_times) > 0:
                # Calculate average heating rate
                avg_heating_rate = sum(temp_diffs[i] / heating_times[i] for i in range(len(heating_times))) / len(heating_times)
                self.model_params['heating_rate'] = max(0.1, avg_heating_rate)
                
                # Calculate outdoor temperature influence
                if len(outdoor_temps) > 0:
                    avg_outdoor = sum(outdoor_temps) / len(outdoor_temps)
                    outdoor_variance = sum((t - avg_outdoor) ** 2 for t in outdoor_temps) / len(outdoor_temps)
                    self.model_params['outdoor_factor'] = 1.0 + (outdoor_variance / 100.0)
                
                self.is_trained = True
                self._save_model()
                _LOGGER.info(f"Model trained on {len(self.training_data)} samples")
                return True
        except Exception as e:
            _LOGGER.error(f"Error training model: {e}")
        
        return False
    
    def predict_preheat_time(self, features):
        """Predict preheat time in minutes using simple heuristic."""
        if not self.is_trained:
            return self._simple_prediction(features)
        
        try:
            temp_diff = features['target_temp'] - features['current_temp']
            if temp_diff <= 0:
                return 0
            
            # Base calculation: time = temperature difference / heating rate
            base_time = temp_diff / self.model_params['heating_rate']
            
            # Outdoor temperature correction
            outdoor_temp = features['outdoor_temp']
            outdoor_factor = 1.0
            if outdoor_temp < 0:
                outdoor_factor = 1.5
            elif outdoor_temp < 10:
                outdoor_factor = 1.2
            elif outdoor_temp > 20:
                outdoor_factor = 0.9
            
            # Humidity correction (higher humidity = slower heating)
            humidity_factor = 1.0 + (features.get('outdoor_humidity', 50) - 50) / 200.0
            
            # Time of day factor (morning = colder house)
            hour_factor = 1.0
            if 5 <= features['hour'] <= 8:
                hour_factor = 1.2
            elif 22 <= features['hour'] or features['hour'] <= 5:
                hour_factor = 1.3
            
            prediction = base_time * outdoor_factor * humidity_factor * hour_factor
            
            # Clamp between 5 and 120 minutes
            return max(5, min(prediction, 120))
        
        except Exception as e:
            _LOGGER.error(f"Error in prediction: {e}")
            return self._simple_prediction(features)
    
    def _simple_prediction(self, features):
        """Simple fallback prediction when model is not trained."""
        temp_diff = features['target_temp'] - features['current_temp']
        if temp_diff <= 0:
            return 0
        
        # Simple rule: 10 minutes per degree, adjusted by outdoor temp
        base_time = temp_diff * 10
        outdoor_temp = features['outdoor_temp']
        
        if outdoor_temp < 0:
            base_time *= 1.5
        elif outdoor_temp < 10:
            base_time *= 1.2
        
        return max(5, min(base_time, 120))
    
    def calculate_learning_time(self):
        """Calculate recommended learning time."""
        days_needed = 14  # Minimum 2 weeks
        samples_needed = 100
        current_samples = len(self.training_data)
        
        if current_samples >= samples_needed:
            return "Ready to switch to operation mode"
        
        progress = (current_samples / samples_needed) * 100
        samples_left = samples_needed - current_samples
        
        # Estimate days left (assuming ~7 samples per day)
        days_left = math.ceil(samples_left / 7)
        
        return f"{progress:.0f}% - ~{days_left} days remaining"
    
    def _save_model(self):
        """Save model parameters to file."""
        try:
            model_path = os.path.join(self.data_dir, f"{DOMAIN}_model.json")
            model_data = {
                'model_params': self.model_params,
                'training_data': self.training_data[-1000:],  # Keep last 1000 samples
                'is_trained': self.is_trained,
                'last_updated': datetime.now().isoformat()
            }
            with open(model_path, 'w') as f:
                json.dump(model_data, f, indent=2)
            _LOGGER.info(f"Model saved to {model_path}")
        except Exception as e:
            _LOGGER.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load model parameters from file."""
        try:
            model_path = os.path.join(self.data_dir, f"{DOMAIN}_model.json")
            if os.path.exists(model_path):
                with open(model_path, 'r') as f:
                    model_data = json.load(f)
                
                self.model_params = model_data.get('model_params', self.model_params)
                self.training_data = model_data.get('training_data', [])
                self.is_trained = model_data.get('is_trained', False)
                _LOGGER.info(f"Model loaded from {model_path}")
                return True
        except Exception as e:
            _LOGGER.warning(f"Could not load model: {e}")
        
        return False
