export type AuthUser = {
  id: string;
  email: string;
  phone: string | null;
  full_name: string;
  role: string;
  is_active: boolean;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type Merchant = {
  id: string;
  user_id: string;
  business_name: string;
  business_registration_number: string;
  representative_name: string;
  phone_number: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type MerchantMeResponse = {
  merchant: Merchant;
};

export type Store = {
  id: string;
  merchant_id: string;
  name: string;
  address: string;
  address_detail: string | null;
  sido: string | null;
  sigungu: string | null;
  dong: string | null;
  latitude: string | null;
  longitude: string | null;
  phone_number: string;
  description: string | null;
  opening_time: string;
  closing_time: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type RegionProduct = Product & {
  store_name: string;
  store_address: string;
  sido: string | null;
  sigungu: string | null;
  dong: string | null;
};

export type Product = {
  id: string;
  store_id: string;
  name: string;
  description: string | null;
  original_price: string;
  discount_price: string;
  quantity: number;
  pickup_start_time: string;
  pickup_end_time: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Reservation = {
  id: string;
  user_id: string;
  product_id: string;
  store_id: string;
  quantity: number;
  total_price: string;
  status: string;
  pickup_code: string;
  reserved_at: string;
  pickup_deadline: string;
  created_at: string;
  updated_at: string;
};

export type PickupConfirmResponse = {
  reservation: Reservation;
};

export type Payment = {
  id: string;
  reservation_id: string;
  user_id: string;
  amount: string;
  method: string;
  status: string;
  paid_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AdminSummary = {
  total_users: number;
  total_merchants: number;
  total_stores: number;
  total_products: number;
  active_products: number;
  total_reservations: number;
  picked_up_reservations: number;
  cancelled_reservations: number;
  total_payments: number;
  paid_payments: number;
  cancelled_payments: number;
  failed_payments: number;
  refunded_payments: number;
  total_paid_amount: string;
};
