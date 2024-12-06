import axios from 'axios';
import { Order } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export const fetchOrders = async (): Promise<Order[]> => {
  const response = await axios.get(`${API_URL}/api/orders`);
  return response.data;
};

export const createOrder = async (order: Omit<Order, 'id' | 'orderedAt'>): Promise<Order> => {
  const response = await axios.post(`${API_URL}/api/orders`, order);
  return response.data;
};