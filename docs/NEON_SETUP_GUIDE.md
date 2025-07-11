# Neon Database Setup Guide for DealVerse OS

## 🎯 **Overview**
This guide will help you set up a PostgreSQL database on Neon for DealVerse OS.

## 📋 **Prerequisites**
- A Neon account (free tier available)
- Internet connection
- DealVerse OS backend code

## 🔧 **Step-by-Step Setup**

### **1. Create Neon Account**
1. Go to [neon.com](https://neon.com)
2. Click "Sign Up" and create your account
3. Verify your email address

### **2. Create a New Project**
1. After logging in, click "Create Project"
2. Choose your settings:
   - **Project Name**: `dealverse-os`
   - **Database Name**: `dealverse_db`
   - **Region**: Choose closest to your location
   - **PostgreSQL Version**: 15 (recommended)
3. Click "Create Project"

### **3. Get Connection String**
1. In your project dashboard, click "Connection Details"
2. Copy the connection string that looks like:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/dealverse_db?sslmode=require
   ```
3. Save this connection string - you'll need it for configuration

### **4. Configure Backend Environment**
1. Navigate to the `backend` directory
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file and update the database URL:
   ```bash
   # Replace with your actual Neon connection string
   NEON_DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/dealverse_db?sslmode=require
   DATABASE_URL=${NEON_DATABASE_URL}
   ```

### **5. Test Connection**
Run the Neon setup script to test your connection:
```bash
cd backend
python neon_setup.py
```

If successful, you should see:
```
✅ Connected to Neon PostgreSQL: PostgreSQL 15.x...
✅ Database schema initialized successfully!
```

### **6. Initialize Database**
The setup script will automatically:
- Create all required tables
- Set up relationships and indexes
- Insert sample data including demo users
- Configure initial organization

## 🔐 **Security Notes**
- Neon automatically uses SSL/TLS encryption
- Connection strings include authentication
- Database is isolated per project
- Automatic backups are included

## 📊 **Database Schema**
The following tables will be created:
- `organizations` - Multi-tenant organization data
- `users` - User accounts and authentication
- `deals` - Investment banking deals
- `clients` - Client relationship management
- `tasks` - Project and task management
- `documents` - File and document management
- `financial_models` - Valuation and modeling data

## 🎭 **Demo Data**
After initialization, you'll have:
- **Demo Organization**: "DealVerse Demo Organization"
- **Demo Users**:
  - Admin: admin@dealverse.com / changethis
  - Manager: manager@dealverse.com / manager123
  - Analyst: analyst@dealverse.com / analyst123
  - Associate: associate@dealverse.com / associate123
  - VP: vp@dealverse.com / vp123

## 🔧 **Troubleshooting**

### **Connection Issues**
- Verify your connection string is correct
- Check that your IP is not blocked (Neon allows all IPs by default)
- Ensure SSL mode is set to 'require'

### **Permission Issues**
- Make sure you're using the correct username/password
- Verify the database name matches your Neon project

### **Timeout Issues**
- Check your internet connection
- Try a different region if available

## 📈 **Neon Features Used**
- **Serverless**: Automatic scaling and hibernation
- **Branching**: Database branching for development
- **Point-in-time Recovery**: Automatic backups
- **Connection Pooling**: Built-in connection management

## 🎯 **Next Steps**
After successful setup:
1. ✅ Database is ready
2. ➡️ Start the backend server
3. ➡️ Launch the frontend
4. ➡️ Test authentication
5. ➡️ Explore the application

## 💡 **Tips**
- Keep your connection string secure
- Use environment variables for production
- Monitor your usage in the Neon dashboard
- Consider upgrading for production workloads
