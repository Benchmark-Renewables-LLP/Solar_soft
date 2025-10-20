
# UI Components

This directory contains all the foundational UI components built on top of shadcn/ui. These components provide the building blocks for the entire application interface.

## Component Categories

### Core Components
- **Button**: Interactive button component with multiple variants
- **Input**: Text input fields with validation support
- **Label**: Accessible form labels
- **Card**: Container component for grouping content

### Form Components
- **Form**: Form wrapper with validation context
- **Input**: Text inputs, textareas, and form fields
- **Label**: Form field labels
- **Checkbox**: Checkbox input with custom styling
- **Radio Group**: Radio button groups
- **Select**: Dropdown select component

### Layout Components
- **Separator**: Visual dividers
- **Scroll Area**: Custom scrollable areas
- **Resizable**: Resizable panel components
- **Sheet**: Slide-out panels

### Navigation Components
- **Navigation Menu**: Multi-level navigation menus
- **Menubar**: Application menu bar
- **Dropdown Menu**: Context menus and dropdowns
- **Context Menu**: Right-click context menus

### Data Display
- **Table**: Data tables with sorting and filtering
- **Progress**: Progress bars and indicators
- **Energy Meter**: Custom energy generation meter

### Feedback Components
- **Toast**: Notification messages
- **Dialog**: Modal dialogs
- **Drawer**: Bottom sheet drawer
- **Alert Dialog**: Confirmation dialogs
- **Hover Card**: Hover-triggered content
- **Popover**: Floating content containers

### Input Components
- **Input OTP**: One-time password input
- **Command**: Command palette interface
- **Pagination**: Page navigation controls

## Design System

### Color Palette
All components use CSS custom properties for theming:
```css
--background: 0 0% 100%
--foreground: 222.2 84% 4.9%
--primary: 222.2 47.4% 11.2%
--secondary: 210 40% 96%
--muted: 210 40% 96%
--accent: 210 40% 96%
--destructive: 0 62.8% 30.6%
--border: 214.3 31.8% 91.4%
--input: 214.3 31.8% 91.4%
--ring: 222.2 84% 4.9%
```

### Typography Scale
- **text-xs**: 12px
- **text-sm**: 14px
- **text-base**: 16px (default)
- **text-lg**: 18px
- **text-xl**: 20px
- **text-2xl**: 24px

### Spacing Scale
Uses Tailwind's default spacing scale (4px base unit):
- **1**: 4px
- **2**: 8px
- **3**: 12px
- **4**: 16px
- **6**: 24px
- **8**: 32px

## Component Usage

### Button Component
```tsx
import { Button } from '@/components/ui/button'

// Primary button
<Button variant="default">Primary Action</Button>

// Secondary button
<Button variant="secondary">Secondary Action</Button>

// Destructive button
<Button variant="destructive">Delete</Button>

// Button with icon
<Button>
  <PlusIcon className="w-4 h-4 mr-2" />
  Add Item
</Button>
```

### Card Component
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>
```

### Form Components
```tsx
import { Form, FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form'
import { Input } from '@/components/ui/input'

<Form>
  <FormField name="email">
    <FormItem>
      <FormLabel>Email Address</FormLabel>
      <FormControl>
        <Input type="email" placeholder="Enter your email" />
      </FormControl>
    </FormItem>
  </FormField>
</Form>
```

## Accessibility Features

### ARIA Support
- All components include proper ARIA attributes
- Screen reader announcements for state changes
- Keyboard navigation support

### Focus Management
- Visible focus indicators
- Logical tab order
- Focus trapping in modals

### Color Contrast
- WCAG AA compliant color ratios
- High contrast mode support

## Customization

### Variant System
Most components support multiple variants:
```tsx
// Button variants
<Button variant="default" />    // Primary style
<Button variant="secondary" />  // Secondary style
<Button variant="outline" />    // Outlined style
<Button variant="ghost" />      // Minimal style

// Size variants
<Button size="sm" />           // Small size
<Button size="default" />      // Default size
<Button size="lg" />           // Large size
```

### CSS Variables
Override theme colors using CSS variables:
```css
:root {
  --primary: 200 100% 50%;     /* Custom primary color */
  --radius: 8px;              /* Custom border radius */
}
```

## Performance Notes

### Bundle Size
- Components are tree-shakable
- Import only what you need
- Total bundle size: ~50KB (gzipped)

### Runtime Performance
- Minimal re-renders with React.memo
- Efficient event handling
- Optimized animations with CSS transforms

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Progressive Enhancement
- Graceful degradation for older browsers
- Core functionality without JavaScript
- Enhanced experience with modern features

## Testing

### Component Testing
```tsx
import { render, screen } from '@testing-library/react'
import { Button } from './button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByRole('button')).toHaveTextContent('Click me')
})
```

### Accessibility Testing
```tsx
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

test('button has no accessibility violations', async () => {
  const { container } = render(<Button>Test</Button>)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```
