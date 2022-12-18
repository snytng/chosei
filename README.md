# chosei

A Python script with [bottle](https://bottlepy.org/docs/dev/), 
the simple wsgi implementation, 
manages the event schedule adjustments with participants.

## Usage

1. Install bottle by `pip install bottle`.
1. Run the chosei.py script by `python chosei.py`.
1. Just access "http://localhost:18101/".

## Commands

- /new
  - Create new event shecdule master with some candicates of date and time with event name and comment.

- /new/\<event name\>
  - Create new shecdule master with some candicates of date and time with event name and comment.

- /get/\<event unique id\>
  - Get the participants' attendances for each date and time, and a comment.

- /add/\<event unique id\>/\<user id\>
  - Add and update the participants' attendances and a comment.

## Azure deployment
- https://chosei-web-app.azurewebsites.net/index.html

***
made by snytng@gmail.com


