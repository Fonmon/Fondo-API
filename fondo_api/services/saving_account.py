import logging
from django.core.paginator import Paginator

from fondo_api.models import UserProfile, SavingAccount
from fondo_api.serializers import SavingAccountSerializer

class SavingAccountService:
    def __init__(self):
        self.ACCOUNTS_PER_PAGE = 10
        self.__logger = logging.getLogger(__name__)

    def create_account(self, user_id, obj):
        user = UserProfile.objects.get(id=user_id)
        saving_account = SavingAccount.objects.create(
            end_date = obj['end_date'],
            user = user,
        )
        return saving_account.id

    def get_accounts(self, user_id, page, all_accounts = False, state = 0, paginate = True):
        if not all_accounts:
            accounts = SavingAccount.objects.filter(user_id=user_id, state=state).order_by('-created_at', '-id')
        else:
            accounts = SavingAccount.objects.filter(state=state).order_by('-created_at', '-id')

        if paginate:
            paginator = Paginator(accounts, self.ACCOUNTS_PER_PAGE)
            if page > paginator.num_pages:
                return {'list': [], 'num_pages': paginator.num_pages, 'count': paginator.count}
            page_return = paginator.page(page)
            serializer = SavingAccountSerializer(page_return.object_list, many=True)
            return {'list': serializer.data, 'num_pages': paginator.num_pages, 'count': paginator.count}
        serializer = SavingAccountSerializer(accounts, many=True)
        return {'list': serializer.data}