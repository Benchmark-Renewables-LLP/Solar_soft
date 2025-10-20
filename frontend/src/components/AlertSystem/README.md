
# AlertSystem Component

The AlertSystem component manages real-time alerts and notifications throughout the application. It simulates backend alert generation and provides visual feedback to users.

## Overview

The AlertSystem is responsible for:
- Generating simulated real-time alerts
- Managing alert display timing
- Providing callbacks for alert state changes
- Categorizing alerts by severity (critical, warning, info)

## Component Interface

```tsx
interface AlertSystemProps {
  /** Callback fired when an alert should be displayed */
  onAlertShow: (userId: string, alert: Alert) => void;
  /** Callback fired when an alert should be hidden */
  onAlertHide: () => void;
}

interface Alert {
  /** Unique identifier for the alert */
  id: string;
  /** Alert severity level */
  type: 'critical' | 'warning' | 'info';
  /** Alert message text */
  message: string;
  /** When the alert was created */
  timestamp: Date;
}
```

## Features

### Alert Generation
- **Automatic Generation**: Alerts are generated every 5-10 seconds
- **Random Distribution**: 30% chance of generating an alert per interval
- **User Targeting**: Alerts are randomly assigned to users (user-1 to user-20)
- **Realistic Messages**: Context-appropriate messages for each alert type

### Alert Types

#### Critical Alerts 🔴
High-priority system issues requiring immediate attention:
- System overheating detected
- Power generation critically low
- Inverter failure detected
- Grid connection lost

#### Warning Alerts 🟡
Medium-priority issues that need monitoring:
- Efficiency below threshold
- High ambient temperature
- Dust accumulation detected
- Battery level low

#### Info Alerts 🔵
Low-priority informational messages:
- Maintenance scheduled
- Weather update received
- System optimization complete
- Performance report ready

### Timing Behavior
- **Display Duration**: 3 seconds per alert
- **Generation Interval**: 5-10 seconds between potential alerts
- **Non-blocking**: Multiple alerts can be queued

## Usage

```tsx
import AlertSystem from '@/components/AlertSystem'

function Dashboard() {
  const [currentAlert, setCurrentAlert] = useState(null)

  const handleAlertShow = (userId: string, alert: Alert) => {
    console.log(`Alert for user ${userId}:`, alert.message)
    setCurrentAlert({ userId, alert })
  }

  const handleAlertHide = () => {
    setCurrentAlert(null)
  }

  return (
    <div>
      <AlertSystem 
        onAlertShow={handleAlertShow}
        onAlertHide={handleAlertHide}
      />
      
      {currentAlert && (
        <AlertOverlay alert={currentAlert.alert} />
      )}
    </div>
  )
}
```

## Integration with UserTile

The AlertSystem works closely with UserTile components to display alerts:

```tsx
// In your main dashboard component
const [alertDisplay, setAlertDisplay] = useState(null)

const showAlert = (userId, alert) => {
  setAlertDisplay({ userId, alert })
}

const hideAlert = () => {
  setAlertDisplay(null)
}

return (
  <>
    <AlertSystem onAlertShow={showAlert} onAlertHide={hideAlert} />
    
    {users.map(user => (
      <UserTile
        key={user.id}
        user={user}
        showAlert={alertDisplay?.userId === user.id ? alertDisplay.alert : null}
      />
    ))}
  </>
)
```

## Styling

The component itself has no visual representation - it's purely functional. Alert styling is handled by the consuming components (like UserTile).

## Performance Considerations

### Memory Management
- Automatic cleanup on component unmount
- No memory leaks from intervals
- Efficient random generation algorithms

### Optimization Tips
- Use React.memo for consuming components if they re-render frequently
- Consider debouncing if handling many rapid alerts
- Implement alert queuing for better UX if needed

## Configuration Options

### Customizing Alert Generation
```tsx
// Modify the component to accept configuration props
interface AlertSystemProps {
  onAlertShow: (userId: string, alert: Alert) => void;
  onAlertHide: () => void;
  
  // Optional configuration
  alertInterval?: number;        // Default: 5000ms
  alertChance?: number;          // Default: 0.3 (30%)
  displayDuration?: number;      // Default: 3000ms
  userCount?: number;            // Default: 20
}
```

### Custom Alert Messages
```tsx
const customAlertMessages = {
  critical: [
    'Custom critical message 1',
    'Custom critical message 2'
  ],
  warning: [
    'Custom warning message 1',
    'Custom warning message 2'
  ],
  info: [
    'Custom info message 1',
    'Custom info message 2'
  ]
}
```

## Testing

### Unit Testing
```tsx
import { render, act } from '@testing-library/react'
import AlertSystem from './AlertSystem'

test('calls onAlertShow when alert is generated', async () => {
  const mockShowAlert = jest.fn()
  const mockHideAlert = jest.fn()
  
  render(
    <AlertSystem 
      onAlertShow={mockShowAlert}
      onAlertHide={mockHideAlert}
    />
  )
  
  // Fast-forward time to trigger alert generation
  act(() => {
    jest.advanceTimersByTime(10000)
  })
  
  expect(mockShowAlert).toHaveBeenCalled()
})
```

### Integration Testing
```tsx
test('alert system integrates with user tiles', async () => {
  const { container } = render(<DashboardWithAlerts />)
  
  // Simulate alert generation and verify UI updates
  act(() => {
    jest.advanceTimersByTime(10000)
  })
  
  expect(container.querySelector('.alert-overlay')).toBeInTheDocument()
})
```

## Troubleshooting

### Common Issues

#### Alerts Not Appearing
- Check that callbacks are properly passed
- Verify component is mounted
- Check console for errors

#### Performance Issues
- Reduce alert generation frequency
- Implement alert queuing
- Use React.memo for expensive components

#### Memory Leaks
- Ensure proper cleanup on unmount
- Clear intervals in useEffect cleanup

### Debug Mode
Add logging to track alert generation:
```tsx
const generateRandomAlert = () => {
  console.log('Generating alert...', { userId, alertType, message })
  // ... rest of function
}
```

## Future Enhancements

### Planned Features
- [ ] Real backend integration
- [ ] Alert persistence
- [ ] User-specific alert preferences
- [ ] Alert acknowledgment system
- [ ] Alert history and analytics
- [ ] Sound notifications
- [ ] Email/SMS integration

### API Integration
```tsx
// Future backend integration
const fetchRealTimeAlerts = async () => {
  const response = await fetch('/api/alerts/stream')
  return response.json()
}
```

This component provides a robust foundation for alert management that can easily be extended as the application grows and integrates with real backend services.
