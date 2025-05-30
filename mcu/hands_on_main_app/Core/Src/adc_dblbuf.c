#include <adc_dblbuf.h>
#include "config.h"
#include "main.h"
#include "spectrogram.h"
#include "arm_math.h"
#include "utils.h"
#include "s2lp.h"
#include "packet.h"
#include <inttypes.h>


static volatile uint16_t ADCDoubleBuf[2*ADC_BUF_SIZE]; /* ADC group regular conversion data (array of data) */
static volatile uint16_t* ADCData[2] = {&ADCDoubleBuf[0], &ADCDoubleBuf[ADC_BUF_SIZE]};
static volatile uint8_t ADCDataRdy[2] = {0, 0};

static volatile uint8_t cur_melvec = 0;
static q15_t mel_vectors[N_MELVECS][MELVEC_LENGTH];

static uint32_t packet_cnt = 0;

static volatile int32_t rem_n_bufs = 0;

static volatile uint8_t in_routine = 0;

static uint16_t threshold = THRESHOLD;

int StartADCAcq(int32_t n_bufs) {
	rem_n_bufs = n_bufs;
	cur_melvec = 0;
	if (rem_n_bufs != 0) {
		return HAL_ADC_Start_DMA(&hadc1, (uint32_t *)ADCDoubleBuf, 2*ADC_BUF_SIZE);
	} else {
		return HAL_OK;
	}
}

int IsADCFinished(void) {
	return (rem_n_bufs == 0);
}

static void StopADCAcq() {
	HAL_ADC_Stop_DMA(&hadc1);
}

static void print_spectrogram(void) {
#if (DEBUGP == 1)
//	start_cycle_count();
	DEBUG_PRINT("Acquisition complete, sending the following FVs\r\n");
	for(unsigned int j=0; j < N_MELVECS; j++) {
		DEBUG_PRINT("FV #%u:\t", j+1);
		for(unsigned int i=0; i < MELVEC_LENGTH; i++) {
			DEBUG_PRINT("%.2f, ", q15_to_float(mel_vectors[j][i]));
		}
		DEBUG_PRINT("\r\n");
	}
//	stop_cycle_count("Print FV");
#endif
}

static void print_encoded_packet(uint8_t *packet) {
#if (DEBUGP == 1)
	char hex_encoded_packet[2*PACKET_LENGTH+1];
	hex_encode(hex_encoded_packet, packet, PACKET_LENGTH);
	DEBUG_PRINT("DF:HEX:%s\r\n", hex_encoded_packet);
#endif
}

static void encode_packet(uint8_t *packet, uint32_t* packet_cnt) {
	// BE encoding of each mel coef
	for (size_t i=0; i<N_MELVECS; i++) {
		for (size_t j=0; j<MELVEC_LENGTH; j++) {
			(packet+PACKET_HEADER_LENGTH)[(i*MELVEC_LENGTH+j)*2]   = mel_vectors[i][j] >> 8;
			(packet+PACKET_HEADER_LENGTH)[(i*MELVEC_LENGTH+j)*2+1] = mel_vectors[i][j] & 0xFF;
		}
	}
	// Write header and tag into the packet.
	make_packet(packet, PAYLOAD_LENGTH, 0, *packet_cnt);
	*packet_cnt += 1;
	if (*packet_cnt == 0) {
		// Should not happen as packet_cnt is 32-bit and we send at most 1 packet per second.
		DEBUG_PRINT("Packet counter overflow.\r\n");
		Error_Handler();
	}
}

static void send_spectrogram() {
	uint8_t packet[PACKET_LENGTH];

//	start_cycle_count();
	encode_packet(packet, &packet_cnt);
//	stop_cycle_count("Encode packet");

//	start_cycle_count();
	S2LP_Send(packet, PACKET_LENGTH);
//	stop_cycle_count("Radio WFI");

	start_cycle_count();
	stop_cycle_count("Send packet");

//	print_encoded_packet(packet);
}

static void routine(int buf_cplt) {
	if (rem_n_bufs != -1) {
			rem_n_bufs--;
		}
	if (rem_n_bufs == 0) {
		in_routine = 0;
		StopADCAcq();
	} else if (ADCDataRdy[1-buf_cplt]) {
		DEBUG_PRINT("Error: ADC Data buffer full\r\n");
		Error_Handler();
	}
	ADCDataRdy[buf_cplt] = 1;
	Spectrogram_Format((q15_t *)ADCData[buf_cplt]);
	Spectrogram_Compute((q15_t *)ADCData[buf_cplt], mel_vectors[cur_melvec]);
	cur_melvec++;
	ADCDataRdy[buf_cplt] = 0;

	if (rem_n_bufs == 0) {
//		print_spectrogram();
//		stop_cycle_count("Total FV");
		send_spectrogram();
	}
}

static int check_for_event(int buf_cplt) {
#if (EVENT_DETECTION_MODE == HARD_THRESHOLD)
#if (HT_METRIC == HT_MEAN)
	q15_t mean = 0;
	arm_mean_q15((q15_t *)ADCData[buf_cplt], SAMPLES_PER_MELVEC, &mean);
	if (mean > threshold) {
		DEBUG_PRINT("Mean value in buffer is %" PRId16 ". Found an event, start the routine.\r\n",mean);
		return 1;
	}
	return 0;
#elif (HT_METRIC == HT_MAX)
	q15_t max = 0;
	uint32_t ignored = 0;
	arm_max_q15((q15_t *)ADCData[buf_cplt], SAMPLES_PER_MELVEC, &max, &ignored);
	if (max > threshold) {
		DEBUG_PRINT("Metric value in buffer is %" PRId16 ". Found an event, start the routine.\r\n",max);
		return 1;
	}
	return 0;
#elif (HT_METRIC == HT_POWER)
#error "Doesn't work currently."
	q63_t power = 0;
	arm_power_q15((q15_t *)ADCData[buf_cplt], SAMPLES_PER_MELVEC, &power);
	if (power > (q63_t)threshold) {
			DEBUG_PRINT("Metric value in buffer is %lld. Found an event, start the routine.\r\n", power);
			return 1;
		}
	return 0;
#else
#error "Wrong value for HT_METRIC."
#endif
#elif (EVENT_DETECTION_MODE == SOFT_THRESHOLD)
#error "Not Yet implemented."
#else
#error "Wrong value for EVENT_DETECTION_MODE."
#endif
}

static void ADC_Callback(int buf_cplt) {
#if (EVENT_DETECTION == 1)
	if (in_routine == 0) {
		if (check_for_event(buf_cplt) == 1) {
			in_routine = 1;
		} else {
			return;
		}

	}
	routine(buf_cplt);
#elif (EVENT_DETECTION == 0)
	routine(buf_cplt);
#else
#error "Wrong value for EVENT_DETECTION."
#endif
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
	ADC_Callback(1);
}

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc)
{
	ADC_Callback(0);
}
