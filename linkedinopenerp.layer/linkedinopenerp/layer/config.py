from livesettings import config_register, ConfigurationGroup, StringValue
from django.utils.translation import ugettext_lazy as _


# LINKEDIN APP KEY/SECRET configs
LINKEDIN_INFO = ConfigurationGroup(
    'LINKEDIN_INFO',
    _('LinkedIn info'),
    ordering=0
)

# key
config_register(
    StringValue(
        LINKEDIN_INFO,
        'KEY',
        description=_('Key'),
        help_text="Insert you linkedin app key",
        default="",
    )
)

# secret
config_register(
    StringValue(
        LINKEDIN_INFO,
        'SECRET',
        description=_('Secret'),
        help_text="Insert you linkedin app secret",
        default="",
    )
)

# username
config_register(
    StringValue(
        LINKEDIN_INFO,
        'USERNAME',
        description=_('Usrname'),
        help_text="Insert you linkedin username",
        default="",
    )
)

# password
config_register(
    StringValue(
        LINKEDIN_INFO,
        'PASSWORD',
        description=_('Password'),
        help_text="Insert you linkedin password",
        default="",
    )
)

# callback_url
config_register(
    StringValue(
        LINKEDIN_INFO,
        'CALLBACK_EMPLOYEE',
        description=_('Employee call back url'),
        help_text="Insert you linkedin call back url for employee",
        default="",
    )
)

config_register(
    StringValue(
        LINKEDIN_INFO,
        'CALLBACK_CONTACT',
        description=_('Contact call back url'),
        help_text="Insert you linkedin call back url for contacts",
        default="",
    )
)

# OPENERP configs
OPENERP_INFO = ConfigurationGroup(
    'OPENERP_INFO',
    _('Openerp info'),
    ordering=0
)

# host
config_register(
    StringValue(
        OPENERP_INFO,
        'HOST',
        description=_('Host'),
        help_text="",
        default="127.0.0.1",
    )
)

# port
config_register(
    StringValue(
        OPENERP_INFO,
        'PORT',
        description=_('Port'),
        help_text="",
        default="9169",
    )
)

# dbname
config_register(
    StringValue(
        OPENERP_INFO,
        'DBNAME',
        description=_('Dbname'),
        help_text="",
        default="erp_db",
    )
)

# user
config_register(
    StringValue(
        OPENERP_INFO,
        'USER',
        description=_('Username'),
        help_text="",
        default="admin",
    )
)

# password
config_register(
    StringValue(
        OPENERP_INFO,
        'PASSWORD',
        description=_('Password'),
        help_text="",
        default="admin",
    )
)