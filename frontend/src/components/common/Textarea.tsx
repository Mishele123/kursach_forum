import React, { useId } from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  fullWidth = true,
  className = '',
  ...props
}) => {
  const id = useId();
  return (
    <div className={`${fullWidth ? 'w-full' : ''}`}>
      {label && (
        <label htmlFor={props.id || id} className="block text-sm font-semibold text-gray-700 mb-2">
          {label}
        </label>
      )}
      <textarea id={props.id || id}
        className={`textarea w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-velo-green focus:border-transparent transition-all min-h-[120px] resize-y ${
          error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300'
        } ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default Textarea;
