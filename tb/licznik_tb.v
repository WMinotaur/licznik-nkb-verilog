`timescale 1ns/1ps
// ---------------------------------------------------------------------------
// Testbench: sprawdza jednoczesnie wersje behawioralna (licznik)
// i bramkowa (licznik_bramki) oraz wyczerpujaco funkcje przejsc.
// ---------------------------------------------------------------------------
module licznik_tb;
    reg        clk = 1'b0;
    reg        rst = 1'b1;
    reg        x   = 1'b0;
    wire [4:0] y;      // wyjscie wersji behawioralnej
    wire [4:0] y_b;    // wyjscie wersji bramkowej
    integer    errors = 0;
    integer    i, s, xi;

    licznik        dut   (.clk(clk), .rst(rst), .x(x), .y(y));
    licznik_bramki dut_b (.clk(clk), .rst(rst), .x(x), .y(y_b));

    // osobna instancja czesci kombinacyjnej do testu wyczerpujacego
    reg  [4:0] tq;
    reg        tx;
    wire [4:0] td;
    licznik_next nxt_test (.q(tq), .x(tx), .d(td));

    always #5 clk = ~clk;          // zegar o okresie 10 ns

    // model odniesienia - specyfikacja zadania
    function [4:0] model;
        input [4:0] q;
        input       xin;
        begin
            if (xin)          model = 5'd31;
            else if (q >= 30) model = 5'd0;
            else              model = q + 5'd1;
        end
    endfunction

    // jeden takt: ustaw x, poczekaj na zbocze, sprawdz obie wersje
    task step;
        input       xin;
        input [4:0] expected;
        begin
            x = xin;
            @(posedge clk); #1;
            if (y !== expected || y_b !== expected) begin
                $display("%t | x=%b | y=%2d (%b) | y_b=%2d | BLAD, oczekiwano %0d",
                         $time, xin, y, y, y_b, expected);
                errors = errors + 1;
            end else
                $display("%t | x=%b | y=%2d (%b) | y_b=%2d | ok",
                         $time, xin, y, y, y_b);
        end
    endtask

    initial begin
        $timeformat(-9, 0, " ns", 7);
        $dumpfile("licznik.vcd");
        $dumpvars(0, licznik_tb);

        $display("   czas | wejscie | wyjscie (NKB) | wersja bramkowa | wynik");
        $display("--- reset ---");
        @(posedge clk); #1;
        rst = 1'b0;
        $display("%t | rst   | y=%2d (%b) | y_b=%2d |", $time, y, y, y_b);

        $display("--- T1: x=0, pelna sekwencja 0..30 i powrot do 0 ---");
        for (i = 1; i <= 30; i = i + 1) step(0, i);
        step(0, 0);
        for (i = 1; i <= 5; i = i + 1) step(0, i);

        $display("--- T2: x=1 w trakcie liczenia -> 31 (utrzymywane) ---");
        step(1, 31);
        step(1, 31);
        step(1, 31);

        $display("--- T3: x=0 po 31 -> sekwencja od nowa ---");
        step(0, 0);
        step(0, 1);
        step(0, 2);

        $display("--- T4: x=1 w stanie 30 ---");
        for (i = 3; i <= 30; i = i + 1) step(0, i);
        step(1, 31);
        step(0, 0);

        $display("--- T5: test wyczerpujacy funkcji przejsc (32 stany x 2) ---");
        for (s = 0; s < 32; s = s + 1)
            for (xi = 0; xi < 2; xi = xi + 1) begin
                tq = s; tx = xi; #1;
                if (td !== model(tq, tx)) begin
                    $display("BLAD: Q=%0d x=%0d -> D=%0d, oczekiwano %0d",
                             tq, tx, td, model(tq, tx));
                    errors = errors + 1;
                end
            end
        $display("sprawdzono 64 kombinacje");

        $display("========================================");
        if (errors == 0) $display("OK: wszystkie testy przeszly");
        else             $display("FAIL: liczba bledow = %0d", errors);
        $finish;
    end
endmodule
