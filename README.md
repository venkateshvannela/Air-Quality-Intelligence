# 🌍 Air Quality Intelligence

An intelligent air-quality analysis system that combines **WAQI/Ozon3 monitoring-station data** with **Open-Meteo model-based air-quality data** to provide AQI classification, dominant-pollutant analysis, and health recommendations.

The system automatically uses WAQI when monitoring-station data is available and falls back to Open-Meteo when a location does not have WAQI coverage.

---

## 🚀 Features

* 🌍 Search air quality by city/place name
* 📡 Retrieve air-quality data from WAQI
* 🔄 Automatic Open-Meteo fallback when WAQI has no station coverage
* 📊 US AQI classification
* 🧪 Pollutant-level AQI analysis
* 🔎 Dominant pollutant detection
* 🫁 Health recommendations based on AQI
* 📍 Location detection using latitude and longitude
* ⏱️ Current air-quality information
* 📈 Hourly air-quality forecast data
* 🐳 Docker support
* 🔐 Environment-variable based API-token configuration
* 🐍 Python 3.12 compatibility for the tested current-data workflow

---

## 🧠 How It Works

The system follows a two-source architecture:

```text
                 User
                   │
                   ▼
          Air Quality Service
                   │
                   ▼
          ┌─────────────────┐
          │   Try WAQI      │
          │   / Ozon3       │
          └────────┬────────┘
                   │
          Station available?
              ┌────┴────┐
             YES        NO
              │          │
              ▼          ▼
        WAQI Station   Open-Meteo
           Data        Coordinate Data
              │          │
              └────┬─────┘
                   ▼
          Air Quality Analyzer
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
         AQI   Pollutant   Category
               Analysis
                   │
                   ▼
          Health Recommendation
```

### Source selection

**WAQI / Ozon3**

Used first when the requested location has an available monitoring station.

**Open-Meteo**

Used as a fallback when WAQI does not provide station coverage for the requested location.

> Open-Meteo air-quality values are model-based and should not be described as measurements from a physical monitoring station.

---

## 📊 AQI Classification

The analyzer classifies US AQI values into the following categories:

|     AQI | Category                       |
| ------: | ------------------------------ |
|    0–50 | Good                           |
|  51–100 | Moderate                       |
| 101–150 | Unhealthy for Sensitive Groups |
| 151–200 | Unhealthy                      |
| 201–300 | Very Unhealthy                 |
|    301+ | Hazardous                      |

The system also generates a health recommendation based on the resulting category.

---

## 🧪 Pollutant Analysis

The system considers pollutant-specific AQI values including:

* PM2.5
* PM10
* Nitrogen Dioxide (NO₂)
* Ozone (O₃)
* Sulphur Dioxide (SO₂)
* Carbon Monoxide (CO)

The pollutant with the highest available pollutant-specific AQI is identified as the **dominant pollutant**.

---

## 📁 Project Structure

```text
Air-Quality-Intelligence/
│
├── .github/
│
├── src/
│   ├── ozon3/
│   │   ├── historical/
│   │   ├── __init__.py
│   │   ├── ozon3.py
│   │   └── urls.py
│   │
│   ├── media/
│   │
│   └── air_quality_intelligence/
│       ├── __init__.py
│       ├── analyzer.py
│       ├── open_meteo.py
│       └── service.py
│
├── tests/
│
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── requirements-docker.txt
├── pyproject.toml
├── setup.py
├── setup.cfg
├── LICENSE
├── README.md
└── FILE_STRUCTURE.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/venkateshvannela/Air-Quality-Intelligence.git
cd Air-Quality-Intelligence
```

---

## 2. Create a Python 3.12 virtual environment

Python 3.12 is recommended for the currently tested workflow.

### Windows

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

in your terminal.

---

## 3. Install dependencies

For the current air-quality intelligence workflow:

```powershell
pip install pandas numpy requests ratelimit python-decouple openpyxl js2py sseclient-py
```

The repository also contains the original dependency configuration in `requirements.txt`.

---

# 🔐 WAQI API Configuration

WAQI requires an API token for its API.

Create a file named:

```text
.env
```

in the project root.

Add:

```env
WAQI_TOKEN=YOUR_WAQI_API_TOKEN
```

Replace `YOUR_WAQI_API_TOKEN` with your actual token.

### ⚠️ Security

Never commit your `.env` file or expose your API token publicly.

The repository's `.gitignore` already excludes:

```text
.env
```

---

# ▶️ Running the Project

Because this repository uses a `src` directory, set the Python path before running the project.

### PowerShell

```powershell
$env:PYTHONPATH="$PWD\src"
```

Then run Python.

Example:

```powershell
python
```

---

## 🧪 Example Usage

```python
from air_quality_intelligence.service import AirQualityService

service = AirQualityService()

result = service.get_city_analysis("Nandyal")

print("Status:", result["status"])
print("City:", result["requested_city"])
print("AQI:", result["aqi"])
print("Category:", result["category"])
print("Dominant pollutant:", result["dominant_pollutant"])
print("Source:", result["source"])
print("Recommendation:", result["recommendation"])
```

---

# 📍 Example: Nandyal

For locations without an available WAQI monitoring station, the system automatically uses Open-Meteo.

Example:

```text
City: Nandyal
AQI: 54
Category: Moderate
Dominant pollutant: pm2.5
Source: Open-Meteo
```

The response also contains current pollutant values and hourly forecast information.

The Open-Meteo result represents **model-based air quality at the requested coordinates**, not a physical monitoring station in Nandyal.

---

# 🏙️ Example: Hyderabad

For locations where WAQI station data is available, the system can use WAQI/Ozon3.

Example:

```text
City: Hyderabad
AQI: 93
Category: Moderate
Dominant pollutant: pm2.5
Source: WAQI / Ozon3
Source type: Monitoring station data
Fallback: False
```

This demonstrates the project's dual-source architecture.

---

# 🔄 Fallback Architecture

The main service uses the following logic:

```text
Request city
     │
     ▼
Try WAQI / Ozon3
     │
     ├── Data available ──────► Analyze WAQI data
     │
     └── No station/data
                │
                ▼
          Try Open-Meteo
                │
                ├── Data available ──► Analyze model data
                │
                └── No data
                         │
                         ▼
                    Return no data
```

This makes the system more useful than depending on a single air-quality data provider.

---

# 🐳 Docker

The project includes Docker support for running the air-quality intelligence workflow in a container.

## Build the Docker image

From the project root:

```powershell
docker build -t air-quality-intelligence .
```

---

## Run the container

Make sure your `.env` file contains your WAQI token.

Then:

```powershell
docker run --rm --env-file .env air-quality-intelligence
```

The container runs the air-quality analysis for Nandyal.

Example output:

```text
status: success
place: Nandyal
source: Open-Meteo
aqi_standard: US AQI
aqi: 54
category: Moderate
dominant_pollutant: pm2.5
fallback: True
```

---

# 🐳 Docker Architecture

```text
                 Docker Container
                       │
                       ▼
          Air Quality Intelligence
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          WAQI/Ozon3         Open-Meteo
             │                   │
             └─────────┬─────────┘
                       ▼
                AQI Analyzer
                       │
                       ▼
              Intelligence Report
```

The API token is supplied at runtime through the `.env` file and is not copied into the Docker image.

---

# 🧩 Main Components

## `analyzer.py`

Contains the intelligence layer.

Responsibilities:

* AQI classification
* Health recommendations
* Air-quality report generation
* Dominant pollutant information

---

## `open_meteo.py`

Provides Open-Meteo integration.

Responsibilities:

* Location search
* Coordinate retrieval
* Current air-quality data
* Hourly air-quality data
* Pollutant-specific AQI values
* Model-based air-quality analysis

---

## `service.py`

Acts as the main service layer.

Responsibilities:

1. Try WAQI/Ozon3.
2. Analyze available station data.
3. Fall back to Open-Meteo if WAQI has no coverage.
4. Return a unified air-quality intelligence result.

---

## `ozon3/`

This is the original Ozon3 package integrated into the project.

Ozon3 provides functionality for retrieving air-quality information through the World Air Quality Index API.

The original project and its licensing/attribution requirements are retained.

---

# 🛠️ Technologies Used

| Technology      | Purpose                             |
| --------------- | ----------------------------------- |
| Python          | Core programming language           |
| Pandas          | Data processing                     |
| NumPy           | Numerical operations                |
| Requests        | API communication                   |
| Python-Decouple | Environment configuration           |
| Ozon3           | WAQI API integration                |
| WAQI            | Monitoring-station air-quality data |
| Open-Meteo      | Model-based air-quality fallback    |
| Docker          | Containerization                    |
| Git             | Version control                     |
| GitHub          | Source-code hosting                 |

---

# 🌐 Data Sources

## World Air Quality Index

WAQI provides access to air-quality information from monitoring stations around the world.

Official API documentation:

https://aqicn.org/api/

---

## Open-Meteo

Open-Meteo provides coordinate-based weather and air-quality data, including pollutant concentrations and AQI values.

Official documentation:

https://open-meteo.com/en/docs/air-quality-api

---

# 🔬 Project Improvements

This project extends the original Ozon3 functionality with an additional intelligence layer.

### Added functionality

* Air Quality Analyzer
* AQI classification
* Health recommendations
* Pollutant analysis
* Dominant pollutant detection
* Open-Meteo integration
* Automatic data-source fallback
* Unified service layer
* Docker containerization
* Python 3.12 compatibility improvements for the tested current-data workflow

The goal is to transform raw air-quality API data into information that is easier for users to understand and act upon.

---

# 📌 Important Data Interpretation

Different data sources represent different types of information.

### WAQI / Ozon3

```text
Monitoring station
       ↓
Observed air-quality data
       ↓
Station AQI
```

### Open-Meteo

```text
User location
       ↓
Coordinate / model grid
       ↓
Model-based air-quality data
       ↓
Estimated AQI
```

Therefore, Open-Meteo fallback results should not be presented as measurements from a physical monitoring station.

---

# 🔮 Future Enhancements

Possible future versions can include:

* 📱 Mobile-friendly dashboard
* 📊 Interactive AQI charts
* 🗺️ Air-quality map
* 🔔 AQI alerts and notifications
* 🤖 Machine-learning based AQI forecasting
* 📈 Historical trend analysis
* 🧠 Personalized health recommendations
* 🌦️ Weather + air-quality correlation
* 🏙️ Multi-city comparison
* 🗄️ Database storage
* 🔐 User accounts
* ☁️ Cloud deployment
* 📡 Real-time monitoring dashboard

---

# 📜 License and Attribution

This repository contains and extends code from the original **Ozon3** open-source project.

Original project:

https://github.com/Ozon3Org/Ozon3

Original author:

**Milind Sharma**

The original Ozon3 project is released under the **GNU General Public License v3.0 (GPL-3.0)**.

The original license and attribution requirements remain applicable to the Ozon3-derived portions of this repository.

Please refer to the included `LICENSE` file for the complete license text.

---

# 👨‍💻 Project

**Air Quality Intelligence**

An enhanced air-quality analysis project combining monitoring-station data, model-based air-quality data, automated fallback, pollutant analysis, and intelligent AQI interpretation.

Built using Python, WAQI/Ozon3, Open-Meteo, and Docker.
