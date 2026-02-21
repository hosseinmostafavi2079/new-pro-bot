"use client";
import { useState, useEffect, use } from 'react';
import axios from 'axios';
import { UserCircleIcon, TicketIcon, CurrencyDollarIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function UserDetail({ params }) {
  const { id } = use(params);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    axios.get(`http://127.0.0.1:8000/api/admin/users/${id}/`, {
        headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => { setData(res.data); setLoading(false); })
      .catch(err => console.error(err));
  }, [id]);

  if (loading) return <div className="p-10 text-center">در حال بارگذاری...</div>;
  if (!data) return <div className="p-10 text-center text-red-500">کاربر یافت نشد</div>;

  const { user_info, stats, tickets } = data;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/users" className="p-2 bg-white rounded-xl border hover:bg-gray-50"><ArrowRightIcon className="w-5 h-5"/></Link>
        <h1 className="text-2xl font-black text-gray-800">پروفایل: {user_info.username}</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* مشخصات */}
        <div className="bg-white p-6 rounded-3xl border border-gray-100 h-fit text-center">
            <UserCircleIcon className="w-20 h-20 text-blue-100 text-blue-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold">{user_info.first_name} {user_info.last_name}</h2>
            <p className="text-gray-500 text-sm mb-4">{user_info.email}</p>
            <div className="bg-gray-50 p-3 rounded-xl text-sm text-gray-600">
                عضویت: {new Date(user_info.date_joined).toLocaleDateString('fa-IR')}
            </div>
        </div>

        {/* آمار و خریدها */}
        <div className="md:col-span-2 space-y-6">
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-600 text-white p-6 rounded-3xl">
                    <div className="flex items-center gap-2 mb-2 opacity-80"><TicketIcon className="w-6 h-6"/><span>تعداد بلیت</span></div>
                    <span className="text-3xl font-black">{stats.total_tickets}</span>
                </div>
                <div className="bg-gray-900 text-white p-6 rounded-3xl">
                    <div className="flex items-center gap-2 mb-2 opacity-80"><CurrencyDollarIcon className="w-6 h-6"/><span>پرداختی کل</span></div>
                    <span className="text-3xl font-black">{stats.total_spent.toLocaleString()}</span> <span className="text-xs">تومان</span>
                </div>
            </div>

            <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden">
                <div className="p-4 border-b border-gray-50 font-bold">تاریخچه خریدها</div>
                <div className="divide-y divide-gray-50">
                    {tickets.map(t => (
                        <div key={t.id} className="p-4 flex items-center gap-4 hover:bg-gray-50">
                            <img src={t.event_image ? `http://127.0.0.1:8000${t.event_image}` : "https://placehold.co/100"} className="w-12 h-12 rounded-lg object-cover"/>
                            <div className="flex-1">
                                <div className="font-bold text-gray-800">{t.event_title}</div>
                                <div className="text-xs text-gray-500">{t.location}</div>
                            </div>
                            <div className="text-blue-600 font-bold">{t.price.toLocaleString()} تومان</div>
                        </div>
                    ))}
                    {tickets.length === 0 && <div className="p-8 text-center text-gray-400">هیچ خریدی ثبت نشده است.</div>}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}