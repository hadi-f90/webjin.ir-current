import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from websites.models import Website, Category  # change if needed


class Command(BaseCommand):
    help = "Import websites from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the CSV file",
        )

    def get_unique_slug(self, title):
        base_slug = slugify(title)
        slug = base_slug
        counter = 1

        while Website.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        created_count = 0
        skipped_count = 0

        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                with transaction.atomic():
                    for row in reader:
                        name = (row.get("name") or "").strip()
                        url = (row.get("url") or "").strip()
                        description = (row.get("description") or "").strip()

                        if not name or not url:
                            skipped_count += 1
                            continue

                        if Website.objects.filter(url=url).exists():
                            skipped_count += 1
                            continue

                        slug = self.get_unique_slug(name)

                        website = Website.objects.create(
                            title=name,
                            slug=slug,
                            url=url,
                            description=description,
                            status="pending",
                        )

                        # Optional category column
                        category_name = (row.get("category") or "").strip()
                        if category_name:
                            category, _ = Category.objects.get_or_create(
                                name=category_name
                            )
                            website.category = category
                            website.save()

                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Imported: {created_count} | Skipped: {skipped_count}"
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("❌ File not found.")
            )
