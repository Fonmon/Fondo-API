import logging
from fondo_api.models import UserProfile, SavingAccount

class SavingAccountService:
    def __init__(self):
        self.ACCOUNTS_PER_PAGE = 10
        self.__logger = logging.getLogger(__name__)

    def create_account(self, user_id, obj):
        user = UserProfile.objects.get(id=user_id)
        saving_account = SavingAccount.objects.create(
            open_date = '',
            end_date = obj['end_date'],
            user = user,
        )
        return saving_account.id