from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import views, permissions, status
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from accounts.models import User
from projects.models import Project
from notifications.models import Notification


# ==========================================
# Server-Rendered Views
# ==========================================

@login_required
def inbox_view(request):
    conversations = request.user.conversations.prefetch_related('participants', 'messages').order_by('-updated_at')
    active_conv = conversations.first()

    return render(request, 'chat/inbox.html', {
        'conversations': conversations,
        'active_conv': active_conv,
    })


@login_required
def conversation_view(request, pk):
    conversation = get_object_or_404(request.user.conversations.prefetch_related('participants', 'messages'), pk=pk)
    conversations = request.user.conversations.prefetch_related('participants').order_by('-updated_at')

    # Mark unread messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    other_user = conversation.get_other_participant(request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        attachment = request.FILES.get('attachment')

        if content or attachment:
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                attachment=attachment
            )
            conversation.save()  # update updated_at

            if other_user:
                Notification.send(
                    user=other_user,
                    notification_type=Notification.Type.MESSAGE,
                    title=f"New message from {request.user.display_name}",
                    message=f"{content[:50]}..." if content else "Sent an attachment",
                    link=f"/chat/{conversation.id}/"
                )

        return redirect('chat:conversation', pk=conversation.id)

    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'conversations': conversations,
        'other_user': other_user,
        'messages_list': conversation.messages.all(),
    })


@login_required
def start_conversation_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('chat:inbox')

    project_id = request.GET.get('project_id')
    project = Project.objects.filter(id=project_id).first() if project_id else None
    demo_title = request.GET.get('demo_title')

    # Check if a conversation between these two already exists
    conv = Conversation.objects.filter(participants=request.user).filter(participants=target_user).first()

    if not conv:
        conv = Conversation.objects.create(related_project=project)
        conv.participants.add(request.user, target_user)

    if demo_title:
        inquiry_text = f"Hi {target_user.display_name}! I saw your demo showcase project '{demo_title}' on AdvIT and I'd like to discuss a custom project with you."
        Message.objects.create(
            conversation=conv,
            sender=request.user,
            content=inquiry_text
        )
        conv.save()

    return redirect('chat:conversation', pk=conv.id)



# ==========================================
# REST API Endpoints
# ==========================================

class MessageListAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        conversation = get_object_or_404(request.user.conversations, pk=pk)
        messages_qs = conversation.messages.select_related('sender').order_by('timestamp')
        return Response(MessageSerializer(messages_qs, many=True).data)


class SendMessageAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conversation = get_object_or_404(request.user.conversations, pk=pk)
        content = request.data.get('content', '').strip()

        if not content:
            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        conversation.save()

        # Send notification to other participant
        other_user = conversation.get_other_participant(request.user)
        if other_user:
            Notification.send(
                user=other_user,
                notification_type=Notification.Type.MESSAGE,
                title=f"New message from {request.user.display_name}",
                message=f"{content[:50]}...",
                link=f"/chat/{conversation.id}/"
            )

        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)
