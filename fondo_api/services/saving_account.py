import logging
from django.core.paginator import Paginator

from fondo_api.models import SavingAccount
from fondo_api.serializers import SavingAccountSerializer

class SavingAccountService:
    def __init__(self, user_service = None, notification_service = None):
        self.ACCOUNTS_PER_PAGE = 10
        self.__logger = logging.getLogger(__name__)
        self.__user_service = user_service
        self.__notification_service = notification_service

    def create_account(self, user_id, obj):
        user = self.__user_service.get_profile(user_id)
        saving_account = SavingAccount.objects.create(
            end_date = obj['end_date'],
            user = user,
        )
        # send notification
        self.__notification_service.send_notification(
			self.__user_service.get_users_attr('id', [0,2]), 
			"Ha sido creada una nueva CAP", 
			"/manage/caps",
		)
        # TODO: schedule task for closing CAP
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

    def update_account(self, obj):
        try:
            account = SavingAccount.objects.get(id=obj['id'])
        except SavingAccount.DoesNotExist:
            return False
        account.state = obj['state']
        account.value = obj['value']
        account.save()
        return True