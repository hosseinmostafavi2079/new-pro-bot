"use client";
import { createContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { jwtDecode } from "jwt-decode"; // اصلاح شد

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // آیا هنوز داریم چک می‌کنیم؟
  const router = useRouter();

  useEffect(() => {
    // چک کردن اینکه آیا قبلاً لاگین کرده؟
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        // نکته: اگر توکن منقضی شده باشد باید اینجا هندل شود (فعلا ساده می‌گیریم)
        setUser({ username: decoded.user_id || 'کاربر', ...decoded }); 
      } catch (error) {
        console.error("Token invalid", error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  }, []);

  const login = (token, refresh) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refresh);
    const decoded = jwtDecode(token);
    setUser({ username: decoded.user_id || 'کاربر', ...decoded });
    router.push('/'); // هدایت به خانه
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    router.push('/login');
    window.location.reload(); // رفرش برای اطمینان از پاک شدن استیت‌ها
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};