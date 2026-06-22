import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../lib/api';
import type { ProductListItem, Category } from '../types';
import { ShoppingCart, Star, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';

export default function Products() {
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const { addItem, refreshCount } = useCartStore();
  const { isAuthenticated } = useAuthStore();

  const searchQuery = (searchParams.get('q') || '').trim();

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [page, selectedCategory, searchParams]);

  const fetchCategories = async () => {
    try {
      const cats = await api.getCategories();
      setCategories(cats.filter(c => c.is_active));
    } catch (error) {
      toast.error('Failed to load categories');
    }
  };

  const fetchProducts = async () => {
    setIsLoading(true);
    try {
      const categoryId = searchParams.get('category') || selectedCategory;
      if (searchQuery) {
        const data = await api.searchProducts(searchQuery, {
          category_id: categoryId || undefined,
        });
        setProducts(data);
        setTotal(data.length);
        setPage(1);
      } else {
        const data = await api.getProducts({
          page,
          page_size: 20,
          category_id: categoryId || undefined,
        });
        setProducts(data.items);
        setTotal(data.total);
      }
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
      await addItem(productId, productId, 1);
      await refreshCount();
      toast.success('Added to cart!');
    } catch (error: any) {
      toast.error(error?.response?.data?.message || 'Failed to add to cart');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Filters Sidebar */}
        <aside className="md:w-64 flex-shrink-0">
          <div className="card p-4 sticky top-20">
            <div className="flex items-center mb-4">
              <Filter className="h-5 w-5 mr-2" />
              <h2 className="font-semibold text-gray-900">Filters</h2>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Categories</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => {
                      setSelectedCategory('');
                      setPage(1);
                    }}
                    className={`block w-full text-left px-3 py-2 rounded-lg text-sm ${
                      !selectedCategory ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
                    }`}
                  >
                    All Products
                  </button>
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => {
                        setSelectedCategory(cat.id);
                        setPage(1);
                      }}
                      className={`block w-full text-left px-3 py-2 rounded-lg text-sm ${
                        selectedCategory === cat.id ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
                      }`}
                    >
                      {cat.name}
                      {cat.product_count && (
                        <span className="text-gray-500 ml-1">({cat.product_count})</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Products Grid */}
        <div className="flex-1">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Products</h1>
            <p className="text-gray-600">
              {searchQuery
                ? `Showing ${total} result${total === 1 ? '' : 's'} for “${searchQuery}”`
                : `${total} products found`}
            </p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">No products found</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {products.map((product) => (
                  <div key={product.id} className="card group hover:shadow-lg transition-shadow">
                    <Link to={`/products/${product.id}`} className="block">
                      <div className="relative aspect-square overflow-hidden">
                        <img
                          src={product.images[0] || '/placeholder-product.jpg'}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        {product.is_featured && (
                          <span className="absolute top-2 left-2 bg-primary-600 text-white text-xs px-2 py-1 rounded-md">
                            Featured
                          </span>
                        )}
                      </div>
                    </Link>
                    <div className="p-4">
                      <Link to={`/products/${product.id}`}>
                        <h3 className="font-semibold text-gray-900 mb-1 hover:text-primary-600 line-clamp-2">
                          {product.name}
                        </h3>
                      </Link>
                      <p className="text-sm text-gray-500 mb-2">{product.brand}</p>
                      <div className="flex items-center mb-3">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm ml-1">{product.avg_rating.toFixed(1)}</span>
                        <span className="text-sm text-gray-500 ml-2">({product.review_count})</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xl font-bold text-gray-900">${product.base_price.toFixed(2)}</span>
                        <button
                          onClick={() => handleAddToCart(product.id)}
                          className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                        >
                          <ShoppingCart className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {!searchQuery && total > 20 && (
                <div className="mt-8 flex justify-center">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2">
                      Page {page} of {Math.ceil(total / 20)}
                    </span>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page >= Math.ceil(total / 20)}
                      className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
