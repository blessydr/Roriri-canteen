import React from 'react';
import { useQuery } from 'react-query';
import { Order } from '../types';
import { fetchOrders } from '../api/orders';
import { format } from 'date-fns';

export const Orders: React.FC = () => {
  const { data: orders, isLoading } = useQuery<Order[]>('orders', fetchOrders);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Your Orders</h2>
      {orders?.map((order) => (
        <div key={order.id} className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-lg font-semibold">Order #{order.id.slice(0, 8)}</h3>
              <p className="text-gray-600">
                {format(new Date(order.orderedAt), 'PPpp')}
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm ${
              order.status === 'completed' ? 'bg-green-100 text-green-800' :
              order.status === 'paid' ? 'bg-blue-100 text-blue-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
            </span>
          </div>
          <div className="space-y-2">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between">
                <span>{item.name} x {item.quantity}</span>
                <span>₹{item.price * item.quantity}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex justify-between font-semibold">
              <span>Total</span>
              <span>₹{order.total}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};