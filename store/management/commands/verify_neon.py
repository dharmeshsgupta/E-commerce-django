import json
from django.core.management.base import BaseCommand
from greatkart.neon_services import run_all_neon_tests

class Command(BaseCommand):
    help = 'Verify end-to-end functionality of all wired Neon services'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Neon Services End-to-End Verification..."))
        results = run_all_neon_tests()
        self.stdout.write(json.dumps(results, indent=2))
        
        all_passed = all(
            v.get("status") in ["ok", "connected", "active", "available", "configured", "credential_verified"]
            for v in results.values()
        )
        if all_passed:
            self.stdout.write(self.style.SUCCESS("\n[SUCCESS] All wired Neon services verified successfully!"))
        else:
            self.stdout.write(self.style.ERROR("\n[WARNING] Some Neon services reported issues."))

