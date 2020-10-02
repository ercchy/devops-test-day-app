## D.Labs test day
The task: 
We need to containarize a Ruby application and write a script which retrieves weather reports and updates temperature in the  application.

* The Dockerfile consists of multi-stage build, ATM the multi-stage is trivial, but if the application would go into production, I would use the multi-stage build, because it makes it easy to create several different images. Also, if we included some kind of secret key in the base image and used it during build time, it would be deleted at the build target level (none of the other levels know anything about the environment variable we used in the base build). However, this is only useful for secrets at build time, but not at runtime.

* Docker compose builds the api image twice, one image is created for production (which would be pushed into the image repo for use by the deploy pipeline), another is used for development purposes. For this reason, the volumes are connected by a compose file (e.g. we use the 'volumes' attribute).

* Sidekiq app is a task processor and uses Redis as an intermediary. For this reason we need to use the same image as for the 'api_development' when we run it. It may be set up differently for production, which is more or less dependent on the devops process.

* We take logs outside where we can, as we please, and need them to tell us if anything strange happens in the containers. This is a step that makes debugging in the development environment easier, but for production we would normally put the logs somewhere where we could expose them and analyze them.

* We also bring persistence to the setup so that we do not lose the data every time we destroy the environment. This is a benefit for development purposes only, as it depends on the type of environment how data persistence is used.

* We have added a make file to make it easier to use and to provide some kind of ad-hoc documentation.

## Stopping climate change

For the script I used Python, because it is my go-to language. For usability I used the 'requests' library, but I can imagine that this would most likely not be appropriate for a barebones environment. This is because the requests library is external and has to be added manually. 

The script implements 'retry' and 'timeout' functions, which is a bit exaggerated, but I wanted to show my muscles. 
It also handles some errors, but it does not implement a test (which it should).

For updating the data I use the 'PATCH'method because we update and not add. 


#### Challenges:
* The first part of the task was easy, but I often wondered how Ruby is wired and how it works. Moving forward, I should definitely have to learn everything about the framework.
* Using the standard Python library for requests
