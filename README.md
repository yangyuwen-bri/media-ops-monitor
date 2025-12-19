# 📊 Xinhua Matrix Dashboard (新华网全媒体矩阵运营监测看板)

**xinhua-matrix-dashboard** is a professional operational analytics system designed to monitor, benchmark, and optimize content performance across Xinhua Net's multi-platform matrix (Toutiao, Weibo, WeChat, Bilibili, Xiaohongshu).

Built with **Streamlit**, **Pandas**, and **Plotly**.

## ✨ Key Features

*   **Matrix Health Overview**: Real-time aggregation of total articles, reach (reads), and interaction volume.
*   **Operational Benchmarking**:
    *   **Distribution Analysis**: Platform-specific content ratios (Donut Chart).
    *   **Rhythm Tracking**: Daily publishing volume trends (Line Chart).
*   **Deep Interaction Metrics**: Comparative analysis of Likes, Comments, and Shares with "Engagement Efficiency" indicators.
*   **Sentiment Intelligence**: Automated sentiment distribution analysis per platform.
*   **Data Back-tracing**: Integrated support for historical data merging and updates.

## 🚀 Quick Start (Local)

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/xinhua-matrix-dashboard.git
    cd xinhua-matrix-dashboard
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**
    ```bash
    streamlit run app.py
    ```
    Access the dashboard at `http://localhost:8501`.

## ☁️ Deployment

### Option 1: Streamlit Cloud (Recommended)
1.  Push this code to GitHub.
2.  Go to [share.streamlit.io](https://share.streamlit.io/) and deploy from your repo.
3.  **Note**: Ensure `信源监测_Updated.xlsx` is included in your repo.

### Option 2: Docker
Building the image:
```bash
docker build -t xinhua-dashboard .
```
Running the container:
```bash
docker run -p 8501:8501 xinhua-dashboard
```

## 📁 Project Structure

```
├── app.py                  # Main application entry point
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── scripts/
│   └── merge_backtrace.py  # Data merging and processing script
├── data/                   # Data directory (add to .gitignore if sensitive)
└── README.md               # Project documentation
```

## 🛠 Tech Stack
*   **Frontend**: Streamlit
*   **Data Processing**: Pandas, OpenPyXL
*   **Visualization**: Plotly Express
