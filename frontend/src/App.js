import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import HomePage from './pages/HomePage';
import ComparisonPage from './pages/ComparisonPage';
import ResultsPage from './pages/ResultsPage';
import PlansListPage from './pages/PlansListPage';
import PlanDetailPage from './pages/PlanDetailPage';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/compare" element={<ComparisonPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/plans" element={<PlansListPage />} />
              <Route path="/plans/:planId" element={<PlanDetailPage />} />
            </Routes>
          </main>
          <Footer />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App; 