from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Room, Meal, Guest, Reservation, DebitCard, Transaction
from .serializers import (
    RoomSerializer, MealSerializer, GuestSerializer, DebitCardSerializer,
    TransactionSerializer, ReservationSerializer, ReservationCreateSerializer,
    PaymentSerializer, DepositSerializer
)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class DebitCardViewSet(viewsets.ModelViewSet):
    queryset = DebitCard.objects.all()
    serializer_class = DebitCardSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        guest, _ = Guest.objects.get_or_create(email=data['guest_email'], defaults={'name': data['guest_name']})

        reservation = Reservation(guest=guest)
        total_cost = 0

        if data.get('room_id'):
            try:
                room = Room.objects.get(pk=data['room_id'], is_available=True)
                reservation.room = room
                time_difference = (data['check_out_date'] - data['check_in_date']).days
                if time_difference < 1:
                    return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)
                total_cost += room.price_per_night * time_difference
                room.is_available = False
                room.save()
            except Room.DoesNotExist:
                return Response({"error": f"Room with ID {data['room_id']} is not available or does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('meal_id'):
            try:
                meal = Meal.objects.get(pk=data['meal_id'])
                reservation.meal = meal
                total_cost += meal.price
            except Meal.DoesNotExist:
                return Response({"error": f"Meal with ID {data['meal_id']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if total_cost == 0:
            return Response({"error": "Reservation must include at least a room or a meal."}, status=status.HTTP_400_BAD_REQUEST)

        reservation.total_cost = total_cost
        reservation.save()

        payment_url = "/api/payments/"  # Simulate redirection URL
        return Response({"message": "Reservation created. Redirecting to payment...", "payment_url": payment_url, "reservation_id": reservation.id}, status=status.HTTP_201_CREATED)

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class TransactionDetailView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

@api_view(['POST'])
def process_payment(request):
    # All the function code for processing payment will go here
    card_number = request.data.get('card_number')
    amount = request.data.get('amount')
    reservation_id = request.data.get('reservation_id')

    if not card_number or not amount or not reservation_id:
        return Response({"error": "Card number, amount, and reservation ID are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        debit_card = DebitCard.objects.get(card_number=card_number)
    except DebitCard.DoesNotExist:
        return Response({"error": "Invalid card number."}, status=status.HTTP_400_BAD_REQUEST)

    amount = float(amount)
    if debit_card.balance >= amount:
        debit_card.balance -= amount
        debit_card.save()
        Transaction.objects.create(debit_card=debit_card, amount=-amount, transaction_type='payment', reservation_id=reservation_id)
        return Response({"message": f"Payment of {amount} successful."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def deposit_funds(request):
    card_number = request.data.get('card_number')
    amount = request.data.get('amount')

    if not card_number or not amount:
        return Response({"error": "Card number and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        debit_card = DebitCard.objects.get(card_number=card_number)
    except DebitCard.DoesNotExist:
        return Response({"error": "Invalid card number."}, status=status.HTTP_400_BAD_REQUEST)

    amount = float(amount)
    debit_card.balance += amount
    debit_card.save()
    Transaction.objects.create(debit_card=debit_card, amount=amount, transaction_type='deposit')
    return Response({"message": f"Deposit of {amount} successful."}, status=status.HTTP_200_OK)