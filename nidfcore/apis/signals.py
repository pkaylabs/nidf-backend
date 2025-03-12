import random

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, OTP


@receiver(post_save, sender=User)
def create_otp(sender, instance, created, **kwargs):
    if created:
        otp = random.randint(1000, 9999)
        otp = OTP.objects.create(phone=instance.phone, otp=otp)
        print(f"OTP for {instance.email} is {otp}")

        # send otp
        otp.send_otp()
    
