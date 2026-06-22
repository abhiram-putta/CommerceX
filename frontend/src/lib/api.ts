import axios, { type AxiosError, type AxiosInstance } from 'axios';
import type {
  AuthToken,
  LoginCredentials,
  RegisterData,
  User,
  Product,
  ProductListItem,
  Category,
  Cart,
  CartItem,
  WishlistItem,
  Order,
  Review,
  ReviewSummary,
  Notification,
  PaginatedResponse,
  MessageResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              localStorage.setItem('access_token', data.access_token);
              localStorage.setItem('refresh_token', data.refresh_token);
              // Retry the original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${data.access_token}`;
                return axios.request(error.config);
              }
            } catch {
              // Refresh failed, logout
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const params = new URLSearchParams();
    params.append('email', credentials.email);
    params.append('password', credentials.password);
    const { data } = await this.client.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  }

  async register(userData: RegisterData): Promise<User> {
    const { data } = await this.client.post('/auth/register', userData);
    return data;
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get('/users/me');
    return data;
  }

  async updateProfile(profileData: Partial<User>): Promise<User> {
    const { data } = await this.client.put('/users/me/profile', profileData);
    return data;
  }

  async forgotPassword(email: string): Promise<MessageResponse> {
    const { data } = await this.client.post('/auth/forgot-password', { email });
    return data;
  }

  async resetPassword(token: string, newPassword: string): Promise<MessageResponse> {
    const { data } = await this.client.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return data;
  }

  // Product endpoints
  async getProducts(params?: {
    page?: number;
    page_size?: number;
    category_id?: string;
    brand?: string;
    is_local?: boolean;
  }): Promise<PaginatedResponse<ProductListItem>> {
    const { data } = await this.client.get('/products', { params });
    return data;
  }

  async getProduct(id: string): Promise<Product> {
    const { data } = await this.client.get(`/products/${id}`);
    return data;
  }

  async searchProducts(query: string, filters?: {
    category_id?: string;
    min_price?: number;
    max_price?: number;
    brand?: string;
    is_local?: boolean;
  }): Promise<ProductListItem[]> {
    const { data } = await this.client.get('/products/search', {
      params: { q: query, ...filters },
    });
    return data;
  }

  async getFeaturedProducts(limit = 10): Promise<ProductListItem[]> {
    const { data } = await this.client.get('/products/featured', {
      params: { limit },
    });
    return data;
  }

  // Category endpoints
  async getCategories(): Promise<Category[]> {
    const { data } = await this.client.get('/categories');
    return data;
  }

  async getCategory(id: string): Promise<Category> {
    const { data } = await this.client.get(`/categories/${id}`);
    return data;
  }

  // Cart endpoints
  async getCart(): Promise<Cart> {
    const { data } = await this.client.get('/cart');
    return data;
  }

  async addToCart(productId: string, inventoryId: string, quantity: number): Promise<CartItem> {
    const { data } = await this.client.post('/cart', {
      product_id: productId,
      inventory_id: inventoryId,
      quantity,
    });
    return data;
  }

  async updateCartItem(cartItemId: string, quantity: number): Promise<CartItem> {
    const { data } = await this.client.put(`/cart/${cartItemId}`, { quantity });
    return data;
  }

  async removeCartItem(cartItemId: string): Promise<MessageResponse> {
    const { data } = await this.client.delete(`/cart/${cartItemId}`);
    return data;
  }

  async clearCart(): Promise<MessageResponse> {
    const { data } = await this.client.delete('/cart');
    return data;
  }

  async getCartCount(): Promise<{ count: number }> {
    const { data } = await this.client.get('/cart/count');
    return data;
  }

  // Wishlist endpoints
  async getWishlist(): Promise<WishlistItem[]> {
    const { data } = await this.client.get('/wishlist');
    return data;
  }

  async addToWishlist(productId: string): Promise<WishlistItem> {
    const { data } = await this.client.post('/wishlist', { product_id: productId });
    return data;
  }

  async removeFromWishlist(productId: string): Promise<MessageResponse> {
    const { data } = await this.client.delete(`/wishlist/${productId}`);
    return data;
  }

  async getWishlistCount(): Promise<{ count: number }> {
    const { data } = await this.client.get('/wishlist/count');
    return data;
  }

  async checkInWishlist(productId: string): Promise<{ in_wishlist: boolean; product_id: string }> {
    const { data} = await this.client.get(`/wishlist/check/${productId}`);
    return data;
  }

  // Order endpoints
  async createOrder(orderData: any): Promise<Order> {
    const { data } = await this.client.post('/orders', orderData);
    return data;
  }

  async getOrders(params?: { status?: string; page?: number; page_size?: number }): Promise<Order[]> {
    const { data } = await this.client.get('/orders', { params });
    return data;
  }

  async getOrder(orderId: string): Promise<Order> {
    const { data } = await this.client.get(`/orders/${orderId}`);
    return data;
  }

  async cancelOrder(orderId: string, reason: string): Promise<Order> {
    const { data } = await this.client.post(`/orders/${orderId}/cancel`, null, {
      params: { reason },
    });
    return data;
  }

  // Review endpoints
  async createReview(reviewData: {
    product_id: string;
    rating: number;
    title?: string;
    comment?: string;
    order_id?: string;
  }): Promise<Review> {
    const { data } = await this.client.post('/reviews', reviewData);
    return data;
  }

  async getProductReviews(
    productId: string,
    params?: { verified_only?: boolean; page?: number; page_size?: number }
  ): Promise<Review[]> {
    const { data } = await this.client.get(`/reviews/product/${productId}`, { params });
    return data;
  }

  async getReviewSummary(productId: string): Promise<ReviewSummary> {
    const { data } = await this.client.get(`/reviews/product/${productId}/summary`);
    return data;
  }

  async getMyReviews(params?: { page?: number; page_size?: number }): Promise<Review[]> {
    const { data } = await this.client.get('/reviews/my-reviews', { params });
    return data;
  }

  async updateReview(reviewId: string, reviewData: Partial<Review>): Promise<Review> {
    const { data } = await this.client.put(`/reviews/${reviewId}`, reviewData);
    return data;
  }

  async deleteReview(reviewId: string): Promise<MessageResponse> {
    const { data } = await this.client.delete(`/reviews/${reviewId}`);
    return data;
  }

  // Notification endpoints
  async getNotifications(params?: {
    unread_only?: boolean;
    notification_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<Notification[]> {
    const { data } = await this.client.get('/notifications', { params });
    return data;
  }

  async getUnreadCount(): Promise<{ count: number }> {
    const { data } = await this.client.get('/notifications/unread-count');
    return data;
  }

  async markNotificationAsRead(notificationId: string): Promise<Notification> {
    const { data } = await this.client.put(`/notifications/${notificationId}/read`);
    return data;
  }

  async markAllNotificationsAsRead(): Promise<MessageResponse> {
    const { data } = await this.client.put('/notifications/mark-all-read');
    return data;
  }

  // Recommendations
  async getPersonalizedRecommendations(topN = 10): Promise<any> {
    const { data } = await this.client.get('/recommendations/for-you', {
      params: { top_n: topN },
    });
    return data;
  }

  async getSimilarProducts(productId: string, topN = 10): Promise<any> {
    const { data } = await this.client.get(`/recommendations/similar/${productId}`, {
      params: { top_n: topN },
    });
    return data;
  }

  async getTrendingProducts(topN = 10, categoryId?: string): Promise<ProductListItem[]> {
    const { data } = await this.client.get('/recommendations/trending', {
      params: { top_n: topN, category_id: categoryId },
    });
    return data;
  }

  // Admin endpoints
  async getDashboardOverview(): Promise<any> {
    const { data } = await this.client.get('/admin/dashboard/overview');
    return data;
  }

  async getSalesMetrics(period = '7d'): Promise<any> {
    const { data } = await this.client.get('/admin/dashboard/sales', {
      params: { period },
    });
    return data;
  }
}

export const api = new ApiClient();
