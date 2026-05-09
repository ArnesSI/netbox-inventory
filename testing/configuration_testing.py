#####################################
#                                   #
#   Config used to run unit tests   #
#                                   #
#####################################

ALLOWED_HOSTS = ["*",]

DATABASE = {
    'NAME': 'netbox',         # Database name
    'USER': 'netbox',               # PostgreSQL username
    'PASSWORD': 'netbox',           # PostgreSQL password
    'HOST': 'localhost',      # Database server
    'PORT': '',               # Database port (leave blank for default)
    'CONN_MAX_AGE': 300,      # Max database connection age
}

REDIS = {
    'tasks': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}

SECRET_KEY = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
API_TOKEN_PEPPERS = {
    1: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
}

PLUGINS = [
    'netbox_inventory',
]
