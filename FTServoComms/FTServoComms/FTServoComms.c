/*
 * FTServoComms.c
 *
 * Created: 2/24/2013 8:34:32 PM
 *  Author: Steve
 */ 

/*
 * FTServoPot.c
 *
 * Created: 2/23/2013 4:46:11 PM
 *  Author: Steve
 */ 

#define F_CPU 16000000L
#define _DEBUG


#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <util/atomic.h>
#include "uart.h"
#include "simpleserial.h"

void initADC0();
void initServo();
void initPWM();
void setServo(uint16_t dest);
uint16_t getADC();

uint16_t volatile ADCRead = 0;
uint16_t volatile ISRCount = 0;


int main(void)
{

	initServo();
	initSerial(9600);
	uint16_t dest;
	SerMsg msg;
	char err;
	_delay_ms(10);   // wait a little while for things to come online.	
	sei();
	 DDRB|=(1<<PB1);  
	 			PORTB |=(1<<PB5);
	 			_delay_ms(200);
	 			
	 			PORTB &= ~(1<<PB5);
	 			_delay_ms(200);

	handshake();
	
			PORTB |=(1<<PB5);
			_delay_ms(200);
			
			PORTB &= ~(1<<PB5);
			_delay_ms(200);


	while(1)
    {
		err = getMessage(&msg,&dest);
		if (err==0)
		{
			setServo(dest);
		}		
		_delay_ms(100);
    }
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
	

}