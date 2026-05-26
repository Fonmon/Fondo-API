import json
import copy
import os
from mock import patch, MagicMock
from datetime import datetime
from django.urls import reverse
from rest_framework import status
from decimal import Decimal

from fondo_api.tests.abstract_test import AbstractTest
from fondo_api.models import Loan
from fondo_api.services.alexa.amazon_alexa import AmazonAlexa

VIEW_ALEXA = "view_alexa"

class AlexaViewTest(AbstractTest):
    def setUp(self):
        self.env = patch.dict(os.environ, {'AWS_SKILL_ID': 'amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049'})
        self.env.start()
        self.create_user()
        self.token = self.get_token('mail_for_tests@mail.com','password')
        self.launch_object = {
            "version": "1.0",
            "session": {
                "new": True,
                "sessionId": "amzn1.echo-api.session.71cf5112-d7a4-4a5c-9e3a-70a24a4a45b1",
                "application": {
                    "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                },
                "user": {
                    "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                    "accessToken": self.token
                }
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                        "accessToken": "87b7f45a0624abb17df90ad71ba2767b31e0f8e6"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.AG4JX3NVXHX7R6RWZIMUKUYLJC7SSRLZUFGKTJYSMVEHEPB6B2Q4GDPRKHVSU6ORGDMMPHXQT32XYOEBFCUUENNU7YAECBV3YKLJ7N7UIRTQ6YMCIVPR67S536KKQ4GB46T676ZZ3QUOKI5XF2VKZQRYUIP4QKZ22UHAQ4SQTEWAXQHCVLDE6",
                        "supportedInterfaces": {
                            "AudioPlayer": {}
                        }
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjdlMmNjZDcxLWVlMGQtNGI2OS04OGM0LTIzMGQwNzQ5ZDA0OSIsImV4cCI6MTU0NTU4MjY2MCwiaWF0IjoxNTQ1NTc5MDYwLCJuYmYiOjE1NDU1NzkwNjAsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUc0SlgzTlZYSFg3UjZSV1pJTVVLVVlMSkM3U1NSTFpVRkdLVEpZU01WRUhFUEI2QjJRNEdEUFJLSFZTVTZPUkdETU1QSFhRVDMyWFlPRUJGQ1VVRU5OVTdZQUVDQlYzWUtMSjdON1VJUlRRNllNQ0lWUFI2N1M1MzZLS1E0R0I0NlQ2NzZaWjNRVU9LSTVYRjJWS1pRUllVSVA0UUtaMjJVSEFRNFNRVEVXQVhRSENWTERFNiIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFGU0hJMllYV1pQNFZQRVZSTFBCM0NPSDMzVVVaUU5CR1RXR0k3N0c3V1dNNEhPNUhMVkdPUlpYNEFGNVFYVlJIS1NMVFdPSlU3QjM1N1dIUkpLNFZSUUVaSFNNRzNHUU9RWlc2QVVVU0dSQTZQTEhZTllPNTRRQkxSREpOWFJJUjdWSzZWVldXU0tOWUpCSktTN0Q1NlVVSU9HVzNWVzU3RVZUNUpDR09VVUFIQVZJRlVJSUtQNVBRRUVQNDVZMklZV0pBTVFaTUc3UVY2QSJ9fQ.PwtyDB872-JHQgGaN8vvjxWGy8MehROjH8yVYNxJRVysVfvVb_aVCq-79FIn5XLza3iba6_JrlMjyCCiL39M-0V682_Ywy2xRUHxyELz5JrmMc1M9UrYzRcNDtIGEfzJwpw8W_43p0wE2OxrxKSo5hxmuSZ2d82EW2L_RhLejHpywTTssEuyho_KQIo-pI0q7kdAWX2FTIJvssT0Lfa3aeVi01SqMNBdq_akFJU5l3VE5r5-teDziw3uYjmd7H0ZxYoEfBT8D7HV4j4IkT14T5p4E0MemJ5tU5VdEal2Ffb0DOJ98FyKaoOwf8btmM64pqzdbfWV3yimhWUrPY2rKw"
                },
                "Viewport": {
                    "experiences": [
                        {
                            "arcMinuteWidth": 246,
                            "arcMinuteHeight": 144,
                            "canRotate": False,
                            "canResize": False
                        }
                    ],
                    "shape": "RECTANGLE",
                    "pixelWidth": 1024,
                    "pixelHeight": 600,
                    "dpi": 160,
                    "currentPixelWidth": 1024,
                    "currentPixelHeight": 600,
                    "touch": [
                        "SINGLE"
                    ]
                }
            },
            "request": {
                "type": "LaunchRequest",
                "requestId": "amzn1.echo-api.request.5b845b75-5eb0-4213-8584-a966d66b64ff",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "locale": "en-US",
                "shouldLinkResultBeReturned": False
            }
        }
        self.request_loan_intent_object_incomplete = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "amzn1.echo-api.session.71cf5112-d7a4-4a5c-9e3a-70a24a4a45b1",
                "application": {
                    "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                },
                "user": {
                    "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                    "accessToken": self.token
                }
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                        "accessToken": "87b7f45a0624abb17df90ad71ba2767b31e0f8e6"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.AG4JX3NVXHX7R6RWZIMUKUYLJC7SSRLZUFGKTJYSMVEHEPB6B2Q4GDPRKHVSU6ORGDMMPHXQT32XYOEBFCUUENNU7YAECBV3YKLJ7N7UIRTQ6YMCIVPR67S536KKQ4GB46T676ZZ3QUOKI5XF2VKZQRYUIP4QKZ22UHAQ4SQTEWAXQHCVLDE6",
                        "supportedInterfaces": {
                            "AudioPlayer": {}
                        }
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjdlMmNjZDcxLWVlMGQtNGI2OS04OGM0LTIzMGQwNzQ5ZDA0OSIsImV4cCI6MTU0NTU4MjkwMiwiaWF0IjoxNTQ1NTc5MzAyLCJuYmYiOjE1NDU1NzkzMDIsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUc0SlgzTlZYSFg3UjZSV1pJTVVLVVlMSkM3U1NSTFpVRkdLVEpZU01WRUhFUEI2QjJRNEdEUFJLSFZTVTZPUkdETU1QSFhRVDMyWFlPRUJGQ1VVRU5OVTdZQUVDQlYzWUtMSjdON1VJUlRRNllNQ0lWUFI2N1M1MzZLS1E0R0I0NlQ2NzZaWjNRVU9LSTVYRjJWS1pRUllVSVA0UUtaMjJVSEFRNFNRVEVXQVhRSENWTERFNiIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFGU0hJMllYV1pQNFZQRVZSTFBCM0NPSDMzVVVaUU5CR1RXR0k3N0c3V1dNNEhPNUhMVkdPUlpYNEFGNVFYVlJIS1NMVFdPSlU3QjM1N1dIUkpLNFZSUUVaSFNNRzNHUU9RWlc2QVVVU0dSQTZQTEhZTllPNTRRQkxSREpOWFJJUjdWSzZWVldXU0tOWUpCSktTN0Q1NlVVSU9HVzNWVzU3RVZUNUpDR09VVUFIQVZJRlVJSUtQNVBRRUVQNDVZMklZV0pBTVFaTUc3UVY2QSJ9fQ.IMHNDZsnxpDbe3WDi6eAuraj7WldYcen2muyukJ0uST6hWzlEJjht_8f1Mwd_hk_1pnHriySA5QrnQAoTT4C1i0OwTXYXVf3p4Wiss6m86NRSt0Xm69pkjQNZ11EkZEsXl1gVR38S_4EKo6PwAZcKAPCB2gY8ClqDdJi5L3LCKQ7NjQjuv7Jl5gpMCOlCLSNJGU00jeHlSxMd-kSbxIIxtK1dLX--CXp1XmkqjHRmsh_LvPmo1gd--t4GLqKk5C888l_dyjzb1DZLxVaTY4TOwEY27T-2RKNdcEnKdZq55GPV28n3h_rBIykQ86c2uQzVAz7eGNSMbpOsWTvB_Zi2w"
                },
                "Viewport": {
                    "experiences": [
                        {
                            "arcMinuteWidth": 246,
                            "arcMinuteHeight": 144,
                            "canRotate": False,
                            "canResize": False
                        }
                    ],
                    "shape": "RECTANGLE",
                    "pixelWidth": 1024,
                    "pixelHeight": 600,
                    "dpi": 160,
                    "currentPixelWidth": 1024,
                    "currentPixelHeight": 600,
                    "touch": [
                        "SINGLE"
                    ]
                }
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "amzn1.echo-api.request.1c3d05ec-58c6-45ff-a095-96b9fb57e6fc",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "locale": "en-US",
                "intent": {
                    "name": "RequestLoan",
                    "confirmationStatus": "NONE",
                    "slots": {
                        "disbursement_date": {
                            "name": "disbursement_date",
                            "confirmationStatus": "NONE"
                        },
                        "payment": {
                            "name": "payment",
                            "confirmationStatus": "NONE"
                        },
                        "value": {
                            "name": "value",
                            "confirmationStatus": "NONE"
                        },
                        "fee": {
                            "name": "fee",
                            "confirmationStatus": "NONE"
                        },
                        "timelimit": {
                            "name": "timelimit",
                            "confirmationStatus": "NONE"
                        }
                    }
                },
                "dialogState": "STARTED"
            }
        }
        self.request_loan_intent_object_partial_1 = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "amzn1.echo-api.session.66e60a42-80eb-435d-a464-e311e14af87e",
                "application": {
                    "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                },
                "user": {
                    "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                    "accessToken": self.token
                }
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                        "accessToken": "87b7f45a0624abb17df90ad71ba2767b31e0f8e6"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.AG4JX3NVXHX7R6RWZIMUKUYLJC7SSRLZUFGKTJYSMVEHEPB6B2Q4GDPRKHVSU6ORGDMMPHXQT32XYOEBFCUUENNU7YAECBV3YKLJ7N7UIRTQ6YMCIVPR67S536KKQ4GB46T676ZZ3QUOKI5XF2VKZQRYUIP4QKZ22UHAQ4SQTEWAXQHCVLDE6",
                        "supportedInterfaces": {
                            "AudioPlayer": {}
                        }
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjdlMmNjZDcxLWVlMGQtNGI2OS04OGM0LTIzMGQwNzQ5ZDA0OSIsImV4cCI6MTU0NTU5MTI3MCwiaWF0IjoxNTQ1NTg3NjcwLCJuYmYiOjE1NDU1ODc2NzAsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUc0SlgzTlZYSFg3UjZSV1pJTVVLVVlMSkM3U1NSTFpVRkdLVEpZU01WRUhFUEI2QjJRNEdEUFJLSFZTVTZPUkdETU1QSFhRVDMyWFlPRUJGQ1VVRU5OVTdZQUVDQlYzWUtMSjdON1VJUlRRNllNQ0lWUFI2N1M1MzZLS1E0R0I0NlQ2NzZaWjNRVU9LSTVYRjJWS1pRUllVSVA0UUtaMjJVSEFRNFNRVEVXQVhRSENWTERFNiIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFGU0hJMllYV1pQNFZQRVZSTFBCM0NPSDMzVVVaUU5CR1RXR0k3N0c3V1dNNEhPNUhMVkdPUlpYNEFGNVFYVlJIS1NMVFdPSlU3QjM1N1dIUkpLNFZSUUVaSFNNRzNHUU9RWlc2QVVVU0dSQTZQTEhZTllPNTRRQkxSREpOWFJJUjdWSzZWVldXU0tOWUpCSktTN0Q1NlVVSU9HVzNWVzU3RVZUNUpDR09VVUFIQVZJRlVJSUtQNVBRRUVQNDVZMklZV0pBTVFaTUc3UVY2QSJ9fQ.AiZWUcj0jkL2lKDZUH_ZFofJ4FCks_la4UQ53P24re5-p9F-PDvey4tm3qnTsIjV5t7fYtD447oU7oNDeIkwn0xAS-dmPV2S-vSC7MA1CIGKZl9hLyu_eOfVSF2trjdJwXdkMPUX4N6aNgc1QpvtpSr-4jKiHEPc39hX4kg6bjgEdrw2yHrpy97UD0yGDtDrk3yAUB1526KP_32JMglbwHsRB1GZDrCjex_W9FwJoLYL5Fi-ghGBOXmJyA0gW7nhB8lnXEKRm4FEt7jBoocep_95LST9faosy4hVxCrAYN35RUBrvnf2g043WpvqH2S7pMRsB56Gfxx4FU9LMvildg"
                },
                "Viewport": {
                    "experiences": [
                        {
                            "arcMinuteWidth": 246,
                            "arcMinuteHeight": 144,
                            "canRotate": False,
                            "canResize": False
                        }
                    ],
                    "shape": "RECTANGLE",
                    "pixelWidth": 1024,
                    "pixelHeight": 600,
                    "dpi": 160,
                    "currentPixelWidth": 1024,
                    "currentPixelHeight": 600,
                    "touch": [
                        "SINGLE"
                    ]
                }
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "amzn1.echo-api.request.d3a28bfa-d2de-4fb1-b020-68d713f02c33",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "locale": "en-US",
                "intent": {
                    "name": "RequestLoan",
                    "confirmationStatus": "NONE",
                    "slots": {
                        "disbursement_date": {
                            "name": "disbursement_date",
                            "value": "2018-12-23",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "payment": {
                            "name": "payment",
                            "value": "cash",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.DeviceType",
                                        "status": {
                                            "code": "ER_SUCCESS_MATCH"
                                        },
                                        "values": [
                                            {
                                                "value": {
                                                    "name": "cash",
                                                    "id": "0"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "value": {
                            "name": "value",
                            "value": "10000",
                            "confirmationStatus": "NONE",
                        },
                        "fee": {
                            "name": "fee",
                            "value": "annual",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.EventType",
                                        "status": {
                                            "code": "ER_SUCCESS_NO_MATCH"
                                        }
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "timelimit": {
                            "name": "timelimit",
                            "value": "?",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        }
                    }
                },
                "dialogState": "IN_PROGRESS"
            }
        }
        self.request_loan_intent_object_partial_2 = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "amzn1.echo-api.session.66e60a42-80eb-435d-a464-e311e14af87e",
                "application": {
                    "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                },
                "user": {
                    "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                    "accessToken": self.token
                }
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                        "accessToken": "87b7f45a0624abb17df90ad71ba2767b31e0f8e6"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.AG4JX3NVXHX7R6RWZIMUKUYLJC7SSRLZUFGKTJYSMVEHEPB6B2Q4GDPRKHVSU6ORGDMMPHXQT32XYOEBFCUUENNU7YAECBV3YKLJ7N7UIRTQ6YMCIVPR67S536KKQ4GB46T676ZZ3QUOKI5XF2VKZQRYUIP4QKZ22UHAQ4SQTEWAXQHCVLDE6",
                        "supportedInterfaces": {
                            "AudioPlayer": {}
                        }
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjdlMmNjZDcxLWVlMGQtNGI2OS04OGM0LTIzMGQwNzQ5ZDA0OSIsImV4cCI6MTU0NTU5MTI3MCwiaWF0IjoxNTQ1NTg3NjcwLCJuYmYiOjE1NDU1ODc2NzAsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUc0SlgzTlZYSFg3UjZSV1pJTVVLVVlMSkM3U1NSTFpVRkdLVEpZU01WRUhFUEI2QjJRNEdEUFJLSFZTVTZPUkdETU1QSFhRVDMyWFlPRUJGQ1VVRU5OVTdZQUVDQlYzWUtMSjdON1VJUlRRNllNQ0lWUFI2N1M1MzZLS1E0R0I0NlQ2NzZaWjNRVU9LSTVYRjJWS1pRUllVSVA0UUtaMjJVSEFRNFNRVEVXQVhRSENWTERFNiIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFGU0hJMllYV1pQNFZQRVZSTFBCM0NPSDMzVVVaUU5CR1RXR0k3N0c3V1dNNEhPNUhMVkdPUlpYNEFGNVFYVlJIS1NMVFdPSlU3QjM1N1dIUkpLNFZSUUVaSFNNRzNHUU9RWlc2QVVVU0dSQTZQTEhZTllPNTRRQkxSREpOWFJJUjdWSzZWVldXU0tOWUpCSktTN0Q1NlVVSU9HVzNWVzU3RVZUNUpDR09VVUFIQVZJRlVJSUtQNVBRRUVQNDVZMklZV0pBTVFaTUc3UVY2QSJ9fQ.AiZWUcj0jkL2lKDZUH_ZFofJ4FCks_la4UQ53P24re5-p9F-PDvey4tm3qnTsIjV5t7fYtD447oU7oNDeIkwn0xAS-dmPV2S-vSC7MA1CIGKZl9hLyu_eOfVSF2trjdJwXdkMPUX4N6aNgc1QpvtpSr-4jKiHEPc39hX4kg6bjgEdrw2yHrpy97UD0yGDtDrk3yAUB1526KP_32JMglbwHsRB1GZDrCjex_W9FwJoLYL5Fi-ghGBOXmJyA0gW7nhB8lnXEKRm4FEt7jBoocep_95LST9faosy4hVxCrAYN35RUBrvnf2g043WpvqH2S7pMRsB56Gfxx4FU9LMvildg"
                },
                "Viewport": {
                    "experiences": [
                        {
                            "arcMinuteWidth": 246,
                            "arcMinuteHeight": 144,
                            "canRotate": False,
                            "canResize": False
                        }
                    ],
                    "shape": "RECTANGLE",
                    "pixelWidth": 1024,
                    "pixelHeight": 600,
                    "dpi": 160,
                    "currentPixelWidth": 1024,
                    "currentPixelHeight": 600,
                    "touch": [
                        "SINGLE"
                    ]
                }
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "amzn1.echo-api.request.d3a28bfa-d2de-4fb1-b020-68d713f02c33",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "locale": "en-US",
                "intent": {
                    "name": "RequestLoan",
                    "confirmationStatus": "NONE",
                    "slots": {
                        "disbursement_date": {
                            "name": "disbursement_date",
                            "value": "2018-12-23",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "payment": {
                            "name": "payment",
                            "value": "cash",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.DeviceType",
                                        "status": {
                                            "code": "ER_SUCCESS_MATCH"
                                        },
                                        "values": [
                                            {
                                                "value": {
                                                    "name": "cash",
                                                    "id": "0"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "value": {
                            "name": "value",
                            "value": "10000",
                            "confirmationStatus": "NONE",
                        },
                        "fee": {
                            "name": "fee",
                            "value": "unique",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.EventType",
                                        "status": {
                                            "code": "ER_SUCCESS_MATCH"
                                        },
                                        "values": [
                                            {
                                                "value": {
                                                    "name": "unique",
                                                    "id": "1"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "timelimit": {
                            "name": "timelimit",
                            "value": "?",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        }
                    }
                },
                "dialogState": "IN_PROGRESS"
            }
        }
        self.request_loan_intent_object_complete = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "amzn1.echo-api.session.8ceb6d6d-c2f6-4726-97f1-7e8811c0012b",
                "application": {
                    "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                },
                "user": {
                    "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                    "accessToken": self.token
                }
            },
            "context": {
                "AudioPlayer": {
                    "playerActivity": "IDLE"
                },
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.AFSHI2YXWZP4VPEVRLPB3COH33UUZQNBGTWGI77G7WWM4HO5HLVGORZX4AF5QXVRHKSLTWOJU7B357WHRJK4VRQEZHSMG3GQOQZW6AUUSGRA6PLHYNYO54QBLRDJNXRIR7VK6VVWWSKNYJBJKS7D56UUIOGW3VW57EVT5JCGOUUAHAVIFUIIKP5PQEEP45Y2IYWJAMQZMG7QV6A",
                        "accessToken": "87b7f45a0624abb17df90ad71ba2767b31e0f8e6"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.AG4JX3NVXHX7R6RWZIMUKUYLJC7SSRLZUFGKTJYSMVEHEPB6B2Q4GDPRKHVSU6ORGDMMPHXQT32XYOEBFCUUENNU7YAECBV3YKLJ7N7UIRTQ6YMCIVPR67S536KKQ4GB46T676ZZ3QUOKI5XF2VKZQRYUIP4QKZ22UHAQ4SQTEWAXQHCVLDE6",
                        "supportedInterfaces": {
                            "AudioPlayer": {}
                        }
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjdlMmNjZDcxLWVlMGQtNGI2OS04OGM0LTIzMGQwNzQ5ZDA0OSIsImV4cCI6MTU0NTU5MzU4OSwiaWF0IjoxNTQ1NTg5OTg5LCJuYmYiOjE1NDU1ODk5ODksInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUc0SlgzTlZYSFg3UjZSV1pJTVVLVVlMSkM3U1NSTFpVRkdLVEpZU01WRUhFUEI2QjJRNEdEUFJLSFZTVTZPUkdETU1QSFhRVDMyWFlPRUJGQ1VVRU5OVTdZQUVDQlYzWUtMSjdON1VJUlRRNllNQ0lWUFI2N1M1MzZLS1E0R0I0NlQ2NzZaWjNRVU9LSTVYRjJWS1pRUllVSVA0UUtaMjJVSEFRNFNRVEVXQVhRSENWTERFNiIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFGU0hJMllYV1pQNFZQRVZSTFBCM0NPSDMzVVVaUU5CR1RXR0k3N0c3V1dNNEhPNUhMVkdPUlpYNEFGNVFYVlJIS1NMVFdPSlU3QjM1N1dIUkpLNFZSUUVaSFNNRzNHUU9RWlc2QVVVU0dSQTZQTEhZTllPNTRRQkxSREpOWFJJUjdWSzZWVldXU0tOWUpCSktTN0Q1NlVVSU9HVzNWVzU3RVZUNUpDR09VVUFIQVZJRlVJSUtQNVBRRUVQNDVZMklZV0pBTVFaTUc3UVY2QSJ9fQ.BvdSZy36CSyZ85g0HOrFAMz04gb8Ik3rFFZpAZLLmAn_O9g_gfqKJYmgBhvfOZqhaapfVhwYH7ZYf_DbDs22qcf_5PUDG6EegOUDXno8X-GgUTIvDuPj-CkeVB_boEhf6Vx7_o6jPViVif5_IzKOQ9WxXwBHcVWPK_sG7Nh5AtHjXgw7KkA_rg-XsaGemy5rxgIkhbxib9z1xvQsNxn30wCk4s9oBoga-JPYTpkNWeUksElDXEgCVnUyZZqzBfNi212f1yqTZ-z5fP6ApYPwYWBFffoC1LHtpaiPoCiWpLO3i72n6AyoZmq74ZvideN1nuPJByHaTcCmWnhrL2ORGQ"
                },
                "Viewport": {
                    "experiences": [
                        {
                            "arcMinuteWidth": 246,
                            "arcMinuteHeight": 144,
                            "canRotate": False,
                            "canResize": False
                        }
                    ],
                    "shape": "RECTANGLE",
                    "pixelWidth": 1024,
                    "pixelHeight": 600,
                    "dpi": 160,
                    "currentPixelWidth": 1024,
                    "currentPixelHeight": 600,
                    "touch": [
                        "SINGLE"
                    ]
                }
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "amzn1.echo-api.request.bc71b88e-3048-43eb-819d-21574d96b7a6",
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "locale": "en-US",
                "intent": {
                    "name": "RequestLoan",
                    "confirmationStatus": "NONE",
                    "slots": {
                        "disbursement_date": {
                            "name": "disbursement_date",
                            "value": "2018-12-23",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "payment": {
                            "name": "payment",
                            "value": "cash",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.DeviceType",
                                        "status": {
                                            "code": "ER_SUCCESS_MATCH"
                                        },
                                        "values": [
                                            {
                                                "value": {
                                                    "name": "cash",
                                                    "id": "0"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "value": {
                            "name": "value",
                            "value": "100",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "disbursement_value": {
                            "name": "disbursement_value",
                            "value": "105",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "fee": {
                            "name": "fee",
                            "value": "unique",
                            "resolutions": {
                                "resolutionsPerAuthority": [
                                    {
                                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.ZZZZZ-ee0d-4b69-YYYY-LKJOIU49d049.AMAZON.EventType",
                                        "status": {
                                            "code": "ER_SUCCESS_MATCH"
                                        },
                                        "values": [
                                            {
                                                "value": {
                                                    "name": "unique",
                                                    "id": "1"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        },
                        "timelimit": {
                            "name": "timelimit",
                            "value": "7",
                            "confirmationStatus": "NONE",
                            "source": "USER"
                        }
                    }
                },
                "dialogState": "IN_PROGRESS"
            }
        }
    
    def tearDown(self):
        self.env.stop()

    def _get_alexa_headers(self):
        return {
            "HTTP_SIGNATURECERTCHAINURL": "https://s3.amazonaws.com/echo.api/echo-api-cert-6-ats.pem",
            "HEDAER_SIGNATURE": ""
        }

    def test_wrong_object(self):
        request_obj = copy.copy(self.launch_object)
        request_obj.pop('request')
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_invalid_token(self):
        request_obj = copy.copy(self.launch_object)
        request_obj['session']['user']['accessToken'] = '87b7f45a0624abb17df90ad71ba2767b31e0f8e6'
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_timestamp(self):
        request_obj = copy.copy(self.launch_object)
        request_obj['request']['timestamp'] = "2018-12-20T15:31:00Z"
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_url_signature(self):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.launch_object),
            content_type = 'application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_invalid_alexa_skill_id(self, mock):
        request_obj = copy.copy(self.launch_object)
        request_obj['session']['application']['applicationId'] = "XXXXXXX"
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.launch_object),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_launch(self, mock):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.launch_object),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertIn('outputSpeech', response.data['response'])
        self.assertIn('type', response.data['response']['outputSpeech'])
        self.assertIn('text', response.data['response']['outputSpeech'])
        self.assertEqual(response.data['response']['outputSpeech']['type'], 'PlainText')
        self.assertEqual(response.data['response']['outputSpeech']['text'], 'Welcome to family Montañez fund assistant, what can I help you?')
        self.assertIn('card', response.data['response'])
        self.assertIn('type', response.data['response']['card'])
        self.assertIn('title', response.data['response']['card'])
        self.assertIn('text', response.data['response']['card'])
        self.assertIn('image', response.data['response']['card'])
        self.assertEqual(response.data['response']['card']['type'], 'Standard')
        self.assertEqual(response.data['response']['card']['title'], 'Fonmon Voice Assistant')
        self.assertEqual(response.data['response']['card']['text'], 'Family assistant for recurring tasks')
        self.assertIn('smallImageUrl', response.data['response']['card']['image'])
        self.assertIn('largeImageUrl', response.data['response']['card']['image'])
        self.assertEqual(response.data['response']['card']['image']['smallImageUrl'], 'https://None/static/banner.png')
        self.assertEqual(response.data['response']['card']['image']['largeImageUrl'], 'https://None/static/banner.png')
        self.assertIn('directives', response.data['response'])
        self.assertEqual(len(response.data['response']['directives']), 0)
        self.assertIn('shouldEndSession', response.data['response'])
        self.assertFalse(response.data['response']['shouldEndSession'])

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_request_type_not_found(self, mock):
        request_obj = copy.copy(self.launch_object)
        request_obj['request']['type'] = "NotExists"
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_intent_not_allowed(self, mock):
        request_obj = copy.copy(self.request_loan_intent_object_incomplete)
        request_obj['request']['intent']['name'] = 'XXXXX'
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_request_loan_intent_incomplete(self, mock):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.request_loan_intent_object_incomplete),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertIn('directives', response.data['response'])
        self.assertIn('shouldEndSession', response.data['response'])
        self.assertEqual(len(response.data['response']['directives']), 1)
        self.assertEqual(response.data['response']['directives'][0]['type'], 'Dialog.Delegate')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['name'], 'RequestLoan')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['name'], 'disbursement_date')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['name'], 'payment')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['name'], 'value')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['name'], 'fee')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['name'], 'timelimit')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['confirmationStatus'], 'NONE')
        self.assertFalse(response.data['response']['shouldEndSession'])

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_request_loan_intent_partial_1(self, mock):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.request_loan_intent_object_partial_1),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertIn('directives', response.data['response'])
        self.assertIn('shouldEndSession', response.data['response'])
        self.assertEqual(len(response.data['response']['directives']), 1)
        self.assertEqual(response.data['response']['directives'][0]['type'], 'Dialog.Delegate')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['name'], 'RequestLoan')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['name'], 'disbursement_date')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['value'], '2018-12-23')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['name'], 'payment')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['value'], 'cash')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['name'], 'value')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['name'], 'fee')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['confirmationStatus'], 'NONE')
        self.assertNotIn('resolutions', response.data['response']['directives'][0]['updatedIntent']['slots']['fee'])
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['name'], 'timelimit')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['confirmationStatus'], 'NONE')
        self.assertFalse(response.data['response']['shouldEndSession'])

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_request_loan_intent_partial_2(self, mock):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.request_loan_intent_object_partial_2),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertIn('directives', response.data['response'])
        self.assertIn('shouldEndSession', response.data['response'])
        self.assertEqual(len(response.data['response']['directives']), 1)
        self.assertEqual(response.data['response']['directives'][0]['type'], 'Dialog.Delegate')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['name'], 'RequestLoan')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['name'], 'disbursement_date')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['disbursement_date']['value'], '2018-12-23')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['name'], 'payment')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['payment']['value'], 'cash')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['name'], 'value')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['value']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['name'], 'fee')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['confirmationStatus'], 'NONE')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['fee']['value'], 'unique')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['name'], 'timelimit')
        self.assertEqual(response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit']['confirmationStatus'], 'NONE')
        self.assertNotIn('value', response.data['response']['directives'][0]['updatedIntent']['slots']['timelimit'])
        self.assertFalse(response.data['response']['shouldEndSession'])

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_request_loan_intent_complete_1(self, mock):
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(self.request_loan_intent_object_complete),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertIn('directives', response.data['response'])
        self.assertIn('shouldEndSession', response.data['response'])
        self.assertEqual(len(response.data['response']['directives']), 1)
        self.assertEqual(response.data['response']['directives'][0]['type'], 'Dialog.Delegate')
        propCount = 0
        for prop in response.data['response']['directives']:
            propCount += 1
        self.assertEqual(propCount, 1)
        self.assertFalse(response.data['response']['shouldEndSession'])

    @patch.object(AmazonAlexa, 'verify_signature')
    def test_process_request_loan_intent_complete_2(self, mock):
        request_obj = copy.copy(self.request_loan_intent_object_complete)
        request_obj['request']['dialogState'] = 'COMPLETED'
        response = self.client.post(
            reverse(VIEW_ALEXA),
            data = json.dumps(request_obj),
            content_type = 'application/json',
            **self._get_alexa_headers()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('response', response.data)
        self.assertEqual(response.data['version'], "1.0")
        self.assertEqual(response.data['response']['outputSpeech']['type'], 'PlainText')
        self.assertEqual(response.data['response']['outputSpeech']['ssml'], '')
        loan_id = response.data['response']['outputSpeech']['text'].split(' ')[-1]
        self.assertEqual(response.data['response']['outputSpeech']['text'], f'Loan has been created successfully, its number is {loan_id}')
        self.assertEqual(response.data['response']['card']['type'], 'Standard')
        self.assertEqual(response.data['response']['card']['title'], 'Request a loan')
        self.assertEqual(response.data['response']['card']['content'], '')
        self.assertEqual(response.data['response']['card']['text'], f'Loan has been created successfully, its number is {loan_id}')
        self.assertEqual(response.data['response']['card']['image']['smallImageUrl'], 'https://None/static/banner.png')
        self.assertEqual(response.data['response']['card']['image']['largeImageUrl'], 'https://None/static/banner.png')
        self.assertEqual(response.data['response']['reprompt'], None)
        self.assertTrue(response.data['response']['shouldEndSession'])
        self.assertEqual(len(response.data['response']['directives']), 0)

        loan = Loan.objects.get(id = loan_id)
        self.assertEqual(loan.value, 100)
        self.assertEqual(loan.get_fee_display(),'UNIQUE')
        self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')
        self.assertEqual(loan.rate,Decimal(0.020).quantize(self.THREEPLACES))
        self.assertEqual(loan.disbursement_date.year, 2018)
        self.assertEqual(loan.disbursement_date.month, 12)
        self.assertEqual(loan.disbursement_date.day, 23)
        self.assertEqual(loan.comments,'Loan requested by Alexa Skill')
        self.assertEqual(loan.payment,0)
        self.assertEqual(loan.get_payment_display(),'CASH')
        self.assertEqual(loan.timelimit, 7)
        self.assertEqual(loan.disbursement_value, 105)