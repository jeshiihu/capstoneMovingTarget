library ieee;
use ieee.std_logic_1164.all;
 
entity EasyDriver_tb is
end EasyDriver_tb;
 
architecture behave of EasyDriver_tb is
  signal sig_clk : std_logic := '0';
  signal sig_rst : std_logic := '1';

  signal sig_step_write_n   : std_logic := '1';
  signal sig_step_data      : std_logic_vector(15 downto 0) := (others => '0');

  signal sig_dir_write_n    : std_logic := '1';
  signal sig_dir_data       : std_logic_vector(7 downto 0)  := (others => '0');

  signal sig_period_write_n : std_logic := '1';
  signal sig_period_data    : std_logic_vector(31 downto 0) := (others => '0');

  signal sig_duty_write_n   : std_logic := '1';
  signal sig_duty_data      : std_logic_vector(31 downto 0) := (others => '0');

  signal cond_dir    : std_logic;
  signal cond_step   : std_logic;
  signal cond_enable : std_logic;

component Easy_Driver is
  port (
	clk                : in  std_logic                     := '0';             --               clock.clk
	reset_n            : in  std_logic                     := '0';             --               reset.reset_n
	
	conduit_end_dir    : out std_logic;                                        --         conduit_end.dir
	conduit_end_step   : out std_logic;                                        --                    .step
	conduit_end_enable : out std_logic;                                        --                    .enable
	
	step_read_n        : in  std_logic                     := '0';             --   avalon_slave_step.read_n
	step_readdata      : out std_logic_vector(15 downto 0);                    --                    .readdata
	step_write_n       : in  std_logic                     := '0';             --                    .write_n
	step_writedata     : in  std_logic_vector(15 downto 0) := (others => '0'); --                    .writedata
	
	dir_read_n         : in  std_logic                     := '0';             --    avalon_slave_dir.read_n
	dir_readdata       : out std_logic_vector(7 downto 0);                     --                    .readdata
	dir_write_n        : in  std_logic                     := '0';             --                    .write_n
	dir_writedata      : in  std_logic_vector(7 downto 0)  := (others => '0'); --                    .writedata
	
	period_read_n      : in  std_logic                     := '0';             -- avalon_slave_period.read_n
	period_readdata    : out std_logic_vector(31 downto 0);                    --                    .readdata
	period_write_n     : in  std_logic                     := '0';             --                    .write_n
	period_writedata   : in  std_logic_vector(31 downto 0) := (others => '0'); --                    .writedata
	
	duty_read_n        : in  std_logic                     := '0';             --   avalon_slave_duty.read_n
	duty_readdata      : out std_logic_vector(31 downto 0);                    --                    .readdata
	duty_write_n       : in  std_logic                     := '0';             --                    .write_n
	duty_writedata     : in  std_logic_vector(31 downto 0) := (others => '0')  --                    .writedata
);
end component Easy_Driver;
   
begin   
  pwm_INST : Easy_Driver 
    port map (
      reset_n  => sig_rst,
      clk      => sig_clk,

      step_write_n   => sig_step_write_n,
      dir_write_n    => sig_dir_write_n,
      period_write_n => sig_period_write_n,
      duty_write_n   => sig_duty_write_n,

      step_writedata   => sig_step_data,
      dir_writedata    => sig_dir_data,
      period_writedata => sig_period_data,
      duty_writedata   => sig_duty_data,

      conduit_end_dir    => cond_dir,
      conduit_end_step   => cond_step,
      conduit_end_enable => cond_enable
  );
  
process is
  begin
	sig_rst <= '1';
 	sig_clk <= '0';
 	wait for 50 ns;
	sig_clk <= '1';
	wait for 50 ns;
  end process;
  
process is
  begin
	sig_step_write_n   <= '1';
	sig_period_write_n <= '1';
	sig_duty_write_n   <= '1';
	sig_dir_write_n    <= '1';
 	wait for 50 ns;

	-- 400 steps: 0000000110010000 binary
	sig_step_write_n <= '0';
	sig_step_data    <= "0000000110010000";

	-- CW: 00000000 binary
	sig_dir_write_n <= '0';
	sig_dir_data    <= "00000000";

	-- Frequency 2000Hz
	-- Period = 50MHz/Freq
	-- Period 25000: 00000000000000000110000110101000 binary
	sig_period_write_n <= '0';
	sig_period_data    <= "00000000000000000110000110101000";

	-- Duty Cycle 90% of 25000
	-- Duty 22500: 00000000000000000101011111100100 binary
	sig_duty_write_n <= '0';
	sig_duty_data    <= "00000000000000000101011111100100";
	wait for 50 ns;

	sig_step_write_n  <= '1';
	sig_dir_write_n   <= '1';
	sig_period_write_n <= '1';
	sig_duty_write_n  <= '1';
 	wait for 1 sec;
  end process;
end behave;
