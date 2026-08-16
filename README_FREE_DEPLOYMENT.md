# 🌐 100% Free 24/7 Deployment Guide
## SVAMITVA AI Feature Extraction Platform

This guide shows you how to deploy the **entire SVAMITVA AI Platform** completely for **FREE (0 USD / 24/7 online)** using:
- **Model Storage**: [Hugging Face Model Hub](https://huggingface.co/holypreet/svamitva-unet-weights) (`holypreet/svamitva-unet-weights`)
- **Backend (FastAPI)**: [Render.com](https://render.com) *(100% Free Web Service)* or [Koyeb](https://koyeb.com)
- **Frontend (Next.js 14)**: [Vercel](https://vercel.com) *(100% Free Global CDN Hosting)*

---

## 📦 Step 1: Upload Model Weights to Hugging Face Model Hub (FREE)

1. Open PowerShell and navigate to the weights directory:
   ```powershell
   cd d:\drone\backend\app\ml\weights
   ```

2. Install Hugging Face CLI & Log In:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"
   hf auth login
   ```

3. Upload the model weights directly to your repository:
   ```powershell
   hf upload holypreet/svamitva-unet-weights .
   ```

> [!NOTE]
> The backend application is pre-configured to automatically fetch model weights directly from `https://huggingface.co/holypreet/svamitva-unet-weights/resolve/main/unet_svamitva_building_best.pth` when deployed on Render!

---

## 🚀 Step 2: Deploy Backend to Render.com (FREE Web Service)

1. Push your code to **GitHub**.
2. Go to **[Render.com](https://render.com)** and log in.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository (`drone` or `svamitva-sih`).
5. Configure the Web Service settings:
   - **Name**: `svamitva-ai-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free ($0/month)**
6. Click **Create Web Service**.
7. Once deployed, copy your live backend URL (e.g. `https://svamitva-ai-backend.onrender.com`).

---

## 🚀 Step 3: Deploy Frontend to Vercel (FREE 24/7 CDN)

1. Go to **[Vercel](https://vercel.com)** and log in with GitHub.
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`drone` or `svamitva-sih`).
4. Configure the settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: Select `frontend`
   - **Environment Variables**:
     - **Name**: `NEXT_PUBLIC_API_URL`
     - **Value**: `https://svamitva-ai-backend.onrender.com` *(Your Render backend URL)*
5. Click **Deploy**.

---

## 🎉 Done!

Your web application is live **24/7 for FREE**:
- **Frontend URL**: `https://your-project.vercel.app`
- **Backend API**: `https://svamitva-ai-backend.onrender.com`
- **Hugging Face Model Repository**: `https://huggingface.co/holypreet/svamitva-unet-weights`

Anyone can open `https://your-project.vercel.app` from anywhere in the world 24/7!
