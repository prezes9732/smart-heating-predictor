# Smart Heating Predictor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Inteligentna integracja Home Assistant do predykcji czasu nagrzewania używająca uczenia maszynowego offline.

## Funkcje

- 🤖 **Machine Learning offline** - Wszystkie obliczenia wykonywane lokalnie
- 📊 **Inteligentne predykcje** - Przewiduje optymalny czas nagrzewania
- 🔄 **Tryb uczenia** - Automatyczne zbieranie danych treningowych
- 🚨 **Wykrywanie anomalii** - Alerty o nietypowych wzorcach grzania
- 📈 **Sensory monitorowania** - Postęp uczenia, próbki treningowe, predykcje
- ⚙️ **Konfigurowalne usługi** - Harmonogram, tryby pracy, ręczny trening
- 🏠 **Pełna integracja z HA** - Natywne wsparcie dla wszystkich platform

## Instalacja przez HACS

1. Dodaj to repozytorium jako custom repository w HACS
2. Wyszukaj "Smart Heating Predictor" w HACS
3. Kliknij "Install"
4. Restart Home Assistant
5. Przejdź do Ustawienia → Urządzenia i usługi → Dodaj integrację
6. Wyszukaj "Smart Heating Predictor"

## Konfiguracja

Po dodaniu integracji możesz skonfigurować:
- Termostaty do monitorowania
- Sensory temperatury zewnętrznej
- Sensory wilgotności
- Sensory okien/drzwi
- Tryb uczenia maszynowego
- Próg wykrywania anomalii

## Entitety

Integracja tworzy następujące entitety:
- **Sensory**: Postęp uczenia, liczba próbek, rekomendowany czas uczenia, predykcje dla każdego termostatu
- **Binary sensory**: Wykryta anomalia, model wytrenowany
- **Number**: Próg wykrywania anomalii (°C/5min)
- **Select**: Tryb pracy (Learning/Operating)

## Usługi

- `smart_heating_predictor.set_schedule_slot` - Ustawienie harmonogramu
- `smart_heating_predictor.set_learning_mode` - Zmiana trybu uczenia
- `smart_heating_predictor.trigger_training` - Ręczny trening modelu
- `smart_heating_predictor.clear_training_data` - Czyszczenie danych

## Wymagania

- Home Assistant 2023.1.0+
- Termostaty climate w Home Assistant
- Sensor temperatury zewnętrznej (opcjonalnie)
- Sensor wilgotności (opcjonalnie)

Autor: prezes9732
