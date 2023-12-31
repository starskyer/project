module Add_method1
#(
    parameter ADDER_NUM = 'd128,//input_shape[0][1]
    parameter DIMENTION = 'd768, //input_shape[0][2]
    parameter WIDTH_ADDEND = 'd8, //input_shape[0][0]
    parameter WIDTH_SUM = WIDTH_ADDEND
)(
//********************************* System Signal *********************************
    input                                                           clk_p,
    input                                                           rst_n,
//********************************* Input Signal *********************************
    input signed  [WIDTH_ADDEND * ADDER_NUM * DIMENTION - 1   :   0]  addend1,
    input signed  [WIDTH_ADDEND * ADDER_NUM * DIMENTION - 1   :   0]  addend2,

//********************************* Output Signal *********************************
    output signed [WIDTH_SUM * ADDER_NUM * DIMENTION - 1      :   0]  sum,
    output sum_valid
);
    
//********************************* Loop Integer **********************************
    genvar                                               i;

    wire signed [WIDTH_ADDEND * DIMENTION - 1   :   0]  addend1_mem [ADDER_NUM - 1 : 0];
    wire signed [WIDTH_ADDEND * DIMENTION - 1   :   0]  addend2_mem [ADDER_NUM - 1 : 0];
    wire signed [WIDTH_ADDEND * DIMENTION - 1   :   0]  sum_mem     [ADDER_NUM - 1 : 0];

    generate
        for(i = 0; i < ADDER_NUM; i = i + 1) begin
            assign addend1_mem[i] = addend1[(i + 1) * WIDTH_ADDEND * DIMENTION - 1 : i * WIDTH_ADDEND * DIMENTION];
            assign addend2_mem[i] = addend2[(i + 1) * WIDTH_ADDEND * DIMENTION - 1 : i * WIDTH_ADDEND * DIMENTION];
            assign sum[(i + 1) * WIDTH_ADDEND * DIMENTION - 1 : i * WIDTH_ADDEND * DIMENTION] = sum_mem[i];
            adder_768 #(.DIMENTION(DIMENTION), .WIDTH_ADDEND(WIDTH_ADDEND), .WIDTH_SUM(WIDTH_SUM)) u_adder_768
            (.addend1(addend1_mem[i]), .addend2(addend2_mem[i]), .sum(sum_mem[i]));
        end
    endgenerate

endmodule