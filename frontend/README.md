# HealthCompare Frontend

A professional React.js frontend for the HealthCompare health insurance comparison platform. This modern, responsive web application provides an intuitive interface for users to compare health insurance plans using AI-powered recommendations.

## Features

### 🏠 Homepage
- **Hero Section**: Compelling introduction with clear value proposition
- **Features Overview**: Highlighting key benefits of the platform
- **How It Works**: Step-by-step process explanation
- **Statistics**: Platform metrics and trust indicators
- **Call-to-Action**: Clear paths to start comparing plans

### 📊 Comparison Tool
- **Multi-Step Form**: Guided user input collection
- **Personal Information**: Age, location, zip code
- **Health & Family**: Family size, health conditions, medications
- **Financial Details**: Income, budget, deductible preferences
- **Plan Preferences**: Plan type, priorities, additional notes
- **Progress Tracking**: Visual progress indicator
- **Form Validation**: Real-time validation with helpful error messages

### 📈 Results Page
- **Personalized Recommendations**: AI-powered plan suggestions
- **Detailed Comparisons**: Side-by-side plan analysis
- **Interactive Charts**: Visual cost comparisons using Recharts
- **Filtering & Sorting**: Multiple ways to organize results
- **Plan Details**: Comprehensive plan information with pros/cons
- **Action Buttons**: View details, download, share options

### 🎨 Design System
- **Modern UI**: Clean, professional design with Tailwind CSS
- **Responsive Design**: Mobile-first approach
- **Smooth Animations**: Framer Motion for engaging interactions
- **Accessibility**: WCAG compliant with proper focus states
- **Custom Components**: Reusable UI components
- **Professional Branding**: Consistent color scheme and typography

## Technology Stack

### Core Technologies
- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library

### UI/UX Libraries
- **Lucide React**: Beautiful, customizable icons
- **React Hook Form**: Performant forms with validation
- **React Hot Toast**: Elegant toast notifications
- **Recharts**: Composable charting library

### Development Tools
- **Create React App**: Zero-configuration build tool
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixing

## Getting Started

### Prerequisites
- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm start
   # or
   yarn start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` to view the application.

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (one-way operation)

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML file
│   └── manifest.json       # Web app manifest
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Header.js       # Navigation header
│   │   └── Footer.js       # Site footer
│   ├── pages/              # Page components
│   │   ├── HomePage.js     # Landing page
│   │   ├── ComparisonPage.js # Plan comparison form
│   │   └── ResultsPage.js  # Results display
│   ├── App.js              # Main app component
│   ├── App.css             # Global styles
│   └── index.js            # App entry point
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
└── README.md               # This file
```

## Customization

### Colors
The color scheme can be customized in `tailwind.config.js`:

```javascript
colors: {
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    // ... more shades
    900: '#1e3a8a',
  },
  secondary: {
    // ... secondary colors
  },
  accent: {
    // ... accent colors
  }
}
```

### Components
All components are modular and can be easily customized:
- Update styling in component files
- Modify props and state management
- Add new features and functionality

### Styling
- Global styles in `src/App.css`
- Component-specific styles using Tailwind classes
- Custom CSS utilities for complex styling needs

## Deployment

### Build for Production
```bash
npm run build
```

This creates a `build` folder with optimized production files.

### Deployment Options
- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your repository for automatic deployments
- **AWS S3**: Upload build files to S3 bucket
- **GitHub Pages**: Deploy using GitHub Actions

## Performance Optimization

### Built-in Optimizations
- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Unused code elimination
- **Minification**: Compressed production builds
- **Image Optimization**: Optimized asset loading

### Additional Optimizations
- **Lazy Loading**: Implement for heavy components
- **Memoization**: Use React.memo for expensive components
- **Bundle Analysis**: Monitor bundle size with webpack-bundle-analyzer

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@healthcompare.com
- Documentation: [docs.healthcompare.com](https://docs.healthcompare.com)
- Issues: [GitHub Issues](https://github.com/healthcompare/frontend/issues)

## Acknowledgments

- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- [Framer Motion](https://www.framer.com/motion/) for smooth animations
- [Lucide](https://lucide.dev/) for beautiful icons
- [Recharts](https://recharts.org/) for data visualization 