import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Star, DollarSign, Shield, Heart } from 'lucide-react';
import InsuranceTooltip from '../components/InsuranceTooltip';

const PlansListPage = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/plans/list`);
        if (!res.ok) throw new Error('Failed to fetch plans');
        const data = await res.json();
        console.log('API Response:', data); // Debug log
        console.log('Plans array:', data.plans); // Debug log for plans array
        if (data.plans && data.plans.length > 0) {
          console.log('First plan deductible:', data.plans[0].deductible);
          console.log('First plan max out of pocket:', data.plans[0].out_of_pocket_max);
        }
        
        // Ensure data is an array
        if (Array.isArray(data)) {
          setPlans(data);
        } else if (data && Array.isArray(data.plans)) {
          setPlans(data.plans);
        } else if (data && typeof data === 'object') {
          // If it's an object, try to extract plans from it
          const plansArray = Object.values(data).find(val => Array.isArray(val));
          if (plansArray) {
            setPlans(plansArray);
          } else {
            setPlans([]);
            setError('No plans data found in response');
          }
        } else {
          setPlans([]);
          setError('Invalid response format');
        }
      } catch (err) {
        setError(err.message || 'Error fetching plans');
        setPlans([]);
      } finally {
        setLoading(false);
      }
    };
    fetchPlans();
  }, []);

  const sortedPlans = [...plans].sort((a, b) => {
    switch (sortBy) {
      case 'premium':
        return a.monthly_premium - b.monthly_premium;
      case 'deductible':
        return a.deductible - b.deductible;
      case 'max_oop':
        return a.out_of_pocket_max - b.out_of_pocket_max;
      case 'name':
      default:
        return a.name.localeCompare(b.name);
    }
  });

  const filteredPlans = sortedPlans.filter(plan => {
    if (filterType === 'all') return true;
    return plan.type === filterType;
  });

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
    // Generate a rating based on plan characteristics
    let rating = 4.0;
    if (plan.monthly_premium < 400) rating += 0.3;
    if (plan.deductible < 2000) rating += 0.2;
    if (plan.out_of_pocket_max < 7000) rating += 0.2;
    if (plan.type === 'PPO') rating += 0.1;
    return Math.min(5.0, rating);
  };

  const getPlanFeatures = (plan) => {
    const features = ['Prescription coverage', 'Preventive care', 'Emergency coverage'];
    if (plan.type === 'PPO') features.push('Out-of-network coverage');
    if (plan.type === 'HDHP') features.push('HSA eligible');
    return features;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Plans</h2>
          <p className="text-gray-600">Fetching all available health insurance plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-center">
          <Link to="/" className="flex items-center text-primary-600 hover:underline">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Home
          </Link>
        </div>
        
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">All Available Plans</h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Browse all {plans.length} health insurance plans in our system
            </p>
          </motion.div>
        </div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Plans</p>
                <p className="text-2xl font-bold text-gray-900">{plans.length}</p>
              </div>
              <Shield className="w-8 h-8 text-primary-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <InsuranceTooltip term="Premium">
                  <p className="text-sm font-medium text-gray-600">Avg Monthly Premium</p>
                </InsuranceTooltip>
                <p className="text-2xl font-bold text-gray-900">
                  ${Math.round(plans.reduce((sum, plan) => sum + (plan.monthly_premium || 0), 0) / plans.length)}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <InsuranceTooltip term="Deductible">
                  <p className="text-sm font-medium text-gray-600">Avg Deductible</p>
                </InsuranceTooltip>
                <p className="text-2xl font-bold text-gray-900">
                  ${Math.round(plans.reduce((sum, plan) => sum + (plan.deductible || 0), 0) / plans.length).toLocaleString()}
                </p>
              </div>
              <Heart className="w-8 h-8 text-red-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <InsuranceTooltip term="Plan Type">
                  <p className="text-sm font-medium text-gray-600">Plan Types</p>
                </InsuranceTooltip>
                <p className="text-2xl font-bold text-gray-900">
                  {new Set(plans.map(p => p.type)).size}
                </p>
              </div>
              <Star className="w-8 h-8 text-yellow-500" />
            </div>
          </motion.div>
        </div>

        {/* Filters and Sort */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Filter by:</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="all">All Plans</option>
                <option value="PPO">PPO</option>
                <option value="HMO">HMO</option>
                <option value="HDHP">HDHP</option>
              </select>
            </div>
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="name">Plan Name</option>
                <option value="premium">Monthly Premium</option>
                <option value="deductible">Deductible</option>
                <option value="max_oop">Max Out of Pocket</option>
              </select>
            </div>
          </div>
        </div>

        {error ? (
          <div className="text-center py-12 text-red-500">{error}</div>
        ) : !Array.isArray(plans) || plans.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No plans available</div>
        ) : (
          <div className="space-y-6">
            {filteredPlans.map((plan, index) => {
              console.log(`Plan ${index + 1} - ${plan.name}: deductible=${plan.deductible}, max_oop=${plan.out_of_pocket_max}`);
              const rating = getPlanRating(plan);
              const features = getPlanFeatures(plan);
              const annualCost = (plan.monthly_premium || 0) * 12;
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bg-white rounded-xl shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow duration-200"
                  onClick={() => navigate(`/plans/${encodeURIComponent(plan.name)}`)}
                >
                  <div className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">{plan.name || 'Unknown Plan'}</h3>
                          <InsuranceTooltip term="Plan Type">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPlanTypeColor(plan.type)}`}>
                              {plan.type || 'Unknown'}
                            </span>
                          </InsuranceTooltip>
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                            <span className="text-sm text-gray-600">{rating.toFixed(1)}</span>
                          </div>
                        </div>
                        <p className="text-gray-600 mb-2">{plan.company || 'Unknown Carrier'}</p>
                      </div>
                      <div className="mt-4 lg:mt-0 lg:ml-6">
                        <div className="text-right">
                          <p className="text-3xl font-bold text-gray-900">
                            ${typeof plan.monthly_premium === 'number' ? plan.monthly_premium.toLocaleString() : '0'}
                          </p>
                          <p className="text-sm text-gray-600">per month</p>
                        </div>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <InsuranceTooltip term="Deductible">
                          <p className="text-sm text-gray-600">Deductible</p>
                        </InsuranceTooltip>
                        <p className="text-lg font-semibold text-gray-900">
                          ${typeof plan.deductible === 'number' ? plan.deductible.toLocaleString() : '0'}
                        </p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <InsuranceTooltip term="Out of Pocket Max">
                          <p className="text-sm text-gray-600">Out-of-Pocket Max</p>
                        </InsuranceTooltip>
                        <p className="text-lg font-semibold text-gray-900">
                          ${typeof plan.out_of_pocket_max === 'number' ? plan.out_of_pocket_max.toLocaleString() : '0'}
                        </p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <InsuranceTooltip term="Annual Cost">
                          <p className="text-sm text-gray-600">Annual Cost</p>
                        </InsuranceTooltip>
                        <p className="text-lg font-semibold text-gray-900">${annualCost.toLocaleString()}</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <InsuranceTooltip term="Plan Type">
                          <p className="text-sm text-gray-600">Plan Type</p>
                        </InsuranceTooltip>
                        <p className="text-lg font-semibold text-gray-900">{plan.type || 'Unknown'}</p>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Key Features</h4>
                      <div className="flex flex-wrap gap-2">
                        {features.map((feature, idx) => (
                          <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlansListPage; 