import { createClient } from "@supabase/supabase-js";
import { runtimeConfig } from "./runtime-config";

export const supabase = createClient(runtimeConfig.supabaseUrl, runtimeConfig.supabaseAnonKey);
