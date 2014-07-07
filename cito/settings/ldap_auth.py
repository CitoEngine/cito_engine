# import ldap
# import logging
# from django_auth_ldap.config import LDAPSearch
#
# logger = logging.getLogger('auth_log_handler')
#
# AUTH_LDAP_SERVER_URI = "ldaps://ldap.example.com"
#
# AUTH_LDAP_BIND_DN = ""
# AUTH_LDAP_BIND_PASSWORD = ""
# AUTH_LDAP_USER_SEARCH = LDAPSearch('CN=Users,DC=EXAMPLE,DC=COM', ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)",)
#
#
# AUTHENTICATION_BACKENDS = (
#     'django_auth_ldap.backend.LDAPBackend',
#
# #####################################################
# # Enable ModelBackend only if you wish to use LDAP as well as
# # the CitoEngine's internal DB for authentication
# # ####################################################
# # 'django.contrib.auth.backends.ModelBackend',
# )
