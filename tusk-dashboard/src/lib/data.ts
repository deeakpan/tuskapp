import "server-only";
import { cache } from "react";
import { api } from "./api";
import type { CustomerDetail, Me } from "./types";

export const getMe = cache(() => api<Me>("/me"));

export const getCustomer = cache((id: number) => api<CustomerDetail>(`/customers/${id}`));
