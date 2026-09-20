# Fondo-API — Project Context

Django REST API for a family investment/savings fund ("Fondo Montañez"). Manages
members, contributions, loans (créditos) with amortization schedules, savings
accounts (CAPs), activities per year, web-push notifications, transactional email,
scheduled reminders, and an Amazon Alexa skill backend.

- **Language / stack:** Python 3.9, Django 2.2.27, Django REST Framework 3.11.2,
  PostgreSQL (with `hstore`), Celery 5.2 + Redis broker, Gunicorn.
- **External services:** AWS SES (email), AWS SQS (notification fan-out to a
  Lambda), Google Cloud Storage (file storage), AWS SSM (deploy trigger).
- **Repo layout:** single Django project `api/` + single app `fondo_api/`.

---

## Architecture

### Layering

```
URL (fondo_api/urls.py, api/urls.py)
  -> View  (fondo_api/views/*.py)      APIView subclasses, thin HTTP glue
    -> Service (fondo_api/services/*.py)  business logic, all ORM access
      -> Model (fondo_api/models.py)   + Serializer (fondo_api/serializers.py)
```

- **Views never touch the ORM directly** (except reading `request.user`). They
  parse query params / body, call a service method, and map the result to an HTTP
  status. Services own all `Model.objects...` calls and all transactions.
- **Services are plain classes** (not Django models/managers), instantiated once
  at module import time in the view module, with dependencies injected through the
  constructor:

  ```python
  # fondo_api/views/loan.py
  notification_service = NotificationService()
  user_service = UserService()
  mail_service = MailService()
  loan_service = LoanService(user_service, notification_service, mail_service)
  ```

  Constructors take optional deps defaulting to `None`
  (`def __init__(self, user_service=None, notification_service=None, ...)`), which
  makes them easy to instantiate bare in tests.
- **Private methods / attributes use name mangling**: `self.__logger`,
  `self.__user_service`, `def __get_rate(self, ...)`. Per-service constants are
  UPPER_CASE instance attributes (`self.LOANS_PER_PAGE = 10`,
  `self.ITEMS_PER_PAGE = 10`).
- **Serializers** are DRF `ModelSerializer` / `Serializer`. Heavy use of
  `SerializerMethodField` for computed/formatted fields. Dates are localized to
  Spanish via `babel.dates.format_date(..., locale=settings.LANGUAGE_LOCALE)` and
  `django.utils.timezone.localtime`. `serializers.py` does `from fondo_api.models
  import *`.

### Settings

- `api/settings/` split: `base.py` + `development.py` / `production.py` /
  `test.py`. Each env module does `from .base import *` and sets `ENVIRONMENT`,
  `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`. `settings.ENVIRONMENT` is branched on in
  code (e.g. `FileService` uses an anonymous GCS client when `== 'test'`;
  `PasswordResetView` picks http/https).
- Selected with `DJANGO_SETTINGS_MODULE` (`api.settings.test` in CI).
- **Almost all configuration comes from environment variables** read with
  `os.environ` / `os.environ.get` scattered across modules (DB creds, `AWS_REGION`,
  `DEFAULT_FROM_EMAIL`, `HOST_URL_APP`, `REDIS_HOST`, `NOTIFICATIONS_QUEUE_URL`,
  `ALEXA_CLIENT_ID`, `AWS_SKILL_ID`, `DJANGO_SECRET_KEY`, `ALLOWED_HOST_DOMAIN`).
  There is no settings object for these — modules read `os.environ` at import or
  call time. `MailService.__init__` does `os.environ['DEFAULT_FROM_EMAIL']`
  (KeyError if unset); `celery/tasks.py` does `os.environ['AWS_REGION']` at import.
- Custom template tag lib `fondo_api.templatetags.env_var` registered as a
  template `builtins`; exposes `{% host %}` -> `HOST_URL_APP` for email templates.
- `CORS_ORIGIN_ALLOW_ALL = True`.

### Auth & permissions

- **Authentication:** DRF `TokenAuthentication` only. Token obtained at
  `POST /api-token-auth` (`rest_framework.authtoken.views.obtain_auth_token`).
- **Default permission classes** (global, in `REST_FRAMEWORK`): `IsAuthenticated`
  + `fondo_api.permissions.APIRolePermission`.
- **Role model:** `UserProfile.role` int — `0 ADMIN, 1 PRESIDENT, 2 TREASURER,
  3 MEMBER`. Lower number = more privileged.
- **`APIRolePermission`** reads a hardcoded dict `list_permissions` in
  `fondo_api/permissions.py` keyed by `ViewClassName -> HTTP_METHOD -> rule`:
  - rule is an **int** N  -> allowed if `request.user.userprofile.role <= N`
    (i.e. "this role or more privileged"),
  - rule is a **list**   -> allowed if `role in list` (e.g. `[0, 2]` = admin or
    treasurer),
  - any lookup miss / exception -> **deny** (`except: return False`).
- Views that must bypass auth set `permission_classes = []`: `AuthView`,
  `UserActivateView`, `AlexaView`. (`PasswordResetView` subclasses Django's
  auth view, not DRF.)
- Any authenticated endpoint whose `ViewClassName`/`METHOD` pair is missing from
  `list_permissions` is denied (the `except: return False` fallthrough), so the
  dict must be kept in sync when adding views/methods. Public views instead clear
  `permission_classes`.

---

## Domain model (`fondo_api/models.py`)

- **`UserProfile(User)`** — subclasses `django.contrib.auth.models.User` (concrete
  multi-table inheritance, *not* a swapped `AUTH_USER_MODEL`). `USERNAME_FIELD =
  'email'` but `username` is still populated (code sets `username = email`
  everywhere). Extra fields: `identification` (BigInteger, unique), `role`,
  `key_activation` (nullable, used for the activation link), `birthdate`.
- **`UserPreference`** — `notifications` bool, `primary_color`, `secondary_color`,
  FK user.
- **`UserFinance`** — `contributions`, `balance_contributions`, `total_quota`,
  `utilized_quota`, `available_quota` (all BigInteger, money in whole units),
  `last_modified` auto. `available_quota` is recomputed as
  `total_quota - utilized_quota` on finance updates.
- **`Loan`** — `value`, `timelimit` (months, capped at 36), `disbursement_date`,
  `payment` (`0 CASH, 1 BANK_ACCOUNT, 2 REFINANCED`), `fee` (`0 MONTHLY,
  1 UNIQUE`), `state` (`0 WAITING_APPROVAL, 1 APPROVED, 2 DENIED, 3 PAID_OUT`),
  `rate` (Decimal 5,3 — monthly rate), `comments`, `prev_loan` (self FK,
  SET_NULL), `refinanced_loan` (bare BigInteger id), `disbursement_value`.
- **`LoanDetail`** — one per approved loan: `total_payment`, `minimum_payment`,
  `payday_limit`, `interests`, `capital_balance`, `from_date`. Populated on
  approval and overwritten by the bulk upload.
- **`ActivityYear`** (`year` unique, `enable` bool) / **`Activity`** (`name`,
  `value`, `date`, FK year, M2M users through `ActivityUser`) / **`ActivityUser`**
  (`state`: `0 NOT_PAID, 1 PAID_OUT, 2 EXEMPTED`).
- **`NotificationSubscriptions`** — FK user + `subscription` **HStoreField**
  (web-push PushSubscription JSON stored as hstore; `keys` sub-object is stored as
  a stringified dict and `json.loads`-ed with `'` -> `"` replacement at send time).
- **`SchedulerTask`** — `type` (`0 NOTIFICATIONS`), `run_date` (datetime),
  `payload` HStoreField, `processed` bool, `repeat` (`0 NONE,1 DAILY,2 WEEKLY,
  3 MONTHLY,4 YEARLY`). Polled by the Celery beat `scheduler` task.
- **`File`** — `type` (`0 proceeding, 1 presentations`), `display_name` unique,
  `created_at`. Bytes live in GCS bucket `fonmon` at `<type_display>/<name lower>`.
- **`Power`** — proxy/power-of-attorney request for an assembly: `meeting_date`,
  `state` (`0 PENDING,1 APPROVED,2 REJECTED`), `requester` / `requestee` FKs to
  UserProfile with `related_name` `power_requested` / `power_requestee`.
- **`SavingAccount`** (CAP) — `end_date`, `state` (`0 ACTIVE, 1 CLOSED`), `value`,
  FK user. `UserFinanceSerializer.total_savingaccounts` sums active accounts.
- **Migrations:** `fondo_api/migrations/0001`..`0019`. `hstore` extension is
  created out-of-band (buildspec `CREATE EXTENSION hstore`; test runner creates it
  — see Testing).

---

## HTTP API

Base prefix `/api/`. All routes declared with the legacy `django.conf.urls.url`
(regex) in `fondo_api/urls.py`; auth/password-reset routes in `api/urls.py`.
All endpoints require `Authorization: Token <key>` unless noted.

| Method & path | View | Role rule | Notes |
|---|---|---|---|
| `POST /api-token-auth` | DRF builtin | public | returns `{token}` |
| `GET/POST /api/authorize` | `AuthView` | public (`permission_classes=[]`) | Alexa account-linking OAuth-ish flow; validates `client_id == ALEXA_CLIENT_ID`, redirects with token in URL fragment |
| `POST /password_reset/` | `PasswordResetView` | public | sends SES email via `EmailTemplate.PASSWORD_RESET`; always redirects to `/password_reset/done/` |
| `GET/POST/PATCH /api/loan` | `LoanView` | GET/POST role<=3, PATCH `[0,2]` | GET paginated (`page`, `state` 0-4 where 4=all, `all_loans`, `paginate`); role<=2 may pass `all_loans`. POST creates loan (quota-checked). PATCH = multipart TSV bulk upload of loan details + auto-close |
| `GET/PATCH /api/loan/<id>` | `LoanDetailView` | GET role<=3, PATCH `[0,2]` | GET returns `{loan, loan_detail?}`. PATCH body `{state}` (<=3) drives approval/denial/payout side effects |
| `POST /api/loan/<id>/<app>` | `LoanAppsView` | role<=3 | `app=paymentProjection` (body `{to_date}`) or `app=refinance` (body incl. `disbursement_date`, `includeInterests`, `comments`) |
| `POST/GET/PATCH /api/user` | `UserView` | POST role<=0, GET role<=3, PATCH `[0,2]` | POST creates user + finance + preference + activation email (rolls back if email fails). GET paginated when `page` given. PATCH = multipart TSV bulk finance update keyed by identification |
| `POST /api/user/<app>` | `UserAppsView` | role<=3 | `app=birthdates` -> list; `app=power` -> `handle_power_request` (body `{type: post/get/patch, ...}`) |
| `GET/PATCH/DELETE /api/user/<id>` | `UserDetailView` | GET role<=3, PATCH role<=3, DELETE role<=0 | `id == -1` means "me". PATCH body `{type: personal|finance|preferences, <section>:{...}}`. DELETE = soft delete (`is_active=False`) |
| `POST /api/user/activate/<id>` | `UserActivateView` | public | body `{key, identification, password}` |
| `GET/DELETE/PATCH /api/activity/<id>` | `ActivityDetailView` | GET role<=3, PATCH role<=1, DELETE role<=1 | PATCH `?patch=activity\|user` |
| `GET/POST /api/activity/year` | `ActivityYearView` | GET role<=3, POST role<=1 | POST creates current-year `ActivityYear`, disables the previous one |
| `GET/POST /api/activity/year/<id_year>` | `ActivityYearDetailView` | GET role<=3, POST role<=1 | POST creates an activity and attaches all active users |
| `POST /api/alexa` | `AlexaView` | public | Alexa request envelope; see Alexa section |
| `POST /api/notification/<operation>` | `NotificationView` | POST role<=3 | `operation` = `subscribe` / `unsubscribe`; body is a web-push subscription |
| `GET/POST /api/file` | `FileView` | POST role<=0, GET role<=3 | POST multipart `{name, file, type}` -> GCS. GET `?type=` |
| `GET /api/file/<id>` | `FileDetailView` | GET role<=3 | returns `{url}` — GCS v4 signed URL, 5 min |
| `GET /api/admin` | `AdminView` | GET role<=0 | `?type=email` or `?type=notifications` — self-test send |
| `GET/POST/PUT /api/saving-account` | `SavingAccountView` | GET/POST role<=3, PUT `[0,2]` | GET paginated (`state` 0-1, `all_accounts`, `paginate`). PUT body `{id, state, value}` |

### View conventions

- Every method returns `rest_framework.response.Response(data, status=status.HTTP_*)`.
- Services return `(bool_success, payload_or_message)` tuples; the view unpacks and
  branches: `state, msg = service.x(...)` then
  `return Response(..., status=201) if state else Response({'message': msg}, status=406/404/409)`.
- Query params are pulled with `request.query_params.get(name, default)` and
  manually `int(...)`-cast; range checks return `400` with `{'message': ...}`.
- Multipart/TSV bulk endpoints decorate the method with
  `@parser_classes((MultiPartParser,))` and iterate `request.data['file']` lines:
  `line.decode('utf-8').strip().split("\t")`, dates as `d/m/Y` -> `Y-m-d`.
- `UserAppsView` / `FileView` / `AlexaView` wrap the body in
  `try/except Exception` -> log -> `500`.
- Pagination response shape is consistently
  `{'list': [...], 'num_pages': N, 'count': M}`; page-out-of-range returns an
  empty list with the same envelope (not 404).

---

## Notable business logic / code patterns

### Loans (`fondo_api/services/loan.py`)

- **Rate table** `__get_rate(timelimit)`: `<=6 -> 0.015`, `7-12 -> 0.020`,
  `13-24 -> 0.022`, `25-36 -> 0.025` (monthly). `timelimit > 36` is clamped to 36.
- **Quota check** on create: reject if `value > user_finance.available_quota`
  unless `refinance=True`.
- **On create**, always fires a web-push notification to roles `[0, 2]`
  (`get_users_attr('id', [0,2])`).
- **On approval (`update_loan(id, 1)`)** inside `transaction.atomic()`:
  builds an HTML amortization table (`__generate_table`), creates `LoanDetail`,
  marks `prev_loan.state = 3` if refinancing, sends
  `CHANGE_STATE_LOAN_APPROVED` email to the borrower with roles `[0,2]` BCC'd,
  returns the serialized `LoanDetail`.
- **On denial (state 2)** sends `CHANGE_STATE_LOAN_DENIED`; clears
  `prev_loan.refinanced_loan`.
- **On payout (state 3)** removes scheduled `payment_reminder` tasks.
- **Interest math** (`__calculate_interests`): `((balance * rate) / 30) *
  days360(from, to)` — a US-NASD 30/360 day count implemented in
  `fondo_api/services/utils/date.py` (`days360`, `isLastDay`).
- **`payment_projection(loan_id, to_date)`** — interest accrued to a future date on
  the current `capital_balance`.
- **`refinance_loan`** — only for own APPROVED loan; new loan value = capital
  balance (+ interests if `includeInterests`), `payment = 2` (REFINANCED), links
  both directions (`loan.refinanced_loan = new_id`, `new_loan.prev_loan = loan`).
- **`bulk_update_loans`** — `@transaction.atomic`; parses a TSV, upserts each
  `LoanDetail`, schedules two `payment_reminder` notifications (T-5d and T-1d) per
  loan, then **auto-closes** any still-APPROVED loan whose id was absent from the
  file (`update_loan(loan_id, 3)`).
- Currency formatting for the email table uses `babel.numbers` with a
  `ROUND_HALF_DOWN` local context.

### Users (`fondo_api/services/user.py`)

- **`create_user`** — `@transaction.atomic`; creates `UserProfile` +
  `UserFinance` (all zeros) + `UserPreference`; generates `key_activation` with
  `binascii.hexlify(os.urandom(25))`; sends activation email; **if the email send
  returns falsy, `transaction.set_rollback(True)`** and returns
  `(False, 'Invalid email')`. `IntegrityError` -> `(False, 'Identification/email
  already exists')`.
- **`update_user`** dispatches on `obj['type']` -> `personal` / `finance` /
  `preferences`. Returns `(bool, http_code_int)` where the int is `200/404/409`.
- **Finance update** only writes if a field actually changed; recomputes
  `available_quota`.
- **`activate_user`** matches on `(id, key_activation, identification)`, sets the
  password, `is_active=True`, nulls the key.
- **`inactive_user`** = soft delete.
- **`handle_power_request`** multiplexes CRUD on `Power` via `request['type']`
  (`post`/`get`/`patch`); on approval emails a formal Spanish power-of-attorney
  letter to all users.
- **Birthday notifications**: setting `birthdate` on a personal update schedules a
  yearly (`repeat=4`) `SchedulerTask` for all other users.
- **`get_users_attr(attr, roles=None)`** — helper returning a list of a single
  attribute across active users, optionally role-filtered. Used to build
  recipient/id lists.

### Notifications (`fondo_api/services/notification.py` + `celery/`)

- **Web-push subscriptions** stored per endpoint (dedupe on
  `subscription__endpoint`).
- **`send_notification(user_ids, message, target, run_async=True)`** — collects
  subscriptions, builds `{subscriptions, message:{body, target}}`, and either
  `send_notification.delay(...)` (Celery) or calls the task inline.
- The Celery task **`send_notification`** (`fondo_api/celery/tasks.py`, registered
  as `name="send_notification"`) just pushes the payload to **AWS SQS**
  (`NOTIFICATIONS_QUEUE_URL`); an external Lambda does the actual Web Push. (Recent
  commits #91-93 moved this from direct `pywebpush` to SQS.)
- **`schedule_notification(run_date, payload, repeat=0)`** — creates a
  `SchedulerTask` unless one with the same `owner_id` + `type` already exists for
  that calendar day and is unprocessed. `run_date` made tz-aware with
  `make_aware`.
- **`remove_sch_notitfications(type, owner_id)`** (note the typo in the method
  name — used as-is in `loan.py` and `user.py`).

### Scheduler (Celery beat)

- `api/celery.py` — `Celery('api')`, config from Django settings,
  `autodiscover_tasks(['fondo_api.scheduler'])`, **beat schedule**: task
  `scheduler` runs `crontab(minute=0, hour='10,14')` (10:00 and 14:00,
  `America/Bogota`).
- `fondo_api/scheduler/tasks.py` — `scheduler` task loads today's unprocessed
  `SchedulerTask`s, resolves an executer via
  `fondo_api/scheduler/executers/factory.get_executer(type)`, runs it, marks
  `processed=True`, and `create_repeat_instance` clones the task forward by the
  `repeat` interval (`relativedelta`).
- Executers: `AbstractExecuter` (ABC, `run(payload)`), `NotificationExecuter`
  (`type 0`) -> `NotificationService.send_notification(..., run_async=False)`.
  `payload['user_ids']` is `json.loads`-ed (hstore stores everything as strings).
- `BROKER_URL = redis://<REDIS_HOST>:6379`.

### Email (`fondo_api/services/mail.py`)

- `MailService` uses **boto3 SES** (`boto3.client('ses', region_name=
  os.environ['AWS_REGION'])`). `Source` from `DEFAULT_FROM_EMAIL`.
- `send_mail(template, recipients, params, bcc=[])` — removes any address that is
  in both `recipients` and `bcc`, renders body+subject from Django templates,
  calls `ses.send_email`. Any exception -> logs, returns `False`; success ->
  `True`.
- Templates selected by the **`EmailTemplate` enum** (`fondo_api/enums.py`:
  `USER_ACTIVATION=1, CHANGE_STATE_LOAN_APPROVED=2, CHANGE_STATE_LOAN_DENIED=3,
  POWER_APPROVED=4, TEST=5, PASSWORD_RESET=6`) in `__get_email_from_template`;
  bodies are `fondo_api/templates/<area>/*.html`, subjects `*_subject.txt`. All
  copy is in Spanish.

### Files (`fondo_api/services/file.py`)

- Google Cloud Storage (`google-cloud-storage`), bucket `fonmon`. In `test` env
  uses `storage.Client.create_anonymous_client()`.
- `save_file` uploads the blob and only persists the `File` row if the blob
  did **not** already exist (`blob.exists()` before upload).
- `get_signed_url` -> v4 signed GET URL, 5-minute expiry.

### Alexa (`fondo_api/services/alexa/`)

- `AlexaView` (public) -> `AmazonAlexa` (`amazon_alexa.py`):
  - `set_request(request)` stashes `request.META`, `request.body`, `request.data`.
  - `verify_authenticity()` runs: request-shape check, token lookup
    (`session.user.accessToken` -> DRF `Token` -> `user_id`), timestamp within
    150s, `SignatureCertChainUrl` regex against `s3.amazonaws.com/echo.api/...pem`,
    X.509 cert validation + SHA-1 signature verify (`pyOpenSSL`), and
    `AWS_SKILL_ID` match against `session.application.applicationId`.
  - Errors are raised as `Exception(<http_status_int>, <message>)`; `AlexaView`
    maps the 2-tuple to a DRF status via a `switcher` dict.
  - `process()` dispatches by `request.type` to `LaunchHandler` /
    `IntentHandler`. `IntentHandler` has an `intents` dict
    (`{'RequestLoan': RequestLoanIntent(...)}`); unknown intent -> `Exception(405,
    ...)`.
- Alexa has its own `serializers.py`, `model/` (enums, models), and
  `handlers/abstract_handler.py`.

---

## Testing

- **Framework:** Django `TestCase` (DB-backed, transactional) + DRF; the `mock`
  package (`from mock import patch, MagicMock`), not `unittest.mock`.
- **Custom runner** `fondo_api.tests.runner.TestRunner`
  (`TEST_RUNNER` in `base.py`): disables logging at `CRITICAL`, and monkey-patches
  `BaseDatabaseCreation._create_test_db` to `CREATE EXTENSION IF NOT EXISTS
  hstore` on the test DB (needed because migrations rely on hstore).
- **`fondo_api/tests/abstract_test.py::AbstractTest(TestCase)`** — shared base:
  - `create_user()` — one ADMIN user (`id=1`, `identification=99999`,
    `mail_for_tests@mail.com` / `password`) + `UserFinance` + `UserPreference`.
  - `create_basic_users()` — 10 TREASURER (role 2) users.
  - `get_token(username, password)` — POSTs to `obtain_auth_token`, returns the
    token string.
  - `get_auth_header(token)` -> `{'HTTP_AUTHORIZATION': 'Token <t>'}` splat into
    `self.client.<verb>(..., **self.get_auth_header(token))`.
  - `THREEPLACES = Decimal(10) ** -3` for rate assertions.
- **Test file layout:** `fondo_api/tests/test_<area>_views.py` (one class per
  area), plus `test_models.py`, `test_mail_service.py`, `test_date_utils.py`, and
  `tests/alexa/`. ~175 test methods total. Naming: `test_<action>_<n>` /
  `test_<condition>`. Methods prefixed `pending_test_` are intentionally skipped
  (not run because they don't start with `test_`).
- **Patterns:**
  - `setUp` seeds users, gets a token, and defines request-body dict fixtures as
    `self.<name>_json` / nested dicts.
  - Requests go through `self.client` (Django test `Client`) with
    `data=json.dumps(body), content_type='application/json'`. Multipart uses
    `django.test.client.encode_multipart`.
  - External I/O is mocked at the boundary: `@patch('boto3.client')` returning a
    `MagicMock` whose `.send_email` is asserted with `assert_called_once_with(...)`
    (full expected SES payload, including rendered Spanish email HTML, is
    hardcoded in the assertion). `@patch('requests.post', ...)` in older
    notification tests.
  - Model assertions lean on Django `get_*_display()` for choice fields.
- **Run locally:**
  ```
  coverage run --branch --source='.' manage.py test && \
  coverage report -m --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"
  ```
  Needs Postgres + Redis (README gives `docker run` lines for
  `postgres` with db `fondodev`/user `fondouser`/pw `fondo`, and `redis`).

---

## CI/CD

- **AWS CodeBuild**, driven by **`buildspec.yml`** (version 0.2). Badge in
  `README.md` points at `codebuild.us-east-2`.
- **Env:** `DJANGO_SETTINGS_MODULE=api.settings.test`, Postgres coords for a
  local container, `AWS_REGION=us-east-2`, `HOST_URL_APP`, `DEFAULT_FROM_EMAIL`.
  `DOCKER_PASSWORD` pulled from **SSM parameter store** (`/fonmon/DOCKER_PASSWORD`).
- **Phases:**
  - `install` (Python 3.9): `docker pull postgres`, run a `fondo_db` container,
    `pip install -r requirements.txt`.
  - `pre_build`: `CREATE EXTENSION hstore` in the test DB, `manage.py migrate`.
  - `build`: `coverage run --branch --source='.' manage.py test && coverage
    report -m --omit=...` — **the test suite is the gate** (no separate lint).
  - `post_build`: `bash scripts/trigger-deploy.sh`.
- **`scripts/trigger-deploy.sh`** — only acts when
  `CODEBUILD_WEBHOOK_EVENT == 'PUSH'` and
  `CODEBUILD_WEBHOOK_HEAD_REF == 'refs/heads/master'`; then
  `aws ssm send-command` (`AWS-RunShellScript`) against a fixed EC2 instance id
  running `entrypoint_deploy master api master`. Deploy is fire-and-forget.
- **Runtime containers** via `scripts/run-server.sh <api|worker|scheduler|sch_work>`:
  - `api` -> `manage.py migrate` + `gunicorn --bind 0.0.0.0:8443 api.wsgi -w 3`
  - `worker` -> `celery -A api worker -l info`
  - `scheduler` -> `celery -A api beat -l info`
  - `sch_work` -> `celery -A api worker -B -l info` (beat + worker in one)
- **`.dockerignore`**: `.git`, `env`, `celerybeat-schedule`. No `Dockerfile` is
  checked in.
- **Git workflow (from history):** feature branches (`feature/...`), PRs merged to
  `develop`, then `develop` -> `master` merge PRs; push to `master` triggers the
  deploy. Recent work: SQS notification publishing (#91-93), CodeBuild config
  (#90), loan rate logic (#95).
- **`scripts/list_latest_packages.py`** — ad-hoc helper that queries PyPI for the
  latest version of every package in `requirements.txt` (dependency-bump aid).

---

## Conventions cheat-sheet

- Indentation is **mixed**: tabs in `models.py`, `serializers.py`,
  `services/loan.py`, `services/user.py`, most `tests/`; 4-space in `views/`,
  `permissions.py`, newer services (`activity.py`, `saving_account.py`,
  `notification.py`), `admin.py` uses 2-space. Match the file you're editing.
- URLconf uses the deprecated `django.conf.urls.url` regex style throughout.
- Logging: `logging.getLogger(__name__)`; single root logger -> console at
  `INFO` (`LOGGING` in `base.py`).
- Money is stored as whole-unit `BigIntegerField`; rounding via
  `int(round(float(x), 0))`.
- Choice fields are plain int tuples on the model; code compares against the raw
  ints (`state == 1`), tests use `get_<field>_display()`.
- Service methods return `(success_bool, payload_or_msg)`; views translate to HTTP.
- Dependency injection is manual, constructor-based, with `None` defaults.
- New external integrations are wrapped in a `Service` class under
  `fondo_api/services/`, instantiated at import time in the owning view module.
