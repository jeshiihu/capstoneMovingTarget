-- pwm_fs_tb.vhd
-- Created by: Jessica Huynh
-- Date: March 16nd, 2018
-- This testbench sets the pwm signal to produce a 2000Hz, 50% duty period,
-- full step, counter ccwsimulation

library ieee;
use ieee.std_logic_1164.all;
 
entity Easy_Driver_var_tb is
end Easy_Driver_var_tb;
 
architecture behave of Easy_Driver_var_tb is
  signal sig_clk : std_logic := '0';
  signal sig_rst : std_logic := '1';

  signal sig_step_write  : std_logic := '1';
  signal sig_step  : std_logic_vector(15 downto 0) := (others => '0');

  signal sig_period_write : std_logic := '1';
  signal sig_period : std_logic_vector(31 downto 0) := (others => '0');

  signal sig_duty_write  : std_logic := '1';
  signal sig_duty  : std_logic_vector(31 downto 0) := (others => '0');

  signal sig_dir_write   : std_logic := '1';
  signal sig_dir   : std_logic_vector(7 downto 0)  := (others => '0');

  signal sig_cond_dir    : std_logic;
  signal sig_cond_enable : std_logic;
  signal sig_cond_step   : std_logic;

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

      step_write_n => sig_step_write,
      period_write_n => sig_period_write,
      duty_write_n  => sig_duty_write,
      dir_write_n   => sig_dir_write,

      step_writedata  => sig_step,
      period_writedata => sig_period,
      duty_writedata  => sig_duty,
      dir_writedata   => sig_dir,

      conduit_end_dir    => sig_cond_dir,
      conduit_end_enable => sig_cond_enable,
      conduit_end_step   => sig_cond_step
  );

-- FPGA clk frequency is 50MHz
process is
  begin
	sig_rst <= '1';
 	sig_clk <= '0';
 	wait for 10 ns;
	sig_clk <= '1';
	wait for 10 ns;
  end process;
  
process is
  begin -- reset all (since active low)
	sig_step_write   <= '1';
	sig_period_write <= '1';
	sig_duty_write   <= '1';
	sig_dir_write    <= '1';
 	wait for 10 ns;

	-- set 20 steps
	sig_step_write <= '0';
	sig_step <= "0000000000010100";

        -- 25000 = 50MHz/2000Hz
	sig_period_write <= '0';
	sig_period <= "00000000000000000110000110101000";

	-- 90% duty is, "00000000000000000101011111100100", 22500 = period*0.9
        -- 50% duty is, "00000000000000000011000011010100", 12500 = period*0.5
	sig_duty_write <= '0';
	sig_duty <= "00000000000000000011000011010100"; --50%

	sig_dir_write <= '0';
	sig_dir <= "00000001"; -- cw
	wait for 10 ns;

	sig_step_write <= '1';
	sig_period_write <= '1';
	sig_duty_write <= '1';
	sig_dir_write <= '1';
 	wait for 20 ms;

	-- set 40 steps
	sig_step_write <= '0';
	sig_step <= "0000000000101000";

        -- 25000 = 50MHz/2000Hz
	sig_period_write <= '0';
	sig_period <= "00000000000000000110000110101000";

	-- 90% duty is, "00000000000000000101011111100100", 22500 = period*0.9
        -- 50% duty is, "00000000000000000011000011010100", 12500 = period*0.5
	sig_duty_write <= '0';
	sig_duty <= "00000000000000000011000011010100"; --50%

	sig_dir_write <= '0';
	sig_dir <= "00000000"; -- cw
	wait for 30 ns;

	sig_step_write <= '1';
	sig_period_write <= '1';
	sig_duty_write <= '1';
	sig_dir_write <= '1';
 	wait for 1 sec;
  end process;
end behave;


