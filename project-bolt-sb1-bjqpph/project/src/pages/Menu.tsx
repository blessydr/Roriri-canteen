import React from 'react';
import { useQuery } from 'react-query';
import { MenuCard } from '../components/MenuCard';
import { MenuItem } from '../types';
import { fetchMenuItems } from '../api/menuItems';

export const Menu: React.FC = () => {
  const { data: menuItems, isLoading, error } = useQuery<MenuItem[]>('menuItems', fetchMenuItems);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 p-4">
        Error loading menu items. Please try again later.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {menuItems?.map((item) => (
        <MenuCard key={item.id} item={item} />
      ))}
    </div>
  );
};