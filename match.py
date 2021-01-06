import re

#指令词典
insDict = {'ADD': '0001', 'AND': '0101', 'BR': '0000111',
           'BRN': '0000100', 'BRZ': '0000010', 'BRP': '0000001', 'BRZP': '0000011',
           'BRNP': '0000101', 'BRNZ': '0000110', 'BRNZP': '0000111',
           'JMP': '1100000', 'JSR': '01001', 'JSRR': '0100000',
           'LD': '0010', 'LDI': '1010', 'LDR': '0110',
           'LEA': '1110', 'NOT': '1001',  'ST': '0011',
           'STI': '1011', 'STR': '0111', 'TRAP': '11110000',
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
keywords = ['ADD', 'AND', 'BR', 'BRN', 'BRZ', 'BRP', 'BRZP', 'BRNP', 'BRNZ', 'BRNZP', 'JMP', 'JSR', 'JSRR', 'LD', 'LDI', 'LDR', 'LEA',
            'NOT',  'ST', 'STI', 'STR', 'TRAP', 'RET', 'RTI', 'GETC', 'OUT', 'PUTS',
            'IN', 'PUTSP', 'HALT', '.ORIG', '.FILL', '.BLKW', '.STRINGZ', '.END']
#所有的分支类型
Branches = ['BR', 'BRN', 'BRZ', 'BRP', 'BRZP', 'BRNP', 'BRNZ', 'BRNZP', ]
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
    try:
        getNum = re.compile(matchNum)
        m = getNum.match(line)
        if m:
            return m.group(0).strip()
        return None
    except:
        return None


def stripNum(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(matchNum, line, re.I)
    return line[m.end():]


def getFirstString(line):
    try:
        getString = re.compile(matchStr)
        m = getString.match(line)
        if m:
            return m.group(0).strip()
        return None
    except:
        return None


def stripString(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(matchStr, line, re.I)
    return line[m.end():]


def getLabel(line):
    #若有标签，则返回标签，否则返回None
    matchLabel = re.compile(labelHead)
    try:
        m = matchLabel.match(line)
        if m:
            #去掉label头尾可能存在的无意义字符
            label = m.group(0).strip()
            #检查是否为关键字或者类似x3000的数字
            if label.upper() not in keywords and getFirstNum(label) == None:
                return label
            return None
        return None
    except:
        return None


def stripLabel(line):
    #这里不能用split，因为模式字符中使用了捕获组合（即圆括号）
    m = re.match(labelHead, line)
    return line[m.end():]


def calNum(strNum):
    if strNum[1] == '-':
        if strNum[0] == 'x':
            targetNum = -int(strNum[2:], 16)
        elif strNum[0] == 'b':
            targetNum = -int(strNum[2:], 2)
        elif strNum[0] == '#':
            targetNum = -int(strNum[2:])
    else:
        if strNum[0] == 'x':
            targetNum = int(strNum[1:], 16)
        elif strNum[0] == 'b':
            targetNum = int(strNum[1:], 2)
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
        pseNum_LRange = {'.ORIG': 0, '.FILL': -2**15, '.BLKW': 1}
        strNum = getFirstNum(spLine[1])
        targetNum = 0
        try:
            targetNum = calNum(strNum)
            if targetNum < pseNum_LRange[pseIns] or targetNum >= 2**15:
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
            #去掉匹配到的字符串开头和结尾的双引号
            for ch in String[1:-1]:
                mCodes.append('{0:016b}'.format(ord(ch)))
            mCodes.append('{0:016b}'.format(0))  # 最后一行为x0000
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


def getOffset(tail, insName, curAddress, symDict, length, *noLabel):
    ret = {}
    strNum = getFirstNum(tail)
    label = getLabel(tail)
    noLab = False
    if len(noLabel) > 0:
        noLab = noLabel[0]
    if strNum:  # tail is number
        rest = stripNum(tail)
        if not noInstruction(rest): #若后面还有其他内容
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
            return ret
        PCoffset = calNum(strNum)
        if PCoffset < -2**(length-1) or PCoffset >= 2**(length - 1):
            ret['flag'] = 'error'
            ret['type'] = 'logic error'
            ret['descrip'] = 'you should use a reasonable offset to %s' % insName
            return ret
        offset = format(PCoffset if PCoffset >= 0 else (
            1 << length) + PCoffset, '0%db' % length)
        ret['flag'] = 'instruction'
        ret['offset'] = offset
        return ret
    elif not noLab and label:  # tail is label
        rest = stripLabel(tail)
        if not noInstruction(rest): #若后面还有其他内容
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
        if label not in symDict.keys():
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'label:%s is not defined' % label
            return ret
        else:  # label has been defined
            PCoffset = symDict[label] - (curAddress + 1)
            if PCoffset < -2**(length-1) or PCoffset >= 2**(length - 1):
                ret['flag'] = 'error'
                ret['type'] = 'logic error'
                ret['descrip'] = 'you should use a reasonable offset to %s' % insName
                return ret
            offset = format(PCoffset if PCoffset >= 0 else (
                1 << length) + PCoffset, '0%db' % length)
            ret['flag'] = 'instruction'
            ret['offset'] = offset
            return ret
    else:  # tail is nothing
        ret['flag'] = 'error'
        ret['type'] = 'syntax error'
        ret['descrip'] = 'the assembler cannot interpret yout %s instruction'%insName
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
        m = re.match(pattern, line, re.I)
        if m:
            rest = line[m.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
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
        m1 = re.match(pattern1, line, re.I)
        m2 = re.match(pattern2, line, re.I)
        if m1:
            #表示 ADD(AND) DR,SR1,SR2的格式
            rest = line[m1.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
            spLines = re.split('[ \t]*,[ \t]*', line, 2)  # 分割两次，得到三个子串
            DR = int(spLines[0].strip()[-1])  # 第一部分的最后一个字符即为第一个寄存器的编号
            SR1 = int(spLines[1].strip()[-1])
            SR2 = int(spLines[2].strip()[-1])
            mCode = insDict[insName] + '{0:03b}'.format(
                DR) + '{0:03b}'.format(SR1) + '000' + '{0:03b}'.format(SR2)
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        elif m2:
            #表示 ADD(AND) DR,SR1,imm5的格式
            rest = line[m2.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
            spLines = re.split('[ \t]*,[ \t]*', line, 2)  # 分割两次，得到三个子串
            DR = int(spLines[0].strip()[-1])  # 第一部分的最后一个字符即为第一个寄存器的编号
            SR1 = int(spLines[1].strip()[-1])
            strNum = spLines[2].strip()
            imm5 = calNum(strNum)
            if imm5 < -2**4 or imm5 >= 2**4:
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
            ret['type'] = 'unknown error'
            ret['descrip'] = 'the assembler cannot interpret yout instruction'
            return ret
    elif insName in Branches:
        m = re.match('[ \t]*%s' % insName, line, re.I)
        tail = line[m.end():]  # 获取剩下的部分
        PCoffset = getOffset(tail, insName, curAddress, symDict, 9)
        if PCoffset['flag'] == 'error':
            return PCoffset
        elif PCoffset['flag'] == 'instruction':
            ret['flag'] = 'instruction'
            ret['mCode'] = insDict[insName] + PCoffset['offset']
            return ret
    elif insName == 'JMP':
        pattern = '[ \t]*JMP[ \t]+R[0-7]($|[ \t]+)'
        m = re.match(pattern, line, re.I)
        if m:
            rest = line[m.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
            #获取寄存器
            BaseR = int(m.group().strip()[-1])
            mCode = insDict[insName] + '{0:03b}'.format(BaseR)+'000000'
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'invalid JMP instruction'
            return ret
    elif insName == 'JSR':
        m = re.match('[ \t]*JSR[ \t]+', line, re.I)
        tail = line[m.end():]
        PCoffset = getOffset(tail, insName, curAddress, symDict, 11)
        if PCoffset['flag'] == 'error':
            return PCoffset
        elif PCoffset['flag'] == 'instruction':
            ret['flag'] = 'instruction'
            ret['mCode'] = insDict[insName] + PCoffset['offset']
            return ret
    elif insName == 'JSRR':
        pattern = '[ \t]*JSRR[ \t]+R[0-7]($|[ \t]+)'
        m = re.match(pattern, line, re.I)
        if m:
            rest = line[m.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
            #获取寄存器
            BaseR = int(m.group().strip()[-1])
            mCode = insDict[insName] + '{0:03b}'.format(BaseR)+'000000'
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'invalid JSRR instruction'
            return ret
    elif insName == 'LD' or insName == 'LDI' or insName == 'ST' or insName == 'STI' or insName == 'LEA':
        pattern = '[ \t]*%s[ \t]+R[0-7][ \t]*,[ \t]*' % insName
        m = re.match(pattern, line, re.I)
        if m:
            tail = line[m.end():]
            m = re.match('[ \t]*%s[ \t]+R[0-7][ \t]*' % insName, line, re.I)
            DR = int(m.group().strip()[-1])
            PCoffset = getOffset(tail, insName, curAddress, symDict, 9)
            if PCoffset['flag'] == 'error':
                return PCoffset
            elif PCoffset['flag'] == 'instruction':
                ret['flag'] = 'instruction'
                ret['mCode'] = insDict[insName] + \
                    '{0:03b}'.format(DR)+PCoffset['offset']
                return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'invalid %s instruction' % insName
            return ret
    elif insName == 'LDR' or insName == 'STR':
        ret = {}
        # instr DR/SR , BaseR , offset6
        pattern = '[ \t]*%s[ \t]+R[0-7][ \t]*,[ \t]*R[0-7][ \t]*,[ \t]*' % insName
        m = re.match(pattern, line, re.I)
        if m:
            #按逗号分割两次
            spLines = re.split(',', line, 2)
            DR = int(spLines[0].strip()[-1])
            BaseR = int(spLines[1].strip()[-1])
            tail = spLines[2]
            offset = getOffset(tail, insName, curAddress, symDict, 6, True)
            if offset['flag'] == 'error':
                return offset
            elif offset['flag'] == 'instruction':
                ret['flag'] = 'instruction'
                ret['mCode'] = insDict[insName] + \
                    '{0:03b}'.format(
                        DR)+'{0:03b}'.format(BaseR)+offset['offset']
                return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'invalid %s instruction' % insName
            return ret

    elif insName == 'NOT':
        ret = {}
        pattern  = '[ \t]*NOT[ \t]+R[0-7][ \t]*,[ \t]*R[0-7]([ \t]*|&)'
        m = re.match(pattern,line,re.I)
        if m:
            rest = line[m.end():]
            #输入行的指令后面不应有其他内容
            if not noInstruction(rest):
                ret['flag'] = 'error'
                ret['type'] = 'syntax error'
                ret['descrip'] = 'there should be nothing after %s instruction other than comments'%insName
                return ret
            spLines = re.split(',',m.group(),1)
            DR = int(spLines[0].strip()[-1])
            SR = int(spLines[1].strip()[-1])
            mCode = insDict[insName] + '{0:03b}'.format(DR) + '{0:03b}'.format(SR) + '111111'
            ret['flag'] = 'instruction'
            ret['mCode'] = mCode
            return ret
        else:
            ret['flag'] = 'error'
            ret['type'] = 'syntax error'
            ret['descrip'] = 'invalid %s instruction' % insName
            return ret

    elif insName == 'TRAP':
        ret = {}
        m = re.match('[ \t]*TRAP[ \t]+',line,re.I)
        tail = line[m.end():]
        trapvect = getOffset(tail, insName, curAddress, symDict, 8, True)
        if trapvect['flag'] == 'error':
            return trapvect
        elif trapvect['flag'] == 'instruction':
            ret['flag'] = 'instruction'
            ret['mCode'] = insDict['TRAP'] + trapvect['offset']
            return ret
