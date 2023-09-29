import os
import json
from configparser import ConfigParser
import re
#def builder(mode, content):

def main():#
    conf = ConfigParser()
    conf.read("./libinfo.ini")
    lib_dict = {}
    for sec in conf.sections():
        lib_dict.update({sec:{}})
        for opt in conf.options(sec):
            value = conf.get(sec, opt)
            #


    with open("./high_level_test.json", "r") as file:
        content_list = json.load(file)
        for i in range(len(content_list)):
            optype = content_list[i]['optype']
            # optypes in high_level: MM, split, transpose, softmax, merge, MADD, layernorm, gelu.
            # optypes in dag_match:  Identity, Constant, Shape, Expand, Gather, Add, Layernorm, Mul, MatMul, 
            #                        Reshape, Transpose, Div, Softmax, Gelu, Gemm, Tanh, Relu
            # seemingly not found
            dimension_1=content_list[i]["input_size"][0][0]
            dimension_2=content_list[i]["input_size"][0][1]
            if(optype == 'gelu'):
                modified_gelu=open("./modified_verilog/nnlut_gelu.v","r+")
                with open("./autotrans_spec_1.0/op_trans/nnlut_gelu_64.v","r+") as gelufile:
                    data_lines=gelufile.readlines()
                    for line in data_lines:
                        if 'parameter DIMENTION = 64' in line:
                            modified_gelu.write(line.replace('parameter DIMENTION = 64', 'parameter DIMENTION = {num}'.format(num=dimension_1)))
                        else:
                            modified_gelu.write(line)

            # elif(optype == 'split'):

            # elif(optype == 'transpose'):

            # elif(optype == 'softmax'):
                
            # elif(optype == 'merge'):

            # elif(optype == 'MADD'):

            elif(optype == 'layernorm'):
                modified_layernorm=open("./modified_verilog/nnlut_layernorm.v","r+")
                with open("./autotrans_spec_1.0/op_trans/layernorm_nnlut.v","r+") as layernormfile:
                    data_lines=layernormfile.readlines()
                    for line in data_lines:
                        if 'parameter   INPUT_NUM = 768' in line:
                            modified_layernorm.write(line.replace('parameter   INPUT_NUM = 768,', 'parameter INPUT_NUM = {num}'.format(num=dimension_2)))
                        else:
                            modified_layernorm.write(line)

            
            # elif(optype == 'MM'):



if __name__ == "__main__":
    main()