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
Store the UTC instead of local time;
convert to local time on demand.

Things to consider:  
1. client local time
2. source local time

Which makes more sense? Should both be displayed?

## 3. UI
The navigation bar collapses too soon