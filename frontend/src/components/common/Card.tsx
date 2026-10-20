import React from 'react';

interface CardProps {
  children: React.ReactNode;
  hover?: boolean;
  className?: string;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  hover = false,
  className = '',
  onClick,
}) => {
  return (
    <div
      className={`card bg-white rounded-2xl shadow-sm p-6 ${
        hover ? 'card-hover hover:shadow-md hover:translate-y-[-4px] cursor-pointer' : ''
      } transition-all duration-200 ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;
