import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import type { ProductListItem, Category } from '../types';
import { ShoppingCart, Star, TrendingUp, Sparkles, Zap, Heart } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';
import { useCartStore } from '../store/cartStore';

export default function Home() {
  const [featuredProducts, setFeaturedProducts] = useState<ProductListItem[]>([]);
  const [trendingProducts, setTrendingProducts] = useState<ProductListItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated } = useAuthStore();
  const { addItem, refreshCount } = useCartStore();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [featured, trending, cats] = await Promise.all([
        api.getFeaturedProducts(8),
        api.getTrendingProducts(8),
        api.getCategories(),
      ]);
      setFeaturedProducts(featured);
      setTrendingProducts(trending);
      setCategories(cats.filter(c => c.is_active).slice(0, 6));
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCart = async (productId: string) => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }

    try {
      // Note: In production, you'd need to select a specific inventory item
      await addItem(productId, productId, 1);
      await refreshCount();
      toast.success('Added to cart!');
    } catch (error: any) {
      toast.error(error?.response?.data?.message || 'Failed to add to cart');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200 border-t-purple-600 mx-auto"></div>
            <Sparkles className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-purple-600 animate-pulse" />
          </div>
          <p className="mt-6 text-lg text-gray-700 font-medium">Loading amazing products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 min-h-screen">
      {/* Hero Section - Enhanced with vibrant gradients */}
      <section className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white">
        {/* Animated background shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-1/2 -right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full mb-6 animate-bounce">
              <Sparkles className="h-5 w-5" />
              <span className="text-sm font-semibold">Premium Quality Products</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold mb-6">
              Welcome to <span className="bg-clip-text text-transparent bg-gradient-to-r from-yellow-200 via-pink-200 to-purple-200">sMart</span>
            </h1>

            <p className="text-xl md:text-2xl mb-10 text-purple-100 max-w-2xl mx-auto">
              Discover quality products at amazing prices with lightning-fast delivery
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/products"
                className="group inline-flex items-center gap-2 bg-white text-purple-600 px-8 py-4 rounded-xl font-bold hover:bg-purple-50 transition-all transform hover:scale-105 hover:shadow-2xl"
              >
                <ShoppingCart className="h-5 w-5 group-hover:animate-bounce" />
                Shop Now
              </Link>
              <Link
                to="/products?featured=true"
                className="group inline-flex items-center gap-2 bg-purple-700/50 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-bold hover:bg-purple-700/70 transition-all transform hover:scale-105 border-2 border-white/30"
              >
                <Zap className="h-5 w-5 group-hover:animate-pulse" />
                Featured Deals
              </Link>
            </div>
          </div>
        </div>

        {/* Wave decoration */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
            <path d="M0 0L60 10C120 20 240 40 360 46.7C480 53 600 47 720 43.3C840 40 960 40 1080 46.7C1200 53 1320 67 1380 73.3L1440 80V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0V0Z" fill="#faf5ff"/>
          </svg>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          Shop by Category
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((category, idx) => (
            <Link
              key={category.id}
              to={`/products?category=${category.id}`}
              className="group card p-6 text-center hover:shadow-xl transition-all transform hover:-translate-y-1 bg-white border-2 border-transparent hover:border-purple-200"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                <span className="text-3xl font-bold text-purple-600">{category.name[0]}</span>
              </div>
              <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">{category.name}</h3>
              {category.product_count && (
                <p className="text-sm text-gray-500 mt-1">{category.product_count} items</p>
              )}
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white animate-pulse" />
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Featured Products
            </h2>
          </div>
          <Link to="/products?featured=true" className="text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-all">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredProducts.map((product, idx) => (
            <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} index={idx} />
          ))}
        </div>
      </section>

      {/* Trending Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 pb-24">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-rose-600 rounded-xl flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
              Trending Now
            </h2>
          </div>
          <Link to="/products?trending=true" className="text-pink-600 hover:text-pink-700 font-semibold hover:underline transition-all">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {trendingProducts.map((product, idx) => (
            <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} index={idx} />
          ))}
        </div>
      </section>
    </div>
  );
}

function ProductCard({ product, onAddToCart, index }: { product: ProductListItem; onAddToCart: (id: string) => void; index: number }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="card group hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 bg-white border-2 border-transparent hover:border-purple-200 overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ animationDelay: `${index * 75}ms` }}
    >
      <Link to={`/products/${product.id}`} className="block">
        <div className="relative aspect-square overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100">
          <img
            src={product.images[0] || '/placeholder-product.jpg'}
            alt={product.name}
            className={`w-full h-full object-cover transition-transform duration-500 ${isHovered ? 'scale-110' : 'scale-100'}`}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

          {product.is_featured && (
            <span className="absolute top-3 left-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1 animate-pulse">
              <Sparkles className="h-3 w-3" />
              Featured
            </span>
          )}
          {product.is_local_product && (
            <span className="absolute top-3 right-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg">
              Local
            </span>
          )}

          <button className="absolute top-3 right-3 p-2 bg-white/90 backdrop-blur-sm rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:scale-110 transform">
            <Heart className="h-4 w-4 text-pink-500" />
          </button>
        </div>
      </Link>
      <div className="p-5">
        <Link to={`/products/${product.id}`}>
          <h3 className="font-bold text-gray-900 mb-1 hover:text-purple-600 line-clamp-2 transition-colors">
            {product.name}
          </h3>
        </Link>
        <p className="text-sm text-gray-500 mb-3 font-medium">{product.brand}</p>
        <div className="flex items-center mb-4">
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`h-4 w-4 ${i < Math.floor(product.avg_rating) ? 'fill-yellow-400 text-yellow-400' : 'fill-gray-200 text-gray-200'}`}
              />
            ))}
          </div>
          <span className="text-sm font-semibold text-gray-700 ml-2">{product.avg_rating.toFixed(1)}</span>
          <span className="text-sm text-gray-400 ml-1">({product.review_count})</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              ${product.base_price.toFixed(2)}
            </span>
          </div>
          <button
            onClick={() => onAddToCart(product.id)}
            className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-110 hover:shadow-lg group"
          >
            <ShoppingCart className="h-5 w-5 group-hover:animate-bounce" />
          </button>
        </div>
      </div>
    </div>
  );
}
