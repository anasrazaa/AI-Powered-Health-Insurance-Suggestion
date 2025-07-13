import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';

const InsuranceTooltip = ({ term, children, className = "" }) => {
  const [isVisible, setIsVisible] = useState(false);

  const tooltipContent = {
    'Deductible': 'The amount you must pay for covered healthcare services before your insurance plan starts to pay. For example, with a $1,500 deductible, you pay the first $1,500 of covered services.',
    'Out of Pocket Max': 'The maximum amount you will pay for covered healthcare services in a year. After you reach this limit, your insurance pays 100% of covered services.',
    'Annual Cost': 'The total yearly cost including monthly premiums plus estimated out-of-pocket expenses like deductibles and copays.',
    'Plan Type': 'The type of health insurance plan that determines which doctors you can see and how much you pay for care.',
    'Premium': 'The monthly payment you make to keep your health insurance coverage active.',
    'Copay': 'A fixed amount you pay for a covered healthcare service, usually when you receive the service.',
    'Coinsurance': 'Your share of the costs of a covered healthcare service, calculated as a percentage of the allowed amount for the service.'
  };

  const content = tooltipContent[term] || 'No description available';

  return (
    <div className="relative inline-block">
      <div
        className={`inline-flex items-center gap-1 cursor-help ${className}`}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
        <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600 transition-colors" />
      </div>
      
      {isVisible && (
        <div className="absolute z-50 w-80 p-3 text-sm text-white bg-gray-900 rounded-lg shadow-lg -top-2 left-1/2 transform -translate-x-1/2 -translate-y-full">
          <div className="font-semibold mb-1">{term}</div>
          <div className="text-gray-200">{content}</div>
          {/* Arrow pointing down */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  );
};

export default InsuranceTooltip; 