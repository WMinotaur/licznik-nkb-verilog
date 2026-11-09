`timescale 1ns/1ps
// ---------------------------------------------------------------------------
// Licznik NKB 0..30 z wymuszeniem wartosci 31 - opis behawioralny
//
//   x = 0 : na wyjsciu kolejno 0, 1, ..., 30, po 30 znowu 0
//   x = 1 : na wyjsciu 31; powrot x = 0 rozpoczyna sekwencje od 0
//
// Automat Moore'a: wyjscie y jest bezposrednio stanem (rejestr 5-bitowy).
// ---------------------------------------------------------------------------
module licznik (
    input            clk,
    input            rst,   // reset synchroniczny, aktywny stanem 1
    input            x,
    output reg [4:0] y
);
    always @(posedge clk) begin
        if (rst)
            y <= 5'd0;
        else if (x)
            y <= 5'd31;          // wymuszenie 31
        else if (y >= 5'd30)
            y <= 5'd0;           // po 30 (oraz po 31) start od 0
        else
            y <= y + 5'd1;       // zwykle liczenie w NKB
    end
endmodule
