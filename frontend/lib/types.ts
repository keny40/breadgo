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
  external_sku: string | null;
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

export type ProductCsvImportError = {
  row_number: number;
  field: string;
  message: string;
};

export type ProductCsvImportResult = {
  batch_id: string | null;
  total_rows: number;
  success_count: number;
  failed_count: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  created_product_ids: string[];
  errors: ProductCsvImportError[];
  rows: ProductCsvImportRowResult[];
};

export type ProductCsvImportRowResult = {
  row_number: number;
  product_id: string | null;
  product_name: string | null;
  action: string;
  action_candidate: string;
  duplicate_detected: boolean;
  error_message: string | null;
};

export type ProductImportRow = {
  id: string;
  batch_id: string;
  row_number: number;
  product_id: string | null;
  action: string;
  product_name: string | null;
  error_message: string | null;
  created_at: string;
};

export type ProductImportBatch = {
  id: string;
  merchant_id: string;
  store_id: string | null;
  file_name: string;
  total_rows: number;
  success_count: number;
  failed_count: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  status: string;
  created_at: string;
  rows: ProductImportRow[];
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

export type OpsComponentStatus = {
  name: string;
  status: string;
  message: string | null;
};

export type OpsStatus = {
  app_name: string;
  api_version: string;
  environment: string;
  app_status: string;
  checked_at: string;
  database: OpsComponentStatus;
  payment_providers: OpsComponentStatus[];
  notification_channels: OpsComponentStatus[];
  incident_notifiers: OpsComponentStatus[];
};

export type Payment = {
  id: string;
  reservation_id: string;
  user_id: string;
  amount: string;
  method: string;
  provider: string;
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

export type ProProductSummary = {
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  status: string;
  registered_quantity: number;
  reserved_quantity: number;
  paid_quantity: number;
  picked_up_quantity: number;
  cancelled_quantity: number;
  remaining_quantity: number;
  gross_sales: string;
  estimated_settlement: string;
  sell_through_rate: number;
};

export type ProDailySummary = {
  date: string;
  registered_quantity: number;
  reserved_quantity: number;
  picked_up_quantity: number;
  cancelled_count: number;
  remaining_quantity: number;
  gross_sales: string;
  estimated_settlement: string;
  sell_through_rate: number;
};

export type MerchantProDashboard = {
  merchant_id: string;
  business_name: string;
  today_registered_quantity: number;
  today_reserved_quantity: number;
  today_paid_count: number;
  today_picked_up_count: number;
  today_cancelled_count: number;
  today_remaining_quantity: number;
  today_gross_sales: string;
  today_estimated_settlement: string;
  today_estimated_saved_items: number;
  today_estimated_waste_prevented_amount: string;
  sell_through_rate: number;
  pickup_completion_rate: number;
  cancellation_rate: number;
  product_summaries: ProProductSummary[];
  recent_7_days: ProDailySummary[];
};

export type ProStoreDashboardSummary = {
  store_id: string;
  store_name: string;
  sido: string | null;
  sigungu: string | null;
  dong: string | null;
  active_product_count: number;
  reservation_count: number;
  paid_count: number;
  picked_up_count: number;
  cancelled_count: number;
  gross_sales_amount: string;
  estimated_settlement_amount: string;
  saved_quantity: number;
  sell_through_rate: number;
  detail_views: number;
  reservation_conversion_rate: number;
  status_label: string;
  store_insight_message: string;
};

export type MerchantProStoresDashboard = {
  merchant_id: string;
  business_name: string;
  period_days: number;
  total_stores: number;
  total_reservations: number;
  total_sales_amount: string;
  total_picked_up_count: number;
  total_saved_quantity: number;
  average_sell_through_rate: number;
  stores: ProStoreDashboardSummary[];
};

export type ProPlanFeatures = {
  yield_dashboard: boolean;
  relist_products: boolean;
  product_templates: boolean;
  csv_product_import: boolean;
  inventory_ledger: boolean;
  inventory_alerts: boolean;
  esg_report: boolean;
  recommendations: boolean;
  recommendation_performance: boolean;
  product_funnel: boolean;
  multi_store_dashboard: boolean;
  pos_api_integration: boolean;
};

export type MerchantProPlan = {
  merchant_id: string;
  business_name: string;
  current_plan: string;
  plan_label: string;
  is_pro_active: boolean;
  trial_ends_at: string | null;
  features: ProPlanFeatures;
  upgrade_message: string;
};

export type ProEsgProductSummary = {
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  saved_items: number;
  saved_amount: string;
  pickup_completed_count: number;
  cancelled_count: number;
  contribution_rate: number;
};

export type ProEsgDailyTrend = {
  date: string;
  saved_items: number;
  saved_amount: string;
  pickup_completed_count: number;
  cancelled_count: number;
};

export type MerchantProEsgReport = {
  merchant_id: string;
  business_name: string;
  today_saved_items: number;
  week_saved_items: number;
  month_saved_items: number;
  today_saved_amount: string;
  week_saved_amount: string;
  month_saved_amount: string;
  estimated_waste_reduction_items: number;
  estimated_waste_prevention_amount: string;
  pickup_completed_count: number;
  cancelled_count: number;
  sell_through_rate: number;
  carbon_reduction_note: string;
  product_esg_summaries: ProEsgProductSummary[];
  daily_esg_trend: ProEsgDailyTrend[];
};

export type ProRecommendation = {
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  recent_reserved_quantity: number;
  recent_picked_up_quantity: number;
  recent_cancelled_quantity: number;
  detail_views: number;
  reservation_started_count: number;
  reservation_count: number;
  view_to_reservation_rate: number;
  started_to_created_rate: number;
  funnel_signal_label: string;
  funnel_message: string;
  current_stock_quantity: number;
  sell_through_rate: number;
  pickup_completion_rate: number;
  recommended_stock_quantity: number;
  current_discount_price: string;
  recommended_discount_price: string;
  recommendation_type: string;
  recommendation_message: string;
  confidence_label: string;
  explanation_title: string;
  explanation_reasons: string[];
  suggested_actions: string[];
  primary_action_label: string;
  action_priority: string;
  risk_label: string;
};

export type MerchantProRecommendations = {
  period_days: number;
  note: string;
  recommendations: ProRecommendation[];
};

export type ProDailyBriefTask = {
  task_type: string;
  priority: string;
  title: string;
  message: string;
  action_label: string;
  action_href: string;
};

export type MerchantProDailyBrief = {
  date: string;
  today_sales_amount: string;
  today_reservation_count: number;
  today_picked_up_count: number;
  today_cancelled_count: number;
  saved_quantity_today: number;
  unresolved_alert_count: number;
  action_started_alert_count: number;
  high_severity_alert_count: number;
  recommendation_action_count: number;
  pos_last_sync_status: string | null;
  pos_last_synced_at: string | null;
  csv_recent_import_count: number;
  csv_recent_failed_count: number;
  inventory_event_count_today: number;
  tasks: ProDailyBriefTask[];
};

export type ProDailyBriefSnapshotTask = {
  id: string;
  snapshot_id: string;
  task_type: string;
  priority: string;
  title: string;
  message: string;
  action_label: string | null;
  action_href: string | null;
  created_at: string;
};

export type ProDailyBriefSnapshot = {
  id: string;
  merchant_id: string;
  store_id: string | null;
  brief_date: string;
  today_sales_amount: string;
  today_reservation_count: number;
  today_picked_up_count: number;
  today_cancelled_count: number;
  saved_quantity_today: number;
  unresolved_alert_count: number;
  action_started_alert_count: number;
  high_severity_alert_count: number;
  recommendation_action_count: number;
  pos_last_sync_status: string | null;
  pos_last_synced_at: string | null;
  csv_recent_import_count: number;
  csv_recent_failed_count: number;
  inventory_event_count_today: number;
  created_at: string;
  updated_at: string;
  tasks: ProDailyBriefSnapshotTask[];
};

export type ProDailyBriefHistoryDelta = {
  unresolved_alert_delta: number | null;
  sales_delta: string | null;
  reservation_delta: number | null;
  picked_up_delta: number | null;
  saved_quantity_delta: number | null;
};

export type MerchantProDailyBriefHistory = {
  snapshots: ProDailyBriefSnapshot[];
  latest_snapshot_id: string | null;
  previous_snapshot_id: string | null;
  delta: ProDailyBriefHistoryDelta;
};

export type ProWeeklyReportDailyTrend = {
  date: string;
  sales_amount: string;
  reservation_count: number;
  picked_up_count: number;
  cancelled_count: number;
  saved_quantity: number;
  unresolved_alert_count: number;
  recommendation_action_count: number;
};

export type ProWeeklyReportInsight = {
  title: string;
  message: string;
  severity: string;
};

export type MerchantProWeeklyReport = {
  start_date: string;
  end_date: string;
  total_sales_amount: string;
  total_reservation_count: number;
  total_picked_up_count: number;
  total_cancelled_count: number;
  total_saved_quantity: number;
  average_unresolved_alert_count: number;
  high_severity_alert_count: number;
  total_recommendation_action_count: number;
  total_inventory_event_count: number;
  pos_sync_issue_count: number;
  csv_import_error_count: number;
  snapshot_days_count: number;
  daily_trends: ProWeeklyReportDailyTrend[];
  insights: ProWeeklyReportInsight[];
};

export type ProWeeklyReportSnapshotInsight = {
  id: string;
  snapshot_id: string;
  title: string | null;
  message: string;
  severity: string | null;
  created_at: string;
};

export type ProWeeklyReportSnapshot = {
  id: string;
  merchant_id: string;
  store_id: string | null;
  start_date: string;
  end_date: string;
  total_sales_amount: string;
  total_reservation_count: number;
  total_picked_up_count: number;
  total_cancelled_count: number;
  total_saved_quantity: number;
  average_unresolved_alert_count: string;
  high_severity_alert_count: number;
  total_recommendation_action_count: number;
  total_inventory_event_count: number;
  pos_sync_issue_count: number;
  csv_import_error_count: number;
  text_summary: string | null;
  created_at: string;
  updated_at: string;
  insights: ProWeeklyReportSnapshotInsight[];
};

export type MerchantProWeeklyReportHistory = {
  snapshots: ProWeeklyReportSnapshot[];
};

export type ProWeeklyReportAutoSnapshotPreview = {
  start_date: string;
  end_date: string;
  would_create_new: boolean;
  existing_snapshot_id: string | null;
  report_summary: MerchantProWeeklyReport;
  insights: ProWeeklyReportInsight[];
};

export type ProWeeklyReportAutoSnapshotRun = {
  snapshot_id: string;
  created_or_updated: "CREATED" | "UPDATED" | string;
  start_date: string;
  end_date: string;
  message: string;
};

export type ProWeeklyReportBatchRunItem = {
  id: string;
  batch_run_id: string;
  merchant_id: string;
  snapshot_id: string | null;
  status: string;
  message: string | null;
  created_at: string;
};

export type ProWeeklyReportBatchRun = {
  id: string;
  run_type: string;
  status: string;
  start_date: string;
  end_date: string;
  target_merchant_count: number;
  success_count: number;
  failed_count: number;
  skipped_count: number;
  message: string | null;
  created_at: string;
  completed_at: string | null;
  items: ProWeeklyReportBatchRunItem[];
};

export type MerchantProWeeklyReportBatchRunHistory = {
  batch_runs: ProWeeklyReportBatchRun[];
};

export type AdminProWeeklyReportBatchRunSummary = {
  total_runs: number;
  completed_count: number;
  failed_count: number;
  partial_count: number;
  latest_run_status: string | null;
  latest_run_at: string | null;
};

export type AdminProWeeklyReportBatchRunMonitor = {
  summary: AdminProWeeklyReportBatchRunSummary;
  batch_runs: ProWeeklyReportBatchRun[];
};

export type AdminWeeklyReportBatchPreview = {
  start_date: string;
  end_date: string;
  target_merchant_count: number;
  would_create_or_update_count: number;
  message: string;
};

export type ProWeeklyReportDeliveryRunItem = {
  id: string;
  delivery_run_id: string;
  merchant_id: string;
  snapshot_id: string | null;
  status: string;
  reason: string | null;
  created_at: string;
};

export type ProWeeklyReportDeliveryRun = {
  id: string;
  run_type: string;
  channel: string;
  status: string;
  period_start: string;
  period_end: string;
  total_count: number;
  ready_count: number;
  skipped_count: number;
  failed_count: number;
  message: string | null;
  created_at: string;
  completed_at: string | null;
  items: ProWeeklyReportDeliveryRunItem[];
};

export type AdminProWeeklyReportDeliveryRunHistory = {
  delivery_runs: ProWeeklyReportDeliveryRun[];
};

export type ProWeeklyReportInAppNotification = {
  notification_id: string;
  snapshot_id: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
  read_at: string | null;
};

export type MerchantProWeeklyReportNotificationList = {
  notifications: ProWeeklyReportInAppNotification[];
};

export type ProRecommendationDraftCreateResponse = {
  created_product: Product;
  usage_id: string;
  recommendation: ProRecommendation;
};

export type RecommendationTypeUsageSummary = {
  recommendation_type: string;
  count: number;
  picked_up_quantity: number;
  paid_amount: string;
};

export type RecommendationUsage = {
  id: string;
  source_product_id: string;
  source_product_name: string | null;
  created_product_id: string | null;
  created_product_name: string | null;
  recommendation_type: string;
  confidence_label: string;
  recommended_stock_quantity: number;
  recommended_discount_price: string;
  original_stock_quantity: number | null;
  original_discount_price: string | null;
  accepted_stock_quantity: number | null;
  accepted_discount_price: string | null;
  stock_delta: number | null;
  discount_price_delta: string | null;
  adoption_type: string | null;
  draft_product_status: string | null;
  published_at: string | null;
  first_reserved_at: string | null;
  first_paid_at: string | null;
  first_picked_up_at: string | null;
  action_type: string;
  created_product_reserved_quantity: number;
  created_product_picked_up_quantity: number;
  created_product_paid_amount: string;
  created_product_sell_through_rate: number;
  created_at: string;
};

export type MerchantProRecommendationPerformance = {
  total_recommendation_drafts: number;
  draft_created_count: number;
  published_from_recommendation_count: number;
  publish_conversion_rate: number;
  reserved_after_publish_count: number;
  paid_after_publish_count: number;
  picked_up_after_publish_count: number;
  average_time_to_publish_minutes: number;
  used_recommendation_count: number;
  recommendation_created_products_count: number;
  picked_up_quantity_from_recommendations: number;
  paid_amount_from_recommendations: string;
  average_sell_through_rate_from_recommendations: number;
  exact_accept_count: number;
  modified_accept_count: number;
  exact_accept_rate: number;
  modified_accept_rate: number;
  average_stock_delta: number;
  average_discount_price_delta: string;
  action_card_click_count: number;
  draft_create_started_count: number;
  action_draft_created_count: number;
  action_to_draft_rate: number;
  recent_action_events: RecommendationActionEvent[];
  usage_by_recommendation_type: RecommendationTypeUsageSummary[];
  recent_usages: RecommendationUsage[];
  recent_funnel_usages: RecommendationUsage[];
};

export type RecommendationActionEvent = {
  id: string;
  merchant_id: string;
  product_id: string | null;
  recommendation_type: string | null;
  action_priority: string | null;
  risk_label: string | null;
  event_type: string;
  source: string;
  created_product_id: string | null;
  created_at: string;
};

export type ProProductFunnelSummary = {
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  detail_views: number;
  reservation_started_count: number;
  reservations: number;
  paid_count: number;
  picked_up_count: number;
  conversion_rate: number;
  paid_conversion_rate: number;
  pickup_conversion_rate: number;
  paid_amount: string;
  from_recommendation: boolean;
  attention_label: string;
};

export type MerchantProProductFunnel = {
  period_days: number;
  total_detail_views: number;
  total_reservation_starts: number;
  total_reservations: number;
  total_paid_count: number;
  total_picked_up_count: number;
  detail_to_reservation_rate: number;
  product_funnel_summaries: ProProductFunnelSummary[];
};

export type PosIntegration = {
  id: string;
  merchant_id: string;
  store_id: string | null;
  provider: string;
  status: string;
  external_store_code: string | null;
  last_synced_at: string | null;
  last_sync_status: string | null;
  created_at: string;
  updated_at: string;
};

export type PosSyncRow = {
  id: string;
  batch_id: string;
  external_sku: string | null;
  product_id: string | null;
  action: string;
  product_name: string | null;
  error_message: string | null;
  created_at: string;
};

export type PosSyncBatch = {
  id: string;
  integration_id: string;
  merchant_id: string;
  store_id: string | null;
  total_rows: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  failed_count: number;
  status: string;
  created_at: string;
  rows: PosSyncRow[];
};

export type MockPosSyncResult = {
  batch_id: string;
  total_rows: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  failed_count: number;
  status: string;
  rows: PosSyncRow[];
};

export type ProductInventoryEvent = {
  id: string;
  merchant_id: string;
  store_id: string | null;
  product_id: string;
  product_name: string | null;
  store_name: string | null;
  event_type: string;
  quantity_before: number | null;
  quantity_after: number | null;
  quantity_delta: number | null;
  source_type: string | null;
  source_id: string | null;
  note: string | null;
  created_at: string;
};

export type ProInventoryAlert = {
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  severity: string;
  alert_type: string;
  title: string;
  message: string;
  suggested_action: string;
  current_stock_quantity: number;
  related_metric: string | null;
  recent_inventory_note: string | null;
  detected_at: string;
  latest_action_type: string | null;
  latest_action_at: string | null;
  is_acknowledged: boolean;
  is_resolved: boolean;
};

export type MerchantProInventoryAlerts = {
  total_alerts: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  alerts: ProInventoryAlert[];
};

export type InventoryAlertAction = {
  id: string;
  merchant_id: string;
  product_id: string | null;
  product_name: string | null;
  alert_type: string;
  severity: string;
  action_type: string;
  note: string | null;
  created_at: string;
};

export type ProductTemplate = {
  id: string;
  merchant_id: string;
  source_product_id: string;
  template_name: string;
  day_of_week: number;
  default_stock_quantity: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  source_product_name: string | null;
  source_store_name: string | null;
};

export type ProductTemplateCreateProductsResponse = {
  created_products: Product[];
  skipped_template_ids: string[];
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
