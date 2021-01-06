import re

#指令词典
insDict = {'ADD': '0001', 'AND': '0101', 'BR': '0000000',
           'BRn':'0000100','BRz':'0000010','BRp':'0000001','BRzp':'0000011',
           'BRnp':'0000101','BRnz':'0000110','BRnzp':'0000111',
           'JMP': '1100', 'JSR': '0100', 'JSRR': '0100',
           'LD': '0010', 'LDI': '1010', 'LDR': '0110',
           'LEA': '1110', 'NOT': '1001',  'ST': '0011',
           'STI': '1011', 'STR': '0111', 'TRAP': '1111',
           'RET': '1100000111000000',
           'RTI': '1000000000000000',
           'GETC': '1111000000100000',
           'OUT': '1111000000100001',
           'PUTS': '1111000000100010',
           'IN': '1111000000100011',
           'PUTSP': '1111000000100100',
           'HALT': '1111000000100101',
           }
noOpIns = ['RET', 'RTI', 'GETC', 'OUT', 'PUTS', 'IN', 'PUTSP', 'HALT']
#汇编伪操作码
pseList = ['.ORIG', '.FILL', '.BLKW', '.STRINGZ', '.END']
#label 操作码
labelOp = ['.FILL', '.BLKW', '.STRINGZ', ]
#所有的关键字
keywords = ['ADD', 'AND', 'BR','BRn','BRz','BRp','BRzp','BRnp','BRnz','BRnzp', 'JMP', 'JSR', 'JSRR', 'LD', 'LDI', 'LDR', 'LEA',
            'NOT',  'ST', 'STI', 'STR', 'TRAP', 'RET', 'RTI', 'GETC', 'OUT', 'PUTS',
            'IN', 'PUTSP', 'HALT', '.ORIG', '.FILL', '.BLKW', '.STRINGZ', '.END']
#所有的分支类型
Branches = ['BR','BRn','BRz','BRp','BRzp','BRnp','BRnz','BRnzp',]
#正则表达式
allComment = '[ \t]*;'  # 整行(或分割出的子字符串)均为注释
empty = '[ \t]*'  # 没有实际意义的字符
emptyLine = '[ \t]*\n'  # 全空的行
emptyTail = '[ \t]*$'  # 全空的结尾
labelHead = '[ \t]*[a-zA-Z]\w*($|[ \t]+)'  # 即空格或制表符+以字母的变量名+至少一个空格或制表符
matchNum = '[ \t]*[x#b](\d+|-\d+)($|[ \t]+)'  # 匹配数字
matchLab = '[ \t]*[a-zA-Z]\w*($|[ \t]+)'    # 匹配 label
matchStr = '[ \t]*"(.*)"($|[ \t]+)'  # 由""界定的字符串


def isAllComment(line):
    if re.match(allComment, line):
        return True
    return False


def isEmptyLine(line):
    if re.match(emptyLine, line):
        return True
    return False


def noInstruction(line):
    if re.match(emptyTail, line) or re.match(emptyLine, line) or re.match(allComment, line):
        return True
    return False


def getFirstNum(line):
    getNum = re.compile(matchNum)
    m = getNum.match(line)
    if m:
        return m.group(0).strip()
    return None


def stripNum(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(matchNum, line, re.I)
    return line[m.end():]


def getFirstString(line):
    getString = re.compile(matchStr)
    m = getString.match(line)
    if m:
        return m.group(0).strip()
    return None


def stripString(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(matchStr, line, re.I)
    return line[m.end():]


def getLabel(line):
    #若有标签，则返回标签，否则返回None
    matchLabel = re.compile(labelHead)
    m = matchLabel.match(line)
    if m:
        #去掉label头尾可能存在的无意义字符
        label = m.group(0).strip()
        #检查是否为关键字
        if label.upper() not in keywords:
            return label
        return None
    return None


def stripLabel(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(labelHead, line)
    return line[m.end():]


def calNum(strNum):
    if strNum[1] == '-':
        if strNum[0] == 'x':
            targetNum = -int('0x' + strNum[2:], 16)
        elif strNum[0] == 'b':
            targetNum = -int('0b' + strNum[2:], 2)
        elif strNum[0] == '#':
            targetNum = -int(strNum[2:])
    else:
        if strNum[0] == 'x':
            targetNum = int('0x' + strNum[1:], 16)
        elif strNum[0] == 'b':
            targetNum = int('0b' + strNum[1:], 2)
        elif strNum[0] == '#':
            targetNum = int(strNum[1:])
    return targetNum


def isPse(line):
    #判断是否是伪操作码
    for pseIns in pseList:
        pattern = '[ \t]*%s($|[ \t]+)' % pseIns  # 指令后面即为字符串末尾或者至少有一个空
        if re.match(pattern, line, re.I):
            return pseIns
    return None


def getPse(line, pseIns):
    #从格式为' \t'+伪操作码+注释的行中检测是否格式正确并返回词典
    selIns = pseIns.upper()
    if selIns not in pseList:
        return None

    ret = {}
    spLine = re.split('[ \t]*%s' % selIns, line, 1, re.I)
    #需要取数字的伪操作码
    if selIns == '.ORIG' or selIns == '.FILL' or selIns == '.BLKW':
        pseNum_LRange = {'.ORIG': 0, '.FILL': -2e15, '.BLKW': 1}
        strNum = getFirstNum(spLine[1])
        targetNum = 0
        try:
            targetNum = calNum(strNum)
            if targetNum < pseNum_LRange[pseIns] or targetNum >= 2e15:
                ret['flag'] = 'error'
                ret['type'] = 'logic error'
                ret['descrip'] = 'you should use a reasonable %s number' % selIns
                return ret
        except:
            ret['flag'] = 'error'
            ret['type'] = 'logic error'
            ret['descrip'] = 'you should use a reasonable %s number' % selIns
            return ret
        tail = stripNum(spLine[1])
        if not noInstruction(tail):
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'there should be nothing after %s statement other than comments' % selIns
            return ret
        ret['flag'] = 'instruction'
        if selIns == '.ORIG':
            ret['origAddress'] = targetNum
        elif selIns == '.FILL':
            ret['mCode'] = [
                format(targetNum if targetNum >= 0 else (1 << 16) + targetNum, '016b')]
            ret['num'] = 1
        elif selIns == '.BLKW':
            ret['mCode'] = ['{0:016b}'.format(0)]*targetNum
            ret['num'] = targetNum
        return ret
    elif selIns == '.STRINGZ':
        String = getFirstString(spLine[1])
        mCodes = []
        try:
            for ch in String:
                mCodes.append('{0:016b}'.format(ord(ch)))
        except:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'you should use a correct .STRINGZ-string'
            return ret
        tail = stripString(spLine[1])
        if not noInstruction(tail):
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'there should be nothing after .STRING statement other than comments'
            return ret
        ret['flag'] = 'instruction'
        #长为string的机器码列表
        ret['mCode'] = mCodes
        ret['num'] = len(mCodes)
        return ret
    elif selIns == '.END':
        if not noInstruction(spLine[1]):
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'there should be nothing after .END statement other than comments'
            return ret
        ret['flag'] = 'instruction'
        return ret


def isIns(line):
    #若是指令，则返回指令名称，否则返回None
    for instruction in insDict.keys():
        #下面这样麻烦的匹配是为了尽可能避免所有错误
        # 指令后面即为字符串末尾或者为注释或者至少有一个空
        pattern = '[ \t]*%s($|[ \t]+)' % instruction
        if re.match(pattern, line, re.I):
            return instruction
    return None


def getIns(line, ins, curAddress, symDict):
    insName = ins.upper()
    if insName not in insDict.keys():
        return None
    ret = {}
    if insName in noOpIns:
        pattern = '[ \t]*%s([ \t]+|$)' % insName
        if re.match(pattern, line):
            #输入行的指令后面没有其他内容
            ret['flag'] = 'instruction'
            ret['mCode'] = insDict[insName]
            return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'instruction %s do not need operands' % insName
            return ret
    elif insName == 'ADD' or insName == 'AND':
        pattern1 = '[ \t]*%s[ \t]+R[0-7][ \t]*,[ \t]*R[0-7][ \t]*,[ \t]*R[0-7]($|[ \t]+)' % insName
        pattern2 = '[ \t]*%s[ \t]+R[0-7][ \t]*,[ \t]*R[0-7][ \t]*,[ \t]*[x#b](-\d+|\d+)($|[ \t]+)' % insName
        if re.match(pattern1, line):
            #表示 ADD(AND) DR,SR1,SR2的格式
            spLines = re.split('[ \t]*,[ \t]*', line, 2)  # 分割两次，得到三个子串
            DR = int(spLines[0].strip()[-1])  # 第一部分的最后一个字符即为第一个寄存器的编号
            SR1 = int(spLines[1].strip()[-1])
            SR2 = int(spLines[2].strip()[-1])
            mCode = insDict[insName] + '{0:03b}'.format(
                DR) + '{0:03b}'.format(SR1) + '000' + '{0:03b}'.format(SR2)
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        elif re.match(pattern2, line):
            #表示 ADD(AND) DR,SR1,imm5的格式
            spLines = re.split('[ \t]*,[ \t]*', line, 2)  # 分割两次，得到三个子串
            DR = int(spLines[0].strip()[-1])  # 第一部分的最后一个字符即为第一个寄存器的编号
            SR1 = int(spLines[1].strip()[-1])
            strNum = spLines[2].strip()
            try:
                imm5 = calNum(strNum)
                if imm5 < -2e4 or imm5 >= 2e4:
                    ret['flag'] = 'error'
                    ret['type'] = 'logic error'
                    ret['descrip'] = 'you should use a reasonable number to ADD'
                    return ret
            except:
                ret['flag'] = 'error'
                ret['type'] = 'logic error'
                ret['descrip'] = 'you should use a reasonable number to ADD'
                return ret
            mCode = insDict[insName] + '{0:03b}'.format(DR) + '{0:03b}'.format(
                SR1) + '1' + format(imm5 if imm5 >= 0 else (1 << 5) + imm5, '05b')
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'the assembler cannot interpret yout instruction'
            return ret
    elif insName in Branches:
        m = re.match('[ \t]*%s'%insName,line)
        tail = line[m.end():]#获取剩下的部分
        strNum = getFirstNum(tail)
        label = getLabel(tail)
        if strNum:    #tail is number
            PCoffset = calNum(strNum)
            if PCoffest < -2e8 or PCoffset >= 2e8:
                ret['flag'] = 'error'
                ret['type'] = 'logic error'
                ret['descrip'] = 'you should use a reasonable offset to branch'
                return ret
            mCode = insDict[insName] + format(PCoffset if PCoffset >= 0 else (1 << 9) + PCoffset, '09b')
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        elif label:   #tail is label
            if label not in symDict.keys():
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'label:%s is not defined'%label
                return ret
            else:     #label has been defined
                PCoffset = symDict['label'] - curAddress
                if PCoffest < -2e8 or PCoffset >= 2e8:
                    ret['flag'] = 'error'
                    ret['type'] = 'logic error'
                    ret['descrip'] = 'you should use a reasonable offset to branch'
                    return ret
                mCode = insDict[insName] + format(PCoffset if PCoffset >= 0 else (1 << 9) + PCoffset, '09b')
                ret['flag'] = 'instruction'
                ret['mCode'] = mCode
                return ret
                
