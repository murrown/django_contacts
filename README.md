# Contacts API
Author: [Nathan Murrow (murrown)](https://www.linkedin.com/in/nathan-murrow)

## Deployment
This project requires Python >= 3.6 and Django >= 2.0.6.
```
git clone https://github.com/murrown/django_contacts.git && cd django_contacts
pip3 install -r pip3_requirements.txt
```
There are some unit/integration tests for testing each of the API endpoints. Verify that they pass like so:
```
./manage.py test -v2
```
To run the server, you must use **testserver**, not **runserver**. This is because the database is stored entirely in memory, so the application needs to load a fixture from a file. **empty_fixture.json** contains two users and no data.
```
./manage.py testserver empty_fixture.json
```
Alternatively, use **contacts/fixtures/test_fixture.json** to start with some initial test data.

## API
### Endpoints
Method | URI | Accepts Data | Must Authenticate | Purpose
------ | --- | ------------ | ----------------- | -------
POST | /api/ | :heavy_check_mark: | :heavy_check_mark: | Create a new contact.
GET | /api/**&lt;pk&gt;** |  |  | Get a contact.
PATCH | /api/**&lt;pk&gt;** | :heavy_check_mark: | :heavy_check_mark: | Replace a contact's data.
GET | /api/ | :heavy_check_mark: |  | Get a list of contacts (filterable).
DELETE | /api/**&lt;pk&gt;** |  | :heavy_check_mark: | Delete a contact.

The editable contact fields are **name**, **phone_number**, **address**, and **email**.

Additionally, contacts can be filtered by **created**, **created_by**, **modified**, **modified_by**, and **pk**.

The server will respond with **HTTP 200: OK** or **HTTP 400: Bad Request** depending on whether the request is successful or not. If authentication is required and fails, it will respond with **HTTP 403: Forbidden**.

### Examples
First let's create a contact. Only a **name** is required to create a new contact.
```
> curl --user test_user:test_password -X POST 127.0.0.1:8000/api/ --data '{"name": "Gordon", "email": "hubris@radham.edu"}'
{
    "address": "",
    "created": "2018-07-15T08:49:11.097Z",
    "created_by": 1,
    "email": "hubris@radham.edu",
    "modified": "2018-07-15T08:49:11.097Z",
    "modified_by": null,
    "name": "Gordon",
    "phone_number": "",
    "pk": 6
}
```
The response from the server is the json representation of the newly created contact.

Now let's update our contact with the missing information. The only fields that can be changed directly are **name**, **phone_number**, **address**, and **email**.
```
> curl --user test_user2:test_password2 -X PATCH 127.0.0.1:8000/api/6 --data '{"address": "Radham Academy", "phone_number": "1180905"}'
{
    "address": "Radham Academy",
    "created": "2018-07-15T08:49:11.097Z",
    "created_by": 1,
    "email": "hubris@radham.edu",
    "modified": "2018-07-15T08:57:21.640Z",
    "modified_by": 2,
    "name": "Gordon",
    "phone_number": "1180905",
    "pk": 6
}
```
Notice that because we authenticated with a different user, the **created_by** and **modified_by** fields are different.

Let's search our contacts for everyone living at Radham with a primary key greater than or equal to 3. The field lookup conventions are the same as for Django **filter()** queries.
```
> curl -X GET 127.0.0.1:8000/api/ --data '{"address__icontains": "radham", "pk__gte": 3}'
[
    {
        "address": "Radham Academy",
        "created": "2018-07-14T12:16:19.504Z",
        "created_by": null,
        "email": "",
        "modified": "2018-07-14T12:16:19.504Z",
        "modified_by": null,
        "name": "Lillian",
        "phone_number": "1921311",
        "pk": 3
    },
    {
        "address": "Radham Academy",
        "created": "2018-07-15T08:49:11.097Z",
        "created_by": 1,
        "email": "hubris@radham.edu",
        "modified": "2018-07-15T08:57:21.640Z",
        "modified_by": 2,
        "name": "Gordon",
        "phone_number": "1180905",
        "pk": 6
    }
]
```
There's two students who meet the requirements. Great!

Now let's delete the contact we just created.
```
> curl --user test_user:test_password -X DELETE 127.0.0.1:8000/api/6
{
    "address": "Radham Academy",
    "created": "2018-07-15T08:49:11.097Z",
    "created_by": 1,
    "email": "hubris@radham.edu",
    "modified": "2018-07-15T08:57:21.640Z",
    "modified_by": 2,
    "name": "Gordon",
    "phone_number": "1180905",
    "pk": 6
}
```
On a successful deletion, the server responds with the data of the deleted contact.

## Authentication
HTTP Basic Authentication is used for all endpoints that modify data, including creations, updates, and deletions.

### Users
Data can be modified by any user in the database. The provided fixtures include two users for testing.

Username | Password 
-------- | --------
test_user | test_password
test_user2 | test_password2

### Change Logging
- Each contact record stores a user id and a timestamp for both when it is created and its most recent update.
- The user id is that of the authenticated user in the relevant request.
- If a contact has never been updated, it will have a null value in its **modified_by** field.
- If a contact is updated multiple times, only the most recent update is stored.
- Deleted contacts are not logged at all.
