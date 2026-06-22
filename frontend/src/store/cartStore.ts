import { create } from 'zustand';
import type { Cart } from '../types';
import { api } from '../lib/api';

interface CartState {
  cart: Cart | null;
  itemCount: number;
  isLoading: boolean;
  fetchCart: () => Promise<void>;
  addItem: (productId: string, inventoryId: string, quantity: number) => Promise<void>;
  updateItem: (cartItemId: string, quantity: number) => Promise<void>;
  removeItem: (cartItemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCount: () => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
  cart: null,
  itemCount: 0,
  isLoading: false,

  fetchCart: async () => {
    set({ isLoading: true });
    try {
      const cart = await api.getCart();
      set({ cart, itemCount: cart.item_count, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  addItem: async (productId, inventoryId, quantity) => {
    try {
      await api.addToCart(productId, inventoryId, quantity);
      await get().fetchCart();
    } catch (error) {
      throw error;
    }
  },

  updateItem: async (cartItemId, quantity) => {
    try {
      await api.updateCartItem(cartItemId, quantity);
      await get().fetchCart();
    } catch (error) {
      throw error;
    }
  },

  removeItem: async (cartItemId) => {
    try {
      await api.removeCartItem(cartItemId);
      await get().fetchCart();
    } catch (error) {
      throw error;
    }
  },

  clearCart: async () => {
    try {
      await api.clearCart();
      set({ cart: null, itemCount: 0 });
    } catch (error) {
      throw error;
    }
  },

  refreshCount: async () => {
    try {
      const { count } = await api.getCartCount();
      set({ itemCount: count });
    } catch (error) {
      // Silently fail for count refresh
    }
  },
}));
