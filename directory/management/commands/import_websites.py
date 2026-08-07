"""Import websites from a CSV file.

Expected columns: name, url, description (optional), category (optional)
"""

import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from directory.models import Category, Website


class Command(BaseCommand):
    help = "Import websites from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the CSV file",
        )
        parser.add_argument(
            "--status",
            type=str,
            default="pending",
            help="Status for imported sites: pending/approved/rejected",
        )

    def get_unique_slug(self, title):
        base_slug = slugify(title) or f"website-{title[:8]}"
        slug = base_slug
        counter = 1
        while Website.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_or_create_category(self, name):
        name = (name or "").strip()
        if not name:
            return None
        slug = slugify(name) or "category"
        base = slug
        n = 1
        while Category.objects.filter(slug=slug).exclude(name=name).exists():
            slug = f"{base}-{n}"
            n += 1
        category, _ = Category.objects.get_or_create(
            name=name,
            defaults={"slug": slug},
        )
        if not category.slug:
            category.slug = slug
            category.save(update_fields=["slug"])
        return category

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        status = kwargs.get("status", "pending")
        if status not in {"pending", "approved", "rejected"}:
            self.stdout.write(self.style.ERROR("Invalid --status value"))
            return

        created_count = 0
        skipped_count = 0

        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                with transaction.atomic():
                    for row in reader:
                        name = (row.get("name") or row.get("title") or "").strip()
                        url = (row.get("url") or "").strip()
                        description = (row.get("description") or "").strip()

                        if not name or not url:
                            skipped_count += 1
                            continue

                        if not url.startswith(("http://", "https://")):
                            url = "https://" + url

                        if Website.objects.filter(url=url).exists():
                            skipped_count += 1
                            continue

                        category = self.get_or_create_category(
                            (row.get("category") or "").strip()
                        )

                        Website.objects.create(
                            title=name,
                            slug=self.get_unique_slug(name),
                            url=url,
                            description=description,
                            category=category,
                            status=status,
                        )
                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported: {created_count} | Skipped: {skipped_count}"
                )
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("File not found."))
