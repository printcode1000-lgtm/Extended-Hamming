module tb_hamming_encoders;
    logic [6:0] data;
    logic [10:0] h117;
    logic [11:0] eh127;
    hamming_11_7_encoder u1(.data(data), .codeword(h117));
    extended_hamming_12_7_encoder u2(.data(data), .codeword(eh127));
    initial begin
        for (int i = 0; i < 128; i++) begin
            data = i[6:0]; #1;
            if (^eh127 !== 1'b0) $fatal(1, "Overall parity failed for %0d", i);
        end
        $display("PASS: 128 data words verified");
        $finish;
    end
endmodule

