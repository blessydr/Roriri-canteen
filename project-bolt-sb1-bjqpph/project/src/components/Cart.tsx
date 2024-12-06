import React from 'react';
import { useCartStore } from '../store/useCartStore';
import { initializeRazorpay } from '../utils/payment';
import { toast } from 'react-hot-toast';

export const Cart: React.FC = () => {
  const { items, total, updateQuantity, removeItem, clearCart } = useCartStore();

  const handleCheckout = async () => {
    try {
      const razorpay = await initializeRazorpay();
      
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID,
        amount: total * 100, // Razorpay expects amount in paise
        currency: 'INR',
        name: 'Roriri Soft Canteen',
        description: 'Food Order Payment',
        handler: function (response: any) {
          // Handle successful payment
          toast.success('Payment successful!');
          clearCart();
          // Generate PDF receipt here
        },
        prefill: {
          name: 'Customer Name',
          email: 'customer@email.com',
        },
        theme: {
          color: '#2563EB',
        },
      };

      const paymentObject = new razorpay(options);
      paymentObject.open();
    } catch (error) {
      toast.error('Payment initialization failed');
      console.error(error);
    }
  };

  if (items.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-gray-600">Your cart is empty</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Your Cart</h2>
      <div className="space-y-4">
        {items.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between bg-white p-4 rounded-lg shadow"
          >
            <div>
              <h3 className="font-semibold">{item.name}</h3>
              <p className="text-gray-600">₹{item.price} x {item.quantity}</p>
            </div>
            <div className="flex items-center space-x-4">
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => updateQuantity(item.id, parseInt(e.target.value))}
                className="w-16 px-2 py-1 border rounded"
              />
              <button
                onClick={() => removeItem(item.id)}
                className="text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6">
        <div className="text-xl font-bold">Total: ₹{total}</div>
        <button
          onClick={handleCheckout}
          className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};