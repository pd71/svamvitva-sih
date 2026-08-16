# 🚀 Render Backend Deployment & Hugging Face Model Integration

This guide walks you through deploying the **SVAMITVA AI Feature Extraction Platform** backend on **[Render](https://render.com)** as a Docker Web Service while fetching ML model weights automatically from **[Hugging Face Model Hub](https://huggingface.co/holypreet/svamitva-unet-weights)** (`holypreet/svamitva-unet-weights`).

---

## 🏗 System Architecture

```
 ┌─────────────────────────────────────────────────────────────┐
 │ Hugging Face Hub: holypreet/svamitva-unet-weights          │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Model weights (Downloaded & cached on boot)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Render Docker Web Service (https://svamitva-backend.onrender.com)│
 │                                                             │
 │  ├── Python FastAPI Backend API (`/api/*`)                  │
 │  ├── PyTorch U-Net Multi-Class Segmentation Engine          │
 │  └── PyTorch EfficientNet Roof Classifier Engine            │
 └──────────────────────────────▲──────────────────────────────┘
                                │ API Rewrites (`/api/*`)
 ┌──────────────────────────────┴──────────────────────────────┐
 │ Vercel / Next.js 14 Web Frontend                             │
 └─────────────────────────────────────────────────────────────┘
```

---

## ⚡ 1-Click Deployment Option (Render Blueprint)

1. Push your repository to **GitHub**:
   ```bash
   git add .
   git commit -m "Configure Render Docker backend with Hugging Face models"
   git push
   ```

2. Go to **[Render Dashboard](https://dashboard.render.com)** -> Click **New +** -> **Blueprint**.
3. Connect your GitHub repository (`pd71/svamvitva-sih`).
4. Render will detect `render.yaml` automatically and prompt you to create the `svamitva-backend` Web Service.
5. Click **Apply**. Render will build the Docker container and launch the service at `https://svamitva-backend.onrender.com`.

---

## 🛠 Manual Web Service Deployment Option (Render Dashboard)

If you prefer to configure the Web Service manually via Render Web UI:

1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose your repository.
4. Configure settings:
   - **Name**: `svamitva-backend`
   - **Language**: `Docker`
   - **Docker Context**: `./backend`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Instance Type**: `Free` (512 MB RAM)
5. Add Environment Variables under **Environment**:
   - `PORT`: `10000`
   - `HF_MODEL_REPO_UNET`: `holypreet/svamitva-unet-weights`
   - `HF_MODEL_REPO_EFFICIENTNET`: `holypreet/svamitva-unet-weights`
6. Click **Create Web Service**.

---

## 🔗 Connecting Next.js Frontend (Vercel) to Render Backend

Once your backend is live on Render (e.g., `https://svamitva-backend.onrender.com`):

1. Go to your **[Vercel Dashboard](https://vercel.com)** project settings.
2. Under **Environment Variables**, set:
   - `NEXT_PUBLIC_API_URL` = `https://svamitva-backend.onrender.com`
3. Redeploy your Vercel frontend.
4. The Next.js frontend will automatically proxy `/api/*` and `/static/*` requests to your Render backend via `next.config.js`.

---

## 🧪 Verifying Deployment

1. **Backend Health Check**:
   Open `https://svamitva-backend.onrender.com/api` in your browser. You should see:
   ```json
   {
     "service": "SVAMITVA AI Feature Extraction Platform Backend",
     "status": "online",
     "team": "Nerdvana",
     "problem_id": "DJS_26_SW_08",
     "docs_url": "/docs"
   }
   ```

2. **Interactive API Documentation**:
   Open `https://svamitva-backend.onrender.com/docs` to test endpoints interactively via Swagger UI.

3. **Hugging Face Model Weight Verification**:
   Inspect Render container logs during startup or initial inference. You will see:
   ```text
   Downloading U-Net model from HF Hub (holypreet/svamitva-unet-weights/unet_svamitva_building_best.pth)...
   Successfully cached Hugging Face weights to /app/app/ml/weights/unet_svamitva_building_best.pth
   Successfully loaded trained PyTorch U-Net weights (classes=4)
   ```
