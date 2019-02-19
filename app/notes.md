# Things to note:
## 1. Cross Collection Reference
Post contains the user name~~(id)~~ of the author;
this means if the user name~~(id)~~ ever changes/disappears
then one of two things need to be done:

In case of removal:
1. a backup user name shows (natural for names)
2. marks removal~~(shows anonymous)~~ (preferred, just need to go through when removing user)

In case of change:
1. user keeps all past ids
2. all posts of a user gets updated (preferred)

## 2. Standardization
Store the UTC instead of local time; (MongoDB id generation time; #TODO: analyses posts)
convert to local time on demand.

Things to consider:  
1. client local time
2. source local time

Which makes more sense? Should both be displayed?

## 3. UI
~~The navigation bar collapses too soon~~[Fixed]

Redirect visitor to a modal for login with messages instead of a site

Click events not properly registered on mobile

(Site is not friendly for blind people)

## 4. Fragmentation
~~Currently, some settings are duplicated in views.py and clock.py~~[Fixed]
(Now has an ANA module for doing analysis)

Some work is need to make a generalized config object and a shared slug
(Now has a better template abstraction; working on sidebar content)

## 5. Security
Currently, debug mode is on.
~~This means when something goes wrong, pieces of code will be shown~~
(Won't be shown on release)

Double check form security

## 6. Analysis Styling
texts that are candidates for NLP samples now have html class "nlp-text"

## 7. Code Improvement
[better spacing styling for Bootstrap](https://getbootstrap.com/docs/4.0/utilities/spacing/)

## 8. Data Base
There are multiple copies of the language model now (check insert & back up issues)
