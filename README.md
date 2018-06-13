# Why I did this piece of software ?

First I'm using a universal remote to control my home device (TV, Home Cinema, Projector, ...)

Recently I bought a new amplifier because the Home Cinema don't have the expected sound quality.

My choice is a Naim Uniti Atom, the only issue with the amplifier is his remote control witch is using radio frequency to communicate.

So I found after buying, it was not possible to control the amplifier.

# How It will work ?

The universal remote will send infra red command to a small computer (raspberry pi like). 
The computer will send a HTTP request to the Naim Uniti device.

The software is a python script.

# Yes it's still in progress