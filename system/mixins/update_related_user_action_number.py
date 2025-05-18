class UpdateRelatedUserActionNumberMixin:
    def update_related_user_action_number(self):
        self.user.action_number += 1
