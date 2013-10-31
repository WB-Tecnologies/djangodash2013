# django-clients-support

Project for [DjangoDash 2013](http://djangodash.com/). Team - [WB-Tech](http://djangodash.com/teams/c4/wb-tech/).

[Demo page](http://146.185.149.139/) is available.

Administrator credentials:

-  login: `djangodash`
-  password: `123123`

*django-clients-support* is a django app that provide users support functionality.

_Futures_:

-  Handy client interface
-  Real-Time update of tickets statuses
-  Tickets filtration by themes and tags
-  Public tickets list (auto generated FAQ section)
-  Customers satisfaction rating
-  Statistics
-  Django-admin integration
-  Easy customization

## Installation

`pip install -e git+git@github.com:WB-Tecnologies/djangodash2013.git#egg=clients_support`

Add `clients_support` and `autocomplete_light` to `INSTALLED_APPS`.

In urls.py, call autocomplete_light.autodiscover() before admin.autodiscover().

Include following templates in your layout:

-  `clients_support/head.html` - to HEAD section.
-  `clients_support/body.html` - to end of BODY section.

Add following to your `urls.py`:

```python
from clients_support.urls import clients_support_urls

urlpatterns = patterns('',
    ...
)

urlpatterns += clients_support_urls()
```