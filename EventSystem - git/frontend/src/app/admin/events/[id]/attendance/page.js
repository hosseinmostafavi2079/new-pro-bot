"use client";
import { useState, useEffect, use } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { CheckCircleIcon, XCircleIcon, QrCodeIcon, UserGroupIcon, CheckIcon } from '@heroicons/react/24/outline';

export default function AttendancePage({ params }) {
    const { id } = use(params);
    const [tickets, setTickets] = useState([]);
    const [eventTitle, setEventTitle] = useState('');
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('list'); // 'list' or 'scanner'
    const [lastScanned, setLastScanned] = useState(null);

    const fetchTickets = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get(`http://127.0.0.1:8000/api/admin/events/${id}/tickets/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTickets(res.data.tickets);
            setEventTitle(res.data.event_title);
        } catch (err) {
            toast.error('خطا در دریافت لیست شرکت‌کنندگان');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTickets();
    }, [id]);

    // راه‌اندازی دوربین اسکنر
    useEffect(() => {
        let scanner;
        if (activeTab === 'scanner') {
            scanner = new Html5QrcodeScanner(
                "qr-reader", 
                { fps: 10, qrbox: { width: 250, height: 250 } }, 
                false
            );
            
            scanner.render(
                (decodedText) => {
                    // جلوگیری از اسکن پشت سر هم یک کد تکراری در کسری از ثانیه
                    if (lastScanned !== decodedText) {
                        setLastScanned(decodedText);
                        handleCheckIn(decodedText);
                        // بعد از ۳ ثانیه اجازه اسکن مجدد همان کد را بده
                        setTimeout(() => setLastScanned(null), 3000); 
                    }
                }, 
                (err) => { /* بی‌صدا از خطاها می‌گذریم تا مزاحم کاربر نشود */ }
            );
        }

        return () => {
            if (scanner) {
                scanner.clear().catch(error => console.error("Failed to clear scanner", error));
            }
        };
    }, [activeTab, lastScanned]);

    const handleCheckIn = async (ticketCode) => {
        const token = localStorage.getItem('access_token');
        try {
            const res = await axios.post('http://127.0.0.1:8000/api/admin/tickets/checkin/', 
                { ticket_code: ticketCode },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            toast.success(`حضور تایید شد: ${res.data.user_name}`, { duration: 4000, icon: '✅' });
            fetchTickets(); // آپدیت لیست
        } catch (err) {
            if (err.response?.status === 400 && err.response?.data?.status === 'already_checked') {
                toast.error('این بلیط قبلا اسکن شده است!', { icon: '❌' });
            } else {
                toast.error(err.response?.data?.error || 'کد نامعتبر است', { icon: '🚫' });
            }
        }
    };

    if (loading) return <div className="text-center py-20 dark:text-white">در حال بارگذاری اطلاعات...</div>;

    const checkedInCount = tickets.filter(t => t.is_checked_in).length;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm p-8 min-h-screen">
            <div className="flex flex-col md:flex-row justify-between items-center mb-8 border-b dark:border-gray-700 pb-6">
                <div>
                    <h1 className="text-2xl font-black text-gray-900 dark:text-white mb-2">حضور و غیاب</h1>
                    <p className="text-blue-600 font-bold">{eventTitle}</p>
                </div>
                <div className="mt-4 md:mt-0 flex gap-4 text-center">
                    <div className="bg-gray-50 dark:bg-gray-700 px-6 py-3 rounded-2xl">
                        <span className="block text-sm text-gray-500 dark:text-gray-400">کل ثبت‌نام</span>
                        <span className="text-xl font-black text-gray-900 dark:text-white">{tickets.length}</span>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/30 px-6 py-3 rounded-2xl">
                        <span className="block text-sm text-green-600 dark:text-green-400">حاضرین</span>
                        <span className="text-xl font-black text-green-600 dark:text-green-400">{checkedInCount}</span>
                    </div>
                </div>
            </div>

            {/* تب‌ها */}
            <div className="flex gap-4 mb-8">
                <button 
                    onClick={() => setActiveTab('list')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition ${activeTab === 'list' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}
                >
                    <UserGroupIcon className="w-5 h-5" />
                    لیست دستی
                </button>
                <button 
                    onClick={() => setActiveTab('scanner')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition ${activeTab === 'scanner' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}
                >
                    <QrCodeIcon className="w-5 h-5" />
                    اسکنر دوربین
                </button>
            </div>

            {/* محتوای تب اسکنر */}
            {activeTab === 'scanner' && (
                <div className="max-w-md mx-auto">
                    <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-3xl shadow-inner border border-gray-200 dark:border-gray-700">
                        <div id="qr-reader" className="rounded-2xl overflow-hidden w-full"></div>
                    </div>
                    <p className="text-center text-gray-500 mt-6 text-sm">
                        دوربین گوشی را روی بارکد بلیط کاربر نگه دارید. سیستم به صورت خودکار حضور را ثبت می‌کند.
                    </p>
                </div>
            )}

            {/* محتوای تب لیست دستی */}
            {activeTab === 'list' && (
                <div className="overflow-x-auto">
                    <table className="w-full text-right border-collapse">
                        <thead>
                            <tr className="bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-b dark:border-gray-600">
                                <th className="p-4 font-bold rounded-tr-2xl">نام شرکت‌کننده</th>
                                <th className="p-4 font-bold">شماره تماس</th>
                                <th className="p-4 font-bold">کد بلیط</th>
                                <th className="p-4 font-bold rounded-tl-2xl text-center">وضعیت / عملیات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickets.map(ticket => (
                                <tr key={ticket.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                                    <td className="p-4 font-bold text-gray-900 dark:text-white">{ticket.user_name}</td>
                                    <td className="p-4 text-gray-500 dark:text-gray-400 font-mono">{ticket.user_phone}</td>
                                    <td className="p-4 text-gray-500 dark:text-gray-400 font-mono text-sm">{ticket.ticket_code.split('-')[0]}...</td>
                                    <td className="p-4 text-center">
                                        {ticket.is_checked_in ? (
                                            <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 px-3 py-1 rounded-lg text-sm font-bold">
                                                <CheckCircleIcon className="w-5 h-5" /> حاضر
                                            </span>
                                        ) : (
                                            <button 
                                                onClick={() => handleCheckIn(ticket.ticket_code)}
                                                className="bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white px-4 py-1.5 rounded-lg text-sm font-bold transition flex items-center gap-1 mx-auto"
                                            >
                                                <CheckIcon className="w-4 h-4" /> ثبت حضور
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {tickets.length === 0 && (
                                <tr>
                                    <td colSpan="4" className="p-8 text-center text-gray-500">هیچکس هنوز ثبت‌نام نکرده است.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}