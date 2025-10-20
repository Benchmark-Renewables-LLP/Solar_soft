
import React, { useState, useEffect } from 'react';
import { Alert } from './UserTile';

/**
 * Props for the AlertSystem component
 */
interface AlertSystemProps {
  /** Callback function fired when an alert should be displayed to a user */
  onAlertShow: (userId: string, alert: Alert) => void;
  /** Callback function fired when an alert should be hidden */
  onAlertHide: () => void;
}

/**
 * AlertSystem Component
 * 
 * Manages real-time alert generation and display throughout the application.
 * This component simulates backend alert generation by creating random alerts
 * at regular intervals and provides callbacks for the parent component to
 * handle alert display and hiding.
 * 
 * @component
 * @example
 * ```tsx
 * <AlertSystem 
 *   onAlertShow={(userId, alert) => setCurrentAlert({userId, alert})}
 *   onAlertHide={() => setCurrentAlert(null)}
 * />
 * ```
 */
const AlertSystem: React.FC<AlertSystemProps> = ({ onAlertShow, onAlertHide }) => {
  // State to track active alerts (currently not used but available for future enhancements)
  const [activeAlerts, setActiveAlerts] = useState<{ userId: string; alert: Alert }[]>([]);

  // Simulate real-time alerts from backend
  useEffect(() => {
    // Define the possible alert severity levels
    const alertTypes: Array<'critical' | 'warning' | 'info'> = ['critical', 'warning', 'info'];
    
    /**
     * Predefined alert messages categorized by severity level
     * These simulate real-world solar energy system alerts
     */
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

    /**
     * Generates a random alert for a random user
     * Creates realistic alert data including type, message, and timestamp
     */
    const generateRandomAlert = () => {
      // Generate random user ID (user-1 to user-20)
      const userId = `user-${Math.floor(Math.random() * 20) + 1}`;
      
      // Select random alert type
      const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
      
      // Get messages for the selected alert type
      const messages = alertMessages[alertType];
      
      // Select random message from the type-specific messages
      const message = messages[Math.floor(Math.random() * messages.length)];
      
      // Create alert object with unique ID and current timestamp
      const alert: Alert = {
        id: `alert-${Date.now()}-${Math.random()}`,
        type: alertType,
        message,
        timestamp: new Date()
      };

      // Trigger the alert display callback
      onAlertShow(userId, alert);

      // Auto-hide the alert after 3 seconds
      setTimeout(() => {
        onAlertHide();
      }, 3000);
    };

    // Set up interval to generate alerts every 5-10 seconds
    // 30% chance to generate an alert on each interval
    const interval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance to generate an alert
        generateRandomAlert();
      }
    }, 5000); // Check every 5 seconds

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, [onAlertShow, onAlertHide]);

  // This component renders nothing - it only manages alert logic
  return null;
};

export default AlertSystem;
