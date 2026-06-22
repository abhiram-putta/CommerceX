// User Types
export const UserRole = {
  CUSTOMER: 'customer',
  RETAILER: 'retailer',
  WHOLESALER: 'wholesaler',
  ADMIN: 'admin',
} as const;

export type UserRole = typeof UserRole[keyof typeof UserRole];

export const Gender = {
  MALE: 'male',
  FEMALE: 'female',
  OTHER: 'other',
} as const;

export type Gender = typeof Gender[keyof typeof Gender];

export interface User {
  id: string;
  email: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  profile_completion: number;
  last_login?: string;
  profile?: UserProfile;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  full_name?: string;
  profile_image_url?: string;
  date_of_birth?: string;
  gender?: Gender;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country: string;
  pincode?: string;
  business_name?: string;
  business_type?: string;
  preferences: Record<string, any>;
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  phone?: string;
  role?: string;
  full_name?: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Product Types
export interface Product {
  id: string;
  name: string;
  description: string;
  brand: string;
  category_id: string;
  category?: Category;
  base_price: number;
  is_local_product: boolean;
  is_featured: boolean;
  is_active: boolean;
  images: string[];
  specifications: Record<string, any>;
  tags: string[];
  avg_rating: number;
  review_count: number;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProductListItem {
  id: string;
  name: string;
  brand: string;
  base_price: number;
  is_local_product: boolean;
  is_featured: boolean;
  images: string[];
  avg_rating: number;
  review_count: number;
  category?: {
    id: string;
    name: string;
  };
}

// Category Types
export interface Category {
  id: string;
  name: string;
  description?: string;
  parent_id?: string;
  image_url?: string;
  is_active: boolean;
  display_order: number;
  product_count?: number;
}

// Cart Types
export interface CartItem {
  id: string;
  product_id: string;
  inventory_id: string;
  quantity: number;
  product: ProductListItem;
  price: number;
  total: number;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  tax: number;
  delivery_charge: number;
  total: number;
  item_count: number;
}

// Wishlist Types
export interface WishlistItem {
  id: string;
  product_id: string;
  product: ProductListItem;
  created_at: string;
}

// Order Types
export const OrderStatus = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  PROCESSING: 'processing',
  SHIPPED: 'shipped',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
  RETURNED: 'returned',
} as const;

export type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus];

export const OrderType = {
  ONLINE: 'online',
  IN_STORE: 'in_store',
} as const;

export type OrderType = typeof OrderType[keyof typeof OrderType];

export interface Order {
  id: string;
  order_number: string;
  user_id: string;
  status: OrderStatus;
  order_type: OrderType;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  delivery_charge: number;
  discount: number;
  total_amount: number;
  payment_method: string;
  payment_status: string;
  delivery_address: Address;
  delivery_notes?: string;
  scheduled_delivery_date?: string;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product?: ProductListItem;
}

export interface Address {
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  pincode: string;
}

// Review Types
export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  order_id?: string;
  rating: number;
  title?: string;
  comment?: string;
  images?: string[];
  is_verified_purchase: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
  user?: {
    id: string;
    full_name?: string;
    profile_image_url?: string;
  };
}

export interface ReviewSummary {
  average_rating: number;
  total_reviews: number;
  rating_distribution: {
    1: number;
    2: number;
    3: number;
    4: number;
    5: number;
  };
  verified_percentage: number;
}

// Notification Types
export const NotificationType = {
  ORDER_UPDATE: 'order_update',
  PAYMENT: 'payment',
  PROMOTION: 'promotion',
  SYSTEM: 'system',
  REVIEW: 'review',
  INVENTORY: 'inventory',
} as const;

export type NotificationType = typeof NotificationType[keyof typeof NotificationType];

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  metadata: Record<string, any>;
  created_at: string;
}

// Pagination Types
export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// API Response Types
export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  error: boolean;
  message: string;
  details?: any;
}
