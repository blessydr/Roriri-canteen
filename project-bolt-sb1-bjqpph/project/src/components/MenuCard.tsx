import React from 'react';
import { MenuItem } from '../types';
import { useCartStore } from '../store/useCartStore';
import { toast } from 'react-hot-toast';

interface MenuCardProps {
  item: MenuItem;
}

export const MenuCard: React.FC<MenuCardProps> = ({ item }) => {
  const addItem = useCartStore((state) => state.addItem);

  const handleAddToCart = () => {
    addItem(item);
    toast.success(`Added ${item.name} to cart`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <img
        src={item.imageUrl}
        alt={item.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold">{item.name}</h3>
        <p className="text-gray-600 mt-1">{item.description}</p>
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xl font-bold">₹{item.price}</span>
          <button
            onClick={handleAddToCart}
            disabled={!item.available}
            className={`px-4 py-2 rounded-md ${
              item.available
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {item.available ? 'Add to Cart' : 'Out of Stock'}
          </button>
        </div>
      </div>
    </div>
  );
};