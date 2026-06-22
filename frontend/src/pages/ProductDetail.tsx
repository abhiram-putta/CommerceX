import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../lib/api';
import type { Product, Review, ReviewSummary } from '../types';
import { ShoppingCart, Heart, Star, Package, Shield, Truck } from 'lucide-react';
import toast from 'react-hot-toast';
import { useCartStore } from '../store/cartStore';
import { useAuthStore } from '../store/authStore';
import { format } from 'date-fns';

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewSummary, setReviewSummary] = useState<ReviewSummary | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [inWishlist, setInWishlist] = useState(false);

  const { addItem, refreshCount } = useCartStore();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (id) {
      fetchProductData();
    }
  }, [id]);

  const fetchProductData = async () => {
    if (!id) return;
    setIsLoading(true);

    try {
      const [productData, reviewsData, summaryData] = await Promise.all([
        api.getProduct(id),
        api.getProductReviews(id, { page: 1, page_size: 5 }),
        api.getReviewSummary(id),
      ]);

      setProduct(productData);
      setReviews(reviewsData);
      setReviewSummary(summaryData);

      if (isAuthenticated) {
        const wishlistStatus = await api.checkInWishlist(id);
        setInWishlist(wishlistStatus.in_wishlist);
      }
    } catch (error) {
      toast.error('Failed to load product');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }

    if (!product) return;

    try {
      await addItem(product.id, product.id, quantity);
      await refreshCount();
      toast.success(`Added ${quantity} item(s) to cart!`);
    } catch (error: any) {
      toast.error(error?.response?.data?.message || 'Failed to add to cart');
    }
  };

  const handleToggleWishlist = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to use wishlist');
      return;
    }

    if (!product) return;

    try {
      if (inWishlist) {
        await api.removeFromWishlist(product.id);
        setInWishlist(false);
        toast.success('Removed from wishlist');
      } else {
        await api.addToWishlist(product.id);
        setInWishlist(true);
        toast.success('Added to wishlist');
      }
    } catch (error) {
      toast.error('Failed to update wishlist');
    }
  };

  if (isLoading || !product) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8 text-sm">
        <Link to="/" className="text-gray-500 hover:text-gray-700">Home</Link>
        <span className="mx-2 text-gray-400">/</span>
        <Link to="/products" className="text-gray-500 hover:text-gray-700">Products</Link>
        <span className="mx-2 text-gray-400">/</span>
        <span className="text-gray-900">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
        {/* Product Images */}
        <div>
          <div className="aspect-square bg-white rounded-xl overflow-hidden mb-4 border border-gray-200">
            <img
              src={product.images[selectedImage] || '/placeholder-product.jpg'}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="grid grid-cols-4 gap-4">
            {product.images.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedImage(idx)}
                className={`aspect-square rounded-lg overflow-hidden border-2 ${
                  selectedImage === idx ? 'border-primary-600' : 'border-gray-200'
                }`}
              >
                <img src={img} alt="" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        </div>

        {/* Product Info */}
        <div>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
              <p className="text-lg text-gray-600">{product.brand}</p>
            </div>
            <button
              onClick={handleToggleWishlist}
              className={`p-2 rounded-lg ${
                inWishlist ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'
              } hover:bg-red-100 hover:text-red-600 transition-colors`}
            >
              <Heart className={`h-6 w-6 ${inWishlist ? 'fill-current' : ''}`} />
            </button>
          </div>

          {reviewSummary && (
            <div className="flex items-center mb-6">
              <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-5 w-5 ${
                      star <= reviewSummary.average_rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="ml-2 text-lg font-medium">{reviewSummary.average_rating.toFixed(1)}</span>
              <span className="ml-2 text-gray-600">({reviewSummary.total_reviews} reviews)</span>
            </div>
          )}

          <div className="text-4xl font-bold text-gray-900 mb-6">
            ${product.base_price.toFixed(2)}
          </div>

          <div className="prose prose-sm mb-6">
            <p className="text-gray-700">{product.description}</p>
          </div>

          <div className="flex items-center space-x-4 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="flex space-x-4 mb-8">
            <button onClick={handleAddToCart} className="flex-1 btn btn-primary py-3 text-lg">
              <ShoppingCart className="h-5 w-5 mr-2 inline" />
              Add to Cart
            </button>
          </div>

          <div className="grid grid-cols-3 gap-4 p-6 bg-gray-50 rounded-lg">
            <div className="text-center">
              <Truck className="h-8 w-8 mx-auto mb-2 text-primary-600" />
              <p className="text-sm font-medium">Free Shipping</p>
            </div>
            <div className="text-center">
              <Shield className="h-8 w-8 mx-auto mb-2 text-primary-600" />
              <p className="text-sm font-medium">Secure Payment</p>
            </div>
            <div className="text-center">
              <Package className="h-8 w-8 mx-auto mb-2 text-primary-600" />
              <p className="text-sm font-medium">Easy Returns</p>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="border-t border-gray-200 pt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Customer Reviews</h2>

        {reviewSummary && (
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <div className="flex items-center mb-4">
              <span className="text-5xl font-bold mr-4">{reviewSummary.average_rating.toFixed(1)}</span>
              <div>
                <div className="flex items-center mb-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`h-5 w-5 ${
                        star <= reviewSummary.average_rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <p className="text-gray-600">{reviewSummary.total_reviews} reviews</p>
              </div>
            </div>

            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((rating) => {
                const count = reviewSummary.rating_distribution[rating as keyof typeof reviewSummary.rating_distribution] || 0;
                const percentage = reviewSummary.total_reviews > 0 ? (count / reviewSummary.total_reviews) * 100 : 0;

                return (
                  <div key={rating} className="flex items-center">
                    <span className="text-sm w-12">{rating} star</span>
                    <div className="flex-1 h-2 bg-gray-200 rounded-full mx-4">
                      <div
                        className="h-full bg-yellow-400 rounded-full"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <span className="text-sm w-12 text-right">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center mb-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`h-4 w-4 ${
                          star <= review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="font-medium text-gray-900">{review.user?.full_name || 'Anonymous'}</p>
                  <p className="text-sm text-gray-500">{format(new Date(review.created_at), 'MMM d, yyyy')}</p>
                </div>
                {review.is_verified_purchase && (
                  <span className="badge bg-green-100 text-green-800">Verified Purchase</span>
                )}
              </div>
              {review.title && <h4 className="font-semibold mb-2">{review.title}</h4>}
              {review.comment && <p className="text-gray-700">{review.comment}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
