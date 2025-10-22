# Smart Heating Predictor

**Author:** prezes9732  
**Created:** 2025  
**Repository:** https://github.com/prezes9732/smart-heating-predictor

## Overview

Custom Home Assistant integration for smart heating prediction using **machine learning with scikit-learn**. This integration intelligently controls your heating system by predicting optimal pre-heating times based on historical data, weather conditions, and learned patterns using RandomForestRegressor.

## Features

- 🤖 **Machine Learning Model** - RandomForestRegressor from scikit-learn
- 📊 **Predictive Heating** - Learns how long it takes to heat each room
- 🌡️ **Weather Integration** - Uses outdoor temperature and humidity sensors
- 🔍 **Anomaly Detection** - Detects open windows and cooking activities (>2.5°C/5min)
- 📅 **Weekly Schedule** - 7-day × 24-hour temperature scheduling
- 🌙 **Night Training** - Automatic model training at 3:00 AM
- 💾 **Persistent Model** - Saves trained model to pickle file
- ⚙️ **Visual Configuration** - Full UI-based setup
- 🎯 **Learning/Operation Modes** - Separate modes for training and active prediction

## ML Model

- **Algorithm**: RandomForestRegressor (scikit-learn)
- **Storage**: Pickle format for model persistence
- **Features**: 9 input features including outdoor temp, humidity, time of day, etc.
- **Training**: Offline learning at night (3:00 AM)
- **Requirements**: scikit-learn==1.3.2, numpy==1.24.3

## How It Works

### Learning Mode

1. Collects data about heating times and temperature changes
2. Stores training samples with features and labels
3. Trains RandomForestRegressor at night to avoid system load
4. Saves model to pickle file automatically
5. Recommends switching to operation mode after 100+ samples

### Operation Mode

1. Loads trained model from pickle file
2. Collects current features (temperatures, time, weather)
3. Predicts preheat time using RandomForestRegressor
4. Clamps predictions between 5-120 minutes

### Anomaly Detection

- Detects rapid temperature changes (>2.5°C/5min)
- Identifies open windows or cooking activities
- Logs anomalies for 24-hour history

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "Smart Heating Predictor" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/smart_heating_predictor` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click "Add Integration" and search for "Smart Heating Predictor"

## Configuration

1. **Select Thermostats**: Choose your climate entities to monitor
2. **Weather Entity**: Select weather integration (optional)
3. **Outdoor Sensors**: Configure external temp/humidity sensors (optional)
4. **Learning Period**: Keep in learning mode for 14-21 days minimum
5. **Switch to Operation**: After sufficient data collection, switch modes

## Services

### `smart_heating_predictor.set_schedule`

Set weekly schedule slot:

```yaml
service: smart_heating_predictor.set_schedule
data:
  day: 0  # Monday (0-6)
  hour: 7  # 7 AM (0-23)
  target_temp: 21.5
```

### `smart_heating_predictor.force_training`

Manually trigger model training:

```yaml
service: smart_heating_predictor.force_training
```

### `smart_heating_predictor.switch_mode`

Switch between learning and operation modes:

```yaml
service: smart_heating_predictor.switch_mode
data:
  mode: operation  # or learning
```

## Sensors

- `sensor.smart_heating_learning_progress` - Training data collection progress
- `sensor.smart_heating_mode` - Current mode (learning/operation)
- `sensor.smart_heating_prediction_*` - Preheat time predictions per thermostat
- `binary_sensor.smart_heating_anomaly` - Anomaly detection status

## Troubleshooting

### Model not training

1. Ensure learning period was sufficient (14+ days)
2. Check for anomalies in `sensor.smart_heating_anomaly_detected`
3. Manually trigger training: `smart_heating_predictor.force_training`

### Predictions inaccurate

1. Verify outdoor sensors are correctly configured
2. Check if enough training data collected (100+ samples)
3. Review anomalies that may affect learning

## Technical Details

### Dependencies

- `scikit-learn==1.3.2`
- `numpy==1.24.3`

### Model Parameters

- n_estimators: 50
- max_depth: 10
- random_state: 42

### Training Data

- Minimum samples: 100
- Maximum stored: 10,000 (rotates oldest)
- Training frequency: Once per day at 3:00 AM
- Storage format: Pickle (.pkl)

## License

**Restricted License: Usage Only**

You are permitted to:
- ✅ Use this integration for personal/home purposes
- ✅ Modify for your own use
- ✅ Run on your Home Assistant instance

You are NOT permitted to:
- ❌ Redistribute or share
- ❌ Sell or commercialize
- ❌ Include in other projects without permission

## Support

- **Issues**: [GitHub Issues](https://github.com/prezes9732/smart-heating-predictor/issues)
- **Author**: [@prezes9732](https://github.com/prezes9732)

## Changelog

### v1.0.2 (2025-10-22)
- ✅ Using RandomForestRegressor from scikit-learn
- ✅ Pickle-based model persistence
- ✅ Offline learning with automatic training
- ✅ Anomaly detection with threshold-based alerts
- ✅ Learning/operation mode switching

### v1.0.0 (2025)
- Initial release with ML libraries

---

**Made with ❤️ for Home Assistant community**
