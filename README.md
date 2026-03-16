## Nova Act Supplier Explorer

End-to-end demo app that uses Amazon Nova Act to automate UI-based supplier search and expose results via a clean three-panel web UI.

### Backend (FastAPI + Nova Act)

- Location: `backend/`
- Stack: FastAPI, `nova-act` SDK
- Key modules:
  - `main.py`: API endpoints (`/search`, `/history`, `/actions/*`, `/health`)
  - `nova_workflow.py`: Nova Act workflow that searches multiple sites with simple failover
  - `models.py`: Pydantic models for requests and responses
  - `config.py`: Reads `NOVA_ACT_API_KEY` and `NOVA_ACT_MODEL_ID` from environment

#### Local run

```bash
cd backend
pip install -r requirements.txt
set NOVA_ACT_API_KEY=your_key_here  # Windows PowerShell: $env:NOVA_ACT_API_KEY="your_key_here"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Static HTML/JS)

- Location: `frontend/`
- Open `index.html` in a browser for local testing, or host on S3/CloudFront.
- Configure the backend URL by setting `window.BACKEND_URL` via an inline script tag before loading `main.js` when deploying.

### AWS deployment (high level)

Backend (App Runner):

1. Containerize the backend (e.g., with a simple Dockerfile using `python:3.11-slim`, installing `requirements.txt` and running `uvicorn main:app --host 0.0.0.0 --port 8000`).
2. Push the image to Amazon ECR.
3. Create an App Runner service from the ECR image:
   - Set environment variables for `NOVA_ACT_API_KEY` (or use Secrets Manager and IAM).
   - Attach an IAM role with permissions to call Nova Act via Amazon Bedrock.
4. Note the HTTPS URL App Runner exposes; this becomes your `BACKEND_URL`.

Frontend (S3 + optional CloudFront):

1. Build step not required (static files only). Upload `frontend/index.html`, `styles.css`, and `main.js` into your S3 bucket.
2. Enable static website hosting on the bucket or put a CloudFront distribution in front of it for HTTPS/custom domain.
3. In `index.html`, define `window.BACKEND_URL` before `main.js`, pointing to your App Runner URL.

Once deployed, the UI will call the backend, which in turn uses Nova Act to browse candidate supplier sites with simple website failover.

