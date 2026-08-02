# Hotfix: jalali_filters + WebsiteSubmitForm Meta

## Bugs fixed

1. **`jalali_filters` is not a registered tag library**
   - Templates (`detail.html`, `admin_dashboard.html`, `user_dashboard.html`) still do `{% load jalali_filters %}`
   - After merging FarsiSaz away, that library disappeared
   - **Fix:** add `farsi/templatetags/jalali_filters.py` as a thin re-export of Jalali filters

2. **`to_jalali` ignored format argument**
   - Templates use `{{ dt|to_jalali:"%H:%M %Y-%m-%d" }}`
   - **Fix:** `to_jalali(value, fmt="%Y/%m/%d")` now accepts the format string

3. **`ValueError: ModelForm has no model class specified`** on `/submit/`
   - `WebsiteSubmitForm` had no `class Meta: model = Website`
   - **Fix:** restored `Meta` + `captcha` field + sensible widgets

4. **`website_card.html`** used filters without `{% load farsi_tags %}`
   - **Fix:** load tag added at top

## Apply

```bash
# From repo root

# A) Compatibility tag library + updated filters
cp path/to/fix/farsi/templatetags/jalali_filters.py farsi/templatetags/
cp path/to/fix/farsi/templatetags/farsi_tags.py     farsi/templatetags/

# B) Form with Meta.model
cp path/to/fix/directory/forms.py directory/forms.py

# C) Partial template load
cp path/to/fix/directory/templates/directory/website_card.html \
   directory/templates/directory/website_card.html

# Restart (required — template libraries are cached at process start)
python manage.py check
python manage.py runserver
```

After restart, registered libraries should include: `farsi`, `farsi_tags`, `farsi_widgets`, **`jalali_filters`**.
