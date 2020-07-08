from rest_framework import serializers

from disturbance.components.das_payments.models import AnnualRentalFee, AnnualRentalFeePeriod


class AnnualRentalFeePeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnualRentalFeePeriod
        fields = (
            'id',
            'period_start_date',
            'period_end_date',
        )


class AnnualRentalFeeSerializer(serializers.ModelSerializer):
    annual_rental_fee_invoice_url = serializers.SerializerMethodField()
    annual_rental_fee_period = AnnualRentalFeePeriodSerializer()

    class Meta:
        model = AnnualRentalFee
        fields = (
            'id',
            'annual_rental_fee_period',
            'invoice_period_start_date',
            'invoice_period_end_date',
            'invoice_reference',
            'annual_rental_fee_invoice_url',
        )

    def validate(self, attr):
        return attr

    def get_annual_rental_fee_invoice_url(self, obj):
        return '/payments/invoice-pdf/{}'.format(obj.invoice_reference) if obj.invoice_reference else None
