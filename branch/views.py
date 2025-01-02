from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from .models import Branch
from django.contrib.auth import get_user_model

User = get_user_model()

@require_GET
def get_user_branches(request, user_id):
    """Fetch all branches for a specific user."""
    branches = Branch.objects.filter(user=user_id).order_by('position')  # Query branches for the user

    # Serialize the branch data
    branches_data = [
        {
            "id": branch.id,
            "title": branch.title,
            "position": branch.position,
            "hash_id": branch.hash_id,
        }
        for branch in branches
    ]

    return JsonResponse(branches_data, safe=False)