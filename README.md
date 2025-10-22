# Smart Heating Predictor

**Author:** prezes9732  
**Created:** 2025  
**Repository:** https://github.com/prezes9732/smart-heating-predictor

## Overview

Custom Home Assistant integration for smart heating prediction using **simple heuristic algorithms**. This integration intelligently controls your heating system by predicting optimal pre-heating times based on historical data, weather conditions, and learned patterns.

**HAOS Compatible** - Uses only standard Python libraries, no external dependencies required!

## Features

- 🔢 **Simple Statistical Learning** - No ML libraries needed, pure Python mathematics
- 📊 **Predictive Heating** - Learns how long it takes to heat each room
- 🌡️ **Weather Integration** - Uses outdoor temperature and humidity sensors
- 🔍 **Anomaly Detection** - Detects open windows and cooking activities (>2.5°C/5min)
- 📅 **Weekly Schedule** - 7-day × 24-hour temperature scheduling
- 🌙 **Night Training** - Automatic model training at 3:00 AM
- 💾 **Persistent Model** - Saves trained parameters to JSON file
- ⚙️ **Visual Configuration** - Full UI-based setup
- ✅ **Zero Dependencies** - Works on HAOS without additional packages

## Why No Machine Learning Libraries?

This integration was redesigned to work perfectly with **Home Assistant Operating System (HAOS)** where you cannot install additional Python packages. Instead of scikit-learn or numpy, it uses:

- **Statistical averaging** for learning heating rates
- **Simple heuristics** for temperature predictions
- **Standard Python math** for calculations
- **JSON storage** instead of pickle files

## How It Works

### Learning Mode
1. Collects data about heating times and temperature changes
2. Calculates average heating/cooling rates
3. Stores patterns in JSON format
4. Trains at night (3:00-4:00 AM) to avoid system load

### Prediction Algorithm

The predictor uses a simple but effective formula:

```
preheat_time = (target_temp - current_temp) / heating_rate × outdoor_factor × humidity_factor × time_factor
```

Where:
- `heating_rate`: learned from historical data (default 0.5°C/min)
- `outdoor_factor`: 1.5x when <0°C, 1.2x when <10°C, 0.9x when >20°C
- `humidity_factor`: adjustment based on outdoor humidity
- `time_factor`: 1.2-1.3x during cold morning/night hours

### Anomaly Detection

Detects unusual temperature changes:
- Rapid drop (>2.5°C/5min) → likely open window
- Rapid rise without heating → likely cooking activity

## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Smart Heating Predictor"
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Smart Heating Predictor"

### Method 2: Manual Installation

1. Copy the `custom_components/smart_heating_predictor` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration via the UI

### Files Structure

```
custom_components/smart_heating_predictor/
├── __init__.py
├── manifest.json          # No dependencies!
├── const.py
├── config_flow.py
├── ml_engine.py          # Simple prediction engine
├── coordinator.py
├── sensor.py
├── number.py
├── select.py
├── binary_sensor.py
├── services.yaml
└── translations/
    ├── en.json
    └── pl.json
```

## Configuration

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Smart Heating Predictor"
4. Follow the configuration wizard

### Step 2: Select Devices

- **Thermostats**: Choose your climate entities
- **Weather Entity**: Optional weather integration
- **Outdoor Temperature Sensor**: Optional external temp sensor
- **Outdoor Humidity Sensor**: Optional external humidity sensor

### Step 3: Configure Schedule

Use the service `smart_heating_predictor.set_schedule` to set your weekly schedule:

```yaml
service: smart_heating_predictor.set_schedule
data:
  day: 0  # Monday (0-6)
  hour: 6  # 6:00 AM
  target_temp: 21
```

### Step 4: Learning Phase

1. Leave in **Learning Mode** for 14-21 days
2. The integration will collect data and learn heating patterns
3. Check `sensor.smart_heating_learning_progress` for progress
4. When ready, switch to **Operation Mode**

## Entities Created

### Sensors

- `sensor.smart_heating_learning_progress` - Training progress percentage
- `sensor.smart_heating_preheat_time_[room]` - Predicted preheat time for each room
- `sensor.smart_heating_outdoor_temp` - Current outdoor temperature
- `sensor.smart_heating_recommended_learning_time` - Estimated time until model is trained

### Binary Sensors

- `binary_sensor.smart_heating_anomaly_detected` - Anomaly detection status

### Selects

- `select.smart_heating_mode` - Switch between Learning/Operation modes

### Numbers

- `number.smart_heating_anomaly_threshold` - Adjust anomaly sensitivity (default 2.5°C/5min)

## Services

### `smart_heating_predictor.set_schedule`

Set a temperature for a specific day and hour.

```yaml
service: smart_heating_predictor.set_schedule
data:
  day: 0  # 0=Monday, 6=Sunday
  hour: 7  # 0-23
  target_temp: 21.5
```

### `smart_heating_predictor.force_training`

Manually trigger model training.

```yaml
service: smart_heating_predictor.force_training
```

## Lovelace Cards

### Temperature Chart with Anomalies

```yaml
type: custom:apexcharts-card
header:
  title: Smart Heating - Temperature & Anomalies
  show: true
graph_span: 24h
series:
  - entity: sensor.smart_heating_target_temp
    name: Target Temperature
    type: line
    stroke_width: 2
  - entity: sensor.smart_heating_current_temp
    name: Current Temperature
    type: line
    stroke_width: 2
  - entity: sensor.smart_heating_outdoor_temp
    name: Outdoor Temperature
    type: line
    stroke_width: 1
  - entity: binary_sensor.smart_heating_anomaly_detected
    name: Anomalies
    type: area
    color: red
    opacity: 0.3
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
    name: Recommended Learning Time
  - entity: number.smart_heating_anomaly_threshold
    name: Anomaly Threshold
```

## Requirements

- **Home Assistant**: 2024.4.0 or newer
- **Python**: 3.10+ (included in HA)
- **Dependencies**: None! 🎉

## Technical Details

### Data Storage

All data is stored in JSON format in the Home Assistant config directory:

```
<config_dir>/smart_heating_predictor_model.json
```

Structure:
```json
{
  "model_params": {
    "heating_rate": 0.5,
    "cooling_rate": 0.1,
    "outdoor_factor": 1.0,
    "thermal_mass": 1.0
  },
  "training_data": [...],
  "is_trained": true,
  "last_updated": "2025-10-22T19:00:00"
}
```

### Performance

- **Update Interval**: 5 minutes
- **Training Schedule**: 3:00-4:00 AM
- **Memory Usage**: Minimal (~1MB)
- **CPU Usage**: Negligible
- **Storage**: ~100KB JSON file

## Troubleshooting

### Integration Not Appearing

1. Check that files are in `custom_components/smart_heating_predictor/`
2. Restart Home Assistant
3. Check logs for errors: **Settings** → **System** → **Logs**

### No Predictions

1. Ensure you're in **Operation Mode**
2. Check if model is trained: `sensor.smart_heating_learning_progress`
3. Verify thermostats are configured correctly

### Inaccurate Predictions

1. Ensure learning period was sufficient (14+ days)
2. Check for anomalies in `sensor.smart_heating_anomaly_detected`
3. Manually trigger training: `smart_heating_predictor.force_training`

## Comparison: Old vs New Version

| Feature | v1.x (ML Libraries) | v2.x (Pure Python) |
|---------|---------------------|--------------------|
| Dependencies | numpy, scikit-learn | None |
| HAOS Compatible | ❌ No | ✅ Yes |
| Installation | Complex | Simple |
| Memory Usage | ~50MB | ~1MB |
| Training Speed | Slow | Fast |
| Accuracy | High | Good |
| Maintenance | High | Low |

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

### v2.0.0 (2025-10-22)
- ✅ Removed numpy and scikit-learn dependencies
- ✅ Implemented pure Python prediction algorithm
- ✅ HAOS compatible
- ✅ Switched from pickle to JSON storage
- ✅ Improved performance and reduced memory usage

### v1.0.0 (2025)
- Initial release with ML libraries

---

**Made with ❤️ for Home Assistant community**
