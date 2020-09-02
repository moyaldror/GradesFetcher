# GradesFetcher

## What is it?
Crawler to extract grades from the **The Open University of Israel** grades system and notify whenever a new grade is present.

## Screenshot of some updates
![alt text](/images/sample.jpg "Example")

## But why?
The current university system updates regarding new grades 1-2 days after they are available and I find myself constantly checking the grading system to see if new grades are present (especially test grades).
I also don't like the fact that the grades are scattered all over the places and prefer to have a small DB with all the grades from all my courses.

## How does it work?
The harnesses the power of [Github Actions](https://github.com/features/actions) to run a periodic check of grades.

## How to use it?
### Step 1 - **REQUIRED** - Fork this repository:
This repository contains everything needed for the fetcher to work automatically - just fork it and follow the next steps.

### Step 2 - **REQUIRED** - Change **config.yaml**:
The configuration file [config.yaml](/config.yaml) contains (at this moment) only which courses to fetch.
    
Syntax examples:
+ Fetch 3 courses using the course number:
```yaml
courses:
    - '22913'
    - '22923'
    - '20574'
```
+ Fetch all courses available:
```yaml
courses:
    - '*'
```
### Step 3 - **REQUIRED** - Add relevant secrets to your forked repository:
The fetch script needs to use the user credentials in order to connect to the university site and to send notifications using [Telegram bot](https://core.telegram.org/bots).

To do so without exposing the credentials it uses [Github Actions Secrets](https://docs.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets).

The following secrets need to be added to the forked repository:
1. **AUTH_TOKEN**: </br>
    Github authentication token - used to manage workflow artifacts. </br>
    Follow this [instructions](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to generate one.
2. **BOT_TOKEN**: </br>
    Token id of a telegram bot. </br>
    Follow this [instructions](https://core.telegram.org/bots#6-botfather) to create a telegram bot.
3. **CHAT_ID**: </br>
    Telegram chat id between you and your bot. To get the chat id, send your bot a message and use the following link to get the chat id -
    `https://api.telegram.org/bot<YourBotToken>/getUpdates`.
4. **DB_PASSWORD**: </br>
    To provide persistency between workflow runs and for other usages you may find (like creating your own custom dashboard of all your grades), the DB is stored as an *artifact*. Because this data is private it is password protected.
5. **USER_NAME**: </br>
    Username used to connect to *Sheilta*.
6. **PASSWORD**: </br>
    Password used to connect to *Sheilta*.
7. **ID_NUMBER**: </br>
    Your ID Number.

### Step 4 - **OPTIONAL** - Change the interval between fetches:
The auto-update workflow is configured to run every day, every hour between 07:00-20:00.

You can change it [python-app.yml](.github/workflows/python-app.yml) by updating the `schedule` part at the beginning of the file.

### Step 5 - **REQUIRED** - Enable the workflow on your forked repository:
1. Enable actions in your repository. Navigate to the actions tab and enable them:
![alt text](/images/actions.jpg "Enable Actions")
2. Remove the first line of [python-app.yml](.github/workflows/python-app.yml) and push it to your repository.

### Step 6 - **REQUIRED** - Enjoy your updates :)
