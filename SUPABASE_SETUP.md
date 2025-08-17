# 🚀 Supabase Setup Guide

This guide will help you set up Supabase for the Text-to-SQL Assistant project.

## 📋 Step-by-Step Setup

### 1. Create Supabase Account
1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" 
3. Sign up with GitHub, Google, or email

### 2. Create a New Project
1. Click "New Project"
2. Choose your organization
3. Fill in project details:
   - **Name**: `text-to-sql-assistant`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
4. Click "Create new project"
5. Wait ~2 minutes for setup to complete

### 3. Get Connection Details
Once your project is ready:

1. Go to **Settings** → **Database**
2. Scroll to **Connection string**
3. Copy the **URI** (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

### 4. Get API Keys (Optional)
For future features, get your API keys:

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL**: `https://[YOUR-PROJECT-REF].supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role secret key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 5. Update .env File
Replace the placeholders in your `.env` file:

```env
# Database settings - Supabase PostgreSQL
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Supabase specific (optional, for future features)
SUPABASE_URL="https://[YOUR-PROJECT-REF].supabase.co"
SUPABASE_ANON_KEY="[YOUR-ANON-KEY]"
SUPABASE_SERVICE_ROLE_KEY="[YOUR-SERVICE-ROLE-KEY]"
```

**Example:**
```env
DATABASE_URL="postgresql://postgres:mypassword123@db.abcdefghijklmnop.supabase.co:5432/postgres"
SUPABASE_URL="https://abcdefghijklmnop.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔧 Install Dependencies

Run this command to install PostgreSQL drivers:

```bash
# In your virtual environment
pip install psycopg2-binary asyncpg
```

## ✅ Test Connection

After setup, we'll test the connection in Phase 2 of the implementation.

## 🎯 Why Supabase for Text-to-SQL?

1. **PostgreSQL**: Best SQL standard compliance for learning
2. **Cloud-hosted**: No local database setup needed
3. **Free tier**: 500MB database, perfect for development
4. **Real-time**: Could add live query monitoring later
5. **Dashboard**: Easy to view your data and schemas
6. **Backups**: Automatic backups included

## 🔒 Security Notes

- Keep your database password secure
- Never commit your `.env` file to version control
- Use the `anon` key for client-side operations only
- Use `service_role` key for server-side operations only

## 📱 Supabase Dashboard Features

Once connected, you can use the Supabase dashboard to:
- View and edit data in tables
- Run SQL queries directly
- Monitor database performance
- Set up row-level security
- View real-time subscriptions

Ready for Phase 2? We'll create the database schema and test the connection!
