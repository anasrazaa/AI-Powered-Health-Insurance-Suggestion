# 🚀 Deployment Guide - Health Insurance Comparison Platform

## 📋 Overview
This guide will help you deploy your health insurance comparison platform with:
- **Frontend (React)**: Vercel
- **Backend (FastAPI)**: Railway

## 🎯 Prerequisites
- GitHub account
- Vercel account (free)
- Railway account (free tier available)
- OpenAI API key

---

## 🔧 Step 1: Prepare Your Code

### 1.1 Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 1.2 Update Environment Variables
You'll need to set these environment variables in your deployment platforms:

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key

---

## 🌐 Step 2: Deploy Backend (Railway)

### 2.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

### 2.2 Deploy Backend
1. **Connect GitHub Repository**
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect it's a Python project

2. **Configure Environment Variables**
   - Go to Variables tab
   - Add: `OPENAI_API_KEY=your_openai_key_here`

3. **Deploy**
   - Railway will automatically build and deploy
   - Wait for deployment to complete
   - Copy the generated URL (e.g., `https://your-app.railway.app`)

### 2.3 Test Backend
```bash
# Test your backend endpoint
curl https://your-app.railway.app/health
```

---

## ⚡ Step 3: Deploy Frontend (Vercel)

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

### 3.2 Configure Frontend
1. **Import Repository**
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect it's a React app

2. **Configure Build Settings**
   - Framework Preset: `Create React App`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

3. **Set Environment Variables**
   - Go to Settings → Environment Variables
   - Add: `REACT_APP_API_URL=https://your-app.railway.app`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your site will be live at `https://your-app.vercel.app`

---

## 🔗 Step 4: Connect Frontend to Backend

### 4.1 Update API Configuration
1. Go to your Vercel project settings
2. Add environment variable:
   - Name: `REACT_APP_API_URL`
   - Value: `https://your-app.railway.app`

### 4.2 Redeploy Frontend
- Vercel will automatically redeploy with the new environment variable

---

## 🧪 Step 5: Test Your Deployment

### 5.1 Test Frontend
1. Visit your Vercel URL
2. Test the comparison flow
3. Verify AI advice is working

### 5.2 Test Backend
```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test plans endpoint
curl https://your-app.railway.app/plans/list
```

---

## 🔧 Troubleshooting

### Common Issues:

**1. CORS Errors**
- Ensure your backend CORS settings include your Vercel domain
- Update `allow_origins` in `backend/main.py`

**2. Environment Variables Not Working**
- Check variable names (must start with `REACT_APP_` for frontend)
- Redeploy after adding variables

**3. Build Failures**
- Check build logs in Vercel/Railway
- Ensure all dependencies are in requirements.txt

**4. API Connection Issues**
- Verify the backend URL is correct
- Check if backend is running (Railway dashboard)

---

## 📊 Monitoring & Maintenance

### Railway (Backend)
- Monitor usage in Railway dashboard
- Check logs for errors
- Scale up if needed

### Vercel (Frontend)
- Monitor performance in Vercel dashboard
- Check analytics
- Set up custom domain if needed

---

## 🎉 Success!
Your health insurance comparison platform is now live and accessible worldwide!

**Frontend**: `https://your-app.vercel.app`
**Backend**: `https://your-app.railway.app`

---

## 🔄 Continuous Deployment
Both platforms support automatic deployments:
- Push to GitHub → Automatic deployment
- No manual intervention needed

## 💰 Cost Estimation
- **Vercel**: Free tier (generous)
- **Railway**: Free tier available, then $5/month
- **Total**: ~$5/month for production use 