# PV Power Generation Forecasting API

A Flask-based REST API for predicting next-day photovoltaic (PV) solar power generation across 10 solar sites in South Korea. Uses deep learning models trained on KMA (Korea Meteorological Administration) weather data to produce 24-hour ahead power generation forecasts.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

This project was developed as part of research on solar power forecasting at Kookmin University, Seoul. The system automates daily PV power predictions using scheduled cron jobs that:

1. Fetch the latest weather observation data from KMA
2. Preprocess and normalize the input features
3. Run inference through 6 different deep learning architectures
4. Store predictions in a MariaDB database
5. Serve results via a REST API endpoint

## Architecture

```
KMA Weather DB ──► Data Fetch ──► Preprocessing ──► Model Inference ──► Prediction DB
                                  (MinMax Norm)     (6 DL Models)         │
                                                                          ▼
                                                                     REST API
                                                                  /data/api/powerpred
```

## Deep Learning Models

Six model architectures are compared for each of the 10 solar sites:

| Model | Architecture | Description |
|---|---|---|
| **BiLSTM** | 3-layer Bidirectional LSTM | Merge mode: sum |
| **BiLSTM_SingleDense** | 2-layer BiLSTM + Dense(256) | Single dense output layer |
| **BiLSTM_MultiDense** | 2-layer BiLSTM + Dense(500→250) | Multi-layer dense output |
| **LSTM** | 3-layer Stacked LSTM | Standard LSTM baseline |
| **ConvLSTM** | Conv1D(128→256→128) + 2-layer LSTM | CNN feature extraction + LSTM |
| **RNN** | 3-layer SimpleRNN | Vanilla RNN baseline |

**Input**: 24-hour weather sequence with 12 features
**Output**: 24-hour power generation forecast (kW)

### Weather Features (12)

| Feature | Description |
|---|---|
| `F_10cm_soil_temp` | Soil temperature at 10cm depth |
| `F_5cm_soil_temp` | Soil temperature at 5cm depth |
| `F_ground_temp` | Ground surface temperature |
| `C_visibility` | Visibility |
| `F_min_cloud_cover` | Minimum cloud cover |
| `F_mid_low_cloud_cover` | Mid-low cloud cover |
| `F_total_cloud_cover` | Total cloud cover |
| `F_solar_radiation` | Solar radiation |
| `F_daylight` | Daylight hours |
| `F_humidity` | Relative humidity |
| `F_wind_speed` | Wind speed |
| `F_temp` | Air temperature |

### Training Configuration

- **Optimizer**: Adam (lr=1e-3)
- **Loss**: Mean Squared Error
- **Normalization**: MinMax scaling with tanh activation (-1, 1)
- **Prediction schedule**: Daily at 10:00 and 16:00 KST

## Requirements

- Python >= 3.8
- TensorFlow >= 2.x
- Flask
- MariaDB / MySQL

## Installation

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/miftahfaridhh/pv-power-api.git
cd pv-power-api
pip install flask flask-restful flask-apscheduler python-dotenv tensorflow pandas numpy scikit-learn joblib mysql-connector-python
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
PV_DB_HOST=your_host
PV_DB_USER=your_user
PV_DB_PASSWORD=your_password
PV_DB_NAME=PVPowerGeneration
PV_DB_PORT=12360

ENS_DB_HOST=your_host
ENS_DB_PORT=3306
ENS_DB_USER=your_user
ENS_DB_PASSWORD=your_password
ENS_DB_NAME=ens_datacenter
```

### 3. Place Model Checkpoints

Place trained model weights in the following structure:

```
train_data/
└── {SITE_NAME}/
    ├── minmaxShort.pkl
    └── 2/
        ├── BiLSTM
        ├── BiLSTM_SingleDense
        ├── BiLSTM_MultiDense
        ├── LSTM
        ├── ConvLSTM
        └── RNN
```

### 4. Run the API

```bash
python api.py
```

The API will be available at `http://localhost:5005`.

## API Endpoint

### `POST /data/api/powerpred`

Returns predicted and actual PV power generation for a given site, date, and model.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `date` | string | Target date (YYYYMMDD) |
| `sitecode` | string | Solar site code (e.g., 717800001) |
| `model` | string | Model name (BiLSTM, LSTM, ConvLSTM, RNN, etc.) |
| `modeltime` | string | Prediction time slot (10 or 16) |

**Response:**

```json
{
  "data": {
    "pred": {"type": "예측", "hr5": 0.0, "hr6": 1.23, ..., "sum": 45.67, "erRate": "5.2%"},
    "true": {"type": "진실", "hr5": 0, "hr6": 1, ..., "sum": 43.21, "erRate": "-"}
  }
}
```

## Project Structure

```
pv-power-api/
├── api.py                          # Flask API server with scheduler
├── apiforgeneratingprediction.py   # Batch prediction script
├── templates/
│   └── powerPlot.html              # Prediction visualization page
├── train_data/                     # Model checkpoints (10:00 models)
├── train_data2021/                 # Model checkpoints (16:00 models)
├── .env.example                    # Environment variable template
└── README.md
```

## Reference

This project is related to research on solar power forecasting techniques:

> Wu, Y.-K.; Huang, C.-L.; Phan, Q.-T.; Li, Y.-Y. "Completed Review of Various Solar Power Forecasting Techniques Considering Different Viewpoints." *Energies* 2022, 15, 3320. https://doi.org/10.3390/en15093320

## Security

**Never commit credentials to this repository.** The following are ignored via `.gitignore`:

| Path | Description |
|---|---|
| `.env` | Database credentials and secrets |
| `train_data/` | Model checkpoints (large files) |
| `train_data2021/` | Model checkpoints (large files) |
| `*.pkl` | Serialized scaler objects |
| `static/uploads/` | Uploaded documents |

Use `.env.example` as the template and fill in your own values locally.

## License

This project is open-sourced under the [MIT License](LICENSE).
