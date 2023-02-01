from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session, filetransfer
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor
from zope.interface import implements, implementer


class SSHSession(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def showPrompt(self):
        self.terminal.write(self.getPrompt())

    def connectionMade(self):
        self.terminal.write('Welcome to the SSH server!')
        self.terminal.nextLine()
        self.terminal.write('Enter your command:')
        self.terminal.nextLine()
        self.terminal.write('>> ')
        self.setRawMode()

    def connectionLost(self, reason):
        self.terminal.write('Connection lost!')
        self.terminal.nextLine()

    def lineReceived(self, line):
        self.terminal.write('You entered: ' + line)
        self.terminal.nextLine()
        self.terminal.write('>> ')

    def rawDataReceived(self, data):
        self.terminal.write('You entered: ' + data)
        self.terminal.nextLine()
        self.terminal.write('>> ')

    def getPrompt(self):
        return '>> '

    def getCommand(self, line):
        return line.split(' ')[0]

    def getCommandArgs(self, line):
        return line.split(' ')[1:]

    def handleCommand(self, command, args):
        if command == 'quit':
            self.terminal.write('Bye!')
            self.terminal.nextLine()
            self.terminal.loseConnection()
        else:
            self.terminal.write('Unknown command: ' + command)
            self.terminal.nextLine()
            self.terminal.write('>> ')

    def handle_CTRL_C(self):
        self.terminal.write('^C')
        self.terminal.nextLine()
        self.terminal.write('>> ')

    def handle_CTRL_D(self):
        self.terminal.write('^D')
        self.terminal.nextLine()
        self.terminal.write('>> ')


@implementer(ISession)
class SSHDemoAvatar(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHSession, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        pass

    def execCommand(self, protocol, cmd):
        raise NotImplementedError()

    def closed(self):
        pass


class SSHUser(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def logout(self):
        pass


@implementer(portal.IRealm)
class SSHRealm(object):

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            avatar = SSHUser(avatarId)
            avatar.subsystemLookup['sftp'] = filetransfer.FileTransferServer
            return IConchUser, avatar, avatar.logout
        elif ISession in interfaces:
            return ISession, SSHSession(avatarId), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found.")


def getRSAKeys():
    with open('id_rsa', 'r') as f:
        privateBlob = f.read()
    with open('id_rsa.pub', 'r') as f:
        publicBlob = f.read()
    return keys.Key.fromString(data=privateBlob), keys.Key.fromString(data=publicBlob)


if __name__ == '__main__':
    users = {'root': 'root'}
    privateRSAKey, publicRSAKey = getRSAKeys()
    factory = factory.SSHFactory()
    factory.portal = portal.Portal(SSHRealm())
    factory.portal.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))
    factory.publicKeys = {'ssh-rsa': publicRSAKey}
    factory.privateKeys = {'ssh-rsa': privateRSAKey}
    reactor.listenTCP(2222, factory)
    reactor.run()
