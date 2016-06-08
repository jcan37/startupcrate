from __future__ import unicode_literals
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
import stripe

stripe.api_key = "sk_test_7omNc4LQGjHI7viCIxfGfIr5"


class Address(models.Model):
    user = models.ForeignKey(User)
    value = models.CharField(max_length=256)
    personal = models.BooleanField(default=False)

    def __str__(self):
        return str(self.value)


class Subscription(models.Model):
    ship_address = models.ForeignKey(Address)
    recipient_name = models.CharField(max_length=64)
    stripe_customer = models.CharField(max_length=32, blank=True, default='')

    def __str__(self):
        return '{0} living at {1}'.format(self.recipient_name, self.ship_address)

    def stripe_customer_retrieve(self):
        return stripe.Customer.retrieve(self.stripe_customer)

    def stripe_subscription_retrieve(self):
        customer = self.stripe_customer_retrieve()
        subscription_id = customer['subscriptions']['data'][0]['id']
        return stripe.Subscription.retrieve(subscription_id)

    def stripe_change_plan(self):
        subscription = self.stripe_subscription_retrieve()
        subscription.plan = 'startupcrate_quarterly' if subscription['plan']['id'] == 'startupcrate_monthly' else 'startupcrate_monthly'
        subscription.save()

    def stripe_cancel(self):
        subscription = self.stripe_subscription_retrieve()
        subscription.delete()

    def customer_object(self):
        customer = self.stripe_customer_retrieve()
        subscription = customer['subscriptions']['data'][0]
        refined_customer = {}
        refined_customer['plan_id'] = subscription['plan']['id']
        refined_customer['plan_type'] = subscription['plan']['name']
        refined_customer['next_bill'] = datetime.fromtimestamp(subscription['current_period_end']).strftime('%B %d, %Y')
        refined_customer['credit_card'] = customer['sources']['data'][0]['last4']
        return refined_customer
