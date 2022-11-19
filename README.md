# chosei

A Python script with [bottle](https://bottlepy.org/docs/dev/), 
the simple wsgi implementation, 
manages the event schedule adjustments with participants.

## Usage

1. Run the chosei.py script with `python chosei.py`.
1. Just access "http://localhost:18081/<command>".

## Commands

- /new
  - Create new event shecdule master with some candicates of date and time with event name and comment.

- /new/\<event name\>
  - Create new shecdule master with some candicates of date and time with event name and comment.

- /get/\<event unique id\>
  - Get the participants' attendances for each date and time, and a comment.

- /add/\<event unique id\>/\<user id\>
  - Add and update the participants' attendances and a comment.

***
made by snytng@gmail.com


