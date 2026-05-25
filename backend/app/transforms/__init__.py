from app.transforms.registry import registry
from app.transforms.phone.phoneinfoga import PhoneInfogaTransform
from app.transforms.phone.platform_checker import PlatformRegistrationTransform
from app.transforms.phone.cnam_lookup import CNAMLookupTransform
from app.transforms.phone.leak_check import LeakCheckTransform
from app.transforms.phone.social_linker import SocialProfileLinkerTransform
from app.transforms.general.username_search import UsernameSearchTransform
from app.transforms.general.email_osint import EmailOSINTTransform
from app.transforms.general.ip_domain_intel import IPDomainIntelTransform
from app.transforms.general.google_dorking import GoogleDorkingTransform
from app.transforms.general.social_graph import SocialGraphExpansionTransform

for cls in [
    PhoneInfogaTransform,
    PlatformRegistrationTransform,
    CNAMLookupTransform,
    LeakCheckTransform,
    SocialProfileLinkerTransform,
    UsernameSearchTransform,
    EmailOSINTTransform,
    IPDomainIntelTransform,
    GoogleDorkingTransform,
    SocialGraphExpansionTransform,
]:
    registry.register(cls())  # type: ignore[abstract]
