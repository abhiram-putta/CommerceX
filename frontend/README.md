# sMart E-Commerce Frontend

A modern, professional e-commerce frontend built with React, TypeScript, and Tailwind CSS for an Object-Oriented Programming course project.

## 🚀 Features

### Core Functionality
- ✅ **Authentication**: Login, Register, Password Reset with JWT
- ✅ **Product Browsing**: Browse products with pagination, filtering, and search
- ✅ **Product Details**: Detailed product pages with reviews and ratings
- ✅ **Shopping Cart**: Add, remove, update cart items with real-time totals
- ✅ **Wishlist**: Save products for later
- ✅ **Orders**: View order history and track orders
- ✅ **Notifications**: Real-time notifications center
- ✅ **Reviews**: Read and write product reviews

### User Roles
- **Customer**: Standard shopping experience
- **Retailer**: Seller account with dashboard access
- **Wholesaler**: Bulk purchasing capabilities
- **Admin**: Dashboard with analytics and management

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **React Query** - Server state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **date-fns** - Date formatting
- **Lucide React** - Icon library
- **React Hot Toast** - Toast notifications

## 📦 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
copy .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Lint code
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── store/         # Zustand state stores
│   ├── lib/           # API client and utilities
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main app with routing
│   └── main.tsx       # Entry point
├── public/            # Static assets
└── .env              # Environment variables
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Tailwind Customization

Edit `tailwind.config.js` to customize colors, fonts, etc.

## 🌐 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api/v1`.

### Key API Endpoints
- **Auth**: `/auth/login`, `/auth/register`
- **Products**: `/products`, `/products/{id}`
- **Cart**: `/cart`
- **Orders**: `/orders`
- **Reviews**: `/reviews`
- **Wishlist**: `/wishlist`
- **Notifications**: `/notifications`

## 📱 Pages

- **Home** (`/`) - Landing page with featured products
- **Products** (`/products`) - Product listing with filters
- **Product Detail** (`/products/:id`) - Product details and reviews
- **Cart** (`/cart`) - Shopping cart
- **Wishlist** (`/wishlist`) - Saved items
- **Orders** (`/orders`) - Order history
- **Notifications** (`/notifications`) - Notification center
- **Login** (`/login`) - User login
- **Register** (`/register`) - User registration

## 🎨 Design Principles

- **Minimalist** - Clean, uncluttered interface
- **Modern** - Contemporary design patterns
- **Responsive** - Mobile-first approach
- **Accessible** - WCAG compliant
- **Fast** - Optimized performance

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

## 🐛 Troubleshooting

### API Connection Issues
1. Verify backend is running on `http://localhost:8000`
2. Check `.env` file has correct `VITE_API_URL`
3. Verify backend ALLOWED_ORIGINS includes `http://localhost:5173`

### Build Errors
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

## 📄 License

Educational use only - Object-Oriented Programming Course Project

---

**Built with ❤️ for learning**
