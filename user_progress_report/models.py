from django.db import models
from django.contrib.auth.models import User
from mushaf_page.models import MushafPage
from user_page.models import UserPage
from django.contrib.auth import get_user_model


class UserProgressReport(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_progress_reports')
    markings = models.IntegerField()
    mushaf_page = models.ForeignKey(MushafPage, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Report for {self.user.email} on page {self.mushaf_page}"

def get_latest_user_page_progress(user_id, branch_id, mushaf_page_id):
    # Fetch user pages from the database for the given user, branch, and mushaf page
    filtered_pages = UserPage.objects.filter(
        user_id=user_id, branch=branch_id, mushaf_page=mushaf_page_id
    ).order_by('-updated_at')
    
    latest_page = filtered_pages.first()
    
    if latest_page:
        # Get drawn_paths or empty list if None
        drawn_paths = latest_page.drawn_paths or []
        
        # Count only drawn_paths that have at least 10 objects
        valid_markings_count = sum(
            1 for path in drawn_paths 
            if len(path) >= 10
        )
        
        return {
            'latest_page': latest_page,
            'drawn_paths_count': valid_markings_count
        }
    
    return {
        'latest_page': None,
        'drawn_paths_count': 0
    }

def update_user_progress_reports(user_id):
    user_pages = UserPage.objects.filter(user_id=user_id)
    for user_page in user_pages:
        update_user_progress_report(user_page)

def update_user_progress_report(user_page):
    from mushaf_segment.models import find_mushaf_segment

    if isinstance(user_page, int):
        id = user_page
        # Get the first user page for this user
        user_page = UserPage.objects.get(id=id)
        if not user_page:
            print(f"No pages found for user {id}")
            return
    
    print(user_page)
    branch_id = user_page.branch.id
    mushaf_page_id = user_page.mushaf_page.id

    progress_data = get_latest_user_page_progress(user_page.user, branch_id, mushaf_page_id)
    latest_page = progress_data['latest_page']
    drawn_paths_count = progress_data['drawn_paths_count']

    if latest_page:
        title = find_mushaf_segment(mushaf_page_id).title
        print(f"Title is {title}, page {mushaf_page_id}")
        
        # First, try to get existing record
        user_model = get_user_model()
        try:
            progress_report = UserProgressReport.objects.get(
                user=user_model.objects.get(id=user_page.user.id),
                mushaf_page=MushafPage.objects.get(id=mushaf_page_id)
            )
            # Update existing record
            progress_report.title = title
            progress_report.markings = drawn_paths_count
            progress_report.updated_at = latest_page.updated_at
            progress_report.save()
        except UserProgressReport.DoesNotExist:
            # Create new record
            UserProgressReport.objects.create(
                user=user_model.objects.get(id=user_page.user.id),
                mushaf_page=MushafPage.objects.get(id=mushaf_page_id),
                title=title,
                markings=drawn_paths_count,
                updated_at=latest_page.updated_at
            )
        
        print(f"Done with {title}, page {mushaf_page_id}")