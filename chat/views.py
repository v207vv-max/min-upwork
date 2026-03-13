from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from .forms import MessageCreateForm
from .models import Conversation
from .services import mark_conversation_as_read, send_message


@login_required
def conversation_list_view(request):
    conversations = Conversation.objects.select_related(
        "contract",
        "contract__project",
        "client",
        "freelancer",
    ).filter(
        models.Q(client=request.user) | models.Q(freelancer=request.user)
    ).order_by("-updated_at")

    return render(
        request,
        "chat/conversation_list.html",
        {"conversations": conversations},
    )


@login_required
def conversation_detail_view(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related(
            "contract",
            "contract__project",
            "client",
            "freelancer",
        ),
        pk=pk,
    )

    if not conversation.has_participant(request.user):
        raise PermissionDenied(_("You do not have permission to view this conversation."))

    mark_conversation_as_read(
        conversation=conversation,
        user=request.user,
    )

    form = MessageCreateForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        try:
            send_message(
                conversation=conversation,
                sender=request.user,
                text=form.cleaned_data.get("text", ""),
                image=form.cleaned_data.get("image"),
            )
            messages.success(request, _("Message sent successfully."))
            return redirect("chat:conversation-detail", pk=conversation.pk)

        except ValidationError as e:
            form.add_error(None, str(e))

    messages_qs = conversation.messages.select_related("sender").all()

    return render(
        request,
        "chat/conversation_detail.html",
        {
            "conversation": conversation,
            "messages_list": messages_qs,
            "form": form,
        },
    )
