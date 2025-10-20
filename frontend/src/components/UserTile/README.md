
# UserTile Component

The UserTile component displays individual user information in a compact, interactive card format. It shows solar energy generation data, system status, and handles real-time alerts.

## Overview

UserTile is a core dashboard component that provides:
- User identification and location information
- Real-time energy generation metrics
- System status indicators
- Alert notifications with overlay display
- Interactive click handling for detailed views

## Component Interface

```tsx
interface UserTileProps {
  /** User data to display */
  user: UserData;
  /** Click handler for tile interaction */
  onClick: (userId: string) => void;
  /** Optional alert to display as overlay */
  showAlert?: Alert;
}

interface UserData {
  /** Unique user identifier */
  id: string;
  /** User's display name */
  name: string;
  /** Geographic location */
  location: string;
  /** Current power generation in kW */
  currentGeneration: number;
  /** Total energy generated in MWh */
  totalGeneration: number;
  /** System efficiency percentage */
  efficiency: number;
  /** Current system status */
  status: 'online' | 'offline' | 'maintenance';
  /** Array of active alerts */
  alerts: Alert[];
}

interface Alert {
  /** Unique alert identifier */
  id: string;
  /** Alert severity level */
  type: 'critical' | 'warning' | 'info';
  /** Alert message text */
  message: string;
  /** Alert creation timestamp */
  timestamp: Date;
}
```

## Visual Design

### Layout Structure
```
┌─────────────────────────────────────┐
│ 👤 User Name        🟢 online       │
│    Location                         │
│                                     │
│ ⚡ Current Gen.     15.2 kW         │
│ 📊 Total Gen.       125.8 MWh       │
│ 📈 Efficiency       94%             │
│                                     │
│ ⚠️  2 alerts                        │
└─────────────────────────────────────┘
```

### Color Coding

#### Status Indicators
- **🟢 Online**: Green (`text-green-500`)
- **🔴 Offline**: Red (`text-red-500`)
- **🟡 Maintenance**: Yellow (`text-yellow-500`)

#### Alert Indicators
- **🔴 Critical**: Red icon (`text-red-500`)
- **🟡 Warning**: Yellow icon (`text-yellow-500`)
- **🔵 Info**: Blue icon (`text-blue-500`)

## Features

### Interactive States
- **Hover Effect**: Scale and shadow animation
- **Click Handling**: Navigates to detailed user view
- **Alert Highlighting**: Ring animation for active alerts
- **Status Animation**: Pulsing dot for status indication

### Responsive Design
- **Mobile First**: Optimized for small screens
- **Grid Layout**: Flexible grid system integration
- **Touch Friendly**: Adequate touch targets (44px minimum)

### Accessibility
- **Keyboard Navigation**: Tab and Enter key support
- **Screen Readers**: Proper ARIA labels and descriptions
- **Focus Indicators**: Clear focus outline
- **Color Independence**: Icons supplement color coding

## Usage Examples

### Basic Usage
```tsx
import UserTile from '@/components/UserTile'

const userData = {
  id: 'user-1',
  name: 'John Smith',
  location: 'California, USA',
  currentGeneration: 15.2,
  totalGeneration: 125.8,
  efficiency: 94,
  status: 'online',
  alerts: []
}

<UserTile 
  user={userData}
  onClick={(userId) => console.log('Clicked user:', userId)}
/>
```

### With Alert Display
```tsx
const userWithAlert = {
  ...userData,
  alerts: [
    {
      id: 'alert-1',
      type: 'warning',
      message: 'Efficiency below threshold',
      timestamp: new Date()
    }
  ]
}

const currentAlert = {
  id: 'alert-2',
  type: 'critical',
  message: 'System overheating detected',
  timestamp: new Date()
}

<UserTile 
  user={userWithAlert}
  onClick={handleUserClick}
  showAlert={currentAlert}
/>
```

### Dashboard Grid Integration
```tsx
function UserDashboard({ users }) {
  const [selectedUser, setSelectedUser] = useState(null)
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {users.map(user => (
        <UserTile
          key={user.id}
          user={user}
          onClick={setSelectedUser}
        />
      ))}
    </div>
  )
}
```

## Styling System

### Theme Variables
```css
/* Card background gradient */
.user-tile {
  background: gradient-to-br from-slate-50 to-slate-100;
  /* Dark mode */
  dark:from-slate-800 dark:to-slate-900;
}

/* Interactive states */
.user-tile:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
```

### Animation Classes
```css
/* Status indicator pulse */
.status-dot {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Alert ring animation */
.alert-ring {
  animation: ring-pulse 2s ease-in-out infinite;
  ring: 2px solid rgb(251 191 36 / 0.5);
}

/* Fade-in animation for alert overlay */
.alert-overlay {
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## Component Behavior

### Status Management
```tsx
const getStatusColor = (status: string) => {
  switch (status) {
    case 'online': return 'text-green-500'
    case 'offline': return 'text-red-500' 
    case 'maintenance': return 'text-yellow-500'
    default: return 'text-gray-500'
  }
}
```

### Alert Icon Rendering
```tsx
const getAlertIcon = (type: string) => {
  switch (type) {
    case 'critical': 
      return <AlertCircle className="w-4 h-4 text-red-500" />
    case 'warning': 
      return <AlertTriangle className="w-4 h-4 text-yellow-500" />
    case 'info': 
      return <Info className="w-4 h-4 text-blue-500" />
    default: 
      return null
  }
}
```

### Click Handling
```tsx
const handleTileClick = () => {
  // Navigate to user detail view
  onClick(user.id)
  
  // Optional: Analytics tracking
  analytics.track('user_tile_clicked', {
    userId: user.id,
    userName: user.name,
    currentGeneration: user.currentGeneration
  })
}
```

## Performance Optimizations

### Memoization
```tsx
import React, { memo } from 'react'

const UserTile = memo(({ user, onClick, showAlert }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison for optimal re-renders
  return (
    prevProps.user.id === nextProps.user.id &&
    prevProps.user.currentGeneration === nextProps.user.currentGeneration &&
    prevProps.user.status === nextProps.user.status &&
    prevProps.showAlert?.id === nextProps.showAlert?.id
  )
})
```

### Lazy Loading
```tsx
// For large user lists
const LazyUserTile = lazy(() => import('./UserTile'))

// Usage with Suspense
<Suspense fallback={<UserTileSkeleton />}>
  <LazyUserTile user={user} onClick={onClick} />
</Suspense>
```

## Testing

### Unit Tests
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import UserTile from './UserTile'

const mockUser = {
  id: 'user-1',
  name: 'Test User',
  location: 'Test Location',
  currentGeneration: 10.5,
  totalGeneration: 100.0,
  efficiency: 90,
  status: 'online',
  alerts: []
}

test('renders user information correctly', () => {
  render(<UserTile user={mockUser} onClick={jest.fn()} />)
  
  expect(screen.getByText('Test User')).toBeInTheDocument()
  expect(screen.getByText('Test Location')).toBeInTheDocument()
  expect(screen.getByText('10.5 kW')).toBeInTheDocument()
})

test('calls onClick when tile is clicked', () => {
  const mockClick = jest.fn()
  render(<UserTile user={mockUser} onClick={mockClick} />)
  
  fireEvent.click(screen.getByRole('button'))
  expect(mockClick).toHaveBeenCalledWith('user-1')
})

test('displays alert overlay when showAlert prop is provided', () => {
  const alert = {
    id: 'alert-1',
    type: 'warning',
    message: 'Test alert',
    timestamp: new Date()
  }
  
  render(<UserTile user={mockUser} onClick={jest.fn()} showAlert={alert} />)
  
  expect(screen.getByText('Test alert')).toBeInTheDocument()
  expect(screen.getByText('Warning Alert')).toBeInTheDocument()
})
```

### Accessibility Tests
```tsx
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

test('has no accessibility violations', async () => {
  const { container } = render(
    <UserTile user={mockUser} onClick={jest.fn()} />
  )
  
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

## Customization Options

### Theme Variants
```tsx
interface UserTileProps {
  user: UserData
  onClick: (userId: string) => void
  showAlert?: Alert
  
  // Customization options
  variant?: 'default' | 'compact' | 'detailed'
  showMetrics?: boolean
  showAlertCount?: boolean
}
```

### Custom Styling
```tsx
<UserTile 
  user={user}
  onClick={onClick}
  className="custom-tile-styles"
  style={{ minHeight: '200px' }}
/>
```

## Integration Examples

### With React Router
```tsx
import { useNavigate } from 'react-router-dom'

function Dashboard() {
  const navigate = useNavigate()
  
  const handleUserClick = (userId) => {
    navigate(`/users/${userId}`)
  }
  
  return (
    <UserTile user={user} onClick={handleUserClick} />
  )
}
```

### With State Management
```tsx
import { useDispatch } from 'react-redux'
import { selectUser } from './store/userSlice'

function Dashboard() {
  const dispatch = useDispatch()
  
  const handleUserClick = (userId) => {
    dispatch(selectUser(userId))
  }
  
  return (
    <UserTile user={user} onClick={handleUserClick} />
  )
}
```

## Troubleshooting

### Common Issues

#### Tile Not Clickable
- Check that `onClick` prop is provided
- Verify CSS pointer-events are not disabled
- Ensure tile is not covered by other elements

#### Status Not Updating
- Verify user data is being updated correctly
- Check that component is re-rendering
- Use React DevTools to inspect props

#### Alert Overlay Not Showing
- Check that `showAlert` prop contains valid alert object
- Verify CSS z-index for overlay positioning
- Check for JavaScript errors in console

### Performance Issues
- Use React.memo to prevent unnecessary re-renders
- Implement virtual scrolling for large user lists
- Optimize images and reduce bundle size

This component serves as a crucial building block for user dashboard interfaces, providing a clean, accessible, and performant way to display user information and interact with the system.
