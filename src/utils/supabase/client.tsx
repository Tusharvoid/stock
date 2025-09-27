// Simple client stub - not using external Supabase library to avoid import issues
// The server handles all Supabase operations via API endpoints

export const supabase = {
  // Placeholder for compatibility - actual auth happens via our API endpoints
  auth: {
    signInWithPassword: () => ({ data: null, error: null }),
    signOut: () => ({ error: null }),
    getSession: () => ({ data: { session: null }, error: null })
  }
};