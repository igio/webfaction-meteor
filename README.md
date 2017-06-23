# Wefaction-Meteor

Basic Python 3 script to install/update a Meteor application on Webfaction servers. I developed this script for my own purposes, inspired by [https://github.com/bvodola/meteorfaction](https://github.com/bvodola/meteorfaction). Use it with caution as no extensive testing has been performed. I can only vouch that it worked on with my own account.

## Prerequisites

- A Webfaction account (shared ok);
- Optional, a mongodb database (if not, you can install one on your webfaction account)

## Necessary Settings

Before you can use this script, you will have to create a new application on your webfaction account for the Meteor project. From the Webfaction console, create a `Node` application and choose the latest available Node version (6.11.0 as of June 2017). Once the application has been created, make a note of:

`name`: The application's folder name;

`port`: The port set up by Webfaction for this application;

Using the Webfaction console create a `domain` and a `website` record for your Meteor project and associate it with the Node application you just created. This will provide you with the `url` you will need for the project settings.

Optionally, if you need to install mongodb locally, follow [Webfaction's documentation](https://docs.webfaction.com/software/mongodb.html?highlight=mongodb#mongodb). Make note of the username, password, and port for your mongodb installation.

Then create your settings file, in JSON format, with the following structure:

```
{
    "local": {
        "app": "<your-app-folder-name>",
        "path": "<path-to-your-app-folder-name>"

    },
    "server": {
        "app": "<your-app-name>",
        "remote": "<webfaction-remote-host-name>",
        "user": "<webfaction-username>",
        "password": "<webfaction-password>",
        "port": "<webfaction-port>",
        "url": "<url-of-the-meteor-app-site>"
    },
    "db": {
        "mongodb": "<uri-of-your-mongodb-database>"
    }
}
```

`local` &rarr; `app`: The name of your app folder on the local machine;

`local` &rarr; `path`: The absolute path to the parent folder of your app;

`server` &rarr; `app`: The name of the app folder on the server;

`server` &rarr; `remote`: The name of the host you use with ssh or sftp to access the server from the console.

`server` &rarr; `user` &amp; `password`: Your credentials to login to the server;

`server` &rarr; `port`: The port opened by Webfaction for your application;

`server` &rarr; `url`: The url where your application will accessed at.

`db` &rarr; `mongodb`: The complete uri of your mongodb database.

Example settings file (with mongodb installed locally as well):

```
{
    "local": {
        "app": "test",
        "path": "~/_meteor"

    },
    "server": {
        "app": "test",
        "remote": "jdoe.webfactional.com",
        "user": "jdoe",
        "password": "jdoe_password",
        "port": "12345",
        "url": "test.jdoe.webfactional.com"
    },
    "db": {
        "mongodb": "mongodb://test:test_pass@localhost:21321/test"
    }
}
```

## Usage

```
python3 deploy.py -f <settings-file>
```

`-f <settings-file>`: Path & file name of where the project settings file is located. Recommended path is in the root folder of the Meteor application itself. For example:

```
python3 deploy.py -f ~/_meteor/app/wf-settings.json
```

## Script Flags

* `-b (--build)`: Include if you wish to build the project before uploading it to the servers.
* `-u (--update)`: Include to update an exiting Meteor project.

## Notes

- The `build` command is set up for a 64bit linux machine.
- When the `-u` flag is missing, the script will generate a `start` script for your meteor application and place it in the appropriate folder.

**If you found this script useful and have made improvements, please send a pull request so that others can benefit from your insights as well.**
