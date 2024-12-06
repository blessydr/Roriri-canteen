export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category: 'food' | 'snack' | 'beverage';
  imageUrl: string;
  available: boolean;
}

export interface CartItem extends MenuItem {
  quantity: number;
}

export interface Order {
  id: string;
  items: CartItem[];
  total: number;
  status: 'pending' | 'paid' | 'completed';
  orderedAt: Date;
  paymentId?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  orders: Order[];
}