# Fetch 🛒✨

An end-to-end AI agent platform that automates UI-based wholesale supplier searches and exposes the results via a clean, three-panel web interface. 

Powered by the **Amazon Nova Act** SDK, Fetch autonomously navigates supplier websites, extracts structured product data, and handles website failovers—all without requiring official supplier APIs.

## 🧰 Tech Stack

Fetch is built using a modern, lightweight stack optimized for AI agent workflows and serverless deployment:

**Backend Engine**
* **Python 3.11+**
* **FastAPI & Uvicorn** (API routing and server)
* [cite_start]**Amazon Nova Act SDK** (Browser automation and AI UI-navigation) [cite: 131, 133]
* **Pydantic** (Data validation and schema modeling)

**Frontend UI**
* **Vanilla HTML, CSS, & JavaScript** (Static, no-build frontend)

**AWS Infrastructure & Deployment**
* **Amazon ECR** (Docker container registry for the backend)
* **AWS App Runner** (Fully managed backend hosting)
* **Amazon S3 & CloudFront** (Static website hosting and CDN for the frontend)
* [cite_start]**AWS IAM** (Secure permissions for Bedrock/Nova Act execution) [cite: 869, 870]

---

## 📂 Project Structure

```text
fetch/
├── backend/
│   ├── main.py            # FastAPI endpoints (/search, /history, /health)
│   ├── nova_workflow.py   # Core Nova Act scraping and failover logic
│   ├── models.py          # Pydantic schemas for inputs/outputs
│   ├── config.py          # Environment variable management
│   └── requirements.txt   # Python dependencies
└── frontend/
    ├── index.html         # Main UI layout
    ├── styles.css         # Three-panel styling
    └── main.js            # API integration and DOM updates
