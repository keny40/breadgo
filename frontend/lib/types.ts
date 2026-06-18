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
  distance_km?: number | null;
};

export type Product = {
  id: string;
  store_id: string;
  name: string;
  description: string | null;
  image_url: string | null;
  original_price: string;
  discount_price: string;
  quantity: number;
  allow_pickup: boolean;
  allow_quick_delivery: boolean;
  allow_parcel_delivery: boolean;
  quick_delivery_fee: string;
  parcel_delivery_fee: string;
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
  product_amount: string;
  delivery_fee: string;
  total_price: string;
  fulfillment_method: string;
  recipient_name: string | null;
  recipient_phone: string | null;
  delivery_address: string | null;
  delivery_request_memo: string | null;
  delivery_status: string;
  status: string;
  pickup_code: string;
  reserved_at: string;
  pickup_deadline: string;
  created_at: string;
  updated_at: string;
  product_name: string | null;
  store_name: string | null;
  customer_email: string | null;
  customer_name: string | null;
  payment_status: string | null;
};

export const deliveryStatuses = [
  "REQUESTED",
  "PREPARING",
  "SENT",
  "DELIVERED",
  "CANCELLED",
] as const;

export function deliveryStatusLabel(status: string | null | undefined): string {
  const labels: Record<string, string> = {
    NOT_REQUIRED: "해당 없음",
    REQUESTED: "요청 접수",
    PREPARING: "준비중",
    SENT: "발송/배차 완료",
    DELIVERED: "전달 완료",
    CANCELLED: "취소됨",
  };
  return status ? labels[status] || status : "-";
}

export type PickupConfirmResponse = {
  reservation: Reservation;
};

export type ReservationHistory = {
  id: string;
  reservation_id: string;
  actor_user_id: string | null;
  actor_role: string | null;
  actor_email: string | null;
  event_type: string;
  from_status: string | null;
  to_status: string | null;
  message: string;
  created_at: string;
};

export type Notification = {
  id: string;
  user_id: string;
  role: string;
  title: string;
  message: string;
  notification_type: string;
  related_reservation_id: string | null;
  related_payment_id: string | null;
  related_settlement_id: string | null;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
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
  product_name: string | null;
  store_name: string | null;
  reservation_status: string | null;
  pickup_code: string | null;
  fulfillment_method: string | null;
  delivery_fee: string | null;
  delivery_status: string | null;
};

export type Settlement = {
  id: string;
  merchant_id: string;
  store_id: string;
  reservation_id: string;
  payment_id: string;
  gross_amount: string;
  platform_fee_rate: string;
  platform_fee_amount: string;
  pg_fee_rate: string;
  pg_fee_amount: string;
  merchant_settlement_amount: string;
  status: string;
  settled_at: string | null;
  admin_memo: string | null;
  hold_reason: string | null;
  created_at: string;
  updated_at: string;
  product_name: string | null;
  store_name: string | null;
  merchant_name: string | null;
  merchant_email: string | null;
  reservation_status: string | null;
  payment_status: string | null;
  pickup_code: string | null;
  fulfillment_method: string | null;
  delivery_fee: string | null;
  delivery_status: string | null;
  bank_name: string | null;
  bank_account_number: string | null;
  bank_account_holder: string | null;
  settlement_cycle: string | null;
  settlement_memo: string | null;
};

export type SettlementSummary = {
  total_gross_amount: string;
  total_platform_fee_amount: string;
  total_pg_fee_amount: string;
  total_merchant_settlement_amount: string;
  pending_amount: string;
  ready_amount: string;
  paid_amount: string;
  hold_amount: string;
  cancelled_amount: string;
  count_by_status: Record<string, number>;
};

export type SettlementAccount = {
  merchant_id: string;
  business_name: string;
  bank_name: string | null;
  bank_account_number: string | null;
  bank_account_holder: string | null;
  settlement_cycle: string | null;
  settlement_memo: string | null;
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
