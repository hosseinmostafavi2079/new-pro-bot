"use client";
import { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import Header from '../../components/Header';
import { AuthContext } from '../../context/AuthContext';
// --- اصلاح شد: TicketIcon اضافه شد ---
import { CalendarIcon, MapPinIcon, QrCodeIcon, TicketIcon } from '@heroicons/react/24/outline'; 
import QRCode from "react-qr-code";
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);
  const router = useRouter();

  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        router.push('/login');
        return;
    }

    axios.get('http://127.0.0.1:8000/api/my-tickets/', {
        headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => {
        setTickets(res.data);
        setLoading(false);
    })
    .catch(err => {
        console.error(err);
        setLoading(false);
    });
  }, []);

  if (loading) return <div className="min-h-screen flex justify-center items-center"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div></div>;

  return (
    <div className="min-h-screen bg-[#F3F4F6]" dir="rtl">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-black text-gray-900 mb-8 flex items-center gap-3">
            <TicketIcon className="w-8 h-8 text-blue-600" />
            بلیط‌های من
        </h1>

        {tickets.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl shadow-sm border border-gray-100">
                <p className="text-gray-500 mb-4">شما هنوز بلیطی نخریده‌اید.</p>
                <a href="/" className="text-blue-600 font-bold hover:underline">مشاهده رویدادها</a>
            </div>
        ) : (
            <div className="space-y-6">
                {tickets.map(ticket => (
                    <div key={ticket.id} className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-6 items-center">
                        {/* عکس رویداد */}
                        <img 
                            src={ticket.event.image_url || "https://placehold.co/200x200"} 
                            className="w-full md:w-48 h-32 object-cover rounded-2xl" 
                            alt={ticket.event.title} 
                        />
                        
                        {/* اطلاعات */}
                        <div className="flex-1 w-full text-center md:text-right">
                            <h2 className="text-xl font-bold text-gray-900 mb-2">{ticket.event.title}</h2>
                            <div className="flex flex-col md:flex-row gap-4 text-sm text-gray-500 mb-4 justify-center md:justify-start">
                                <span className="flex items-center gap-1"><CalendarIcon className="w-4 h-4"/> {new Date(ticket.event.start_time).toLocaleDateString('fa-IR')}</span>
                                <span className="flex items-center gap-1"><MapPinIcon className="w-4 h-4"/> {ticket.event.location}</span>
                            </div>
                            <div className="text-xs text-gray-400">کد رهگیری: {ticket.ticket_code.split('-')[0]}...</div>
                        </div>

                        {/* دکمه QR */}
                        <button 
                            onClick={() => setSelectedTicket(ticket)}
                            className="w-full md:w-auto bg-gray-900 text-white px-6 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-gray-800 transition shadow-lg shadow-gray-900/20"
                        >
                            <QrCodeIcon className="w-5 h-5" />
                            نمایش بلیط
                        </button>
                    </div>
                ))}
            </div>
        )}
      </main>

      {/* --- مودال نمایش QR Code --- */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4" onClick={() => setSelectedTicket(null)}>
            <div className="bg-white p-8 rounded-3xl max-w-sm w-full text-center shadow-2xl transform scale-100 transition-all" onClick={e => e.stopPropagation()}>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{selectedTicket.event.title}</h3>
                <p className="text-gray-500 text-sm mb-6">این کد را هنگام ورود به مسئول سالن نشان دهید</p>
                
                <div className="bg-white p-4 border-2 border-dashed border-gray-200 rounded-2xl inline-block mb-6">
                    <QRCode 
                        value={selectedTicket.ticket_code} 
                        size={200}
                        viewBox={`0 0 256 256`}
                    />
                </div>
                
                <div className="text-xs font-mono text-gray-400 mb-6 bg-gray-50 p-2 rounded-lg break-all">
                    {selectedTicket.ticket_code}
                </div>

                <button 
                    onClick={() => setSelectedTicket(null)}
                    className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition"
                >
                    بستن
                </button>
            </div>
        </div>
      )}
    </div>
  );
}