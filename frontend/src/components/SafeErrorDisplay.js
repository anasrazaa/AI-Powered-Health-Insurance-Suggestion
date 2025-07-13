import React from 'react';

const SafeErrorDisplay = ({ error, className = "text-red-500 text-sm mt-1" }) => {
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

  if (!error) return null;

  return (
    <p className={className}>
      {getErrorMessage(error)}
    </p>
  );
};

export default SafeErrorDisplay; 