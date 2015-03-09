import re

class vcd_reader:
    def __init__(self,file_name):
        """INIT function. signal_symbol dictionary and transition dictionary are created"""
        self.signal_symbol,self.transitions=self.read_file(file_name)
        #pass
        
    def read_file(self,file_name):
        """Parses the file and returns the signal-symbol pair and transition history"""
        signal_symbol_dict={}
        transition_dict={}
        current_scope=''
        with open(file_name) as f:
            file_content=f.readlines()
            change_dump_started=0
        for line_no in range(len(file_content)):
            if re.match(r'^\$date',file_content[line_no]):
                date=file_content[line_no+1]
            if re.match(r'^\$version',file_content[line_no]):
                version=file_content[line_no+1]
            if re.match(r'^\$timescale',file_content[line_no]):
                timescale_string=file_content[line_no+1]
                matchObj=re.match(r'^[\s\t]*(\d+)\s*(\w+)',timescale_string)
                timescale_dict={'fs':1e-15,'ps':1e-12,'ns':1e-9,'us':1e-6,'ms':1e-3}
                if matchObj:
                    timescale=float(matchObj.group(1))*timescale_dict[matchObj.group(2)]
                    #print timescale
            matchObj=re.match(r'^\$scope\s+module\s+(\w+)\s+\$end',file_content[line_no])
            if matchObj:
                current_scope=current_scope+'/'+matchObj.group(1)
                print current_scope
            matchObj=re.match(r'^\$upscope',file_content[line_no])
            if matchObj:
                scopes=current_scope.split('/')
                current_scope=''
                for scope in range(len(scopes)-1):
                    if scopes[scope]!='':
                        current_scope=current_scope+'/'+scopes[scope]
                print current_scope
            matchObj=re.match(r'^\$var\s+(\w+)\s+(\d+)\s+(\S+?)\s+(\S+)\s+\$end$', file_content[line_no])
            if matchObj:
                #print matchObj.group(3)
                #print matchObj.group(2)
                current_signal=current_scope+'/'+matchObj.group(4)
                signal_symbol_dict[current_signal]=matchObj.group(3)
                transition_dict[matchObj.group(3)]=[[],[]]
    
            matchObj=re.match(r'^\$dumpvars', file_content[line_no])
            matchObj2=re.match(r'^\$enddefinitions', file_content[line_no])
            if matchObj or matchObj2:
                change_dump_started=1
                timestamp=0
                #print "Change dump started"

            matchObj=re.match(r'^\#(\d+)', file_content[line_no])
            if matchObj:
                timestamp=matchObj.group(1)
                
            matchObj=re.match(r'^(\S)(\S)$',file_content[line_no])
            if matchObj and change_dump_started==1 and matchObj.group(2) in transition_dict.keys() and matchObj.group(1)!='#':
                transition_dict[matchObj.group(2)][0].append(timestamp)
                transition_dict[matchObj.group(2)][1].append(matchObj.group(1))               
            
            matchObjBus=re.match(r'^b(\w+) (\S)$',file_content[line_no])
            if matchObjBus and change_dump_started==1 and matchObjBus.group(2) in transition_dict.keys() and matchObjBus.group(1)!='#':
                transition_dict[matchObjBus.group(2)][0].append(timestamp)
                transition_dict[matchObjBus.group(2)][1].append(matchObjBus.group(1)) 
        return signal_symbol_dict,transition_dict 

    def symbols(self,array_of_names):
        """Returns a dictionary with signal-symbol pairs
        When a list of names is sent, make sure you have '/' at the beginning of the hierarchy.
        For eg. query for ['/clk'] and not ['clk']"""
        dict_to_return={}
        for item in array_of_names:
            dict_to_return[item]=self.signal_symbol[item]
        return dict_to_return
    def transitions(self):
        pass

