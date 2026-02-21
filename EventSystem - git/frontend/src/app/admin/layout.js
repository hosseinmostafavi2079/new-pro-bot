"use client";
import { useEffect, useContext, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AuthContext } from '../../context/AuthContext'; // مسیر کانتکست
import AdminSidebar from '../../components/AdminSidebar';
import { Toaster } from 'react-hot-toast';

export default function AdminLayout({ children }) {
  const { user, loading } = useContext(AuthContext);
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // صبر می‌کنیم تا لودینگ کانتکست تمام شود (یعنی وضعیت کاربر مشخص شود)
    if (!loading) {
      if (!user) {
        // اگر کاربر لاگین نبود -> برو به لاگین
        router.push('/login');
      } else {
        // اگر لاگین بود -> اجازه ورود بده
        // نکته: در آینده می‌توانیم اینجا چک کنیم که user.is_staff هست یا نه
        setIsAuthorized(true);
      }
    }
  }, [user, loading, router]);

  // تا زمانی که وضعیت مشخص نشده، چیزی نشان نده (یا لودینگ نشان بده)
  if (loading || !isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FD]" dir="rtl">
      <Toaster position="top-center" />
      
      {/* سایدبار */}
      <AdminSidebar />

      {/* محتوای اصلی */}
      <div className="md:mr-64 p-8 transition-all">
        {children}
      </div>
    </div>
  );
}