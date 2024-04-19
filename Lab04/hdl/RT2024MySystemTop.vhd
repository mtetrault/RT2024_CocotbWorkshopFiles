-- Author - Marc-André Tétrault
--          Université de Sherbrooke
--			IEEE NPSS Real Time Conference 2024
--          Cocotb workshop


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
 
 
entity rt2024mysystemtop is
	port(
		clk             : in std_logic;
		reset           : in std_logic;
		rx_uart_serial_in         : in std_logic;
		tx_uart_serial_out      : out std_logic
	);
end entity rt2024mysystemtop;
 
 
architecture Behavioural of rt2024mysystemtop is
 
 
component UART_RX is
  generic (
    g_CLKS_PER_BIT : integer := 115     -- Needs to be set correctly
    );
  port (
    i_Clk       : in  std_logic;
    i_RX_Serial : in  std_logic;
    o_RX_DV     : out std_logic;
    o_RX_Byte   : out std_logic_vector(7 downto 0)
    );
end component;

 
component UART_TX is
  generic (
    g_CLKS_PER_BIT : integer := 115     -- Needs to be set correctly
    );
  port (
    i_Clk       : in  std_logic;
    i_TX_DV     : in  std_logic;
    i_TX_Byte   : in  std_logic_vector(7 downto 0);
    o_TX_Active : out std_logic;
    o_TX_Serial : out std_logic;
    o_TX_Done   : out std_logic
    );
end component;

 
component square_root is
	generic(
		WIDTH	: positive := 8
	);
	port(
		clk             : in std_logic;
		reset           : in std_logic;
		-- Input interface
		arg_valid       : in std_logic;
		arg             : in unsigned (WIDTH - 1 downto 0);

		-- output interface
		sqrt_valid      : out std_logic;
		sqrt_res        : out unsigned (WIDTH/2 - 1 downto 0)
	);
end component;
 
 
signal rx_uart_data_valid : std_logic;
signal rx_uart_data       : std_logic_vector(7 downto 0);


signal sqrt_res_ready : std_logic;
signal sqrt_res       : unsigned(7 downto 0) := (others => '0');

signal tx_uart_active : std_logic;
signal tx_uart_done   : std_logic;
 
begin

inst_rx_uart : UART_RX 
  generic map (
    g_CLKS_PER_BIT => 10     -- for 115kbps with 10 Mhz clock
    )
  port map(
    i_Clk       => clk,
    i_RX_Serial => rx_uart_serial_in,
    o_RX_DV     => rx_uart_data_valid,
    o_RX_Byte   => rx_uart_data
    );
	
inst_tx_uart : UART_TX
  generic map(
    g_CLKS_PER_BIT => 10
    )
  port map(
    i_Clk       => clk,
    i_TX_DV     => sqrt_res_ready,
    i_TX_Byte   => std_logic_vector(sqrt_res),
    o_TX_Active => tx_uart_active,
    o_TX_Serial => tx_uart_serial_out,
    o_TX_Done   => tx_uart_done
    );
	
inst_square_root : square_root
	generic map(
		WIDTH	=> 8
	)
	port map(
		clk             => clk,
		reset           => reset,
		-- Input interface
		arg_valid       => rx_uart_data_valid,
		arg             => unsigned(rx_uart_data),

		-- output interface
		sqrt_valid      => sqrt_res_ready,
		sqrt_res        => sqrt_res(3 downto 0)
	);
 
end Behavioural;
 
