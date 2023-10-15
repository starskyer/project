import os
import json
from configparser import ConfigParser
import re

class myconf(ConfigParser): # ensure uppercase
    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


def read_libinfo(libinfo_file): # for example: lib_dict = {'code': {'Gelu_method1': ['input_shape', 'output_shape']}}
    conf = myconf()
    conf.read(libinfo_file)

    lib_dict = {}
    for sec in conf.sections():
        lib_dict.update({sec:{}})
        for opt in conf.options(sec):
            value = conf.get(sec, opt) # for example: value = 'input_shape, output_shape'
            value_list = value.split(', ')
            lib_dict[sec].update({opt:value_list})

    return lib_dict

# class builder includes some methods
def builder(mode, network_file, lib_dict):
    # find operator in lib_dict
    with open(network_file, "r") as file:
        content_list = json.load(file)
        for i in range(len(content_list)): # content_list[i] represents an operator
            optype = content_list[i]["op_type"]
            # optypes in high_level: 'MAC', 'Split', 'Transpose', 'MatMul', 'Softmax', 'Merge', 'Add', 'Layernorm', 'Gelu'
            input_shape= content_list[i]["input_shape"] # list
            output_shape = content_list[i]["output_shape"] # list
            op_name=content_list[i]["op_name"] # string



            found = 0
            method_dict = {}
            for method in lib_dict[mode].items(): # for example: method = ('Gelu_method1', ['input_shape', 'output_shape'])
                method_name = method[0]
                method_params = method[1]
                if optype in method_name.split('_'):
                    found = 1
                    method_dict[method_name] = method_params 
                    # for example: if optype is 'Add',
                    # method_dict = {'Add_method1': ['input_shape', 'output_shape'], 'Add_method2': ['input_shape', 'output_shape']}

            # print(method_dict)

            if found == 0:
                print("Generation failed: Cannot find optype \"" + optype + "\" in libinfo.")

            else:
                modified_file = open("./modified_verilog/" + op_name + "_modified.v", "w+") # name of modified operator
                if len(method_dict) == 1:
                    name="{}_method1".format(optype) # name is the generator method (operator + '_' + tag)
                    address = "./autotrans_spec_1.0/op_trans/{}.v".format(name) # address is the operator file to be modified
                else:
                    print('''Multiple methods for operator \"" + optype +"\" was found.
                          ''') # 
                    
                    method = "test" # TODO: method应该是用户输入的字符串

                    name="{}_{}".format(optype, method)
                    address = "./autotrans_spec_1.0/op_trans/{}.v".format(name)

                with open(address) as file_to_be_modified: 
                    content=file_to_be_modified.read()
                    modified_content = file_to_be_modified.read().replace('\n', ' ')  # copy the file for revision
                    search=re.compile('//(input_shape\[.*?\]\[.*?\])') # Regular expression finds "input_shape[index][index]" in the comments
                    input_shape_list=search.findall(content) # find all "//input_shape[index][index]"
 
 
                    if "input_shape" in method_dict[name]: # (In libinfo.ini) The method requires "input_shape" parameter
                        matching_lines = []  # 用于存储匹配的行
                        for index1,one_input_shape in enumerate(input_shape):
                            for index2,everyParameter in enumerate(one_input_shape):
                                print("input_shape"+"[{}]".format(index1)+"[{}]".format(index2))
                                if ("input_shape"+"[{}]".format(index1)+"[{}]".format(index2)) in input_shape_list:#如果input_shape给了的话,此时去匹配对应的行进行参数修改
                                        # 构建新的行内容
                                        keyword_to_match = re.escape("input_shape[{index1}][{index2}]".format(index1=index1,index2=index2))  
                                        print(keyword_to_match)    
                                        print(input_shape[index1][index2])
                                        a = "=(.*)(?=(?:,)\s*\/\/" + keyword_to_match + ')'
                                        #(?= ... ) 是正则表达式中的正向预查（Positive Lookahead）构造，它用于匹配一个字符串后面的内容，但不包括这个内容在匹配的结果中。
                                        pattern_a = re.compile(a)  
                                        content = re.sub(pattern_a,"={}".format(input_shape[index1][index2]),content)
                                        # change content

                    # if "output_shape" in method_dict[name]:
                                        
                        modified_file.write(content)#写入

                             
                            
                    

            # if(optype == 'gelu'):
            #     modified_gelu=open("./modified_verilog/nnlut_gelu.v","r+")
            #     with open("./autotrans_spec_1.0/op_trans/nnlut_gelu_64.v","r+") as gelufile:
            #         data_lines=gelufile.readlines()
            #         for line in data_lines:
            #             if 'parameter DIMENTION = 64' in line:
            #                 modified_gelu.write(line.replace('parameter DIMENTION = 64', 'parameter DIMENTION = {num}'.format(num=dimension_1)))
            #             else:
            #                 modified_gelu.write(line)

            # # elif(optype == 'split'):

            # # elif(optype == 'transpose'):

            # # elif(optype == 'softmax'):
            # #     modified_softmax=open("./modified_verilog/nnlut_softmax_modified.v","r+")
            # #     with open("./autotrans_spec_1.0/op_trans/nnlut_softmax_128_quant.v","r+") as softmaxfile:
            # #         data_lines=softmaxfile.readlines()
            # #         for line in data_lines:
            # #             if 'parameter DIMENTION = 64' in line:
            # #                 modified_softmax.write(line.replace('parameter DIMENTION = 64', 'parameter DIMENTION = {num}'.format(num=dimension)))
            # #             else:
            # #                 modified_softmax.write(line)
                
            # # elif(optype == 'merge'):

            # elif(optype == 'MADD'):
            #     modified_MADD=open("./modified_verilog/Madder.v","r+")
            #     with open("./autotrans_spec_1.0/op_trans/Madder_128_768.v","r+") as MADDfile:
            #         data_lines=MADDfile.readlines()
            #         for line in data_lines:
            #             if "parameter ADDER_NUM = 'd128" in line:
            #                 modified_MADD.write(line.replace("parameter ADDER_NUM = 'd128", "parameter ADDER_NUM = 'd{num}".format(num=dimension_1)))
            #             else:
            #                 modified_MADD.write(line)

            # elif(optype == 'layernorm'):
            #     modified_layernorm=open("./modified_verilog/nnlut_layernorm.v","r+")
            #     with open("./autotrans_spec_1.0/op_trans/layernorm_nnlut_128_768.v","r+") as layernormfile:
            #         data_lines=layernormfile.readlines()
            #         for line in data_lines:
            #             if 'parameter   SENTENCE_NUM=128' in line:
            #                 modified_layernorm.write(line.replace('parameter   SENTENCE_NUM=128,', 'parameter SENTENCE_NUM = {num}'.format(num=dimension_1)))
            #             else:
            #                 modified_layernorm.write(line)

            
            # # elif(optype == 'MM'):




def main():
    lib_dict = read_libinfo("autotrans_spec_1.0/libinfo.ini")
    builder("code","autotrans_spec_1.0/test.json",lib_dict)  
    print(lib_dict)



if __name__ == "__main__":
    main()