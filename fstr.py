import unittest
def formatstr(formatDict):
    result=[]
    if formatDict['fill'] and formatDict['align']:
        result.append(str(formatDict['fill']))
    if formatDict['align']:
        result.append(str(formatDict['align']))
    if formatDict['sign']:
        result.append(str(formatDict['sign']))
    if formatDict['alternate']:
        result.append(str(formatDict['alternate']))
    if formatDict['zeropadding']:
        result.append(str(formatDict['zeropadding']))
    if formatDict['width']:
        result.append(str(formatDict['width']))
    if formatDict['precision']:
        result.append(str(formatDict['precision']))
    if formatDict['type']:
        result.append(str(formatDict['type']))
    return ''.join(result)
def uni2int(val,formatDict,*args,**kwargs):
    if type(val) not in [str,unicode]:
        return ('{0:'+formatstr(formatDict)+'}').format(val)
    return ord(val.strip())
def perc2float(val,formatDict,*args,**kwargs):
    if type(val)!=str:
        return ('{0:'+formatstr(formatDict)+'}').format(val)
    return float(val.rstrip('%'))/100.0
def floatparse(val,formatDict,*args,**kwargs):
    if type(val)!=str:
        return ('{0:'+formatstr(formatDict)+'}').format(val)
    sign=1
    if formatDict['sign']=='-':
        sign=-1 
    if val.isspace():
        return None
    if '?' in val:
        return None
    if not formatDict['precision']:    
        return sign*float(val.strip(' ').replace(' ','0'))
    else:
        try:
            return sign*float(val)
        except:
            pass   
        dec=int(formatDict['precision'])
        integer=int(len(val.replace('.','')))-dec
        return sign*(float('0'+val[:integer].strip(' '))+float('.'+val[-dec:]).strip(' ')+'0')
def intparse(val,formatDict,*args,**kwargs):
    if type(val)!=str:
        return ('{0:'+formatstr(formatDict)+'}').format(val)
    sign=1
    if formatDict['sign']=='-':
        sign=-1 
    return sign*int(val,*args)
def strparse(val,formatDict,*args,**kwargs):
    if type(val)!=str:
        return ('{0:'+formatstr(formatDict)+'}').format(val)
    return str(val)
class FormatString(object):
    """FormatString
    Class for reading and writing a format string - use is similar to standard python str.format() method
    Pass the format string as an argument on initialisation.
    
    Contains two main methods:
        format(*args,**kwargs):
            returns a string
            
            Behaves like standard python str.format() method (PEP 3101)
        read(inputString):
            returns a dictionary
            
            Reads inputString and parses according to format string (inverse of str.format()). 
            
    Can parse free format stings (space delimited) which is signified by the __freeformatdelimiter__ value (default is |)
    Other methods are helper methods for the format parsing etc. 
    """
    _typeDict={'b':(intparse,[2]),
                'c':(uni2int,[]),
                'd':(intparse,[10]),
                'o':(intparse,[8]),
                'x':(intparse,[16]),
                'X':(intparse,[16]),
                'e':(floatparse,[]),
                'E':(floatparse,[]),
                'f':(floatparse,[]),
                'F':(floatparse,[]),
                'g':(floatparse,[]),
                'G':(floatparse,[]),
                'n':(floatparse,[]),
                '%':(perc2float,[]),
                's':(strparse,[]),
                None:(float,[])}
    __freeformatdelimiter__='|'
    __fixed__=False
    def __init__(self,formatstring,fixedWidth=False):
        self.__fixed__=fixedWidth
        self.__setformatstring__(formatstring)
    def __setformatstring__(self,formatString):
        self.__setattr__('__formatstring__',formatString)
    def __specparse__(self,formatSpec):
        formatDict={}
        formatDict['fill']=False
        formatDict['align']=False
        if len(formatSpec)>1 and formatSpec[1] in ['<','>','=','^']:
            formatDict['fill']=formatSpec[0]
            formatDict['align']=formatSpec[1]
            formatSpec=formatSpec[2:]
        elif len(formatSpec)>0 and formatSpec[0] in ['<','>','=','^']:
            formatDict['fill']=False
            formatDict['align']=formatSpec[0]
            formatSpec=formatSpec[1:]
        #Align and fill dealt with and removed from formatspec
        formatDict['type']='s'
        if len(formatSpec)>0 and formatSpec[-1] in self._typeDict.keys():
            formatDict['type']=formatSpec[-1]
            formatSpec=formatSpec[:-1]
        # type dealt with and removed from formatspec
        formatDict['sign']=False
        if len(formatSpec)>0 and formatSpec[0] in ['+','-',' ']:
            formatDict['sign']=formatSpec[0]
            formatSpec=formatSpec[1:]
        #sign dealt with and removed from formatspec
        formatDict['alternate']=False
        if len(formatSpec)>0 and formatSpec[0]=='#':
            formatDict['alternate']=True
            formatSpec=formatSpec[1:]
        formatDict['zeropadding']=False
        if len(formatSpec)>0 and formatSpec[0]=='0':
            formatDict['zeropadding']=True
            formatSpec=formatSpec[1:]
        formatDict['comma']=False
        if len(formatSpec)>0 and ',' in formatSpec:
            formatDict['comma']=True
            formatSpec=formatSpec.replace(',','')
        formatDict['precision']=False
        formatDict['width']=False
        if len(formatSpec)>0 and formatSpec[0]=='.':
            formatDict['precision']=formatSpec[1:]
        elif len(formatSpec)>0 and '.' in formatSpec:
            formatDict['width']=int(formatSpec.split('.')[0])
            formatDict['precision']='.'.join(formatSpec.split('.')[1:])
        elif len(formatSpec)>0:
            formatDict['width']=int(''.join([v for v in formatSpec if v.isdigit()]))            
        formatDict['output']=False
        return formatDict
    def __parse__(self):
        Results=[]
        for literal_text, field_name, format_spec, conversion in \
            self.__formatstring__._formatter_parser():
            if literal_text:
                Results.append(literal_text)
            if field_name is not None:
                Results.append((field_name,self.__specparse__(format_spec),conversion))
        return Results
    def __repr__(self):
        return self.__formatstring__
    def format(self,*args,**kwargs):
        """format(*args,**kwargs):
    Behaves like the standard python str.format (PEP 3101) method for parsing a format spec type string (see python docs for format spec construction) 
    Can parse attributes of objects as in PEP 3101
    """
        return self._vformat(self.__formatstring__,args,kwargs,2)
    def _vformat(self,formatstring,args,kwargs,recursion_depth):        
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result=[]
        for literal_text, field_name, format_spec, conversion in \
            formatstring._formatter_parser():
            # output the literal text
            if literal_text:
                if self.__freeformatdelimiter__ in literal_text:
                    result.append(literal_text.replace('|',' '))
                else:
                    result.append(literal_text)
            # if there's a field, output it
            if field_name is not None:
                attr=self.__getfield__(field_name,args,kwargs)
                attr=self.__convertfield__(attr,conversion)
                format_spec = self._vformat(format_spec, args, kwargs,
                                             recursion_depth-1)
                result.append(self.__formatfield__(attr,format_spec))
        return ''.join(result)
    def __formatfield__(self,attr,format_spec):
        try:
            out=format(attr,format_spec)
            formatDict=self.__specparse__(format_spec)
            if self.__fixed__ and formatDict['width']:
                out= out[:formatDict['width']]
                if len(out)<formatDict['width']:
                    out=' '*(formatDict['width']-len(out))+out
            return out
        except:
            formatDict=self.__specparse__(format_spec)
            formatType=formatDict['type']
            formatDict['output']=True
            out=self._typeDict[formatType][0](attr,formatDict,fixedWidth=self.__fixed__,*self._typeDict[formatType][1])
            if self.__fixed__ and formatDict['width']:
                out= out[:formatDict['width']]
                if len(out)<formatDict['width']:
                    out=' '*(formatDict['width']-len(out))+out
            return out
    def __convertfield__(self, value, conversion):
        # do any conversion on the resulting object
        if conversion == 'r':
            return repr(value)
        elif conversion == 's':
            return str(value)
        elif conversion is None:
            return value
        raise ValueError("Unknown conversion specifier {0!s}".format(conversion))
    def __getfield__(self,field_name,args,kwargs):        
        first, rest = field_name._formatter_field_name_split()
        obj=self.__getvalue__(first,args,kwargs)
        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj[i]
        return obj
    def __getvalue__(self,key,args,kwargs):
        if isinstance(key, (int, long)):
            return args[key]
        else:
            return kwargs[key]
    def read(self,inputString):
        """read(inputString:
    Behaves like the inverse of thestandard python str.format (PEP 3101) method for parsing a 
    format spec type string (see python docs for format spec construction) 
    Returns a dictionary of attributes and values
    
    Can't handle nested format specifiers (no obvious method)
    """
        __stringpointer__=0
        parseresults=self.__parse__()
        Results={}
        parseString=inputString
        for result in parseresults:
            if type(result)==str:
                if result==self.__freeformatdelimiter__:
                    #freeformat so split and join string....
                    pass
                elif self.__freeformatdelimiter__ in result:
                    __stringpointer__+=1
                elif self.__freeformatdelimiter__ not in parseresults:   
                    #literal_string - skip
                    __stringpointer__+=len(result)
                    parseString=inputString[__stringpointer__:]
            else:
                if self.__freeformatdelimiter__ in parseresults:
                    parseString=inputString.split()[__stringpointer__]
                else:
                    parseString=inputString[__stringpointer__:]
                if len(parseString.strip()) and parseString.strip() not in ['?']:
                    (attr,val)=self.__stringparse__(parseString,*result)
                    Results[attr]=val
                if self.__freeformatdelimiter__ in parseresults:
                    __stringpointer__+=1
                elif result[1]['width']:
                    __stringpointer__+=int(result[1]['width'])
        for key in Results.keys():
            value=Results.pop(key)
            Results=self.recursiveDictUpdate(Results,self.__attrsplit__(key,value))
        return Results
    def __attrsplit__(self,key,value):
        keys=key.split('.')
        keys.reverse()
        for attr in keys:
            data={}
            data[attr]=value
            value=data.copy()
        return data
    def recursiveDictUpdate(self,d, u):
        """
        Recursively merge or update dict-like objects. 
        >>> recursiveDictUpdate({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
        {'k1': {'k2': {'k3': 3}}, 'k4': 4}
        """
        from collections import Mapping
        for k, v in u.iteritems():
            if isinstance(v, Mapping):
                r = self.recursiveDictUpdate(d.get(k, {}), v)
                d[k] = r
            elif isinstance(d, Mapping):
                d[k] = u[k]
            else:
                d = {k: u[k]}
        return d
    def __stringparse__(self,string,attribute,formatDict,conversion):
        #Handle exponential precision errors - N.B. cannot parse fixed format with more than 2 digits in exponent (e.g. e+123 will fail)
        if formatDict['type'].lower() in ['e']:
            formatDict['width']=len(string.split('e')[0].split('E')[0])+4
        if formatDict['type'].lower() in ['g']:
            if formatDict['precision']:
                x=3+int(formatDict['precision'])
            else:
                x=9
            if 'e' in string[:x].lower():
                formatDict['width']=len(string.split('e')[0].split('E')[0])+4
        #Handle default format precision
        if formatDict['type'].lower()in ['f']:
            if not formatDict['precision'] and not self.__fixed__:
                #PEP 3101 default precision is 6 for 'f','g','e' handling read assuming default precision
                formatDict['precision']=6
                formatDict['width']+=6
                if '.' in string and formatDict['precision']:
                    try:
                        length=string.index('.')+formatDict['precision']+1
                        a=float(string[:length])
                        #Reset length
                        formatDict['width']=length
                    except:
                        pass
        if formatDict['width']:
            string=string[:int(formatDict['width'])]
        if formatDict['align'] and not formatDict['fill']:
            formatDict['fill']=' '
        if formatDict['align']=='<':
            string=string.rstrip(formatDict['fill'])
            formatDict.pop('fill')
            formatDict.pop('align')
        elif formatDict['align']=='^':
            string=string.strip(formatDict['fill'])
            formatDict.pop('fill')
            formatDict.pop('align')
        elif formatDict['align']=='>':
            string=string.ltrip(formatDict['fill'])
            formatDict.pop('fill')
            formatDict.pop('align')
        if formatDict['comma']:
            string=string.replace(',','')
            formatDict.pop('comma')
        formatType=formatDict.pop('type')
        return (attribute,self._typeDict[formatType][0](string,formatDict,fixedWidth=self.__fixed__,*self._typeDict[formatType][1]))
class __FormatStringTestCase(unittest.TestCase):
    """__FormatStringTestCase
    Subclass of unittest.TestCase
    Contains test cases for FormatString Class
    Call using fstr._runTests()
    """
    def setUp(self):
        self.__setattr__('formatString',FormatString(''))
    def tearDown(self):
        self.__delattr__('formatString')
    def test___specparse__(self):
        testFormat='z^ #020,.566f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': '^', 'alternate': True, 'comma': True, 'fill': 'z', 'precision': '566', 'sign': ' ', 'type': 'f', 'width': 20,'zeropadding': True},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='=+20.566d'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': '=', 'alternate': False, 'comma': False, 'fill': False, 'precision': '566', 'sign': '+', 'type': 'd', 'width': 20,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat=' #020,.566f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': True, 'comma': True, 'fill': False, 'precision': '566', 'sign': ' ', 'type': 'f', 'width': 20,'zeropadding': True},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='z^ #020,.566'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': '^', 'alternate': True, 'comma': True, 'fill': 'z', 'precision': '566', 'sign': ' ', 'type': 's', 'width': 20,'zeropadding': True},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='#020,.566f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': True, 'comma': True, 'fill': False, 'precision': '566', 'sign': False, 'type': 'f', 'width': 20,'zeropadding': True},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='20.566f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': '566', 'sign': False, 'type': 'f', 'width': 20,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='z^ #020,.566f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': '^', 'alternate': True, 'comma': True, 'fill': 'z', 'precision': '566', 'sign': ' ', 'type': 'f', 'width': 20,'zeropadding': True},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat=''
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 's', 'width': False,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6c'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'c', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6b'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'b', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6x'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'x', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6d'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'd', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6o'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'o', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6X'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'X', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6e'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'e', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6E'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'E', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6f'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'f', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6F'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'F', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6g'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'g', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6G'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'G', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6n'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 'n', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6%'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': '%', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
        testFormat='6s'
        self.assertEqual(self.formatString.__specparse__(testFormat),{'output':False,'align': False, 'alternate': False, 'comma': False, 'fill': False, 'precision': False, 'sign': False, 'type': 's', 'width': 6,'zeropadding': False},'__specparse__ Error: '+str(testFormat)+'|'+str(self.formatString.__specparse__(testFormat)))
    def test___setformatstring__(self):
        self.formatString.__setformatstring__('{a.b:10.5f} {a.c:10.5f}{b.a:9.3f}                      {b.b:6f}')
        self.assertEqual(self.formatString.__formatstring__,'{a.b:10.5f} {a.c:10.5f}{b.a:9.3f}                      {b.b:6f}')
    def test___parse__(self):
        self.test___setformatstring__()
        self.assertEqual(self.formatString.__parse__(),[('a.b', {'output':False,'zeropadding': False, 'align': False, 'alternate': False, 'precision': '5', 'sign': False, 'width': 10, 'comma': False, 'type': 'f', 'fill': False}, None), ' ', 
                                                        ('a.c', {'output':False,'zeropadding': False, 'align': False, 'alternate': False, 'precision': '5', 'sign': False, 'width': 10, 'comma': False, 'type': 'f', 'fill': False}, None), 
                                                        ('b.a', {'output':False,'zeropadding': False, 'align': False, 'alternate': False, 'precision': '3', 'sign': False, 'width': 9, 'comma': False, 'type': 'f', 'fill': False}, None), '                      ', 
                                                        ('b.b', {'output':False,'zeropadding': False, 'align': False, 'alternate': False, 'precision': False, 'sign': False, 'width': 6, 'comma': False, 'type': 'f', 'fill':False}, None)],
                         '__parse__ Error: '+str(self.formatString.__parse__()))
    def test___stringparse__(self):
        testCase=self.formatString.__stringparse__('abc ','a.x',self.formatString.__specparse__('<4s'),None)
        self.assertEqual(testCase,('a.x','abc'),'__stringparse__ Error: '+str(testCase))
        testCase=self.formatString.__stringparse__('abcd','a',self.formatString.__specparse__('s'),None)
        self.assertEqual(testCase,('a','abcd'),'__stringparse__ Error: '+str(testCase))
    def test_format(self):
        self.formatString.__setformatstring__('{0:10.5f} {1:10.5f}{2:9.3f}                      {3:6f}{a.x:6s}') 
        class A(object):
            x='abcdef'
        a=A()       
        self.assertEqual(self.formatString.format(121.355,84.23,11.2,11,a=a),' 121.35500   84.23000   11.200                      11.000000abcdef','format Error: '+str(self.formatString.format(121.355,84.23,11.2,11,a=a)))
        self.formatString.__setformatstring__('{0:f}|{1:f}|{2:f}|ABC|{3:f}|{a.x:s}')    
        self.assertEqual(self.formatString.format(121.355,84.23,11.2,11,a=a),'121.355000 84.230000 11.200000 ABC 11.000000 abcdef','format Error: '+str(self.formatString.format(121.355,84.23,11.2,11,a=a)))
        self.formatString.__setformatstring__('XYZ|{0:f}|{1:f}|{2:f}|ABC|{3:f}|{a.x:s}')    
        self.assertEqual(self.formatString.format(121.355,84.23,11.2,11,a=a),'XYZ 121.355000 84.230000 11.200000 ABC 11.000000 abcdef','format Error: '+str(self.formatString.format(121.355,84.23,11.2,11,a=a)))
    def test_read(self):
        self.formatString.__setformatstring__('{0:10.5f} {1:10.5f}{2:9.3f}                      {3:6f} {a.b:6b}')        
        self.assertEqual(self.formatString.read(' 121.35500   84.23000   11.200                      11.001000 000101'),{'0':121.355,'1':84.23,'2':11.2,'3':11.001,'a':{'b':5}},'format Error: '+str(self.formatString.read(' 121.35500   84.23000   11.200                      11.001000 000101')))
        self.formatString.__setformatstring__('{0:5c} {1:4d} {2:7o} {3:5x} {4:6X}')        
        self.assertEqual(self.formatString.read('    y 8423  301255   3dd    3DD'),{'0':121,'1':8423,'2':98989,'3':989,'4':989},'format Error: '+str(self.formatString.read('    y 8423  301255   3dd    3DD')))
        self.formatString.__setformatstring__('{0:5e} {1:4E} {2:7f} {3:5F}')      
        self.assertEqual(self.formatString.read('1.234000e+01 1.256000E+01 123.456000 12.345000'),{'0':12.34,'1':12.56,'2':123.456,'3':12.345},'format Error: '+str(self.formatString.read('1.234000e+01 1.256000E+01 123.456000 12.345000')))
        self.formatString.__setformatstring__('{0:6g} {1:6.2G}')  
        self.assertEqual(self.formatString.read(' 12345 1.2E+02'),{'0':12345,'1':120},'format Error: '+str(self.formatString.read(' 12345 1.2E+02'))) 
        self.formatString.__setformatstring__('{picks.pt:6.0f} {picks.st:6.2f}')  
        self.assertEqual(self.formatString.read(' 12345 123.23'),{'picks':{'pt':12345.0,'st':123.23}},'format Error: '+str(self.formatString.read(' 12345 123.23')))
        self.formatString.__setformatstring__('XYZ|{0:f}|{1:f}|{2:f}|ABC|{3:f}|{a.x:s}')    
        self.assertEqual(self.formatString.read('XYZ 121.355000 84.230000 11.200000 ABC 11.000000 abcdef'),{'0':121.355,'1':84.23,'2':11.2,'3':11.0,'a':{'x':'abcdef'}},'format Error: '+str(self.formatString.read('XYZ 121.355000 84.230000 11.200000 ABC 11.000000 abcdef')))
    
    def test___fixed__(self):
        self.formatString.__fixed__=True
        self.formatString.__setformatstring__('{0:4.5f} {1:10.5f}{2:9.3f}                      {3:6f}{a.x:6s}') 
        class A(object):
            x='abcdef'
        a=A()       
        self.assertEqual(self.formatString.format(121.355,84.23,11.2,11,a=a),'121.   84.23000   11.200                      11.000abcdef','format Error: '+str(self.formatString.format(121.355,84.23,11.2,11,a=a)))

def __debugTestSuite():
    suite=unittest.TestSuite()
    formatStringSuite = unittest.TestLoader().loadTestsFromTestCase(__FormatStringTestCase)
    suite.addTests(formatStringSuite._tests)
    return suite
def __testSuite():
    formatStringSuite = unittest.TestLoader().loadTestsFromTestCase(__FormatStringTestCase)
    return unittest.TestSuite([formatStringSuite])
def _runTests():
    suite=__testSuite()
    unittest.TextTestRunner(verbosity=4).run(suite)
def _debugTests():
    suite=__debugTestSuite()
    import ipdb,sys
    for test in suite:
        try:
            test.debug()
        except Exception,e:
            if type(e)==AssertionError:                
                ipdb.post_mortem(sys.exc_info()[2])
            else:
                try:
                    from IPython.core.ultratb import VerboseTB
                    vtb=VerboseTB(call_pdb=1)
                    vtb(*sys.exc_info())
                except:
                    import traceback
                    print'\n'
                    traceback.print_exc()
                ipdb.post_mortem(sys.exc_info()[2])
if  __name__=='__main__':
    _runTests()