from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recognition.models import UserProfile


class Command(BaseCommand):
    help = "Creates two default users with their profiles"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="johndoe@example.com").exists():
            user1 = User.objects.create_user(
                username="johndoe@example.com",
                email="johndoe@example.com",
                password="password123",
            )
            UserProfile.objects.create(
                user=user1,
                last_name="Doe",
                first_name="John",
                zone_agro_select="Nord",
                zone_agro_text="Zone agricole du Nord",
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created default johndoe@example.com")
            )

        # User 2
        if not User.objects.filter(username="janesmith@example.com").exists():
            user2 = User.objects.create_user(
                username="janesmith@example.com",
                email="janesmith@example.com",
                password="password123",
            )
            UserProfile.objects.create(
                user=user2,
                last_name="Smith",
                first_name="Jane",
                zone_agro_select="Sud",
                zone_agro_text="Zone agricole du Sud",
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created default janesmith@example.com")
            )
