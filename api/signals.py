# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CartItem

# 🛒 Optional: Signal for any future automatic action after user creation
@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        # Currently, do NOT create CartItem automatically, because product is required
        # If you want, you could log or perform other safe actions here
        print(f"New user registered: {instance.username}")
