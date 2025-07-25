from django.core.cache import cache
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Order, Product, Category
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .views import status_fields


@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, **kwargs):
    print("signal received")
    print(instance.tracker.previous('status'))
    if instance.tracker.previous('status') != instance.status:
        print("Status changed, sending message")
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.user.id}"
        print(group_name)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order_status_update",
                "content": {
                    "order_id": instance.id,
                    "status": instance.status,
                    "message": f"Your order #{instance.id} changed to {status_fields[int(instance.status)]}."
                }
            }
        )


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    print("signal received")
    cache.delete("product_list")


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache.delete("category_list")
