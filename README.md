# SSHChatRoom
The modules provide simple private messaging over SSH through an authenticating message broker server.
## How to run
1. Simply run the server
2. Run any number of intances of the client
3. Authenticate each user based on the "users.json" file
4. Enter the "[onlineusers]" command on each client to see a list of online users
5. Enter "[msg] <target-user-id> <message>" to send messages to different users
6. Hit enter for any client to refresh its feed of message
7. Tap on Ctrl + C any time to conveniently shutdown clients or the server