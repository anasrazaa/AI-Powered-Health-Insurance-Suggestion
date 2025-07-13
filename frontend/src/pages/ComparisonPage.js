import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import SafeErrorDisplay from '../components/SafeErrorDisplay';
import { 
  User, 
  DollarSign, 
  Heart, 
  Settings, 
  ArrowRight, 
  ArrowLeft,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const ComparisonPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, watch, trigger, formState: { errors } } = useForm({
    mode: 'onBlur',
    reValidateMode: 'onChange'
  });

  // Helper function to safely extract error messages
  const getErrorMessage = (error) => {
    try {
      if (!error) return '';
      

      
      // If it's already a string, return it
      if (typeof error === 'string') return error;
      
      // If it has a message property that's a string
      if (error.message && typeof error.message === 'string') return error.message;
      
      // If it has a msg property that's a string
      if (error.msg && typeof error.msg === 'string') return error.msg;
      
      // If it's an object with type, loc, msg, input, url (validation error object)
      if (error.type && error.msg && typeof error.msg === 'string') return error.msg;
      
      // If it's an object, try to stringify it safely
      if (typeof error === 'object') {
        // Try to get a meaningful message from the object
        if (error.detail) return String(error.detail);
        if (error.error) return String(error.error);
        
        // Handle React Hook Form validation errors
        if (error.type === 'required') return 'This field is required';
        if (error.type === 'min') return error.message || 'Value is too low';
        if (error.type === 'max') return error.message || 'Value is too high';
        if (error.type === 'pattern') return error.message || 'Invalid format';
        if (error.type === 'validate') return error.message || 'Invalid value';
        
        // If it's a complex object, try to extract a meaningful message
        const keys = Object.keys(error);
        if (keys.length > 0) {
          const firstKey = keys[0];
          const firstValue = error[firstKey];
          if (typeof firstValue === 'string') return firstValue;
          if (firstValue && typeof firstValue === 'object' && firstValue.message) {
            return String(firstValue.message);
          }
        }
        
        // If we can't extract a meaningful message, return a safe fallback
        return 'This field is required';
      }
      
      // Fallback - ensure we always return a string
      return 'This field is required';
    } catch (e) {
      // If anything goes wrong, return a safe fallback
      console.error('Error extracting error message:', e);
      return 'This field is required';
    }
  };

  const steps = [
    { id: 1, title: 'Personal Information', icon: <User className="w-5 h-5" /> },
    { id: 2, title: 'Health & Family', icon: <Heart className="w-5 h-5" /> },
    { id: 3, title: 'Financial Details', icon: <DollarSign className="w-5 h-5" /> },
    { id: 4, title: 'Preferences', icon: <Settings className="w-5 h-5" /> }
  ];

  const healthConditions = [
    'Diabetes', 'Heart Disease', 'Asthma', 'Cancer', 'Mental Health',
    'Pregnancy', 'Chronic Pain', 'None', 'Other'
  ];

  const planTypes = [
    'PPO (Preferred Provider Organization)',
    'HMO (Health Maintenance Organization)',
    'EPO (Exclusive Provider Organization)',
    'HDHP (High Deductible Health Plan)',
    'Any Type'
  ];

  const handleNext = () => {
    // Validate current step before proceeding
    const currentStepFields = getCurrentStepFields();
    const hasErrors = currentStepFields.some(field => errors[field]);
    const hasEmptyRequired = currentStepFields.some(field => {
      const value = watch(field);
      return !value || value === "";
    });

    if (hasErrors || hasEmptyRequired) {
      // Trigger validation for current step
      trigger(currentStepFields);
      toast.error('Please complete all required fields before proceeding.');
      return;
    }

    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const getCurrentStepFields = () => {
    switch (currentStep) {
      case 1:
        return ['age'];
      case 2:
        return ['familySize', 'prescriptionMeds'];
      case 3:
        return ['income'];
      case 4:
        return ['priority'];
      default:
        return [];
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      // Prepare the data with correct types for the backend
      const userProfile = {
        age: parseInt(data.age) || 0,
        familySize: data.familySize,
        healthConditions: data.healthConditions || [],
        prescriptionMeds: data.prescriptionMeds,
        income: data.income,
        priority: data.priority,
        additionalNotes: data.additionalNotes || ""
      };
      
      // Import the API service
      const { apiService } = await import('../services/api');
      
      // Send data to backend API
      const response = await apiService.comparePlans(userProfile);
      
      // Store data and response in localStorage for results page
      localStorage.setItem('userData', JSON.stringify(userProfile));
      localStorage.setItem('comparisonResults', JSON.stringify(response));
      
      toast.success('Analysis complete! Here are your recommendations.');
      navigate('/results');
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Something went wrong. Please try again.';
      toast.error(errorMessage);
      console.error('Comparison error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age
              </label>
              <input
                type="number"
                {...register('age', { 
                  required: 'Age is required', 
                  min: { value: 18, message: 'Must be 18 or older' },
                  valueAsNumber: true
                })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter your age"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleNext();
                  }
                }}
              />
              <SafeErrorDisplay error={errors.age} />
            </div>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Family Size
              </label>
              <select
                {...register('familySize', { required: 'Family size is required' })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleNext();
                  }
                }}
              >
                <option value="">Select family size</option>
                <option value="1">Individual (1 person)</option>
                <option value="2">Couple (2 people)</option>
                <option value="3">Family of 3</option>
                <option value="4">Family of 4</option>
                <option value="5">Family of 5</option>
                <option value="6+">Family of 6+</option>
              </select>
              <SafeErrorDisplay error={errors.familySize} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Health Conditions (Select all that apply)
              </label>
              <div className="grid grid-cols-2 gap-3">
                {healthConditions.map((condition) => (
                  <label key={condition} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      value={condition}
                      {...register('healthConditions')}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">{condition}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Do you take prescription medications regularly?
              </label>
              <div className="space-y-2" onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleNext();
                }
              }}>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="yes"
                    {...register('prescriptionMeds', { required: 'Please select an option' })}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Yes</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="no"
                    {...register('prescriptionMeds')}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">No</span>
                </label>
              </div>
              <SafeErrorDisplay error={errors.prescriptionMeds} />
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Annual Household Income
              </label>
              <select
                {...register('income', { required: 'Income is required' })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleNext();
                  }
                }}
              >
                <option value="">Select income range</option>
                <option value="under-25000">Under $25,000</option>
                <option value="25000-50000">$25,000 - $50,000</option>
                <option value="50000-75000">$50,000 - $75,000</option>
                <option value="75000-100000">$75,000 - $100,000</option>
                <option value="100000-150000">$100,000 - $150,000</option>
                <option value="over-150000">Over $150,000</option>
              </select>
              <SafeErrorDisplay error={errors.income} />
            </div>


          </motion.div>
        );

      case 4:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority (What's most important to you?)
              </label>
              <div className="space-y-3" onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleNext();
                }
              }}>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="lowest-cost"
                    {...register('priority', { required: 'Please select a priority' })}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Lowest monthly cost</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="best-coverage"
                    {...register('priority')}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Best coverage</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="lowest-deductible"
                    {...register('priority')}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Lowest deductible</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    value="balanced"
                    {...register('priority')}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Balanced approach</span>
                </label>
              </div>
              <SafeErrorDisplay error={errors.priority} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                {...register('additionalNotes')}
                rows="3"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Any additional information about your health needs or preferences..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleNext();
                  }
                }}
              />
            </div>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep >= step.id 
                    ? 'bg-primary-600 border-primary-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-500'
                }`}>
                  {currentStep > step.id ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    step.icon
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-20 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-primary-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2">
            {steps.map((step) => (
              <span
                key={step.id}
                className={`text-sm font-medium ${
                  currentStep >= step.id ? 'text-primary-600' : 'text-gray-500'
                }`}
              >
                {step.title}
              </span>
            ))}
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {steps[currentStep - 1].title}
            </h1>
            <p className="text-gray-600">
              Step {currentStep} of {steps.length}
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {renderStepContent()}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6">
              <button
                type="button"
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
                  currentStep === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </button>

              {currentStep < steps.length ? (
                <button
                  type="button"
                  onClick={handleNext}
                  className="flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex items-center px-8 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Get My Recommendations
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">
                Your privacy is protected
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                All information you provide is used solely to generate personalized insurance recommendations. 
                We don't store or share your personal data.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonPage; 