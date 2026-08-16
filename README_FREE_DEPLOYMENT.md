# 🌐 100% Free 24/7 Deployment Guide (Vercel-Only Architecture)
## SVAMITVA AI Feature Extraction Platform

This guide shows you how to deploy the **entire SVAMITVA AI Platform** completely on **[Vercel](https://vercel.com)** for **FREE (0 USD / 24/7 online)** with **ZERO external servers (No Render required)**:

- **Frontend & Backend**: [Vercel](https://vercel.com) *(Next.js 14 + Python FastAPI Serverless Functions)*
- **Model Storage**: [Hugging Face Model Hub](https://huggingface.co/holypreet/svamitva-unet-weights) (`holypreet/svamitva-unet-weights`)

---

## ⚡ How Vercel-Only Deployment Works

```
 ┌─────────────────────────────────────────────────────────────┐
 │ Hugging Face Hub: holypreet/svamitva-unet-weights          │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Model weights (Auto-downloaded on request)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Vercel 24/7 Global Platform                                 │
 │                                                             │
 │  ├── Next.js 14 App Router (Frontend Web UI)                │
 │  └── Python FastAPI Serverless Functions (`/api/*`)          │
 └─────────────────────────────────────────────────────────────┘
```

---

## 🚀 1-Click Deployment Instructions

### Step 1: Upload Model Weights to Hugging Face (Completed)
Your model weights are hosted on Hugging Face:
`https://huggingface.co/holypreet/svamitva-unet-weights`

### Step 2: Deploy Entire App on Vercel
1. Push your repository to **GitHub**:
   ```bash
   git add .
   git commit -m "Configure Vercel-only serverless deployment"
   git push
   ```
2. Go to **[Vercel](https://vercel.com)** and log in with your GitHub account.
3. Click **Add New...** -> **Project**.
4. Import your GitHub repository (`pd71/svamvitva-sih`).
5. Click **Deploy**!

Vercel will automatically detect `vercel.json`, build the Next.js frontend and Python FastAPI serverless API, and give you a live HTTPS URL (`https://svamitva-sih.vercel.app`).

---

## 🎉 Done!

Your platform is live **24/7 for FREE**:
- **Live URL**: `https://your-project.vercel.app`
- **Zero Server Maintenance**: No external backend servers (Render/VPS) required!
