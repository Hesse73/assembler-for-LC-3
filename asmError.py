class Asmerror:
    def __init__(self):
        self.eList = []

    def addError(self, line, etype, descrip):
        #line:行号，type：语法错误、逻辑错误等，descrip：可选的附加描述
        eDict = {'line': 0, 'type': '', 'descrip': ''}
        eDict['line'] = int(line)
        eDict['type'] = str(etype)
        eDict['descrip'] = str(descrip)
        self.eList.append(eDict)

    def isCorrect(self):
        if len(self.eList) >= 1:
            return False
        return True

    def showError(self):
        print(len(self.eList), ' Error(s)')
        for eDict in self.eList:
            if eDict['line'] < 0:
                print(eDict['type'], ':', eDict['descrip'])
            else:
                print(eDict['type'], ': in Line',
                      eDict['line'], ',', eDict['descrip'])
