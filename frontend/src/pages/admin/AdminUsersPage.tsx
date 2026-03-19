import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getAdminUsers, createAdminUser, updateAdminUser, deleteAdminUser } from "@/api/admin";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Plus, Edit, Trash2, X } from "lucide-react";
import { format } from "date-fns";
import toast from "react-hot-toast";
import type { User } from "@/types";

export default function AdminUsersPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const { data: users, refetch } = useQuery({
    queryKey: ["admin-users"],
    queryFn: getAdminUsers,
  });

  const createMutation = useMutation({
    mutationFn: createAdminUser,
    onSuccess: () => {
      toast.success("User created!");
      setShowCreateForm(false);
      refetch();
    },
    onError: () => toast.error("Failed to create user"),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAdminUser,
    onSuccess: () => {
      toast.success("User deleted!");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || "Failed to delete user");
    },
  });

  const handleDelete = (user: User) => {
    if (!confirm(`Delete user ${user.email}?`)) return;
    deleteMutation.mutate(user.id);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-1">Manage platform users and access</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create User
        </Button>
      </div>

      {showCreateForm && (
        <UserFormModal
          onClose={() => setShowCreateForm(false)}
          onSave={(data) => createMutation.mutate(data)}
        />
      )}

      {editingUser && (
        <UserFormModal
          user={editingUser}
          onClose={() => setEditingUser(null)}
          onSave={(data) => {
            // TODO: implement update
            toast.info("Edit functionality pending");
            setEditingUser(null);
          }}
        />
      )}

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Last Login</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users?.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Badge variant={user.role === "admin" ? "default" : "secondary"}>
                      {user.role}
                    </Badge>
                  </TableCell>
                  <TableCell>{format(new Date(user.created_at), "MMM dd, yyyy")}</TableCell>
                  <TableCell>
                    {user.last_login ? format(new Date(user.last_login), "MMM dd, yyyy") : "Never"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => setEditingUser(user)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(user)}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

interface UserFormModalProps {
  user?: User;
  onClose: () => void;
  onSave: (data: any) => void;
}

function UserFormModal({ user, onClose, onSave }: UserFormModalProps) {
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(user?.role || "user");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: any = { email, role };
    if (password || !user) {
      data.password = password;
    }
    onSave(data);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-lg m-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{user ? "Edit User" : "Create User"}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Email</Label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label>Password {user && "(leave blank to keep current)"}</Label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required={!user}
                className="mt-1"
              />
            </div>

            <div>
              <Label>Role</Label>
              <Select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="mt-1"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </Select>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {user ? "Update User" : "Create User"}
              </Button>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
