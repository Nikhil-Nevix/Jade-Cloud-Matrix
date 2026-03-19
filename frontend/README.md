# JADE Cloud Matrix — Frontend

React + TypeScript frontend for the JADE Cloud Matrix cloud pricing intelligence platform.

## Architecture

### Tech Stack

- **React 18** — UI framework
- **TypeScript** — Type safety
- **Vite** — Build tool & dev server
- **React Router v6** — Client-side routing
- **TanStack Query v5** — Server state management
- **Tailwind CSS v3** — Utility-first CSS
- **shadcn/ui** — Component library
- **Recharts** — Data visualization
- **Axios** — HTTP client
- **date-fns** — Date formatting

### Directory Structure

```
src/
├── main.tsx                # Application entry point
├── App.tsx                 # Root component with routing
├── index.css               # Global styles & Tailwind directives
│
├── api/                    # API client modules (11 files)
│   ├── axios.ts            # Axios instance with JWT interceptor
│   ├── auth.ts
│   ├── providers.ts
│   ├── pricing.ts
│   ├── calculations.ts
│   ├── reserved.ts
│   ├── kubernetes.ts
│   ├── network.ts
│   ├── budgets.ts
│   ├── recommendations.ts
│   ├── admin.ts
│   └── export.ts
│
├── hooks/                  # Custom React hooks
│   ├── useAuth.tsx         # Authentication context provider
│   └── useToast.ts         # Toast notifications
│
├── components/
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   ├── label.tsx
│   │   └── tabs.tsx
│   ├── layout/
│   │   ├── Layout.tsx      # Main layout wrapper
│   │   ├── Sidebar.tsx     # Navigation sidebar
│   │   └── TopBar.tsx      # Top navigation bar
│   ├── calculator/         # Calculator form components
│   │   ├── ComputeForm.tsx
│   │   ├── StorageForm.tsx
│   │   ├── ReservedForm.tsx
│   │   ├── KubernetesForm.tsx
│   │   ├── NetworkForm.tsx
│   │   └── ResultsPanel.tsx
│   └── budgets/
│       ├── BudgetCard.tsx
│       └── BudgetAlertBadge.tsx
│
├── pages/                  # Page components
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── CalculatorPage.tsx
│   ├── HistoryPage.tsx
│   ├── BudgetsPage.tsx
│   ├── RecommendationsPage.tsx
│   ├── NotFoundPage.tsx
│   └── admin/
│       ├── AdminDashboardPage.tsx
│       ├── AdminUsersPage.tsx
│       └── AdminAuditLogsPage.tsx
│
├── types/
│   └── index.ts            # TypeScript interfaces
│
└── lib/
    ├── utils.ts            # Utility functions
    └── export.ts           # PDF/Excel download helpers
```

---

## Setup Instructions

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

---

## Configuration

### Vite Proxy

The Vite dev server is configured to proxy `/api` requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

This means:
- Frontend runs on port **5173**
- Backend runs on port **8000**
- All `/api/*` requests are automatically forwarded to backend

### Environment Variables

No `.env` file needed for frontend! The proxy handles backend communication.

---

## Key Features

### Authentication

- **JWT-based** authentication with automatic token management
- **localStorage** persistence (key: `jade_auth`)
- **Automatic logout** on token expiry or 401 responses
- **Protected routes** with role-based access control

### State Management

**TanStack Query** handles all server state:

```typescript
// Queries (fetching data)
const { data, isLoading, error } = useQuery({
  queryKey: ["providers"],
  queryFn: getProviders,
});

// Mutations (modifying data)
const mutation = useMutation({
  mutationFn: createBudget,
  onSuccess: () => {
    toast.success("Budget created!");
    queryClient.invalidateQueries(["budgets"]);
  },
});
```

### Routing

**React Router v6** with protected routes:

```typescript
<Route
  path="/admin"
  element={
    <ProtectedRoute adminOnly>
      <Layout>
        <AdminDashboardPage />
      </Layout>
    </ProtectedRoute>
  }
/>
```

### Data Visualization

**Recharts** for cost comparison charts:

```typescript
<BarChart data={chartData}>
  <Bar dataKey="monthly" fill="#3b82f6" />
</BarChart>
```

---

## Pages

### LoginPage

- Split-screen design (branded left panel + form right panel)
- Email/password authentication
- Auto-redirect to dashboard on success
- Shows default credentials for testing

### DashboardPage

- Overview stats (calculations, budgets, spending)
- Recent calculations table
- Budget status overview
- Quick action buttons

### CalculatorPage

4 tabs for different calculation types:

1. **Standard** — Compute + Storage pricing
2. **Reserved** — Reserved instance analysis
3. **Kubernetes** — Cluster cost modeling
4. **Network** — Data transfer pricing

Each tab has:
- Dynamic form with cascading dropdowns
- Multi-selection support
- Real-time pricing data from backend
- Results panel with charts and comparison

### HistoryPage

- Paginated calculation history
- Advanced filtering:
  - Calculation type
  - Provider
  - Date range
  - Cost range
- Export individual calculations as PDF/Excel
- Delete calculations

### BudgetsPage

- Budget cards grid showing current status
- Create/edit/delete budgets
- Active alerts section
- Visual progress bars
- Status badges (OK, Warning, Exceeded)

### RecommendationsPage

- Select up to 10 calculations for analysis
- Generate AI recommendations via Claude
- View recommendations by priority
- Estimated savings (monthly/annual)
- Actionable steps for each recommendation

### Admin Pages

**AdminDashboardPage:**
- Platform statistics
- Trigger manual pricing ingestion
- System information

**AdminUsersPage:**
- User management (CRUD)
- Role assignment
- Last login tracking

**AdminAuditLogsPage:**
- Complete audit trail
- Advanced filtering (action, user, date range)
- Pagination

---

## Components

### Layout Components

**Layout.tsx** — Main layout wrapper
- Conditionally renders sidebar + topbar for authenticated users
- Full-width for login page

**Sidebar.tsx** — Navigation sidebar
- Branded header
- Navigation links with icons
- Admin-only section (conditional)
- Active route highlighting

**TopBar.tsx** — Top navigation bar
- User email display
- Role badge (admin)
- Logout button

### Calculator Components

**ComputeForm.tsx** — Compute instance selection
- Multi-provider support
- Cascading dropdowns (provider → region → instance)
- Dynamic add/remove instances

**StorageForm.tsx** — Storage selection
- Block and object storage types
- Size configuration in GB

**ReservedForm.tsx** — Reserved instance selection
- Term selection (1yr, 3yr)
- Payment type (no_upfront, partial, all_upfront)
- Savings calculation vs on-demand

**KubernetesForm.tsx** — Kubernetes cluster config
- Node type and count
- Cluster management fee toggle
- EKS/AKS/GKE support

**NetworkForm.tsx** — Network transfer config
- Source region and destination type
- Transfer size in GB
- Free tier consideration

**ResultsPanel.tsx** — Calculation results display
- Bar charts for cost comparison
- Provider breakdown cards
- Cheapest provider recommendation
- Export buttons (PDF/Excel)

### Budget Components

**BudgetCard.tsx** — Individual budget display
- Progress bar visualization
- Status badge
- Edit/delete actions

**BudgetAlertBadge.tsx** — Alert status indicator
- Color-coded by status (active, acknowledged, resolved)

---

## TypeScript Types

All API response types are defined in `src/types/index.ts`:

```typescript
interface User {
  id: number;
  email: string;
  role: string;
  created_at: string;
  last_login?: string;
}

interface CalculationResult {
  id: number;
  user_id: number;
  calc_type: string;
  cheapest_provider?: string;
  aws_total_monthly?: number;
  azure_total_monthly?: number;
  gcp_total_monthly?: number;
  duration_months: number;
  created_at: string;
}

// ... and many more
```

---

## Styling

### Tailwind CSS

Utility-first CSS framework with custom configuration:

```javascript
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      // Custom color palette matching shadcn/ui
    },
  },
}
```

### shadcn/ui

Component library built on Radix UI primitives:

- Accessible by default
- Fully customizable
- Tailwind CSS styling
- Copy-paste friendly

---

## Error Handling

### API Errors

Axios interceptor automatically handles:

- **401 Unauthorized** → Logout + redirect to login
- **403 Forbidden** → Toast error message
- **500 Server Error** → Toast generic error

### User Feedback

- **react-hot-toast** for notifications
- Success messages on mutations
- Error messages with details
- Loading states on buttons/forms

---

## Development Tips

### Type Safety

TypeScript is configured with strict mode. All API responses are typed:

```typescript
const { data } = useQuery<Provider[]>({
  queryKey: ["providers"],
  queryFn: getProviders,
});
```

### Query Invalidation

After mutations, invalidate related queries:

```typescript
const mutation = useMutation({
  mutationFn: createBudget,
  onSuccess: () => {
    queryClient.invalidateQueries(["budgets"]);
  },
});
```

### Code Splitting

React Router v6 supports lazy loading:

```typescript
const AdminPage = React.lazy(() => import("./pages/admin/AdminDashboardPage"));
```

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

---

## Troubleshooting

### "Cannot find module '@/...'"

The `@` alias points to `src/`. Ensure `tsconfig.json` has:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### API requests fail

- Ensure backend is running on port 8000
- Check Vite proxy configuration
- Verify CORS settings in backend

### Types mismatch

- Check `src/types/index.ts` matches backend schemas
- Run `npm run type-check` to find type errors

---

## License

Proprietary — Jade Global Software Pvt Ltd. All rights reserved.
