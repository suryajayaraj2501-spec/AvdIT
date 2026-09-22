from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer
from accounts.models import User
from projects.models import Project


@login_required
def add_review_view(request):
    if request.method == 'POST':
        reviewee_id = request.POST.get('reviewee_id')
        project_id = request.POST.get('project_id')
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '').strip()
        target_type = request.POST.get('target_type', Review.TargetType.FREELANCER)

        reviewee = get_object_or_404(User, id=reviewee_id)
        project = Project.objects.filter(id=project_id).first() if project_id else None

        if not comment:
            messages.error(request, "Review comment cannot be empty.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        Review.objects.create(
            reviewer=request.user,
            reviewee=reviewee,
            target_type=target_type,
            project=project,
            rating=int(rating),
            comment=comment
        )

        messages.success(request, f"Review submitted for {reviewee.display_name}. Thank you for your feedback!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('landing:index')


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
