import React, { useState, useEffect, useRef } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';

const Timer = ({ duration, onTimeUp, isActive = true }) => {
  const [timeLeft, setTimeLeft] = useState(duration);
  const timeUpCalledRef = useRef(false);

  useEffect(() => {
    if (!isActive) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1 && !timeUpCalledRef.current) {
          timeUpCalledRef.current = true;
          onTimeUp();
          return 0;
        } else if (prev <= 1) {
          return 0; // Time is up but onTimeUp already called
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isActive, onTimeUp]);

  useEffect(() => {
    setTimeLeft(duration);
    timeUpCalledRef.current = false; // Reset the flag when duration changes
  }, [duration]);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const isWarning = timeLeft <= 300; // 5 minutes warning
  const isCritical = timeLeft <= 60; // 1 minute critical

  return (
    <div className={`timer ${isWarning ? 'warning' : ''}`}>
      <div className="flex items-center space-x-2">
        {isCritical ? (
          <AlertTriangle className="w-5 h-5 text-danger-600" />
        ) : (
          <Clock className="w-5 h-5" />
        )}
        <span className="text-lg">{formatTime(timeLeft)}</span>
      </div>
      {isWarning && (
        <div className="text-xs mt-1">
          {isCritical ? 'Time almost up!' : 'Hurry up!'}
        </div>
      )}
    </div>
  );
};

export default Timer;
