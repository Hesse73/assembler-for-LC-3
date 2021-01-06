#汇编文件名，之后要改成命令行输入
from match import *
from asmError import Asmerror
import re


def main():
    filename = r'C:\Users\14570\Desktop\Python\ics\test.asm'
    asmFile = open(filename, 'r')
    text = asmFile.readlines()
    asmFile.close()
    Errors = Asmerror()
    haveOrig = False
    haveEnd = False
    origAddress = -1
    origLine = 0
    endLine = 0
    #label及其对应的地址
    symDict = {}
    #含有label的行
    labeledLine = []
    mCodeDict = {}
    '''
    思路：首先去掉所有的注释(空行不能去掉，否则不能正确标注行号)
    判断是否有Orig和END(否则就无法获取地址)
    然后按行获取label和操作码
    最后进行编译
    '''
    #去掉所有的注释和空行
    out = []
    for line in text:
        if ';' in line:
            out.append(re.split(';', line, 1)[0])
        else:
            out.append(line)
    text = out
    #遍历文件，获取基本信息并检查是否有Orig和End
    for i in range(len(text)):
        if noInstruction(text[i]):
            continue
        elif not haveOrig:
            if isPse(text[i]) == '.ORIG':
                haveOrig = True
                origLine = i + 1
                message = getPse(text[i], '.ORIG')
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
                elif message['flag'] == 'instruction':
                    origAddress = message['origAddress']
            elif isPse(text[i]) == '.END':
                haveEnd = True
                endLine = i + 1
                message = getPse(text[i], '.END')
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
        elif not haveEnd:
            if isPse(text[i]) == '.END':
                haveEnd = True
                endLine = i + 1
                message = getPse(text[i], '.END')
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
    if not haveOrig:
        Errors.addError(-1, 'format error', 'no .orig statement in asm file')
    if not haveEnd:
        Errors.addError(-1, 'format error', 'no .end statement in asm file')
    if not Errors.isCorrect():
        Errors.showError()
        return -1

    #遍历文件，获取label，同时生成部分机器码
    curAddress = origAddress
    for i in range(origLine, endLine - 1):
        #在orig和end之前获取label
        if noInstruction(text[i]):
            continue
        #若此行存在label
        elif getLabel(text[i]):
            label = getLabel(text[i])
            labeledLine.append(i)
            #若此label未被定义过
            if label not in symDict.keys():
                symDict[str(label)] = curAddress
                instr = stripLabel(text[i])
                pseIns = isPse(instr)
                #若label后为伪指令
                if pseIns:
                    message = getPse(instr, pseIns)
                    if message['flag'] == 'error':
                        Errors.addError(
                            i+1, message['type'], message['descrip'])
                    elif message['flag'] == 'instruction':
                        for i in range(message['num']):
                            mCodeDict['%x' % curAddress] = message['mCode'][i]
                            curAddress += 1
                #若label后为正常指令
                else:
                    curAddress += 1
            #否则说明此标签被重定义
            else:
                Errors.addError(i+1, 'syntax error',
                                'redefinition of label: %s' % label)
        #说明此行是不带label的指令
        else:
            pseIns = isPse(text[i])
            #若此行是为伪指令
            if pseIns:
                message = getPse(text[i], pseIns)
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
                elif message['flag'] == 'instruction':
                    for i in range(message['num']):
                        mCodeDict['%x' % curAddress] = message['mCode'][i]
                        curAddress += 1
            #若此行是正常指令，留到后面再处理
            else:
                curAddress += 1
    print(symDict)
    print(labeledLine)
    if not Errors.isCorrect():
        Errors.showError()
        return -1
    #最后一次遍历，生成机器码，同时检查语法
    curAddress = origAddress
    for i in range(origLine, endLine - 1):
        #若为空行，则跳过
        if noInstruction(text[i]):
            continue
        #若此行有标签
        elif i in labeledLine:
            instr = stripLabel(text[i])
            insName = isIns(instr)
            #若此行是指令
            if insName != None:
                message = getIns(instr, insName,curAddress, symDict)
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
                    curAddress += 1
                elif message['flag'] == 'instruction':
                    #保存指令的机器码，并使地址加一
                    mCodeDict['%x' % curAddress] = message['mCode']
                    curAddress += 1
        else:
            insName = isIns(text[i])
            #若此行是指令
            if insName != None:
                message = getIns(text[i], insName, curAddress, symDict)
                if message['flag'] == 'error':
                    Errors.addError(i+1, message['type'], message['descrip'])
                    curAddress += 1
                elif message['flag'] == 'instruction':
                    #保存指令的机器码，并使地址加一
                    mCodeDict['%x' % curAddress] = message['mCode']
                    curAddress += 1
            else:
                Errors.addError(
                    i+1, 'unknown error', 'the assembler cannot interpret yout instruction')
    if not Errors.isCorrect():
        Errors.showError()
        return -1
    print('{0:016b}'.format(origAddress))
    for key in sorted(mCodeDict):
        #print(key,':',mCodeDict[key])
        print(key,':','%x'%int(mCodeDict[key],2))

'''
存在的问题，许多函数对于每一行的结尾并没有做检查
'''
if __name__ == '__main__':
    main()
