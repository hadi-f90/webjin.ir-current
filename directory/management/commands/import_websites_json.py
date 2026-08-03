"""Import websites from a nested JSON file into directory.Website."""

import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from directory.models import Category, Website


class Command(BaseCommand):
    help = "Import websites from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the JSON file")
        parser.add_argument(
            "--created-by",
            type=str,
            default=None,
            help="Username to assign as created_by",
        )
        parser.add_argument(
            "--default-status",
            type=str,
            default="pending",
            help="Status for imported items: pending/approved/rejected",
        )
        parser.add_argument(
            "--default-category",
            type=str,
            default="Imported",
            help="Fallback category name if none can be inferred",
        )

    def get_unique_slug(self, title):
        base_slug = (slugify(title) or "item")[:45]
        slug = base_slug
        counter = 1
        while Website.objects.filter(slug=slug).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[: 50 - len(suffix)]}{suffix}"
            counter += 1
        return slug

    def get_user(self, username):
        if not username:
            return None
        User = get_user_model()
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' not found. created_by will be empty."
                )
            )
            return None

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

    def import_item(self, item, category_obj, created_by, default_status):
        name = (item.get("name") or item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        description = (item.get("description") or "").strip()
        tags = item.get("tags") or []

        if not name or not url:
            return "skipped", "missing name/url"

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if Website.objects.filter(url=url).exists():
            return "skipped", "duplicate url"

        website = Website.objects.create(
            title=name,
            slug=self.get_unique_slug(name),
            url=url,
            description=description,
            category=category_obj,
            status=default_status,
            created_by=created_by,
            owner_name="",
            owner_email="",
            hide_owner_info=True,
        )

        if tags:
            cleaned = [str(t).strip() for t in tags if str(t).strip()]
            if cleaned:
                website.tags.add(*cleaned)

        return "created", website.title

    def handle(self, *args, **options):
        file_path = options["file_path"]
        default_status = options["default_status"]
        default_category_name = options["default_category"]
        created_by = self.get_user(options["created_by"])

        if default_status not in {"pending", "approved", "rejected"}:
            self.stdout.write(self.style.ERROR("Invalid --default-status value"))
            return

        json_path = Path(file_path)
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON: {e}"))
            return

        created_count = 0
        skipped_count = 0
        default_category = self.get_or_create_category(default_category_name)

        with transaction.atomic():
            # Nested structure:
            # { "group": { "subgroup": [ {name, url, description?, tags?}, ... ] } }
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        skipped_count += 1
                        continue
                    result, message = self.import_item(
                        item, default_category, created_by, default_status
                    )
                    if result == "created":
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Created: {message}"))
                    else:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f"Skipped: {message}"))
            elif isinstance(data, dict):
                for top_key, top_value in data.items():
                    if isinstance(top_value, list):
                        for item in top_value:
                            if not isinstance(item, dict):
                                skipped_count += 1
                                continue
                            cat = (
                                self.get_or_create_category(
                                    str(top_key).replace("_", " ").title()
                                )
                                or default_category
                            )
                            result, message = self.import_item(
                                item, cat, created_by, default_status
                            )
                            if result == "created":
                                created_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"Created: {message}")
                                )
                            else:
                                skipped_count += 1
                                self.stdout.write(
                                    self.style.WARNING(f"Skipped: {message}")
                                )
                        continue
                    if not isinstance(top_value, dict):
                        continue
                    for sub_key, items in top_value.items():
                        if not isinstance(items, list):
                            continue
                        category_name = (
                            sub_key.replace("_", " ").title()
                            if sub_key
                            else default_category_name
                        )
                        category_obj = (
                            self.get_or_create_category(category_name)
                            or default_category
                        )
                        for item in items:
                            if not isinstance(item, dict):
                                skipped_count += 1
                                continue
                            result, message = self.import_item(
                                item=item,
                                category_obj=category_obj,
                                created_by=created_by,
                                default_status=default_status,
                            )
                            if result == "created":
                                created_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"Created: {message}")
                                )
                            else:
                                skipped_count += 1
                                self.stdout.write(
                                    self.style.WARNING(f"Skipped: {message}")
                                )
            else:
                self.stdout.write(self.style.ERROR("JSON root must be object or array"))
                return

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Skipped: {skipped_count}"
            )
        )
