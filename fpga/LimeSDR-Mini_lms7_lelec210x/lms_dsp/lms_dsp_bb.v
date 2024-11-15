
module lms_dsp (
	clk_clk,
	fifo_in_wdata,
	fifo_in_wrreq,
	fifo_out_wrdata,
	fifo_out_wrreq,
	ppd_cfg_passthrough_len,
	ppd_cfg_threshold,
	ppd_cfg_clear_rs,
	ppd_cfg_enable,
	ppd_debug_count,
	ppd_debug_long_sum,
	ppd_debug_short_sum,
	reset_reset_n,
	fir_compiler_ii_0_clk_clk,
	fir_compiler_ii_0_rst_reset_n,
	fir_compiler_ii_0_avalon_streaming_sink_data,
	fir_compiler_ii_0_avalon_streaming_sink_valid,
	fir_compiler_ii_0_avalon_streaming_sink_error,
	fir_compiler_ii_0_avalon_streaming_source_data,
	fir_compiler_ii_0_avalon_streaming_source_valid,
	fir_compiler_ii_0_avalon_streaming_source_error,
	packet_presence_detection_0_avalon_streaming_sink_data,
	packet_presence_detection_0_avalon_streaming_sink_valid,
	packet_presence_detection_0_avalon_streaming_source_data,
	packet_presence_detection_0_avalon_streaming_source_valid,
	packet_presence_detection_0_clock_sink_clk,
	packet_presence_detection_0_reset_sink_reset);	

	input		clk_clk;
	input	[47:0]	fifo_in_wdata;
	input		fifo_in_wrreq;
	output	[47:0]	fifo_out_wrdata;
	output		fifo_out_wrreq;
	input	[15:0]	ppd_cfg_passthrough_len;
	input	[7:0]	ppd_cfg_threshold;
	input		ppd_cfg_clear_rs;
	input		ppd_cfg_enable;
	output	[31:0]	ppd_debug_count;
	output	[31:0]	ppd_debug_long_sum;
	output	[31:0]	ppd_debug_short_sum;
	input		reset_reset_n;
	input		fir_compiler_ii_0_clk_clk;
	input		fir_compiler_ii_0_rst_reset_n;
	input	[23:0]	fir_compiler_ii_0_avalon_streaming_sink_data;
	input		fir_compiler_ii_0_avalon_streaming_sink_valid;
	input	[1:0]	fir_compiler_ii_0_avalon_streaming_sink_error;
	output	[23:0]	fir_compiler_ii_0_avalon_streaming_source_data;
	output		fir_compiler_ii_0_avalon_streaming_source_valid;
	output	[1:0]	fir_compiler_ii_0_avalon_streaming_source_error;
	input	[23:0]	packet_presence_detection_0_avalon_streaming_sink_data;
	input		packet_presence_detection_0_avalon_streaming_sink_valid;
	output	[23:0]	packet_presence_detection_0_avalon_streaming_source_data;
	output		packet_presence_detection_0_avalon_streaming_source_valid;
	input		packet_presence_detection_0_clock_sink_clk;
	input		packet_presence_detection_0_reset_sink_reset;
endmodule
