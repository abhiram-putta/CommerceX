import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../lib/api';
import type { Order } from '../types';
import { ArrowLeft, Package, Clock, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

export default function OrderDetail() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchOrder = async () => {
      setIsLoading(true);
      try {
        const data = await api.getOrder(id);
        setOrder(data);
      } catch (error) {
        toast.error('Failed to load order details');
      } finally {
        setIsLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

  const getStatusIcon = (status: Order['status']) => {
    switch (status) {
      case 'delivered':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'processing':
      case 'shipped':
        return <Clock className="h-5 w-5 text-blue-600" />;
      default:
        return <Package className="h-5 w-5 text-gray-600" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!order) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <Package className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Order not found</h1>
          <p className="text-gray-600 mb-6">We couldn&apos;t find the order you&apos;re looking for.</p>
          <Link to="/orders" className="btn btn-primary inline-flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Orders
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/orders" className="inline-flex items-center text-sm text-gray-600 hover:text-primary-600">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Orders
          </Link>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              Order #{order.order_number}
            </h1>
            <p className="text-sm text-gray-600">
              Placed on {format(new Date(order.created_at), 'MMM d, yyyy • h:mm a')}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(order.status)}
            <span className="badge bg-gray-100 text-gray-800 capitalize">
              {order.status.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3 mb-6">
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-sm font-semibold text-gray-700 tracking-wide uppercase">
              Items
            </h2>
            <div className="space-y-4">
              {order.items.map((item) => (
                <div key={item.id} className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-16 h-16 rounded-lg bg-gray-100 overflow-hidden">
                    {item.product?.images?.[0] && (
                      <img
                        src={item.product.images[0]}
                        alt={item.product_name}
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.product_name}</p>
                    <p className="text-sm text-gray-600">
                      Qty {item.quantity} • ${item.unit_price.toFixed(2)} each
                    </p>
                  </div>
                  <div className="text-right font-semibold text-gray-900">
                    ${item.total_price.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h2 className="text-sm font-semibold text-gray-700 tracking-wide uppercase mb-2">
                Summary
              </h2>
              <div className="space-y-1 text-sm text-gray-700">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>${order.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax</span>
                  <span>${order.tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Delivery</span>
                  <span>${order.delivery_charge.toFixed(2)}</span>
                </div>
                {order.discount > 0 && (
                  <div className="flex justify-between text-green-700">
                    <span>Discount</span>
                    <span>- ${order.discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-2 mt-2 flex justify-between font-semibold">
                  <span>Total</span>
                  <span>${order.total_amount.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-sm font-semibold text-gray-700 tracking-wide uppercase mb-2">
                Delivery Address
              </h2>
              <div className="text-sm text-gray-700 space-y-1">
                <p>{order.delivery_address.address_line1}</p>
                {order.delivery_address.address_line2 && (
                  <p>{order.delivery_address.address_line2}</p>
                )}
                <p>
                  {order.delivery_address.city}, {order.delivery_address.state}
                </p>
                <p>
                  {order.delivery_address.country} - {order.delivery_address.pincode}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

