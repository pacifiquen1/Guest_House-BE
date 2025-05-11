from rest_framework import serializers
from .models import Room, Meal, Guest, Reservation, DebitCard, Transaction

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class DebitCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitCard
        fields = '__all__'

    def to_representation(self, instance):
        serialized_data = super(DebitCardSerializer, self).to_representation(instance)
        # serialized_data["has_guest"] = True if instance.guest else False
        return serialized_data

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('timestamp',)

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class ReservationCreateSerializer(serializers.Serializer):
    guest_name = serializers.CharField(max_length=100)
    guest_email = serializers.EmailField()
    room_id = serializers.IntegerField(required=False, allow_null=True)
    meal_id = serializers.IntegerField(required=False, allow_null=True)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()

class PaymentSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reservation_id = serializers.IntegerField()

class DepositSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)