from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Vessel
import threading


class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        Vessel.objects.create(name="Test Vessel", content=50.0)
        self.stdout.write("Simulating condition...")
        self.run_simulation()

    def run_simulation(self):
        barrier = threading.Barrier(2)
        lock = threading.Lock()
        
        """ The problem appears to be that each thread is simultaneously getting the object from the DB. 
        This means that there will be an issue with the integrity of the data.
        We can introduce a lock to ensure that only one thread has access to the database at a time, 
        and also use some tools form django to make sure the transactions are atomic """
        
        # Check to see if if vessel is currently empty. This is how I interpret the specification in the README, but it should probably be done elsewhere, like in the specific threads.

        vessel = Vessel.objects.get(id=1)
        if vessel.content == 0.0:
            raise ValueError("Vessel is currently empty, no withdrawals can be made.")
        
        def user1():
            barrier.wait()
            with lock:
                with transaction.atomic():
                    vessel = Vessel.objects.get(id=1)
                    #Potential point to check current content of vessel
                    vessel.content -= 10.0
                    vessel.save()

        def user2():
            barrier.wait()
            with lock:
                with transaction.atomic():
                    vessel = Vessel.objects.get(id=1)
                    #Potential point to check current content of vessel
                    vessel.content -= 10.0
                    vessel.save()

        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=1)
        self.stdout.write(f"Remaining content: {vessel.content} kg")
