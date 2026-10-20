import React from 'react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../utils/constants';

const RightSidebar: React.FC = () => {
  // Mock bike data - replace with real data from context/API
  const myBike = {
    name: 'Trek Marlin 7',
    year: 2023,
    type: 'Горный',
    gearCount: 29,
    image: '/bike-placeholder.png',
  };

  return (
    <aside className="w-[320px] min-h-[calc(100vh-72px)] sticky top-[72px] overflow-y-auto">
      <div className="p-6">
        {/* My Bike Card */}
        <div className="bg-[#2d5f4d] rounded-2xl overflow-hidden mb-6">
          <div className="p-5">
            <div className="text-[11px] font-semibold text-white/70 uppercase tracking-wider mb-3">
              МОЙ ВЕЛОСИПЕД
            </div>
            <h3 className="text-[22px] font-semibold text-white mb-4">
              {myBike.name}
            </h3>
            
            {/* Bike Image */}
            <div className="bg-gradient-to-br from-[#a8c5a0] to-[#7a9f7a] rounded-xl h-[180px] mb-4 flex items-center justify-center relative overflow-hidden">
              {/* Mountain landscape illustration */}
              <svg className="w-full h-full" viewBox="0 0 280 180" fill="none">
                {/* Sun */}
                <circle cx="240" cy="40" r="20" fill="#f4d58d" opacity="0.8"/>
                
                {/* Mountains */}
                <path d="M0 120 L60 60 L120 100 L180 40 L240 80 L280 60 L280 180 L0 180 Z" fill="#5a8060" opacity="0.7"/>
                <path d="M40 140 L100 80 L160 110 L220 70 L280 100 L280 180 L0 180 Z" fill="#7a9f7a" opacity="0.6"/>
                
                {/* Road */}
                <path d="M120 180 Q140 120, 160 100 Q180 80, 200 90" 
                      stroke="#e8d5b5" strokeWidth="12" fill="none" opacity="0.7"/>
                
                {/* Bike silhouette */}
                <g transform="translate(100, 120)">
                  {/* Wheels */}
                  <circle cx="0" cy="20" r="15" fill="none" stroke="#2d4f3d" strokeWidth="3"/>
                  <circle cx="60" cy="20" r="15" fill="none" stroke="#2d4f3d" strokeWidth="3"/>
                  
                  {/* Frame */}
                  <path d="M15 20 L30 0 L45 20 L30 20 L15 20 M30 0 L50 10" 
                        stroke="#2d4f3d" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
                  <path d="M45 20 L60 20" stroke="#2d4f3d" strokeWidth="2.5"/>
                  
                  {/* Handlebars */}
                  <path d="M30 0 L28 -5 M30 0 L32 -5" stroke="#2d4f3d" strokeWidth="2"/>
                  
                  {/* Seat */}
                  <rect x="38" y="6" width="10" height="3" rx="1.5" fill="#2d4f3d"/>
                </g>
              </svg>
            </div>

            {/* Bike Details */}
            <div className="flex items-center gap-4 text-white/90 text-[13px] mb-4">
              <span>{myBike.year}</span>
              <span>·</span>
              <span>{myBike.type}</span>
              <span>·</span>
              <span>{myBike.gearCount}"</span>
            </div>

            {/* Garage Link */}
            <Link
              to={ROUTES.MY_BIKES}
              className="block w-full bg-white hover:bg-gray-100 text-[#2d5f4d] text-center py-2.5 rounded-lg text-[13px] font-medium transition-colors"
            >
              Мой гараж
            </Link>
          </div>
        </div>

        {/* Welcome Card */}
        <div className="bg-white border border-gray-200 rounded-2xl p-5">
          <h3 className="text-[18px] font-semibold text-gray-900 mb-3">
            Добро пожаловать, Минь!
          </h3>
          <p className="text-[14px] text-gray-600 leading-relaxed mb-4">
            Расскажите о себе и своих интересах — так вас быстрее найдут единомышленники.
          </p>
          <Link
            to={ROUTES.PROFILE}
            className="inline-block bg-[#f5f3f0] hover:bg-gray-200 text-[#2d5f4d] px-4 py-2 rounded-lg text-[13px] font-medium transition-colors"
          >
            Заполнить профиль
          </Link>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-6 text-[11px] text-gray-400 space-y-0.5">
          <div>VELO © 2026</div>
          <div>Сообщество Опыт. Движение.</div>
        </div>
      </div>
    </aside>
  );
};

export default RightSidebar;
