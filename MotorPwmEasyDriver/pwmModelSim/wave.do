onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /l298n_pwm_tb/sig_clk
add wave -noupdate /l298n_pwm_tb/sig_rst
add wave -noupdate /l298n_pwm_tb/sig_step_write
add wave -noupdate /l298n_pwm_tb/sig_step
add wave -noupdate /l298n_pwm_tb/sig_cycle_write
add wave -noupdate /l298n_pwm_tb/sig_cycle
add wave -noupdate /l298n_pwm_tb/sig_duty_write
add wave -noupdate /l298n_pwm_tb/sig_duty
add wave -noupdate /l298n_pwm_tb/sig_dir_write
add wave -noupdate /l298n_pwm_tb/sig_dir
add wave -noupdate /l298n_pwm_tb/sig_a
add wave -noupdate /l298n_pwm_tb/sig_a_comp
add wave -noupdate /l298n_pwm_tb/sig_b
add wave -noupdate /l298n_pwm_tb/sig_b_comp
add wave -noupdate /l298n_pwm_tb/sig_en_a
add wave -noupdate /l298n_pwm_tb/sig_en_b
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {377515250000 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 209
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ps
update
WaveRestoreZoom {886805170804 ps} {942022160647 ps}
