import { projectId, publicAnonKey } from './supabase/info';

const API_BASE_URL = `https://${projectId}.supabase.co/functions/v1/make-server-c004c1e8`;

export interface User {
  id: string;
  email: string;
  name: string;
  created_at?: string;
  portfolio_initialized?: boolean;
}

export interface AuthResponse {
  user?: User;
  session?: any;
  error?: string;
}

// In-memory session storage for demo purposes
let currentSession: { user: User; token: string } | null = null;

// Sign up new user
export async function signUp(email: string, password: string, name: string): Promise<AuthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${publicAnonKey}`
      },
      body: JSON.stringify({ email, password, name })
    });

    const data = await response.json();

    if (!response.ok) {
      return { error: data.error || 'Sign up failed' };
    }

    // Create a demo session
    const user: User = {
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      created_at: new Date().toISOString(),
      portfolio_initialized: false
    };

    const session = {
      access_token: `demo_token_${Date.now()}`,
      user
    };

    currentSession = { user, token: session.access_token };

    return { user, session };

  } catch (error) {
    console.error('Sign up error:', error);
    return { error: 'Network error during sign up' };
  }
}

// Sign in existing user (simplified for demo)
export async function signIn(email: string, password: string): Promise<AuthResponse> {
  try {
    // For demo purposes, create a session for any valid email/password
    if (!email || !password) {
      return { error: 'Email and password are required' };
    }

    if (password.length < 6) {
      return { error: 'Invalid credentials' };
    }

    const user: User = {
      id: `user_${Date.now()}`,
      email,
      name: email.split('@')[0], // Use email prefix as name
      created_at: new Date().toISOString(),
      portfolio_initialized: true
    };

    const session = {
      access_token: `demo_token_${Date.now()}`,
      user
    };

    currentSession = { user, token: session.access_token };

    return { user, session };

  } catch (error) {
    console.error('Sign in error:', error);
    return { error: 'Network error during sign in' };
  }
}

// Sign out user
export async function signOut(): Promise<{ error?: string }> {
  try {
    currentSession = null;
    return {};
  } catch (error) {
    console.error('Sign out error:', error);
    return { error: 'Network error during sign out' };
  }
}

// Get current user session
export async function getCurrentUser(): Promise<AuthResponse> {
  try {
    if (!currentSession) {
      return { error: 'No active session' };
    }

    return {
      user: currentSession.user,
      session: { access_token: currentSession.token, user: currentSession.user }
    };

  } catch (error) {
    console.error('Get current user error:', error);
    return { error: 'Network error checking session' };
  }
}

// Update user profile
export async function updateProfile(updates: Partial<User>): Promise<{ error?: string }> {
  try {
    if (!currentSession) {
      return { error: 'No active session' };
    }

    // Update the current session user data
    currentSession.user = { ...currentSession.user, ...updates };

    return {};

  } catch (error) {
    console.error('Update profile error:', error);
    return { error: 'Network error updating profile' };
  }
}