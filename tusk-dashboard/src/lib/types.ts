export type BookingStatus = "held" | "confirmed" | "cancelled" | "expired";

export type Hours = { weekday: number; open: string; close: string };

export type Business = {
  slug: string;
  name: string;
  category: string;
  area: string;
  address: string;
  about: string;
  whatsapp: string;
  cover_photo: string;
  deposit_naira: number;
  home_service: boolean;
  home_service_fee_naira: number;
  located: boolean;
  profile_url: string;
  policies: string[];
  hours: Hours[];
  customer_mcp_url: string;
  owner_mcp_url: string;
  payments: "paystack-test" | "paystack-live" | "test";
};

export type PublicBusinessSummary = {
  slug: string;
  name: string;
  category: string;
  area: string;
  about: string;
  profile_url: string;
  cover_photo: string;
};

export type PublicBusiness = PublicBusinessSummary & {
  address: string;
  whatsapp_url: string | null;
  opening_hours: string[];
  deposit_to_book: string | null;
  home_service: { offered: boolean; fee: string | null };
  policies: string[];
  services: Service[];
  customer_mcp_url: string;
};

export type Me = {
  user: { id: number; name: string; email: string; phone: string };
  business: Business;
};

export type Service = {
  id: number;
  name: string;
  description: string;
  price: string;
  price_kobo: number;
  duration: string;
  duration_min: number;
  photo_urls: string[];
  is_published: boolean;
};

export type Booking = {
  ref: string;
  status: BookingStatus;
  service: string;
  when: string;
  start_time: string;
  customer_name: string;
  customer_phone: string;
  customer_email: string | null;
  notes: string;
  total: string;
  total_kobo: number;
  deposit: string;
  deposit_kobo: number;
  hold_expires_at: string | null;
  created_at: string;
  payment?: { reference: string; status: string; gateway: string; pay_url: string };
};

export type Customer = {
  id: number;
  name: string;
  phone: string;
  email: string | null;
  source: "chat" | "dashboard";
  bookings: number;
  confirmed_bookings: number;
  total_value: string;
  first_seen: string;
  last_seen: string;
  has_chat: boolean;
};

export type Enquiry = {
  id: number;
  question: string;
  answer: string;
  status: "open" | "answered";
  customer_name: string | null;
  customer_phone: string | null;
  customer_email: string | null;
  created_at: string;
};

export type ChatMessage = { id: number; from: "customer" | "assistant"; text: string; at: string };

export type CustomerDetail = Customer & { booking_history: Booking[]; questions: Enquiry[]; chat: ChatMessage[] };

export type Notification = {
  id: number;
  is_read: boolean;
  created_at: string;
  notification: { id: number; title: string; message: string; created_at: string };
};

export type Activity = {
  id: string;
  kind: "booking" | "question" | "chat";
  title: string;
  subtitle: string;
  amount: string | null;
  status: string;
  at: string;
};

export type Overview = {
  stats: {
    bookings_today: number;
    upcoming_bookings: number;
    awaiting_deposit: number;
    deposits_collected: string;
    booked_value: string;
    customers: number;
    chat_requests_7d: number;
    open_questions: number;
  };
  upcoming: Booking[];
  insights: {
    customer_tool_calls: number;
    tool_usage: Record<string, number>;
    most_asked_services: Record<string, number>;
    days_customers_asked_about: Record<string, number>;
    bookings_by_status: Record<string, number>;
    deposits_collected: string;
    open_questions: string[];
  };
  activity: Activity[];
};

export type McpToken = {
  id: number;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at: string | null;
  token?: string;
};

export type ImportResult = {
  created: string[];
  updated: string[];
  errors: { row: number; name: string | null; message: string }[];
};

export type ImportState = { error?: string; result?: ImportResult } | undefined;

export type ActionState =
  | { error?: string; fieldErrors?: Record<string, string>; ok?: boolean; message?: string; token?: string }
  | undefined;
