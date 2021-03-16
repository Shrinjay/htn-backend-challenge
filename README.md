# Overview:
Attached is a REST API built with Python and Flask, using an SQLite database,
for managing hacker data. Submitted for the Hack The North 2021 Backend Challenge.

## Features:
* Loader to extract, transform and load data from a hacker-data json. 
  Transformation process includes duplicate removal and normalization.
* Select and update hacker data for multiple hackers by Id, denormalize data from database
on query.
  
* Count and select skills by frequency.
* Request validation on all routes to validate parameter/request body shape.

## Setup:
* Clone the directory into your local machine.
* Ensure you have Python 3.5+, and the most recent
  version of SQLite installed, run ```pip install flask```
if the appropriate packages are not already installed on your environment.
  
* Run ```python main.py```
* Using any HTTP client, send ```GET http://localhost:5000/run_loader```
to generate the database in your local machine.
  
* At this point, your Hacker API is set up, go wild!

# Routes:

### Loader Route
```GET http://localhost:5000/run_loader```
<br>No configuration is required, as long as a valid ```hacker-data-2021.json```
file is present in the loader directory, an SQLite database will be created, or reset
if one already exists.

### Users Route
```GET http://localhost:5000/users?user=```
* Leaving ```user``` undefined will fetch all users
* ```user``` parameter **must correspond to a user id** .
* Multiple users can be selected with multiple values, ex: 
```GET http://localhost:5000/uers?user=id1&user=id2```
  
```PUT http://localhost:5000/users?user=```
* To **update a single user** specify a user id and specify request body as:
```
{
    "valid_parameter": "valid_value"
}
```
Where the parameter is any or multiple of the following: name, picture, company
, email, phone, skills (must be passed in as a list).
* To **update multiple users** specify multiple user ids, 
  ```PUT http://localhost:5000/users?user=x&user=y``` and specify request body
as a list in order of user ids:
  
```
[
    {
        "valid_parameter": "valid_value"
    },
    {
        "valid_parameter": "valid_value"
    }
]
```
In the above request, the first object will update user id x, the 
second will update user id y.

### Skills Route
```GET http://localhost:5000/skills?min_frequency=x&max_frequency=y```
* min_frequency and max_frequency are optional, if not specified, all
skills in order to most to least common will be returned.
  
* If only min_frequnecy is defined, all skills with a frequency from min_frequency 
to the maximum will be returned, and vice versa for if only max_frequency is defined.
  
### Request Validation
All routes have validation, therefore if incorrect input is passed in,
a failed validation will be returned to prevent a server crash. The validation 
rules are as follows:
* **All Requests**: Only valid parameters as defined in the documentation may be passed.
* **User GET Request**: 
  * Multiple arguments pay only be passed as ```arg=x&arg=y```, not ```arg=x,y``` 
  * The user id passed in must be valid.
  
* **User PUT Request**:
   * The request body may **only be a dict if one user is being updated**, if 
  multiple users are being updated, the request body **must be a JSON array of equal
     length as the number of user ids being updated**. Request body must be **either a dict or a list**.
     
  * All parameters in the user being updated must be valid.
  
* **Skill GET Request**: 
  * If minimum or maximum frequency is defined, they must be integer values.
  * Minimum frequency must be less than maximum frequency.