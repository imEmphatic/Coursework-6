import logging

from django import forms
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from blog.models import BlogPost

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import Client, Mailing, MailingLog, Message

logger = logging.getLogger(__name__)


CustomUser = get_user_model()


@method_decorator(cache_page(60 * 15), name="dispatch")
class MainPageView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="running").count()
        context["unique_clients"] = Client.objects.aggregate(
            Count("id", distinct=True)
        )["id__count"]
        context["random_posts"] = BlogPost.objects.order_by("?")[:3]
        return context


@method_decorator(cache_page(60 * 5), name="dispatch")
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("client_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


@method_decorator(cache_page(60 * 5), name="dispatch")
class MessageListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.all()


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")


# представления для Mailing
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        if self.request.user.is_manager:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_manager


class MailingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "periodicity", "message", "clients", "status"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.status == "running":
            form.fields["start_time"].widget.attrs["readonly"] = True
            form.fields["periodicity"].widget.attrs["readonly"] = True
        return form

    def form_valid(self, form):
        if self.object.status == "running":
            # Если рассылка активна, разрешаем изменять только определенные поля
            self.object.message = form.cleaned_data["message"]
            self.object.clients.set(form.cleaned_data["clients"])
            self.object.save()
        else:
            form.save()
        return super().form_valid(form)


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = "created"
        return super().form_valid(form)


# class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
#     model = Mailing
#     template_name = 'mailing/mailing_form.html'
#     fields = ['subject', 'message', 'clients', 'start_time', 'periodicity']
#     success_url = reverse_lazy('mailing_list')


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


class MailingStatusView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        action = request.POST.get("action")
        if action == "start":
            mailing.status = "running"
        elif action == "pause":
            mailing.status = "paused"
        elif action == "resume":
            mailing.status = "running"
        mailing.save()
        return redirect("mailing_detail", pk=pk)


class MailingAttemptStatsView(ListView):
    model = Mailing
    template_name = "mailing/mailing_attempt_stats.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.annotate(
            total_attempts=Count("attempts"),
            successful_attempts=Count(
                "attempts", filter=models.Q(attempts__status=True)
            ),
        )


class MailingAttemptDetailView(DetailView):
    model = Mailing
    template_name = "mailing/mailing_attempt_detail.html"
    context_object_name = "mailing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all().order_by("-timestamp")
        return context


class MailingLogListView(ListView):
    model = MailingLog
    template_name = "mailing/mailing_log_list.html"
    context_object_name = "logs"
    ordering = ["-timestamp"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MailingLog.objects.all()
        return MailingLog.objects.filter(mailing__owner=self.request.user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class StatisticsView(TemplateView):
    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="running").count()
        context["total_clients"] = Client.objects.count()
        context["total_messages"] = Message.objects.count()

        if context["total_mailings"] > 0:
            context["active_percentage"] = (
                context["active_mailings"] / context["total_mailings"]
            ) * 100
        else:
            context["active_percentage"] = 0

        return context


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_manager


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        remember_me = form.cleaned_data.get("remember_me")
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or reverse("client_list")


def verify_email(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_verified = True
    user.save()
    return redirect("login")


def verify_email(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_verified = True
    user.save()
    return redirect("login")


class UserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = CustomUser
    template_name = "mailing/user_list.html"


class ManagerMailingListView(UserPassesTestMixin, ListView):
    model = Mailing
    template_name = "mailing/manager_mailing_list.html"

    def test_func(self):
        return self.request.user.is_manager


class ManagerUserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "mailing/manager_user_list.html"

    def test_func(self):
        return self.request.user.is_manager


class UserBlockView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = CustomUser
    fields = ["is_active"]
    template_name = "mailing/user_block.html"
    success_url = reverse_lazy("user_list")


class MailingDeactivateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Mailing
    fields = ["is_active"]
    template_name = "mailing/mailing_deactivate.html"
    success_url = reverse_lazy("mailing_list")


def custom_logout(request):
    logout(request)
    return redirect("main_page")
