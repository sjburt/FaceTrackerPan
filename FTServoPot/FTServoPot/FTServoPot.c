/*
 * FTServoPot.c
 *
 * Created: 2/23/2013 4:46:11 PM
 *  Author: Steve
 */ 

#define F_CPU 16000000
#include <avr/io.h>
#include <avr/interrupt.h>

/*
   static void uart_9600(void)
   {
	   #define BAUD 9600
	   #include <util/setbaud.h>
	   UBRRH = UBRRH_VALUE;
	   UBRRL = UBRRL_VALUE;
	   #if USE_2X
	   UCSRA |= (1 << U2X);
	   #else
	   UCSRA &= ~(1 << U2X);
	   #endif
   }
*/

void initADC0();
void initServo();
void initPWM();

uint16_t getADC();

uint16_t ADCRead;

int main(void)
{
	
	initADC0();
	
//  TODO: Initialize PWM on PD3/OC2B,  50hz cycle
    
	_delay_ms(10);   // wait a little while for things to come online.
	
	while(1)
    {
		uint16_t PotValue = getADC();
		

//  TODO: Set PWM on period.

        
    }
}

void initADC0()
{
	ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);  // set prescale to 128; (table 23-5)
	ADMUX |= (1 << REFS0);    // reference to vcc (table 23-3)
	//ADCSRA |= (1 << ADFR);    // put into free-running mode. (not in 328??)
	ADMUX &= (0 << ADLAR);    // put into 8-bit mode.
	
	ADCSRA |= (1 << ADEN); 
	ADCSRA |= (1 << ADSC);  // start taking measurements
	
	ADCSRA |= (1 << ADIE);  // Enable ADC Interrupt
	sei();   // Enable Global Interrupts
}

uint16_t getADC()
{
	return ADCRead;
}


ISR(ADC_vect)
{
	uint8_t ADCLow= ADCL;
	ADCRead = ADCH << 8 + ADCLow;
}