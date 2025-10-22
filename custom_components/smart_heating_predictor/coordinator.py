"""Data coordinator for Smart Heating Predictor"""
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging

from .ml_engine import HeatingPredictor
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartHeatingCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Smart Heating Predictor data."""
    
    def __init__(self, hass, config_entry):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Smart Heating Predictor",
            update_interval=timedelta(minutes=5),
        )
        self.config_entry = config_entry
        self.predictor = HeatingPredictor(hass, hass.config.config_dir)
        self.schedule = {}
        self.thermostats = config_entry.options.get("thermostats", [])
        self.weather_entity = config_entry.options.get("weather_entity")
        self.outdoor_temp_sensor = config_entry.options.get("outdoor_temp_sensor")
        self.outdoor_humidity_sensor = config_entry.options.get("outdoor_humidity_sensor")
        self.anomalies = []
        self.last_temps = {}
        
    async def _async_update_data(self):
        """Update data."""
        current_time = datetime.now()
        
        # Collect thermostat data
        thermostat_data = await self._collect_thermostat_data()
        
        # Collect weather data
        weather_data = await self._get_weather_data()
        
        # Check for anomalies
        anomaly_detected = self._check_anomalies(thermostat_data)
        
        # Learning mode - collect training data
        if self.predictor.learning_mode:
            await self._collect_training_data(thermostat_data, weather_data)
        
        # Operating mode - execute predictions
        else:
            await self._execute_predictions(thermostat_data, weather_data)
        
        # Night training (3:00-4:00 AM)
        if 3 <= current_time.hour < 4 and self.predictor.learning_mode:
            await self.hass.async_add_executor_job(self.predictor.train_model)
        
        return {
            "thermostat_data": thermostat_data,
            "weather_data": weather_data,
            "anomalies": self.anomalies,
            "learning_mode": self.predictor.learning_mode,
            "is_trained": self.predictor.is_trained,
        }
    
    async def _collect_thermostat_data(self):
        """Collect data from thermostats."""
        data = {}
        for thermostat_id in self.thermostats:
            state = self.hass.states.get(thermostat_id)
            if state:
                current_temp = state.attributes.get("current_temperature")
                target_temp = state.attributes.get("temperature")
                
                # Calculate temperature delta
                temp_delta = 0
                if thermostat_id in self.last_temps:
                    temp_delta = current_temp - self.last_temps[thermostat_id]
                
                data[thermostat_id] = {
                    "current_temp": current_temp,
                    "target_temp": target_temp,
                    "temp_delta": temp_delta,
                    "state": state.state,
                }
                
                self.last_temps[thermostat_id] = current_temp
        
        return data
    
    async def _get_weather_data(self):
        """Get weather data."""
        outdoor_temp = None
        outdoor_humidity = None
        
        if self.weather_entity:
            weather_state = self.hass.states.get(self.weather_entity)
            if weather_state:
                outdoor_temp = weather_state.attributes.get("temperature")
                outdoor_humidity = weather_state.attributes.get("humidity")
        
        if self.outdoor_temp_sensor and not outdoor_temp:
            temp_state = self.hass.states.get(self.outdoor_temp_sensor)
            if temp_state:
                try:
                    outdoor_temp = float(temp_state.state)
                except (ValueError, TypeError):
                    pass
        
        if self.outdoor_humidity_sensor and not outdoor_humidity:
            humidity_state = self.hass.states.get(self.outdoor_humidity_sensor)
            if humidity_state:
                try:
                    outdoor_humidity = float(humidity_state.state)
                except (ValueError, TypeError):
                    pass
        
        return {
            "temperature": outdoor_temp or 10.0,
            "humidity": outdoor_humidity or 50.0,
        }
    
    def _check_anomalies(self, thermostat_data):
        """Check for temperature anomalies."""
        anomaly_detected = False
        for thermostat_id, data in thermostat_data.items():
            temp_change_rate = abs(data.get("temp_delta", 0)) / 5.0  # per 5 minutes
            
            if self.predictor.detect_anomaly(None, temp_change_rate):
                anomaly_detected = True
                self.anomalies.append({
                    "thermostat": thermostat_id,
                    "time": datetime.now(),
                    "rate": temp_change_rate,
                })
                
                # Keep only last 100 anomalies
                if len(self.anomalies) > 100:
                    self.anomalies = self.anomalies[-100:]
        
        return anomaly_detected
    
    async def _collect_training_data(self, thermostat_data, weather_data):
        """Collect training data in learning mode."""
        current_time = datetime.now()
        
        for thermostat_id, data in thermostat_data.items():
            features = self.predictor.collect_features(
                data,
                weather_data["temperature"],
                weather_data["humidity"],
                data["target_temp"],
                current_time,
            )
            
            # Simulate heat-on time (you would need real measurement here)
            heat_on_time = 30  # Default 30 minutes
            if data["current_temp"] < data["target_temp"]:
                temp_diff = data["target_temp"] - data["current_temp"]
                heat_on_time = min(120, max(5, temp_diff * 15))
            
            self.predictor.add_training_sample(features, heat_on_time)
    
    async def _execute_predictions(self, thermostat_data, weather_data):
        """Execute heating predictions in operating mode."""
        current_time = datetime.now()
        
        for thermostat_id, data in thermostat_data.items():
            # Check schedule for target temperature
            schedule_key = f"{current_time.weekday()}_{current_time.hour}_default"
            target_temp = self.schedule.get(schedule_key, data["target_temp"])
            
            features = self.predictor.collect_features(
                data,
                weather_data["temperature"],
                weather_data["humidity"],
                target_temp,
                current_time,
            )
            
            # Predict pre-heat time
            preheat_time = self.predictor.predict_preheat_time(features)
            _LOGGER.debug(f"Predicted preheat time for {thermostat_id}: {preheat_time} minutes")
