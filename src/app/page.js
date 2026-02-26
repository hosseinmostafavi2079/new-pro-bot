"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';
import EventCard from '../components/EventCard';
import Header from '../components/Header';
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // وضعیت‌های فیلتر
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  // دریافت لیست دسته‌بندی‌ها برای دراپ‌دان
  useEffect(() => {
    axios.get(`${API_URL}/api/categories/`)
      .then(res => setCategories(res.data))
      .catch(err => console.error("خطا در دریافت دسته‌بندی‌ها:", err));
  }, []);

  // تابع اصلی دریافت رویدادها
  const fetchEvents = () => {
    setLoading(true);
    let params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    if (selectedCategory) params.append('category', selectedCategory);

    axios.get(`${API_URL}/api/events/?${params.toString()}`)
      .then(res => {
        setEvents(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("خطا در دریافت رویدادها:", err);
        setLoading(false);
      });
  };

  // اجرای جستجو با تغییر دسته‌بندی
  useEffect(() => {
    fetchEvents();
  }, [selectedCategory]);

  return (
    <div className="min-h-screen bg-[#F3F4F6]" dir="rtl">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-16 mt-6">
          <h2 className="text-4xl md:text-6xl font-black text-gray-900 mb-6 leading-tight">
            رویداد مورد علاقه‌ت رو <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              همین الان پیدا کن!
            </span>
          </h2>

          {/* باکس جستجو و فیلتر */}
          <div className="bg-white p-2 rounded-2xl shadow-xl border border-gray-100 flex flex-col md:flex-row gap-2 max-w-4xl mx-auto relative z-10">
            {/* اینپوت متن */}
            <div className="flex-[2] flex items-center px-4 h-14 bg-gray-50 rounded-xl focus-within:bg-white focus-within:ring-2 ring-blue-100 transition">
              <MagnifyingGlassIcon className="w-6 h-6 text-gray-400 ml-2" />
              <input 
                type="text" 
                placeholder="جستجو در عنوان یا توضیحات..." 
                className="bg-transparent w-full h-full outline-none text-gray-800 font-bold"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && fetchEvents()}
              />
            </div>

            <div className="w-px bg-gray-200 hidden md:block my-2"></div>

            {/* انتخاب دسته‌بندی */}
            <div className="flex-1 relative">
              <select 
                className="w-full h-14 bg-gray-50 rounded-xl px-4 outline-none text-gray-500 font-bold appearance-none cursor-pointer hover:bg-gray-100 transition"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">همه دسته‌بندی‌ها</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.title}</option>
                ))}
              </select>
              <ChevronDownIcon className="w-4 h-4 text-gray-400 absolute left-4 top-5 pointer-events-none" />
            </div>

            <button 
              onClick={fetchEvents}
              className="h-14 px-8 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg transition flex items-center gap-2 justify-center"
            >
              <MagnifyingGlassIcon className="w-5 h-5" />
              <span>بگرد</span>
            </button>
          </div>
        </div>

        {/* بخش نمایش نتایج */}
        <div className="flex justify-between items-end mb-8">
          <h3 className="text-2xl font-black text-gray-900 flex items-center gap-3">
            <span className="w-1.5 h-8 bg-blue-600 rounded-full"></span>
            {searchTerm || selectedCategory ? 'نتایج جستجو' : 'تازه‌ترین رویدادها'}
          </h3>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {events.length > 0 ? (
              events.map(event => (
                <EventCard key={event.id} event={event} />
              ))
            ) : (
              <div className="col-span-full text-center py-20 text-gray-500 font-bold">
                رویدادی با این مشخصات پیدا نشد.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}