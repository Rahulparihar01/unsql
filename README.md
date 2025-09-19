
> **Step 2** - Start the APP in `Docker`

```bash
$ docker-compose up --build 
```

Visit `http://localhost:5085` in your browser. The app should be up & running.

<br />

## ✨ Create a new `.env` file using sample `env.sample`

The meaning of each variable can be found below: 

- `DEBUG`: if `True` the app runs in develoment mode
  - For production value `False` should be used
- `ASSETS_ROOT`: used in assets management
  - default value: `/static/assets`
- FTP Settings: used by users to upload their profile photo. 
  - `FTP_UPLOAD=True` - enables/disables the FTP upload feature
  - `ftp_username`
  - `ftp_password`
  - `ftp_server_url`
  - `ftp_port`
  - `upload_url`
- `MYSQL` credentials 
  - `DB_ENGINE`, default value = `mysql`
  - `DB_NAME`, default value = `appseed_db`
  - `DB_HOST`, default value = `localhost`
  - `DB_PORT`, default value = `3306`
  - `DB_USERNAME`, default value = `appseed_db_usr`
  - `DB_PASS`, default value = `pass`
- `OAuth` via Github
  - `GITHUB_ID`=<GITHUB_ID_HERE>
  - `GITHUB_SECRET`=<GITHUB_SECRET_HERE> 
- `OAuth` via Twitter
  - `TWITTER_ID`=<TWITTER_ID_HERE>
  - `TWITTER_SECRET`=<TWITTER_SECRET_HERE> 

<br />

## ✨ Manual Build

> Download and unzip the sources

```bash
$ cd django-soft-ui-dashboard-pro
```

<br />

### 👉 Set Up for `Unix`, `MacOS` 

> Install modules via `VENV`  

```bash
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

<br />

> Set Up Database

```bash
$ python manage.py makemigrations
$ python manage.py makemigrations accounts
$ python manage.py makemigrations authentication
$ python manage.py migrate
```

<br />

> Start the app

```bash
$ python manage.py runserver
// OR with https
$ python manage.py runsslserver 
```

At this point, the app runs at `http://127.0.0.1:8000/`. 

<br />

### 👉 Set Up for `Windows` 

> Install modules via `VENV` (windows) 

```
$ virtualenv env
$ .\env\Scripts\activate
$ pip3 install -r requirements.txt
```

<br />

> Set Up Database

```bash
$ python manage.py makemigrations
$ python manage.py makemigrations accounts
$ python manage.py makemigrations authentication
$ python manage.py migrate
```

<br />

> Start the app

```bash
$ python manage.py runserver
// OR with https
$ python manage.py runsslserver 
```

At this point, the app runs at `http://127.0.0.1:8000/`. 

<br />

## ✨ Create Users

By default, the app redirects guest users to authenticate. In order to access the private pages, follow this set up: 

- Start the app:
  - `$ python manage.py runserver`
- Access the `registration` page and create a new user:
  - `http://127.0.0.1:8000/register/`
- Access the `sign in` page and authenticate
  - `http://127.0.0.1:8000/login/`

<br />

## ✨ Enable OAuth 

> 👉 **Github Setup** - [Create an OAuth App](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app)

- SignIN to `Github`
- Access `Settings` -> `Developer Settings` -> `OAuth Apps`
- Edit your OAuth App
  - `App Name`
  - `App Description`
  - (mandatory) `HomePage`: `https://localhost:5000`
  - (mandatory) `Authorization   URL`: `https://localhost:5000/login/github/authorized`
  - Generate a new `secret key`

<br />

> 👉 **Twitter Setup** - [Create an OAuth App](https://developer.twitter.com/en/portal/projects-and-apps) 

- SignIN to `Twitter`
- Access `Developer Section` -> https://developer.twitter.com/en/portal/projects-and-apps
- Create a new APP
- Edit User authentication settings
  - Check `OAuth 1.0a`
  - (mandatory) `HomePage`: `https://localhost:5000`
  - (mandatory) `Authorization callback URL`: `https://localhost:5000/login/twitter/authorized`

<br />

> 👉 **Update Environment** - Rename `.env.sample` to `.env` and edit the file

- For GITHUB Login
  - `GITHUB_ID` - value provided by `Github Setup`
  - `GITHUB_SECRET` - value provided by `Github Setup`
- For TWitter Login
  - `TWITTER_ID` - value provided by `Twitter Setup`
  - `TWITTER_SECRET` - value provided by `Twitter Setup`

<br />

> 👉 **Start the project** Using HTTPS 

```bash
$ python manage.py runsslserver 
$
$ # Access the app: https://127.0.0.1:5000/
```

<br />

## ✨ Code-base structure

The project is coded using a simple and intuitive structure presented below:

```bash
< PROJECT ROOT >
   |
   |-- core/                               # Implements app configuration
   |    |-- settings.py                    # Defines Global Settings
   |    |-- wsgi.py                        # Start the app in production
   |    |-- urls.py                        # Define URLs served by all apps/nodes
   |
   |-- apps/
   |    |
   |    |-- home/                          # A simple app that serve HTML files
   |    |    |-- views.py                  # Serve HTML pages for authenticated users
   |    |    |-- urls.py                   # Define some super simple routes  
   |    |
   |    |-- authentication/                # Handles auth routes (login and register)
   |    |    |-- urls.py                   # Define authentication routes  
   |    |    |-- views.py                  # Handles login and registration  
   |    |    |-- forms.py                  # Define auth forms (login and register) 
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>         # CSS files, Javascripts files
   |    |
   |    |-- templates/                     # Templates used to render pages
   |         |-- includes/                 # HTML chunks and components
   |         |    |-- navigation.html      # Top menu component
   |         |    |-- sidebar.html         # Sidebar component
   |         |    |-- footer.html          # App Footer
   |         |    |-- scripts.html         # Scripts common to all pages
   |         |
   |         |-- layouts/                   # Master pages
   |         |    |-- base-fullscreen.html  # Used by Authentication pages
   |         |    |-- base.html             # Used by common pages
   |         |
   |         |-- accounts/                  # Authentication pages
   |         |    |-- login.html            # Login page
   |         |    |-- register.html         # Register page
   |         |
   |         |-- home/                      # UI Kit Pages
   |              |-- index.html            # Index page
   |              |-- 404-page.html         # 404 page
   |              |-- *.html                # All other pages
   |
   |-- requirements.txt                     # Development modules - SQLite storage
   |
   |-- .env                                 # Inject Configuration via Environment
   |-- manage.py                            # Start the app - Django default start script
   |
   |-- ************************************************************************
```

<br />

---
[Soft UI Dashboard PRO Django](https://appseed.us/product/soft-ui-dashboard-pro/django/) - Starter generated by **[AppSeed Generator](https://appseed.us/generator/)**.





#### Push to ECR

#Retrieve an authentication token and authenticate your Docker client to your registry.
Use the AWS CLI:

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 270214493806.dkr.ecr.us-east-1.amazonaws.com

# Note: If you receive an error using the AWS CLI, make sure that you have the latest version of the AWS CLI and Docker installed.
# Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here . You can skip this step if your image is already built:

docker build -t querygrunt-prod .
# or when deploying from arm device
(old) docker build --platform linux/amd64 -t querygrunt-prod .
(update) docker build --platform linux/amd64 -f Dockerfile.prod -t querygrunt-prod .

# After the build completes, tag your image so you can push the image to this repository:

docker tag querygrunt-prod:latest 270214493806.dkr.ecr.us-east-1.amazonaws.com/querygrunt-prod:latest

# Run the following command to push this image to your newly created AWS repository:

docker push 270214493806.dkr.ecr.us-east-1.amazonaws.com/querygrunt-prod:latest


## Running Locally
docker build -t querygrunt-local . 
docker run -p 80:80 querygrunt-local

navigate to localhost
localhost is an approved callback for auth0 dev

## Running locally, with prod credentials
docker build -f Dockerfile.prod -t querygrunt-prod .

```
az login
```

Build and run on mac:
```
docker buildx build --platform linux/arm64 -f Dockerfile.prod -t unsql.azurecr.io/unsql:dec17v3-mac .
docker run -p 80:80  -e POSTGRES_DB=postgres unsql.azurecr.io/unsql:dec17v3-mac
```


Build and push to Azure Container Registry
```
docker buildx build --platform linux/amd64 -f Dockerfile.prod -t unsql.azurecr.io/unsql:dec17v3-multi .
docker push unsql.azurecr.io/unsql:dec17v3-multi
az containerapp update --name unsql-app --resource-group rg-sarthak1995ai \
    --image unsql.azurecr.io/unsql:dec17v3-multi \
    --cpu 4 --memory 8.0Gi
```

See container logs:
```
az containerapp logs show --name unsql-app --resource-group rg-sarthak1995ai
```