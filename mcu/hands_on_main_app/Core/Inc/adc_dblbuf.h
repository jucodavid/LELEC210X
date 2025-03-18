#ifndef INC_ADC_DBLBUF_H_
#define INC_ADC_DBLBUF_H_

#include "main.h"
#include "config.h"
#include "arm_math.h"

// ADC parameters
#define ADC_BUF_SIZE SAMPLES_PER_MELVEC

static volatile uint16_t ADCDoubleBuf[2*ADC_BUF_SIZE]; /* ADC group regular conversion data (array of data) */
int StartADCAcq(int32_t n_bufs);
int IsADCFinished(void);

extern ADC_HandleTypeDef hadc1;

static volatile uint8_t first_buf = 1;

static volatile q15_t mean_buf;

#endif /* INC_ADC_DBLBUF_H_ */
