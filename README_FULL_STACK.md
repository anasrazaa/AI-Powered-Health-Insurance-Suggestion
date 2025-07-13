# HealthCompare - Full Stack Health Insurance Comparison Platform

A complete, professional health insurance comparison platform built with React.js frontend and FastAPI backend, powered by AI-driven RAG (Retrieval-Augmented Generation) technology.

## 🚀 Features

### Frontend (React.js)
- **Modern, Responsive Design**: Professional UI with Tailwind CSS
- **Multi-Step Form**: Guided user input collection
- **Interactive Results**: Detailed plan comparisons with charts
- **Real-time Validation**: Form validation with helpful error messages
- **Smooth Animations**: Engaging user experience with Framer Motion
- **Mobile-First**: Optimized for all device sizes

### Backend (FastAPI)
- **RESTful API**: Clean, documented API endpoints
- **RAG Integration**: Connects to your existing health insurance RAG system
- **Data Validation**: Pydantic models for type safety
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error management
- **Performance**: Async/await for optimal performance

### AI-Powered Features
- **Personalized Recommendations**: Based on user profile and preferences
- **Smart Plan Matching**: AI analyzes 17+ insurance plans
- **Cost Analysis**: Detailed breakdown of premiums, deductibles, and savings
- **Health-Focused**: Considers health conditions and family needs

## 🏗️ Architecture

```
HealthCompare/
├── frontend/                 # React.js application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   └── App.js           # Main application
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                  # FastAPI application
│   ├── main.py              # API server
│   └── requirements.txt     # Backend dependencies
├── app_optimized.py         # Your existing RAG system
├── sample_plan.md           # Insurance plan data
└── README_FULL_STACK.md     # This file
```

## 🛠️ Technology Stack

### Frontend
- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **React Hook Form**: Form management
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **Lucide React**: Beautiful icons

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **CORS**: Cross-origin support
- **Your RAG System**: Health insurance analysis engine

## 📋 Prerequisites

- **Node.js** (version 16 or higher)
- **Python** (version 3.8 or higher)
- **npm** or **yarn** package manager
- **pip** package manager
- **Your OpenAI API key** (already configured)

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

#### Windows
```bash
# Run the batch file
start_app.bat
```

#### Linux/Mac
```bash
# Make the script executable
chmod +x start_app.sh

# Run the shell script
./start_app.sh
```

### Option 2: Manual Startup

#### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 3. Start the Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Start the Frontend (in a new terminal)
```bash
cd frontend
npm start
```

## 🌐 Access Points

Once both services are running:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API Docs**: http://localhost:8000/redoc

## 📱 How to Use

### 1. Homepage
- Visit http://localhost:3000
- Explore the features and benefits
- Click "Start Comparing Plans" to begin

### 2. Plan Comparison
- **Step 1**: Enter personal information (age, location, zip code)
- **Step 2**: Provide health and family details
- **Step 3**: Specify financial preferences
- **Step 4**: Choose plan preferences and priorities
- Submit the form to get AI-powered recommendations

### 3. Results
- View personalized plan recommendations
- Compare costs, coverage, and benefits
- Filter and sort results
- Download or share recommendations

## 🔧 API Endpoints

### Health & Status
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /stats` - System statistics

### Plans
- `GET /plans/count` - Total number of plans
- `GET /plans/list` - List all available plans

### Comparison
- `POST /compare` - Get personalized recommendations
- `POST /query` - Direct RAG system query

## 🎨 Customization

### Frontend Styling
Edit `frontend/tailwind.config.js` to customize:
- Color scheme
- Typography
- Spacing
- Animations

### Backend Configuration
Modify `backend/main.py` to:
- Add new API endpoints
- Customize response formats
- Implement additional features

### RAG Integration
The backend automatically connects to your existing `app_optimized.py` RAG system. To modify:
- Update the import path in `backend/main.py`
- Adjust the response parsing in `parse_rag_response()`
- Customize the question building in `build_question_from_profile()`

## 🔍 Development

### Frontend Development
```bash
cd frontend
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Backend Development
```bash
cd backend
python -m uvicorn main:app --reload  # Start with auto-reload
```

### API Testing
Visit http://localhost:8000/docs for interactive API testing.

## 🚀 Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy the 'build' folder to your hosting service
```

### Backend Deployment
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
Create `.env` files for production:

**Frontend (.env)**
```
REACT_APP_API_URL=https://your-api-domain.com
```

**Backend (.env)**
```
OPENAI_API_KEY=your_openai_api_key
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Ensure your RAG system files are accessible

2. **Frontend won't start**
   - Check if port 3000 is available
   - Verify Node.js version (16+)
   - Clear npm cache: `npm cache clean --force`

3. **API connection errors**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Ensure network connectivity

4. **RAG system errors**
   - Verify `app_optimized.py` exists
   - Check OpenAI API key configuration
   - Ensure `sample_plan.md` is accessible

### Debug Mode
Enable debug logging by setting environment variables:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 📊 Performance

### Frontend Optimizations
- Code splitting with React Router
- Lazy loading of components
- Optimized bundle size
- Caching strategies

### Backend Optimizations
- Async/await for I/O operations
- Response caching
- Efficient data processing
- Connection pooling

## 🔒 Security

- CORS properly configured
- Input validation with Pydantic
- Error handling without sensitive data exposure
- Secure API key management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub

## 🎉 Success!

You now have a complete, professional health insurance comparison platform running locally. The system combines:

- **Modern React frontend** with beautiful UI/UX
- **FastAPI backend** with robust API
- **AI-powered RAG system** for intelligent recommendations
- **Real-time data processing** and visualization

Enjoy building and customizing your health insurance comparison platform! 