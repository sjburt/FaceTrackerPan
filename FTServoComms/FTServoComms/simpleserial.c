/*
* simpleserial.c
*
* Created: 2/24/2013 8:40:56 PM
*  Author: Steve
*/
#define F_CPU 16000000L
#include <avr/io.h>
#include <util/delay.h>
#include <avr/pgmspace.h>
#include "uart.h"
#include "simpleserial.h"


typedef enum MODE {
	REGULAR =0,
DEBUG=1} MODE;

static MODE PortMode;


char initSerial(uint16_t baud)
{
	switch(baud)
	{
		case 38400:
		uart_init(UART_BAUD_SELECT(38400,F_CPU));
		break;
		case 9600:
		uart_init(UART_BAUD_SELECT(9600,F_CPU));
		break;
		case 1200:
		uart_init(UART_BAUD_SELECT(1200,F_CPU));
		break;
		default:
		return(-1);
	}
	return 0;
}

char handshake()
{
	uart_flush();
	_delay_ms(100);
	
	while(uart_available()==0)
	{

		PORTB |=(1<<PB5);
		_delay_ms(100);
		PORTB &=~(1<<PB5);
		_delay_ms(100);
		
	}
	
	if (uart_getc() == 'a')
	{
		PORTB |=(1<<PB5);
		_delay_ms(50);
		PORTB &=~(1<<PB5);
		_delay_ms(50);
		PORTB |=(1<<PB5);
		_delay_ms(50);
		PORTB &=~(1<<PB5);
		_delay_ms(50);
		
	}
	
	uart_putc('b');
	while(uart_available()==0)
	{
		PORTB |=(1<<PB5);
		_delay_ms(20);
		
		PORTB &= ~(1<<PB5);
		_delay_ms(20);
	}
	
	if (uart_getc() == 'c')
	{
		uart_putc('d');
		PortMode = REGULAR;
		return(0);  // handshake success
	}
	else
	{
		uart_puts_p(PSTR("\n Debug mode"));
		PortMode = DEBUG;
		return(1);  // debug mode
	}
}

void clean_string(uint8_t* clean,const uint8_t* dirty)
{
	uint8_t cleanidx = 0;
	uint8_t dirtyidx = 0;
	
	while(dirty[dirtyidx++]==0x7F);

	while(dirty[dirtyidx++-1]!=0x7F)
	{
		if (dirty[dirtyidx-2]==0x7E)
		{
			clean[cleanidx++]=((dirty[dirtyidx-1]) ^ (0x20));
			dirtyidx++;
		}
		else
		{
			clean[cleanidx++]=dirty[dirtyidx-2];
		}
	}
	clean[cleanidx] = '\0';

}

void dirty_string(uint8_t* dirty, const uint8_t *clean)
{
	uint8_t cleanidx =0;
	uint8_t dirtyidx =0;
	
	dirty[dirtyidx++] = 0x7F;
	while(clean[cleanidx++] != '\0')
	{
		if (clean[cleanidx-1] == 0x7F)
		{	dirty[dirtyidx++] = 0x7E;
			dirty[dirtyidx++] = 0x7F ^ 0x20;
		}
		else if (clean[cleanidx-1] == 0x7E)
		{	dirty[dirtyidx++] = 0x7E;
			dirty[dirtyidx++] = 0x7E ^ 0x20;
		}
		else
		{
			dirty[dirtyidx++]=clean[cleanidx-1];
		}
	}
	dirty[dirtyidx] = 0x7F;
	dirty[dirtyidx+1] = '\0';
}



char getMessage(SerMsg *msg,uint16_t *data)
{
	static uint8_t alt=0;
	uint8_t raw_string[10];
	uint8_t cln_string[10];
	static uint16_t yaw =512;
	static uint16_t pitch=512;
	switch(PortMode)
	{
		case DEBUG:
		uart_puts_P("\r\n wasd >");
		while(uart_available()==0);
		
		char c = uart_getc();
		
		switch (c)
		{
			case 'a':
			yaw+=50;
			*msg = YAWPOS;
			*data = yaw;
			break;
			case 'd':
			yaw-=50;
			*msg = YAWPOS;
			*data = yaw;
			break;
			case 'w':
			pitch -=50;
			*msg = PITCHPOS;
			*data = pitch;
			break;
			case 's':
			pitch +=50;
			*msg = PITCHPOS;
			*data = pitch;
			break;
		}
		

		return 0;
		break;
		case REGULAR:

		if (uart_available()>0)
		{
			uint8_t i =0;
			raw_string[0] = uart_getc();
			while (raw_string[i] != 0x7F && uart_available())
			{
				raw_string[i++] = uart_getc();  // get to new frame
			}
			raw_string[i]=uart_getc();
			if (raw_string[i]==0x7F)
			{
				raw_string[i] = uart_getc();
			}
			while (uart_available())
			{
				raw_string[++i] = uart_getc();
				if (raw_string[i]==0x7F)
			{break;}
			}
			clean_string(cln_string,raw_string);
			
			
			switch(cln_string[0])
			{
				case 'p':
				if (cln_string[1]=='p')
				{
					*msg = YAWPOS;
					*data = (cln_string[2] << 8) + cln_string[3];
					return 0; //success!
				}
				else
				{
					return -1;
				}
				break;
				
				case 'o':
				if( cln_string[1]=='o')
				{
					
					*msg = PITCHPOS;
					*data = (cln_string[2] << 8) + cln_string[3];
					return 0; //success!
				} else
				{
					return -1;
				}
				
				
				break;
				
				case 's':
				*msg = STOP;
				*data = 0;
				return 0;
				break;
			}
			
		}
		else
		{
			switch(alt){
				case 0:
				uart_putc('o');
				alt =1;
				break;
				case 1:
				uart_putc('p');
				alt=0;
				break;
				default:
				uart_putc('p');
				alt = 0;
				break;
			}
			
		}
		break;
		default:
		*msg = NULL;
		return -1;  // error.
	}
	
	
	return 0;
}
