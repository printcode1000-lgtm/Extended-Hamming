module hamming_11_7_encoder(
    input  logic [6:0] data,
    output logic [10:0] codeword
);
    logic p1, p2, p4, p8;
    always_comb begin
        p1 = data[0] ^ data[1] ^ data[3] ^ data[4] ^ data[6];
        p2 = data[0] ^ data[2] ^ data[3] ^ data[5] ^ data[6];
        p4 = data[1] ^ data[2] ^ data[3];
        p8 = data[4] ^ data[5] ^ data[6];
        // Vector index 0 corresponds to one-based code position 1.
        codeword = {data[6], data[5], data[4], p8, data[3], data[2], data[1], p4, data[0], p2, p1};
    end
endmodule

module extended_hamming_12_7_encoder(
    input  logic [6:0] data,
    output logic [11:0] codeword
);
    logic [10:0] base;
    hamming_11_7_encoder base_encoder(.data(data), .codeword(base));
    always_comb codeword = {^base, base};
endmodule

