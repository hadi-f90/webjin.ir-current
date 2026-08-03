# Replace delete_tag_ajax in directory/views.py with this body
# (keep the same decorators already above the function).

@require_POST
@staff_member_required
def delete_tag_ajax(request, pk):
    """Handles deletion of a tag via AJAX"""
    tag = get_object_or_404(Tag, pk=pk)

    # TaggableManager related_name is 'websites_tagged' (see directory.models.Website)
    if tag.websites_tagged.exists():
        return JsonResponse(
            {
                'status': 'error',
                'message': (
                    f"این برچسب شامل {tag.websites_tagged.count()} وب‌سایت است. "
                    "لطفاً ابتدا وب‌سایت‌ها را تغییر دهید."
                ),
            },
            status=400,
        )

    tag.delete()
    return JsonResponse({'status': 'success', 'message': "برچسب حذف شد."})
