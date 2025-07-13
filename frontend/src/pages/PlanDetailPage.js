import React, { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Star, 
  DollarSign, 
  Shield, 
  Heart, 
  CheckCircle, 
  AlertCircle,
  FileText,
  Calendar,
  Users,
  CreditCard,
  Award
} from 'lucide-react';
import InsuranceTooltip from '../components/InsuranceTooltip';

const PlanDetailPage = () => {
  const { planId } = useParams();
  const location = useLocation();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Determine where the user came from
  const cameFromResults = location.state?.from === 'results' || 
                         document.referrer.includes('/results') ||
                         location.pathname.includes('from=results');
  
  const backUrl = cameFromResults ? '/results' : '/plans';
  const backText = cameFromResults ? 'Back to Results' : 'Back to All Plans';

  useEffect(() => {
    const fetchPlanDetails = async () => {
      try {
        // First get all plans to find the specific one
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/plans/list`);
        if (!res.ok) throw new Error('Failed to fetch plans');
        const data = await res.json();
        
        const allPlans = data.plans || data;
        const selectedPlan = allPlans.find(p => p.id === planId || p.name === planId);
        
        if (!selectedPlan) {
          throw new Error('Plan not found');
        }

        // Get detailed information from the backend
        const detailRes = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/plans/detail/${encodeURIComponent(selectedPlan.name)}`);
        if (detailRes.ok) {
          const detailData = await detailRes.json();
          setPlan({ ...selectedPlan, ...detailData });
        } else {
          // Fallback to basic plan info if detail endpoint doesn't exist
          setPlan(selectedPlan);
        }
      } catch (err) {
        setError(err.message || 'Error fetching plan details');
      } finally {
        setLoading(false);
      }
    };

    fetchPlanDetails();
  }, [planId]);

  const getPlanTypeColor = (type) => {
    switch (type?.toUpperCase()) {
      case 'HMO':
        return 'bg-blue-100 text-blue-800';
      case 'PPO':
        return 'bg-green-100 text-green-800';
      case 'HDHP':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPlanRating = (plan) => {
    if (!plan) return 4.0;
    let rating = 4.0;
    if (plan.monthly_premium < 400) rating += 0.3;
    if (plan.deductible < 2000) rating += 0.2;
    if (plan.out_of_pocket_max < 7000) rating += 0.2;
    if (plan.type === 'PPO') rating += 0.1;
    return Math.min(5.0, rating);
  };

  const formatContent = (content) => {
    if (!content) return [];
    
    // Split content into sections
    const sections = content.split(/(?=## )/);
    return sections.map(section => {
      const lines = section.split('\n');
      const title = lines[0].replace('## ', '').trim();
      const body = lines.slice(1).join('\n').trim();
      return { title, body };
    }).filter(section => section.title && section.body);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Plan Details</h2>
          <p className="text-gray-600">Fetching comprehensive plan information...</p>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Plan Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The requested plan could not be found.'}</p>
          <Link to={backUrl} className="text-primary-600 hover:underline">
            ← {backText}
          </Link>
        </div>
      </div>
    );
  }

  const rating = getPlanRating(plan);
  const annualCost = (plan.monthly_premium || 0) * 12;
  const contentSections = formatContent(plan.content);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link to={backUrl} className="flex items-center text-primary-600 hover:underline mb-4">
            <ArrowLeft className="w-5 h-5 mr-2" />
            {backText}
          </Link>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900">{plan.name}</h1>
                  <InsuranceTooltip term="Plan Type">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getPlanTypeColor(plan.type)}`}>
                      {plan.type}
                    </span>
                  </InsuranceTooltip>
                  <div className="flex items-center space-x-1">
                    <Star className="w-5 h-5 text-yellow-500 fill-current" />
                    <span className="text-lg font-semibold text-gray-900">{rating.toFixed(1)}</span>
                  </div>
                </div>
                <p className="text-xl text-gray-600 mb-4">{plan.company}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                    Comprehensive Coverage
                  </span>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    Network Provider
                  </span>
                  {plan.type === 'HDHP' && (
                    <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full">
                      HSA Eligible
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-6 lg:mt-0 lg:ml-8">
                <div className="text-center lg:text-right">
                  <p className="text-4xl font-bold text-gray-900">${plan.monthly_premium?.toLocaleString()}</p>
                  <p className="text-lg text-gray-600">per month</p>
                  <p className="text-sm text-gray-500 mt-1">${annualCost.toLocaleString()} annually</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Key Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="grid md:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-6 h-6 text-green-600" />
              <InsuranceTooltip term="Deductible">
                <span className="text-sm font-medium text-gray-600">Deductible</span>
              </InsuranceTooltip>
            </div>
            <p className="text-2xl font-bold text-gray-900">${plan.deductible?.toLocaleString()}</p>
            <p className="text-sm text-gray-500">Individual / Family</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Shield className="w-6 h-6 text-blue-600" />
              <InsuranceTooltip term="Out of Pocket Max">
                <span className="text-sm font-medium text-gray-600">Out-of-Pocket Max</span>
              </InsuranceTooltip>
            </div>
            <p className="text-2xl font-bold text-gray-900">${plan.out_of_pocket_max?.toLocaleString()}</p>
            <p className="text-sm text-gray-500">Maximum annual cost</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Calendar className="w-6 h-6 text-purple-600" />
              <span className="text-sm font-medium text-gray-600">Effective Date</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">Aug 2025</p>
            <p className="text-sm text-gray-500">Plan year start</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Award className="w-6 h-6 text-yellow-600" />
              <span className="text-sm font-medium text-gray-600">Quality Rating</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{rating.toFixed(1)}/5</p>
            <p className="text-sm text-gray-500">Based on benefits</p>
          </div>
        </motion.div>

        {/* Plan Details */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {contentSections.map((section, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-sm p-6"
              >
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-primary-600" />
                  {section.title}
                </h2>
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    {section.body}
                  </pre>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Summary */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Summary</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <InsuranceTooltip term="Plan Type">
                    <span className="text-sm text-gray-600">Plan Type</span>
                  </InsuranceTooltip>
                  <span className="font-medium">{plan.type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Carrier</span>
                  <span className="font-medium">{plan.company}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">HSA Eligible</span>
                  <span className="font-medium">{plan.hsa_eligible ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Network Type</span>
                  <span className="font-medium">{plan.type === 'HMO' ? 'HMO Network' : 'PPO Network'}</span>
                </div>
              </div>
            </motion.div>

            {/* Cost Breakdown */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Monthly Premium</span>
                  <span className="font-medium">${plan.monthly_premium?.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Annual Premium</span>
                  <span className="font-medium">${annualCost.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <InsuranceTooltip term="Deductible">
                    <span className="text-sm text-gray-600">Deductible</span>
                  </InsuranceTooltip>
                  <span className="font-medium">${plan.deductible?.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <InsuranceTooltip term="Out of Pocket Max">
                    <span className="text-sm text-gray-600">Out-of-Pocket Max</span>
                  </InsuranceTooltip>
                  <span className="font-medium">${plan.out_of_pocket_max?.toLocaleString()}</span>
                </div>
                <hr className="my-3" />
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">Total Annual Cost</span>
                  <span className="font-bold text-lg text-gray-900">${(annualCost + (plan.deductible || 0)).toLocaleString()}</span>
                </div>
              </div>
            </motion.div>

            {/* Contact Information */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Get More Information</h3>
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  For detailed information about this plan, including network providers and specific benefits, please contact the insurance carrier directly.
                </p>
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Contact {plan.company}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CreditCard className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Plan ID: {plan.id}</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanDetailPage; 