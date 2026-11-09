`timescale 1ns/1ps
// ---------------------------------------------------------------------------
// Ten sam uklad zrealizowany strukturalnie: 5 przerzutnikow D + bramki.
//
// Rownania wzbudzen (wyprowadzenie w sprawozdaniu):
//   W  = Q4 Q3 Q2 Q1                (stan 30 lub 31)
//   D0 = x + ~W * ~Q0
//   D1 = x + ~W * (Q1 ^ Q0)
//   D2 = x + ~W * (Q2 ^ Q1 Q0)
//   D3 = x + ~W * (Q3 ^ Q2 Q1 Q0)
//   D4 = x + ~W * (Q4 ^ Q3 Q2 Q1 Q0)
// ---------------------------------------------------------------------------

// Czesc kombinacyjna: funkcja przejsc  (Q, x) -> D
module licznik_next (
    input  [4:0] q,
    input        x,
    output [4:0] d
);
    wire w  = q[4] & q[3] & q[2] & q[1];
    wire nw = ~w;

    assign d[0] = x | (nw & ~q[0]);
    assign d[1] = x | (nw & (q[1] ^ q[0]));
    assign d[2] = x | (nw & (q[2] ^ (q[1] & q[0])));
    assign d[3] = x | (nw & (q[3] ^ (q[2] & q[1] & q[0])));
    assign d[4] = x | (nw & (q[4] ^ (q[3] & q[2] & q[1] & q[0])));
endmodule

// Przerzutnik D z synchronicznym resetem
module dff (
    input      clk,
    input      rst,
    input      d,
    output reg q
);
    always @(posedge clk)
        q <= rst ? 1'b0 : d;
endmodule

// Caly uklad: 5 przerzutnikow D sterowanych przez licznik_next
module licznik_bramki (
    input        clk,
    input        rst,
    input        x,
    output [4:0] y
);
    wire [4:0] d;

    licznik_next nxt (.q(y), .x(x), .d(d));

    genvar i;
    generate
        for (i = 0; i < 5; i = i + 1) begin : ff
            dff u (.clk(clk), .rst(rst), .d(d[i]), .q(y[i]));
        end
    endgenerate
endmodule
