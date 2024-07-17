# Remember to format your message properly (newlines etc)
# The position of each messge in the founder_messages array MATTERS A LOT and is linked to the position of each interest group in the IMPORTANT_SHARED_INTERESTS environment var
# Example: IMPORTANT_SHARED_INTERESTS is set to "Hard Tech;Agriculture / Agtech". In this case, if the bot finds that a founder is interested in Hard Tech,
#          it will send FOUNDER_MESSAGE_ONE to that founder. If, instead, the bot finds out that the founder is interested in Agriculture / Agtech, it will
#          use FOUNDER_MESSAGE_TWO. Now, imagine that you added FOUNDER_MESSAGE_TWO as the first entry in founder_messages. In this case, the bot would send
#          a message about floating farms to founders who are interested in hard tech but not in agriculture. It would be really weird
FOUNDER_MESSAGE_ONE = """Hi! I'm also a founder and would like to connect.

Let me know if you'd like to build spaceships.

See you soon,

Mr Spaceship Builder"""

FOUNDER_MESSAGE_TWO = """Hi! I'm also a founder and would like to connect.

Let me know if you'd like to build floating farms.

See you soon,

Mr Farm-a-Lot"""

founder_messages = [FOUNDER_MESSAGE_ONE, FOUNDER_MESSAGE_TWO]