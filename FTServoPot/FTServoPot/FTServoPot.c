/*
 * FTServoPot.c
 *
 * Created: 2/23/2013 4:46:11 PM
 *  Author: Steve
 */ 

#define F_CPU 16000000
#define _DEBUG


#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <util/atomic.h>
#include "uart.h"

void initADC0();
void initServo();
void initPWM();
void setServo(uint16_t dest);
uint16_t getADC();

uint16_t volatile ADCRead = 0;
uint16_t volatile ISRCount = 0;
int main(void)
{
	uint16_t potValue = 0;
	initADC0();
	// todo: initialize the UART

	uart_init(UART_BAUD_SELECT(38400,F_CPU));
	initServo();

//  TODO: Initialize PWM on PD3/OC2B,  50hz cycle




	_delay_ms(10);   // wait a little while for things to come online.
		sei();
#ifdef _DEBUG
	uart_flush();
	uart_puts("ubasdfasdf");
#endif // _DEBUG

	while(1)
    {
		potValue = ADCRead;



		ISRCount=0;
		
		setServo(potValue);
		
		_delay_ms(100);
    }
}

void initADC0()
{
	ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);  // set prescale to 128; (table 23-5)
	ADMUX |= (1 << REFS0);    // reference to vcc (table 23-3)
	//ADCSRA |= (1 << ADFR);    // put into free-running mode. (not in 328??)
//	ADMUX |= (1 << ADLAR);    // put into 8-bit mode.
	ADCSRA |= (1 << ADEN); 
	
	
	ADCSRA |= (1 << ADATE); // Auto-trigger
	ADCSRA |= (1 << ADIE);  // Enable ADC Interrupt
	
	ADCSRA |= (1 << ADSC);  // start taking measurements
}

uint16_t getADC()
{
	uint16_t ADCReadLocal;
	ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
	{
		ADCReadLocal=ADCRead;
	}
	return ADCReadLocal;
}


ISR(ADC_vect)
{
	ADCRead = ADC;
	
	
	ISRCount++;

}


void initPWM()
{
	 TCCR1A|=(1<<COM1A1)|(1<<COM1B1)|(1<<WGM11);       
	 TCCR1B|=(1<<WGM13)|(1<<WGM11)|(1<<CS11); //PRESCALER=8 MODE 10(phase correct)

	 ICR1=20000;  //50Hz (Period = 20ms).

	 DDRB|=(1<<PB1);   //PWM Pins as Out
	 
}

void initServo()
{
	initPWM();
}

void setServo(uint16_t dest)
{
	int servo = dest*1.8+600;
	
	OCR1A = servo;
	
	#ifdef _DEBUG
	char count[10];
	sprintf(count,"%d ",servo);
	uart_puts(count);
	#endif
}