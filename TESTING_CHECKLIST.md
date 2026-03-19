# JADE Cloud Matrix — Testing & Deployment Checklist

## ✅ Pre-Testing Checklist

### Prerequisites Installation
- [ ] PostgreSQL 15 installed and running
- [ ] Python 3.9+ available
- [ ] Node.js 18+ and npm installed
- [ ] Git initialized (already done)

---

## 🧪 Testing Steps

### 1. Database Setup

#### Step 1a: Check if PostgreSQL is Already Running

```bash
# Check if PostgreSQL is running
ps aux | grep postgres | grep -v grep

# If you see postgres processes, it's already running!
# Note the port number (usually 5432 or 5433)
```

#### Step 1b: If PostgreSQL is NOT Running

```bash
# Start PostgreSQL service (requires root/sudo)
su -
systemctl start postgresql
systemctl enable postgresql  # optional: auto-start on boot
exit
```

#### Step 1c: Run Database Setup Script

**Important**: The user is `postgres` (not `postgresql`)

```bash
cd /home/NikhilRokade/JadeCloudMatrix

# If PostgreSQL is on default port 5432:
sudo -u postgres psql -f db_setup.sql

# If PostgreSQL is on port 5433 (or another port):
psql -h localhost -p 5433 -U $USER -d postgres -f db_setup.sql

# Or if the above doesn't work:
psql -h localhost -p 5433 -U NikhilRokade -d postgres -f db_setup.sql
```

**Expected Output:**
```
CREATE ROLE
CREATE DATABASE
GRANT
You are now connected to database "jade_db" as user "..."
GRANT
ALTER DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES
```

#### Step 1d: Verify Database Creation

```bash
# For default port 5432:
sudo -u postgres psql -c "\l" | grep jade_db

# For port 5433:
psql -h localhost -p 5433 -U $USER -d postgres -c "\l" | grep jade_db

# Should show: jade_db | jade_user | UTF8
```

**✅ Checkpoint**: Database `jade_db` exists and user `jade_user` can connect

---

### 2. Backend Setup & Testing

#### Step 2a: Create Virtual Environment

```bash
cd /home/NikhilRokade/JadeCloudMatrix/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

#### Step 2b: Configure Environment Variables

The `.env` file needs to be configured with the correct database port.

```bash
# Copy template
cp ../.env.example .env

# Generate JWT secret key
openssl rand -hex 32

# Edit .env file
nano .env
```

**Required changes in `.env`:**

1. **DATABASE_URL** - Update with your PostgreSQL port:
   ```env
   # If port is 5432 (default):
   DATABASE_URL=postgresql+asyncpg://jade_user:jade_pass@localhost:5432/jade_db
   
   # If port is 5433:
   DATABASE_URL=postgresql+asyncpg://jade_user:jade_pass@localhost:5433/jade_db
   ```

2. **JWT_SECRET_KEY** - Paste the generated key:
   ```env
   JWT_SECRET_KEY=paste-your-generated-key-here
   ```

3. **ANTHROPIC_API_KEY** (optional for now):
   ```env
   # You can keep the placeholder or add your real key
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

Save and exit (Ctrl+O, Enter, Ctrl+X in nano)

#### Step 2c: Install Dependencies & Setup Database

**Option A: Use the setup script (easiest)**

```bash
# Make sure you're in backend/ with venv activated
./setup_and_run.sh
```

This automatically:
- Installs all Python dependencies
- Runs database migrations
- Seeds initial data

**Option B: Manual setup**

```bash
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head
# Should output: INFO  [alembic.runtime.migration] Running upgrade  -> 0001, initial_schema

# Seed initial data
python scripts/seed.py
# Should output:
#   - Created providers: AWS, Azure, GCP
#   - Created regions: 15+ regions
#   - Created users: admin, user
#   - Ingestion complete
```

#### Step 2d: Start Backend Server

```bash
cd /home/NikhilRokade/JadeCloudMatrix/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test backend endpoints:**

Open a new terminal:

```bash
# 1. Health check
curl http://localhost:8000/api/healthz
# Expected: {"status":"ok","version":"1.0.0"}

# 2. Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@jadeglobal.com","password":"admin123"}'
# Expected: JSON with token, userId, email, role

# Save the token from response, then:
export TOKEN="your-token-here"

# 3. Get providers
curl http://localhost:8000/api/v1/providers \
  -H "Authorization: Bearer $TOKEN"
# Expected: Array with AWS, Azure, GCP

# 4. Get compute pricing
curl "http://localhost:8000/api/v1/pricing/compute?provider_id=1" \
  -H "Authorization: Bearer $TOKEN"
# Expected: Array of compute pricing objects

# 5. View API docs
# Open browser: http://localhost:8000/docs
# You should see interactive Swagger UI
```

**✅ Checkpoint**: Backend responds to all test endpoints, login works, API docs accessible

---

### 3. Frontend Setup & Testing

Keep backend running, open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install
# This will install 100+ packages (React, Vite, TanStack Query, etc.)
# Takes 1-3 minutes

# Start development server
npm run dev
# Should output:
#   VITE ready in xxx ms
#   Local:   http://localhost:5173/
#   Network: use --host to expose
```

**Test frontend in browser:**

1. **Open http://localhost:5173**
   - Should redirect to `/login`
   - Left panel: JADE Cloud Matrix branding
   - Right panel: Login form

2. **Login with admin credentials**
   - Email: `admin@jadeglobal.com`
   - Password: `admin123`
   - Click "Sign In"
   - Should redirect to Dashboard

3. **Test Dashboard**
   - Should show stats cards (My Calculations, etc.)
   - Recent Calculations table (empty initially)
   - Quick action buttons

4. **Test Navigation**
   - Sidebar should show: Dashboard, Calculator, History, Budgets, AI Insights
   - Admin section should show: Admin, Users, Audit Logs
   - Click each link to verify pages load

5. **Test Calculator**
   - Navigate to Calculator
   - Should see 4 tabs: Standard, Reserved, Kubernetes, Network
   - Standard tab should show Compute and Storage forms
   - Try selecting: AWS → us-east-1 → any instance type
   - Forms should populate with real data from backend

6. **Test Budget Creation**
   - Navigate to Budgets
   - Click "Create Budget"
   - Fill form: Name, Budget Amount, Period, Threshold
   - Click "Create Budget"
   - Should see success toast and new budget card

7. **Test Admin Features** (as admin)
   - Navigate to Admin → Users
   - Should see user list table
   - Navigate to Admin → Audit Logs
   - Should see login events and other actions

8. **Test Logout**
   - Click Logout button in top right
   - Should redirect to login page

**✅ Checkpoint**: Frontend loads, login works, all pages accessible, can interact with backend

---

### 4. End-to-End Calculation Test

1. Login as admin or user
2. Navigate to **Calculator**
3. Select **Standard** tab
4. Add compute instance:
   - Provider: AWS
   - Region: US East (N. Virginia)
   - Instance: t2.micro
   - Quantity: 1
5. Add storage:
   - Provider: AWS
   - Region: US East (N. Virginia)
   - Storage: S3 Standard
   - Size: 100 GB
6. Set duration: 12 months
7. Click **Calculate Pricing**
8. Verify results appear with:
   - Bar chart showing AWS costs
   - Provider breakdown card
   - Monthly/annual costs
9. Click **Export PDF**
   - Should download PDF file
10. Click **Export Excel**
    - Should download Excel file
11. Navigate to **History**
    - New calculation should appear in table
12. Try exporting the calculation again from History page

**✅ Checkpoint**: Full calculation flow works end-to-end, exports work, history saved

---

### 5. AI Recommendations Test (Optional)

⚠️ **Requires valid ANTHROPIC_API_KEY in .env**

1. Login and create 2-3 calculations
2. Navigate to **AI Insights**
3. Select the calculations from left panel
4. Click **Generate Recommendations**
5. Wait for Claude API response
6. Verify recommendations appear with:
   - Summary and total savings estimate
   - Individual recommendation cards
   - Priority badges (high/medium/low)
   - Action steps
   - Affected providers

**✅ Checkpoint**: AI recommendations work (if API key configured)

---

## 🐛 Known Issues & Solutions

### Issue: "unknown user: postgresql" error

**Solution**: The correct user is `postgres` (not `postgresql`)
```bash
# Correct command:
sudo -u postgres psql -f db_setup.sql

# NOT: sudo -u postgresql psql -f db_setup.sql
```

### Issue: PostgreSQL "Access denied" when starting service

**Possible causes:**
1. PostgreSQL is already running (check with `ps aux | grep postgres`)
2. You need to use `su` to become root first:
   ```bash
   su -
   systemctl start postgresql
   exit
   ```

### Issue: Backend import errors

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Frontend build fails

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Database connection refused

**Solution**:
```bash
# Check if PostgreSQL is running
ps aux | grep postgres | grep -v grep

# Check what port it's running on
netstat -an | grep LISTEN | grep 543

# Common ports: 5432 (default) or 5433

# Update DATABASE_URL in backend/.env with correct port
nano backend/.env
# Change: postgresql+asyncpg://jade_user:jade_pass@localhost:5433/jade_db

# Verify database exists on that port
psql -h localhost -p 5433 -U $USER -d postgres -c "\l" | grep jade_db
```

### Issue: 401 Unauthorized on all API calls

**Solution**:
- Check JWT_SECRET_KEY is set in backend/.env
- Try logging out and logging in again
- Check browser console for error messages

### Issue: CORS errors in browser

**Solution**:
- Verify CORS_ORIGINS in backend/.env includes http://localhost:5173
- Restart backend server after changing .env
- Check browser DevTools Network tab for OPTIONS preflight requests

---

## 📊 Expected Results

### After Seed Script

**Database should contain:**
- 3 providers: AWS, Azure, GCP
- 15+ regions across providers
- 100+ compute pricing records
- 50+ storage pricing records
- 50+ reserved pricing records
- 50+ Kubernetes pricing records
- 50+ network pricing records
- 2 users: admin and regular user

### After First Login

**Should see:**
- Dashboard with 0 calculations
- Empty budget list
- No audit logs (except seed operations)
- Working navigation
- Admin menu (if logged in as admin)

### After First Calculation

**Should see:**
- New entry in History page
- Updated dashboard stats
- PDF and Excel exports working
- Calculation can be deleted

---

## 🚀 Deployment Preparation (Future)

### Security Checklist
- [ ] Change default user passwords
- [ ] Generate strong JWT_SECRET_KEY
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable PostgreSQL SSL connections
- [ ] Set APP_ENV=production
- [ ] Review and restrict CORS_ORIGINS

### Infrastructure Checklist
- [ ] Set up production PostgreSQL instance
- [ ] Configure database backups
- [ ] Set up Nginx reverse proxy
- [ ] Create systemd services
- [ ] Configure log rotation
- [ ] Set up monitoring (uptime, errors)
- [ ] Configure CDN for frontend assets

### Performance Checklist
- [ ] Enable database query caching
- [ ] Configure Redis for session storage
- [ ] Set up database connection pooling limits
- [ ] Enable gzip compression
- [ ] Optimize frontend bundle size
- [ ] Configure CDN caching headers

---

## 📝 Testing Checklist Summary

### Critical Path Testing

- [ ] Backend health check responds
- [ ] Database migrations run successfully
- [ ] Seed script populates data
- [ ] Login works (admin + user)
- [ ] JWT authentication working
- [ ] Frontend loads and renders
- [ ] Navigation works (all pages load)
- [ ] Standard calculation works end-to-end
- [ ] Calculation saves to history
- [ ] PDF export works
- [ ] Excel export works
- [ ] Budget creation works
- [ ] Admin pages accessible (admin only)
- [ ] Logout works

### Optional Testing

- [ ] Reserved instance calculation
- [ ] Kubernetes calculation
- [ ] Network calculation
- [ ] AI recommendations (requires API key)
- [ ] Budget alerts trigger correctly
- [ ] Admin user management CRUD
- [ ] Admin audit logs filtering
- [ ] Manual pricing ingestion

### Edge Case Testing

- [ ] Login with invalid credentials (should fail gracefully)
- [ ] Access admin pages as regular user (should redirect)
- [ ] Try to delete calculation from another user (should fail)
- [ ] Token expiry handling (logout after 24h)
- [ ] Large data sets (100+ calculations)
- [ ] API rate limiting behavior

---

## 🎯 Success Criteria

The implementation is considered successful when:

1. ✅ Backend starts without errors
2. ✅ Frontend starts without errors
3. ✅ Login flow works
4. ✅ At least one calculation type works end-to-end
5. ✅ Calculation saves to database and appears in history
6. ✅ PDF/Excel export works
7. ✅ Budget tracking works
8. ✅ Admin features work (if logged in as admin)
9. ✅ All pages render without errors
10. ✅ Navigation works throughout the app

---

## 📞 Support

If you encounter issues during testing:

1. Check the error message carefully
2. Review the README files for troubleshooting
3. Check browser DevTools console (F12)
4. Check backend terminal for error logs
5. Verify all prerequisites are installed

---

**Implementation Status: 100% Complete**  
**Ready for Testing: YES**  
**Next Phase: Testing → Deployment**

---

## 🎯 Quick Reference

### Default Credentials
```
Admin: admin@jadeglobal.com / admin123
User:  user@jadeglobal.com / user123
```

### Database Connection
```
Host:     localhost
Port:     5433 (or 5432 - check with: ps aux | grep postgres)
Database: jade_db
User:     jade_user
Password: jade_pass
```

### Service URLs
```
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
Frontend: http://localhost:5173
```

### Common Commands

**Check PostgreSQL Status:**
```bash
ps aux | grep postgres | grep -v grep
netstat -an | grep LISTEN | grep 543
```

**Check PostgreSQL Port:**
```bash
ps aux | grep postgres | head -1
# Look for -p flag (e.g., -p 5433)
```

**Backend:**
```bash
cd /home/NikhilRokade/JadeCloudMatrix/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd /home/NikhilRokade/JadeCloudMatrix/frontend
npm run dev
```

**Test Backend Health:**
```bash
curl http://localhost:8000/api/healthz
```

---

## 📋 Troubleshooting Checklist

Before asking for help, verify:

- [ ] PostgreSQL is running (`ps aux | grep postgres`)
- [ ] Database `jade_db` exists (run `\l` in psql)
- [ ] Backend `.env` has correct DATABASE_URL with right port
- [ ] Backend `.env` has JWT_SECRET_KEY set (not default placeholder)
- [ ] Virtual environment is activated (`source venv/bin/activate`)
- [ ] Dependencies are installed (`pip list | grep fastapi`)
- [ ] Migrations ran successfully (`alembic current`)
- [ ] Seed script completed without errors
- [ ] Backend is running on port 8000 (check with `netstat -an | grep 8000`)
- [ ] Frontend dependencies installed (`ls frontend/node_modules`)
- [ ] Frontend is running on port 5173 (check terminal output)
- [ ] Browser can access http://localhost:5173

---

**Last Updated**: 2026-03-19  
**Status**: ✅ Verified working with PostgreSQL on port 5433
