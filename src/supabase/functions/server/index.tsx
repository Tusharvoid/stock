import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import { createClient } from "npm:@supabase/supabase-js";
import * as kv from "./kv_store.tsx";

const app = new Hono();

// Supabase client with service role for admin operations
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
);

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-c004c1e8/health", (c) => {
  return c.json({ status: "ok" });
});

// Sign up endpoint
app.post("/make-server-c004c1e8/auth/signup", async (c) => {
  try {
    const body = await c.req.json();
    const { email, password, name } = body;

    if (!email || !password || !name) {
      return c.json({ 
        error: "Missing required fields: email, password, and name are required" 
      }, 400);
    }

    // Create user with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      user_metadata: { name },
      // Automatically confirm the user's email since an email server hasn't been configured.
      email_confirm: true
    });

    if (authError) {
      console.log(`Authentication error during sign up: ${authError.message}`);
      return c.json({ 
        error: `Sign up failed: ${authError.message}` 
      }, 400);
    }

    // Store additional user data in KV store
    const userData = {
      id: authData.user.id,
      email: authData.user.email,
      name,
      created_at: new Date().toISOString(),
      portfolio_initialized: false
    };

    await kv.set(`user:${authData.user.id}`, userData);

    return c.json({ 
      message: "User created successfully",
      user: {
        id: authData.user.id,
        email: authData.user.email,
        name
      }
    });

  } catch (error) {
    console.log(`Server error during sign up: ${error}`);
    return c.json({ 
      error: "Internal server error during sign up" 
    }, 500);
  }
});

// Get user profile endpoint
app.get("/make-server-c004c1e8/auth/profile", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: "Authorization token required" }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      console.log(`Authorization error while getting user profile: ${error?.message}`);
      return c.json({ error: "Unauthorized" }, 401);
    }

    // Get additional user data from KV store
    const userData = await kv.get(`user:${user.id}`);
    
    return c.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.user_metadata?.name || userData?.name || 'User',
        created_at: userData?.created_at || user.created_at,
        portfolio_initialized: userData?.portfolio_initialized || false
      }
    });

  } catch (error) {
    console.log(`Server error while getting user profile: ${error}`);
    return c.json({ 
      error: "Internal server error while getting profile" 
    }, 500);
  }
});

// Update user profile endpoint
app.put("/make-server-c004c1e8/auth/profile", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: "Authorization token required" }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      console.log(`Authorization error while updating user profile: ${error?.message}`);
      return c.json({ error: "Unauthorized" }, 401);
    }

    const body = await c.req.json();
    const { name, portfolio_initialized } = body;

    // Get existing user data
    const existingData = await kv.get(`user:${user.id}`) || {};
    
    // Update user data in KV store
    const updatedData = {
      ...existingData,
      id: user.id,
      email: user.email,
      ...(name && { name }),
      ...(portfolio_initialized !== undefined && { portfolio_initialized }),
      updated_at: new Date().toISOString()
    };

    await kv.set(`user:${user.id}`, updatedData);

    return c.json({ 
      message: "Profile updated successfully",
      user: updatedData
    });

  } catch (error) {
    console.log(`Server error while updating user profile: ${error}`);
    return c.json({ 
      error: "Internal server error while updating profile" 
    }, 500);
  }
});

Deno.serve(app.fetch);