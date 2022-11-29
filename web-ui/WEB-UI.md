# Courts Info Service :: Web UI Module

The main project [README.md](../README.md) file.
Project's [TODO.md](../TODO.md) items.

## Useful Tech Resources

- [JS Data Tables](https://datatables.net/)
- [Web Site Favicon Creation](https://favicon.io/)
- ???

## Hosting [REG.RU](https://reg.ru) helping resources/articles

- [Adding Domains / Subdomains](https://help.reg.ru/support/hosting/privyazka-domena-k-hostingu/poddomeny)
- [SSH connect to hosting](https://help.reg.ru/support/hosting/dostupy-i-podklyucheniye-panel-upravleniya-ftp-ssh/rabota-po-ssh-na-virtualnom-hostinge)
- [Django Setup on the hosting](https://help.reg.ru/support/hosting/php-asp-net-i-skripty/kak-ustanovit-django-na-hosting)
- [???](link)
- [???](link)

## Web UI Modules Structure

- **[module]** - ???
- **[module]** - ???
- **[module]** - ???
- **[module]** - ???
- **[module]** - ???

## DB description

Web site uses main DB in read-only mode - no writes to actual tables. Also site uses it's own tables for authentication and tech purposes (see django and it's extensions docs).

### Actual Courts Data tables

- dm_v_court_cases - main table with courts data.
- dm_v_court_stats - common statistics for the datamart - # of cases in the system and, telegram bot uses it in answer for /status request.
- dm_v_court_case_stats_detail - statistical data for various courts.
