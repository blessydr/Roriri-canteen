import axios from 'axios';
import { MenuItem } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export const fetchMenuItems = async (): Promise<MenuItem[]> => {
  const response = await axios.get(`${API_URL}/api/menu-items`);
  return response.data;
};