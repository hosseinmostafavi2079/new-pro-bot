from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import Event, Lecturer, Ticket, Category
from .serializers import (
    EventSerializer, 
    LecturerSerializer, 
    TicketSerializer, 
    CategorySerializer, 
    UserListSerializer,
    UserSerializer
)
from django.contrib.auth.models import User
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

# --- ویوهای اصلی ---
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAdminUser] # اگر خواستید فقط ادمین ببیند

class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_active=True)
    serializer_class = EventSerializer

class MyTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user, status='paid').order_by('-purchase_date')

# --- بخش ثبت نام ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

# --- بخش مدیریت کاربران (که باعث خطا شده بود) ---
class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        
        # دریافت تمام تیکت‌های کاربر
        tickets = Ticket.objects.filter(user=user).select_related('event')
        
        tickets_data = []
        total_spent = 0
        
        for ticket in tickets:
            # بررسی ایمن قیمت
            price = 0
            if ticket.event and hasattr(ticket.event, 'price'):
                price = ticket.event.price
            
            total_spent += int(price)
            
            tickets_data.append({
                'id': ticket.id,
                'event_title': ticket.event.title if ticket.event else "رویداد حذف شده",
                'event_image': ticket.event.image.url if (ticket.event and ticket.event.image) else None,
                'purchase_date': ticket.purchase_date if ticket.purchase_date else None,
                'price': price,
                'location': ticket.event.location if ticket.event else "-"
            })

        user_data = UserListSerializer(user).data
        
        return Response({
            'user_info': user_data,
            'stats': {
                'total_tickets': tickets.count(),
                'total_spent': total_spent,
            },
            'tickets': tickets_data
        })


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_events = Event.objects.count()
        total_tickets = Ticket.objects.count()
        
        # 2. اصلاح بخش محاسبه درآمد (اضافه کردن output_field)
        revenue_data = Ticket.objects.aggregate(
            total=Coalesce(
                Sum('event__price'), 
                0, 
                output_field=DecimalField()  # <--- این خط مشکل را حل می‌کند
            )
        )
        total_revenue = revenue_data['total']

        return Response({
            'total_users': total_users,
            'total_events': total_events,
            'total_tickets': total_tickets,
            'total_revenue': total_revenue,
        })

class AdminEventTicketsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        # دریافت تمام بلیط‌های این رویداد
        tickets = Ticket.objects.filter(event=event).select_related('user')
        
        result = []
        for t in tickets:
            result.append({
                'id': t.id,
                'ticket_code': t.ticket_code,
                'is_checked_in': t.is_checked_in,
                'purchase_date': t.purchase_date,
                'user_name': f"{t.user.first_name} {t.user.last_name}".strip() or t.user.username,
                'user_phone': t.user.username
            })
        return Response({'event_title': event.title, 'tickets': result})

class AdminCheckInTicketView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        ticket_code = request.data.get('ticket_code')
        if not ticket_code:
            return Response({'error': 'کد بلیط ارسال نشده است'}, status=400)
            
        try:
            ticket = Ticket.objects.get(ticket_code=ticket_code)
            if ticket.is_checked_in:
                return Response({'error': 'این بلیط قبلا استفاده شده است!', 'status': 'already_checked'}, status=400)
            
            # ثبت حضور
            ticket.is_checked_in = True
            ticket.save()
            
            user_name = f"{ticket.user.first_name} {ticket.user.last_name}".strip() or ticket.user.username
            return Response({
                'message': 'حضور با موفقیت ثبت شد', 
                'user_name': user_name,
                'event_title': ticket.event.title
            })
        except Ticket.DoesNotExist:
            return Response({'error': 'بلیط نامعتبر است (یافت نشد)'}, status=404)