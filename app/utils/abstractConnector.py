from abc import ABC, abstractmethod


class abstractConnector(ABC):
    @abstractmethod
    def initApp(self, app):
        raise NotImplementedError('Subclass must override initApp method')

    @abstractmethod
    def connection(self):
        raise NotImplementedError('Subclass must override connection method')

    @abstractmethod
    def authenticateUser(self, username):
        raise NotImplementedError('Subclass must override authenticateUser method')

    @abstractmethod
    def getUserGroups(self, username):
        raise NotImplementedError('Subclass must override getUserGroups method')

    @abstractmethod
    def createUser(self):
        raise NotImplementedError('Subclass must override createUser method')

    @abstractmethod
    def createGroup(self, groupName, options=None):
        raise NotImplementedError('Subclass must override createGroup method')

    @abstractmethod
    def deleteUser(self, username):
        raise NotImplementedError('Subclass must override deleteUser method')

    @abstractmethod
    def deleteGroup(self, groupName, options=None):
        raise NotImplementedError('Subclass must override deleteGroup method')

    @abstractmethod
    def addUserToGroups(self, username, groups):
        raise NotImplementedError('Subclass must override addUserToGroups method')

    @abstractmethod
    def removeUserFromGroups(self, username, groups):
        raise NotImplementedError('Subclass must override removeUserFromGroups method')

    @abstractmethod
    def resetPassword(self, username, password):
        raise NotImplementedError('Subclass must override removeUserFromGroups method')