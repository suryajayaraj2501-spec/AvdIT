from django.shortcuts import render
from rest_framework import views, permissions, status
from rest_framework.response import Response
from .services import GeminiService
from .models import AIConversation, AIMessage, AIRecommendation
from projects.models import Project
from freelancers.models import FreelancerProfile, Skill


def team_builder_page_view(request):
    """Interactive client-facing AI Team Builder page."""
    return render(request, 'ai_chatbot/team_builder.html')


# ==========================================
# REST API Endpoints
# ==========================================

class AITeamBuilderAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get('title', 'AI Web Application')
        description = request.data.get('description', '')
        budget = request.data.get('budget', 1500)
        category = request.data.get('category', 'Full-Stack Product')
        project_id = request.data.get('project_id')

        if not description:
            return Response({'error': 'Project description is required.'}, status=status.HTTP_400_BAD_REQUEST)

        rec_data = GeminiService.build_team_recommendation(
            project_title=title,
            description=description,
            budget=budget,
            category=category
        )

        # Persist recommendation
        if request.user.is_authenticated:
            project_obj = Project.objects.filter(id=project_id).first() if project_id else None
            AIRecommendation.objects.create(
                user=request.user,
                project=project_obj,
                recommendation_type=AIRecommendation.RecType.TEAM_STRUCTURE,
                payload=rec_data
            )

        return Response(rec_data, status=status.HTTP_200_OK)


class AIFreelancerMatchingAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        skills = request.data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]

        freelancers = GeminiService._match_freelancers_from_db(skills)
        teams = GeminiService._match_teams_from_db(skills)

        return Response({
            'matching_freelancers': freelancers,
            'matching_teams': teams
        })


class AIProposalGeneratorAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        project_title = request.data.get('project_title', '')
        project_desc = request.data.get('project_desc', '')

        if project_id:
            try:
                p = Project.objects.get(id=project_id)
                project_title = p.title
                project_desc = p.description
            except Project.DoesNotExist:
                pass

        user = request.user
        fl_profile = getattr(user, 'freelancer_profile', None)
        fl_bio = fl_profile.bio if fl_profile else user.bio
        skills = [fs.skill.name for fs in fl_profile.freelancer_skills.all()] if fl_profile else ['Full-Stack Development']

        cover_letter = GeminiService.generate_proposal_draft(
            project_title=project_title,
            project_desc=project_desc,
            freelancer_name=user.display_name,
            freelancer_bio=fl_bio,
            skills_list=skills
        )

        return Response({'cover_letter': cover_letter})


class AIProfileImproverAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        fl_profile = getattr(request.user, 'freelancer_profile', None)
        title = request.data.get('title', fl_profile.title if fl_profile else 'Freelancer')
        bio = request.data.get('bio', fl_profile.bio if fl_profile else '')
        hourly_rate = request.data.get('hourly_rate', fl_profile.hourly_rate if fl_profile else 40)
        skills = [fs.skill.name for fs in fl_profile.freelancer_skills.all()] if fl_profile else ['Python', 'Web']

        tips = GeminiService.audit_and_improve_profile(title, bio, skills, hourly_rate)
        return Response(tips)


class AIProjectDecomposerAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get('title', 'Project Scope')
        description = request.data.get('description', '')
        budget = request.data.get('budget', 1000)

        result = GeminiService.decompose_project(title, description, budget)
        return Response(result)


class AIChatbotAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id', '')

        if not message:
            return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or create AI conversation
        conv = None
        if request.user.is_authenticated:
            conv, _ = AIConversation.objects.get_or_create(user=request.user)
        elif session_id:
            conv, _ = AIConversation.objects.get_or_create(session_id=session_id)

        history = conv.messages.all() if conv else []

        bot_result = GeminiService.get_chatbot_response(message, conversation_history=list(history))

        if conv:
            AIMessage.objects.create(conversation=conv, role=AIMessage.Role.USER, content=message)
            AIMessage.objects.create(
                conversation=conv,
                role=AIMessage.Role.ASSISTANT,
                content=bot_result['reply'],
                structured_data=bot_result.get('structured_data', {})
            )

        return Response(bot_result)
