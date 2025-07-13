from rest_framework import serializers
from .models import User, Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'email')


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
# This code defines serializers for the User, Listing, Booking, and Review models.
# Serializers are used to convert complex data types, like model instances, into JSON or other content types.
# They also handle validation and deserialization of incoming data.
# The UserSerializer includes basic user fields, while the ListingSerializer includes all fields of the Listing model.
# The BookingSerializer and ReviewSerializer include nested user information and handle the creation of bookings and reviews by associating them with the current user. 
# The read_only_fields ensure that certain fields are not modified during updates.