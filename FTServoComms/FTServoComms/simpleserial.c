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

#define MSG_SIZE 6

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
	while(uart_available()==0)
	_delay_ms(100);
	
	if (uart_getc() == 'a')
		uart_putc('b');
	else
		uart_putc('d');
		
	while(uart_available()==0)
	_delay_ms(100);
	
	if (uart_getc() == 'c')
	{
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

char getMessage(SerMsg *msg,uint16_t *data)
{
	static uint16_t loc =512;
	switch(PortMode)
	{
		case DEBUG:
		
		
		uart_puts_P("\n f/v >");
		while(uart_available()==0);
		
		char c = uart_getc();
		
		switch (c)
		{
			case 'f':
			loc+=50;
			break;
			case 'v':
			loc-=50;
			break;
		}
		
		*msg = POS;
		*data = loc;
		return 0;
		break;
		case REGULAR:
		
		if (uart_available()<MSG_SIZE)
		{
			if (uart_available() ==0)
			uart_putc('g');
			// no command waiting
			*msg = NULL;
			return 1; // wait
		}
		else
		{
			uint8_t raw[MSG_SIZE];
			uint8_t i;
			for (i=0;i<MSG_SIZE;i++)
			raw[i] = uart_getc();
			
			
			switch (raw[0])
			{
				case 'p':
				*msg = POS;
				
				
				loc = ((raw[1]-64) << 6) + (raw[2]-64);
				*data = loc;
				
				return 0; //successful
				break;
				case 's':
				*msg = STOP;
				*data = 0;
				return 0;
				break;
				default:
				*msg = NULL;
				*data = 0;
				return -1;
			}
		}
		break;
		default:
		*msg = NULL;
		return -1;  // error.
	}
	
	
	return 0;
}
