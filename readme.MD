# AIR Function Template

Before proceeding make sure all necessary [onboarding steps](https://cognitedata.atlassian.net/wiki/spaces/AIR/pages/1910407214/Onboarding+to+AIR) are done. 

### Installation steps
1.  To use this repo as a template create a new repo and use air-template under templates.
2.  Install poetry in your terminal of choice.
3. `poetry install`: Run this cmd in terminal.
4. `poetry run pre-commit install`: This installs the required pre-commit hooks.

(For more information checkout the [Python Developer Hub](https://github.com/cognitedata/python-developer-hub/tree/master/tutorials).)

(For more information checkout the [Python Developer Hub](https://github.com/cognitedata/python-developer-hub/tree/master/tutorials).)

### Setting up Github secrets 
1. This repo makes use of GitHub Actions to perform deployment and testing of your model.
2. The air-demo-repo template requires the following secrets to be [defined in GitHub](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets) (Settings >> Secrets):
    
    a) PROJECT_NAME_API_KEY: This is your api key for the project in question . For example an API key for eureka tad dev would be defned as EUREKA_TAD_DEV_API_KEY.
    
Please make sure that your api key has the correct permissions required to use Cognite Functions and AIR. It's a good idea to use the api key generated in the [onboarding steps](https://cognitedata.atlassian.net/wiki/spaces/AIR/pages/1910407214/Onboarding+to+AIR).

### Creating a Model
(Find all documentation here: [https://cog.link/air-documentation](https://cog.link/air-documentation))

0. Create a new development branch with `git checkout -b your_branch_name`

1. Any function in this repo needs to have it's own folder in the `functions` folder. For getting started feel free to rename and edit the existing `templatefunction`. 

2. Edit the `config.yaml`. This file is handling the interaction with the AIR Infrastructure and Front End. Read more about it [here](https://cog.link/air-config-yaml).

3. When using AIR, it is encouraged to use the AIR client to get all the benefits of retrieving information about [schedules](https://cog.link/air-docs-schedules), writing [versioned](https://cog.link/air-docs-versioning) [Time Series](https://cog.link/air-docs-versionedts) and [Events](https://cog.link/air-docs-alerts), [notifications to the end user](https://cog.link/air-docs-alerts), and [visualize calculated Time Series](https://cog.link/air-docs-visualizecalculated-ts) in the Front End. Additionally, 
AIR is using Cognite Functions which is documented [here](https://cognitedata.atlassian.net/wiki/spaces/datastudio/pages/1582171375/FAQ+on+Functions).

4. Add all required libraries for your function to the `requirements.txt` file. Please make sure to add the air-sdk library to the requirements for every project. Additionally, install all packages to poetry as well since those are needed for unit and integration tests.

5. Navigate to the repoconfig.yaml file in the root folder and under the project properties tab make sure to add a mapping value as follows `PROJECT_NAME: [PROJECT_URL, "PROJECT_NAME_API_KEY"]`. Under the ProjectFunctionMap write the name of the function that needs to be deployed as well as the project you wish to deploy to.

6. Testing can be done by making use of a test handler under the test folder in your `function_name` folder.

7. If an existing function should not be deployed, the folder name needs to be added to the `.ignore_models` file.

8. Once the function is ready, add, commit and push it to open a pull request.

### Troubleshooting

1. If an error pops up in github actions which states that there is a bad token. This means that appropriate privileges have not been given to the api key.

### Contact 

If there are any bugs or any support is needed please feel free visit our slack channel (#air) or contact us directly:

1. Arun Kaashyap Arunachalam (arun.arunachalam@cognite.com)
2. Sebastian Nickel (sebastian.nickel@cognite.com)


