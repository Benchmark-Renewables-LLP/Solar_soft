
import React, { useState, useEffect } from 'react';
import { Alert } from './UserTile';

interface AlertSystemProps {
  onAlertShow: (userId: string, alert: Alert) => void;
  onAlertHide: () => void;
}

const AlertSystem: React.FC<AlertSystemProps> = ({ onAlertShow, onAlertHide }) => {
  const [activeAlerts, setActiveAlerts] = useState<{ userId: string; alert: Alert }[]>([]);

  // Simulate real-time alerts from backend
  useEffect(() => {
    const alertTypes: Array<'critical' | 'warning' | 'info'> = ['critical', 'warning', 'info'];
    const alertMessages = {
      critical: [
        'System overheating detected',
        'Power generation critically low',
        'Inverter failure detected',
        'Grid connection lost'
      ],
      warning: [
        'Efficiency below threshold',
        'High ambient temperature',
        'Dust accumulation detected',
        'Battery level low'
      ],
      info: [
        'Maintenance scheduled',
        'Weather update received',
        'System optimization complete',
        'Performance report ready'
      ]
    };

    const generateRandomAlert = () => {
      const userId = `user-${Math.floor(Math.random() * 20) + 1}`;
      const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
      const messages = alertMessages[alertType];
      const message = messages[Math.floor(Math.random() * messages.length)];
      
      const alert: Alert = {
        id: `alert-${Date.now()}-${Math.random()}`,
        type: alertType,
        message,
        timestamp: new Date()
      };

      // Show alert overlay
      onAlertShow(userId, alert);

      // Hide alert after 3 seconds
      setTimeout(() => {
        onAlertHide();
      }, 3000);
    };

    // Generate alerts every 5-10 seconds
    const interval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance to generate an alert
        generateRandomAlert();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [onAlertShow, onAlertHide]);

  return null; // This component only manages alert logic
};

export default AlertSystem;
