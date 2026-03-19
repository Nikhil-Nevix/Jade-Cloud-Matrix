import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import {
  LayoutDashboard,
  Calculator,
  History,
  Wallet,
  Lightbulb,
  Shield,
  Users,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  const location = useLocation();
  const { isAdmin } = useAuth();

  const navItems = [
    { path: "/", label: "Dashboard", icon: LayoutDashboard },
    { path: "/calculator", label: "Calculator", icon: Calculator },
    { path: "/history", label: "History", icon: History },
    { path: "/budgets", label: "Budgets", icon: Wallet },
    { path: "/recommendations", label: "AI Insights", icon: Lightbulb },
  ];

  const adminItems = isAdmin
    ? [
        { path: "/admin", label: "Admin", icon: Shield },
        { path: "/admin/users", label: "Users", icon: Users },
        { path: "/admin/audit-logs", label: "Audit Logs", icon: FileText },
      ]
    : [];

  const allItems = [...navItems, ...adminItems];

  return (
    <aside className="w-64 bg-gradient-to-b from-blue-900 to-blue-950 text-white flex flex-col">
      <div className="p-6 border-b border-blue-800">
        <h1 className="text-2xl font-bold">JADE Cloud Matrix</h1>
        <p className="text-xs text-blue-300 mt-1">Pricing Intelligence</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {allItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                  ? "bg-blue-800 text-white"
                  : "text-blue-200 hover:bg-blue-800/50 hover:text-white"
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-blue-800 text-xs text-blue-300">
        <p>Jade Global Software Pvt Ltd</p>
        <p>Infrastructure BU</p>
      </div>
    </aside>
  );
}
