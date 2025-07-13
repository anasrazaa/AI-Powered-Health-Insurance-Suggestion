@echo off
REM Health Insurance RAG System - Docker Runner (Windows)
REM This script builds and runs the optimized RAG system

echo 🏥 Health Insurance RAG System - Docker Setup
echo ==============================================

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t health-insurance-rag .

REM Run the container
echo 🚀 Starting the optimized RAG system...
echo The system will parse your insurance plans and run test queries.
echo.

docker run --rm health-insurance-rag

echo.
echo ✅ System completed successfully!
echo.
echo To run with your own API key:
echo docker run --rm -e OPENAI_API_KEY=your-key-here health-insurance-rag
pause 