python-exist
============

Exist API Python Client Implementation


Requirements
============

* Python >= 2.6, Python >= 3.2, or PyPy. You can download it from https://www.python.org/
* Pip. If you have Python >= 2.7.9 or >= 3.4 then you already have ``pip``. Otherwise, please follow these instructions : https://pip.pypa.io/en/latest/installing.html


Installing
==========

Once you have satisfied the requirements listed above, install by running the
following command from them terminal:

    pip install exist


Quick Start
===========

Install with ``pip install exist``

python-exist can be used with one of three authorization types; basic, oauth, or an api_token

To use basic authorization and store the returned token, add your "username" and "password" in the following
command:

    exist authorize --username=<username> --password=<password>

If you already have a token, add it to the following command:

    exist authorize --api_token=<token>

To use OAuth authorizations and store the returned token add your "App key", "App secret" and "Redirect URL" (optional) in the following
command (Note: this requires app to registered directly with Exist):

    exist authorize --client_id=<app_key> --client_secret=<app_secret> --redirect_uri=<redirect_uri>

That will save the necessary credentials for making further API calls to a file
called "exist.cfg". These credentials should be kept private. You can use same
the command-line client to access everything in the
Exist API (http://developer.exist.io). You can also access the
same resources using the Python API:

    >>> from exist import Exist
    >>> exist = Exist(<client_id>, <client_secret>, <access_token>)
    >>> print(exist.user())
    {
        "id": 1,
        "username": "josh",
        "first_name": "Josh",
        "last_name": "Sharp",
        "bio": "I made this thing you're using.",
        "url": "http://hellocode.co/",
        "avatar": "https://exist.io/static/media/avatars/josh_2.png",
        "timezone": "Australia/Melbourne",
        "local_time": "2020-07-31T22:33:49.359+10:00",
        "private": false,
        "imperial_units": false,
        "attributes": [
            {
                "group": "steps",
                "priority": 1,
                "items": [
                    {
                        "attribute": "steps",
                        "label": "Steps",
                        "value": 258,
                        "service": "Fitbit",
                        "priority": 1,
                        "private": false,
                        "value_type": 0,
                        "value_type_description": "Integer"
                    },
                    {
                        "attribute": "floors",
                        "label": "Floors",
                        "value": 2,
                        "service": "Fitbit",
                        "priority": 2,
                        "private": false,
                        "value_type": 0,
                        "value_type_description": "Integer"
                    }
                ]
            }
        ]
    }

More commands are available as per the help section of the exist command from ``exist --help``


Roadmap
=======
* Tests (next)
* Write API connectivitiy (in progress)
