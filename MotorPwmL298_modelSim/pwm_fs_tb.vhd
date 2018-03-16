-- pwm_fs_tb.vhd
-- Created by: Jessica Huynh
-- Date: March 2nd, 2018
-- This testbench sets the pwm signal to produce a 2000Hz, 90% duty cycle,
-- full step, counter clockwise simulation

library ieee;
use ieee.std_logic_1164.all;
 
entity L298N_Pwm_fs_tb is
end L298N_Pwm_fs_tb;
 
architecture behave of L298N_Pwm_fs_tb is
  signal sig_clk : std_logic := '0';
  signal sig_rst : std_logic := '1';

  signal sig_step_write  : std_logic := '1';
  signal sig_step  : std_logic_vector(15 downto 0) := (others => '0');

  signal sig_cycle_write : std_logic := '1';
  signal sig_cycle : std_logic_vector(31 downto 0) := (others => '0');

  signal sig_duty_write  : std_logic := '1';
  signal sig_duty  : std_logic_vector(31 downto 0) := (others => '0');

  signal sig_dir_write   : std_logic := '1';
  signal sig_dir   : std_logic_vector(7 downto 0)  := (others => '0');

  signal sig_mode_write   : std_logic := '1';
  signal sig_mode   : std_logic_vector(7 downto 0)  := (others => '0');

  signal sig_a : std_logic;
  signal sig_a_comp : std_logic;
  signal sig_b : std_logic;
  signal sig_b_comp : std_logic;
  signal sig_en_a : std_logic;
  signal sig_en_b : std_logic;

component L298N_Pwm is
	port (
		reset_n            : in  std_logic                     := '0';             --       reset.reset_n
		clk                : in  std_logic                     := '0';             --       clock.clk
		a                  : out std_logic;                                        -- conduit_end.a
		b                  : out std_logic;                                        --            .b
		a_comp             : out std_logic;                                        --            .a_comp
		b_comp             : out std_logic;                                        --            .b_comp
		en_a               : out std_logic;                                        --            .en_a
		en_b               : out std_logic;                                        --            .en_b
		
		step_write_n       : in  std_logic                     := '0';             --        step.write_n
		step_writedata     : in  std_logic_vector(15 downto 0) := (others => '0'); --            .writedata
		step_read_n        : in  std_logic                     := '0';             --            .read_n
		step_readdata      : out std_logic_vector(15 downto 0);                    --            .readdata
		
		cycle_write_n      : in  std_logic                     := '0';             --       cycle.write_n
		cycle_writedata    : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		cycle_readdata     : out std_logic_vector(31 downto 0);                    --            .readdata
		cycle_read_n       : in  std_logic                     := '0';             --            .read_n
		
		duty_write_n       : in  std_logic                     := '0';             --        duty.write_n
		duty_writedata     : in  std_logic_vector(31 downto 0) := (others => '0'); --            .writedata
		duty_read_n        : in  std_logic                     := '0';             --            .read_n
		duty_readdata      : out std_logic_vector(31 downto 0);                    --            .readdata
		
		dir_write_n        : in  std_logic                     := '0';             --         dir.write_n
		dir_writedata      : in  std_logic_vector(7 downto 0)  := (others => '0'); --            .writedata
		dir_read_n         : in  std_logic                     := '0';             --            .read_n
		dir_readdata       : out std_logic_vector(7 downto 0);                     --            .readdata
		
		stepMode_read_n    : in  std_logic                     := '0';             --    stepMode.read_n
		stepMode_readdata  : out std_logic_vector(7 downto 0);                     --            .readdata
		stepMode_write_n   : in  std_logic                     := '0';             --            .write_n
		stepMode_writedata : in  std_logic_vector(7 downto 0)  := (others => '0')  --            .writedata
	);
end component L298N_Pwm;
   
begin   
  pwm_INST : L298N_Pwm 
    port map (
      reset_n  => sig_rst,
      clk      => sig_clk,

      step_write_n => sig_step_write,
      cycle_write_n => sig_cycle_write,
      duty_write_n  => sig_duty_write,
      dir_write_n   => sig_dir_write,
      stepMode_write_n   => sig_mode_write,

      step_writedata  => sig_step,
      cycle_writedata => sig_cycle,
      duty_writedata  => sig_duty,
      dir_writedata   => sig_dir,
      stepMode_writedata => sig_mode,

      a => sig_a,
      a_comp => sig_a_comp,
      b => sig_b,
      b_comp => sig_b_comp,
      en_a => sig_en_a,
      en_b => sig_en_b
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
	sig_step_write <= '1';
	sig_cycle_write <= '1';
	sig_duty_write <= '1';
	sig_dir_write <= '1';
	sig_mode_write <= '1';
 	wait for 10 ns;
	-- set 400 steps
	sig_step_write <= '0';
	sig_step <= "0000000110010000";

        -- 25000 = 50MHz/2000Hz
	sig_cycle_write <= '0';
	sig_cycle <= "00000000000000000110000110101000";

	-- 90% duty is, "00000000000000000101011111100100", 22500 = cycle*0.9
        -- 50% duty is, "00000000000000000011000011010100", 12500 = cycle*0.5
	sig_duty_write <= '0';
	sig_duty <= "00000000000000000011000011010100";

	sig_dir_write <= '0';
	sig_dir <= "00000000"; -- cw

	sig_mode_write <= '0';
	sig_mode <= "00000000"; -- full
	wait for 10 ns;

	sig_step_write <= '1';
	sig_cycle_write <= '1';
	sig_duty_write <= '1';
	sig_dir_write <= '1';
	sig_mode_write <= '1';
 	wait for 1 sec;
  end process;
end behave;
