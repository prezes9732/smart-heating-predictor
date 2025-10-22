# Smart Heating Predictor

**Author:** prezes9732  
**Created:** 2025  
**Repository:** https://github.com/prezes9732/smart-heating-predictor

## Overview

Custom Home Assistant integration for smart heating prediction using **offline machine learning**. This integration intelligently controls your heating system by predicting optimal pre-heating times based on historical data, weather conditions, and learned patterns.

## Features

- 🤖 **Offline Machine Learning** - Uses scikit-learn Random Forest, no internet required
- 📊 **Predictive Heating** - Learns how long it takes to heat each room
- 🌡️ **Weather Integration** - Uses outdoor temperature and humidity sensors
- 🔍 **Anomaly Detection** - Detects open windows and cooking activities (>2.5°C/5min)
- 📅 **Weekly Schedule** - 7-day × 24-hour temperature scheduling
- 🌙 **Night Training** - Automatic model training at 3:00 AM
- 💾 **Persistent Model** - Saves trained model to pickle file
- ⚙️ **Visual Configuration** - Full UI-based setup (like Adaptive Lighting)

## Installation

### Full Implementation Code

**IMPORTANT:** Complete implementation with all files is available in the Perplexity AI response:

👉 **[View Full Code Documentation](https://www.perplexity.ai/search/stworz-mi-custom-integration-d-4WuaNPQWQ.u3BH4ciKFAtw)**

### Files Required

Copy these files from the Perplexity response to your Home Assistant:

```
custom_components/smart_heating_predictor/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── ml_engine.py
├── coordinator.py
├── sensor.py
├── number.py
├── select.py
├── binary_sensor.py
├── services.yaml
└── translations/
    └── pl.json
```

### Installation Steps

1. Create directory: `config/custom_components/smart_heating_predictor/`
2. Copy all 12 files from the Perplexity documentation link above
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Smart Heating Predictor"
6. Follow the setup wizard

## Configuration

After installation, configure through the UI:

1. **Thermostats** - Select your `climate.*` entities
2. **Sensors** - Choose `weather.*` or temperature/humidity sensors
3. **Schedule** - Set comfort (21°C) and eco (18°C) temperatures
4. **Advanced** - Configure learning mode (14-21 days recommended)

## How It Works

### Learning Mode (First 14-21 days)

- Collects heating data from your thermostats
- Records outdoor conditions and heating times
- Trains ML model nightly at 3:00 AM
- Shows progress: "65% - ~7 days remaining"

### Operating Mode

- Predicts pre-heat time needed (5-120 minutes)
- Automatically starts heating before scheduled times
- Continues learning and adapting
- Detects anomalies (open windows, cooking)

## Key Components

### Machine Learning Engine (`ml_engine.py`)
- Random Forest Regressor (50 estimators, max depth 10)
- Standard Scaler for feature normalization
- Anomaly detection (temperature change >2.5°C/5min)
- Model persistence via pickle

### Coordinator (`coordinator.py`)
- Data collection from thermostats and sensors
- 5-minute update interval
- Night training scheduler (3:00-4:00 AM)
- Anomaly tracking

### Sensors
- `sensor.smart_heating_learning_progress` - Training progress
- `sensor.smart_heating_recommended_learning_time` - Estimated days left
- `sensor.smart_heating_prediction_*` - Pre-heat time per thermostat
- `binary_sensor.smart_heating_anomaly` - Anomaly detection status

### Controls
- `select.smart_heating_mode` - Learning / Operating mode toggle
- `number.smart_heating_anomaly_threshold` - Sensitivity (0.5-5.0°C/5min)

## Services

### `smart_heating_predictor.set_schedule_slot`
Set weekly schedule temperature for specific day/hour.

```yaml
service: smart_heating_predictor.set_schedule_slot
data:
  day: 0  # Monday
  hour: 7  # 7:00 AM
  target_temp: 21.5
  room: "living_room"
```

### `smart_heating_predictor.set_learning_mode`
Toggle between learning and operating mode.

```yaml
service: smart_heating_predictor.set_learning_mode
data:
  mode: false  # Switch to operating mode
```

## Dashboard Cards

### Temperature Chart (Apex Charts)

```yaml
type: custom:apexcharts-card
header:
  title: Smart Heating - Temperature & Anomalies
graph_span: 24h
series:
  - entity: sensor.smart_heating_target_temp
    name: Target Temperature
    type: line
  - entity: sensor.smart_heating_current_temp
    name: Current Temperature
    type: line
  - entity: binary_sensor.smart_heating_anomaly
    name: Anomalies
    type: area
    color: red
```

### Control Panel

```yaml
type: entities
title: Smart Heating Control
entities:
  - entity: select.smart_heating_mode
    name: Mode
  - entity: sensor.smart_heating_learning_progress
    name: Learning Progress
  - entity: sensor.smart_heating_recommended_learning_time
    name: Time Remaining
```

## Technical Details

### Dependencies
- `scikit-learn==1.3.0`
- `numpy==1.24.0`

### Performance
- Model training: Only at night (3:00-4:00 AM)
- Data sampling: Every 5 minutes
- Minimum samples for training: 100
- Prediction time: <100ms

### Feature Set
1. Outdoor temperature
2. Outdoor humidity
3. Target temperature
4. Hour of day
5. Day of week
6. Month
7. Current room temperature
8. Temperature delta

## Credits

**Created by:** prezes9732  
**Year:** 2025  
**License:** MIT (or your chosen license)

## Support

For issues, questions, or contributions:
- **GitHub Issues:** https://github.com/prezes9732/smart-heating-predictor/issues

---

**⭐ If you find this integration useful, please give it a star on GitHub!**

*Developed with ❤️ by prezes9732*
