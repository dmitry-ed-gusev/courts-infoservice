# Courts Info Service :: Web UI Module

The main project [README.md](../README.md) file.
Project's [TODO.md](../TODO.md) items.

## Useful Tech Resources and Articles

### Tech Resources

- [JS Data Tables](https://datatables.net/)
- [Web Site Favicon Creation](https://favicon.io/)
- [Configuring Django settings](https://djangostars.com/blog/configuring-django-settings-best-practices/)
- [django-environ](https://github.com/joke2k/django-environ)
- [django-environ docs](https://django-environ.readthedocs.io/en/latest/index.html)
- [django sql queries logging](https://coderwall.com/p/uzhyca/quickly-setup-sql-query-logging-django)
- [determine if django run on dev](https://stackoverflow.com/questions/12027545/determine-if-django-is-running-under-the-development-server)
- [django secret key generator](https://djecrety.ir/)
- [how to gen django secret key](https://www.educative.io/answers/how-to-generate-a-django-secretkey)

### Hosting [REG.RU](https://reg.ru) Resources

- [Adding Domains / Subdomains](https://help.reg.ru/support/hosting/privyazka-domena-k-hostingu/poddomeny)
- [SSH connect to hosting](https://help.reg.ru/support/hosting/dostupy-i-podklyucheniye-panel-upravleniya-ftp-ssh/rabota-po-ssh-na-virtualnom-hostinge)
- [Django Setup on the hosting](https://help.reg.ru/support/hosting/php-asp-net-i-skripty/kak-ustanovit-django-na-hosting)
- ???

## Deployment to hosting REG.RU

Before deployment, chech this [django deployment checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/)!  

The following steps should be done before deployment as well:

1. Generate ssh key public/private pair - see example here: [ssh.com](https://www.ssh.com/academy/ssh/keygen)
2. Use command `ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>` for copying the public key to the target host (see article above)
3. Use script []() for deployment the site source to hosting.

### Copy files to/from remote host

sssss

## Web UI Module Structure

- **[module]** - ???
- **[module]** - ???
- **[module]** - ???
- **[module]** - ???
- **[module]** - ???

## Managing Web UI settings

TODO: look here -> [best practices](https://djangostars.com/blog/configuring-django-settings-best-practices/)

## DB Info

Web site uses main DB in read-only mode - no writes to actual tables. Also site uses it's own tables for authentication and tech purposes (see django and it's extensions docs).

### Specify DBMS / Environment to use

- if set environment variable **ENV_PATH** - specified file will be loaded, relative path should be
  used - it will be resolved according to the site root directory. Example:  
  `export ENV_PATH=.env.prod`
- default/fallback option (env variable isn't set) - DBMS config will be loaded from **.env.prod** file in
  the current directory

Example: `ENV_PATH=.env.myenv ./manage.py runserver` uses **BASE_DIR/.env.myenv** config file, while  
  `./manage.py runserver` uses **BASE_DIR/.env.prod** default config file (\${BASE_DIR} - see the site settings.py file - base/root site dir).

One more sample: `export ENV_PATH=.env.local.prod_db; python manage.py check`

Strictly speaking, the environment file will be looked for inside the site's BASE_DIR.

### Inspect existing DB

In order to inspect existing DB and get description in terms of django models. use the following command:  
`python manage.py inspectdb > models.py`  
It is worth executing this command from the virtual environment.

### Actual Courts Data tables

- dm_v_court_cases - main table with courts data.
- dm_v_court_stats - common statistics for the datamart - # of cases in the system and, telegram bot uses it in answer for /status request.
- dm_v_court_case_stats_detail - statistical data for various courts.
