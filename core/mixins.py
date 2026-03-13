from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied("Authentication is required.")

        if self.required_role == "client" and not getattr(user, "is_client", False):
            raise PermissionDenied("Only clients can access this page.")

        if self.required_role == "freelancer" and not getattr(user, "is_freelancer", False):
            raise PermissionDenied("Only freelancers can access this page.")

        return super().dispatch(request, *args, **kwargs)


class ClientRequiredMixin(RoleRequiredMixin):
    required_role = "client"


class FreelancerRequiredMixin(RoleRequiredMixin):
    required_role = "freelancer"